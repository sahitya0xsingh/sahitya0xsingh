"""Redraw the neofetch card (assets/neofetch-dark.svg and -light.svg) with live GitHub numbers.

    python scripts/generate.py          # needs GITHUB_TOKEN
"""
from __future__ import annotations

import metrics
import neofetch
from common import LOGIN


def main() -> None:
    from github_api import fetch_stats
    stats = fetch_stats(LOGIN)
    neofetch.write_all(stats, metrics.compute(stats))


if __name__ == "__main__":
    main()
