# How this profile works

The README is drawn as a set of engineering-blueprint sheets. Everything is plain SVG made by the scripts in `scripts/`. There are no third-party widgets.

| File | What it is | Made by | Refreshed |
|:--|:--|:--|:--|
| `assets/hero.svg` | Sheet 01: the plotted portrait and title block | `scripts/hero.py` (needs Pillow) | by hand, when the photo or details change |
| `assets/detail-*.svg` | Detail drawings: PreFlight, checkstyle, openSUSE, where my PRs went | `scripts/cards.py` | every 6 hours |
| `assets/record.svg` | Sheet 02: contributions per day as a strip chart | `scripts/cards.py` | every 6 hours |

`scripts/theme.py` holds the shared look: colours, grid, glow filters and the pen-drawing animation.

## Updating

- **Live cards:** the `refresh profile` workflow runs `scripts/generate.py` every 6 hours and commits only when something changed.
- **Header:** after changing `assets/photo.jpg` or the title block, run this locally and commit `assets/hero.svg`:

  ```bash
  pip install pillow && python scripts/hero.py
  ```

- **Text:** edit the bio in `README.md` by hand.
- **Hidden repos:** keep a repo out of the pull-request card with `hide_repos` in `data/profile.json`.
