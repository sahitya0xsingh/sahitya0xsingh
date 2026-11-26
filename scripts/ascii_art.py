"""Turn assets/photo.jpg into data/ascii-dark.txt and data/ascii-light.txt (the portrait in the neofetch card).

Dark mode draws bright skin with dense characters; light mode draws dark areas densely, so each reads on its page.
Needs Pillow, so it runs locally:  python scripts/ascii_art.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
COLS, ROWS = 54, 30
RAMP = " .:-=+*#%@"   # empty → dense


def main() -> None:
    im = Image.open(ROOT / "assets/photo.jpg").convert("RGB")
    s = min(im.size)
    im = im.crop((int(s * .20), int(s * .07), int(s * .80), int(s * .78)))   # head and shoulders, ~ the card's aspect
    g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
    g = Image.blend(g, ImageOps.equalize(g), .6)
    g = ImageEnhance.Contrast(g).enhance(1.25).filter(ImageFilter.UnsharpMask(radius=3, percent=120))
    w, h = g.size
    mask = Image.new("L", g.size, 0)
    ImageDraw.Draw(mask).ellipse((w * .06, h * .02, w * .94, h * 1.25), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w * .035))
    g, mask = g.resize((COLS, ROWS), Image.LANCZOS), mask.resize((COLS, ROWS), Image.LANCZOS)
    for theme in ("dark", "light"):
        lines = []
        for y in range(ROWS):
            row = ""
            for x in range(COLS):
                v, k = g.getpixel((x, y)) / 255, mask.getpixel((x, y)) / 255
                density = (v if theme == "dark" else 1 - v) * k            # outside the head stays empty
                row += RAMP[min(len(RAMP) - 1, int(density ** .85 * len(RAMP)))]
            lines.append(row)
        (ROOT / f"data/ascii-{theme}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"data/ascii-{theme}.txt")


if __name__ == "__main__":
    main()
