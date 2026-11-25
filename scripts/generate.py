"""Refresh the live blocks in README.md (numbers and where my pull requests went).

    python scripts/generate.py          # live data (needs GITHUB_TOKEN)
"""
from __future__ import annotations

import metrics
import readme_sections
from common import LOGIN, profile


def main() -> None:
    from github_api import fetch_stats
    stats = fetch_stats(LOGIN)
    m = metrics.compute(stats)
    did = readme_sections.update(stats, m, profile().get("hide_repos", []))
    print(f"{'updated' if did else 'same   '}  README.md")


if __name__ == "__main__":
    main()
