"""Tech stack as a package-manager install log, plus the connect banner."""
from __future__ import annotations

from common import (ACCENT, BG, BRIGHT, GREEN, LINE2, MONO, MUTED, TEXT, esc,
                    svg_open)
from frame import hud_frame, scanlines, window

DEFAULT_STACK = [
    {"group": "LANGUAGES", "items": [["Python", "#3776AB"], ["Java", "#E76F00"], ["JavaScript", "#F7DF1E"]]},
    {"group": "WEB", "items": [["HTML5", "#E34F26"], ["CSS3", "#1572B6"], ["React", "#61DAFB"]]},
    {"group": "TOOLING", "items": [["Git", "#F05032"], ["Docker", "#2496ED"], ["VS Code", "#3fa0f0"]]},
    {"group": "PLATFORMS", "items": [["macOS", "#c9d1d9"], ["Linux", "#FCC624"], ["GitHub", "#f0f6fc"]]},
]


def stack(prof: dict, groups: list[dict]) -> str:
    W, H = 1000, 360
    wx, wy, ww, wh = 48, 48, 904, H - 96
    chrome, clip = window(wx, wy, ww, wh, "pkg — installed", wid="sk")
    bx, py = wx + 24, wy + 54
    u = f"{prof['user']}@{prof['host']}"
    prompt = (f'<text x="{bx}" y="{py}" font-family="{MONO}" font-size="13" xml:space="preserve">'
              f'<tspan fill="{GREEN}">{esc(u)}</tspan><tspan fill="{MUTED}">:</tspan><tspan fill="{ACCENT}">~</tspan>'
              f'<tspan fill="{MUTED}">$ </tspan><tspan fill="{BRIGHT}">pkg list --installed --group</tspan></text>')

    cols = len(groups)
    cw = (ww - 48) / cols
    body, n = [], 0
    total = sum(len(g["items"]) for g in groups)
    for gi, g in enumerate(groups):
        gx = bx + gi * cw
        body.append(f'<text x="{gx}" y="{py + 34}" font-family="{MONO}" font-size="9" font-weight="700" '
                    f'fill="{MUTED}" letter-spacing="2.5">{esc(g["group"])}</text>'
                    f'<line x1="{gx}" y1="{py + 42}" x2="{gx + cw - 22}" y2="{py + 42}" stroke="{LINE2}"/>')
        for ii, (name, color) in enumerate(g["items"]):
            y = py + 56 + ii * 40
            t = 0.3 + n * 0.11
            n += 1
            chip_w = cw - 22
            body.append(
                f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
                f'<rect x="{gx}" y="{y}" width="{chip_w:.0f}" height="30" rx="6" fill="#0f141b" stroke="{LINE2}"/>'
                f'<rect x="{gx}" y="{y}" width="3" height="30" rx="1.5" fill="{color}"/>'
                f'<circle cx="{gx + 18}" cy="{y + 15}" r="5" fill="{color}" opacity=".9"/>'
                f'<circle cx="{gx + 18}" cy="{y + 15}" r="9" fill="{color}" opacity=".15">'
                f'<animate attributeName="r" values="6;10;6" dur="2.4s" begin="{t:.2f}s" repeatCount="indefinite"/></circle>'
                f'<text x="{gx + 32}" y="{y + 19}" font-family="{MONO}" font-size="12.5" font-weight="700" '
                f'fill="{BRIGHT}">{esc(name)}</text>'
                f'<text x="{gx + chip_w - 10:.0f}" y="{y + 19}" text-anchor="end" font-family="{MONO}" font-size="10" '
                f'fill="{GREEN}">✓</text></g>')
    done_t = 0.3 + n * 0.11 + 0.2
    by = py + 56 + 3 * 40 + 12
    bar_w = 260
    footer = (f'<rect x="{bx}" y="{by - 9}" width="{bar_w}" height="8" fill="none" stroke="{LINE2}"/>'
              f'<rect x="{bx + 2}" y="{by - 7}" width="0" height="4" fill="{ACCENT}">'
              f'<animate attributeName="width" from="0" to="{bar_w - 4}" begin=".3s" dur="{done_t - .3:.2f}s" fill="freeze"/></rect>'
              f'<g opacity="0"><set attributeName="opacity" to="1" begin="{done_t:.2f}s" fill="freeze"/>'
              f'<text x="{bx + bar_w + 14}" y="{by}" font-family="{MONO}" font-size="11" fill="{TEXT}" xml:space="preserve">'
              f'{total}/{total} packages installed  <tspan fill="{GREEN}">· all systems nominal</tspan></text></g>')

    frame = hud_frame(W, H, tl="PKG // MANIFEST", tr=f"{total} INSTALLED", bl="ALWAYS LEARNING",
                      br="NEXT: WHATEVER'S INTERESTING", tab="TECH STACK", trace=True, fid="st")
    return svg_open(W, H, "Tech stack") + f"""
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
{frame}
{chrome}
<g clip-path="url(#{clip})">
{prompt}
{''.join(body)}
{footer}
</g>
{scanlines(W, H)}
</svg>
"""


def connect(prof: dict, login: str) -> str:
    W, H = 1000, 190
    wx, wy, ww, wh = 48, 48, 904, H - 96
    chrome, clip = window(wx, wy, ww, wh, "ssh — open channels", wid="cn")
    bx, py = wx + 24, wy + 54
    u = f"{prof['user']}@{prof['host']}"
    lines = [
        (f'<tspan fill="{GREEN}">{esc(u)}</tspan><tspan fill="{MUTED}">:</tspan><tspan fill="{ACCENT}">~</tspan>'
         f'<tspan fill="{MUTED}">$ </tspan><tspan fill="{BRIGHT}">ssh connect --list</tspan>'),
        (f'<tspan fill="{GREEN}">●</tspan><tspan fill="{ACCENT}" font-weight="700">  linkedin </tspan>'
         f'<tspan fill="{MUTED}"> →  </tspan><tspan fill="{TEXT}">in/{esc(prof["linkedin_full"])}</tspan>'
         f'<tspan fill="{GREEN}" font-weight="700">     github </tspan><tspan fill="{MUTED}"> →  </tspan>'
         f'<tspan fill="{TEXT}">@{esc(login)}</tspan>'),
    ]
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{bx}" y="{py + i * 24}" font-family="{MONO}" font-size="13" xml:space="preserve" '
                   f'opacity="0">{ln}<set attributeName="opacity" to="1" begin="{.3 + i * .5:.2f}s" fill="freeze"/></text>')
    hint = (f'<text x="{wx + ww - 24}" y="{py + 24}" text-anchor="end" font-family="{MONO}" font-size="11" '
            f'fill="{MUTED}" opacity="0">pick a channel below ▼<set attributeName="opacity" to="1" begin="1.2s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="1;.3;1" dur="1.6s" begin="1.4s" repeatCount="indefinite"/></text>')
    frame = hud_frame(W, H, tab="CONNECT", trace=True, c=18, fid="cf")
    return svg_open(W, H, "Connect with me") + f"""
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
{frame}
{chrome}
<g clip-path="url(#{clip})">{''.join(out)}{hint}</g>
{scanlines(W, H)}
</svg>
"""
