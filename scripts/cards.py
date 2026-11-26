"""Blueprint detail cards and the record strip (standard library only, runs in the workflow).

detail-preflight.svg · detail-checkstyle.svg · detail-opensuse.svg · detail-upstream.svg · record.svg  →  assets/
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from theme import DIM, FAINT, INK, MONO, PAPER, PEN, SANS, appear, dim_h, draw_in, esc, label, sheet, svg

ROOT = Path(__file__).resolve().parent.parent
CW, CH = 440, 300


def head(tag: str, title: str, sub: str) -> str:
    return (label(30, 44, tag, 9.5, DIM, ls=2.4)
            + f'<text x="29" y="76" font-family="{SANS}" font-size="27" font-weight="800" fill="{INK}" letter-spacing="-.6" filter="url(#glowT)">{esc(title)}</text>'
            + label(30, 98, sub, 10.5, PEN, ls=.6))


def spec(x: float, y: float, rows: list[tuple[str, str]], w: float = 380) -> str:
    """A small spec table: label left, value right, dotted leader between."""
    out = ""
    for i, (k, v) in enumerate(rows):
        yy = y + i * 24
        out += (label(x, yy, k, 9.5, DIM, ls=1.4)
                + f'<line x1="{x + len(k) * 7.1 + 8:.0f}" y1="{yy - 3}" x2="{x + w - len(v) * 8.4 - 8:.0f}" y2="{yy - 3}" stroke="{FAINT}" stroke-dasharray="1 4"/>'
                + label(x + w, yy, v, 12.5, INK, "end", .4))
    return out


def box(x: float, y: float, w: float, h: float, title: str, sub: str, t: float) -> str:
    return draw_in(f"M{x},{y} H{x + w} V{y + h} H{x} Z", t, .6, INK, 1.3, int(2 * (w + h)) + 4) + appear(
        t + .4, f'<text x="{x + w / 2}" y="{y + h / 2 - 1}" text-anchor="middle" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{INK}">{title}</text>'
                + label(x + w / 2, y + h / 2 + 14, sub, 9, DIM, "middle", .6))


def preflight() -> str:
    body = head("DETAIL A · OWN PROJECT", "PreFlight", "CI before you push")
    body += (box(30, 124, 96, 50, "laptop", "git commit", .4) + box(172, 124, 96, 50, "PreFlight", "replays CI", .9)
             + box(314, 124, 96, 50, "GitHub", "green on push", 1.4)
             + draw_in("M126,149 H170", .8, .3, PEN, 1.6, 50, 'marker-end="url(#arr)"')
             + draw_in("M268,149 H312", 1.3, .3, PEN, 1.6, 50, 'marker-end="url(#arr)"')
             + appear(1.4, label(219, 194, "SAME DOCKER IMAGE · SAME JOBS", 8.5, DIM, "middle", 1)))
    body += appear(1.8, spec(30, 226, [("MATCH WITH GITHUB CI", "97.1%"), ("REAL PRS REPLAYED", "106"), ("FAILURES CAUGHT", "90 / 91")]))
    return svg(CW, CH, sheet(CW, CH, False) + body)


def checkstyle(n_core: int, n_contrib: int) -> str:
    body = head("DETAIL B · CONTRIBUTOR", "checkstyle", "Java static analysis")
    # a small drawing: source → checks → report
    body += (draw_in("M40,132 h46 l14,14 v44 h-60 Z M86,132 v14 h14", .4, .9, INK, 1.2, 300)
             + appear(.9, "".join(f'<line x1="50" y1="{156 + i * 8}" x2="{90 - (i % 2) * 14}" y2="{156 + i * 8}" stroke="{DIM}" stroke-width="1.4"/>' for i in range(4)))
             + draw_in("M110,160 H160", 1.1, .3, PEN, 1.6, 60, 'marker-end="url(#arr)"')
             + appear(1.3, "".join(label(176, 142 + i * 18, t, 10.5, INK, ls=.4) for i, t in
                                   enumerate(["✓ naming", "✓ imports", "✗ whitespace", "✓ javadoc"])))
             + appear(1.3, f'<ellipse cx="216" cy="173" rx="52" ry="11" fill="none" stroke="{PEN}" stroke-width="1.3"/>'
                      + label(276, 177, "← what I fix", 9.5, PEN, ls=.3)))
    body += appear(1.8, spec(30, 226, [("PULL REQUESTS · CORE", str(n_core)), ("REGRESSION TOOLING", str(n_contrib)),
                                       ("ALSO", "OpenRewrite recipes")]))
    return svg(CW, CH, sheet(CW, CH, False) + body)


def opensuse() -> str:
    body = head("DETAIL C · COMMUNITY", "openSUSE", "member since 2026")
    # route: Bengaluru → Yogyakarta, a dashed great-circle-ish arc
    ax, ay, bx, by = 70, 190, 360, 176
    body += (appear(.3, f'<circle cx="{ax}" cy="{ay}" r="4.5" fill="{INK}" filter="url(#glow)"/>' + label(ax, ay + 22, "BENGALURU", 9.5, DIM, "middle", 1.2)
                    + label(ax, ay + 35, "12.97 N  77.59 E", 8, FAINT, "middle", .3))
             + f'<mask id="arcm" maskUnits="userSpaceOnUse" x="0" y="0" width="{CW}" height="{CH}">'
             + draw_in(f"M{ax},{ay} Q{(ax + bx) / 2},{ay - 110} {bx},{by}", .6, 1.3, "#fff", 8)
             + f'</mask><path d="M{ax},{ay} Q{(ax + bx) / 2},{ay - 110} {bx},{by}" fill="none" stroke="{PEN}" stroke-width="1.6" '
               f'stroke-dasharray="6 5" mask="url(#arcm)" filter="url(#glowY)"/>'
             + appear(1.8, f'<circle cx="{bx}" cy="{by}" r="4.5" fill="{PEN}" filter="url(#glowY)"/><circle cx="{bx}" cy="{by}" r="10" fill="none" stroke="{PEN}" filter="url(#glowY)"><animate attributeName="r" values="8;15;8" dur="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.2;1" dur="2.4s" repeatCount="indefinite"/></circle>'
                      + label(bx, by + 24, "YOGYAKARTA", 9.5, DIM, "middle", 1.2) + label(bx, by + 37, "7.80 S  110.36 E", 8, FAINT, "middle", .3)
                      + label(215, 214, "openSUSE.Asia Summit 2026", 10.5, INK, "middle", .3)))
    body += appear(2.1, spec(30, 262, [("ROLE", "invited participant")]))
    return svg(CW, CH, sheet(CW, CH, False) + body)


def upstream(rows: list[tuple[str, int]]) -> str:
    body = head("DETAIL D · UPSTREAM", "Where my PRs went", f"{sum(c for _, c in rows)} pull requests, {len(rows)} repositories")
    top = max((c for _, c in rows), default=1)
    for i, (repo, c) in enumerate(rows[:6]):
        y = 130 + i * 25
        name = repo if len(repo) <= 30 else repo[:29] + "…"
        w = max(3, 92 * c / top)
        body += appear(.3 + i * .12, label(30, y + 4, name, 10, INK, ls=.1)
                       + f'<line x1="290" y1="{y}" x2="{290 + w:.0f}" y2="{y}" stroke="{PEN if i == 0 else INK}" stroke-width="7" filter="url(#{"glowY" if i == 0 else "glow"})"/>'
                       + label(410, y + 4, str(c), 11, INK, "end", .2))
    return svg(CW, CH, sheet(CW, CH, False) + body)


def record(m: dict, days: list[dict]) -> str:
    W, H = 1000, 400
    days = days[-365:]
    x0, x1, y0, ch = 60, 700, 330, 190
    top = max((d["count"] for d in days), default=1) or 1
    n = len(days)
    pts = [(x0 + i * (x1 - x0) / max(1, n - 1), y0 - (d["count"] / top) ** .6 * ch) for i, d in enumerate(days)]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    # longest streak span
    best_i = max(range(n), key=lambda i: days[i]["count"]) if n else 0
    run, s0, bs, be = 0, 0, 0, 0
    for i, d in enumerate(days):
        if d["count"]:
            if run == 0:
                s0 = i
            run += 1
            if run > be - bs:
                bs, be = s0, i + 1
        else:
            run = 0
    grid = "".join(f'<line x1="{x0}" y1="{y0 - k * ch / 4:.0f}" x2="{x1}" y2="{y0 - k * ch / 4:.0f}" stroke="{FAINT}" stroke-dasharray="2 4" stroke-width=".7"/>' for k in range(1, 5))
    months, last = "", None
    for i, d in enumerate(days):
        mo = d["date"][:7]
        if mo != last:
            last = mo
            if i == 0 and dt.date.fromisoformat(d["date"]).day > 20:
                continue
            x = x0 + i * (x1 - x0) / max(1, n - 1)
            months += (f'<line x1="{x:.0f}" y1="{y0}" x2="{x:.0f}" y2="{y0 + 6}" stroke="{DIM}"/>'
                       + label(x + 3, y0 + 18, dt.date.fromisoformat(d["date"]).strftime("%b").upper(), 8, DIM, ls=1))
    bx, by = pts[best_i]
    day = dt.date.fromisoformat(days[best_i]["date"]).strftime("%-d %b") if n else ""
    sx0, sx1 = pts[bs][0] if n else x0, pts[max(bs, be - 1)][0] if n else x0
    markup = (draw_in(f"M{bx - 16:.0f},{by - 6:.0f} a16,14 0 1,0 32,0 a16,14 0 1,0 -32,0", 3.6, .5, PEN, 1.5, 120)
              + appear(3.9, f'<path d="M{bx + 18:.0f},{by - 8:.0f} L{bx + 60:.0f},{by - 26:.0f}" stroke="{PEN}" stroke-width="1.2"/>'
                       + label(bx + 64, by - 23, f"{days[best_i]['count'] if n else 0} in one day, {day}", 11, PEN, ls=.3))
              + appear(4.2, f'<path d="M{sx0:.0f},{y0 + 30} v-6 H{sx1:.0f} v6" fill="none" stroke="{PEN}" stroke-width="1.3"/>'
                       + label((sx0 + sx1) / 2, y0 + 44, f"{m['longest']} days in a row", 10, PEN, "middle", .3)))
    pen = (f'<circle r="4" fill="{PEN}" filter="url(#glowY)"><animateMotion dur="3s" begin=".5s" fill="freeze" path="{path}"/>'
           f'<set attributeName="opacity" to="0" begin="3.6s" fill="freeze"/></circle>')
    title = (label(40, 52, "SHEET 02 · THE RECORD", 10.5, DIM, ls=3)
             + f'<text x="39" y="88" font-family="{SANS}" font-size="30" font-weight="800" fill="{INK}" letter-spacing="-.6" filter="url(#glowT)">Twelve months, one pen</text>'
             + label(40, 112, "contributions per day, plotted on a strip chart", 10.5, DIM, ls=.4))
    tx = 748
    side = (f'<rect x="{tx}" y="132" width="212" height="210" fill="{PAPER}" stroke="{INK}" stroke-width="1.2" filter="url(#glow)"/>'
            + "".join(f'<line x1="{tx}" y1="{132 + k * 52.5:.0f}" x2="{tx + 212}" y2="{132 + k * 52.5:.0f}" stroke="{DIM}" stroke-width=".8"/>' for k in range(1, 4))
            + "".join(label(tx + 12, 150 + k * 52.5, a, 8.5, DIM, ls=1.5)
                      + f'<text x="{tx + 12}" y="{175 + k * 52.5:.0f}" font-family="{SANS}" font-size="22" font-weight="800" fill="{PEN if k == 0 else INK}" filter="url(#glowT)">{b}</text>'
                      for k, (a, b) in enumerate([("CONTRIBUTIONS", m["total"]), ("PULL REQUESTS", m["pr_count"]),
                                                  ("ACTIVE DAYS", m["active"]), ("LONGEST STREAK", f"{m['longest']} days")])))
    chart = (grid + f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{INK}" stroke-width="1.2"/>'
             f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 - ch - 6}" stroke="{INK}" stroke-width="1.2"/>' + months
             + draw_in(path, .5, 3, INK, 1.4, 6000) + pen + markup)
    return svg(W, H, sheet(W, H) + title + chart + appear(.3, side))


def write_all(stats: dict, m: dict, hide: list[str]) -> None:
    from common import LOGIN
    out = ROOT / "assets"
    out.mkdir(exist_ok=True)
    pr = dict(stats.get("pr_repos", []))
    rows = [(r, c) for r, c in stats.get("pr_repos", []) if r not in hide and not r.startswith(LOGIN + "/")][:6]
    files = {"detail-preflight.svg": preflight(),
             "detail-checkstyle.svg": checkstyle(pr.get("checkstyle/checkstyle", 0), pr.get("checkstyle/contribution", 0)),
             "detail-opensuse.svg": opensuse(), "detail-upstream.svg": upstream(rows), "record.svg": record(m, stats["days"])}
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8")
        print("wrote  assets/" + name)
