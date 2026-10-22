"""Closing line: the session logs out."""
from __future__ import annotations

from common import ACCENT, BG, BRIGHT, GREEN, MONO, MUTED, esc, svg_open
from frame import hud_frame, scanlines

W, H = 1000, 120


def render(prof: dict) -> str:
    u = f"{prof['user']}@{prof['host']}"
    x, y = 56, 62
    frame = hud_frame(W, H, br="SESSION CLOSED · EXIT 0", tab="EOF", trace=True, c=16, fid="hf")
    return svg_open(W, H, "logout") + f"""
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
{frame}
<g font-family="{MONO}" font-size="13" xml:space="preserve">
  <text x="{x}" y="{y}"><tspan fill="{GREEN}">{esc(u)}</tspan><tspan fill="{MUTED}">:</tspan><tspan fill="{ACCENT}">~</tspan><tspan fill="{MUTED}">$ </tspan><tspan fill="{BRIGHT}">exit</tspan></text>
  <text x="{x}" y="{y + 20}" fill="{MUTED}">logout · thanks for reading. [Process completed]</text>
  <rect x="{x + 380}" y="{y + 9}" width="8" height="14" fill="{ACCENT}">
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" repeatCount="indefinite"/>
  </rect>
</g>
{scanlines(W, H)}
</svg>
"""
