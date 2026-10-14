import AppKit
import ApplicationServices

/// Reads the Spotlight panel through Accessibility. Call from one serial queue, never the main thread.
final class SpotlightReader: @unchecked Sendable {
    // On current macOS the panel lives in "Siri AI.app"; older systems use com.apple.Spotlight.
    private static let bundleIDs = ["com.apple.campo", "com.apple.Spotlight"]
    private static let maxDepth = 25
    // shortcut: stops collecting after 500 nodes, so rows past that are lost; raise if Spotlight panels grow.
    private static let maxNodes = 500

    /// Empty when Accessibility is denied, no panel process runs, or Spotlight is closed.
    func read() -> SpotlightSnapshot {
        guard AXIsProcessTrusted() else { return .empty }
        for id in Self.bundleIDs {
            guard let app = NSRunningApplication.runningApplications(withBundleIdentifier: id).first else { continue }
            let element = AXUIElementCreateApplication(app.processIdentifier)
            AXUIElementSetMessagingTimeout(element, 0.5)
            guard let windows = attribute(element, kAXWindowsAttribute) as? [AXUIElement] else { continue }
            var nodes: [SpotlightNode] = []
            for window in windows { walk(window, depth: 0, into: &nodes) }
            let snapshot = SpotlightParser.parse(nodes)
            if snapshot != .empty { return snapshot }
        }
        return .empty
    }

    /// Sets the search field's value; false when the field is missing after retrying
    /// (the panel may not exist yet after Cmd+Space). Never types keys.
    func setQuery(_ query: String) -> Bool {
        guard AXIsProcessTrusted() else { return false }
        let deadline = Date().addingTimeInterval(0.5)
        repeat {
            if let field = findField() {
                return AXUIElementSetAttributeValue(field, kAXValueAttribute as CFString, query as CFString) == .success
            }
            Thread.sleep(forTimeInterval: 0.05)
        } while Date() < deadline
        return false
    }

    private func findField() -> AXUIElement? {
        for id in Self.bundleIDs {
            guard let app = NSRunningApplication.runningApplications(withBundleIdentifier: id).first else { continue }
            let element = AXUIElementCreateApplication(app.processIdentifier)
            AXUIElementSetMessagingTimeout(element, 0.5)
            guard let windows = attribute(element, kAXWindowsAttribute) as? [AXUIElement] else { continue }
            var budget = Self.maxNodes
            for window in windows {
                if let field = search(window, depth: 0, budget: &budget) { return field }
            }
        }
        return nil
    }

    private func search(_ element: AXUIElement, depth: Int, budget: inout Int) -> AXUIElement? {
        guard budget > 0 else { return nil }
        budget -= 1
        if attribute(element, kAXIdentifierAttribute) as? String == "SpotlightSearchField" { return element }
        guard depth < Self.maxDepth, let children = attribute(element, kAXChildrenAttribute) as? [AXUIElement]
        else { return nil }
        for child in children {
            if let field = search(child, depth: depth + 1, budget: &budget) { return field }
        }
        return nil
    }

    private func attribute(_ element: AXUIElement, _ name: String) -> AnyObject? {
        var value: CFTypeRef?
        return AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success ? value : nil
    }

    private func frame(_ element: AXUIElement) -> CGRect {
        var origin = CGPoint.zero, size = CGSize.zero
        if let value = attribute(element, kAXPositionAttribute), CFGetTypeID(value) == AXValueGetTypeID() {
            AXValueGetValue(value as! AXValue, .cgPoint, &origin)
        }
        if let value = attribute(element, kAXSizeAttribute), CFGetTypeID(value) == AXValueGetTypeID() {
            AXValueGetValue(value as! AXValue, .cgSize, &size)
        }
        return CGRect(origin: origin, size: size)
    }

    private func walk(_ element: AXUIElement, depth: Int, into nodes: inout [SpotlightNode]) {
        guard nodes.count < Self.maxNodes else { return }
        nodes.append(SpotlightNode(
            depth: depth,
            role: attribute(element, kAXRoleAttribute) as? String ?? "",
            id: attribute(element, kAXIdentifierAttribute) as? String ?? "",
            value: attribute(element, kAXValueAttribute) as? String ?? "",
            frame: frame(element)))
        guard depth < Self.maxDepth, let children = attribute(element, kAXChildrenAttribute) as? [AXUIElement]
        else { return }
        for child in children { walk(child, depth: depth + 1, into: &nodes) }
    }
}
