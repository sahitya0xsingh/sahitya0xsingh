# How this profile works

The README is one neofetch-style card: an ASCII portrait on the left and system-style info on the right. It has a dark version and a light version, and GitHub shows the one that matches the visitor's theme.

| File | What it is | Made by | Refreshed |
|:--|:--|:--|:--|
| `data/ascii-dark.txt`, `data/ascii-light.txt` | the ASCII portrait | `scripts/ascii_art.py` from `assets/photo.jpg` (needs Pillow) | by hand, when the photo changes |
| `assets/neofetch-dark.svg`, `assets/neofetch-light.svg` | the card | `scripts/neofetch.py` | every 6 hours, by the `refresh profile` workflow |

## Updating

- **Info lines** (name, studying, tools, contact): edit `lines()` in `scripts/neofetch.py`.
- **GitHub stats:** these update by themselves.
- **New photo:** replace `assets/photo.jpg`, then run this locally and commit the two text files:

  ```bash
  pip install pillow && python scripts/ascii_art.py
  ```
