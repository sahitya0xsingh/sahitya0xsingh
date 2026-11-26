"""Redraw the live cards in assets/ (detail cards and the record strip).

    python scripts/generate.py          # live data (needs GITHUB_TOKEN)
"""
from __future__ import annotations

import cards
import metrics
from common import LOGIN, profile


def main() -> None:
    from github_api import fetch_stats
    stats = fetch_stats(LOGIN)
    cards.write_all(stats, metrics.compute(stats), profile().get("hide_repos", []))


if __name__ == "__main__":
    main()
