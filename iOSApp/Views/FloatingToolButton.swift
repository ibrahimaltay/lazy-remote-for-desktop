import RemoteClientCore
import SwiftUI

/// AssistiveTouch-style button that opens a tool (Remote or Keyboard). Positions are in the "root"
/// coordinate space, which this layer shares with `RootView`.
struct FloatingToolButton: View {
    let model: RemoteViewModel
    let glyph: String
    let label: String
    @Binding var isDocked: Bool
    // Fractions of the layer size, so the spot survives size and device changes.
    @Binding var fractionX: Double
    @Binding var fractionY: Double
    /// The other tool's fractions while it floats, else nil.
    let other: CGPoint?
    /// Keyboard yields to Remote when rotation leaves them overlapping.
    let yields: Bool
    /// Center of the dock slot.
    let dock: CGPoint
    /// Distances from the layer edges to the box the button snaps within.
    let snap: EdgeInsets
    /// Dropping above this y docks (the portrait header).
    let nearDockAbove: CGFloat
    /// Landscape: the screen side of the controls column; dropping in line with the slot there docks.
    let columnSide: HorizontalEdge?
    let open: () -> Void

    @State private var dragOrigin: CGPoint?
    @State private var dragPosition: CGPoint?
    @State private var isNearDock = false

    private static let floatingSize: CGFloat = 58

    var body: some View {
        GeometryReader { geo in
            let docked = isDocked && dragPosition == nil
            // Landscape lets this layer extend under the Island inset, so "root" is offset from it.
            let origin = geo.frame(in: .named("root")).origin
            let dock = CGPoint(x: self.dock.x - origin.x, y: self.dock.y - origin.y)
            let center = dragPosition ?? (docked ? dock : snapped(
                CGPoint(x: fractionX * geo.size.width, y: fractionY * geo.size.height),
                in: geo.size, stacked: yields
            ))

            if dragPosition != nil {
                dockTarget.position(dock)
            }
            button(docked: docked)
                .position(center)
                .gesture(drag(from: center, in: geo.size, dock: dock))
        }
        .ignoresSafeArea(.keyboard)
    }

    private func button(docked: Bool) -> some View {
        let size = docked ? 32 : Self.floatingSize
        return Image(systemName: glyph)
            .font(.system(size: docked ? 22 : 28))
            .foregroundStyle(docked ? Color.accentColor : Color.primary)
            .frame(width: size, height: size)
            .background {
                if !docked {
                    Circle()
                        .fill(.ultraThinMaterial)
                        .overlay(Circle().fill(Color(.systemGray6).opacity(0.86)))
                        .overlay(Circle().strokeBorder(.white.opacity(0.18), lineWidth: 0.5))
                        .shadow(color: .black.opacity(0.5), radius: 12, y: 8)
                }
            }
            .contentShape(Circle())
            .opacity(model.isConnected ? 1 : 0.5)
            .animation(.easeOut(duration: 0.2), value: docked)
            .accessibilityLabel(label)
            .accessibilityAddTraits(.isButton)
            .accessibilityAction { if model.isConnected { open() } }
    }

    private var dockTarget: some View {
        Circle()
            .strokeBorder(
                isNearDock ? Color.accentColor : Color.secondary.opacity(0.6),
                style: StrokeStyle(lineWidth: 1.5, dash: [4, 3])
            )
            .background(Circle().fill(isNearDock ? Color.accentColor.opacity(0.18) : .clear))
            .frame(width: 36, height: 36)
            .allowsHitTesting(false)
    }

    /// Under 5pt of travel is a tap; anything more drags 1:1, then docks or snaps to an edge.
    private func drag(from center: CGPoint, in size: CGSize, dock: CGPoint) -> some Gesture {
        DragGesture(minimumDistance: 0, coordinateSpace: .named("root"))
            .onChanged { value in
                let t = value.translation
                if dragOrigin == nil {
                    guard hypot(t.width, t.height) >= 5 else { return }
                    dragOrigin = center
                }
                guard let origin = dragOrigin else { return }
                let radius = Self.floatingSize / 2
                let p = CGPoint(
                    x: min(max(origin.x + t.width, radius), size.width - radius),
                    y: min(max(origin.y + t.height, radius), size.height - radius)
                )
                dragPosition = p
                let inLine = columnSide.map { ($0 == .leading ? p.x < size.width / 2 : p.x > size.width / 2)
                    && abs(p.y - dock.y) < 30 } ?? false
                isNearDock = p.y < nearDockAbove || inLine || hypot(p.x - dock.x, p.y - dock.y) < 60
            }
            .onEnded { _ in
                guard let p = dragPosition else {
                    if model.isConnected { open() }
                    return
                }
                withAnimation(.easeOut(duration: 0.28)) {
                    if isNearDock {
                        isDocked = true
                    } else {
                        isDocked = false
                        let s = snapped(p, in: size, stacked: true)
                        fractionX = s.x / size.width
                        fractionY = s.y / size.height
                    }
                    dragOrigin = nil
                    dragPosition = nil
                    isNearDock = false
                }
            }
    }

    /// Nearest side edge of the snap box; `stacked` keeps it 70 clear of the other tool on that edge.
    private func snapped(_ p: CGPoint, in size: CGSize, stacked: Bool = false) -> CGPoint {
        let at = plainSnap(p, in: size)
        guard stacked, let other, size.height > snap.top + snap.bottom else { return at }
        let o = plainSnap(CGPoint(x: other.x * size.width, y: other.y * size.height), in: size)
        return CGPoint(x: at.x, y: FloatingToolLayout.stackedY(
            at.y, other: o.x == at.x ? o.y : nil, range: snap.top...(size.height - snap.bottom)
        ))
    }

    private func plainSnap(_ p: CGPoint, in size: CGSize) -> CGPoint {
        CGPoint(
            x: p.x < size.width / 2 ? snap.leading : size.width - snap.trailing,
            y: min(max(p.y, snap.top), size.height - snap.bottom)
        )
    }
}
