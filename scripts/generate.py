"""Regenerate the profile cards and the auto-updated README sections.

    python scripts/generate.py          # live data (needs GITHUB_TOKEN)
    python scripts/generate.py --demo   # fake data, for previewing locally
"""
from __future__ import annotations

import sys

import metrics
import readme_sections
import term
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
        "hero.svg": write_asset("hero.svg", term.hero(m, prof, stats)),
        "orbit.svg": write_asset("orbit.svg", term.orbit(m, stats, prof)),
        "records.svg": write_asset("records.svg", term.records(m, stats, prof)),
        "skyline.svg": write_asset("skyline.svg", term.skyline(m, stats, prof)),
        "divider.svg": write_asset("divider.svg", term.divider()),
        **{f"project-{p['slug']}.svg": write_asset(f"project-{p['slug']}.svg", term.project(p))
           for p in load_json("projects.json", [])},
        "README.md": readme_sections.update(stats),
    }
    for name, did in changed.items():
        print(f"{'updated' if did else 'same   '}  {name}")


if __name__ == "__main__":
    main()
