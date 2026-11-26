"""Shared look: an engineering blueprint. Deep blue paper, fine grid, white ink, yellow markup pen."""
from __future__ import annotations

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, 'Liberation Mono', monospace"

PAPER = "#0b2545"
GRID = "#14345c"
GRID2 = "#1b4170"
INK = "#e9f1ff"
DIM = "#8fb0d9"
FAINT = "#4d74a3"
PEN = "#ffc83d"          # markup


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def defs() -> str:
    return (f'<pattern id="g1" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M12,0 V12 H0" fill="none" stroke="{GRID}" stroke-width=".6"/></pattern>'
            f'<pattern id="g2" width="60" height="60" patternUnits="userSpaceOnUse"><rect width="60" height="60" fill="url(#g1)"/>'
            f'<path d="M60,0 V60 H0" fill="none" stroke="{GRID2}" stroke-width="1"/></pattern>'
            f'<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,1 L10,5 L0,9" fill="none" stroke="{DIM}" stroke-width="1.4"/></marker>'
            # glows: ink lines get a cool bloom, markup pen a warm one
            f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="100%" height="100%"><feGaussianBlur in="SourceGraphic" stdDeviation="2.2" result="b"/>'
            f'<feColorMatrix in="b" type="matrix" values="0 0 0 0 .55  0 0 0 0 .78  0 0 0 0 1  0 0 0 1.4 0" result="c"/>'
            f'<feMerge><feMergeNode in="c"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            f'<filter id="glowY" filterUnits="userSpaceOnUse" x="0" y="0" width="100%" height="100%"><feGaussianBlur in="SourceGraphic" stdDeviation="2.6" result="b"/>'
            f'<feColorMatrix in="b" type="matrix" values="0 0 0 0 1  0 0 0 0 .78  0 0 0 0 .24  0 0 0 1.6 0" result="c"/>'
            f'<feMerge><feMergeNode in="c"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            f'<filter id="glowT" filterUnits="userSpaceOnUse" x="0" y="0" width="100%" height="100%"><feGaussianBlur in="SourceGraphic" stdDeviation="3" result="b"/>'
            f'<feColorMatrix in="b" type="matrix" values="0 0 0 0 .45  0 0 0 0 .7  0 0 0 0 1  0 0 0 .55 0" result="c"/>'
            f'<feMerge><feMergeNode in="c"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            f'<radialGradient id="lightbox" cx=".35" cy=".4" r=".75"><stop offset="0" stop-color="#2a6bb3" stop-opacity=".45"/>'
            f'<stop offset=".6" stop-color="#1a4c86" stop-opacity=".12"/><stop offset="1" stop-color="#0b2545" stop-opacity="0"/></radialGradient>')


def sheet(w: int, h: int, zones: bool = True) -> str:
    """Paper, grid, double border and (optionally) zone marks A, B, C… / 1, 2, 3… like a drawing sheet."""
    out = (f'<rect width="{w}" height="{h}" rx="6" fill="{PAPER}"/><rect width="{w}" height="{h}" rx="6" fill="url(#lightbox)">'
           f'<animate attributeName="opacity" values=".75;1;.75" dur="6s" repeatCount="indefinite"/></rect>'
           f'<rect x="14" y="14" width="{w - 28}" height="{h - 28}" fill="url(#g2)"/>'
           f'<rect x="14.5" y="14.5" width="{w - 29}" height="{h - 29}" fill="none" stroke="{DIM}" stroke-width="1" filter="url(#glow)"/>'
           f'<rect x="8.5" y="8.5" width="{w - 17}" height="{h - 17}" fill="none" stroke="{FAINT}" stroke-width=".8"/>')
    if zones:
        nx, ny = max(2, round(w / 170)), max(2, round(h / 170))
        for i in range(nx):
            x = 14 + (w - 28) * (i + .5) / nx
            out += (f'<text x="{x:.0f}" y="13" text-anchor="middle" font-family="{MONO}" font-size="7" fill="{FAINT}">{i + 1}</text>'
                    f'<text x="{x:.0f}" y="{h - 5}" text-anchor="middle" font-family="{MONO}" font-size="7" fill="{FAINT}">{i + 1}</text>')
            if i:
                xb = 14 + (w - 28) * i / nx
                out += f'<path d="M{xb:.0f},8.5 V14.5 M{xb:.0f},{h - 14.5} V{h - 8.5}" stroke="{FAINT}"/>'
        for j in range(ny):
            y = 14 + (h - 28) * (j + .5) / ny
            c = "ABCDEFGH"[j]
            out += (f'<text x="11.5" y="{y + 2.5:.0f}" text-anchor="middle" font-family="{MONO}" font-size="7" fill="{FAINT}">{c}</text>'
                    f'<text x="{w - 11.5}" y="{y + 2.5:.0f}" text-anchor="middle" font-family="{MONO}" font-size="7" fill="{FAINT}">{c}</text>')
    return out


def label(x: float, y: float, text: str, size: float = 10.5, fill: str = DIM, anchor: str = "start", ls: float = 1.6) -> str:
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
            f'letter-spacing="{ls}">{esc(text)}</text>')


def dim_h(x1: float, x2: float, y: float, text: str) -> str:
    """Horizontal dimension line with arrows and a value in the middle."""
    m = (x1 + x2) / 2
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{DIM}" stroke-width=".9" marker-start="url(#arr)" marker-end="url(#arr)"/>'
            f'<rect x="{m - len(text) * 3.6 - 5:.0f}" y="{y - 7}" width="{len(text) * 7.2 + 10:.0f}" height="14" fill="{PAPER}"/>'
            + label(m, y + 3.5, text, 10, DIM, "middle", .5))


def dim_v(x: float, y1: float, y2: float, text: str) -> str:
    m = (y1 + y2) / 2
    return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{DIM}" stroke-width=".9" marker-start="url(#arr)" marker-end="url(#arr)"/>'
            f'<g transform="rotate(-90 {x} {m})"><rect x="{x - len(text) * 3.6 - 5:.0f}" y="{m - 7}" width="{len(text) * 7.2 + 10:.0f}" height="14" fill="{PAPER}"/>'
            + label(x, m + 3.5, text, 10, DIM, "middle", .5) + '</g>')


def draw_in(d: str, t: float, dur: float, stroke: str = INK, width: float = 1.4, length: int = 2000, extra: str = "") -> str:
    """A path that draws itself, like a pen (with a glow matching its ink)."""
    if "filter=" not in extra and stroke in (INK, PEN):
        extra += f' filter="url(#{"glowY" if stroke == PEN else "glow"})"'
    return (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" '
            f'pathLength="100" stroke-dasharray="100 100" stroke-dashoffset="100" {extra}><animate attributeName="stroke-dashoffset" from="100" to="0" '
            f'begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></path>')


def appear(t: float, body: str) -> str:
    return f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur=".5s" fill="freeze"/>{body}</g>'


def svg(w: int, h: int, body: str, extra_defs: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<defs>{defs()}{extra_defs}</defs>{body}</svg>\n')
