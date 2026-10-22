"""Derived numbers from the contribution calendar."""
from __future__ import annotations

import datetime as dt


def compute(stats: dict) -> dict:
    days = stats["days"]
    counts = [d["count"] for d in days]
    streak, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today isn't over; don't break the streak yet
        i -= 1
    while i >= 0 and counts[i] > 0:
        streak += 1
        i -= 1
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c else 0
        longest = max(longest, cur)
    best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}
    weekday = [0] * 7  # Sun..Sat
    for d in days:
        weekday[(dt.date.fromisoformat(d["date"]).weekday() + 1) % 7] += d["count"]

    def avg(n):
        part = counts[-n:]
        return sum(part) / max(1, len(part))

    own = [r for r in stats["repos"] if not r.get("fork")]
    return {
        "today": counts[-1] if counts else 0,
        "week": sum(counts[-7:]),
        "streak": streak,
        "longest": longest,
        "active": sum(1 for c in counts if c),
        "span": len(counts),
        "total": stats["total"],
        "best": best,
        "weekday": weekday,
        "load": (avg(1), avg(7), avg(30)),
        "own_repos": len(own),
        "repo_count": stats.get("repo_count", len(stats["repos"])),
        "pr_count": stats.get("pr_count", len(stats["prs"])),
        "followers": stats.get("followers", 0),
    }
