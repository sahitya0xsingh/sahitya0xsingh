# Setup

Copy everything in this folder into the root of your `sahitya0xsingh/sahitya0xsingh` repository.

## Install

1. Replace your current `README.md` and `assets/` folder with the ones here (your old versions stay in git history).
2. Add `scripts/`, `data/` and `.github/workflows/refresh.yml`.
3. Delete the old Pac-Man workflow from `.github/workflows/`. You can delete the `output` branch afterwards too.
4. In the repo, go to **Settings → Actions → General → Workflow permissions**, choose **Read and write permissions**, and save.
5. Commit and push, then open **Actions → refresh profile → Run workflow** once.

The first run replaces the demo numbers in `assets/` with your real data and fills the `~/projects` and `~/oss` sections. After that it refreshes every 6 hours and only commits when something actually changed.

## Make it yours

- **Your logo** on the start screen: your panther logo is already included as `assets/logo.png`. If you delete it, the start screen uses your GitHub avatar instead. To use a different logo, commit a square image as `assets/logo.png` (or `.jpg`). High contrast works best: a light mark on a dark background, or the reverse (it auto-inverts so the mark glows). Pushing it re-renders automatically.

- **`data/profile.json`** controls the neofetch panel: name, role, stack, tools, focus, status, and the `user@host` shown in the prompt. Pushing a change re-renders automatically.
- **`~/about`** in `README.md` is the one hand-written paragraph. Rewrite it in your own words.

## Preview locally

```bash
python scripts/generate.py --demo
```

Then open the files in `assets/` in a browser. GitHub plays the same animations.

## How the data maps

| Panel | Shows |
|:--|:--|
| start screen | your logo rebuilt from the characters of this repo's own `scripts/*.py`, revealed by a laser scan, then ACCESS GRANTED |
| header · boot | CRT power-on, then a BIOS POST built from your stats, then `neofetch` |
| header · HEXDUMP rail | your last 120 days of contributions as hex bytes, scrolling |
| header · oscilloscope | commits per day over the last 120 days, traced live |
| header · SCAN radar | blips scale with how active your week was |
| neofetch · Uptime | current commit streak |
| neofetch · Packages | public repos and PRs merged into other people's repos |
| htop · weekday meters | share of the year's contributions made on each weekday |
| htop · Load average | average contributions per day over the last 1, 7 and 30 days |
| htop · Mem / Swp | active days out of 365 · contributions in the last 7 days |
| htop · process list | your most recently pushed repos, with %CPU as share of commits |
| activity | the contribution calendar, shaded by quartile |

## Files

| File | Job |
|:--|:--|
| `scripts/generate.py` | Entry point: renders every SVG and rewrites the README tables |
| `scripts/frame.py` | The chamfered HUD frame and terminal window chrome shared by all panels |
| `scripts/svg_splash.py` | start screen: code-glyph logo + identity scan |
| `scripts/logo.py` | loads `assets/logo.png` or your avatar and turns it into a brightness grid |
| `scripts/svg_terminal.py` | cyberdeck header: boot sequence, neofetch, rails |
| `scripts/svg_htop.py` | htop monitor |
| `scripts/svg_heatmap.py` | activity heatmap |
| `scripts/svg_footer.py` | logout line |
| `scripts/github_api.py` | one GraphQL query for all the data |

Plain Python standard library, plus Pillow for reading your logo (the workflow installs it; without it the start screen falls back to the 0x monogram).
