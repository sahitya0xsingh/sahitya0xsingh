"""Three monochrome terminal cards for the profile.

hero      `whoami`, a quote and a halftone portrait with a light sweep and glitch slices
activity  contribution calendar with a scanning playhead
skyline   one building per week, one lit window per contribution, searchlights over the city

Black, white and greys only. Every card shares one CRT layer: film grain, scanlines, a rolling
refresh band and a vignette. All motion is SVG/SMIL, so it plays inside GitHub's <img> sandbox.
"""
from __future__ import annotations

import datetime as dt
import random

from common import ROOT, esc, now_ist

# ── theme ───────────────────────────────────────────────────────────────────
WIN = "#0a0a0a"
BAR = "#141414"
EDGE = "#262626"
TEXT = "#f5f5f5"
DIM = "#a3a3a3"
MUTE = "#555555"
HI = "#ffffff"                                             # the one "accent": pure white
RAMP = ["#171717", "#3d3d3d", "#6e6e6e", "#b5b5b5", "#ffffff"]  # empty → busiest
MONO = ("ui-monospace, 'SF Mono', SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")


def _open(w: int, h: int, label: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f'<title>{esc(label)}</title>')


def _window(w: int, h: int, title: str, foot_l: str, foot_r: str) -> str:
    dots = "".join(f'<circle cx="{22 + i * 18}" cy="18" r="5.5" fill="none" stroke="{MUTE}"/>' for i in range(3))
    live = (f'<circle cx="{w - 30}" cy="18" r="3.5" fill="{HI}">'
            f'<animate attributeName="opacity" values="1;.2;1" dur="1.8s" repeatCount="indefinite"/></circle>'
            f'<text x="{w - 42}" y="22" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="{MUTE}" '
            f'letter-spacing="2">LIVE</text>')
    return (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{WIN}" stroke="{EDGE}"/>'
            f'<path d="M12.5,.5H{w - 12.5}A12,12 0 0 1 {w - .5},12.5V36H.5V12.5A12,12 0 0 1 12.5,.5Z" fill="{BAR}"/>'
            f'<line x1=".5" y1="36" x2="{w - .5}" y2="36" stroke="{EDGE}"/>{dots}{live}'
            f'<text x="{w / 2}" y="22" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTE}">{esc(title)}</text>'
            f'<line x1="24" y1="{h - 34}" x2="{w - 24}" y2="{h - 34}" stroke="{EDGE}"/>'
            f'<text x="24" y="{h - 14}" font-family="{MONO}" font-size="11" fill="{MUTE}">{esc(foot_l)}</text>'
            f'<text x="{w - 24}" y="{h - 14}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTE}">{esc(foot_r)}</text>')


def _crt(w: int, h: int, uid: str) -> tuple[str, str]:
    """(defs, overlay): grain, scanlines, a rolling refresh band and a vignette over the window body."""
    defs = (f'<clipPath id="{uid}-body"><rect x="1" y="37" width="{w - 2}" height="{h - 38}" rx="11"/></clipPath>'
            f'<filter id="{uid}-grain" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="3" stitchTiles="stitch">'
            f'<animate attributeName="seed" values="3;9;17;26;4;31" dur=".6s" calcMode="discrete" repeatCount="indefinite"/>'
            f'</feTurbulence><feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .9 -.4"/></filter>'
            f'<pattern id="{uid}-scan" width="4" height="3" patternUnits="userSpaceOnUse">'
            f'<rect width="4" height="1" fill="#000" opacity=".45"/></pattern>'
            f'<linearGradient id="{uid}-roll" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="{uid}-vig" cx=".5" cy=".55" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>')
    overlay = (f'<g clip-path="url(#{uid}-body)" pointer-events="none">'
               f'<rect width="{w}" height="{h}" filter="url(#{uid}-grain)" opacity=".09"/>'
               f'<rect width="{w}" height="{h}" fill="url(#{uid}-scan)"/>'
               f'<rect x="0" y="-120" width="{w}" height="120" fill="url(#{uid}-roll)">'
               f'<animate attributeName="y" values="-120;{h}" dur="6.5s" repeatCount="indefinite"/></rect>'
               f'<rect width="{w}" height="{h}" fill="url(#{uid}-vig)"/>'
               # whole-screen flicker, rare and short
               f'<rect width="{w}" height="{h}" fill="#fff" opacity="0">'
               f'<animate attributeName="opacity" values="0;0;.06;0;.03;0" keyTimes="0;.86;.87;.88;.9;1" '
               f'dur="7s" repeatCount="indefinite"/></rect></g>')
    return defs, overlay


def _at(t: float, body: str) -> str:
    """Hidden until t seconds, then shown for good."""
    return f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>{body}</g>'


def _typed(x: float, y: float, cmd: str, t: float, uid: str, size: float = 14) -> tuple[str, str, float]:
    """A prompt line whose command types itself in: (clip defs, svg, time typing ends)."""
    cw = size * 0.602
    dur = max(.25, len(cmd) * .045)
    px = x + 4 * cw
    clip = (f'<clipPath id="{uid}"><rect x="{px}" y="{y - size}" width="0" height="{size * 1.5}">'
            f'<animate attributeName="width" from="0" to="{len(cmd) * cw + 2:.1f}" begin="{t + .15:.2f}s" '
            f'dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
    line = (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" xml:space="preserve">'
            f'<tspan fill="{HI}" font-weight="700">~ </tspan><tspan fill="{MUTE}">$ </tspan></text>'
            f'<text x="{px}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{TEXT}" '
            f'clip-path="url(#{uid})" xml:space="preserve">{esc(cmd)}</text>')
    return clip, _at(t, line), t + .15 + dur


def _cursor(x: float, y: float, t: float, size: float = 14) -> str:
    return _at(t, f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" xml:space="preserve">'
                  f'<tspan fill="{HI}" font-weight="700">~ </tspan><tspan fill="{MUTE}">$ </tspan></text>'
                  f'<rect x="{x + 4 * size * .602:.1f}" y="{y - size + 2}" width="{size * .6:.1f}" height="{size + 1}" fill="{HI}">'
                  f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" '
                  f'begin="{t:.2f}s" repeatCount="indefinite"/></rect>')


def _glitch(body: str, x: float, y: float, w: float, h: float, uid: str, period: float = 4.0,
            slices: int = 4, amp: float = 9) -> str:
    """Draw `body`, plus horizontal slices of it that jump sideways for a few frames every period."""
    rng = random.Random(uid)
    out = [f'<g id="{uid}">{body}</g>']
    for k in range(slices):
        sy = y + rng.uniform(0, h * .85)
        sh = rng.uniform(4, h * .14)
        at = rng.uniform(.55, .9)
        dx1, dx2 = rng.choice((-1, 1)) * rng.uniform(amp * .4, amp), rng.choice((-1, 1)) * rng.uniform(2, amp * .6)
        kt = f"0;{at:.3f};{at + .008:.3f};{at + .016:.3f};{at + .024:.3f};1"
        out.append(f'<clipPath id="{uid}-s{k}"><rect x="{x - 20}" y="{sy:.1f}" width="{w + 40}" height="{sh:.1f}"/></clipPath>'
                   f'<g clip-path="url(#{uid}-s{k})" opacity="0">'
                   f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="{period}s" repeatCount="indefinite"/>'
                   f'<rect x="{x - 20}" y="{sy:.1f}" width="{w + 40}" height="{sh:.1f}" fill="{WIN}"/>'
                   f'<g><animateTransform attributeName="transform" type="translate" '
                   f'values="0 0;0 0;{dx1:.1f} 0;{dx2:.1f} 0;0 0;0 0" keyTimes="{kt}" dur="{period}s" repeatCount="indefinite"/>'
                   f'<use href="#{uid}" xlink:href="#{uid}"/></g></g>')
    return "".join(out)


# ── halftone portrait ──────────────────────────────────────────────────────
def _halftone(x0: float, y0: float, size: float, n: int = 64) -> tuple[str, str]:
    """(defs, svg) for the photo as dots: dim base, a bright light-sweep pass, glitch slices.

    No blur filters here: a filter over ~3,000 animated dots stalls the SMIL timeline."""
    src = next((ROOT / "assets" / f for f in ("photo.jpg", "photo.jpeg", "photo.png")
                if (ROOT / "assets" / f).exists()), None)
    if not src:
        return "", ""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return "", ""
    im = Image.open(src).convert("L")
    side = min(im.size)
    im = im.crop(((im.width - side) // 2, (im.height - side) // 2,
                  (im.width + side) // 2, (im.height + side) // 2))
    # head and shoulders sit a little above centre in a typical profile photo
    im = im.crop((int(side * .175), int(side * .05), int(side * .825), int(side * .70)))
    im = ImageOps.autocontrast(im, cutoff=2).resize((n, n), Image.LANCZOS)
    px = im.load()
    cell = size / n
    cx = cy = (n - 1) / 2
    dots = []
    for j in range(n):
        for i in range(n):
            v = px[i, j] / 255
            d = ((i - cx) ** 2 + ((j - cy) * .9) ** 2) ** .5 / (n / 2)
            v *= max(0.0, min(1.0, (1.0 - d) / .25))
            r = cell * .55 * v ** 1.3
            if r < .35:
                continue
            col = RAMP[4] if v > .74 else RAMP[3] if v > .48 else RAMP[2]
            dots.append(f'<circle cx="{x0 + (i + .5) * cell:.1f}" cy="{y0 + (j + .5) * cell:.1f}" r="{r:.2f}" fill="{col}"/>')
    mx, my = x0 + size / 2, y0 + size / 2
    band = size * .35
    defs = (f'<g id="pdots">{"".join(dots)}</g>'
            f'<clipPath id="develop"><circle cx="{mx}" cy="{my}" r="0">'
            f'<animate attributeName="r" from="0" to="{size * .75:.0f}" begin=".3s" dur="1.6s" '
            f'calcMode="spline" keySplines=".2 .7 .2 1" fill="freeze"/></circle></clipPath>'
            f'<linearGradient id="sweepg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="sweep" maskUnits="userSpaceOnUse" x="{x0 - 40}" y="{y0 - 40}" width="{size + 80}" height="{size + 80}">'
            f'<rect x="{x0 - band}" y="{y0 - 60}" width="{band}" height="{size + 120}" fill="url(#sweepg)" '
            f'transform="rotate(18 {mx} {my})"><animate attributeName="x" values="{x0 - band * 1.6:.0f};{x0 + size + band * .6:.0f}" '
            f'dur="3.2s" begin="2s" repeatCount="indefinite"/></rect></mask>'
)
    base = '<use href="#pdots" xlink:href="#pdots" opacity=".62"/>'
    lit = '<g mask="url(#sweep)"><use href="#pdots" xlink:href="#pdots"/></g>'
    # orbit ring and tick marks around the portrait
    r0 = size * .53
    ring = (f'<circle cx="{mx}" cy="{my}" r="{r0:.0f}" fill="none" stroke="{MUTE}" stroke-width=".8" stroke-dasharray="2 5">'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {mx} {my}" to="360 {mx} {my}" dur="40s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{mx}" cy="{my}" r="{r0 + 8:.0f}" fill="none" stroke="{HI}" stroke-width="1.2" stroke-dasharray="40 {2 * 3.1416 * (r0 + 8) - 40:.0f}" opacity=".7">'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {mx} {my}" to="-360 {mx} {my}" dur="9s" repeatCount="indefinite"/></circle>')
    svg = (ring + f'<g clip-path="url(#develop)">'
           + _glitch(base + lit, x0, y0, size, size, "portrait", period=3.6, slices=5, amp=12) + '</g>')
    return defs, svg


def _rain(x0: float, x1: float, y0: float, y1: float, uid: str, cols: int = 26) -> str:
    """Faint columns of 0s and 1s drifting down behind everything."""
    rng = random.Random(uid)
    out = [f'<clipPath id="{uid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>'
           f'<g clip-path="url(#{uid})" opacity=".07" font-family="{MONO}" font-size="11" fill="{HI}">']
    step = (x1 - x0) / cols
    for c in range(cols):
        chars = "".join(rng.choice("01") for _ in range(40))
        spans = "".join(f'<tspan x="{x0 + c * step + 4:.0f}" dy="13">{ch}</tspan>' for ch in chars)
        dur = rng.uniform(6, 14)
        start = rng.uniform(-520, -200)
        out.append(f'<text y="0"><animateTransform attributeName="transform" type="translate" '
                   f'values="0 {start:.0f};0 {y1 + 40:.0f}" dur="{dur:.1f}s" begin="-{rng.uniform(0, dur):.1f}s" '
                   f'repeatCount="indefinite"/>{spans}</text>')
    out.append("</g>")
    return "".join(out)


# ── cards ──────────────────────────────────────────────────────────────────
def hero(m: dict, prof: dict, stats: dict) -> str:
    W, H = 1000, 460
    crt_defs, crt = _crt(W, H, "h")
    pdefs, portrait = _halftone(40, 66, 320)
    defs, body = [crt_defs, pdefs], [_rain(1, W - 1, 37, H - 35, "hr"), portrait]

    x, y, t = 400, 84, .4
    c, ln, t = _typed(x, y, "whoami", t, "c1")
    defs.append(c)
    body.append(ln)
    t += .15
    name = (f'<text x="{x}" y="{y + 44}" font-family="{MONO}" font-size="36" font-weight="800" '
            f'fill="{HI}" letter-spacing="-.5">{esc(prof["name"])}</text>')
    # a ghost copy of the name that splits off now and then
    ghost = (f'<text x="{x}" y="{y + 44}" font-family="{MONO}" font-size="36" font-weight="800" fill="none" '
             f'stroke="{DIM}" stroke-width=".8" letter-spacing="-.5" opacity="0">{esc(prof["name"])}'
             f'<animate attributeName="opacity" values="0;0;.9;.9;0;0" keyTimes="0;.7;.705;.74;.745;1" dur="5s" repeatCount="indefinite"/>'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;-5 1;4 -1;0 0;0 0" '
             f'keyTimes="0;.7;.705;.74;.745;1" dur="5s" repeatCount="indefinite"/></text>')
    body.append(_at(t, ghost + _glitch(name, x, y + 12, 400, 42, "name", period=5, slices=3, amp=10)
                    + f'<text x="{x}" y="{y + 70}" font-family="{MONO}" font-size="13.5" fill="{DIM}">'
                      f'{esc(prof["headline"])}</text>'))

    # the quote: the one line that says what I do, set larger than everything else
    y += 108
    qt = t + .45
    qh = len(prof["quote"]) * 28 + 6
    body.append(_at(qt, f'<rect x="{x}" y="{y - 22}" width="3" height="0" fill="{HI}">'
                        f'<animate attributeName="height" from="0" to="{qh}" begin="{qt:.2f}s" dur=".5s" fill="freeze"/></rect>'))
    for k, line in enumerate(prof["quote"]):
        qc, ql, _ = _typed_text(x + 18, y + k * 28, line, qt + .1 + k * .9, f"q{k}", 18, TEXT, italic=True)
        defs.append(qc)
        body.append(ql)
    y += len(prof["quote"]) * 28 + 34
    t = qt + .1 + len(prof["quote"]) * .9
    c, ln, t = _typed(x, y, "cat now.txt", t, "c2")
    defs.append(c)
    body.append(ln)
    t += .15
    for k, line in enumerate(prof["now"]):
        body.append(_at(t + k * .08, f'<text x="{x}" y="{y + 26 + k * 21}" font-family="{MONO}" font-size="13.5" '
                                     f'fill="{DIM}">{esc(line)}</text>'))
    y += 26 + len(prof["now"]) * 21 + 14
    body.append(_cursor(x, y, t + .6))

    return (_open(W, H, f"{prof['name']}: {prof['role']}") + f"<defs>{''.join(defs)}</defs>"
            + _window(W, H, f"{prof['user']}@{prof['host']}: ~ — zsh", prof["footer"], f"updated {now_ist():%Y-%m-%d}")
            + "".join(body) + crt + "</svg>")


def _typed_text(x: float, y: float, text: str, t: float, uid: str, size: float, fill: str,
                italic: bool = False) -> tuple[str, str, float]:
    """Plain text that types itself in, with a block caret riding the edge."""
    cw = size * .602
    dur = max(.3, len(text) * .02)
    wpx = len(text) * cw + 2
    clip = (f'<clipPath id="{uid}"><rect x="{x}" y="{y - size}" width="0" height="{size * 1.5}">'
            f'<animate attributeName="width" from="0" to="{wpx:.1f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
            f'</rect></clipPath>')
    style = ' font-style="italic"' if italic else ""
    svg = (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}"{style} '
           f'clip-path="url(#{uid})" xml:space="preserve">{esc(text)}</text>'
           f'<rect x="{x}" y="{y - size + 3}" width="{size * .55:.1f}" height="{size}" fill="{HI}" opacity="0">'
           f'<set attributeName="opacity" to=".9" begin="{t:.2f}s"/>'
           f'<animate attributeName="x" from="{x}" to="{x + wpx:.1f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
           f'<set attributeName="opacity" to="0" begin="{t + dur + .05:.2f}s"/></rect>')
    return clip, svg, t + dur


def activity(m: dict, stats: dict, prof: dict) -> str:
    W, H = 1000, 304
    crt_defs, crt = _crt(W, H, "a")
    days = stats["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    first_sun = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    nz = sorted(d["count"] for d in days if d["count"])
    q = [nz[int(len(nz) * f)] for f in (.25, .5, .75)] if nz else [1, 2, 3]

    def level(c: int) -> int:
        return 0 if c == 0 else 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4

    gx, gy, cs, gap = 78, 118, 13, 3
    glow_attr = ' filter="url(#cellglow)"'
    cols: dict[int, list[str]] = {}
    months, last_m = [], None
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        c, r = (date - first_sun).days // 7, (date.weekday() + 1) % 7
        lv = level(d["count"])
        pulse = ('<animate attributeName="opacity" values="1;.55;1" dur="2.4s" '
                 f'begin="{(c * .07) % 2.4:.2f}s" repeatCount="indefinite"/>' if lv == 4 else "")
        cols.setdefault(c, []).append(
            f'<rect x="{gx + c * (cs + gap)}" y="{gy + r * (cs + gap)}" width="{cs}" height="{cs}" rx="2" '
            f'fill="{RAMP[lv]}"{glow_attr if lv == 4 else ""}>'
            f'<title>{d["count"]} on {date:%d %b %Y}</title>{pulse}</rect>')
        if date.month != last_m and date.day <= 7:
            months.append(f'<text x="{gx + c * (cs + gap)}" y="{gy - 10}" font-family="{MONO}" font-size="11" '
                          f'fill="{MUTE}">{date:%b}</text>')
            last_m = date.month
    ncols = max(cols) + 1
    clip, cmd, t = _typed(28, 72, f"gh contributions --user {stats['login']} --last 12mo", .2, "a1")
    grid = "".join(_at(t + .1 + c * .018, "".join(v)) for c, v in sorted(cols.items()))
    gh = 7 * (cs + gap) - gap
    gw = ncols * (cs + gap)
    # a playhead that keeps scanning the year, with a soft trail
    head = (f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t + 1.2:.2f}s"/>'
            f'<rect x="{gx - 40}" y="{gy - 4}" width="40" height="{gh + 8}" fill="url(#trail)">'
            f'<animate attributeName="x" values="{gx - 40};{gx + gw - 40}" dur="5s" begin="{t + 1.2:.2f}s" repeatCount="indefinite"/></rect>'
            f'<rect x="{gx}" y="{gy - 6}" width="1.5" height="{gh + 12}" fill="{HI}">'
            f'<animate attributeName="x" values="{gx};{gx + gw}" dur="5s" begin="{t + 1.2:.2f}s" repeatCount="indefinite"/></rect></g>')
    labels = "".join(f'<text x="{gx - 12}" y="{gy + r * (cs + gap) + 10}" text-anchor="end" font-family="{MONO}" '
                     f'font-size="10.5" fill="{MUTE}">{n}</text>' for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    legend_x = W - 28 - 5 * 17
    legend = (f'<text x="{legend_x - 8}" y="{gy + 7 * (cs + gap) + 22}" text-anchor="end" font-family="{MONO}" '
              f'font-size="11" fill="{MUTE}">less</text>'
              + "".join(f'<rect x="{legend_x + k * 17}" y="{gy + 7 * (cs + gap) + 12}" width="{cs}" height="{cs}" rx="2" '
                        f'fill="{RAMP[k]}"/>' for k in range(5)))
    best = m["best"]
    best_d = dt.date.fromisoformat(best["date"]).strftime("%d %b") if best["date"] else "-"
    summary = (f'<text x="{gx}" y="{gy + 7 * (cs + gap) + 22}" font-family="{MONO}" font-size="12.5" '
               f'xml:space="preserve"><tspan fill="{HI}" font-weight="700">{m["total"]}</tspan>'
               f'<tspan fill="{DIM}"> contributions   </tspan><tspan fill="{TEXT}">{m["active"]}</tspan>'
               f'<tspan fill="{DIM}"> active days   best day </tspan><tspan fill="{TEXT}">{best["count"]} on {best_d}</tspan>'
               f'<tspan fill="{DIM}">   longest streak </tspan><tspan fill="{TEXT}">{m["longest"]}d</tspan></text>')
    defs = (crt_defs + clip
            + '<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
              '<stop offset="1" stop-color="#fff" stop-opacity=".16"/></linearGradient>'
              '<filter id="cellglow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2.4" result="b"/>'
              '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return (_open(W, H, f"Contributions in the last year: {m['total']}") + f"<defs>{defs}</defs>"
            + _window(W, H, f"{prof['user']}@{prof['host']}: ~/activity — zsh",
                      "data: GitHub contribution calendar", f"updated {now_ist():%Y-%m-%d}")
            + cmd + labels + "".join(months) + grid + head + _at(t + 1.2, summary + legend) + crt + "</svg>")


def skyline(m: dict, stats: dict, prof: dict) -> str:
    """One building per week of the last year; every contribution switches on a window."""
    W, H = 1000, 380
    crt_defs, crt = _crt(W, H, "s")
    days = stats["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    first_sun = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    weeks: dict[int, int] = {}
    for d in days:
        c = (dt.date.fromisoformat(d["date"]) - first_sun).days // 7
        weeks[c] = weeks.get(c, 0) + d["count"]
    n = max(weeks) + 1
    top = max(weeks.values()) or 1

    base, x0 = 300, 40
    bw = (W - 2 * x0) / n
    win, wgap = 3.2, 2.2          # window size and spacing
    rng = random.Random(stats["login"])
    clip, cmd, t = _typed(28, 72, "skyline --last 12mo --one-window-per-commit", .2, "s1")
    defs = [crt_defs, clip,
            f'<clipPath id="ground"><rect x="0" y="0" width="{W}" height="{base}"/></clipPath>',
            f'<clipPath id="skyclip"><rect x="1" y="92" width="{W - 2}" height="{base - 92}"/></clipPath>',
            f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WIN}"/>'
            f'<stop offset="1" stop-color="#1c1c1c"/></linearGradient>',
            '<linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".22"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
            '<linearGradient id="meteor" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset="1" stop-color="#fff"/></linearGradient>',
            '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>']

    sky = [f'<rect x="1" y="92" width="{W - 2}" height="{base - 92}" fill="url(#sky)"/>']
    for _ in range(60):
        sx, sy = rng.uniform(40, W - 40), rng.uniform(100, 200)
        tw = (f'<animate attributeName="opacity" values=".1;.8;.1" dur="{rng.uniform(1.5, 4):.1f}s" '
              f'begin="-{rng.uniform(0, 3):.1f}s" repeatCount="indefinite"/>' if rng.random() < .4 else "")
        sky.append(f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="{rng.choice((.6, .8, 1.1))}" fill="{HI}" '
                   f'opacity="{rng.uniform(.15, .55):.2f}">{tw}</circle>')
    # moon with a halo
    sky.append(f'<circle cx="{W - 120}" cy="132" r="30" fill="#fff" opacity=".05"/>'
               f'<circle cx="{W - 120}" cy="132" r="17" fill="{HI}" filter="url(#glow)"/>'
               f'<circle cx="{W - 112}" cy="126" r="16" fill="#101010"/>')
    # two searchlights sweeping the sky
    for bx_, dur, ph in ((x0 + bw * n * .3, 9, 0), (x0 + bw * n * .72, 7, 2.5)):
        sky.append(f'<polygon points="{bx_ - 2},{base} {bx_ + 2},{base} {bx_ + 60},{100} {bx_ - 60},{100}" fill="url(#beam)">'
                   f'<animateTransform attributeName="transform" type="rotate" values="-32 {bx_} {base};32 {bx_} {base};-32 {bx_} {base}" '
                   f'dur="{dur}s" begin="-{ph}s" repeatCount="indefinite" calcMode="spline" '
                   f'keySplines=".45 0 .55 1;.45 0 .55 1"/></polygon>')
    # a shooting star every few seconds
    sky.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;.6;.62;.7;1" '
               f'dur="8s" repeatCount="indefinite"/>'
               f'<rect x="0" y="0" width="90" height="1.6" fill="url(#meteor)" transform="rotate(18)">'
               f'</rect><animateTransform attributeName="transform" type="translate" values="{W * .2} 96;{W * .2} 96;{W * .55} 210;{W * .55} 210" '
               f'keyTimes="0;.6;.7;1" dur="8s" repeatCount="indefinite"/></g>')

    city = []
    busiest = max(weeks, key=weeks.get)
    for c in range(n):
        v = weeks.get(c, 0)
        h = 14 + (v / top) ** .55 * 170 if v else rng.uniform(8, 18)
        bx = x0 + c * bw + .8
        w = bw - 1.6
        cols = max(1, int((w - wgap) // (win + wgap)))
        rows = max(1, int((h - 8) // (win + wgap)))
        slots = [(i, j) for j in range(rows) for i in range(cols)]
        lit = set(rng.sample(range(len(slots)), min(v, len(slots))))
        wins = []
        for k, (i, j) in enumerate(slots):
            wx = bx + wgap + i * (win + wgap) + (w - wgap - cols * (win + wgap)) / 2 + wgap / 2
            wy = base - h + 6 + j * (win + wgap)
            if k in lit:
                fill = HI if rng.random() < .55 else "#c9c9c9"
                blink = (f'<animate attributeName="opacity" values="1;1;.15;1" keyTimes="0;.8;.85;1" '
                         f'dur="{rng.uniform(3, 9):.1f}s" begin="-{rng.uniform(0, 5):.1f}s" repeatCount="indefinite"/>'
                         if rng.random() < .12 else "")
                wins.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{win}" height="{win}" fill="{fill}">{blink}</rect>')
            else:
                wins.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{win}" height="{win}" fill="#1f1f1f"/>')
        roof = ""
        if c == busiest:  # an antenna with a beacon on the busiest week
            ax = bx + w / 2
            roof = (f'<line x1="{ax:.1f}" y1="{base - h:.1f}" x2="{ax:.1f}" y2="{base - h - 22:.1f}" stroke="{DIM}"/>'
                    f'<circle cx="{ax:.1f}" cy="{base - h - 23:.1f}" r="2.4" fill="{HI}" filter="url(#glow)">'
                    f'<animate attributeName="opacity" values="1;.1;1" dur="1.4s" repeatCount="indefinite"/></circle>'
                    f'<circle cx="{ax:.1f}" cy="{base - h - 23:.1f}" r="3" fill="none" stroke="{HI}">'
                    f'<animate attributeName="r" values="3;22" dur="2.8s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values=".8;0" dur="2.8s" repeatCount="indefinite"/></circle>')
        rise = t + .2 + c * .025
        city.append(f'<g transform="translate(0 {h + 30:.0f})">'
                    f'<animateTransform attributeName="transform" type="translate" from="0 {h + 30:.0f}" to="0 0" '
                    f'begin="{rise:.2f}s" dur=".7s" calcMode="spline" keySplines=".2 .8 .2 1" fill="freeze"/>'
                    f'<rect x="{bx:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#0f0f0f" stroke="#2a2a2a" stroke-width=".6"/>'
                    f'{"".join(wins)}{roof}</g>')

    # the city reflected in wet ground below the baseline
    reflect = (f'<g transform="translate(0 {2 * base}) scale(1 -1)" opacity=".13" clip-path="url(#reflclip)">'
               f'<use href="#city" xlink:href="#city"/></g>')
    defs.append(f'<clipPath id="reflclip"><rect x="0" y="{base - 30}" width="{W}" height="30"/></clipPath>')

    wk = first_sun + dt.timedelta(weeks=busiest)
    lit_total = sum(weeks.values())
    caption = (f'<text x="{x0}" y="{base + 30}" font-family="{MONO}" font-size="12.5" xml:space="preserve">'
               f'<tspan fill="{HI}" font-weight="700">{n}</tspan><tspan fill="{DIM}"> buildings   </tspan>'
               f'<tspan fill="{HI}" font-weight="700">{lit_total}</tspan><tspan fill="{DIM}"> lit windows   tallest: week of </tspan>'
               f'<tspan fill="{TEXT}">{wk:%d %b}</tspan><tspan fill="{DIM}"> ({weeks[busiest]})</tspan></text>')
    ground = f'<line x1="{x0 - 10}" y1="{base + .5}" x2="{W - x0 + 10}" y2="{base + .5}" stroke="{DIM}" stroke-opacity=".6"/>'
    return (_open(W, H, f"Commit skyline: one building per week, {lit_total} contributions as lit windows")
            + f"<defs>{''.join(defs)}</defs>"
            + _window(W, H, f"{prof['user']}@{prof['host']}: ~/skyline — zsh",
                      "taller = busier week · oldest on the left", f"updated {now_ist():%Y-%m-%d}")
            + cmd + f'<g clip-path="url(#skyclip)">{"".join(sky)}</g>'
            + f'<g id="city" clip-path="url(#ground)">{"".join(city)}</g>' + reflect + ground
            + _at(t + .2 + n * .025 + .5, caption) + crt + "</svg>")
