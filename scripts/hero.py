"""Build assets/hero.svg: a blueprint sheet. The portrait is plotted from the photo as wavy pen lines that draw
themselves row by row; name and details sit in an engineering title block.

Needs Pillow, so it runs locally (not in the workflow):  python scripts/hero.py
"""
from __future__ import annotations

import base64
import datetime as dt
import io
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from theme import DIM, FAINT, INK, MONO, PAPER, PEN, SANS, appear, dim_h, dim_v, draw_in, label, sheet, svg  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent
W, H = 1000, 540
PX, PY, S = 64, 70, 340          # portrait box
ROWS = 86


def engraved_rows() -> list[str]:
    """Each row is a ribbon whose thickness follows the photo's brightness (white ink on blue = a positive image)."""
    im = Image.open(ROOT / "assets/photo.jpg").convert("RGB")
    s = min(im.size)
    im = im.crop((int(s * .14), int(s * .03), int(s * .86), int(s * .75)))
    g = ImageOps.grayscale(im)
    g = ImageOps.autocontrast(ImageEnhance.Contrast(g).enhance(1.25), cutoff=1)
    w, h = g.size
    mask = Image.new("L", g.size, 0)
    ImageDraw.Draw(mask).ellipse((w * .14, h * .0, w * .86, h * 1.3), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w * .06))
    g = Image.composite(g, Image.new("L", g.size, 0), mask).resize((S // 2 + 1, ROWS), Image.BILINEAR)
    gap = S / ROWS
    rows = []
    for r in range(ROWS):
        y0 = PY + (r + .5) * gap
        top, bot = [], []
        for i in range(S // 2 + 1):
            x = PX + i * 2
            v = (g.getpixel((i, r)) / 255) ** 1.1
            t = .25 + v * gap * .92
            wob = math.sin(i * .21 + r * .7) * gap * .12
            top.append(f"{x},{y0 + wob - t / 2:.1f}")
            bot.append(f"{x},{y0 + wob + t / 2:.1f}")
        rows.append("M" + " L".join(top) + " L" + " L".join(reversed(bot)) + "Z")
    return rows


def duotone_photo(px: int = 1020) -> str:
    """The portrait as a sharp blueprint-tinted photo (3x the display size, so it stays crisp on retina screens)."""
    im = Image.open(ROOT / "assets/photo.jpg").convert("RGB")
    s = min(im.size)
    im = im.crop((int(s * .14), int(s * .03), int(s * .86), int(s * .75))).resize((px, px), Image.LANCZOS)
    g = ImageOps.grayscale(im)
    g = ImageOps.autocontrast(g, cutoff=1)
    g = Image.blend(g, ImageOps.equalize(g), .35)                         # a little local punch
    g = g.filter(ImageFilter.UnsharpMask(radius=2.2, percent=140, threshold=2))
    w, h = g.size
    mask = Image.new("L", g.size, 0)
    ImageDraw.Draw(mask).ellipse((w * .1, -h * .02, w * .9, h * 1.3), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w * .07))
    g = Image.composite(g, ImageEnhance.Brightness(g).enhance(.35), mask)  # dim the busy background
    col = ImageOps.colorize(g, black=PAPER, mid="#5b93d6", white="#f6faff", blackpoint=6, whitepoint=238, midpoint=112)
    buf = io.BytesIO()
    col.save(buf, "JPEG", quality=90, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode()


def fx(f: float) -> float:
    return PX + f * S


def fy(f: float) -> float:
    return PY + f * S


def face_effects(t0: float) -> str:
    """Effects on the portrait once it is plotted: a scan beam that lights the lines it crosses, a short glitch,
    focus brackets around the face and drafting marks (centre line, eye line)."""
    b = f"{t0:.2f}s"
    out = (f'<filter id="warm" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" '
           f'values=".33 .65 .12 0 .06  .26 .5 .1 0 .03  .08 .16 .03 0 0  0 0 0 1 0"/></filter>')
    out += f'<clipPath id="pbox"><rect x="{PX}" y="{PY}" width="{S}" height="{S}"/></clipPath><g clip-path="url(#pbox)">'
    # 1. scan beam: a band of the portrait re-drawn in warm light, sweeping down every 7 s
    out += (f'<clipPath id="band"><rect x="{PX}" y="{PY - 40}" width="{S}" height="34">'
            f'<animate attributeName="y" values="{PY - 40};{PY + S + 6};{PY + S + 6}" keyTimes="0;.5;1" dur="7s" begin="{b}" repeatCount="indefinite"/></rect></clipPath>'
            f'<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PEN}" stop-opacity="0"/>'
            f'<stop offset=".8" stop-color="{PEN}" stop-opacity=".16"/><stop offset="1" stop-color="#fff3c4" stop-opacity=".42"/></linearGradient>'
            f'<g clip-path="url(#band)"><rect x="{PX}" y="{PY - 60}" width="{S}" height="{S + 120}" fill="url(#beam)">'
            f'<animate attributeName="y" values="{PY - 74};{PY + S - 28};{PY + S - 28}" keyTimes="0;.5;1" dur="7s" begin="{b}" repeatCount="indefinite"/>'
            f'<animate attributeName="height" values="34;34;34" dur="7s"/></rect></g>'
            f'<rect x="{PX}" y="{PY - 8}" width="{S}" height="1.6" fill="{PEN}" filter="url(#glowY)">'
            f'<animate attributeName="y" values="{PY - 8};{PY + S + 38};{PY + S + 38}" keyTimes="0;.5;1" dur="7s" begin="{b}" repeatCount="indefinite"/></rect>')
    # 2. glitch: two slices jump sideways for a blink, every 5 s
    for k, (y, h, dx) in enumerate([(.36, 12, 9), (.63, 16, -7)]):
        out += (f'<clipPath id="sl{k}"><rect x="{PX}" y="{fy(y):.0f}" width="{S}" height="{h}"/></clipPath>'
                f'<g clip-path="url(#sl{k})" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="0;.86;.865;.9;.905;1" dur="5s" begin="{t0 + 1 + k * .4:.2f}s" repeatCount="indefinite"/>'
                
                f'<use href="#facephoto" transform="translate({dx} 0)"/>'
                f'<rect x="{PX}" y="{fy(y):.0f}" width="{S}" height="{h}" fill="#4cc9ff" opacity=".18"/></g>')
    out += '</g>'
    # 3. focus brackets around the face, pulsing, with a small tag
    x0, y0, x1, y1, L = fx(.2), fy(.2), fx(.79), fy(.92), 18
    br = "".join(f'<path d="M{x},{y + sy * L} V{y} H{x + sx * L}" fill="none" stroke="{PEN}" stroke-width="2" stroke-linecap="round"/>'
                 for x, y, sx, sy in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)])
    out += appear(t0 + .2, f'<g filter="url(#glowY)">{br}<animate attributeName="opacity" values="1;.45;1" dur="2.4s" repeatCount="indefinite"/></g>'
                  f'<rect x="{x0}" y="{y0 - 19}" width="118" height="15" fill="{PEN}"/>'
                  + label(x0 + 5, y0 - 8, "SUBJECT · S. SINGH", 8.5, PAPER, ls=1))
    # 4. drafting marks: centre line and eye line
    cx = fx(.49)
    ex1, ey1, ex2, ey2 = fx(.345), fy(.585), fx(.55), fy(.53)
    out += (appear(t0 + .4, f'<line x1="{cx:.0f}" y1="{fy(.14):.0f}" x2="{cx:.0f}" y2="{fy(.98):.0f}" stroke="{PEN}" stroke-width="1" '
                             f'stroke-dasharray="14 4 3 4" opacity=".8" filter="url(#glowY)"/>')
            + appear(t0 + .9, label(cx + 6, fy(.17), "℄", 13, PEN, ls=0))
            + draw_in(f"M{ex1:.0f},{ey1:.0f} L{ex2:.0f},{ey2:.0f}", t0 + .7, .5, PEN, 1.4, extra='marker-start="url(#arr)" marker-end="url(#arr)"')
            + appear(t0 + 1.1, f'<circle cx="{ex1:.0f}" cy="{ey1:.0f}" r="9" fill="none" stroke="{PEN}" stroke-width="1.2" filter="url(#glowY)">'
                     f'<animate attributeName="r" values="8;11;8" dur="2s" repeatCount="indefinite"/></circle>'
                     f'<circle cx="{ex2:.0f}" cy="{ey2:.0f}" r="9" fill="none" stroke="{PEN}" stroke-width="1.2" filter="url(#glowY)">'
                     f'<animate attributeName="r" values="8;11;8" dur="2s" begin=".3s" repeatCount="indefinite"/></circle>'))
    return out


def build() -> str:
    rows = engraved_rows()
    # the plotter works top to bottom: each row appears in turn, a pen head rides along
    plot = '<g filter="url(#glow)"><g id="facepaths">' + "".join(f'<path d="{d}" fill="{INK}" opacity="0"><set attributeName="opacity" to="1" begin="{.3 + i * .03:.2f}s" fill="freeze"/></path>'
                   for i, d in enumerate(rows)) + '</g></g>'
    end = .3 + len(rows) * .03
    plot += (f'<rect x="{PX - 4}" y="{PY}" width="{S + 8}" height="2" fill="{PEN}" filter="url(#glowY)">'
             f'<animate attributeName="y" from="{PY}" to="{PY + S}" begin=".3s" dur="{end - .3:.2f}s" fill="freeze"/>'
             f'<set attributeName="opacity" to="0" begin="{end:.2f}s" fill="freeze"/></rect>')
    photo = (f'<pattern id="engr" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height=".8" fill="{PAPER}" opacity=".13"/></pattern>'
             f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{end:.2f}s" dur="1.4s" fill="freeze"/>'
             f'<defs><image id="facephoto" href="data:image/jpeg;base64,{duotone_photo()}" x="{PX}" y="{PY}" width="{S}" height="{S}"/></defs>'
             f'<use href="#facephoto"/>'
             f'<rect x="{PX}" y="{PY}" width="{S}" height="{S}" fill="url(#engr)"/></g>')
    plot += photo + face_effects(end)
    portrait = (f'<rect x="{PX - 6}" y="{PY - 6}" width="{S + 12}" height="{S + 12}" fill="{PAPER}" stroke="{DIM}" stroke-width=".8" filter="url(#glow)"/>'
                + plot
                + dim_h(PX, PX + S, PY + S + 26, "340") + dim_v(PX - 28, PY, PY + S, "340")
                + appear(3.6, f'<path d="M{PX + S - 40},{PY + 60} L{PX + S + 40},{PY + 22} H{PX + S + 70}" fill="none" stroke="{PEN}" stroke-width="1.4" filter="url(#glowY)"/>'
                              f'<circle cx="{PX + S - 40}" cy="{PY + 60}" r="3" fill="{PEN}" filter="url(#glowY)"><animate attributeName="r" values="3;5;3" dur="2s" repeatCount="indefinite"/></circle>'
                              + label(PX + S + 76, PY + 26, "FIG. 1 — THE AUTHOR,", 10, PEN, ls=1)
                              + label(PX + S + 76, PY + 40, "PLOTTED FROM A PHOTO", 10, PEN, ls=1)))

    x0 = 512
    name = (appear(.4, label(x0, 150, "SHEET 01 · PROFILE", 11, DIM, ls=3)
                   + f'<text x="{x0 - 3}" y="214" font-family="{SANS}" font-size="64" font-weight="800" fill="{INK}" letter-spacing="-2" filter="url(#glowT)">Sahitya</text>'
                     f'<text x="{x0 - 3}" y="278" font-family="{SANS}" font-size="64" font-weight="800" fill="{INK}" letter-spacing="-2" filter="url(#glowT)">Singh</text>')
            + draw_in(f"M{x0},292 C{x0 + 60},286 {x0 + 140},298 {x0 + 196},289", 1.2, .6, PEN, 3, 260)
            + appear(1.4, label(x0, 326, "OPEN-SOURCE CONTRIBUTOR · CS STUDENT", 11.5, INK, ls=1.5)
                     + label(x0, 346, "ship small, ship often.", 13, PEN, ls=.4)))

    # title block, bottom right
    tx, ty, tw = 512, 380, 424
    today = dt.date.today().strftime("%d %b %Y").upper()
    cells = [(0, 0, 212, "DRAWN BY", "@sahityasingh08"), (212, 0, 212, "LOCATION", "BENGALURU, IN"),
             (0, 44, 212, "COMMUNITY", "openSUSE"), (212, 44, 212, "CONTRIBUTES TO", "checkstyle"),
             (0, 88, 141, "BUILDING", "PreFlight"), (141, 88, 141, "SCALE", "1 : 1"), (282, 88, 142, "REVISED", today)]
    block = f'<rect x="{tx}" y="{ty}" width="{tw}" height="132" fill="{PAPER}" stroke="{INK}" stroke-width="1.4" filter="url(#glow)"/>'
    for cx, cy, cw, k, v in cells:
        block += (f'<rect x="{tx + cx}" y="{ty + cy}" width="{cw}" height="44" fill="none" stroke="{DIM}" stroke-width=".8"/>'
                  + label(tx + cx + 10, ty + cy + 15, k, 8.5, DIM, ls=1.6)
                  + label(tx + cx + 10, ty + cy + 34, v, 13, INK, ls=.6))
    return svg(W, H, sheet(W, H) + portrait + name + appear(2, block))


if __name__ == "__main__":
    out = ROOT / "assets/hero.svg"
    out.write_text(build(), encoding="utf-8")
    print("wrote", out.name, out.stat().st_size // 1024, "KB")
