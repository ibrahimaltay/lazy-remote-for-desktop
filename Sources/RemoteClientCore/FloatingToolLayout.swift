/// Vertical placement of a floating tool button beside another one on the same edge.
public enum FloatingToolLayout {
    public static let stackSpacing = 70.0

    /// `y` clamped into `range`; if that lands within `spacing` of `other` (the other tool's y on
    /// the same edge), it moves to exactly `spacing` away on the side `y` is already on, or on
    /// the opposite side when that side leaves `range`.
    public static func stackedY(
        _ y: Double, other: Double?, range: ClosedRange<Double>, spacing: Double = stackSpacing
    ) -> Double {
        let y = min(max(y, range.lowerBound), range.upperBound)
        guard let other, abs(y - other) < spacing else { return y }
        let preferred = y >= other ? [other + spacing, other - spacing] : [other - spacing, other + spacing]
        // shortcut: a range too narrow to hold both sides falls back to the plain clamp.
        return preferred.first(where: range.contains) ?? y
    }
}
