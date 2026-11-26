"""Three black-and-amber terminal cards for the profile.

hero      `whoami`, a quote and a halftone portrait with a light sweep and glitch slices
records   a split-flap board of personal records, digits rolling like odometers
skyline   one building per week, one lit window per contribution, searchlights over the city

Warm blacks with one amber accent. Every card shares one CRT layer: film grain, scanlines, a rolling
refresh band and a vignette. All motion is SVG/SMIL, so it plays inside GitHub's <img> sandbox.
"""
from __future__ import annotations

import datetime as dt
import random

from common import ROOT, esc, now_ist

# ── theme ───────────────────────────────────────────────────────────────────
WIN = "#0a0a0a"
BAR = "#141312"
EDGE = "#272522"
TEXT = "#f5f1ea"
DIM = "#a8a29e"
MUTE = "#5c5650"
HI = "#f5a524"                                             # the one accent: amber
RAMP = ["#171615", "#4a3206", "#8a5a0b", "#d08a14", "#ffc35c"]  # empty → busiest
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
            f'<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="1" seed="3" stitchTiles="stitch"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .9 -.4"/></filter>'
            f'<pattern id="{uid}-scan" width="4" height="3" patternUnits="userSpaceOnUse">'
            f'<rect width="4" height="1" fill="#000" opacity=".45"/></pattern>'
            f'<linearGradient id="{uid}-roll" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffb547" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#ffb547" stop-opacity=".05"/><stop offset="1" stop-color="#ffb547" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="{uid}-vig" cx=".5" cy=".55" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>')
    overlay = (f'<g clip-path="url(#{uid}-body)" pointer-events="none">'
               f'<rect width="{w}" height="{h}" filter="url(#{uid}-grain)" opacity=".09"/>'
               f'<rect width="{w}" height="{h}" fill="url(#{uid}-scan)"/>'
               f'<rect x="0" y="-120" width="{w}" height="120" fill="url(#{uid}-roll)">'
               f'<animate attributeName="y" values="-120;{h}" dur="6.5s" repeatCount="indefinite"/></rect>'
               f'<rect width="{w}" height="{h}" fill="url(#{uid}-vig)"/>'
               # whole-screen flicker, rare and short
               f'<rect width="{w}" height="{h}" fill="#ffb547" opacity="0">'
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
            slices: int = 4, amp: float = 9, clone: str = "") -> str:
    """Draw `body`, plus horizontal slices of it that jump sideways for a few frames every period."""
    rng = random.Random(uid)
    out = [f'<g id="{uid}">{body}</g>']
    ref = clone or f"#{uid}"   # what the slices copy: a lighter element than the whole body if given
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
                   f'<use href="{ref}" xlink:href="{ref}"/></g></g>')
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
            v *= max(0.0, min(1.0, (1.06 - d) / .3))
            r = cell * .6 * v ** 1.15
            if r < .35:
                continue
            col = RAMP[4] if v > .66 else "#f0a030" if v > .42 else "#b8720f"
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
    base = '<use href="#pdots" xlink:href="#pdots" opacity=".92"/>'
    lit = '<g mask="url(#sweep)"><use href="#pdots" xlink:href="#pdots"/></g>'
    # orbit ring and tick marks around the portrait
    r0 = size * .53
    ring = (f'<circle cx="{mx}" cy="{my}" r="{r0:.0f}" fill="none" stroke="{MUTE}" stroke-width=".8" stroke-dasharray="2 5">'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {mx} {my}" to="360 {mx} {my}" dur="40s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{mx}" cy="{my}" r="{r0 + 8:.0f}" fill="none" stroke="{HI}" stroke-width="1.2" stroke-dasharray="40 {2 * 3.1416 * (r0 + 8) - 40:.0f}" opacity=".7">'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {mx} {my}" to="-360 {mx} {my}" dur="9s" repeatCount="indefinite"/></circle>')
    svg = (ring + f'<g clip-path="url(#develop)">'
           + _glitch(base + lit, x0, y0, size, size, "portrait", period=3.6, slices=3, amp=12, clone="#pdots") + '</g>')
    return defs, svg


def _rain(x0: float, x1: float, y0: float, y1: float, uid: str, cols: int = 26) -> str:
    """Faint columns of 0s and 1s drifting down behind everything."""
    rng = random.Random(uid)
    out = [f'<clipPath id="{uid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>'
           f'<g clip-path="url(#{uid})" opacity=".05" font-family="{MONO}" font-size="11" fill="{HI}">']
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
            f'fill="{TEXT}" letter-spacing="-.5">{esc(prof["name"])}</text>')
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


def records(m: dict, stats: dict, prof: dict) -> str:
    """A split-flap board of personal records; every digit rolls like an odometer before it lands."""
    W, H = 1000, 540
    crt_defs, crt = _crt(W, H, "r")
    best = m["best"]
    best_d = dt.date.fromisoformat(best["date"]) if best["date"] else None
    rows = [
        ("CONTRIBUTIONS", m["total"], "THIS YEAR", "every commit, PR, review and issue"),
        ("BEST DAY", best["count"], "IN ONE DAY", f"{best_d:%d %b %Y}".upper() if best_d else ""),
        ("PULL REQUESTS", m["pr_count"], "UPSTREAM", "shipped into other people's repos"),
        ("LONGEST STREAK", m["longest"], "DAYS", "without missing a day"),
        ("ACTIVE DAYS", m["active"], f"OF {m['span']}", "days with at least one contribution"),
        ("REPOSITORIES", m["repo_count"], "PUBLIC", f"@{stats['login']}"),
    ]
    clip, cmd, t = _typed(28, 72, "records --all --rank", .2, "r1")
    defs = [crt_defs, clip,
            '<linearGradient id="flap" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1e1c1a"/>'
            '<stop offset=".5" stop-color="#151413"/><stop offset=".5" stop-color="#0c0b0a"/><stop offset="1" stop-color="#121110"/></linearGradient>']
    body = []
    tw, th, tg = 30, 42, 4          # tile width, height, gap
    digits = 4
    x_lab, x_tiles = 70, 330
    y0, rh = 118, 54
    strip = "0123456789" * 3
    for k, (label, val, unit, note) in enumerate(rows):
        y = y0 + k * rh
        t0 = t + .3 + k * .22
        rank = f"#{k + 1:02d}"
        body.append(_at(t0, f'<text x="28" y="{y + 27}" font-family="{MONO}" font-size="11" fill="{MUTE}">{rank}</text>'
                            f'<text x="{x_lab}" y="{y + 27}" font-family="{MONO}" font-size="14" font-weight="700" '
                            f'fill="{TEXT}" letter-spacing="3">{label}</text>'
                            f'<line x1="{x_lab}" y1="{y + rh - 6}" x2="{W - 28}" y2="{y + rh - 6}" stroke="{EDGE}"/>'))
        txt = str(val).rjust(digits)
        for i, ch in enumerate(txt):
            tx = x_tiles + i * (tw + tg)
            uid = f"od{k}{i}"
            tile = (f'<rect x="{tx}" y="{y}" width="{tw}" height="{th}" rx="3" fill="url(#flap)" stroke="#2c2a27"/>'
                    f'<line x1="{tx}" y1="{y + th / 2}" x2="{tx + tw}" y2="{y + th / 2}" stroke="#000" stroke-width="1.2"/>')
            if ch == " ":
                body.append(_at(t0, tile))
                continue
            d = int(ch)
            land = 20 + d               # lands on the third copy of the digit, after two full spins
            defs.append(f'<clipPath id="{uid}"><rect x="{tx}" y="{y}" width="{tw}" height="{th}" rx="3"/></clipPath>')
            col = "".join(f'<tspan x="{tx + tw / 2}" dy="{th if j else 0}">{c}</tspan>' for j, c in enumerate(strip))
            spin = 1.1 + i * .18
            body.append(_at(t0, tile + f'<g clip-path="url(#{uid})"><text x="{tx + tw / 2}" y="{y + th * .72}" '
                                       f'text-anchor="middle" font-family="{MONO}" font-size="27" font-weight="800" fill="{HI}">'
                                       f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 {-land * th}" '
                                       f'begin="{t0:.2f}s" dur="{spin:.2f}s" calcMode="spline" keySplines=".15 .7 .2 1" fill="freeze"/>'
                                       f'{col}</text></g>'
                                       f'<line x1="{tx}" y1="{y + th / 2}" x2="{tx + tw}" y2="{y + th / 2}" stroke="#000" stroke-width="1.2"/>'))
        done = t0 + 1.1 + digits * .18
        ux = x_tiles + digits * (tw + tg) + 16
        body.append(_at(done, f'<text x="{ux}" y="{y + 20}" font-family="{MONO}" font-size="12" font-weight="700" '
                              f'fill="{HI}" letter-spacing="2">{esc(unit)}</text>'
                              f'<text x="{ux}" y="{y + 36}" font-family="{MONO}" font-size="11" fill="{MUTE}">{esc(note)}</text>'))
    end = t + .3 + len(rows) * .22 + 1.1 + digits * .18
    # arcade header that flickers like a cabinet marquee
    body.append(f'<text x="{W - 28}" y="78" text-anchor="end" font-family="{MONO}" font-size="24" font-weight="800" '
                f'fill="{HI}" letter-spacing="7">HIGH SCORES'
                f'<animate attributeName="opacity" values="1;1;.2;1;.4;1;1" keyTimes="0;.6;.62;.64;.66;.68;1" '
                f'dur="3.5s" repeatCount="indefinite"/></text>'
                f'<text x="{W - 28}" y="96" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="{MUTE}" '
                f'letter-spacing="3">PLAYER 1 · {esc(stats["login"].upper())}</text>')
    # a selector that walks down the board, like picking a row on a cabinet
    steps = ";".join(f"{y0 + k * rh - 6}" for k in range(len(rows)))
    body.append(_at(end, f'<rect x="20" y="{y0 - 6}" width="{W - 40}" height="{rh - 4}" fill="#ffb547" opacity=".055">'
                         f'<animate attributeName="y" values="{steps}" dur="{len(rows) * .9:.1f}s" calcMode="discrete" '
                         f'repeatCount="indefinite"/></rect>'
                         f'<text x="16" y="{y0 + 27}" font-family="{MONO}" font-size="13" fill="{HI}">▶'
                         f'<animate attributeName="y" values="{";".join(str(y0 + k * rh + 27) for k in range(len(rows)))}" '
                         f'dur="{len(rows) * .9:.1f}s" calcMode="discrete" repeatCount="indefinite"/></text>'))
    # ticker tape along the bottom, looping forever
    ty = y0 + len(rows) * rh + 8
    tape = "   ✦   ".join(f"{r[0]} {r[1]} {r[2]}" for r in rows) + "   ✦   INSERT COIN TO CONTINUE   ✦   "
    tw_px = len(tape) * 12 * .602
    defs.append(f'<clipPath id="tape"><rect x="20" y="{ty}" width="{W - 40}" height="28"/></clipPath>')
    body.append(_at(end, f'<line x1="20" y1="{ty}" x2="{W - 20}" y2="{ty}" stroke="{EDGE}"/>'
                         f'<line x1="20" y1="{ty + 28}" x2="{W - 20}" y2="{ty + 28}" stroke="{EDGE}"/>'
                         f'<g clip-path="url(#tape)"><text y="{ty + 19}" font-family="{MONO}" font-size="12" font-weight="700" '
                         f'fill="{DIM}" letter-spacing="0" xml:space="preserve">'
                         f'<animateTransform attributeName="transform" type="translate" values="0 0;{-tw_px:.0f} 0" '
                         f'dur="{tw_px / 60:.1f}s" repeatCount="indefinite"/>'
                         f'<tspan x="20">{esc(tape)}</tspan><tspan x="{20 + tw_px:.0f}">{esc(tape)}</tspan></text></g>'))
    return (_open(W, H, "Personal records: " + ", ".join(f"{r[0].lower()} {r[1]}" for r in rows))
            + f"<defs>{''.join(defs)}</defs>"
            + _window(W, H, f"{prof['user']}@{prof['host']}: ~/records — zsh",
                      "source: GitHub contribution calendar and search", f"updated {now_ist():%Y-%m-%d}")
            + cmd + "".join(body) + crt + "</svg>")


def skyline(m: dict, stats: dict, prof: dict) -> str:
    """One building per week of the last year; every contribution switches on a window."""
    W, H = 1000, 420
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
    clip, cmd, t = _typed(28, 72, "git log --since=12.months --author=me | skyline", .2, "s1")
    defs = [crt_defs, clip,
            f'<clipPath id="ground"><rect x="0" y="0" width="{W}" height="{base}"/></clipPath>',
            f'<clipPath id="skyclip"><rect x="1" y="92" width="{W - 2}" height="{base - 92}"/></clipPath>',
            f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WIN}"/>'
            f'<stop offset="1" stop-color="#1d160b"/></linearGradient>',
            '<linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#ffb547" stop-opacity=".22"/>'
            '<stop offset="1" stop-color="#ffb547" stop-opacity="0"/></linearGradient>',
            '<linearGradient id="meteor" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffb547" stop-opacity="0"/>'
            '<stop offset="1" stop-color="#ffb547"/></linearGradient>',
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
    sky.append(f'<circle cx="{W - 120}" cy="132" r="30" fill="#ffb547" opacity=".05"/>'
               f'<circle cx="{W - 120}" cy="132" r="17" fill="{HI}" filter="url(#glow)"/>'
               f'<circle cx="{W - 112}" cy="126" r="16" fill="#0c0b0a"/>')
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
                fill = HI if rng.random() < .55 else "#ffd08a"
                blink = (f'<animate attributeName="opacity" values="1;1;.15;1" keyTimes="0;.8;.85;1" '
                         f'dur="{rng.uniform(3, 9):.1f}s" begin="-{rng.uniform(0, 5):.1f}s" repeatCount="indefinite"/>'
                         if rng.random() < .12 else "")
                wins.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{win}" height="{win}" fill="{fill}">{blink}</rect>')
            else:
                wins.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{win}" height="{win}" fill="#1f1d1b"/>')
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
                    f'<rect x="{bx:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#0f0e0d" stroke="#2c2a27" stroke-width=".6"/>'
                    f'{"".join(wins)}{roof}</g>')

    # the city reflected in wet ground below the baseline
    reflect = (f'<g transform="translate(0 {2 * base}) scale(1 -1)" opacity=".13" clip-path="url(#reflclip)">'
               f'<use href="#city" xlink:href="#city"/></g>')
    defs.append(f'<clipPath id="reflclip"><rect x="0" y="{base - 30}" width="{W}" height="30"/></clipPath>')

    wk = first_sun + dt.timedelta(weeks=busiest)
    lit_total = sum(weeks.values())
    ground = f'<line x1="{x0 - 10}" y1="{base + .5}" x2="{W - x0 + 10}" y2="{base + .5}" stroke="{DIM}" stroke-opacity=".6"/>'
    # street under the city: lane markings and traffic running both ways
    road = (f'<rect x="{x0 - 10}" y="{base + 1}" width="{W - 2 * x0 + 20}" height="14" fill="#0d0c0b"/>'
            f'<line x1="{x0}" y1="{base + 8}" x2="{W - x0}" y2="{base + 8}" stroke="{MUTE}" stroke-dasharray="6 8" stroke-width=".8"/>')
    for k in range(7):
        rtl = k % 2
        yy = base + (11 if rtl else 4)
        dur = rng.uniform(5, 11)
        a0, a1 = (W - x0, x0 - 10) if rtl else (x0 - 10, W - x0)
        lights = (f'<rect x="0" y="0" width="7" height="2.4" rx="1" fill="{HI if not rtl else "#c98516"}"/>'
                  f'<rect x="{-14 if not rtl else 7}" y=".7" width="14" height="1" fill="{HI}" opacity=".25"/>')
        road += (f'<g><animateTransform attributeName="transform" type="translate" values="{a0} {yy};{a1} {yy}" '
                 f'dur="{dur:.1f}s" begin="-{rng.uniform(0, dur):.1f}s" repeatCount="indefinite"/>{lights}</g>')
    # month ticks under the street
    axis, seen = [], set()
    for c in range(n):
        d0 = first_sun + dt.timedelta(weeks=c)
        if d0.month not in seen and d0.day <= 7:
            seen.add(d0.month)
            axis.append(f'<text x="{x0 + c * bw:.0f}" y="{base + 30}" font-family="{MONO}" font-size="10.5" '
                        f'fill="{MUTE}">{d0:%b}</text>')
    # a callout pinned to the tallest tower
    hb = 14 + (weeks[busiest] / top) ** .55 * 170
    ax = x0 + busiest * bw + bw / 2
    ay = base - hb - 23
    callout = (f'<path d="M{ax + 4},{ay} l14,-14 h70" fill="none" stroke="{HI}" stroke-width=".8"/>'
               f'<text x="{ax + 22}" y="{ay - 19}" font-family="{MONO}" font-size="11" font-weight="700" fill="{HI}">'
               f'PEAK · {weeks[busiest]} commits</text>'
               f'<text x="{ax + 22}" y="{ay - 6}" font-family="{MONO}" font-size="10" fill="{DIM}">week of {wk:%d %b %Y}</text>')
    base += 26
    caption = (f'<text x="{x0}" y="{base + 30}" font-family="{MONO}" font-size="12.5" xml:space="preserve">'
               f'<tspan fill="{HI}" font-weight="700">{n}</tspan><tspan fill="{DIM}"> buildings   </tspan>'
               f'<tspan fill="{HI}" font-weight="700">{lit_total}</tspan><tspan fill="{DIM}"> lit windows   </tspan>'
               f'<tspan fill="{HI}" font-weight="700">{sum(1 for v in weeks.values() if v)}</tspan>'
               f'<tspan fill="{DIM}"> weeks with the lights on</tspan></text>')
    return (_open(W, H, f"Commit skyline: one building per week, {lit_total} contributions as lit windows")
            + f"<defs>{''.join(defs)}</defs>"
            + _window(W, H, f"{prof['user']}@{prof['host']}: ~/skyline — zsh",
                      "one building per week · one lit window per contribution", f"updated {now_ist():%Y-%m-%d}")
            + cmd + f'<g clip-path="url(#skyclip)">{"".join(sky)}</g>'
            + f'<g id="city" clip-path="url(#ground)">{"".join(city)}</g>' + reflect + road + ground
            + "".join(axis) + _at(t + .2 + n * .025 + .5, caption + callout) + crt + "</svg>")


def divider() -> str:
    """A hairline section break: blue fading in from both edges, with a glint that travels along it."""
    W, H = 1000, 24
    return (_open(W, H, "section divider")
            + '<defs><linearGradient id="dv" x1="0" y1="0" x2="1" y2="0">'
              '<stop offset="0" stop-color="#d08a14" stop-opacity="0"/><stop offset=".5" stop-color="#d08a14" stop-opacity=".7"/>'
              '<stop offset="1" stop-color="#d08a14" stop-opacity="0"/></linearGradient>'
              '<radialGradient id="gl"><stop offset="0" stop-color="#ffc35c"/><stop offset="1" stop-color="#ffc35c" stop-opacity="0"/></radialGradient></defs>'
            + f'<rect x="0" y="{H / 2 - .5}" width="{W}" height="1" fill="url(#dv)"/>'
            + f'<rect x="{W / 2 - 4}" y="{H / 2 - 4}" width="8" height="8" fill="{WIN}" stroke="{HI}" transform="rotate(45 {W / 2} {H / 2})"/>'
            + f'<ellipse cx="0" cy="{H / 2}" rx="60" ry="3" fill="url(#gl)">'
              f'<animate attributeName="cx" values="-60;{W + 60}" dur="4.5s" repeatCount="indefinite"/></ellipse>'
            + "</svg>")


def project(p: dict) -> str:
    """A project as a real pre-flight check: the checklist ticks itself off, then a plane takes off from the runway.
    The headline numbers sit underneath as cockpit readouts."""
    W, H = 1000, 500
    uid = p["slug"]
    crt_defs, crt = _crt(W, H, f"p{uid}")
    clip, cmd, t = _typed(28, 72, p["command"], .2, f"{uid}c")
    body = [_at(t, f'<text x="28" y="112" font-family="{MONO}" font-size="10.5" fill="{HI}" letter-spacing="3">'
                   f'{esc(p["kicker"])}</text>'
                   f'<text x="28" y="148" font-family="{MONO}" font-size="32" font-weight="800" fill="{TEXT}" '
                   f'letter-spacing="-.5">{esc(p["name"])}</text>')]
    for k, line in enumerate(p["desc"]):
        body.append(_at(t + .15 + k * .1, f'<text x="28" y="{174 + k * 18}" font-family="{MONO}" font-size="12.5" '
                                          f'fill="{DIM}">{esc(line)}</text>'))
    x = 28
    chips = []
    for tag in p["tags"]:
        w = len(tag) * 7 + 16
        chips.append(f'<rect x="{x}" y="206" width="{w:.0f}" height="19" rx="9.5" fill="none" stroke="{HI}" stroke-opacity=".45"/>'
                     f'<text x="{x + w / 2:.0f}" y="219.5" text-anchor="middle" font-family="{MONO}" font-size="10.5" '
                     f'fill="{TEXT}">{esc(tag)}</text>')
        x += w + 7
    body.append(_at(t + .3, "".join(chips)))

    # ── the checklist ticks itself off ──
    checks = p.get("checks", ["read CI from .github/workflows", "build the same Docker image",
                              "run every job on this machine", "compare with GitHub's own result"])
    spin = "|/-\\"
    ct = t + .7
    for i, item in enumerate(checks):
        y = 254 + i * 21
        t0 = ct + i * .75
        frames = "".join(
            f'<text x="38" y="{y}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{DIM}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{t0 + f * .12:.2f}s"/><set attributeName="opacity" to="0" begin="{t0 + (f + 1) * .12:.2f}s"/>{esc(c)}</text>'
            for f, c in enumerate(spin))
        done = t0 + len(spin) * .12
        body.append(_at(t0, f'<text x="28" y="{y}" font-family="{MONO}" font-size="13" fill="{MUTE}">[ ]</text>'
                            f'<text x="58" y="{y}" font-family="{MONO}" font-size="13" fill="{TEXT}">{esc(item)}</text>'
                            f'<line x1="{58 + len(item) * 7.83 + 10:.0f}" y1="{y - 4}" x2="476" y2="{y - 4}" stroke="{EDGE}" stroke-dasharray="2 4"/>')
                    + frames
                    + _at(done, f'<text x="38" y="{y}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="800" fill="{HI}">✓</text>'
                                f'<text x="500" y="{y}" text-anchor="end" font-family="{MONO}" font-size="12" font-weight="700" fill="{HI}">OK</text>'))
    t_done = ct + len(checks) * .75 + .2
    yl = 254 + len(checks) * 21 - 6
    body.append(_at(t_done, f'<rect x="26" y="{yl}" width="476" height="26" rx="3" fill="{HI}" fill-opacity=".12" stroke="{HI}" stroke-opacity=".6"/>'
                            f'<text x="38" y="{yl + 17.5}" font-family="{MONO}" font-size="12.5" font-weight="800" fill="{HI}" letter-spacing="1.5">'
                            f'ALL CHECKS PASSED · CLEARED FOR PUSH<animate attributeName="opacity" values="1;.45;1" dur="1.6s" '
                            f'begin="{t_done:.2f}s" repeatCount="indefinite"/></text>'))

    # ── the runway: a plane holds, then takes off once everything is green; loops ──
    px0, py0, pw, ph = 548, 100, W - 28 - 548, 266
    gy = py0 + ph - 46                                   # ground line
    rng = random.Random(uid)
    stars = "".join(f'<circle cx="{px0 + rng.uniform(8, pw - 8):.0f}" cy="{py0 + rng.uniform(26, ph - 110):.0f}" r="{rng.uniform(.6, 1.3):.1f}" '
                    f'fill="{TEXT}" opacity="{rng.uniform(.15, .5):.2f}"><animate attributeName="opacity" values=".1;.6;.1" '
                    f'dur="{rng.uniform(2, 5):.1f}s" repeatCount="indefinite"/></circle>' for _ in range(26))
    dashes = (f'<line x1="{px0}" y1="{gy + 16}" x2="{px0 + pw}" y2="{gy + 16}" stroke="{TEXT}" stroke-opacity=".5" '
              f'stroke-width="2" stroke-dasharray="18 14"><animate attributeName="stroke-dashoffset" from="0" to="64" dur=".8s" '
              f'repeatCount="indefinite"/></line>')
    lights = "".join(f'<circle cx="{px0 + 14 + i * (pw - 28) / 13:.0f}" cy="{gy + 2}" r="2" fill="{HI}" opacity=".25">'
                     f'<animate attributeName="opacity" values=".25;1;.25" dur="1.4s" begin="{i * .1:.2f}s" repeatCount="indefinite"/></circle>'
                     f'<circle cx="{px0 + 14 + i * (pw - 28) / 13:.0f}" cy="{gy + 30}" r="2" fill="{HI}" opacity=".25">'
                     f'<animate attributeName="opacity" values=".25;1;.25" dur="1.4s" begin="{i * .1:.2f}s" repeatCount="indefinite"/></circle>'
                     for i in range(14))
    tower = (f'<path d="M{px0 + 30},{gy} v-58 h-8 l4,-16 h28 l4,16 h-8 v58 Z" fill="#141210" stroke="{EDGE}"/>'
             f'<rect x="{px0 + 28}" y="{gy - 72}" width="24" height="8" fill="{HI}" opacity=".35"/>'
             f'<circle cx="{px0 + 40}" cy="{gy - 80}" r="2.4" fill="{HI}"><animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/></circle>')
    plane = (f'<g id="{uid}-plane"><path d="M0,0 L46,0 Q60,0 62,5 Q60,10 46,10 L12,10 L5,20 L0,20 L2,10 Z" fill="{TEXT}"/>'
             f'<path d="M24,5 L33,5 L21,22 L14,22 Z" fill="#cfc8bb"/>'
             + "".join(f'<circle cx="{20 + k * 6}" cy="4" r="1.2" fill="{HI}"/>' for k in range(4))
             + f'<circle cx="62" cy="5" r="1.6" fill="{HI}"><animate attributeName="opacity" values="1;.2;1" dur=".8s" repeatCount="indefinite"/></circle></g>')
    sx, sy = px0 + 80, gy - 21
    path = f"M{sx},{sy} L{sx + 150},{sy} Q{sx + 270},{sy - 6} {px0 + pw + 80},{py0 - 30}"
    cyc = 8
    kt = "0;.12;.75;1"
    motion = (f'<g><animateMotion path="{path}" dur="{cyc}s" begin="{t_done:.2f}s" repeatCount="indefinite" '
              f'keyPoints="0;0;1;1" keyTimes="{kt}" calcMode="spline" keySplines="0 0 1 1;.6 0 .9 .6;0 0 1 1" rotate="auto"/>'
              f'<use href="#{uid}-plane" xlink:href="#{uid}-plane" transform="translate(0 -10)"/></g>')
    trail = (f'<path d="{path}" fill="none" stroke="{HI}" stroke-width="2.5" stroke-linecap="round" opacity=".7" '
             f'pathLength="100" stroke-dasharray="100 100" stroke-dashoffset="100">'
             f'<animate attributeName="stroke-dashoffset" values="100;100;0;0" keyTimes="{kt}" dur="{cyc}s" begin="{t_done:.2f}s" '
             f'calcMode="spline" keySplines="0 0 1 1;.6 0 .9 .6;0 0 1 1" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;.7;.7;0" keyTimes="0;.12;.8;1" dur="{cyc}s" begin="{t_done:.2f}s" repeatCount="indefinite"/></path>')
    holding = f'<g transform="translate({sx} {sy - 10})"><use href="#{uid}-plane" xlink:href="#{uid}-plane"/></g>'
    status = (f'<text x="{px0 + pw - 14}" y="{py0 + 22}" text-anchor="end" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="{MUTE}">'
              f'STATUS: HOLDING<set attributeName="opacity" to="0" begin="{t_done:.2f}s" fill="freeze"/></text>'
              + _at(t_done, f'<text x="{px0 + pw - 14}" y="{py0 + 22}" text-anchor="end" font-family="{MONO}" font-size="10.5" '
                            f'font-weight="700" letter-spacing="1.5" fill="{HI}">STATUS: CLEARED · TAKEOFF</text>'))
    scene = (f'<clipPath id="{uid}-sky"><rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" rx="8"/></clipPath>'
             f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" rx="8" fill="#0c0b0a" stroke="{EDGE}"/>'
             f'<g clip-path="url(#{uid}-sky)">{stars}'
             f'<rect x="{px0}" y="{gy}" width="{pw}" height="{ph}" fill="#11100e"/>'
             f'<line x1="{px0}" y1="{gy}" x2="{px0 + pw}" y2="{gy}" stroke="{EDGE}"/>{dashes}{lights}{tower}'
             f'<g opacity="1">{holding}<set attributeName="opacity" to="0" begin="{t_done:.2f}s" fill="freeze"/></g>'
             f'{trail}{motion}</g>'
             f'<text x="{px0 + 14}" y="{py0 + 22}" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="{MUTE}">RWY 08 · BLR</text>{status}')
    body.append(f'<defs>{plane}</defs>' + _at(t, scene))

    # ── cockpit readouts ──
    n = len(p["stats"])
    bw = (W - 56 - (n - 1) * 14) / n
    for k, (v, lab) in enumerate(p["stats"]):
        bx = 28 + k * (bw + 14)
        body.append(_at(t_done + .2 + k * .15,
                        f'<rect x="{bx:.0f}" y="384" width="{bw:.0f}" height="56" rx="6" fill="#070706" stroke="{EDGE}"/>'
                        f'<text x="{bx + 16:.0f}" y="404" font-family="{MONO}" font-size="9.5" fill="{MUTE}" letter-spacing="2">{esc(lab.upper())}</text>'
                        f'<text x="{bx + 16:.0f}" y="430" font-family="{MONO}" font-size="22" font-weight="800" fill="{HI}">{esc(v)}</text>'
                        f'<circle cx="{bx + bw - 16:.0f}" cy="400" r="3" fill="{HI}"><animate attributeName="opacity" values="1;.3;1" '
                        f'dur="{1.6 + k * .3:.1f}s" repeatCount="indefinite"/></circle>'))
    return (_open(W, H, f"{p['name']}: {' '.join(p['desc'])}") + f"<defs>{crt_defs}{clip}</defs>"
            + _window(W, H, f"sahitya@github: ~/projects/{uid} — zsh", p["repo"].replace("https://", ""),
                      p.get("site", "").replace("https://", ""))
            + cmd + "".join(body) + crt + "</svg>")


def mixer(m: dict, stats: dict, prof: dict) -> str:
    """Repos I've sent pull requests to, as channel strips on a mixing desk: gain knob, bouncing LED meter,
    fader and a masking-tape label each, plus a master channel for the total."""
    hide = set(prof.get("hide_repos", []))
    repos = [(r, n) for r, n in stats.get("pr_repos", []) if r not in hide and not r.startswith(stats["login"] + "/")]
    total = m["pr_count"]                                 # master = every merged PR, hidden repos included
    # one channel per organisation, so all of checkstyle's repos add up on one strip
    by_owner: dict[str, list[tuple[str, int]]] = {}
    for r, n in repos:
        by_owner.setdefault(r.split("/")[0], []).append((r, n))
    groups = sorted(by_owner.items(), key=lambda kv: -sum(n for _, n in kv[1]))[:7]
    rows = []
    for owner, items in groups:
        n = sum(c for _, c in items)
        rows.append((f"{owner}/{owner}" if len(items) > 1 else items[0][0], n, len(items)))
    nrepos = {r: k for r, _, k in rows}
    rows = [(r, n) for r, n, _ in rows]
    W, H = 1000, 500
    crt_defs, crt = _crt(W, H, "x")
    clip, cmd, t = _typed(28, 72, "gh search prs --author=@me | mixdown", .2, "x1")
    strips = rows + [("MASTER/master", total)]
    n_s = len(strips)
    sw, sg = 106, 8
    x0 = (W - n_s * sw - (n_s - 1) * sg) / 2
    top = max((n for _, n in rows), default=1)
    rng = random.Random(stats["login"] + "mix")
    SEG, my0, my1 = 16, 176, 336                       # meter segments and their vertical span
    seg_h = (my1 - my0) / SEG
    defs = [crt_defs, clip,
            f'<linearGradient id="x-desk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16140f"/><stop offset="1" stop-color="#0c0b09"/></linearGradient>',
            f'<linearGradient id="x-cap" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9d3c7"/><stop offset=".5" stop-color="#8f897d"/><stop offset="1" stop-color="#cfc8bb"/></linearGradient>',
            f'<radialGradient id="x-knob" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#3a3631"/><stop offset="1" stop-color="#111"/></radialGradient>']
    body = [f'<rect x="{x0 - 14:.0f}" y="96" width="{W - 2 * x0 + 28:.0f}" height="{H - 96 - 46}" rx="10" fill="url(#x-desk)" stroke="{EDGE}"/>']
    for sx, sy in [(x0 - 6, 104), (W - x0 + 6, 104), (x0 - 6, H - 58), (W - x0 + 6, H - 58)]:
        body.append(f'<circle cx="{sx:.0f}" cy="{sy}" r="3" fill="#2a2723"/><path d="M{sx - 2:.0f},{sy} h4" stroke="#0a0a0a"/>')
    for k, (repo, n) in enumerate(strips):
        master = k == n_s - 1
        x = x0 + k * (sw + sg)
        cx = x + sw / 2
        level = 1 if master else max(.08, (n / top) ** .75)
        lit = max(1, round(level * SEG))
        owner, name = repo.split("/", 1)
        start = t + .3 + k * .12
        g = [f'<rect x="{x:.1f}" y="108" width="{sw}" height="{H - 168}" rx="6" fill="#0f0e0c" stroke="{"#5a4a2a" if master else "#201e1a"}"/>',
             f'<text x="{cx:.1f}" y="126" text-anchor="middle" font-family="{MONO}" font-size="9.5" fill="{HI if master else MUTE}" letter-spacing="1.5">'
             f'{"MASTER" if master else f"CH {k + 1}"}</text>']
        # gain knob
        ang = -135 + 270 * level
        g.append(f'<circle cx="{cx - 18:.1f}" cy="150" r="11" fill="url(#x-knob)" stroke="#2c2924"/>'
                 f'<line x1="{cx - 18:.1f}" y1="150" x2="{cx - 18:.1f}" y2="141" stroke="{HI}" stroke-width="2" stroke-linecap="round">'
                 f'<animateTransform attributeName="transform" type="rotate" from="-135 {cx - 18:.1f} 150" to="{ang:.0f} {cx - 18:.1f} 150" '
                 f'begin="{start:.2f}s" dur=".9s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/></line>'
                 f'<text x="{cx + 2:.1f}" y="153" font-family="{MONO}" font-size="8.5" fill="{MUTE}" letter-spacing="1">GAIN</text>')
        # LED meter: segments, lit up to the level, bouncing a little
        mx = x + 18
        unlit, lit_s = [], []
        for i in range(SEG):
            yy = my1 - (i + 1) * seg_h + 1.2
            col = "#ff5a1f" if i >= SEG - 2 else "#ffc35c" if i >= SEG - 6 else HI
            unlit.append(f'<rect x="{mx}" y="{yy:.1f}" width="26" height="{seg_h - 2.4:.1f}" rx="1.5" fill="#1d1a16"/>')
            if i < lit:
                lit_s.append(f'<rect x="{mx}" y="{yy:.1f}" width="26" height="{seg_h - 2.4:.1f}" rx="1.5" fill="{col}"/>')
        full = lit * seg_h
        lows = [full * rng.uniform(.62, .95) for _ in range(5)]
        vals = ";".join(f"{v:.1f}" for v in [full] + lows + [full])
        ys = ";".join(f"{my1 - v:.1f}" for v in [full] + lows + [full])
        g.append("".join(unlit)
                 + f'<clipPath id="x-m{k}"><rect x="{mx - 2}" y="{my1}" width="30" height="0">'
                 f'<animate attributeName="height" from="0" to="{full:.1f}" begin="{start:.2f}s" dur=".6s" fill="freeze"/>'
                 f'<animate attributeName="y" from="{my1}" to="{my1 - full:.1f}" begin="{start:.2f}s" dur=".6s" fill="freeze"/>'
                 f'<animate attributeName="height" values="{vals}" dur="{rng.uniform(1.1, 1.7):.2f}s" begin="{start + .6:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{ys}" dur="{rng.uniform(1.1, 1.7):.2f}s" begin="{start + .6:.2f}s" repeatCount="indefinite"/>'
                 f'</rect></clipPath><g clip-path="url(#x-m{k})">{"".join(lit_s)}</g>'
                 # peak-hold light
                 + _at(start + .6, f'<rect x="{mx}" y="{my1 - full + 1.2:.1f}" width="26" height="2" fill="#fff1d0" opacity=".9"/>'))
        # fader slot and cap
        fx = x + sw - 30
        fy = my1 - level * (my1 - my0)
        g.append(f'<rect x="{fx - 1.5}" y="{my0}" width="3" height="{my1 - my0}" rx="1.5" fill="#000" stroke="#24211c"/>'
                 + "".join(f'<line x1="{fx + 7}" y1="{my0 + j * (my1 - my0) / 8:.0f}" x2="{fx + 11}" y2="{my0 + j * (my1 - my0) / 8:.0f}" stroke="#2f2b25"/>' for j in range(9))
                 + f'<g><animateTransform attributeName="transform" type="translate" from="0 {my1 - fy:.1f}" to="0 0" begin="{start:.2f}s" dur="1s" '
                 f'fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>'
                 f'<rect x="{fx - 11}" y="{fy - 8:.1f}" width="22" height="16" rx="2.5" fill="url(#x-cap)" stroke="#000"/>'
                 f'<line x1="{fx - 9}" y1="{fy:.1f}" x2="{fx + 9}" y2="{fy:.1f}" stroke="{"#c2410c" if master else "#111"}" stroke-width="1.6"/></g>')
        # readout
        g.append(f'<rect x="{x + 14}" y="350" width="{sw - 28}" height="22" rx="3" fill="#050505" stroke="#24211c"/>'
                 + _at(start + .5, f'<text x="{cx:.1f}" y="366" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="800" '
                                   f'fill="{HI}">{n}<tspan fill="{MUTE}" font-size="9.5" font-weight="400"> PR{"s" if n != 1 else ""}</tspan></text>'))
        # masking-tape label
        rot = rng.uniform(-2.2, 2.2)
        nm = name if len(name) <= 14 else name[:13] + "…"
        ow = owner if len(owner) <= 17 else owner[:16] + "…"
        g.append(f'<g transform="rotate({rot:.1f} {cx:.1f} 400)"><rect x="{x + 6}" y="384" width="{sw - 12}" height="34" fill="{"#f5a524" if master else "#e9dfc6"}" opacity=".92"/>'
                 f'<text x="{cx:.1f}" y="399" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="800" fill="#1b1712">'
                 f'{esc("ALL REPOS" if master else nm)}</text>'
                 f'<text x="{cx:.1f}" y="412" text-anchor="middle" font-family="{MONO}" font-size="8.5" fill="#5a5144">{esc("total" if master else (f"{nrepos[repo]} repos" if nrepos.get(repo, 1) > 1 else ow))}</text></g>')
        body.append("".join(g))
    legend = (f'<text x="{W - 28}" y="72" text-anchor="end" font-family="{MONO}" font-size="12.5" xml:space="preserve">'
              f'<tspan fill="{HI}" font-weight="700">{len(repos) + len([r for r, _ in stats.get("pr_repos", []) if r in hide])}</tspan><tspan fill="{DIM}"> repos   </tspan>'
              f'<tspan fill="{HI}" font-weight="700">{total}</tspan><tspan fill="{DIM}"> pull requests on the master bus</tspan></text>')
    return (_open(W, H, "Mixing desk of pull requests by repository: " + ", ".join(f"{r} {n}" for r, n in rows))
            + f"<defs>{''.join(defs)}</defs>"
            + _window(W, H, f"{prof['user']}@{prof['host']}: ~/mixdown — zsh", "one channel per organisation · level = merged pull requests · refreshed hourly",
                      f"updated {now_ist():%Y-%m-%d}")
            + cmd + _at(t, "".join(body)) + _at(t + 1.6, legend) + crt + "</svg>")
