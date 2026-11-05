"""Roadie brand assets: the prairie vanity plate, with lettering converted to outlines
so it renders identically everywhere and is centred to measured bounds.

Outputs:
  data/brand/plate.svg        horizontal plate logo (viewBox 0 0 200 104)
  data/brand/icon.svg         square app icon (plate on navy)
  data/brand/brand.json       {"plate": "<svg...>", "icon": "<svg...>"} for the app build
  docs/icons/*.png            apple-touch / PWA / favicon PNGs
"""
import json, os, sys
import fitz
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = sys.argv[1]
FONT = "C:/Windows/Fonts/bahnschrift.ttf"
NAVY, AMBER, WHITE = "#12305b", "#f5b301", "#ffffff"


def load(wght, wdth):
    f = instancer.instantiateVariableFont(TTFont(FONT), {"wght": wght, "wdth": wdth})
    return f, f.getGlyphSet(), f.getBestCmap(), f["OS/2"].sCapHeight


def text_path(font, s, cap, track, cx, baseline, max_w=None):
    """Path for string s with cap height `cap`, letter tracking `track`, visually centred on cx."""
    _, gs, cmap, caph = font
    def build(scale, x0):
        pen, bounds, x = SVGPathPen(gs), BoundsPen(gs), x0
        for ch in s:
            g = gs[cmap[ord(ch)]]
            g.draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
            g.draw(TransformPen(bounds, (scale, 0, 0, -scale, x, baseline)))
            x += g.width * scale + (track if ch != " " else track * .6)
        return pen.getCommands(), bounds.bounds
    scale = cap / caph
    _, b = build(scale, 0)
    if max_w and b[2] - b[0] > max_w:          # shrink to fit the measured width
        scale *= max_w / (b[2] - b[0]); _, b = build(scale, 0)
    d, b = build(scale, cx - (b[0] + b[2]) / 2)  # centre on the true ink bounds
    return d, b


bold = load(700, 75)       # Bold Condensed for the plate number
semi = load(600, 87.5)     # SemiBold SemiCondensed for the header line

# ---- plate geometry (inner field 11..189 x 11..93) ----
roadie_d, rb = text_path(bold, "ROADIE", cap=31, track=4.2, cx=100, baseline=66, max_w=128)
head_d, hb = text_path(semi, "LEARNER\u2019S EDITION", cap=6.2, track=1.9, cx=100, baseline=26.5, max_w=104)
bolts = "".join(f'<circle cx="{x}" cy="{y}" r="3.3" fill="#d5dde8" stroke="#9aa8bb" stroke-width="1"/><path d="M{x-2} {y}h4" stroke="#9aa8bb" stroke-width="1"/>'
                for x, y in ((24, 22), (176, 22), (24, 82), (176, 82)))
scenery = (f'<clipPath id="rdInner"><rect x="11" y="11" width="178" height="82" rx="7"/></clipPath><g clip-path="url(#rdInner)">'
           f'<path d="M11 80 L30 70 L42 76 L60 68 L74 75 L92 70 L108 77 L126 69 L142 76 L160 68 L176 74 L189 70 V93 H11Z" fill="#dfe8f5"/>'
           f'<path d="M11 86 C50 79 90 88 130 81 S178 83 189 80 V93 H11Z" fill="#f3d27a"/></g>')
plate_inner = (f'<rect x="4" y="4" width="192" height="96" rx="12" fill="{WHITE}" stroke="{NAVY}" stroke-width="4"/>'
               f'{scenery}<rect x="11" y="11" width="178" height="82" rx="7" fill="none" stroke="{NAVY}" stroke-width="1.2" opacity=".55"/>'
               f'{bolts}<path d="{head_d}" fill="#c98d00"/><path d="{roadie_d}" fill="{NAVY}"/>')
plate_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 104" role="img" aria-label="Roadie">{plate_inner}</svg>'
icon_svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" fill="{NAVY}"/>'
            f'<g transform="translate(10 48) scale(.9)">{plate_inner}</g></svg>')

print(f"ROADIE ink x {rb[0]:.1f}-{rb[2]:.1f} (margins {rb[0]-11:.1f} / {189-rb[2]:.1f}), y {rb[1]:.1f}-{rb[3]:.1f}")
print(f"header ink x {hb[0]:.1f}-{hb[2]:.1f}, clear of bolts: {hb[0] > 30 and hb[2] < 170}")

out = os.path.join(ROOT, "data", "brand"); os.makedirs(out, exist_ok=True)
open(os.path.join(out, "plate.svg"), "w", encoding="utf-8").write(plate_svg)
open(os.path.join(out, "icon.svg"), "w", encoding="utf-8").write(icon_svg)
json.dump({"plate": plate_svg, "icon": icon_svg}, open(os.path.join(out, "brand.json"), "w", encoding="utf-8"))

icons = os.path.join(ROOT, "docs", "icons"); os.makedirs(icons, exist_ok=True)
for name, svg, px in (("icon-512.png", icon_svg, 512), ("icon-192.png", icon_svg, 192), ("apple-touch-icon.png", icon_svg, 180),
                      ("favicon-32.png", icon_svg, 32), ("plate-600.png", plate_svg, 600)):
    doc = fitz.open(stream=svg.encode(), filetype="svg")
    page = doc[0]
    z = px / page.rect.width
    page.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False).save(os.path.join(icons, name))
print("wrote", out, "and", icons)
