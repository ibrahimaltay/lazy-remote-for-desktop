import SwiftUI

struct RootView: View {
    let model: RemoteViewModel

    @State private var confirmsForget = false
    @State private var isSpotlight = false
    @State private var isTyping = false
    @AppStorage("remoteFab.docked") private var isRemoteDocked = true
    @AppStorage("remoteFab.x") private var remoteX = 357.0 / 393
    @AppStorage("remoteFab.y") private var remoteY = 0.66
    @AppStorage("keyboardFab.docked") private var isKeyboardDocked = true
    @AppStorage("keyboardFab.x") private var keyboardX = 357.0 / 393
    @AppStorage("keyboardFab.y") private var keyboardY = 0.74
    @State private var isDPadOpen = false
    @State private var dockCenter = CGPoint.zero
    @State private var headerBottom: CGFloat = 0
    @State private var isLandscape = false
    /// .landscapeLeft puts the Island on the right, so the column goes on the left.
    @State private var columnAtLeading = true
    /// Real safe-area inset on the Island side, from the window scene.
    @State private var islandInset: CGFloat = 0

    private let columnEdge: CGFloat = 14
    private var farEdge: CGFloat { max(16, islandInset) }
    private var nearInset: CGFloat { columnEdge + 42 }
    private var sideInsets: (leading: CGFloat, trailing: CGFloat) {
        columnAtLeading ? (nearInset, farEdge) : (farEdge, nearInset)
    }

    private var trackpadInsets: EdgeInsets {
        guard isLandscape else { return EdgeInsets(top: 0, leading: 20, bottom: 14, trailing: 20) }
        return EdgeInsets(top: 12, leading: sideInsets.leading, bottom: 20, trailing: sideInsets.trailing)
    }

    private var barInsets: EdgeInsets {
        guard isLandscape else { return EdgeInsets(top: 12, leading: 20, bottom: 12, trailing: 20) }
        return EdgeInsets(top: 8, leading: sideInsets.leading, bottom: 8, trailing: sideInsets.trailing)
    }

    /// Distances from the layer edges to the box the floating tools snap within (design y 150-760
    /// portrait, 49-340 landscape; portrait assumes the 59 / 34 safe areas of the design canvas).
    private var snapInsets: EdgeInsets {
        guard isLandscape else { return EdgeInsets(top: 91, leading: 41, bottom: 58, trailing: 41) }
        return EdgeInsets(
            top: 49, leading: sideInsets.leading + 37, bottom: 53, trailing: sideInsets.trailing + 37
        )
    }

    /// Slot centers: Remote is the one next to Spotlight, Keyboard sits one slot (44) before it.
    private var remoteDock: CGPoint { dockCenter }
    private var keyboardDock: CGPoint {
        isLandscape ? CGPoint(x: dockCenter.x, y: dockCenter.y + 40) : CGPoint(x: dockCenter.x - 44, y: dockCenter.y)
    }

    var body: some View {
        ZStack(alignment: .bottom) {
            VStack(spacing: 0) {
                if !isLandscape {
                    header
                        .onGeometryChange(for: CGFloat.self) { $0.frame(in: .named("root")).maxY } action: {
                            headerBottom = $0
                        }
                }
                TrackpadView(model: model, insets: trackpadInsets)
            }
            .overlay(alignment: columnAtLeading ? .topLeading : .topTrailing) {
                if isLandscape { column }
            }
            .overlay {
                if isTyping { scrim }
            }
            .animation(.easeOut(duration: 0.2), value: isTyping)
            .accessibilityHidden(isTyping)
            .blur(radius: isSpotlight ? 14 : 0)
            // The keyboard covers the controls instead of squeezing them.
            .ignoresSafeArea(.keyboard, edges: .bottom)

            TextInputBar(model: model, isFocused: $isTyping, insets: barInsets)
                .blur(radius: isSpotlight ? 14 : 0)

            // Both tools hide while the Keyboard overlay or Spotlight is open.
            if !isSpotlight && !isTyping {
                let columnSide: HorizontalEdge? = isLandscape ? (columnAtLeading ? .leading : .trailing) : nil
                FloatingToolButton(
                    model: model, glyph: "appletvremote.gen4", label: "Remote", isDocked: $isRemoteDocked,
                    fractionX: $remoteX, fractionY: $remoteY,
                    other: isKeyboardDocked ? nil : CGPoint(x: keyboardX, y: keyboardY), yields: false,
                    dock: remoteDock, snap: snapInsets, nearDockAbove: isLandscape ? 0 : headerBottom,
                    columnSide: columnSide
                ) {
                    withAnimation(.easeOut(duration: 0.2)) { isDPadOpen = true }
                }
                FloatingToolButton(
                    model: model, glyph: "keyboard", label: "Keyboard", isDocked: $isKeyboardDocked,
                    fractionX: $keyboardX, fractionY: $keyboardY,
                    other: isRemoteDocked ? nil : CGPoint(x: remoteX, y: remoteY), yields: true,
                    dock: keyboardDock, snap: snapInsets, nearDockAbove: isLandscape ? 0 : headerBottom,
                    columnSide: columnSide
                ) {
                    isTyping = true
                }
            }

            if isDPadOpen {
                DPadOverlay(model: model, isPresented: $isDPadOpen)
                    .transition(.opacity)
            }
        }
        .overlay {
            if isSpotlight {
                SpotlightOverlay(model: model, close: closeSpotlight)
                    .ignoresSafeArea(.keyboard)
                    .transition(.opacity)
            }
        }
        .animation(.easeOut(duration: 0.2), value: isSpotlight)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        // Before ignoresSafeArea so it sees the real insets, which change when the interface rotates.
        .onGeometryChange(for: EdgeInsets.self) { $0.safeAreaInsets } action: { _ in readScene() }
        // Landscape lays out by hand to the screen edges; the keyboard inset still applies.
        .ignoresSafeArea(.container, edges: isLandscape ? [.horizontal, .bottom] : [])
        .coordinateSpace(.named("root"))
        .onGeometryChange(for: Bool.self) { $0.size.width > $0.size.height } action: {
            isLandscape = $0
            readScene()
        }
        // Landscape-to-landscape flips keep the size, so listen for the rotation itself.
        .onReceive(NotificationCenter.default.publisher(for: UIDevice.orientationDidChangeNotification)) { _ in
            // The notification can beat UIKit's scene update, so read again once it settles.
            DispatchQueue.main.async { readScene() }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { readScene() }
        }
        .onAppear { readScene() }
        .background(Color(.systemBackground))
        // The controls reach the top and bottom edges, where a sideways drag would otherwise
        // flick iOS into another app mid-gesture.
        .defersSystemGestures(on: isLandscape ? [.top, .bottom] : .bottom)
        .confirmationDialog("Forget this Mac?", isPresented: $confirmsForget, titleVisibility: .visible) {
            Button("Forget Mac", role: .destructive) { model.forgetMac() }
        } message: {
            Text("The saved Mac identity will be removed. Only reconnect to a Mac you trust.")
        }
    }

    private func readScene() {
        let scenes = UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
        guard let scene = scenes.first(where: { $0.activationState == .foregroundActive }) ?? scenes.first else { return }
        let insets = scene.keyWindow?.safeAreaInsets ?? .zero
        switch scene.interfaceOrientation {
        case .landscapeLeft: columnAtLeading = true; islandInset = insets.right
        case .landscapeRight: columnAtLeading = false; islandInset = insets.left
        default: break
        }
    }

    /// Sent text leaves the Mac's Spotlight open on its results; otherwise Cmd+Space again closes it.
    private func closeSpotlight(closeMac: Bool) {
        guard isSpotlight else { return }
        isSpotlight = false
        if closeMac { model.tap(.spotlight, feedback: false) }
    }

    /// Fires on touch-down so a stray touch while typing only dismisses the
    /// keyboard and never reaches the trackpad or a key.
    private var scrim: some View {
        ToolScrim()
            .contentShape(.rect)
            .gesture(DragGesture(minimumDistance: 0).onChanged { _ in isTyping = false })
            .transition(.opacity)
    }

    private var spotlightButton: some View {
        Button {
            model.tap(.spotlight)
            isTyping = false
            isSpotlight = true
        } label: {
            Magnifier(size: 18, ringWidth: 1.7, handleWidth: 1.9, color: Color(red: 10 / 255, green: 132 / 255, blue: 1))
                .frame(width: 32, height: 32)
                .opacity(model.isConnected ? 1 : 0.5)
        }
        .disabled(!model.isConnected)
        .accessibilityLabel("Spotlight Search")
    }

    private var moreMenu: some View {
        Menu {
            Button("Reconnect", systemImage: "arrow.clockwise") {
                model.reconnect()
            }
            Button("Forget Mac", systemImage: "trash", role: .destructive) {
                confirmsForget = true
            }
        } label: {
            Image(systemName: "ellipsis.circle")
                .frame(width: 32, height: 32)
        }
        .accessibilityLabel("Connection options")
    }

    private var header: some View {
        HStack(spacing: 12) {
            StatusLabel(model: model)
                .frame(maxWidth: .infinity, alignment: .leading)
            // FloatingToolButton draws itself over these slots. Keyboard's never moves when Remote
            // leaves; Remote's stays reserved while either tool is docked.
            if isKeyboardDocked {
                Color.clear.frame(width: 32, height: 32)
            }
            if isRemoteDocked || isKeyboardDocked {
                Color.clear.frame(width: 32, height: 32)
            }
            spotlightButton
                .onGeometryChange(for: CGPoint.self) {
                    let frame = $0.frame(in: .named("root"))
                    // One 32pt slot plus the 12pt stack spacing to the left.
                    return CGPoint(x: frame.minX - 12 - 16, y: frame.midY)
                } action: {
                    dockCenter = $0
                }
            moreMenu
        }
        .padding(.horizontal, 20)
        .padding(.top, 14)
        .padding(.bottom, 14)
    }

    /// Landscape controls, 32pt wide on the side opposite the Island.
    private var column: some View {
        VStack(spacing: 8) {
            moreMenu
            spotlightButton
            // Always reserved; FloatingToolButton draws itself over these when docked.
            Color.clear.frame(width: 32, height: 32)
                .onGeometryChange(for: CGPoint.self) {
                    let frame = $0.frame(in: .named("root"))
                    return CGPoint(x: frame.midX, y: frame.midY)
                } action: {
                    dockCenter = $0
                }
            Color.clear.frame(width: 32, height: 32)
            VerticalStatus(model: model)
                .padding(.top, 10)
                .padding(.bottom, 34 - 8)
        }
        .frame(width: 32)
        .padding(.top, 20)
        .padding(.horizontal, columnEdge)
        .frame(maxHeight: .infinity, alignment: .top)
    }
}

/// Status set vertically (top to bottom) under the dot; the tail truncates.
struct VerticalStatus: View {
    let model: RemoteViewModel

    var body: some View {
        VStack(spacing: 8) {
            Circle()
                .fill(model.isConnected ? .green : .orange)
                .frame(width: 8, height: 8)
            Color.clear
                .frame(width: 18)
                .overlay {
                    GeometryReader { geo in
                        Text(model.statusText)
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                            .lineLimit(1)
                            .frame(width: geo.size.height, height: 18, alignment: .leading)
                            .rotationEffect(.degrees(90), anchor: .topLeading)
                            .offset(x: 18)
                    }
                }
        }
        .frame(maxHeight: .infinity)
        .accessibilityElement(children: .combine)
    }
}

struct StatusLabel: View {
    let model: RemoteViewModel

    var body: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(model.isConnected ? .green : .orange)
                .frame(width: 8, height: 8)
            Text(model.statusText)
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
    }
}
