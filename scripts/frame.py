"""The signature frame: engineered instrument bezel + terminal window chrome.

Every panel shares this so the profile reads as one system.
"""
from __future__ import annotations

from common import (ACCENT, BAR, LINE, LINE2, MONO, MUTED, TEXT, WIN, esc)

M = 16  # gap between canvas edge and frame


def _barcode(x: int, y: int, seed: str, width: int = 120, h: int = 8) -> str:
    import hashlib
    bits = bin(int(hashlib.sha1(seed.encode()).hexdigest(), 16))[2:]
    out, cx, i, ink = [], x, 0, True
    while cx < x + width and i < len(bits) - 1:
        w = 1 + int(bits[i]) + int(bits[i + 1])
        if ink:
            out.append(f'<rect x="{cx}" y="{y}" width="{w}" height="{h}" fill="{MUTED}" opacity=".6"/>')
        cx += w
        i += 2
        ink = not ink
    return "".join(out)


def instrument_frame(W: int, H: int, tl: str, tr: str, bl: str, br: str,
                     trace: bool = True, ruler_labels: bool = True, extras: bool = False,
                     side_text: str = "", seed: str = "0x") -> str:
    x0, y0, x1, y1 = M, M, W - M, H - M
    fw, fh = x1 - x0, y1 - y0
    out = [f'<rect x="{x0}" y="{y0}" width="{fw}" height="{fh}" fill="none" stroke="{LINE}" stroke-width="1"/>']

    # ruler ticks on all four edges (outside the frame line)
    ticks = []
    for x in range(x0, x1 + 1, 10):
        rel = x - x0
        ln = 7 if rel % 100 == 0 else 4 if rel % 50 == 0 else 2
        ticks.append(f"M{x},{y0}v-{ln}M{x},{y1}v{ln}")
        if ruler_labels and rel % 100 == 0 and 0 < rel < fw - 40:
            out.append(f'<text x="{x + 3}" y="{y0 - 5}" font-family="{MONO}" font-size="7" '
                       f'fill="{MUTED}" opacity=".55">0x{rel:03X}</text>')
    for y in range(y0, y1 + 1, 10):
        rel = y - y0
        ln = 7 if rel % 100 == 0 else 4 if rel % 50 == 0 else 2
        ticks.append(f"M{x0},{y}h-{ln}M{x1},{y}h{ln}")
    out.append(f'<path d="{"".join(ticks)}" stroke="{MUTED}" stroke-width="1" opacity=".35"/>')

    # corner brackets
    b = 18
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        out.append(f'<path d="M{cx},{cy + sy * b}V{cy}H{cx + sx * b}" fill="none" stroke="{ACCENT}" '
                   f'stroke-width="2"/>')
        out.append(f'<rect x="{cx - 2}" y="{cy - 2}" width="4" height="4" fill="{ACCENT}"/>')

    # registration crosses at edge midpoints
    for cx, cy in ((W / 2, y0), (W / 2, y1), (x0, H / 2), (x1, H / 2)):
        out.append(f'<path d="M{cx - 5},{cy}h10M{cx},{cy - 5}v10" stroke="{ACCENT}" stroke-width="1" opacity=".7"/>')

    # corner labels, sitting in the margin
    lab = f'font-family="{MONO}" font-size="8.5" fill="{MUTED}" letter-spacing="1.5"'
    out.append(f'<text x="{x0 + 24}" y="{y0 + 12}" {lab}>{esc(tl)}</text>')
    out.append(f'<text x="{x1 - 24}" y="{y0 + 12}" text-anchor="end" {lab}>{esc(tr)}</text>')
    out.append(f'<text x="{x0 + 24}" y="{y1 - 5}" {lab}>{esc(bl)}</text>')
    out.append(f'<text x="{x1 - 24}" y="{y1 - 5}" text-anchor="end" {lab}>{esc(br)}</text>')

    if extras:
        # left rail: vertical system string
        out.append(f'<text transform="translate({x0 + 14},{H / 2}) rotate(-90)" text-anchor="middle" '
                   f'font-family="{MONO}" font-size="8" fill="{MUTED}" letter-spacing="3" opacity=".8">'
                   f'{esc(side_text)}</text>')
        # right rail: activity LEDs at different rhythms
        import random as _r
        rnd = _r.Random(seed)
        for k in range(14):
            cy = H / 2 - 70 + k * 10
            d = rnd.choice([1.3, 1.7, 2.3, 2.9, 3.7])
            lo = rnd.choice([".15", ".25"])
            out.append(f'<rect x="{x1 - 17}" y="{cy}" width="5" height="5" fill="{ACCENT}" opacity="{lo}">'
                       f'<animate attributeName="opacity" values="{lo};.9;{lo}" dur="{d}s" '
                       f'begin="{rnd.uniform(0, 2):.1f}s" repeatCount="indefinite"/></rect>')
        # bottom rail: barcode either side of the registration cross
        out.append(_barcode(int(W / 2) - 150, y1 - 13, seed + "L"))
        out.append(_barcode(int(W / 2) + 30, y1 - 13, seed + "R"))

    if trace:  # a light that slowly traces the frame
        per = 2 * (fw + fh)
        out.append(f"""
<defs><filter id="tr-glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
  <feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <linearGradient id="tr-fade"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="1" stop-color="{ACCENT}"/></linearGradient></defs>
<rect x="{x0}" y="{y0}" width="{fw}" height="{fh}" fill="none" stroke="{ACCENT}" stroke-width="1.6"
      stroke-dasharray="90 {per - 90}" filter="url(#tr-glow)" opacity=".9">
  <animate attributeName="stroke-dashoffset" from="0" to="-{per}" dur="14s" repeatCount="indefinite"/>
</rect>
<rect x="{x0}" y="{y0}" width="{fw}" height="{fh}" fill="none" stroke="{ACCENT}" stroke-width="1"
      stroke-dasharray="40 {per - 40}" opacity=".35">
  <animate attributeName="stroke-dashoffset" from="{per / 2}" to="-{per / 2}" dur="14s" repeatCount="indefinite"/>
</rect>""")
    return "".join(out)


def window(x: int, y: int, w: int, h: int, title: str, status_left: str = "",
           status_right: str = "", wid: str = "w") -> tuple[str, str]:
    """Terminal window chrome. Returns (chrome_svg, clip_id) for the body."""
    tb = 30
    sb = 22 if (status_left or status_right) else 0
    dots = "".join(f'<circle cx="{x + 18 + i * 16}" cy="{y + tb / 2}" r="5" fill="none" '
                   f'stroke="{LINE2}" stroke-width="1.4"/>' for i in range(3))
    chrome = [
        f'<clipPath id="{wid}-clip"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/></clipPath>',
        f'<g clip-path="url(#{wid}-clip)">',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{WIN}"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{tb}" fill="{BAR}"/>',
        f'<line x1="{x}" y1="{y + tb}" x2="{x + w}" y2="{y + tb}" stroke="{LINE}"/>',
        dots,
        f'<text x="{x + w / 2}" y="{y + tb / 2 + 4}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="11.5" fill="{MUTED}">{esc(title)}</text>',
    ]
    if sb:
        sy = y + h - sb
        chrome += [
            f'<rect x="{x}" y="{sy}" width="{w}" height="{sb}" fill="{BAR}"/>',
            f'<line x1="{x}" y1="{sy}" x2="{x + w}" y2="{sy}" stroke="{LINE}"/>',
            f'<rect x="{x}" y="{sy}" width="{8 + 7 * len(status_left.split("  ")[0]) + 8}" height="{sb}" '
            f'fill="{ACCENT}" fill-opacity=".14"/>',
            f'<text x="{x + 10}" y="{sy + 15}" font-family="{MONO}" font-size="11" fill="{TEXT}" xml:space="preserve">'
            f'{esc(status_left)}</text>',
            f'<text x="{x + w - 10}" y="{sy + 15}" text-anchor="end" font-family="{MONO}" font-size="11" '
            f'fill="{MUTED}">{esc(status_right)}</text>',
        ]
    chrome.append("</g>")
    chrome.append(f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="8" fill="none" '
                  f'stroke="{LINE2}"/>')
    return "".join(chrome), f"{wid}-clip"


def scanlines(W: int, H: int) -> str:
    return (f'<defs><pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse">'
            f'<rect width="4" height="1" fill="#ffffff" opacity=".018"/></pattern>'
            f'<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity=".35"/></radialGradient></defs>'
            f'<rect width="{W}" height="{H}" rx="14" fill="url(#scan)" pointer-events="none"/>'
            f'<rect width="{W}" height="{H}" rx="14" fill="url(#vig)" pointer-events="none"/>')


# ── HUD frame: chamfered, double-walled, with a title tab ──────────────────
def chamfer(x0: float, y0: float, x1: float, y1: float, c: float) -> tuple[str, float]:
    pts = [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1),
           (x0, y1 - c), (x0, y0 + c)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    per = 2 * ((x1 - x0) - 2 * c) + 2 * ((y1 - y0) - 2 * c) + 4 * c * 1.41421
    return d, per


def hud_frame(W: int, H: int, tl: str = "", tr: str = "", bl: str = "", br: str = "",
              tab: str = "", m: int = 14, c: int = 22, trace: bool = True, fid: str = "hf") -> str:
    x0, y0, x1, y1 = m, m, W - m, H - m
    outer, per = chamfer(x0, y0, x1, y1, c)
    inner, _ = chamfer(x0 + 6, y0 + 6, x1 - 6, y1 - 6, c - 2)
    out = [
        f'<path d="{outer}" fill="none" stroke="{LINE2}" stroke-width="1.2"/>',
        f'<path d="{inner}" fill="none" stroke="{ACCENT}" stroke-opacity=".18" stroke-width="1"/>',
    ]
    # glowing chamfer cuts
    for (ax, ay), (bx, by) in (((x0, y0 + c), (x0 + c, y0)), ((x1 - c, y0), (x1, y0 + c)),
                               ((x1, y1 - c), (x1 - c, y1)), ((x0 + c, y1), (x0, y1 - c))):
        out.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="{ACCENT}" stroke-width="3" '
                   f'filter="url(#{fid}-g)"/>')
    # ticks on the long edges
    t = []
    for x in range(int(x0 + c + 10), int(x1 - c), 8):
        ln = 6 if (x - x0) % 80 < 8 else 3
        t.append(f"M{x},{y1 - 6}v-{ln}")
    out.append(f'<path d="{"".join(t)}" stroke="{MUTED}" opacity=".35"/>')
    # title tab on the top edge
    if tab:
        tw = len(tab) * 7.2 + 40
        tx = W / 2 - tw / 2
        out.append(f'<path d="M{tx},{y0} L{tx + 12},{y0 + 18} L{tx + tw - 12},{y0 + 18} L{tx + tw},{y0} Z" '
                   f'fill="{ACCENT}" fill-opacity=".12" stroke="{ACCENT}" stroke-opacity=".7"/>')
        out.append(f'<text x="{W / 2}" y="{y0 + 13}" text-anchor="middle" font-family="{MONO}" font-size="10" '
                   f'font-weight="700" fill="{ACCENT}" letter-spacing="2.5">{esc(tab)}</text>')
    lab = f'font-family="{MONO}" font-size="8.5" fill="{MUTED}" letter-spacing="1.5"'
    for txt, x, y, a in ((tl, x0 + c + 6, y0 + 14, "start"), (tr, x1 - c - 6, y0 + 14, "end"),
                         (bl, x0 + c + 6, y1 - 14, "start"), (br, x1 - c - 6, y1 - 14, "end")):
        if txt:
            out.append(f'<text x="{x}" y="{y}" text-anchor="{a}" {lab}>{esc(txt)}</text>')
    defs = (f'<defs><filter id="{fid}-g" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/>'
            f'<feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    if trace:
        out.append(f'<path d="{outer}" fill="none" stroke="{ACCENT}" stroke-width="2" '
                   f'stroke-dasharray="120 {per - 120:.0f}" filter="url(#{fid}-g)">'
                   f'<animate attributeName="stroke-dashoffset" from="0" to="-{per:.0f}" dur="10s" '
                   f'repeatCount="indefinite"/></path>'
                   f'<path d="{outer}" fill="none" stroke="#bc8cff" stroke-width="1.5" opacity=".8" '
                   f'stroke-dasharray="60 {per - 60:.0f}" filter="url(#{fid}-g)">'
                   f'<animate attributeName="stroke-dashoffset" from="{per / 2:.0f}" to="-{per / 2:.0f}" '
                   f'dur="10s" repeatCount="indefinite"/></path>')
    return defs + "".join(out)
