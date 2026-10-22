"""htop-style system monitor, fed by contribution data."""
from __future__ import annotations

import datetime as dt
import hashlib

from common import (ACCENT, AMBER, BG, BRIGHT, GREEN, LINE2, MONO, MUTED, TEXT,
                    esc, svg_open)
from frame import hud_frame, scanlines, window

W, H = 1000, 430
FS = 13


def _t(x, y, s, fill=TEXT, anchor="start", weight="400", size=FS) -> str:
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" xml:space="preserve">{esc(s)}</text>')


def _meter(x, y, label, frac, right_txt, width, idx) -> str:
    seg, gap = 3, 1
    n = int(width / (seg + gap))
    lit = round(max(0.0, min(1.0, frac)) * n)
    rects = []
    for k in range(lit):
        p = k / n
        col = GREEN if p < 0.55 else ACCENT if p < 0.85 else AMBER
        rects.append(f'<rect x="{x + 40 + k * (seg + gap)}" y="{y - 10}" width="{seg}" height="12" fill="{col}"/>')
    cid = f"m{idx}"
    full = n * (seg + gap)
    return (f'{_t(x, y, label, ACCENT, weight="700")}{_t(x + 30, y, "[", BRIGHT)}'
            f'<clipPath id="{cid}"><rect x="{x + 40}" y="{y - 12}" height="16" width="0">'
            f'<animate attributeName="width" from="0" to="{full}" dur=".9s" begin="{0.15 + idx * 0.06:.2f}s" '
            f'fill="freeze" calcMode="spline" keySplines=".2 .7 .3 1" keyTimes="0;1"/></rect></clipPath>'
            f'<g clip-path="url(#{cid})">{"".join(rects)}</g>'
            f'{_t(x + 44 + full, y, "]", BRIGHT)}{_t(x + 58 + full, y, right_txt, MUTED)}')


def _ago(iso: str) -> str:
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    d = (dt.datetime.now(dt.timezone.utc) - t).days
    return "today" if d < 1 else f"{d}d" if d < 14 else f"{d // 7}w" if d < 90 else f"{d // 30}mo"


def render(m: dict, stats: dict, prof: dict) -> str:
    wx, wy, ww, wh = 48, 48, 904, H - 96
    user = prof["user"]
    chrome, clip = window(wx, wy, ww, wh, f"htop — {user}@{prof['host']}", wid="hw")
    x, y0, lh = wx + 24, wy + 58, 19

    total = max(1, sum(m["weekday"]))
    peak = max(m["weekday"]) or 1
    names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    left = "".join(_meter(x, y0 + i * lh, names[i], m["weekday"][i] / peak,
                          f"{100 * m['weekday'][i] / total:4.1f}%", 280, i) for i in range(7))

    rx = wx + 470
    l1, l7, l30 = m["load"]
    right = [
        (f'<text x="{rx}" y="{y0}" font-family="{MONO}" font-size="{FS}" xml:space="preserve">'
         f'<tspan fill="{ACCENT}" font-weight="700">Tasks: </tspan><tspan fill="{BRIGHT}">{m["repo_count"]}</tspan>'
         f'<tspan fill="{TEXT}"> repos, </tspan><tspan fill="{BRIGHT}">{m["pr_count"]}</tspan>'
         f'<tspan fill="{TEXT}"> merged upstream; </tspan><tspan fill="{GREEN}">1 running</tspan></text>'),
        (f'<text x="{rx}" y="{y0 + lh}" font-family="{MONO}" font-size="{FS}" xml:space="preserve">'
         f'<tspan fill="{ACCENT}" font-weight="700">Load average: </tspan><tspan fill="{BRIGHT}">{l1:.2f} </tspan>'
         f'<tspan fill="{TEXT}">{l7:.2f} </tspan><tspan fill="{MUTED}">{l30:.2f}</tspan></text>'),
        (f'<text x="{rx}" y="{y0 + 2 * lh}" font-family="{MONO}" font-size="{FS}" xml:space="preserve">'
         f'<tspan fill="{ACCENT}" font-weight="700">Uptime: </tspan><tspan fill="{BRIGHT}">{m["streak"]} days</tspan>'
         f'<tspan fill="{MUTED}">  (commit streak · best {m["longest"]}d)</tspan></text>'),
    ]
    right.append(_meter(rx, y0 + 4 * lh, "Mem", m["active"] / max(1, m["span"]),
                        f"{m['active']}/{m['span']}d active", 200, 7))
    right.append(_meter(rx, y0 + 5 * lh, "Swp", m["week"] / max(25, m["week"]),
                        f"{m['week']} commits / 7d", 200, 8))
    best = m["best"]
    if best.get("date"):
        right.append(_t(rx, y0 + 6 * lh,
                        f"Peak: {best['count']} on {dt.date.fromisoformat(best['date']):%d %b %Y}", MUTED))

    # process table
    ty = y0 + 7 * lh + 18
    cols = [(x, "PID"), (x + 64, "USER"), (x + 150, "PRI"), (x + 196, "★"), (x + 236, "%CPU"),
            (x + 300, "LAST"), (x + 372, "Command")]
    head = (f'<rect x="{wx}" y="{ty - 14}" width="{ww}" height="19" fill="{ACCENT}" fill-opacity=".85"/>'
            + "".join(_t(cx, ty, n, BG, weight="700") for cx, n in cols))
    own = sorted([r for r in stats["repos"] if not r.get("fork")], key=lambda r: r["pushed"], reverse=True)
    forks = sorted([r for r in stats["repos"] if r.get("fork")], key=lambda r: r["pushed"], reverse=True)
    rows_src = (own + forks)[:4]
    csum = max(1, sum(r["commits"] for r in rows_src))
    rows = []
    for i, r in enumerate(rows_src):
        ry = ty + 20 + i * lh
        pid = 1000 + int(hashlib.md5(r["name"].encode()).hexdigest(), 16) % 9000
        sel = i == 0
        if sel:
            rows.append(f'<rect x="{wx}" y="{ry - 14}" width="{ww}" height="19" fill="{ACCENT}" fill-opacity=".14"/>')
        tag = " [fork]" if r.get("fork") else ""
        rows.append(_t(cols[0][0], ry, f"{pid}", MUTED) + _t(cols[1][0], ry, user[:8], TEXT)
                    + _t(cols[2][0], ry, "20", MUTED) + _t(cols[3][0], ry, str(r["stars"]), TEXT)
                    + _t(cols[4][0], ry, f"{100 * r['commits'] / csum:5.1f}", BRIGHT if sel else TEXT)
                    + _t(cols[5][0], ry, _ago(r["pushed"]), TEXT)
                    + f'<text x="{cols[6][0]}" y="{ry}" font-family="{MONO}" font-size="{FS}" xml:space="preserve">'
                      f'<tspan fill="{GREEN if not r.get("fork") else TEXT}">{esc(r["name"][:34])}</tspan>'
                      f'<tspan fill="{MUTED}">{tag}  {esc(r["lang"])}</tspan></text>')
    if not rows_src:
        rows.append(_t(x, ty + 20, "no processes yet — first build incoming", MUTED))

    fy = wy + wh - 6
    keys = [("F1", "About"), ("F2", "Projects"), ("F3", "Stack"), ("F4", "Connect"), ("F5", "Tree"),
            ("F10", "Quit")]
    fk, fx = [], wx + 10
    for k, v in keys:
        fk.append(_t(fx, fy, k, BRIGHT, weight="700"))
        fx += len(k) * 7.8 + 2
        fk.append(f'<rect x="{fx}" y="{fy - 12}" width="{len(v) * 7.8 + 8}" height="16" fill="{ACCENT}" fill-opacity=".22"/>')
        fk.append(_t(fx + 4, fy, v, TEXT))
        fx += len(v) * 7.8 + 18

    frame = hud_frame(W, H, tl="PROC // MONITOR", tr=f"LOAD {l1:.2f} {l7:.2f} {l30:.2f}",
                      bl="SRC: GITHUB CONTRIBUTION GRAPH", br="REFRESH 6H", tab="HTOP", trace=True, fid="hh")
    return svg_open(W, H, "htop-style activity monitor") + f"""
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
{frame}
{chrome}
<g clip-path="url(#{clip})">
{left}
{''.join(right)}
<line x1="{wx + 448}" y1="{y0 - 12}" x2="{wx + 448}" y2="{y0 + 6 * lh + 2}" stroke="{LINE2}" stroke-dasharray="2 3"/>
{head}
{''.join(rows)}
{''.join(fk)}
</g>
{scanlines(W, H)}
</svg>
"""
