"""Rewrite the auto-generated blocks inside README.md between marker comments."""
from __future__ import annotations

import datetime as dt
import re

from common import LOGIN, README


def clean(s: str, n: int = 70) -> str:
    """Make outside text (PR titles, descriptions) safe inside a markdown table."""
    s = re.sub(r"[\r\n\t|<>`\[\]]", " ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _ago(iso: str) -> str:
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    d = (dt.datetime.now(dt.timezone.utc) - t).days
    return "today" if d < 1 else f"{d}d ago" if d < 14 else f"{d // 7}w ago" if d < 90 else f"{d // 30}mo ago"


def projects(repos: list[dict]) -> str:
    own = [r for r in repos if not r.get("fork") and r["name"].lower() != LOGIN.lower()]
    if not own:
        return "<sub>`ls: no original projects published yet. this list fills itself when one ships.`</sub>"
    rows = ["| project | lang | ★ | commits | last push |", "|:--|:--|:--:|:--:|:--|"]
    for r in own[:6]:
        desc = f"<br><sub>{clean(r['desc'], 90)}</sub>" if r.get("desc") else ""
        rows.append(f"| [`{clean(r['name'], 40)}`]({r['url']}){desc} | {clean(r['lang'], 20)} | "
                    f"{r['stars']} | {r['commits']:,} | {_ago(r['pushed'])} |")
    return "\n".join(rows)


def contributions(prs: list[dict]) -> str:
    if not prs:
        return "<sub>`git log: merged upstream pull requests will appear here automatically.`</sub>"
    rows = ["| repository | pull request | merged |", "|:--|:--|:--|"]
    for p in prs[:8]:
        when = dt.datetime.fromisoformat(p["merged"].replace("Z", "+00:00")).strftime("%d %b %Y")
        rows.append(f"| `{clean(p['repo'], 45)}` | [{clean(p['title'], 72)}]({p['url']}) | {when} |")
    return "\n".join(rows)


def replace_block(text: str, name: str, body: str) -> str:
    pat = re.compile(rf"(<!-- {name}:START -->)(.*?)(<!-- {name}:END -->)", re.S)
    return pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text)


def stats_line(m: dict) -> str:
    """One quiet line of live numbers for the text-first README."""
    best = m["best"]
    day = dt.date.fromisoformat(best["date"]).strftime("%-d %b") if best.get("date") else ""
    return (f"<sub>**{m['total']}** contributions this year &nbsp;·&nbsp; **{m['pr_count']}** pull requests to other projects"
            f" &nbsp;·&nbsp; best day **{best['count']}** ({day}) &nbsp;·&nbsp; longest streak **{m['longest']} days**</sub>")


def upstream(stats: dict, hide: list[str], n: int = 6) -> str:
    """Where my pull requests went, most first."""
    rows = [(r, c) for r, c in stats.get("pr_repos", []) if r not in hide and not r.startswith(LOGIN + "/")][:n]
    return "\n".join(f"- [`{r}`](https://github.com/{r}/pulls?q=is%3Apr+author%3A{LOGIN}) &nbsp;{c} PRs" for r, c in rows)


def update(stats: dict, m: dict | None = None, hide: list[str] | None = None) -> bool:
    if stats.get("demo"):
        return False
    text = README.read_text(encoding="utf-8")
    new = replace_block(text, "PROJECTS", projects(stats["repos"]))
    new = replace_block(new, "CONTRIBUTIONS", contributions(stats["prs"]))
    if m is not None:
        new = replace_block(new, "STATS", stats_line(m))
    new = replace_block(new, "UPSTREAM", upstream(stats, hide or []))
    if new != text:
        README.write_text(new, encoding="utf-8")
        return True
    return False
