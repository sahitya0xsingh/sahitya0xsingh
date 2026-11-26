"""The profile card: an ASCII portrait beside neofetch-style system info, in dark and light versions.

Standard library only (the portrait comes from data/ascii-*.txt, made once by scripts/ascii_art.py).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MONO = "ConsolasFallback, Consolas, 'SF Mono', Menlo, 'DejaVu Sans Mono', 'Liberation Mono', monospace"
W, H, FS, LH = 985, 530, 16, 20
X_INFO, COLS = 470, 51

THEMES = {
    "dark": {"bg": "#161b22", "text": "#c9d1d9", "key": "#ffa657", "value": "#a5d6ff", "dots": "#616e7f", "add": "#3fb950", "del": "#f85149"},
    "light": {"bg": "#f6f8fa", "text": "#24292f", "key": "#953800", "value": "#0a3069", "dots": "#c2cfde", "add": "#1a7f37", "del": "#cf222e"},
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def row(key: str, value: str, width: int = COLS) -> list[tuple[str, str]]:
    """'. Key: ........ value' padded to a fixed width."""
    dots = max(1, width - len(key) - len(value) - 5)
    return [(". ", "text"), (key, "key"), (":", "text"), (" " + "." * dots + " ", "dots"), (value, "value")]


def pair(k1: str, v1: str, k2: str, v2: str) -> list[tuple[str, str]]:
    left, right = 25, COLS - 25 - 3
    return row(k1, v1, left) + [(" | ", "text")] + row(k2, v2, right)[1:]


def rule(title: str) -> list[tuple[str, str]]:
    return [("- ", "text"), (title, "text"), (" " + "-" * (COLS - len(title) - 3), "text")]


def lines(stats: dict, m: dict) -> list[list[tuple[str, str]]]:
    best = m["best"]
    repos = len(stats.get("pr_repos", []))
    return [
        [("sahitya", "key"), ("@", "text"), ("bengaluru", "key"), (" " + "-" * (COLS - 18), "text")],
        row("Name", "Sahitya Singh"),
        row("Studying", "CS @ Newton School of Technology"),
        row("Community", "openSUSE member"),
        row("Contributing", "checkstyle, contribution"),
        row("Building", "PreFlight"),
        row("Motto", "ship small, ship often"),
        [],
        row("Languages.Programming", "Java, Python, JavaScript"),
        row("Languages.Web", "HTML, CSS, React"),
        row("Tools", "Git, Docker, GitHub Actions"),
        row("Events", "openSUSE.Asia Summit 2026"),
        [],
        rule("Contact"),
        row("Email", "sahityasingh508002@gmail.com"),
        row("LinkedIn", "sahityasingh08"),
        row("GitHub", "sahityasingh08"),
        [],
        rule("GitHub Stats"),
        pair("Contributions", str(m["total"]), "Pull Requests", str(m["pr_count"])),
        pair("Longest streak", f"{m['longest']}d", "Best day", f"{best['count']}"),
        pair("Active days", str(m["active"]), "Repos PR'd to", str(repos)),
    ]


def render(theme: str, stats: dict, m: dict) -> str:
    c = THEMES[theme]
    art = (ROOT / f"data/ascii-{theme}.txt").read_text(encoding="utf-8").rstrip("\n").split("\n")
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" font-family="{MONO}" width="{W}px" height="{H}px" font-size="{FS}px">',
           f'<style>.k{{fill:{c["key"]}}}.v{{fill:{c["value"]}}}.d{{fill:{c["dots"]}}}text,tspan{{white-space:pre}}</style>',
           f'<rect width="{W}px" height="{H}px" fill="{c["bg"]}" rx="15"/>']
    # the portrait uses a smaller grid than the info text, for more detail; each line is pinned to an exact width
    afs, alh, aw = 13.2, 16.8, 420
    for i, line in enumerate(art):
        out.append(f'<text x="18" y="{27 + i * alh:.1f}" fill="{c["text"]}" font-size="{afs}px" '
                   f'textLength="{aw * len(line) / max(len(x) for x in art):.0f}" lengthAdjust="spacingAndGlyphs">{esc(line)}</text>')
    out.append(f'<text x="{X_INFO}" y="30" fill="{c["text"]}">')
    cls = {"key": "k", "value": "v", "dots": "d", "text": ""}
    for i, parts in enumerate(lines(stats, m)):
        spans = "".join(f'<tspan class="{cls[k]}">{esc(t)}</tspan>' if cls[k] else f'<tspan>{esc(t)}</tspan>' for t, k in parts)
        out.append(f'<tspan x="{X_INFO}" y="{30 + i * LH}">{spans}</tspan>')
    out.append('</text></svg>\n')
    return "\n".join(out)


def write_all(stats: dict, m: dict, hide: list[str] | None = None) -> None:
    for theme in THEMES:
        p = ROOT / f"assets/neofetch-{theme}.svg"
        p.write_text(render(theme, stats, m), encoding="utf-8")
        print("wrote  " + str(p.relative_to(ROOT)))
