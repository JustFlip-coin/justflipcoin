"""Profile pictures on the reference background, using the outlined coin style."""

import math
import random
from PIL import Image, ImageDraw, ImageFilter

from make_coins import draw_coin, BG

SIZE = 800
RESAMPLE = getattr(Image, "Resampling", Image).NEAREST
BGRGB = (0x21, 0x0F, 0x4B)


def ground():
    """Reference violet with a soft lift in the middle, nothing more."""
    img = Image.new("RGB", (SIZE, SIZE), BGRGB)
    g = Image.new("RGB", (SIZE, SIZE), BGRGB)
    gd = ImageDraw.Draw(g)
    for i in range(34, 0, -1):
        r = int(SIZE * 0.66 * i / 34)
        t = 1 - i / 34.0
        gd.ellipse([SIZE // 2 - r, SIZE // 2 - r, SIZE // 2 + r, SIZE // 2 + r],
                   fill=(int(0x21 + 22 * t), int(0x0F + 14 * t), int(0x4B + 30 * t)))
    return Image.blend(img, g.filter(ImageFilter.GaussianBlur(70)), 0.9)


def scatter(img, clear_radius):
    """Small coins behind, kept faint and away from the centre."""
    random.seed(23)
    tiles = [draw_coin(80, face="H"), draw_coin(80, face="T")]
    step = 140
    for gy in range(-1, SIZE // step + 2):
        for gx in range(-1, SIZE // step + 2):
            cx = gx * step + random.randint(-36, 36)
            cy = gy * step + random.randint(-36, 36)
            if math.hypot(cx - SIZE / 2, cy - SIZE / 2) < clear_radius:
                continue
            s = random.randint(44, 76)
            t = random.choice(tiles).resize((s, s), RESAMPLE)
            f = t.copy()
            f.putalpha(t.getchannel("A").point(lambda v: int(v * random.uniform(0.15, 0.28))))
            img.paste(f, (cx - s // 2, cy - s // 2), f)
    return img


def drop(img, coins):
    """Soft shadow under each coin so they sit on the ground, not float."""
    sh = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    for c, (x, y) in coins:
        sh.paste(Image.new("RGBA", c.size, (0, 0, 0, 120)), (x, y + 16), c)
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    img.paste(sh, (0, 0), sh)
    for c, pos in coins:
        img.paste(c, pos, c)
    return img


# two coins side by side, far enough apart that neither letter is covered
BIG, OFF = 330, 132
t_big, h_big = draw_coin(BIG, face="T"), draw_coin(BIG, face="H")
pair = [
    (t_big, (SIZE // 2 - BIG // 2 - OFF, SIZE // 2 - BIG // 2 + 26)),
    (h_big, (SIZE // 2 - BIG // 2 + OFF, SIZE // 2 - BIG // 2 - 26)),
]
drop(ground(), pair).save("pfp-pair.png")
print("wrote pfp-pair.png")

# the split coin on the same ground
SPLIT = 470
sc = draw_coin(SPLIT, split=True)
drop(ground(), [(sc, (SIZE // 2 - SPLIT // 2, SIZE // 2 - SPLIT // 2))]).save("pfp-split-v2.png")
print("wrote pfp-split-v2.png")
