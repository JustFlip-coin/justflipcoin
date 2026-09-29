"""Coins rebuilt in the reference style: dark outline, brighter metal, violet ground.

Palette sampled straight from the reference image rather than eyeballed.
"""

import math
from PIL import Image, ImageDraw

N = 26                       # art grid, one cell per drawn pixel
RESAMPLE = getattr(Image, "Resampling", Image).NEAREST

BG = "#210F4B"

GOLD = {
    "line":  "#230704",
    "light": "#FCCA07",
    "mid":   "#FBB402",
    "dark":  "#DD6600",
    "deep":  "#CA5204",
    "ink":   "#230503",
}

SILVER = {
    "line":  "#131A22",
    "light": "#F4F9FC",
    "mid":   "#C6D5E0",
    "dark":  "#8A9BAA",
    "deep":  "#6B7C8C",
    "ink":   "#131A22",
}

# letters on a 10 wide by 12 tall block, thick enough to read when tiny
H_BARS = [(0, 0, 3, 12), (7, 0, 3, 12), (3, 5, 4, 2)]
T_BARS = [(0, 0, 10, 3), (4, 3, 2, 9)]


def band(y, pal):
    if y <= 3:
        return pal["light"]
    if y <= 15:
        return pal["mid"]
    if y <= 20:
        return pal["dark"]
    return pal["deep"]


def spans(n):
    """Row by row extent of a circle that fills the grid."""
    out = []
    r = n / 2.0
    for y in range(n):
        dy = y + 0.5 - r
        if abs(dy) >= r:
            out.append(None)
            continue
        half = math.sqrt(max(0.0, r * r - dy * dy))
        out.append((int(round(r - half)), int(round(r + half)) - 1))
    return out


def draw_coin(px, face="H", split=False):
    """face: 'H' or 'T'. split=True puts gold H in the left half, silver T in the right."""
    c = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    rows = spans(N)
    mid = N // 2

    def pal_at(x):
        if split:
            return GOLD if x < mid else SILVER
        return GOLD if face == "H" else SILVER

    # body
    for y, sp in enumerate(rows):
        if not sp:
            continue
        x0, x1 = sp
        for x in range(x0, x1 + 1):
            d.point((x, y), fill=band(y, pal_at(x)))

    # dark rim: any filled cell that touches empty space or the grid edge
    filled = {(x, y) for y, sp in enumerate(rows) if sp for x in range(sp[0], sp[1] + 1)}
    for (x, y) in list(filled):
        if any((x + dx, y + dy) not in filled
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            d.point((x, y), fill=pal_at(x)["line"])

    # letters
    def letter(bars, ox, oy, ink):
        for bx, by, bw, bh in bars:
            d.rectangle([ox + bx, oy + by, ox + bx + bw - 1, oy + by + bh - 1], fill=ink)

    if split:
        # one letter per half, each shrunk to fit its side
        small_h = [(0, 0, 2, 9), (4, 0, 2, 9), (2, 4, 2, 2)]
        small_t = [(0, 0, 6, 2), (2, 2, 2, 7)]
        letter(small_h, 3, 9, GOLD["ink"])
        letter(small_t, 17, 9, SILVER["ink"])
        for y, sp in enumerate(rows):
            if not sp:
                continue
            d.point((mid - 1, y), fill=GOLD["deep"])
            d.point((mid, y), fill=SILVER["deep"])
    else:
        pal = GOLD if face == "H" else SILVER
        letter(H_BARS if face == "H" else T_BARS, 8, 7, pal["ink"])

    return c.resize((px, px), RESAMPLE)


def plate(coin_img, size=800, coin_px=520):
    img = Image.new("RGB", (size, size), BG)
    # barely there vignette, the reference is almost flat
    g = Image.new("RGB", (size, size), BG)
    gd = ImageDraw.Draw(g)
    for i in range(30, 0, -1):
        r = int(size * 0.62 * i / 30)
        t = 1 - i / 30.0
        gd.ellipse([size // 2 - r, size // 2 - r, size // 2 + r, size // 2 + r],
                   fill=(int(0x21 + 10 * t), int(0x0F + 7 * t), int(0x4B + 16 * t)))
    img = Image.blend(img, g, 0.85)
    c = coin_img.resize((coin_px, coin_px), RESAMPLE)
    img.paste(c, (size // 2 - coin_px // 2, size // 2 - coin_px // 2), c)
    return img


for name, kw in [("coin-h", dict(face="H")),
                 ("coin-t", dict(face="T")),
                 ("coin-split", dict(split=True))]:
    coin = draw_coin(N * 24, **kw)
    plate(coin).save(name + ".png")
    print("wrote", name + ".png")
