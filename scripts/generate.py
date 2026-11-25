"""Regenerate every asset and auto-section of the profile.

    python scripts/generate.py          # live data (needs GITHUB_TOKEN)
    python scripts/generate.py --demo   # fake data, for previewing locally
"""
from __future__ import annotations

import sys

import metrics
import readme_sections
import svg_heatmap
import svg_splash
import svg_stack
from common import LOGIN, demo_stats, load_json, profile, write_asset


def main() -> None:
    if "--demo" in sys.argv:
        stats = demo_stats()
    else:
        from github_api import fetch_stats
        stats = fetch_stats(LOGIN)
    m = metrics.compute(stats)
    prof = profile()

    changed = {
        "start.svg": write_asset("start.svg", svg_splash.render(m, prof, stats)),
        "activity.svg": write_asset("activity.svg", svg_heatmap.render(m, stats, prof)),
        "stack.svg": write_asset("stack.svg", svg_stack.stack(prof, load_json("stack.json", svg_stack.DEFAULT_STACK))),
        "README.md": readme_sections.update(stats),
    }
    for name, did in changed.items():
        print(f"{'updated' if did else 'same   '}  {name}")


if __name__ == "__main__":
    main()
