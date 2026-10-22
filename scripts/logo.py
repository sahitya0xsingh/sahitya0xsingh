"""Turn the logo into a grid of brightness levels (0-4) for the code-glyph render.

Source priority:
  1. assets/logo.png (or .jpg) committed to the repo
  2. the GitHub avatar of PROFILE_LOGIN (downloaded at run time)
  3. the built-in "0x" pixel monogram
Pillow is used for 1 and 2 when available; without it the monogram is used.
"""
from __future__ import annotations

import io
import urllib.request

from common import ASSETS, LOGIN

LAST_GLOW: bytes | None = None  # small JPEG of the logo, set when an image logo is used

ZERO = [".#####.", "##...##", "##...##", "##..###", "##.#.##", "###..##", "##...##", "##...##", ".#####."]
XCH = [".......", ".......", ".......", "##...##", ".##.##.", "..###..", "..###..", ".##.##.", "##...##"]


def _monogram(cols: int, rows: int) -> list[list[int]]:
    bmp = [ZERO[r] + ".." + XCH[r] for r in range(9)]
    bw, bh = len(bmp[0]), len(bmp)
    sx, sy = cols * 0.8 / bw, rows * 0.62 / bh
    ox, oy = (cols - bw * sx) / 2, (rows - bh * sy) / 2
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            bx, by = (c - ox) / sx, (r - oy) / sy
            if 0 <= bx < bw and 0 <= by < bh and bmp[int(by)][int(bx)] == "#":
                fx, fy = bx - int(bx), by - int(by)
                edge = min(fx, 1 - fx, fy, 1 - fy)
                row.append(4 if edge > .18 else 3)
            else:
                # faint halo around the shapes
                near = any(0 <= int((c + dx - ox) / sx) < bw and 0 <= int((r + dy - oy) / sy) < bh
                           and (c + dx - ox) >= 0 and (r + dy - oy) >= 0
                           and bmp[int((r + dy - oy) / sy)][int((c + dx - ox) / sx)] == "#"
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                row.append(1 if near else 0)
        grid.append(row)
    return grid


def _image_bytes() -> tuple[bytes | None, str]:
    for name in ("logo.png", "logo.jpg", "logo.jpeg", "logo.webp"):
        p = ASSETS / name
        if p.exists():
            return p.read_bytes(), f"assets/{name}"
    try:
        req = urllib.request.Request(f"https://github.com/{LOGIN}.png?size=400",
                                     headers={"User-Agent": "terminal-profile"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read(), "github avatar"
    except Exception:
        return None, ""


def logo_grid(cols: int, rows: int):
    """Returns (levels, colours, source). colours is None for the monogram."""
    data, src = _image_bytes()
    if data is None:
        return _monogram(cols, rows), None, "0x monogram"
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return _monogram(cols, rows), None, "0x monogram (no Pillow)"
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
    except Exception:
        return _monogram(cols, rows), None, "0x monogram (unreadable image)"

    if im.mode in ("RGBA", "LA") or "transparency" in im.info:
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
        im = Image.alpha_composite(bg, im)
    rgb = im.convert("RGB")
    # trim empty margins, then pad back to a square so the mark fills the scan box
    box = rgb.convert("L").point(lambda v: 255 if v > 28 else 0).getbbox()
    if box:
        rgb = rgb.crop(box)
    corner = rgb.getpixel((0, 0))
    side = int(max(rgb.size) * 1.04)
    sq = Image.new("RGB", (side, side), corner)
    sq.paste(rgb, ((side - rgb.width) // 2, (side - rgb.height) // 2))
    rgb = sq
    glow_buf = io.BytesIO()
    sq.resize((220, 220), Image.LANCZOS).save(glow_buf, "JPEG", quality=70)
    global LAST_GLOW
    LAST_GLOW = glow_buf.getvalue()
    rgb = rgb.resize((cols, rows), Image.LANCZOS)
    g = ImageOps.autocontrast(rgb.convert("L"), cutoff=2)
    px = list(g.getdata())
    cpx = list(rgb.getdata())
    # subject should glow on a dark field: invert if the border is mostly light
    border = [px[i] for i in range(cols)] + [px[-i - 1] for i in range(cols)]
    inverted = sum(border) / len(border) > 140
    if inverted:
        px = [255 - v for v in px]
    grid, colours = [], []
    for r in range(rows):
        row, crow = [], []
        for c in range(cols):
            v = px[r * cols + c]
            lvl = 0 if v < 34 else 1 if v < 80 else 2 if v < 135 else 3 if v < 190 else 4
            row.append(lvl)
            crow.append(None if inverted or not lvl else _tint(cpx[r * cols + c], lvl))
        grid.append(row)
        colours.append(crow)
    # thicken neon strokes sideways: glyphs are narrow, so thin lines would vanish
    for r in range(rows):
        src_row, src_col = grid[r][:], colours[r][:]
        for c in range(cols):
            for dc in (-1, 1):
                n = c + dc
                if 0 <= n < cols and src_row[n] >= 3 and grid[r][c] < 3:
                    grid[r][c] = 3
                    colours[r][c] = src_col[n] if not inverted else None
    return grid, (None if inverted else colours), src


def _tint(rgb, lvl: int) -> str:
    """Keep the logo's own hue, lift it so it reads as light on a dark screen, quantise for small SVGs."""
    r, g, b = rgb
    peak = max(r, g, b, 1)
    target = (70, 105, 170, 235, 255)[lvl]
    k = max(1.0, target / peak)
    q = lambda v: min(255, int(round(v * k / 24) * 24))
    if lvl == 4:  # hottest pixels bloom toward white
        return "#{:02x}{:02x}{:02x}".format(*(min(255, q(v) + 40) for v in (r, g, b)))
    return "#{:02x}{:02x}{:02x}".format(q(r), q(g), q(b))
