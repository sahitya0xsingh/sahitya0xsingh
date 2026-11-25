"""Brand cards for the profile: one card system, warm black and amber, gold edges.

hero      a member card: logo, name, quote, chip, a "card number" made of real stats, halftone portrait
records   a split-flap board of personal records, digits rolling like odometers
skyline   one building per week, one lit window per contribution, searchlights over the city
orbit     repos I've sent pull requests to, as planets
project   one card per entry in data/projects.json

Every card shares one frame: brand mark and wordmark top-left, card label top-right, a guilloche
(banknote-style) background, a gold edge and a light sheen that sweeps across. All motion is SVG/SMIL,
so it plays inside GitHub's <img> sandbox.
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


_LOGO: dict[int, str] = {}


def _logo(px: int = 64) -> str:
    """assets/logo.png as an amber mark on transparent, base64 PNG (brightness becomes alpha)."""
    if px in _LOGO:
        return _LOGO[px]
    src = ROOT / "assets" / "logo.png"
    try:
        import base64
        import io
        from PIL import Image, ImageOps
        im = ImageOps.autocontrast(Image.open(src).convert("L")).resize((px, px), Image.LANCZOS)
        mark = Image.new("RGBA", im.size, (245, 165, 36, 0))
        mark.putalpha(im)
        buf = io.BytesIO()
        mark.save(buf, "PNG", optimize=True)
        _LOGO[px] = base64.b64encode(buf.getvalue()).decode()
    except (ImportError, OSError):
        _LOGO[px] = ""
    return _LOGO[px]


def _brandmark(x: float, y: float, size: float, wordmark: bool = True, big: bool = False) -> str:
    b64 = _logo(128 if big else 64)
    img = (f'<image href="data:image/png;base64,{b64}" xlink:href="data:image/png;base64,{b64}" '
           f'x="{x}" y="{y}" width="{size}" height="{size}"/>' if b64 else "")
    if not wordmark:
        return img
    fs, fs2 = (15, 10) if big else (11, 8)
    tx = x + size + (14 if big else 10)
    return (img + f'<text x="{tx}" y="{y + size * .48:.0f}" font-family="{MONO}" font-size="{fs}" font-weight="800" '
                  f'fill="{TEXT}" letter-spacing="{5 if big else 4}">SAHITYA SINGH</text>'
                  f'<text x="{tx}" y="{y + size * .48 + fs2 + 8:.0f}" font-family="{MONO}" font-size="{fs2}" fill="{HI}" '
                  f'letter-spacing="{4 if big else 3}">OPEN SOURCE · ENGINEERING</text>')


def _window(w: int, h: int, title: str, foot_l: str, foot_r: str) -> str:
    """Card body and header: background, guilloche, brand mark, card label; footer line."""
    return (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="22" fill="url(#cbg)"/>'
            f'<g clip-path="url(#cclip)"><rect width="{w}" height="{h}" fill="url(#cguil)"/>'
            f'<circle cx="{w - 90}" cy="40" r="{min(w, h) * .45:.0f}" fill="{HI}" opacity=".045"/></g>'
            + _brandmark(26, 12, 30)
            + f'<text x="{w - 28}" y="32" text-anchor="end" font-family="{MONO}" font-size="10.5" font-weight="700" '
              f'fill="{HI}" letter-spacing="3">{esc(title)}</text>'
              f'<line x1="26" y1="52" x2="{w - 26}" y2="52" stroke="{HI}" stroke-opacity=".18"/>'
              f'<line x1="26" y1="{h - 34}" x2="{w - 26}" y2="{h - 34}" stroke="{HI}" stroke-opacity=".14"/>'
              f'<text x="26" y="{h - 14}" font-family="{MONO}" font-size="10.5" fill="{MUTE}" letter-spacing="1">{esc(foot_l)}</text>'
              f'<text x="{w - 26}" y="{h - 14}" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="{MUTE}" '
              f'letter-spacing="1">{esc(foot_r)}</text>')


def _crt(w: int, h: int, uid: str) -> tuple[str, str]:
    """(defs, overlay) for the card finish: gradients and patterns, then a sweeping sheen and a gold edge."""
    defs = (f'<clipPath id="cclip"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="22"/></clipPath>'
            f'<linearGradient id="cbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1a1611"/>'
            f'<stop offset=".55" stop-color="#0b0a09"/><stop offset="1" stop-color="#140f08"/></linearGradient>'
            f'<linearGradient id="cedge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffc35c" stop-opacity=".9"/>'
            f'<stop offset=".5" stop-color="{HI}" stop-opacity=".15"/><stop offset="1" stop-color="#ffc35c" stop-opacity=".7"/></linearGradient>'
            f'<linearGradient id="csheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#ffe2a8" stop-opacity=".12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<pattern id="cguil" width="28" height="28" patternUnits="userSpaceOnUse">'
            f'<path d="M0,14 Q7,0 14,14 T28,14" fill="none" stroke="{HI}" stroke-opacity=".055"/></pattern>')
    overlay = (f'<g clip-path="url(#cclip)" pointer-events="none">'
               f'<rect x="-400" y="-100" width="240" height="{h + 200}" fill="url(#csheen)" transform="rotate(18)">'
               f'<animate attributeName="x" values="-400;{w + 300}" dur="{3 + w / 400:.1f}s" begin="1s" '
               f'repeatCount="indefinite"/></rect></g>'
               f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="21.5" fill="none" stroke="url(#cedge)" stroke-width="1.5"/>')
    return defs, overlay


def _at(t: float, body: str) -> str:
    """Hidden until t seconds, then shown for good."""
    return f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>{body}</g>'


def _typed(x: float, y: float, title: str, t: float, uid: str, size: float = 17) -> tuple[str, str, float]:
    """A section title that writes itself in behind an amber bar: (clip defs, svg, time it ends)."""
    cw = size * 0.602
    dur = max(.25, len(title) * .03)
    tx = x + 14
    clip = (f'<clipPath id="{uid}"><rect x="{tx}" y="{y - size}" width="0" height="{size * 1.5}">'
            f'<animate attributeName="width" from="0" to="{len(title) * cw + 4:.1f}" begin="{t + .1:.2f}s" '
            f'dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
    line = (f'<rect x="{x}" y="{y - size + 3}" width="4" height="{size}" fill="{HI}"/>'
            f'<text x="{tx}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="800" fill="{TEXT}" '
            f'clip-path="url(#{uid})" xml:space="preserve">{esc(title)}</text>')
    return clip, _at(t, line), t + .1 + dur




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




# ── cards ──────────────────────────────────────────────────────────────────
def hero(m: dict, prof: dict, stats: dict) -> str:
    """The member card: brand mark, name, quote, chip, a card number made of real stats, portrait."""
    W, H = 1000, 580
    fin_defs, fin = _crt(W, H, "h")
    pdefs, portrait = _halftone(600, 120, 330)
    gold = "#ffc35c"
    chip = (f'<g transform="translate(64 300)"><rect width="62" height="46" rx="8" fill="url(#chipg)"/>'
            f'<path d="M0,16H20M0,30H20M42,16H62M42,30H62M20,0V46M42,0V46M20,23H42" stroke="#7a4d08" '
            f'stroke-width="1.4" fill="none"/></g>'
            f'<g transform="translate(146 323)" fill="none" stroke="{DIM}" stroke-width="2" stroke-linecap="round">'
            + "".join(f'<path d="M{i * 7},-{6 + i * 4} a{8 + i * 5},{8 + i * 5} 0 0 1 0,{12 + i * 8}"/>' for i in range(3))
            + "</g>")
    best = m["best"]["count"] if m.get("best") else 0
    groups = [(m["total"], "CONTRIB"), (m["pr_count"], "PULL REQ"), (m["repo_count"], "REPOS"), (best, "BEST DAY")]
    number = "".join(
        _at(.5 + k * .18, f'<text x="{64 + k * 128}" y="410" font-family="{MONO}" font-size="30" font-weight="700" '
                          f'fill="{TEXT}" letter-spacing="4">{n:04d}</text>'
                          f'<text x="{64 + k * 128}" y="430" font-family="{MONO}" font-size="9.5" fill="{MUTE}" '
                          f'letter-spacing="2">{lab}</text>')
        for k, (n, lab) in enumerate(groups))
    q = prof["quote"]
    foot = [("CARDHOLDER", f"@{stats['login'].upper()}", 64), ("BASED IN", prof.get("city", "BENGALURU"), 330),
            ("LONGEST STREAK", f"{m['longest']} DAYS", 560)]
    footer = "".join(f'<text x="{x}" y="502" font-family="{MONO}" font-size="10" fill="{MUTE}" letter-spacing="2">{k}</text>'
                     f'<text x="{x}" y="522" font-family="{MONO}" font-size="14" font-weight="700" fill="{TEXT}" '
                     f'letter-spacing="3">{esc(v)}</text>' for k, v, x in foot)
    body = (f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" rx="28" fill="url(#cbg)"/>'
            f'<g clip-path="url(#cclip)"><rect width="{W}" height="{H}" fill="url(#cguil)"/>'
            f'<circle cx="{W - 120}" cy="80" r="260" fill="{HI}" opacity=".05"/>{portrait}</g>'
            + _brandmark(58, 52, 58, big=True)
            + f'<g transform="translate({W - 64} 70)"><text text-anchor="end" font-family="{MONO}" font-size="10" '
              f'fill="{MUTE}" letter-spacing="3">MEMBER CARD</text><text y="20" text-anchor="end" font-family="{MONO}" '
              f'font-size="13" font-weight="700" fill="{gold}" letter-spacing="3">NO. 0x08</text></g>'
            + _at(.2, f'<text x="64" y="190" font-family="{MONO}" font-size="44" font-weight="800" fill="{TEXT}" '
                      f'letter-spacing="-1">{esc(prof["name"])}</text>'
                      f'<text x="64" y="220" font-family="{MONO}" font-size="14" fill="{DIM}">{esc(prof["headline"])}</text>')
            + _at(.35, f'<rect x="64" y="240" width="3" height="40" fill="{HI}"/>'
                       + "".join(f'<text x="80" y="{256 + i * 20}" font-family="{MONO}" font-size="13.5" font-style="italic" '
                                 f'fill="{TEXT}">{esc(line)}</text>' for i, line in enumerate(q)))
            + chip + number
            + f'<line x1="64" y1="470" x2="{W - 64}" y2="470" stroke="{HI}" stroke-opacity=".25"/>' + footer
            + f'<text x="{W - 64}" y="522" text-anchor="end" font-family="{MONO}" font-size="20" font-weight="800" '
              f'fill="{HI}" letter-spacing="2">openSUSE</text>')
    inset = f'<clipPath id="cclip"><rect x="16" y="16" width="{W - 32}" height="{H - 32}" rx="28"/></clipPath>'
    defs = (inset + fin_defs.split("</clipPath>", 1)[1] + pdefs
            + '<linearGradient id="chipg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffd27a"/>'
              '<stop offset=".5" stop-color="#d9962a"/><stop offset="1" stop-color="#ffcf6e"/></linearGradient>')
    edge = (f'<rect x="16.5" y="16.5" width="{W - 33}" height="{H - 33}" rx="28" fill="none" stroke="url(#cedge)" '
            f'stroke-width="1.5"/>')
    sheen = fin.split("</g>")[0] + "</g>"     # sheen only; this card draws its own inset edge
    return (_open(W, H, f"{prof['name']} member card: {prof['headline']}. {' '.join(q)}")
            + f"<defs>{defs}</defs>" + body + sheen + edge + "</svg>")


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
    clip, cmd, t = _typed(28, 86, "Personal records", .2, "r1")
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
            + _window(W, H, "CARD 03 · RECORDS",
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
    clip, cmd, t = _typed(28, 86, "Commit history: one building per week", .2, "s1")
    defs = [crt_defs, clip,
            f'<clipPath id="ground"><rect x="0" y="0" width="{W}" height="{base}"/></clipPath>',
            f'<clipPath id="skyclip"><rect x="1" y="92" width="{W - 2}" height="{base - 92}"/></clipPath>',
            f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WIN}" stop-opacity="0"/>'
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
            + _window(W, H, "CARD 04 · COMMIT HISTORY",
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
    """A wide terminal card for one project: name, pitch, three headline numbers and tags."""
    W, H = 1000, 300
    uid = p["slug"]
    crt_defs, crt = _crt(W, H, f"p{uid}")
    clip, cmd, t = _typed(28, 86, "Featured project", .2, f"{uid}c")
    body = [_at(t, f'<text x="28" y="112" font-family="{MONO}" font-size="10.5" fill="{HI}" letter-spacing="3">'
                   f'{esc(p["kicker"])}</text>'
                   f'<text x="28" y="150" font-family="{MONO}" font-size="32" font-weight="800" fill="{TEXT}" '
                   f'letter-spacing="-.5">{esc(p["name"])}</text>')]
    for k, line in enumerate(p["desc"]):
        body.append(_at(t + .15 + k * .1, f'<text x="28" y="{178 + k * 19}" font-family="{MONO}" font-size="13" '
                                          f'fill="{DIM}">{esc(line)}</text>'))
    # headline numbers, right side
    sx = 600
    for k, (v, lab) in enumerate(p["stats"]):
        y = 112 + k * 44
        body.append(_at(t + .3 + k * .15, f'<text x="{sx}" y="{y + 18}" font-family="{MONO}" font-size="26" '
                                          f'font-weight="800" fill="{HI}">{esc(v)}</text>'
                                          f'<text x="{sx + 120}" y="{y + 14}" font-family="{MONO}" font-size="12" '
                                          f'fill="{DIM}">{esc(lab)}</text>'
                                          f'<line x1="{sx}" y1="{y + 28}" x2="{W - 28}" y2="{y + 28}" stroke="{EDGE}"/>'))
    # tag chips
    x = 28
    chips = []
    for tag in p["tags"]:
        w = len(tag) * 7.2 + 18
        chips.append(f'<rect x="{x}" y="{H - 70}" width="{w:.0f}" height="20" rx="10" fill="none" stroke="{HI}" stroke-opacity=".5"/>'
                     f'<text x="{x + w / 2:.0f}" y="{H - 56}" text-anchor="middle" font-family="{MONO}" font-size="11" '
                     f'fill="{TEXT}">{esc(tag)}</text>')
        x += w + 8
    body.append(_at(t + .8, "".join(chips)))
    return (_open(W, H, f"{p['name']}: {' '.join(p['desc'])}") + f"<defs>{crt_defs}{clip}</defs>"
            + _window(W, H, "CARD 02 · PROJECTS", p["repo"].replace("https://", ""),
                      p.get("site", "").replace("https://", ""))
            + cmd + "".join(body) + crt + "</svg>")


def orbit(m: dict, stats: dict, prof: dict) -> str:
    """Repos I've sent pull requests to, as planets: size = PRs, inner orbits = more PRs."""
    W, H = 1000, 470
    crt_defs, crt = _crt(W, H, "o")
    hide = set(prof.get("hide_repos", []))
    planets = [(r, n) for r, n in stats.get("pr_repos", []) if r not in hide and not r.startswith(stats["login"] + "/")][:7]
    cx, cy = W / 2, 262
    clip, cmd, t = _typed(28, 86, "Pull requests in orbit", .2, "o1")
    body = [f'<circle cx="{cx}" cy="{cy}" r="70" fill="{HI}" opacity=".05"/>'
            f'<circle cx="{cx}" cy="{cy}" r="30" fill="{HI}" opacity=".9"><animate attributeName="r" values="30;33;30" '
            f'dur="3s" repeatCount="indefinite"/></circle>'
            f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="800" '
            f'fill="{WIN}">ME</text>']
    top = planets[0][1] if planets else 1
    rng = random.Random(stats["login"])
    for k, (repo, n) in enumerate(planets):
        rx = 110 + k * 52
        ry = rx * .36
        path = (f"M{cx - rx},{cy} a{rx},{ry} 0 1,0 {2 * rx},0 a{rx},{ry} 0 1,0 {-2 * rx},0")
        r = 4 + (n / top) ** .5 * 11
        dur = 9 + k * 4.5
        name = repo.split("/")[1]
        body.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry:.1f}" fill="none" stroke="{HI}" '
                    f'stroke-opacity="{.32 - k * .03:.2f}" stroke-dasharray="{"" if k % 2 else "3 5"}"/>')
        body.append(_at(t + .2 + k * .15,
                        f'<g><animateMotion dur="{dur:.1f}s" begin="-{rng.uniform(0, dur):.1f}s" repeatCount="indefinite" path="{path}"/>'
                        f'<circle r="{r + 6:.1f}" fill="{HI}" opacity=".12"/>'
                        f'<circle r="{r:.1f}" fill="{HI}"/>'
                        f'<text x="{r + 8:.0f}" y="4" font-family="{MONO}" font-size="11" fill="{TEXT}">{esc(name)}'
                        f'<tspan fill="{HI}" font-weight="700"> {n}</tspan></text></g>'))
    total = sum(n for _, n in planets)
    legend = (f'<text x="{W - 28}" y="86" text-anchor="end" font-family="{MONO}" font-size="12.5" xml:space="preserve">'
              f'<tspan fill="{HI}" font-weight="700">{len(planets)}</tspan><tspan fill="{DIM}"> repos in orbit   </tspan>'
              f'<tspan fill="{HI}" font-weight="700">{total}</tspan><tspan fill="{DIM}"> pull requests between them</tspan></text>')
    return (_open(W, H, "Pull requests by repository: " + ", ".join(f"{r} {n}" for r, n in planets))
            + f"<defs>{crt_defs}{clip}</defs>"
            + _window(W, H, "CARD 05 · ORBIT", "planet size = pull requests · inner = more",
                      f"updated {now_ist():%Y-%m-%d}")
            + cmd + "".join(body) + _at(t + 1.4, legend) + crt + "</svg>")
