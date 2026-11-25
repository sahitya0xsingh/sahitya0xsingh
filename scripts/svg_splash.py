"""Start page: the logo, rebuilt from this repo's own source code, revealed by a laser scan."""
from __future__ import annotations

from pathlib import Path

from common import (ACCENT, BG, BRIGHT, GREEN, LINE, LINE2, MONO, MUTED, TEXT,
                    esc, glow, svg_open)
from frame import hud_frame, scanlines
import base64

import logo as logo_mod
from logo import logo_grid

W, H = 1000, 600
FS, CWID, LH = 6, 3.6, 6          # glyph size, advance, line height
COLS = 110
ROWS = round(COLS * CWID / LH)       # keeps the logo square
BX, BY = (W - COLS * CWID) / 2, 96   # logo box
SCAN_START, SCAN_DUR = 0.7, 2.6
LEVEL_FILL = [None, "#1d3d63", "#2f6fb3", ACCENT, "#d6eaff"]


def _code_stream() -> str:
    """Every non-space character of this repo's scripts: the logo is literally made of its code."""
    src = "".join(p.read_text(encoding="utf-8") for p in sorted(Path(__file__).parent.glob("*.py")))
    s = "".join(ch for ch in src if not ch.isspace() and 33 <= ord(ch) < 127)
    return s or "0x17"


def _stamp(t: float, t_end: float | None, body: str) -> str:
    """Visible from t until t_end."""
    hide = f'<set attributeName="opacity" to="0" begin="{t_end:.2f}s" fill="freeze"/>' if t_end else ""
    return (f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>{hide}'
            f'{body}</g>')


PHOTO_PX = 320  # embedded size: crisp on retina, small enough to keep the svg light


def _photo_b64() -> str | None:
    """assets/photo.jpg (or .png), downscaled and embedded so GitHub's image proxy can render it."""
    root = Path(__file__).resolve().parent.parent / "assets"
    src = next((root / n for n in ("photo.jpg", "photo.jpeg", "photo.png") if (root / n).exists()), None)
    if not src:
        return None
    try:
        import io
        from PIL import Image
        im = Image.open(src).convert("RGB")
        side = min(im.size)
        im = im.crop(((im.width - side) // 2, (im.height - side) // 2,
                      (im.width + side) // 2, (im.height + side) // 2)).resize((PHOTO_PX, PHOTO_PX), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=84, optimize=True)
        data = buf.getvalue()
    except ImportError:
        data = src.read_bytes()
    return base64.b64encode(data).decode()


def _portrait(prof: dict, x0: float, x1: float, t_lock: float) -> str:
    """Holographic ID card: the photo materialises as a cyan hologram, glitches, then locks into full colour."""
    b64 = _photo_b64()
    cx, cy, r = (x0 + x1) / 2, 196, 84
    out = []
    # orbiting rings
    ring = lambda rr, dash, dur, sw, col, op: (
        f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{col}" stroke-width="{sw}" '
        f'stroke-dasharray="{dash}" opacity="{op}"><animateTransform attributeName="transform" type="rotate" '
        f'from="0 {cx} {cy}" to="{360 if dur > 0 else -360} {cx} {cy}" dur="{abs(dur)}s" repeatCount="indefinite"/></circle>')
    out.append(_stamp(.1, None, ring(r + 9, "60 8 4 8", 18, 1.6, ACCENT, .9) + ring(r + 17, "2 6", -30, 1, ACCENT, .55)
                      + ring(r + 24, "120 60", 11, .8, "#a371f7", .5)))
    # tick marks at the cardinal points
    ticks = "".join(f'<path d="M{cx},{cy - r - 30}v8" stroke="{ACCENT}" stroke-width="1.4" transform="rotate({a} {cx} {cy})"/>'
                    for a in (0, 90, 180, 270))
    out.append(_stamp(.1, None, ticks))
    if b64:
        img = lambda extra="", flt="": (f'<image href="data:image/jpeg;base64,{b64}" x="{cx - r}" y="{cy - r}" '
                                        f'width="{2 * r}" height="{2 * r}" clip-path="url(#pclip)"{flt}>{extra}</image>')
        # phase 1: flickering cyan hologram with an rgb-split glitch
        holo = (f'<g opacity="0"><animate attributeName="opacity" values="0;.9;.3;1;.6;1" keyTimes="0;.15;.25;.4;.5;1" '
                f'begin=".2s" dur="1s" fill="freeze"/>'
                f'<animate attributeName="opacity" to="0" begin="{t_lock + .25:.2f}s" dur=".5s" fill="freeze"/>'
                + img('<animate attributeName="x" values="{0};{1};{0};{2};{0}" keyTimes="0;.1;.2;.3;1" dur="2.3s" '
                      'repeatCount="indefinite"/>'.format(cx - r, cx - r + 5, cx - r - 4), ' filter="url(#holoR)" opacity=".6"')
                + img("", ' filter="url(#holo)"') + '</g>')
        # phase 2: true colour, wiped in top-down when the scan locks
        real = (f'<g clip-path="url(#pwipe)">{img()}</g>')
        out.append(holo + real)
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#pscan)" opacity=".3"/>')
        # a sweep bar that keeps scanning the face
        out.append(f'<g clip-path="url(#pclip)"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="14" fill="url(#psweep)">'
                   f'<animate attributeName="y" values="{cy - r - 14};{cy + r}" dur="3.2s" repeatCount="indefinite"/></rect></g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ACCENT}" stroke-width="1.5" filter="url(#lg)"/>')
    # verified chip on the ring
    out.append(_stamp(t_lock + .3, None,
                      f'<g transform="translate({cx + r * .62} {cy + r * .62})"><circle r="13" fill="{BG}" stroke="{GREEN}" stroke-width="1.5"/>'
                      f'<path d="M-5,0 l3.5,3.5 l6.5,-7" fill="none" stroke="{GREEN}" stroke-width="2.2" stroke-linecap="round"/></g>'))
    # name plate
    ny = cy + r + 52
    name = esc(prof["name"].upper())
    out.append(_stamp(t_lock + .2, None,
                      f'<text x="{cx}" y="{ny}" text-anchor="middle" font-family="{MONO}" font-size="19" font-weight="800" '
                      f'fill="{BRIGHT}" letter-spacing="3" filter="url(#lg)">{name}</text>'
                      f'<text x="{cx}" y="{ny + 20}" text-anchor="middle" font-family="{MONO}" font-size="9.5" fill="{ACCENT}" '
                      f'letter-spacing="1.5">{esc(prof["role"])}</text>'))
    # three short lines, decoded in sequence
    rows = [("FOCUS", prof["focus_short"] + " · Web", TEXT), ("STACK", "Python · Java · JS", TEXT),
            ("STATUS", "● " + prof["status"], GREEN)]
    y = ny + 50
    for i, (k, v, col) in enumerate(rows):
        out.append(_stamp(t_lock + .45 + i * .15, None,
                          f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="9" fill="{MUTED}" letter-spacing="2">{k}</text>'
                          f'<text x="{x1}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="9.5" fill="{col}">{esc(v)}</text>'
                          f'<line x1="{x0}" y1="{y + 7}" x2="{x1}" y2="{y + 7}" stroke="{LINE}"/>'))
        y += 22
    defs = (f'<defs><clipPath id="pclip"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
            f'<clipPath id="pwipe"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="0">'
            f'<animate attributeName="height" from="0" to="{2 * r}" begin="{t_lock:.2f}s" dur=".7s" fill="freeze"/></rect></clipPath>'
            f'<filter id="holo" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="'
            f'.05 .1 .02 0 0  .25 .55 .1 0 .03  .35 .7 .15 0 .12  0 0 0 1 0"/></filter>'
            f'<filter id="holoR" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="'
            f'.4 .6 .1 0 .05  0 0 0 0 0  .2 .3 .05 0 .08  0 0 0 .8 0"/></filter>'
            f'<pattern id="pscan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="{BG}" opacity=".55"/></pattern>'
            f'<linearGradient id="psweep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{ACCENT}" stop-opacity=".45"/></linearGradient></defs>')
    return defs + "".join(out)


def render(m: dict, prof: dict, stats: dict) -> str:
    grid, colours, src = logo_grid(COLS, ROWS)
    code = _code_stream()
    k = 0

    # ── the logo, as rows of code glyphs grouped into colour runs ──
    rows_svg = []
    glyphs = 0
    for r, row in enumerate(grid):
        parts, run_key, run, run_lvl = [], None, "", 0
        crow = colours[r] if colours else [None] * len(row)
        for lvl, col in list(zip(row, crow)) + [(-1, None)]:
            key = (col or LEVEL_FILL[lvl]) if lvl > 0 else lvl
            if key != run_key and run:
                if run_key:
                    bold = ' font-weight="700"' if run_lvl >= 3 else ""
                    parts.append(f'<tspan fill="{run_key}"{bold}>{esc(run)}</tspan>')
                else:
                    parts.append(" " * len(run))
                run = ""
            if lvl == -1:
                break
            run_key, run_lvl = key, lvl
            if lvl >= 3:      # neon line work: dense code glyphs
                run += code[k % len(code)]
                k += 1
                glyphs += 1
            elif lvl == 2:    # mid tones: sparse punctuation
                run += ":" if (r + len(run)) % 2 else "."
            elif lvl == 1:    # fill: a faint dot field
                run += "·" if (r + len(run)) % 2 == 0 else " "
            else:
                run += " "
        y = BY + (r + 1) * LH - 2
        rows_svg.append(f'<text x="{BX}" y="{y}" font-family="{MONO}" font-size="{FS}" '
                        f'xml:space="preserve" textLength="{COLS * CWID}" lengthAdjust="spacing">{"".join(parts)}</text>')

    # faint wall of code behind everything
    wall = []
    for i, y in enumerate(range(64, H - 50, 12)):
        off = (i * 137) % len(code)
        line = (code[off:] + code)[:150]
        wall.append(f'<text x="40" y="{y}" font-family="{MONO}" font-size="9" fill="{TEXT}" '
                    f'textLength="920" lengthAdjust="spacing">{esc(line)}</text>')
    wall_svg = (f'<g opacity=".045">{"".join(wall)}</g>')

    bw, bh = COLS * CWID, ROWS * LH
    t_end = SCAN_START + SCAN_DUR

    reveal = (f'<clipPath id="reveal"><rect x="{BX - 4}" y="{BY}" width="{bw + 8}" height="0">'
              f'<animate attributeName="height" from="0" to="{bh + 4}" begin="{SCAN_START}s" dur="{SCAN_DUR}s" '
              f'fill="freeze"/></rect></clipPath>')
    # pre-scan: logo exists only as a dim ghost
    ghost = f'<g opacity=".12" filter="url(#blurry)">{"".join(rows_svg)}</g>'
    underlay = ""
    if colours and logo_mod.LAST_GLOW:
        b64 = base64.b64encode(logo_mod.LAST_GLOW).decode()
        underlay = (f'<image href="data:image/jpeg;base64,{b64}" x="{BX}" y="{BY}" width="{bw}" height="{bh}" '
                    f'opacity=".42" filter="url(#imgglow)" mask="url(#feather)" preserveAspectRatio="none"/>')
    logo = (f'<g clip-path="url(#reveal)">{underlay}'
            f'<g filter="url(#lg)">{"".join(rows_svg)}</g></g>')

    laser = (f'<g opacity="0"><set attributeName="opacity" to="1" begin="{SCAN_START}s" fill="freeze"/>'
             f'<set attributeName="opacity" to="0" begin="{t_end:.2f}s" fill="freeze"/>'
             f'<rect x="{BX - 30}" y="{BY - 40}" width="{bw + 60}" height="40" fill="url(#trail)"/>'
             f'<rect x="{BX - 30}" y="{BY - 1}" width="{bw + 60}" height="2" fill="#e8f3ff" filter="url(#lg)"/>'
             f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 {bh}" '
             f'begin="{SCAN_START}s" dur="{SCAN_DUR}s" fill="freeze"/></g>')
    idle = (f'<g opacity="0"><set attributeName="opacity" to=".55" begin="{t_end + .6:.2f}s" fill="freeze"/>'
            f'<rect x="{BX - 12}" y="{BY - 1}" width="{bw + 24}" height="1.5" fill="{ACCENT}" filter="url(#lg)"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {bh};0 0" '
            f'dur="6s" begin="{t_end + .6:.2f}s" repeatCount="indefinite"/></g>')

    # target brackets: start wide, lock on
    def brackets(pad: float, color: str, sw: float, extra: str = "") -> str:
        x0, y0, x1, y1 = BX - pad, BY - pad, BX + bw + pad, BY + bh + pad
        L = 22
        d = (f"M{x0},{y0 + L}V{y0}H{x0 + L} M{x1 - L},{y0}H{x1}V{y0 + L} "
             f"M{x1},{y1 - L}V{y1}H{x1 - L} M{x0 + L},{y1}H{x0}V{y1 - L}")
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}">{extra}</path>'

    cx, cy = BX + bw / 2, BY + bh / 2
    # scale about the centre: wrap so the scale origin is the box centre
    lock = (f'<g transform="translate({cx} {cy})"><g>'
            f'<animateTransform attributeName="transform" type="scale" values="1.3;1.3;1" keyTimes="0;.3;1" '
            f'dur=".8s" calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1" fill="freeze"/>'
            f'<g transform="translate({-cx} {-cy})">{brackets(14, ACCENT, 2)}</g></g></g>'
            + brackets(26, LINE2, 1)
            + f'<path d="M{cx},{BY - 26}v10M{cx},{BY + bh + 16}v10M{BX - 26},{cy}h10M{BX + bw + 16},{cy}h10" '
              f'stroke="{ACCENT}" stroke-width="1.2"/>')

    # ── fastfetch-style readouts on both sides of the scan ──
    CH = 5.75  # advance at 9.5px

    def row(x0: float, x1: float, y: float, k: str, v: str, vcol: str = TEXT) -> str:
        k_end = x0 + len(k) * CH + 6
        v_start = x1 - len(v) * CH - 6
        dots = (f'<line x1="{k_end:.0f}" y1="{y - 3}" x2="{v_start:.0f}" y2="{y - 3}" stroke="{LINE2}" '
                f'stroke-dasharray="1 3"/>' if v_start - k_end > 8 else "")
        return (f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="9.5" fill="{ACCENT}">{esc(k)}</text>{dots}'
                f'<text x="{x1}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="9.5" fill="{vcol}">{esc(v)}</text>')

    def header(x0: float, x1: float, y: float, title: str) -> str:
        w = len(title) * 6.4 + 10
        return (f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="9" font-weight="700" fill="{BRIGHT}" '
                f'letter-spacing="2">▸ {esc(title)}</text>'
                f'<line x1="{x0 + w + 14:.0f}" y1="{y - 3}" x2="{x1}" y2="{y - 3}" stroke="{LINE2}"/>')

    left = [_portrait(prof, 40, BX - 40, SCAN_START + SCAN_DUR)]

    # right: GitHub numbers, then where to find me
    rx0, rx1 = BX + bw + 40, W - 40
    right, ry = [], 96
    right.append(_stamp(.2, None, header(rx0, rx1, ry, "GITHUB")))
    ry += 22
    for i, (k, v) in enumerate((("Repositories", str(m["repo_count"])), ("Merged PRs", str(m["pr_count"])),
                                ("Contributions", f'{m["total"]} / yr'), ("Followers", str(stats.get("followers", 0))))):
        right.append(_stamp(.3 + i * .12, None, row(rx0, rx1, ry, k, v, BRIGHT)))
        ry += 18
    ry += 18
    right.append(_stamp(.8, None, header(rx0, rx1, ry, "OPEN SOURCE")))
    ry += 22
    for i, (k, v) in enumerate((("checkstyle", "contributor"), ("apereo/cas", "contributor"), ("openSUSE", "member"))):
        right.append(_stamp(.9 + i * .12, None, row(rx0, rx1, ry, k, v)))
        ry += 18
    ry += 18
    right.append(_stamp(1.2, None, header(rx0, rx1, ry, "CONTACT")))
    ry += 22
    for i, (k, v) in enumerate((("GitHub", f"@{stats['login']}"), ("LinkedIn", prof["linkedin"]))):
        right.append(_stamp(1.3 + i * .12, None, row(rx0, rx1, ry, k, v)))
        ry += 18

    frame = hud_frame(W, H, tab=stats["login"].upper(), fid="sp")
    return svg_open(W, H, f"Start screen: {prof['name']} logo rendered from source code") + f"""
<defs>
  {glow("lg", 1.8)}
  <radialGradient id="featherg" cx=".5" cy=".5" r=".5"><stop offset=".72" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
  <mask id="feather" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect x="{BX}" y="{BY}" width="{COLS * CWID}" height="{ROWS * LH}" fill="url(#featherg)"/></mask>
  <filter id="imgglow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="1.2"/></filter>
  <filter id="blurry" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="1.4"/></filter>
  <linearGradient id="trail" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="1" stop-color="{ACCENT}" stop-opacity=".35"/></linearGradient>
  <pattern id="dots" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="{LINE2}"/></pattern>
  {reveal}
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="14" fill="url(#dots)" opacity=".45"/>
{wall_svg}
{frame}
<rect x="{BX - 26}" y="{BY - 26}" width="{bw + 52}" height="{bh + 52}" fill="{BG}" opacity=".7"/>
<path d="M{BX},{cy}H{BX + bw}M{cx},{BY}V{BY + bh}" stroke="{LINE}" stroke-dasharray="2 4"/>
{ghost}
{logo}
{laser}{idle}
{lock}
{"".join(left)}
{"".join(right)}
{scanlines(W, H)}
</svg>
"""
