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

    lx0, lx1 = 40, BX - 40
    sections = [
        ("SYSTEM", [("OS", prof["os"]), ("Uptime", prof["uptime"]), ("Host", prof["host_machine"]),
                    ("Kernel", prof["kernel"]), ("IDE", prof["ide"])]),
        ("LANGUAGES", [("Code", prof["lang_code"]), ("Web", prof["lang_web"]), ("Real", prof["lang_real"])]),
        ("PROFILE", [("Hobbies", prof["hobbies"]), ("Focus", prof["focus_short"]),
                     ("Hardware", prof["hardware"])]),
    ]
    left, y, n = [], 96, 0
    for title, items in sections:
        left.append(_stamp(.2 + n * .14, None, header(lx0, lx1, y, title)))
        y += 22
        for k, v in items:
            n += 1
            left.append(_stamp(.2 + n * .14, None, row(lx0, lx1, y, k, v)))
            y += 18
        y += 14

    # right: progress, then live stats rolling up, contact, verdict
    rx0, rx1 = BX + bw + 40, W - 40
    steps = 10
    right = [f'<text x="{rx1}" y="96" text-anchor="end" font-family="{MONO}" font-size="9" fill="{ACCENT}" '
             f'letter-spacing="2">SCAN PROGRESS ◂</text>',
             _stamp(0, SCAN_START, f'<text x="{rx1}" y="128" text-anchor="end" font-family="{MONO}" font-size="28" '
                                   f'font-weight="800" fill="{MUTED}">---%</text>')]
    for i in range(steps + 1):
        t0 = SCAN_START + SCAN_DUR * i / steps
        t1 = SCAN_START + SCAN_DUR * (i + 1) / steps if i < steps else None
        right.append(_stamp(t0, t1, f'<text x="{rx1}" y="128" text-anchor="end" font-family="{MONO}" '
                                    f'font-size="28" font-weight="800" fill="{BRIGHT}">{i * 10:03d}%</text>'))
    right.append(f'<rect x="{rx0}" y="138" width="{rx1 - rx0}" height="5" fill="none" stroke="{LINE2}"/>'
                 f'<rect x="{rx0 + 1}" y="139" width="0" height="3" fill="{ACCENT}">'
                 f'<animate attributeName="width" from="0" to="{rx1 - rx0 - 2}" begin="{SCAN_START}s" '
                 f'dur="{SCAN_DUR}s" fill="freeze"/></rect>')
    right.append(_stamp(SCAN_START, t_end, f'<text x="{rx0}" y="158" font-family="{MONO}" font-size="9" '
                                           f'fill="{ACCENT}" letter-spacing="2">SCANNING<tspan>'
                                           f'<animate attributeName="opacity" values="1;0;1" dur=".6s" '
                                           f'repeatCount="indefinite"/>_</tspan></text>'))
    right.append(_stamp(t_end, None, f'<text x="{rx0}" y="158" font-family="{MONO}" font-size="9" fill="{GREEN}" '
                                     f'letter-spacing="2">MATCH · {esc(stats["login"].upper())}</text>'))

    def rolling(x0, x1, y, k, final, suffix, t):
        """value counts up in a few quick frames"""
        out = []
        frames = 6
        for f in range(frames + 1):
            v = round(final * f / frames)
            ta = t + f * .07
            tb = t + (f + 1) * .07 if f < frames else None
            out.append(_stamp(ta, tb, row(x0, x1, y, k, f"{v}{suffix}", BRIGHT)))
        return "".join(out)

    ry = 192
    st = t_end + .1
    right.append(_stamp(st, None, header(rx0, rx1, ry, "GITHUB STATS")))
    ry += 22
    for k, final, suf in (("Repositories", m["repo_count"], ""), ("Merged PRs", m["pr_count"], ""),
                          ("Contributions", m["total"], " /yr")):
        right.append(rolling(rx0, rx1, ry, k, final, suf, st + .1))
        ry += 18
    right.append(_stamp(st + .3, None, row(rx0, rx1, ry, "Lines of Code", prof["loc"], BRIGHT)))
    ry += 32
    ct = st + .5
    right.append(_stamp(ct, None, header(rx0, rx1, ry, "CONTACT")))
    ry += 22
    for i, (k, v) in enumerate((("GitHub", f"@{stats['login']}"), ("LinkedIn", prof["linkedin"]),
                                ("Role", prof["title"]))):
        right.append(_stamp(ct + .1 + i * .12, None, row(rx0, rx1, ry, k, v)))
        ry += 18
    ag_t = ct + .7
    ay = ry + 14
    right.append(_stamp(ag_t, None,
                        f'<rect x="{rx0}" y="{ay}" width="{rx1 - rx0}" height="30" fill="{GREEN}" fill-opacity=".12" stroke="{GREEN}"/>'
                        f'<text x="{(rx0 + rx1) / 2}" y="{ay + 20}" text-anchor="middle" font-family="{MONO}" font-size="13" '
                        f'font-weight="800" fill="{GREEN}" letter-spacing="3" filter="url(#lg)">ACCESS GRANTED'
                        f'<animate attributeName="opacity" values="1;.45;1" dur="1.4s" begin="{ag_t + .4:.2f}s" repeatCount="indefinite"/></text>'))

    # bottom prompt + subtle hint
    hint = _stamp(ag_t + .3, None,
                  f'<text x="{W / 2}" y="{H - 30}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}" '
                  f'letter-spacing="4">▼  SCROLL TO BOOT  ▼'
                  f'<animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></text>')
    status = (f'<text x="{W / 2}" y="{BY + bh + 42}" text-anchor="middle" font-family="{MONO}" font-size="10" '
              f'fill="{MUTED}" letter-spacing="2">logo rendered from {glyphs} characters of this repo\'s own source code</text>')

    frame = hud_frame(W, H, tl="SECURE TERMINAL", tr=f"NODE {stats['login'].upper()}",
                      bl="v0x17 · STARTUP", br="AUTH: GLYPH-SCAN", tab="IDENTITY SCAN", fid="sp")
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
{status}
{hint}
{scanlines(W, H)}
</svg>
"""
