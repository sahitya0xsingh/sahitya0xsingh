"""Two terminal cards for the profile: a `whoami` hero with a halftone portrait, and a contribution log.

One window style, one accent colour, real data only.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from common import ROOT, esc, now_ist

# ── theme ───────────────────────────────────────────────────────────────────
WIN = "#111113"
BAR = "#19191c"
EDGE = "#27272a"
TEXT = "#e4e4e7"
DIM = "#a1a1aa"
MUTE = "#5c5c66"
AMBER = "#f5a524"
RAMP = ["#1c1c20", "#4a3206", "#8a5a0b", "#d08a14", "#ffc35c"]  # empty → busiest
MONO = ("ui-monospace, 'SF Mono', SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")


def _open(w: int, h: int, label: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}"><title>{esc(label)}</title>')


def _window(w: int, h: int, title: str, foot_l: str, foot_r: str) -> str:
    dots = "".join(f'<circle cx="{22 + i * 18}" cy="18" r="5.5" fill="{EDGE}"/>' for i in range(3))
    return (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{WIN}" stroke="{EDGE}"/>'
            f'<path d="M12.5,.5H{w - 12.5}A12,12 0 0 1 {w - .5},12.5V36H.5V12.5A12,12 0 0 1 12.5,.5Z" fill="{BAR}"/>'
            f'<line x1=".5" y1="36" x2="{w - .5}" y2="36" stroke="{EDGE}"/>{dots}'
            f'<text x="{w / 2}" y="22" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTE}">{esc(title)}</text>'
            f'<line x1="24" y1="{h - 34}" x2="{w - 24}" y2="{h - 34}" stroke="{EDGE}"/>'
            f'<text x="24" y="{h - 14}" font-family="{MONO}" font-size="11" fill="{MUTE}">{esc(foot_l)}</text>'
            f'<text x="{w - 24}" y="{h - 14}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTE}">{esc(foot_r)}</text>')


def _at(t: float, body: str) -> str:
    """Hidden until t seconds, then shown for good."""
    return f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>{body}</g>'


def _typed(x: float, y: float, cmd: str, t: float, uid: str, size: float = 14) -> tuple[str, float]:
    """A prompt line whose command types itself in; returns the svg and when typing ends."""
    cw = size * 0.602
    dur = max(.25, len(cmd) * .045)
    px = x + 4 * cw
    clip = (f'<clipPath id="{uid}"><rect x="{px}" y="{y - size}" width="0" height="{size * 1.5}">'
            f'<animate attributeName="width" from="0" to="{len(cmd) * cw + 2:.1f}" begin="{t + .15:.2f}s" '
            f'dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
    line = (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" xml:space="preserve">'
            f'<tspan fill="{AMBER}">~ </tspan><tspan fill="{MUTE}">$ </tspan></text>'
            f'<text x="{px}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{TEXT}" '
            f'clip-path="url(#{uid})" xml:space="preserve">{esc(cmd)}</text>')
    return clip, _at(t, line), t + .15 + dur


def _cursor(x: float, y: float, t: float, size: float = 14) -> str:
    return _at(t, f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" xml:space="preserve">'
                  f'<tspan fill="{AMBER}">~ </tspan><tspan fill="{MUTE}">$ </tspan></text>'
                  f'<rect x="{x + 4 * size * .602:.1f}" y="{y - size + 2}" width="{size * .6:.1f}" height="{size + 1}" fill="{AMBER}">'
                  f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" '
                  f'begin="{t:.2f}s" repeatCount="indefinite"/></rect>')


# ── halftone portrait ──────────────────────────────────────────────────────
def _halftone(x0: float, y0: float, size: float, n: int = 64) -> str:
    src = next((ROOT / "assets" / f for f in ("photo.jpg", "photo.jpeg", "photo.png")
                if (ROOT / "assets" / f).exists()), None)
    if not src:
        return ""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return ""
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
            # soft circular vignette so the portrait floats instead of ending in a hard square
            d = ((i - cx) ** 2 + ((j - cy) * .9) ** 2) ** .5 / (n / 2)
            v *= max(0.0, min(1.0, (1.0 - d) / .25))
            r = cell * .55 * v ** 1.3
            if r < .35:
                continue
            col = RAMP[4] if v > .78 else RAMP[3] if v > .5 else RAMP[2]
            dots.append(f'<circle cx="{x0 + (i + .5) * cell:.1f}" cy="{y0 + (j + .5) * cell:.1f}" r="{r:.2f}" fill="{col}"/>')
    mx, my = x0 + size / 2, y0 + size / 2
    reveal = (f'<clipPath id="develop"><circle cx="{mx}" cy="{my}" r="0">'
              f'<animate attributeName="r" from="0" to="{size * .75:.0f}" begin=".3s" dur="1.6s" '
              f'calcMode="spline" keySplines=".2 .7 .2 1" fill="freeze"/></circle></clipPath>')
    return reveal + f'<g clip-path="url(#develop)">{"".join(dots)}</g>'


# ── cards ──────────────────────────────────────────────────────────────────
def hero(m: dict, prof: dict, stats: dict) -> str:
    W, H = 1000, 460
    out = [_open(W, H, f"{prof['name']}: {prof['role']}"), "<defs>"]
    body = []
    body.append(_halftone(40, 66, 320))

    x, y, t = 400, 84, .4
    defs = []
    c, ln, t = _typed(x, y, "whoami", t, "c1")
    defs.append(c)
    body.append(ln)
    t += .15
    body.append(_at(t, f'<text x="{x}" y="{y + 44}" font-family="{MONO}" font-size="34" font-weight="700" '
                       f'fill="{TEXT}" letter-spacing="-.5">{esc(prof["name"])}</text>'
                       f'<text x="{x}" y="{y + 70}" font-family="{MONO}" font-size="13.5" fill="{DIM}">'
                       f'{esc(prof["headline"])}</text>'))
    y += 112
    c, ln, t = _typed(x, y, "cat now.txt", t + .35, "c2")
    defs.append(c)
    body.append(ln)
    t += .15
    for k, line in enumerate(prof["now"]):
        body.append(_at(t + k * .08, f'<text x="{x}" y="{y + 26 + k * 21}" font-family="{MONO}" font-size="13.5" '
                                     f'fill="{TEXT}">{esc(line)}</text>'))
    y += 26 + len(prof["now"]) * 21 + 20
    c, ln, t = _typed(x, y, "gh stats", t + .45, "c3")
    defs.append(c)
    body.append(ln)
    t += .15
    nums = [(str(m["pr_count"]), "merged PRs"), (str(m["total"]), "contributions / yr"),
            (str(m["repo_count"]), "repositories"), (f'{m["longest"]}d', "longest streak")]
    colw = (W - 40 - x) / len(nums)
    for k, (v, lab) in enumerate(nums):
        cx0 = x + k * colw
        body.append(_at(t + k * .1, f'<text x="{cx0}" y="{y + 40}" font-family="{MONO}" font-size="26" font-weight="700" '
                                    f'fill="{AMBER}">{esc(v)}</text>'
                                    f'<text x="{cx0}" y="{y + 60}" font-family="{MONO}" font-size="11.5" fill="{DIM}">{esc(lab)}</text>'))
    y += 98
    body.append(_cursor(x, y, t + .6))

    out += defs + ["</defs>", _window(W, H, f"{prof['user']}@{prof['host']}: ~ — zsh",
                                      prof["footer"], f"updated {now_ist():%Y-%m-%d}")]
    out += body + ["</svg>"]
    return "".join(out)


def activity(m: dict, stats: dict, prof: dict) -> str:
    W, H = 1000, 304
    days = stats["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    first_sun = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    nz = sorted(d["count"] for d in days if d["count"])
    q = [nz[int(len(nz) * f)] for f in (.25, .5, .75)] if nz else [1, 2, 3]

    def level(c: int) -> int:
        return 0 if c == 0 else 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4

    gx, gy, cs, gap = 78, 118, 13, 3
    cols: dict[int, list[str]] = {}
    months, last_m = [], None
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        c, r = (date - first_sun).days // 7, (date.weekday() + 1) % 7
        cols.setdefault(c, []).append(
            f'<rect x="{gx + c * (cs + gap)}" y="{gy + r * (cs + gap)}" width="{cs}" height="{cs}" rx="3" '
            f'fill="{RAMP[level(d["count"])]}"><title>{d["count"]} on {date:%d %b %Y}</title></rect>')
        if date.month != last_m and date.day <= 7:
            months.append(f'<text x="{gx + c * (cs + gap)}" y="{gy - 10}" font-family="{MONO}" font-size="11" '
                          f'fill="{MUTE}">{date:%b}</text>')
            last_m = date.month
    body = []
    clip, cmd, t = _typed(28, 72, f"gh contributions --user {stats['login']} --last 12mo", .2, "a1")
    grid = "".join(_at(t + .1 + c * .018, "".join(v)) for c, v in sorted(cols.items()))
    labels = "".join(f'<text x="{gx - 12}" y="{gy + r * (cs + gap) + 10}" text-anchor="end" font-family="{MONO}" '
                     f'font-size="10.5" fill="{MUTE}">{n}</text>' for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    legend_x = W - 28 - 5 * 17
    legend = (f'<text x="{legend_x - 8}" y="{gy + 7 * (cs + gap) + 22}" text-anchor="end" font-family="{MONO}" '
              f'font-size="11" fill="{MUTE}">less</text>'
              + "".join(f'<rect x="{legend_x + k * 17}" y="{gy + 7 * (cs + gap) + 12}" width="{cs}" height="{cs}" rx="3" '
                        f'fill="{RAMP[k]}"/>' for k in range(5))
)
    best = m["best"]
    best_d = dt.date.fromisoformat(best["date"]).strftime("%d %b") if best["date"] else "-"
    summary = (f'<text x="{gx}" y="{gy + 7 * (cs + gap) + 22}" font-family="{MONO}" font-size="12.5" '
               f'xml:space="preserve"><tspan fill="{AMBER}" font-weight="700">{m["total"]}</tspan>'
               f'<tspan fill="{DIM}"> contributions   </tspan><tspan fill="{TEXT}">{m["active"]}</tspan>'
               f'<tspan fill="{DIM}"> active days   best day </tspan><tspan fill="{TEXT}">{best["count"]} on {best_d}</tspan>'
               f'<tspan fill="{DIM}">   longest streak </tspan><tspan fill="{TEXT}">{m["longest"]}d</tspan></text>')
    body += [labels, "".join(months), grid, _at(t + 1.2, summary + legend)]
    return (_open(W, H, f"Contributions in the last year: {m['total']}") + f"<defs>{clip}</defs>"
            + _window(W, H, f"{prof['user']}@{prof['host']}: ~/activity — zsh",
                      "data: GitHub contribution calendar", f"updated {now_ist():%Y-%m-%d}")
            + cmd + "".join(body) + "</svg>")
