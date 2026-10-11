import RemoteProtocol
import SwiftUI

struct DPadOverlay: View {
    let model: RemoteViewModel
    @Binding var isPresented: Bool

    @State private var isShown = false

    var body: some View {
        ZStack {
            // Touch-down, like the typing scrim, so a stray touch only closes the pad.
            Rectangle()
                .fill(.ultraThinMaterial)
                .overlay(Color.black.opacity(0.6))
                .ignoresSafeArea()
                .contentShape(.rect)
                .gesture(DragGesture(minimumDistance: 0).onChanged { _ in close() })
                .accessibilityHidden(true)

            HStack(alignment: .top, spacing: 6) {
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
                    axis: .horizontal, segment: CGSize(width: 70, height: 56), repeats: false
                )
                .offset(y: 60 + 56)
            }
            // Dim as one layer, or the gaps show through the center button.
            .compositingGroup()
            .opacity(model.isConnected ? 1 : 0.35)
            .scaleEffect(isShown ? 1 : 0.92)
            // Sits a little below screen center, toward the thumb.
            .offset(y: 44)
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
            .padding(.bottom, 40)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .bottom)
            .ignoresSafeArea()
        }
        // The backdrop is dark in both appearances, so the pad always uses dark colors.
        .environment(\.colorScheme, .dark)
        .accessibilityAddTraits(.isModal)
        .accessibilityAction(.escape, close)
        .onAppear {
            withAnimation(.easeOut(duration: 0.2)) { isShown = true }
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
                .frame(width: 114, height: 114)
            DPadKey(
                shape: Circle(), size: CGSize(width: 100, height: 100), command: .mid, symbol: "space",
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
        .frame(width: 236, height: 236)
        .clipShape(Circle())
        .shadow(color: .black.opacity(0.5), radius: 25, y: 20)
    }

    private func sideCapsule(_ keys: [(Command, String, String)]) -> some View {
        capsule(keys, axis: .vertical, segment: CGSize(width: 48, height: 71.5), repeats: true)
            .offset(y: -69)
    }

    /// Equal segments 5pt apart, clipped to one capsule, like the function-row keys.
    private func capsule(
        _ keys: [(Command, String, String)], axis: Axis, segment: CGSize, repeats: Bool
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
                        fill: Color(.systemGray4).opacity(0.92), iconSize: 20, iconWeight: .regular,
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
            shape: Wedge(angle: angle), size: CGSize(width: 236, height: 236), command: command,
            symbol: symbol, label: label, fill: Color(.systemGray4).opacity(0.92),
            iconOffset: CGSize(width: 80 * cos(angle.radians), height: 80 * sin(angle.radians)),
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
