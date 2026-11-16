"""Composes the App Store Connect header and search-results images from the 4K stills (run with .venv/bin/python)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
ICON = os.path.join(HERE, "..", "..", "iOSApp/Assets.xcassets/AppIcon.appiconset/AppIcon.png")
SUB = "Trackpad, keyboard, D-pad and search. Over Bluetooth."   # store copy: no Apple product names


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def frame(name):
    return Image.open(f"{HERE}/frames/{name}.png").convert("RGB")


def sc(*box, ref=3840, w=3840):
    return tuple(round(v * w / ref) for v in box)


def scene(name, height=None, width=None):
    im = frame(name).crop(sc(100, 200, 3670, 1990))   # tight on Mac + phone, drops the corner mark
    w = width or round(im.width * height / im.height)
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def background(w, h):
    return Image.new("RGB", (w, h), "#000000")   # same black as the stills, so no visible seam


def icon(size):
    im = Image.open(ICON).convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), size * 0.225, fill=255)
    im.putalpha(mask)
    return im


def text_block(img, x, cy, u):
    """Icon, two-line headline and subtitle, 6.8u tall in total, vertically centered on cy; left edge at x."""
    d, y = ImageDraw.Draw(img), int(cy - 3.4 * u)
    ic = icon(int(u * 1.6))
    img.paste(ic, (x, y), ic)
    ty = y + int(u * 2.2)
    for l in ["Your phone is now", "your computer's remote."]:
        d.text((x, ty), l, font=font(int(u * 1.5), True), fill="white")
        ty += int(u * 1.8)
    d.text((x, ty + u * 0.3), SUB, font=font(int(u * 0.62)), fill="#C9C3D8")


def header(w, h, name, still):
    img = background(w, h)
    if w / h > 2:   # wide: text left, scene right, both centered vertically
        s = scene(still, height=int(h * 0.74))
        m = int(h * 0.09)
        img.paste(s, (w - m - s.width, (h - s.height) // 2))
        text_block(img, m, h // 2, int(h * 0.04))
    else:           # 16:9: text block on top, scene below, shared left edge
        m = int(h * 0.07)
        s = scene(still, height=int(h * 0.6))
        x = (w - s.width) // 2
        img.paste(s, (x, h - m - s.height))
        text_block(img, x, int((h - m - s.height) / 2), int(h * 0.028))
    img.save(f"{OUT}/{name}.png", optimize=True)
    return img


def search(w, h, name, still):
    img = background(w, h)
    s = scene(still, width=int(w * 0.9))
    x = (w - s.width) // 2
    img.paste(s, (x, h - int(h * 0.05) - s.height))
    text_block(img, x, int((h - int(h * 0.05) - s.height) / 2), int(h * 0.025))
    img.save(f"{OUT}/{name}.png", optimize=True)
    return img


header(3840, 1646, "header-3840x1646", "StillRemote")
header(5244, 2950, "header-5244x2950", "StillRemote")
big = search(3840, 2560, "search-results-3840x2560", "StillSpotlight")
big.resize((1920, 1280), Image.LANCZOS).save(f"{OUT}/search-results-1920x1280.png", optimize=True)


SHOTS = [("StillTrackpad", "Move the cursor", "with one finger"), ("StillRemote", "Arrow keys, play/pause,", "volume and brightness"),
         ("StillKeyboard", "Type on your phone,", "see it on your computer"), ("StillSpotlight", "Search your computer", "from your phone")]
os.makedirs(f"{OUT}/screenshots", exist_ok=True)
for i, (still, l1, l2) in enumerate(SHOTS, 1):   # 6.3" iPhone portrait, 1206x2622
    W, H = 1206, 2622
    img = background(W, H)
    ph = frame(still).crop(sc(2780, 195, 3680, 1995))
    img.paste(ph, ((W - 900) // 2, 620))
    d = ImageDraw.Draw(img)
    for j, l in enumerate([l1, l2]):
        f = font(82, True)
        d.text(((W - d.textlength(l, font=f)) / 2, 200 + j * 100), l, font=f, fill="white")
    img.save(f"{OUT}/screenshots/phone-6.3-{i}-{still[5:].lower()}.png", optimize=True)
