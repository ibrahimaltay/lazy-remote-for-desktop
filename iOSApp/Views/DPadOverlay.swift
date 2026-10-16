import RemoteProtocol
import SwiftUI

struct DPadOverlay: View {
    let model: RemoteViewModel
    @Binding var isPresented: Bool

    @State private var isShown = false
    @State private var armed = false
    @State private var armTask: Task<Void, Never>?
    @Environment(\.verticalSizeClass) private var verticalSizeClass

    private var compact: Bool { verticalSizeClass == .compact }
    private var padSize: CGFloat { compact ? 210 : 236 }

    var body: some View {
        ZStack {
            // Tap on lift; the first tap only arms for 1s so a stray touch can't close the pad.
            ToolScrim()
                .contentShape(.rect)
                .onTapGesture(perform: backdropTapped)
                .accessibilityHidden(true)

            HStack(alignment: compact ? .center : .top, spacing: compact ? 14 : 6) {
                sideCapsule([
                    (.brightnessUp, "sun.max", "Brightness up"),
                    (.brightnessDown, "sun.min", "Brightness down"),
                ])
                pad
                sideCapsule([
                    (.volumeUp, "speaker.wave.3", "Volume up"),
                    (.volumeDown, "speaker.wave.1", "Volume down"),
                ])
            }
            .overlay(alignment: .bottom) {
                capsule(
                    [
                        (.previousTrack, "backward", "Previous track"),
                        (.playPause, "playpause", "Play / Pause"),
                        (.nextTrack, "forward", "Next track"),
                    ],
                    axis: .horizontal, segment: compact ? CGSize(width: 200.0 / 3, height: 50) : CGSize(width: 70, height: 56),
                    repeats: false, iconSize: 20
                )
                .offset(y: compact ? 18 + 50 : 60 + 56)
            }
            // Dim as one layer, or the gaps show through the center button.
            .compositingGroup()
            .opacity(model.isConnected ? 1 : 0.35)
            .scaleEffect(isShown ? 1 : 0.92)
            // Sits a little below screen center, toward the thumb.
            .offset(y: compact ? -34 : 44)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .ignoresSafeArea()

            Button(action: close) {
                Image(systemName: "xmark")
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundStyle(.white)
                    .frame(width: 44, height: 44)
                    .background(Color(.systemGray4).opacity(0.8), in: Circle())
            }
            .accessibilityLabel("Close")
            .padding(compact ? .top : .bottom, compact ? 20 : 40)
            .padding(.trailing, compact ? 72 : 0)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: compact ? .topTrailing : .bottom)
            .ignoresSafeArea()

            Text("Tap again to close")
                .font(.caption)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 10)
                .padding(.vertical, 5)
                .background(.regularMaterial, in: Capsule())
                .opacity(armed ? 1 : 0)
                .animation(.easeOut(duration: 0.2), value: armed)
                .padding(compact ? .top : .bottom, compact ? 20 + 44 + 12 : 40 + 44 + 12)
                .padding(.trailing, compact ? 72 : 0)
                .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: compact ? .topTrailing : .bottom)
                .ignoresSafeArea()
                .allowsHitTesting(false)
                .accessibilityHidden(true)
        }
        // The backdrop is dark in both appearances, so the pad always uses dark colors.
        .environment(\.colorScheme, .dark)
        .accessibilityAddTraits(.isModal)
        .accessibilityAction(.escape, close)
        .onAppear {
            withAnimation(.easeOut(duration: 0.2)) { isShown = true }
        }
        .onDisappear { armTask?.cancel() }
    }

    private func backdropTapped() {
        if armed { return close() }
        armed = true
        armTask?.cancel()
        armTask = Task {
            try? await Task.sleep(for: .seconds(1))
            if !Task.isCancelled { armed = false }
        }
    }

    private var pad: some View {
        ZStack {
            // Swallows touches in the gaps so they don't reach the backdrop and close the pad.
            Color.clear.contentShape(Circle())
            segment(.up, "chevron.up", "Up", degrees: -90)
            segment(.right, "chevron.right", "Right", degrees: 0)
            segment(.down, "chevron.down", "Down", degrees: 90)
            segment(.left, "chevron.left", "Left", degrees: 180)
            Circle()
                .fill(Color(red: 10 / 255, green: 10 / 255, blue: 12 / 255).opacity(0.85))
                .frame(width: compact ? 102 : 114, height: compact ? 102 : 114)
            DPadKey(
                shape: Circle(), size: CGSize(width: compact ? 88 : 100, height: compact ? 88 : 100), command: .mid, symbol: "space",
                label: "Space", fill: Color(.systemGray3), iconSize: 30, model: model
            )
            .overlay {
                Circle()
                    .strokeBorder(
                        LinearGradient(colors: [.white.opacity(0.12), .clear], startPoint: .top, endPoint: .center),
                        lineWidth: 1
                    )
                    .allowsHitTesting(false)
            }
        }
        .frame(width: padSize, height: padSize)
        .clipShape(Circle())
        .shadow(color: .black.opacity(0.5), radius: 25, y: 20)
    }

    private func sideCapsule(_ keys: [(Command, String, String)]) -> some View {
        capsule(
            keys, axis: .vertical, segment: compact ? CGSize(width: 44, height: 63.5) : CGSize(width: 48, height: 71.5),
            repeats: true, iconSize: compact ? 24 : 20
        )
        .offset(y: compact ? 0 : -69)
    }

    /// Equal segments 5pt apart, clipped to one capsule, like the function-row keys.
    private func capsule(
        _ keys: [(Command, String, String)], axis: Axis, segment: CGSize, repeats: Bool, iconSize: CGFloat
    ) -> some View {
        let layout = axis == .vertical
            ? AnyLayout(VStackLayout(spacing: 5)) : AnyLayout(HStackLayout(spacing: 5))
        return ZStack {
            // Swallows touches in the gaps so they don't reach the backdrop and close the pad.
            Color.clear.contentShape(Capsule())
            layout {
                ForEach(keys, id: \.0) { command, symbol, label in
                    DPadKey(
                        shape: Rectangle(), size: segment, command: command, symbol: symbol, label: label,
                        fill: Color(.systemGray4).opacity(0.92), iconSize: iconSize, iconWeight: .regular,
                        repeats: repeats, model: model
                    )
                }
            }
        }
        .fixedSize()
        .clipShape(Capsule())
        .shadow(color: .black.opacity(0.5), radius: 25, y: 20)
    }

    private func segment(_ command: Command, _ symbol: String, _ label: String, degrees: Double) -> some View {
        let angle = Angle.degrees(degrees)
        return DPadKey(
            shape: Wedge(angle: angle), size: CGSize(width: padSize, height: padSize), command: command,
            symbol: symbol, label: label, fill: Color(.systemGray4).opacity(0.92),
            iconOffset: CGSize(width: padSize * 80 / 236 * cos(angle.radians), height: padSize * 80 / 236 * sin(angle.radians)),
            model: model
        )
    }

    private func close() {
        withAnimation(.easeOut(duration: 0.2)) { isPresented = false }
    }
}

/// A quarter of the pad centered on `angle`, pushed outward so neighbors are 5pt apart.
private struct Wedge: Shape {
    let angle: Angle

    func path(in rect: CGRect) -> Path {
        // Shifting along the bisector by d moves each straight edge d/√2 away from its neighbor's.
        let shift = 2.5 * sqrt(2)
        let tip = CGPoint(
            x: rect.midX + shift * cos(angle.radians),
            y: rect.midY + shift * sin(angle.radians)
        )
        var path = Path()
        path.move(to: tip)
        path.addRelativeArc(
            center: tip, radius: min(rect.width, rect.height) / 2,
            startAngle: angle - .degrees(45), delta: .degrees(90)
        )
        path.closeSubpath()
        return path
    }
}

/// Press on touch-down, release on lift or when the finger leaves the shape;
/// the Mac repeats held keys, while `repeats` keys re-tap from here because system keys don't.
private struct DPadKey<S: Shape>: View {
    let shape: S
    let size: CGSize
    let command: Command
    let symbol: String
    let label: String
    let fill: Color
    var iconOffset = CGSize.zero
    var iconSize: CGFloat = 26
    var iconWeight = Font.Weight.semibold
    var repeats = false
    let model: RemoteViewModel

    @State private var isPressed = false
    @State private var hasLeft = false
    @State private var repeatTask: Task<Void, Never>?
    // Resets on cancellation too, where onEnded never fires and a key would stay held.
    @GestureState private var isTouching = false

    var body: some View {
        shape
            .fill(isPressed ? Color.accentColor : fill)
            .overlay {
                Image(systemName: symbol)
                    .font(.system(size: iconSize, weight: iconWeight))
                    .foregroundStyle(.white)
                    .offset(iconOffset)
            }
            .animation(.easeOut(duration: 0.12), value: isPressed)
            .frame(width: size.width, height: size.height)
            .contentShape(shape)
            .gesture(
                DragGesture(minimumDistance: 0)
                    .updating($isTouching) { _, touching, _ in touching = true }
                    .onChanged { value in
                        guard !hasLeft else { return }
                        let bounds = CGRect(origin: .zero, size: size)
                        if !shape.path(in: bounds).contains(value.location) {
                            hasLeft = true
                            release()
                        } else if !isPressed, model.isConnected {
                            isPressed = true
                            press()
                        }
                    }
            )
            .onChange(of: isTouching) { _, touching in
                guard !touching else { return }
                hasLeft = false
                release()
            }
            .onDisappear(perform: release)
            .accessibilityElement()
            .accessibilityLabel(label)
            .accessibilityAddTraits(.isButton)
            .accessibilityAction { model.tap(command) }
    }

    private func press() {
        guard repeats else { return model.press(command) }
        model.tap(command)
        repeatTask = Task {
            try? await Task.sleep(for: .milliseconds(450))
            while !Task.isCancelled {
                model.tap(command, feedback: false)
                try? await Task.sleep(for: .milliseconds(100))
            }
        }
    }

    private func release() {
        guard isPressed else { return }
        isPressed = false
        if repeats {
            repeatTask?.cancel()
            repeatTask = nil
        } else {
            model.release(command)
        }
    }
}

/// Backdrop shared by the Remote and Keyboard overlays.
struct ToolScrim: View {
    var body: some View {
        Rectangle()
            .fill(.ultraThinMaterial)
            .overlay(Color(red: 10 / 255, green: 10 / 255, blue: 12 / 255).opacity(0.74))
            .ignoresSafeArea()
    }
}
