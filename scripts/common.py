"""Shared theme, helpers and data plumbing for the terminal profile.

Python standard library only: the GitHub Actions runner needs no installs.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
README = ROOT / "README.md"

LOGIN = os.environ.get("PROFILE_LOGIN", "sahitya0xsingh")
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

# ── Palette: restrained, GitHub-dark compatible, one accent ────────────────
BG = "#0a0d12"
WIN = "#0d1117"
BAR = "#11161d"
LINE = "#21262d"
LINE2 = "#30363d"
TEXT = "#c9d1d9"
BRIGHT = "#f0f6fc"
MUTED = "#6e7681"
ACCENT = "#58A6FF"
ACCENT_DIM = "#1f6feb"
GREEN = "#3fb950"
AMBER = "#d29922"
RAMP = ["#161b22", "#0d2f57", "#124a85", "#1f6feb", "#58a6ff"]

MONO = ("ui-monospace, 'SFMono-Regular', 'JetBrains Mono', 'Cascadia Code', Menlo, "
        "Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace")

DEFAULT_PROFILE = {
    "user": "sahitya",
    "host": "0x",
    "name": "Sahitya Singh",
    "role": "Developer · open-source contributor",
    "stack": "Python · Java · JavaScript · React",
    "tools": "Git · Docker · HTML/CSS",
    "focus": "open source · web · ML explainability",
    "status": "open to collaborate",
    "title": "Student",
    "os": "macOS, Linux",
    "uptime": "Always Learning",
    "host_machine": "Developer Machine",
    "kernel": "Open Source",
    "ide": "VS Code",
    "lang_code": "Python, Java, JavaScript",
    "lang_web": "HTML, CSS, Markdown",
    "lang_real": "English, Hindi",
    "hobbies": "Web Development",
    "focus_short": "Open Source",
    "hardware": "Tech Exploring",
    "loc": "25K+",
    "linkedin": "sahitya-singh",
    "linkedin_full": "sahitya-singh-7012b137b",
}


def now_ist() -> dt.datetime:
    override = os.environ.get("PROFILE_NOW")  # e.g. 2026-10-23T02:00, for previews
    if override:
        return dt.datetime.fromisoformat(override).replace(tzinfo=IST)
    return dt.datetime.now(IST)


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def svg_open(w: int, h: int, label: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">\n'
            f'<title>{esc(label)}</title>\n')


def glow(fid: str, std: float = 2.0) -> str:
    # userSpaceOnUse so perfectly horizontal/vertical strokes still render
    return (f'<filter id="{fid}" filterUnits="userSpaceOnUse" x="-50%" y="-50%" width="200%" height="200%">'
            f'<feGaussianBlur stdDeviation="{std}" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def write_asset(name: str, content: str) -> bool:
    """Write only when content changed, so quiet days produce no commit."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    p = ASSETS / name
    if p.exists() and p.read_text(encoding="utf-8") == content:
        return False
    p.write_text(content, encoding="utf-8")
    return True


def load_json(name: str, default):
    p = DATA / name
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def profile() -> dict:
    return {**DEFAULT_PROFILE, **load_json("profile.json", {})}


def demo_stats(seed: int = 7) -> dict:
    """Plausible fake data for previewing before the first Action run."""
    rnd = random.Random(seed)
    today = now_ist().date()
    start = today - dt.timedelta(days=364)
    days, d = [], start
    while d <= today:
        busy = 0.30 + 0.40 * (d > today - dt.timedelta(days=120)) - 0.15 * (d.weekday() >= 5)
        c = 0 if rnd.random() > busy else int(rnd.expovariate(0.4)) + 1
        days.append({"date": d.isoformat(), "count": c})
        d += dt.timedelta(days=1)
    for i in range(1, 9):
        days[-i]["count"] = max(days[-i]["count"], rnd.randint(1, 5))
    repos = [
        {"name": "sahitya0xsingh", "url": "#", "desc": "profile", "stars": 1, "lang": "Python",
         "commits": 64, "pushed": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat(), "fork": False},
        {"name": "shap", "url": "#", "desc": "", "stars": 0, "lang": "Jupyter Notebook",
         "commits": 3, "pushed": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=20)).isoformat(), "fork": True},
        {"name": "story-spark-ai", "url": "#", "desc": "", "stars": 0, "lang": "TypeScript",
         "commits": 5, "pushed": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=41)).isoformat(), "fork": True},
        {"name": "python-mini-project", "url": "#", "desc": "", "stars": 0, "lang": "JavaScript",
         "commits": 2, "pushed": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=75)).isoformat(), "fork": True},
    ]
    return {"login": LOGIN, "days": days, "total": sum(x["count"] for x in days),
            "repos": repos, "prs": [], "pr_count": 2, "repo_count": 18, "followers": 7,
            "demo": True}
