import SwiftUI

/// The design's magnifier, drawn in an 18-unit box and scaled to the frame.
/// Stroke widths are in those units.
struct Magnifier: View {
    let size: CGFloat
    let ringWidth: CGFloat
    let handleWidth: CGFloat
    let color: Color

    private struct Ring: Shape {
        func path(in rect: CGRect) -> Path {
            let s = rect.width / 18
            return Path(ellipseIn: CGRect(x: (7.6 - 5.9) * s, y: (7.6 - 5.9) * s, width: 11.8 * s, height: 11.8 * s))
        }
    }

    private struct Handle: Shape {
        func path(in rect: CGRect) -> Path {
            let s = rect.width / 18
            var p = Path()
            p.move(to: CGPoint(x: 12 * s, y: 12 * s))
            p.addLine(to: CGPoint(x: 16.3 * s, y: 16.3 * s))
            return p
        }
    }

    var body: some View {
        let s = size / 18
        ZStack {
            Ring().stroke(color, lineWidth: ringWidth * s)
            Handle().stroke(color, style: StrokeStyle(lineWidth: handleWidth * s, lineCap: .round))
        }
        .frame(width: size, height: size)
        .accessibilityHidden(true)
    }
}

struct SpotlightOverlay: View {
    let model: RemoteViewModel
    /// Closes and clears. `true` when the Mac's Spotlight should be closed too.
    let close: (_ closeMac: Bool) -> Void

    @State private var query = ""
    @FocusState private var isFocused: Bool

    private let placeholderColor = Color(red: 235 / 255, green: 235 / 255, blue: 245 / 255)

    var body: some View {
        ZStack(alignment: .top) {
            // Touch-down, so a stray touch never reaches what is underneath.
            Color.black.opacity(0.45)
                .ignoresSafeArea()
                .contentShape(.rect)
                .gesture(DragGesture(minimumDistance: 0).onChanged { _ in close(true) })
                .accessibilityElement()
                .accessibilityLabel("Spotlight Search")
                .accessibilityAddTraits(.isModal)
                .accessibilityAction(named: "Close Spotlight") { close(true) }

            pill
                .padding(.horizontal, 14)
                .padding(.top, 70)
        }
        .onAppear { isFocused = true }
    }

    private var pill: some View {
        HStack(spacing: 12) {
            Magnifier(size: 22, ringWidth: 1.6, handleWidth: 1.8, color: placeholderColor.opacity(0.6))
            TextField(
                "",
                text: $query,
                prompt: Text("Spotlight Search").foregroundStyle(placeholderColor.opacity(0.55))
            )
            .font(.system(size: 22))
            .foregroundStyle(.white)
            .tint(.white)
            .lineLimit(1)
            .focused($isFocused)
            .submitLabel(.go)
            .onSubmit(go)
            .preferredColorScheme(.dark)
        }
        .padding(.horizontal, 20)
        .frame(height: 56)
        .background {
            Capsule().fill(.ultraThinMaterial)
            Capsule().fill(Color(red: 74 / 255, green: 70 / 255, blue: 68 / 255).opacity(0.82))
        }
        .overlay(Capsule().strokeBorder(.white.opacity(0.18), lineWidth: 0.5))
        .shadow(color: .black.opacity(0.4), radius: 15, y: 10)
    }

    private func go() {
        let text = query
        if text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            close(true)
        } else {
            model.submitSpotlight(text)
            close(false)
        }
    }
}
