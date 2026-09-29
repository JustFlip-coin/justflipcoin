"""Media kit for Just Flip. Everything is drawn here, nothing is a stored image.

Run from inside press/ with make_coins.py reachable on the path.
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'brand'))
from make_coins import draw_coin, GOLD, SILVER

RES = getattr(Image, "Resampling", Image).NEAREST
BG = (0x21, 0x0F, 0x4B)

# 5 wide by 7 tall, only the letters JUST FLIP needs
FONT = {
 'J': ["00111","00010","00010","00010","00010","10010","01100"],
 'U': ["10001","10001","10001","10001","10001","10001","01110"],
 'S': ["01111","10000","10000","01110","00001","00001","11110"],
 'T': ["11111","00100","00100","00100","00100","00100","00100"],
 'F': ["11111","10000","10000","11110","10000","10000","10000"],
 'L': ["10000","10000","10000","10000","10000","10000","11111"],
 'I': ["11111","00100","00100","00100","00100","00100","11111"],
 'P': ["11110","10001","10001","11110","10000","10000","10000"],
 ' ': ["00000"] * 7,
}


def text(draw, s, x, y, px, fill):
    """Pixel type, one rect per lit cell, so it stays crisp at any size."""
    cx = x
    for ch in s:
        g = FONT[ch]
        for gy, row in enumerate(g):
            for gx, bit in enumerate(row):
                if bit == "1":
                    draw.rectangle([cx + gx * px, y + gy * px,
                                    cx + (gx + 1) * px - 1, y + (gy + 1) * px - 1], fill=fill)
        cx += (len(g[0]) + 1) * px
    return cx - x - px


def text_width(s, px):
    return sum((len(FONT[c][0]) + 1) * px for c in s) - px


def ground(w, h, bright=1.0):
    """The violet wash the game sits on, sized to whatever canvas is asked for."""
    img = Image.new("RGB", (w, h), BG)
    g = Image.new("RGB", (w, h), BG)
    px = g.load()
    for y in range(h):
        for x in range(0, w, 4):
            t = 1 - min(1.0, math.hypot((x - w / 2) * (h / float(w)), y - h / 2) / (h * 0.62))
            t *= bright
            c = (int(0x21 + 30 * t), int(0x0F + 18 * t), int(0x4B + 40 * t))
            for k in range(4):
                if x + k < w:
                    px[x + k, y] = c
    return Image.blend(img, g.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.06))), 0.92)


def scatter(img, seed, clear_w, clear_h, step, lo, hi, alpha=(0.12, 0.24)):
    random.seed(seed)
    w, h = img.size
    tiles = [draw_coin(96, face="H"), draw_coin(96, face="T")]
    for gy in range(-1, h // step + 2):
        for gx in range(-1, w // step + 2):
            cx = gx * step + random.randint(-step // 3, step // 3)
            cy = gy * step + random.randint(-step // 3, step // 3)
            if abs(cx - w / 2) < clear_w / 2 and abs(cy - h / 2) < clear_h / 2:
                continue
            s = random.randint(lo, hi)
            t = random.choice(tiles).resize((s, s), RES)
            f = t.copy()
            f.putalpha(t.getchannel("A").point(lambda v: int(v * random.uniform(*alpha))))
            img.paste(f, (cx - s // 2, cy - s // 2), f)
    return img


def shadowed(img, items, blur=22, alpha=120, drop=18):
    w, h = img.size
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for c, (x, y) in items:
        sh.paste(Image.new("RGBA", c.size, (0, 0, 0, alpha)), (x, y + drop), c)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste(sh, (0, 0), sh)
    for c, pos in items:
        img.paste(c, pos, c)
    return img


# ---------------- transparent marks, for compositing over video ----------------
for name, kw in (("coin-h", dict(face="H")), ("coin-t", dict(face="T")), ("coin-split", dict(split=True))):
    for size in (1024, 512, 256, 128):
        draw_coin(size, **kw).save("logo/%s-%d.png" % (name, size))
print("logo: 12 transparent files")

# ---------------- avatar, square, coins side by side ----------------
for size in (800, 400):
    big = int(size * 0.41)
    off = int(size * 0.165)
    img = scatter(ground(size, size), 23, size * 0.62, size * 0.62, int(size * 0.175),
                  int(size * 0.055), int(size * 0.095))
    pair = [(draw_coin(big, face="T"), (size // 2 - big // 2 - off, size // 2 - big // 2 + int(size * 0.032))),
            (draw_coin(big, face="H"), (size // 2 - big // 2 + off, size // 2 - big // 2 - int(size * 0.032)))]
    shadowed(img, pair).save("avatar/avatar-%d.png" % size)
print("avatar: 2 files")

# ---------------- social ----------------
def banner(w, h, path, coin_frac=0.46, title=True):
    img = scatter(ground(w, h), 7, w * 0.52, h * 0.7, int(min(w, h) * 0.17),
                  int(min(w, h) * 0.045), int(min(w, h) * 0.085))
    big = int(h * coin_frac)
    off = int(big * 0.42)
    # lifted when a title follows, or the type runs off the bottom edge
    cy = int(h * (0.38 if title else 0.5))
    pair = [(draw_coin(big, face="T"), (w // 2 - big // 2 - off, cy - big // 2 + int(h * 0.03))),
            (draw_coin(big, face="H"), (w // 2 - big // 2 + off, cy - big // 2 - int(h * 0.03)))]
    shadowed(img, pair, blur=int(h * 0.035), drop=int(h * 0.028))
    if title:
        d = ImageDraw.Draw(img)
        s = "JUST FLIP"
        # sized from the WIDTH, never the height: on a 1080x1920 plate a height
        # derived cell ran the word more than twice past both edges
        px = max(2, int(w * 0.70 / (text_width(s, 1) or 1)))
        px = min(px, max(2, int(h * 0.030)))
        tw = text_width(s, px)
        # placed from the bottom so the last row never clips, whatever the ratio
        ty = h - 7 * px - int(h * 0.08)
        text(d, s, (w - tw) // 2 + px // 2, ty + px // 2, px, (0x23, 0x07, 0x04))
        text(d, s, (w - tw) // 2, ty, px, (0xFC, 0xCA, 0x07))
    img.save(path)

banner(1500, 500, "social/x-header-1500x500.png", coin_frac=0.52)
banner(1080, 1080, "social/square-1080.png", coin_frac=0.40)
banner(1200, 630, "social/og-1200x630.png", coin_frac=0.46)
banner(1280, 720, "social/youtube-thumb-1280x720.png", coin_frac=0.44)
# same ratio with the middle left clear, for a title or a face
plate = scatter(ground(1280, 720, bright=0.8), 11, 1280 * 0.62, 720 * 0.52, 115, 30, 56)
plate.save("social/youtube-plate-1280x720.png")
print("social: 5 files")

# ---------------- video plates ----------------
banner(1920, 1080, "video/bg-1920x1080.png", coin_frac=0.40)
banner(1080, 1920, "video/bg-1080x1920.png", coin_frac=0.26)

for w, h, path in ((1920, 1080, "video/plate-1920x1080.png"), (1080, 1920, "video/plate-1080x1920.png")):
    # nothing in the middle: room for your own text or footage
    scatter(ground(w, h, bright=0.8), 11, w * 0.60, h * 0.50, int(min(w, h) * 0.16),
            int(min(w, h) * 0.04), int(min(w, h) * 0.075)).save(path)
print("video: 4 files")

# ---------------- colour list, written as text so the codes can be copied ----------------
rows = [("ink", "#0D0818"), ("panel", "#160F28"), ("violet", "#A78BFA"),
        ("violet bright", "#D8B4FE"), ("violet deep", "#4C2E8A"), ("copper", "#E0672B"),
        ("copper bright", "#FF9257"), ("gold light", GOLD["light"]), ("gold", GOLD["mid"]),
        ("gold dark", GOLD["dark"]), ("gold deep", GOLD["deep"]), ("outline", GOLD["line"]),
        ("silver light", SILVER["light"]), ("silver", SILVER["mid"]), ("silver deep", SILVER["deep"])]
with open("palette.txt", "w", encoding="utf-8") as fh:
    fh.write("Just Flip palette\n\n")
    for nm, hx in rows:
        fh.write("%-16s %s\n" % (nm, hx.upper()))
print("palette.txt: %d colours" % len(rows))
