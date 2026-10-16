import SwiftUI

/// Compose row of the Keyboard overlay: Close, field, Send. Stays in the hierarchy (hidden) when
/// unfocused so the field always resigns through its own path and never leaves stale text state.
struct TextInputBar: View {
    let model: RemoteViewModel
    @Binding var isFocused: Bool
    var insets = EdgeInsets(top: 12, leading: 20, bottom: 12, trailing: 20)

    @State private var hasText = false

    private static let accent = Color(red: 10 / 255, green: 132 / 255, blue: 1)

    var body: some View {
        HStack(alignment: .bottom, spacing: 10) {
            Button { isFocused = false } label: {
                Image(systemName: "xmark")
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundStyle(.white)
                    .frame(width: 44, height: 44)
                    .background(Color(red: 58 / 255, green: 58 / 255, blue: 60 / 255).opacity(0.92), in: Circle())
            }
            .accessibilityLabel("Close")

            LiveTextField(model: model, isFocused: $isFocused, hasText: $hasText)
                .padding(.horizontal, 16)
                .frame(minHeight: 44)
                .background(
                    Color(red: 44 / 255, green: 44 / 255, blue: 46 / 255),
                    in: RoundedRectangle(cornerRadius: 22, style: .continuous)
                )
                .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).strokeBorder(.white.opacity(0.18), lineWidth: 0.5))
                .shadow(color: .black.opacity(0.4), radius: 15, y: 10)

            Button(action: model.sendText) {
                Image(systemName: "arrow.up")
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundStyle(.white)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle().fill(hasText && model.isConnected
                            ? Self.accent : Color(red: 58 / 255, green: 58 / 255, blue: 60 / 255))
                    )
            }
            .accessibilityLabel("Send")
            .disabled(!model.isConnected)
        }
        // The scrim is always dark, so the row is too.
        .environment(\.colorScheme, .dark)
        .padding(insets)
        .opacity(isFocused ? 1 : 0)
        .allowsHitTesting(isFocused)
        .accessibilityHidden(!isFocused)
        .animation(.easeOut(duration: 0.2), value: isFocused)
    }
}

/// Mirrors each change of its text to the Mac. Thin shell: the diffing lives in `LiveTextSync`.
private struct LiveTextField: UIViewRepresentable {
    let model: RemoteViewModel
    @Binding var isFocused: Bool
    @Binding var hasText: Bool

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeUIView(context: Context) -> BackspaceField {
        let field = BackspaceField()
        field.delegate = context.coordinator
        field.placeholder = "Type to send…"
        field.returnKeyType = .default
        field.font = .preferredFont(forTextStyle: .body)
        field.setContentHuggingPriority(.defaultLow, for: .horizontal)
        field.onEmptyBackspace = { [model] in model.emptyBackspace() }
        field.addTarget(context.coordinator, action: #selector(Coordinator.changed), for: .editingChanged)
        return field
    }

    func updateUIView(_ field: BackspaceField, context: Context) {
        context.coordinator.parent = self
        // Act only when the binding changes: the delegate writes it back asynchronously, so a stale
        // `false` seen mid-focus must not resign the field the user just tapped.
        if isFocused != context.coordinator.lastFocused {
            if isFocused {
                // Stay unacked on failure (e.g. not in a window yet) so the next update retries.
                context.coordinator.lastFocused = field.becomeFirstResponder()
            } else {
                context.coordinator.lastFocused = false
                // Deferred: resigning inside the view update leaves SwiftUI's keyboard inset stale.
                DispatchQueue.main.async { field.resignFirstResponder() }
            }
        }
        // Disconnect or reconnect: the Mac's text is unknown, so start empty.
        if !model.isConnected || context.coordinator.resetCount != model.textResetCount {
            context.coordinator.resetCount = model.textResetCount
            context.coordinator.clear(field)
        }
    }

    func sizeThatFits(_ proposal: ProposedViewSize, uiView: BackspaceField, context: Context) -> CGSize? {
        CGSize(width: proposal.width ?? 200, height: uiView.intrinsicContentSize.height)
    }

    final class BackspaceField: UITextField {
        var onEmptyBackspace: (() -> Void)?

        override func deleteBackward() {
            if (text ?? "").isEmpty { onEmptyBackspace?() }
            super.deleteBackward()
        }

        // Cursor lock (decision 14): the phone cursor always equals the Mac's, at the end.
        override func closestPosition(to point: CGPoint) -> UITextPosition? { endOfDocument }

        // Covers taps, spacebar drag and hardware arrows; composition keeps its own range.
        override var selectedTextRange: UITextRange? {
            get { super.selectedTextRange }
            set {
                if markedTextRange == nil, let end = textRange(from: endOfDocument, to: endOfDocument) {
                    super.selectedTextRange = end
                } else {
                    super.selectedTextRange = newValue
                }
            }
        }

        override func canPerformAction(_ action: Selector, withSender sender: Any?) -> Bool {
            if action == #selector(UIResponder.select(_:)) || action == #selector(UIResponder.selectAll(_:)) {
                return false
            }
            return super.canPerformAction(action, withSender: sender)
        }
    }

    final class Coordinator: NSObject, UITextFieldDelegate {
        var parent: LiveTextField
        var resetCount = 0
        var lastFocused = false

        init(_ parent: LiveTextField) { self.parent = parent }

        func clear(_ field: UITextField) {
            guard !(field.text ?? "").isEmpty else { return }
            field.text = ""
            DispatchQueue.main.async { self.parent.hasText = false }
            parent.model.resetText()
        }

        @objc func changed(_ field: UITextField) {
            // Japanese/Chinese composition: send only once it commits.
            guard field.markedTextRange == nil else { return }
            parent.hasText = !(field.text ?? "").isEmpty
            parent.model.textChanged(field.text ?? "")
        }

        func textFieldDidChangeSelection(_ field: UITextField) {
            // Cursor left the end: mid-text edits would land wrong on the Mac, so re-baseline.
            guard field.markedTextRange == nil, let range = field.selectedTextRange,
                  !range.isEmpty || range.end != field.endOfDocument else { return }
            clear(field)
        }

        func textFieldShouldReturn(_ field: UITextField) -> Bool {
            parent.model.tap(.enter)
            return false
        }

        func textFieldDidBeginEditing(_ field: UITextField) {
            DispatchQueue.main.async { self.parent.isFocused = true }
        }

        func textFieldDidEndEditing(_ field: UITextField) {
            clear(field)
            DispatchQueue.main.async { self.parent.isFocused = false }
        }
    }
}
