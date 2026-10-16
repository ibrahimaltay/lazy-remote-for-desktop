import SwiftUI

struct TextInputBar: View {
    let model: RemoteViewModel
    @Binding var isFocused: Bool
    var insets = EdgeInsets(top: 4, leading: 20, bottom: 12, trailing: 20)

    var body: some View {
        HStack(alignment: .bottom, spacing: 0) {
            LiveTextField(model: model, isFocused: $isFocused)
                .padding(.horizontal, 16)
                .frame(minHeight: 44)
                .background(
                    Color(.systemGray5),
                    in: RoundedRectangle(cornerRadius: 20, style: .continuous)
                )

            // Always laid out; width and opacity ease with the keyboard (no insertion travel).
            Button(action: model.sendText) {
                Image(systemName: "arrow.up")
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundStyle(Color.white)
                    .frame(width: 42, height: 42)
                    .background(Circle().fill(Color(red: 10 / 255, green: 132 / 255, blue: 1)))
            }
            .accessibilityLabel("Send")
            .opacity(model.isConnected ? 1 : 0.5)
            .disabled(!model.isConnected || !isFocused)
            .padding(.leading, 10)
            .frame(width: isFocused ? 52 : 0, alignment: .trailing)
            .clipped()
            .opacity(isFocused ? 1 : 0)
            .accessibilityHidden(!isFocused)
        }
        .animation(.easeOut(duration: 0.25), value: isFocused)
        .padding(insets)
        // Tapping the bar's padding also opens the keyboard.
        .contentShape(.rect)
        .onTapGesture { isFocused = true }
    }
}

/// Mirrors each change of its text to the Mac. Thin shell: the diffing lives in `LiveTextSync`.
private struct LiveTextField: UIViewRepresentable {
    let model: RemoteViewModel
    @Binding var isFocused: Bool

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
            parent.model.resetText()
        }

        @objc func changed(_ field: UITextField) {
            // Japanese/Chinese composition: send only once it commits.
            guard field.markedTextRange == nil else { return }
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
