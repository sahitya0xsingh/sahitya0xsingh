# How this profile works

`README.md` is plain text. Two blocks inside it are filled in from public GitHub data:

| Block | Shows |
|:--|:--|
| `STATS` | contributions this year, pull requests to other projects, best day, longest streak |
| `UPSTREAM` | the repos that received the most pull requests from me |

`scripts/generate.py` rewrites those blocks. The `refresh profile` workflow runs it every 6 hours and commits only when a number changed.

- Edit everything else in `README.md` by hand.
- Keep a repo out of the pull-request list with `hide_repos` in `data/profile.json`.
