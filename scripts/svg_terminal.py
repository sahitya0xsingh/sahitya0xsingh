"""Header: a cyberdeck. CRT power-on → BIOS POST → neofetch, framed by live rails."""
from __future__ import annotations

import datetime as dt
import random

from common import (ACCENT, BG, BRIGHT, GREEN, LINE, LINE2, MONO, MUTED, RAMP,
                    TEXT, esc, glow, now_ist, svg_open)
from frame import hud_frame, scanlines, window, _barcode

W, H = 1000, 600
CW = 8.4  # monospace advance at 14px

ZERO = [".#####.", "##...##", "##...##", "##..###", "##.#.##", "###..##", "##...##", "##...##", ".#####."]
XCH = [".......", ".......", ".......", "##...##", ".##.##.", "..###..", "..###..", ".##.##.", "##...##"]
RED, CYAN = "#ff3b6b", "#39c5cf"


def _monogram(x0: int, y0: int, start: float) -> str:
    rnd = random.Random(0x17)
    px, step = 12, 14
    cells = [(c, r) for r in range(9) for c, ch in enumerate(ZERO[r] + ".." + XCH[r]) if ch == "#"]

    def layer(fill, appear=True, extra=""):
        rs = []
        for c, r in cells:
            x, y = x0 + c * step, y0 + r * step
            if appear:
                t = start + rnd.uniform(0, .5)
                rs.append(f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="{fill}" opacity="0">'
                          f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></rect>')
            else:
                rs.append(f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="{fill}"/>')
        return "".join(rs)

    g0 = start + 1.0
    kt = "0;.86;.87;.89;.9;.95;.96;1"
    split = (f'<g opacity="0">{layer(RED, False)}'
             f'<animate attributeName="opacity" values="0;0;.75;.75;0;0;.5;0" keyTimes="{kt}" dur="5s" begin="{g0}s" repeatCount="indefinite"/>'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;-5 0;4 1;0 0;0 0;-3 0;0 0" keyTimes="{kt}" dur="5s" begin="{g0}s" repeatCount="indefinite"/></g>'
             f'<g opacity="0">{layer(CYAN, False)}'
             f'<animate attributeName="opacity" values="0;0;.75;.75;0;0;.5;0" keyTimes="{kt}" dur="5s" begin="{g0}s" repeatCount="indefinite"/>'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;5 0;-4 -1;0 0;0 0;3 0;0 0" keyTimes="{kt}" dur="5s" begin="{g0}s" repeatCount="indefinite"/></g>')
    main = (f'<g filter="url(#soft)">{layer("url(#mono)")}'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;2 0;-2 0;0 0;0 0;1 0;0 0" keyTimes="{kt}" dur="5s" begin="{g0}s" repeatCount="indefinite"/></g>')
    return split + main


def _hex_rail(x: int, y: int, w: int, h: int, stats: dict) -> str:
    counts = [d["count"] for d in stats["days"]][-120:]
    lines = []
    for i in range(0, 120, 2):
        a = counts[i] if i < len(counts) else 0
        b = counts[i + 1] if i + 1 < len(counts) else 0
        lines.append((f"{i * 2:04X}", f"{a:02X}", f"{b:02X}"))
    lh = 13
    block_h = len(lines) * lh
    txt = []
    for k in range(2):  # duplicated for a seamless loop
        for j, (addr, a, b) in enumerate(lines):
            yy = y + 10 + (k * len(lines) + j) * lh
            hot_a = ACCENT if a != "00" else LINE2
            hot_b = ACCENT if b != "00" else LINE2
            txt.append(f'<text x="{x}" y="{yy}" font-family="{MONO}" font-size="8.5" xml:space="preserve">'
                       f'<tspan fill="{MUTED}" opacity=".6">{addr} </tspan><tspan fill="{hot_a}">{a}</tspan>'
                       f'<tspan fill="{hot_b}"> {b}</tspan></text>')
    return (f'<clipPath id="hexclip"><rect x="{x - 4}" y="{y}" width="{w}" height="{h}"/></clipPath>'
            f'<g clip-path="url(#hexclip)"><g>{"".join(txt)}'
            f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 -{block_h}" '
            f'dur="40s" repeatCount="indefinite"/></g>'
            f'<rect x="{x - 4}" y="{y}" width="{w}" height="40" fill="url(#fadeT)"/>'
            f'<rect x="{x - 4}" y="{y + h - 40}" width="{w}" height="40" fill="url(#fadeB)"/></g>')


def _radar(cx: int, cy: int, r: int, m: dict) -> str:
    rnd = random.Random(m["total"])
    blips = "".join(
        f'<circle cx="{cx + rnd.uniform(-r * .65, r * .65):.1f}" cy="{cy + rnd.uniform(-r * .65, r * .65):.1f}" r="1.6" fill="{GREEN}" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;0" dur="3s" begin="{rnd.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>'
        for _ in range(min(7, 2 + m["week"] // 4)))
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#07101c" stroke="{ACCENT}" stroke-opacity=".5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .62:.1f}" fill="none" stroke="{ACCENT}" stroke-opacity=".25"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .28:.1f}" fill="none" stroke="{ACCENT}" stroke-opacity=".25"/>'
            f'<path d="M{cx - r},{cy}h{2 * r}M{cx},{cy - r}v{2 * r}" stroke="{ACCENT}" stroke-opacity=".2"/>'
            f'<g><path d="M{cx},{cy} L{cx + r},{cy} A{r},{r} 0 0 0 {cx + r * .5:.1f},{cy - r * .866:.1f} Z" fill="url(#sweep)"/>'
            f'<line x1="{cx}" y1="{cy}" x2="{cx + r}" y2="{cy}" stroke="{ACCENT}" stroke-width="1.4"/>'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" '
            f'dur="4s" repeatCount="indefinite"/></g>{blips}'
            f'<text x="{cx}" y="{cy + r + 14}" text-anchor="middle" font-family="{MONO}" font-size="7.5" '
            f'fill="{MUTED}" letter-spacing="1.5">SCAN</text>')


def _scope(x: int, y: int, w: int, h: int, stats: dict) -> str:
    counts = [d["count"] for d in stats["days"]][-120:]
    peak = max(1, max(counts))
    n = len(counts)
    pts = [(x + 10 + i * (w - 20) / max(1, n - 1), y + h - 10 - (c / peak) * (h - 26)) for i, c in enumerate(counts)]
    d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    length = sum(((pts[i + 1][0] - pts[i][0]) ** 2 + (pts[i + 1][1] - pts[i][1]) ** 2) ** .5 for i in range(n - 1))
    grid = "".join(f'<line x1="{x + gx}" y1="{y}" x2="{x + gx}" y2="{y + h}" stroke="{LINE}"/>'
                   for gx in range(0, w, 40))
    grid += "".join(f'<line x1="{x}" y1="{y + gy}" x2="{x + w}" y2="{y + gy}" stroke="{LINE}"/>'
                    for gy in range(0, h, 16))
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#060a10" stroke="{LINE2}"/>{grid}'
            f'<path d="{d}" fill="none" stroke="{ACCENT}" stroke-opacity=".18" stroke-width="1"/>'
            f'<path d="{d}" fill="none" stroke="{GREEN}" stroke-width="1.6" filter="url(#soft)" '
            f'stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}">'
            f'<animate attributeName="stroke-dashoffset" values="{length:.0f};0;0" keyTimes="0;.8;1" dur="7s" repeatCount="indefinite"/></path>'
            f'<circle r="3" fill="{BRIGHT}" filter="url(#soft)"><animateMotion path="{d}" keyPoints="0;1;1" '
            f'keyTimes="0;.8;1" calcMode="linear" dur="7s" repeatCount="indefinite"/></circle>'
            f'<text x="{x + 8}" y="{y + 12}" font-family="{MONO}" font-size="8.5" fill="{GREEN}" letter-spacing="1.5">'
            f'CH1 · COMMITS/DAY · 120D</text>'
            f'<text x="{x + w - 8}" y="{y + 12}" text-anchor="end" font-family="{MONO}" font-size="8.5" '
            f'fill="{MUTED}" letter-spacing="1.5">VPP {peak} · 5ms/div</text>')


def render(m: dict, prof: dict, stats: dict) -> str:
    t = now_ist()
    user, host = prof["user"], prof["host"]
    pu = f"{user}@{host}"
    wx, wy, ww, wh = 96, 74, 808, 400
    chrome, clip = window(wx, wy, ww, wh, f"{pu}: ~ — zsh — 120×32",
                          status_left="[0] zsh  1:readme  2:projects  3:oss",
                          status_right=f"streak {m['streak']}d │ {t:%d %b %Y} IST", wid="tw")
    bx = wx + 24
    y1 = wy + 58

    # ── act 1: BIOS POST ──
    post_start = 0.8
    post_rows = [
        ("0xBIOS v17.0", f"(c) {stats['login']}", None),
        ("CPU0 ............", "human, caffeinated", "OK"),
        ("MEM .............", f"{m['active']}/{m['span']} days active", "OK"),
        ("GIT .............", f"{m['total']} contributions indexed", "OK"),
        ("NET .............", f"github.com/{stats['login']}", "LINK"),
        ("SEC .............", "curiosity: unrestricted", "OK"),
        ("BOOT ............", "loading zsh", None),
    ]
    post = []
    for i, (a, b, st) in enumerate(post_rows):
        yy = y1 + i * 20
        stat = (f'<tspan fill="{MUTED}">  [ </tspan><tspan fill="{GREEN}" font-weight="700">{st}</tspan>'
                f'<tspan fill="{MUTED}"> ]</tspan>') if st else ""
        post.append(f'<text x="{bx}" y="{yy}" font-family="{MONO}" font-size="13" xml:space="preserve" opacity="0">'
                    f'<tspan fill="{ACCENT if i == 0 else MUTED}" font-weight="{700 if i == 0 else 400}">{esc(a)} </tspan>'
                    f'<tspan fill="{TEXT}">{esc(b)}</tspan>{stat}'
                    f'<set attributeName="opacity" to="1" begin="{post_start + i * .16:.2f}s" fill="freeze"/></text>')
    bar_y = y1 + len(post_rows) * 20 - 4
    bar_t = post_start + len(post_rows) * .16
    post.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{bar_t - .1:.2f}s" fill="freeze"/>'
                f'<rect x="{bx}" y="{bar_y}" width="300" height="8" fill="none" stroke="{LINE2}"/>'
                f'<rect x="{bx + 2}" y="{bar_y + 2}" width="0" height="4" fill="{ACCENT}">'
                f'<animate attributeName="width" from="0" to="296" begin="{bar_t:.2f}s" dur=".6s" fill="freeze"/></rect></g>')
    post_end = bar_t + .8
    act1 = (f'<g>{"".join(post)}<set attributeName="opacity" to="0" begin="{post_end:.2f}s" fill="freeze"/></g>'
            f'<rect x="{wx}" y="{wy + 30}" width="{ww}" height="{wh - 52}" fill="{BG}" opacity="0">'
            f'<animate attributeName="opacity" values="0;.9;0" begin="{post_end - .1:.2f}s" dur=".25s" fill="freeze"/></rect>')

    # ── act 2: neofetch ──
    cmd = "neofetch"
    pw = len(f"{pu}:~$ ") * CW
    ts = post_end + .3
    per = .075
    te = ts + per * len(cmd)
    os_ = te + .35

    def prompt(y: float) -> str:
        return (f'<text x="{bx}" y="{y}" font-family="{MONO}" font-size="14">'
                f'<tspan fill="{GREEN}">{esc(pu)}</tspan><tspan fill="{MUTED}">:</tspan>'
                f'<tspan fill="{ACCENT}">~</tspan><tspan fill="{MUTED}">$ </tspan></text>')

    widths = ";".join(f"{i * CW:.1f}" for i in range(len(cmd) + 1))
    times = ";".join(f"{i / len(cmd):.3f}" for i in range(len(cmd) + 1))
    xs = ";".join(f"{bx + pw + i * CW:.1f}" for i in range(len(cmd) + 1))
    dur = f"{te - ts + .001:.3f}s"
    typed = (f'<clipPath id="typeclip"><rect x="{bx + pw}" y="{y1 - 16}" height="22" width="0">'
             f'<animate attributeName="width" values="{widths}" keyTimes="{times}" calcMode="discrete" '
             f'begin="{ts:.2f}s" dur="{dur}" fill="freeze"/></rect></clipPath>'
             f'<text x="{bx + pw}" y="{y1}" font-family="{MONO}" font-size="14" fill="{BRIGHT}" '
             f'clip-path="url(#typeclip)">{cmd}</text>'
             f'<rect x="{bx + pw}" y="{y1 - 13}" width="8" height="16" fill="{ACCENT}" opacity="0">'
             f'<set attributeName="opacity" to="1" begin="{ts - .2:.2f}s" fill="freeze"/>'
             f'<animate attributeName="x" values="{xs}" keyTimes="{times}" calcMode="discrete" '
             f'begin="{ts:.2f}s" dur="{dur}" fill="freeze"/>'
             f'<set attributeName="opacity" to="0" begin="{os_ - .05:.2f}s" fill="freeze"/></rect>')

    ix, iy, lh = wx + 300, wy + 86, 21
    rows = [
        ("Name", prof["name"]), ("Role", prof["role"]), ("Stack", prof["stack"]),
        ("Tools", prof["tools"]), ("Focus", prof["focus"]),
        ("Uptime", f"{m['streak']} days  (commit streak)"),
        ("Commits", f"{m['total']} in the last year"),
        ("Packages", f"{m['repo_count']} repos · {m['pr_count']} merged upstream"),
        ("Status", f"● {prof['status']}"),
    ]
    lines = [
        (f'<text x="{ix}" y="{iy}" font-family="{MONO}" font-size="14" font-weight="700">'
         f'<tspan fill="{ACCENT}">{esc(user)}</tspan><tspan fill="{TEXT}">@</tspan>'
         f'<tspan fill="{ACCENT}">{esc(host)}</tspan></text>'),
        f'<line x1="{ix}" y1="{iy + 12}" x2="{ix + 200}" y2="{iy + 12}" stroke="{LINE2}"/>',
    ]
    for i, (k, v) in enumerate(rows):
        y = iy + 38 + i * lh
        lines.append(f'<text x="{ix}" y="{y}" font-family="{MONO}" font-size="14" font-weight="700" '
                     f'fill="{ACCENT}">{esc(k)}</text>'
                     f'<text x="{ix + 92}" y="{y}" font-family="{MONO}" font-size="14" '
                     f'fill="{GREEN if k == "Status" else TEXT}">{esc(v)}</text>')
    by = iy + 38 + len(rows) * lh - 6
    pal = ["#0d1117", "#f85149", GREEN, "#d29922", ACCENT, "#bc8cff", CYAN, "#c9d1d9"]
    lines.append("".join(f'<rect x="{ix + i * 28}" y="{by}" width="26" height="12" fill="{c}" '
                         f'stroke="{LINE2}" stroke-width=".6"/>' for i, c in enumerate(pal)))
    reveal = "".join(f'<g opacity="0">{ln}<set attributeName="opacity" to="1" begin="{os_ + i * .07:.2f}s" '
                     f'fill="freeze"/></g>' for i, ln in enumerate(lines))
    y2 = by + 40
    ft = os_ + len(lines) * .07 + .2
    final = (f'<g opacity="0">{prompt(y2)}<rect x="{bx + pw}" y="{y2 - 13}" width="8" height="16" fill="{ACCENT}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" '
             f'begin="{ft:.2f}s" repeatCount="indefinite"/></rect>'
             f'<set attributeName="opacity" to="1" begin="{ft:.2f}s" fill="freeze"/></g>')
    act2 = (f'<g opacity="0">{prompt(y1)}<set attributeName="opacity" to="1" begin="{post_end + .1:.2f}s" fill="freeze"/></g>'
            f'{typed}{_monogram(bx + 12, wy + 112, os_)}{reveal}{final}')

    # screen tear, synced with the monogram glitch
    tear = (f'<rect x="{wx}" y="{wy + 160}" width="{ww}" height="6" fill="{ACCENT}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;.18;0;0" keyTimes="0;.86;.87;.9;1" dur="5s" '
            f'begin="{os_ + 1:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{wy + 160};{wy + 160};{wy + 230};{wy + 120};{wy + 160}" '
            f'keyTimes="0;.86;.87;.9;1" dur="5s" begin="{os_ + 1:.2f}s" repeatCount="indefinite"/></rect>')

    # CRT power-on: the whole window expands from a line
    cx, cy = wx + ww / 2, wy + wh / 2
    screen = (f'<g transform="translate({cx} {cy})"><g>'
              f'<animateTransform attributeName="transform" type="scale" values="1 .004;1 .004;1 1" keyTimes="0;.35;1" '
              f'dur=".75s" calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1" fill="freeze"/>'
              f'<g transform="translate({-cx} {-cy})">{chrome}<g clip-path="url(#{clip})">{act1}{act2}{tear}</g></g>'
              f'</g></g>'
              f'<rect x="{wx}" y="{cy - 1}" width="{ww}" height="2" fill="#e6f1ff" filter="url(#bloom)" opacity="0">'
              f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.4;1" dur=".7s" fill="freeze"/></rect>')

    # ── rails ──
    signal = "".join(f'<rect x="{868 + i * 7}" y="{44 - i * 3}" width="4" height="{6 + i * 3}" fill="{ACCENT}" opacity=".25">'
                     f'<animate attributeName="opacity" values=".25;.95;.25" dur="{1.4 + i * .3:.1f}s" '
                     f'begin="{i * .2:.1f}s" repeatCount="indefinite"/></rect>' for i in range(5))
    top_rail = (f'<circle cx="104" cy="44" r="3.5" fill="{GREEN}" filter="url(#soft)">'
                f'<animate attributeName="opacity" values="1;.3;1" dur="1.4s" repeatCount="indefinite"/></circle>'
                f'<text x="114" y="47" font-family="{MONO}" font-size="9" fill="{GREEN}" letter-spacing="2">SYS.ONLINE</text>'
                f'<text x="196" y="47" font-family="{MONO}" font-size="9" fill="{MUTED}" letter-spacing="2">'
                f'· UPLINK github.com/{esc(stats["login"])}</text>'
                f'<text x="858" y="47" text-anchor="end" font-family="{MONO}" font-size="9" fill="{MUTED}" '
                f'letter-spacing="2">SIGNAL</text>{signal}')
    leds = "".join(
        f'<rect x="938" y="{190 + k * 11}" width="10" height="6" fill="{ACCENT if k % 4 else GREEN}" opacity=".2">'
        f'<animate attributeName="opacity" values=".2;.95;.2" dur="{[1.3, 1.9, 2.6, 3.1][k % 4]}s" '
        f'begin="{(k * .37) % 2:.2f}s" repeatCount="indefinite"/></rect>' for k in range(16))
    right_rail = (_radar(943, 116, 26, m) + leds
                  + f'<text transform="translate(943,{H / 2 + 150}) rotate(90)" text-anchor="middle" font-family="{MONO}" '
                    f'font-size="8" fill="{MUTED}" letter-spacing="3">◆ PID 0x17 ◆ TTY0 ◆</text>')
    left_rail = (f'<text x="30" y="88" font-family="{MONO}" font-size="8" fill="{ACCENT}" letter-spacing="1.5">HEXDUMP</text>'
                 + _hex_rail(30, 96, 62, 368, stats))
    bottom = (_scope(wx, 488, ww, 64, stats)
              + _barcode(40, H - 40, pu + "L", width=40)
              + f'<text x="{W - 40}" y="{H - 33}" text-anchor="end" font-family="{MONO}" font-size="8.5" '
                f'fill="{MUTED}" letter-spacing="1.5">0x{m["total"]:04X} · REV {t:%Y.%m.%d}</text>')

    frame = hud_frame(W, H, tab=f"{stats['login'].upper()} // CYBERDECK", fid="hd")
    return svg_open(W, H, f"{prof['name']} — terminal profile") + f"""
<defs>
  {glow("soft", 1.6)}
  <filter id="bloom" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <linearGradient id="mono" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9ecbff"/><stop offset="1" stop-color="{RAMP[3]}"/></linearGradient>
  <linearGradient id="fadeT" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
  <linearGradient id="fadeB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>
  <radialGradient id="sweep" gradientUnits="userSpaceOnUse" cx="943" cy="116" r="26"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".6"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="{LINE2}"/></pattern>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="14" fill="url(#dots)" opacity=".5"/>
{frame}
{top_rail}{left_rail}{right_rail}{bottom}
{screen}
{scanlines(W, H)}
</svg>
"""
