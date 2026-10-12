// Usage: swift marketing/sfsymbol.swift <symbol|file.svg> <weight> <out.png>
// Renders a real SF Symbol, white on clear, at 100 pt and 4x, for marketing/scenes/common.py.
import AppKit

let args = CommandLine.arguments
guard args.count == 4 else { fatalError("usage: sfsymbol.swift <symbol> <weight> <out.png>") }
let weights: [String: NSFont.Weight] = [
    "regular": .regular, "medium": .medium, "semibold": .semibold, "bold": .bold,
]
guard let weight = weights[args[2]] else { fatalError("unknown weight \(args[2])") }
let config = NSImage.SymbolConfiguration(pointSize: 100, weight: weight)
    .applying(.init(paletteColors: [.white]))
// An .svg path renders that file instead (the Mac app's menu-bar template images).
let image: NSImage
if args[1].hasSuffix(".svg") {
    guard let svg = NSImage(contentsOfFile: args[1]) else { fatalError("cannot read \(args[1])") }
    image = svg
} else {
    guard let sym = NSImage(systemSymbolName: args[1], accessibilityDescription: nil)?
        .withSymbolConfiguration(config) else { fatalError("no symbol \(args[1])") }
    image = sym
}

let scale: CGFloat = args[1].hasSuffix(".svg") ? 16 : 4
let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil, pixelsWide: Int(image.size.width * scale), pixelsHigh: Int(image.size.height * scale),
    bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
    bytesPerRow: 0, bitsPerPixel: 0)!
rep.size = image.size
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
image.draw(in: NSRect(origin: .zero, size: image.size))
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: args[3]))
