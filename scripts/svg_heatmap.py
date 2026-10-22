"""The contribution calendar, rendered inside a terminal with a slow scan beam."""
from __future__ import annotations

import datetime as dt

from common import (ACCENT, BG, BRIGHT, GREEN, LINE2, MONO, MUTED, RAMP, TEXT,
                    esc, svg_open)
from frame import hud_frame, scanlines, window

W, H = 1000, 320
CELL, STEP = 12, 15


def _levels(counts):
    nz = sorted(c for c in counts if c > 0)
    if not nz:
        return lambda c: 0
    q = [nz[max(0, int(len(nz) * f) - 1)] for f in (0.25, 0.5, 0.8)]
    return lambda c: 0 if c <= 0 else 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4


def render(m: dict, stats: dict, prof: dict) -> str:
    wx, wy, ww, wh = 48, 48, 904, H - 96
    chrome, clip = window(wx, wy, ww, wh, "git — activity", wid="gw")
    bx = wx + 24
    py = wy + 56
    prompt = (f'<text x="{bx}" y="{py}" font-family="{MONO}" font-size="13" xml:space="preserve">'
              f'<tspan fill="{GREEN}">{esc(prof["user"])}@{esc(prof["host"])}</tspan><tspan fill="{MUTED}">:</tspan>'
              f'<tspan fill="{ACCENT}">~</tspan><tspan fill="{MUTED}">$ </tspan>'
              f'<tspan fill="{BRIGHT}">git log --all --since="1 year" --author=@{esc(stats["login"])} | heatmap</tspan></text>')

    days = stats["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    first_sun = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    lvl = _levels([d["count"] for d in days])
    gx, gy = bx + 34, py + 30
    cells, months, last_month, ncols, last_label_col = [], [], None, 0, -9
    for i, d in enumerate(days):
        date = dt.date.fromisoformat(d["date"])
        col, row = (date - first_sun).days // 7, (date.weekday() + 1) % 7
        ncols = max(ncols, col + 1)
        x, y = gx + col * STEP, gy + row * STEP
        L = lvl(d["count"])
        today = i == len(days) - 1
        anim = ""
        if today:
            anim = (f'<animate attributeName="stroke-opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/>')
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{RAMP[L]}"'
                     f'{f" stroke={chr(34)}{BRIGHT}{chr(34)} stroke-width={chr(34)}1.2{chr(34)}" if today else ""}>'
                     f'<title>{date:%d %b %Y}: {d["count"]}</title>{anim}</rect>')
        if row == 0 and date.month != last_month:
            last_month = date.month
            if col < 51 and col - last_label_col >= 3:
                last_label_col = col
                months.append(f'<text x="{x}" y="{gy - 7}" font-family="{MONO}" font-size="10" '
                              f'fill="{MUTED}">{date:%b}</text>')
    labels = "".join(f'<text x="{bx}" y="{gy + r * STEP + 10}" font-family="{MONO}" font-size="10" '
                     f'fill="{MUTED}">{n}</text>' for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))

    gw, gh = ncols * STEP, 7 * STEP
    beam = (f'<g opacity=".55"><rect x="{gx - 30}" y="{gy - 4}" width="30" height="{gh + 4}" fill="url(#beam)"/>'
            f'<rect x="{gx - 1}" y="{gy - 4}" width="1.5" height="{gh + 4}" fill="{ACCENT}"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;{gw + 30} 0;{gw + 30} 0" '
            f'keyTimes="0;.7;1" dur="9s" repeatCount="indefinite"/></g>')

    best = m["best"]
    sy = gy + gh + 22
    best_txt = (f"{best['count']} on {dt.date.fromisoformat(best['date']):%d %b}" if best.get("date") else "—")
    summary = (f'<text x="{bx}" y="{sy}" font-family="{MONO}" font-size="12" xml:space="preserve">'
               f'<tspan fill="{BRIGHT}">{m["total"]}</tspan><tspan fill="{MUTED}"> contributions  ·  </tspan>'
               f'<tspan fill="{BRIGHT}">{m["active"]}</tspan><tspan fill="{MUTED}"> active days  ·  peak </tspan>'
               f'<tspan fill="{BRIGHT}">{esc(best_txt)}</tspan><tspan fill="{MUTED}">  ·  longest streak </tspan>'
               f'<tspan fill="{BRIGHT}">{m["longest"]}d</tspan></text>')
    legend_x = wx + ww - 24 - 5 * 15 - 70
    legend = (f'<text x="{legend_x}" y="{sy}" font-family="{MONO}" font-size="10" fill="{MUTED}">less</text>'
              + "".join(f'<rect x="{legend_x + 30 + i * 15}" y="{sy - 10}" width="12" height="12" rx="2" fill="{c}"/>'
                        for i, c in enumerate(RAMP))
              + f'<text x="{legend_x + 30 + 5 * 15 + 4}" y="{sy}" font-family="{MONO}" font-size="10" fill="{MUTED}">more</text>')

    frame = hud_frame(W, H, tl="LOG // 365D", tr=f"Σ {m['total']}", bl="SCAN 9S", br="LEVELS: QUARTILE",
                      tab="GIT LOG", trace=True, fid="ha")
    return svg_open(W, H, f"{m['total']} contributions in the last year") + f"""
<defs><linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="1" stop-color="{ACCENT}" stop-opacity=".35"/></linearGradient></defs>
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
{frame}
{chrome}
<g clip-path="url(#{clip})">
{prompt}
{''.join(months)}{labels}
{''.join(cells)}
{beam}
{summary}{legend}
<line x1="{wx}" y1="{sy - 14}" x2="{wx + ww}" y2="{sy - 14}" stroke="{LINE2}" stroke-dasharray="2 3" opacity=".6"/>
</g>
{scanlines(W, H)}
</svg>
"""
