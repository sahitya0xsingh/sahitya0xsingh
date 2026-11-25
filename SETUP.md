# How this profile works

`README.md` is plain text. Two blocks inside it are filled in from public GitHub data:

| Block | Shows |
|:--|:--|
| `STATS` | contributions this year, pull requests to other projects, best day, longest streak |
| `UPSTREAM` | the repos that received the most pull requests from me |

`scripts/generate.py` rewrites those blocks. The `refresh profile` workflow runs it every 6 hours and commits only when a number changed.

- Edit everything else in `README.md` by hand.
- Keep a repo out of the pull-request list with `hide_repos` in `data/profile.json`.

## Visuals

| Piece | Source |
|:--|:--|
| Wave header and footer | [capsule-render](https://github.com/kyechan99/capsule-render) |
| Typing line | [readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg) |
| 3D contribution graph | [github-profile-3d-contrib](https://github.com/yoshi389111/github-profile-3d-contrib), drawn daily by `profile visuals` |
| Snake | [Platane/snk](https://github.com/Platane/snk), drawn daily by `profile visuals` |
| Streak card | [github-readme-streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) |
| Activity graph | [github-readme-activity-graph](https://github.com/Ashutosh00710/github-readme-activity-graph) |
