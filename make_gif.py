import math
import os
from PIL import Image, ImageChops, ImageDraw, ImageFilter

BG = (13, 8, 24)
SIZE = 480
CELL = 20
ART = 16
COIN = ART * CELL

RESAMPLE = getattr(Image, "Resampling", Image).NEAREST
DITHER = getattr(Image, "Dither", Image).NONE

HEADS = [
    (5, 0, 6, 1, "#FFCE58"),
    (3, 1, 10, 1, "#FFCE58"),
    (2, 2, 12, 1, "#FFCE58"),
    (1, 3, 14, 2, "#F5A623"),
    (0, 5, 16, 6, "#F5A623"),
    (1, 11, 14, 2, "#C98419"),
    (2, 13, 12, 1, "#C98419"),
    (3, 14, 10, 1, "#A66A12"),
    (5, 15, 6, 1, "#A66A12"),
    (5, 5, 2, 7, "#2B1A02"),
    (10, 5, 2, 7, "#2B1A02"),
    (7, 7, 3, 2, "#2B1A02"),
]

TAILS = [
    (5, 0, 6, 1, "#EEF4F8"),
    (3, 1, 10, 1, "#EEF4F8"),
    (2, 2, 12, 1, "#EEF4F8"),
    (1, 3, 14, 2, "#B9C8D4"),
    (0, 5, 16, 6, "#B9C8D4"),
    (1, 11, 14, 2, "#8497A6"),
    (2, 13, 12, 1, "#8497A6"),
    (3, 14, 10, 1, "#6A7C8A"),
    (5, 15, 6, 1, "#6A7C8A"),
    (4, 5, 8, 2, "#16202A"),
    (7, 7, 2, 5, "#16202A"),
]

EDGE = {0: "#C98419", 1: "#8497A6"}

# hand-drawn 5x7 pixel glyphs so the wordmark matches the coin, no font file needed
GLYPHS = {
    "J": ["00001", "00001", "00001", "00001", "10001", "10001", "01110"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    " ": ["00000"] * 7,
}


def render_face(rects):
    img = Image.new("RGB", (COIN, COIN), BG)
    d = ImageDraw.Draw(img)
    for x, y, w, h, color in rects:
        d.rectangle(
            [x * CELL, y * CELL, (x + w) * CELL - 1, (y + h) * CELL - 1], fill=color
        )
    return img


faces = [render_face(HEADS), render_face(TAILS)]


def coin_frame(theta):
    side = int(theta // math.pi) % 2
    width = max(1, int(round(COIN * abs(math.cos(theta)))))
    frame = Image.new("RGB", (SIZE, SIZE), BG)
    top = (SIZE - COIN) // 2
    if width < 8:
        bar = max(4, width)
        x0 = (SIZE - bar) // 2
        ImageDraw.Draw(frame).rectangle(
            [x0, top + 12, x0 + bar, top + COIN - 12], fill=EDGE[side]
        )
    else:
        frame.paste(faces[side].resize((width, COIN), RESAMPLE), ((SIZE - width) // 2, top))
    return frame


def render_wordmark(word="JUST FLIP", scale=7, color="#D8B4FE"):
    cols = len(word) * 5 + (len(word) - 1)
    strip = Image.new("RGB", (cols, 7), BG)
    d = ImageDraw.Draw(strip)
    for i, ch in enumerate(word):
        rows = GLYPHS[ch]
        ox = i * 6
        for y, row in enumerate(rows):
            for x, bit in enumerate(row):
                if bit == "1":
                    d.point((ox + x, y), fill=color)
    big = strip.resize((cols * scale, 7 * scale), RESAMPLE)

    frame = Image.new("RGB", (SIZE, SIZE), BG)
    frame.paste(big, ((SIZE - big.width) // 2, (SIZE - big.height) // 2))
    # phosphor glow, the same amber bloom the game's headline has
    glow = frame.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.75))
    return ImageChops.add(glow, frame)


def dim(img, factor):
    return img.point(lambda v: int(v * factor))


text_img = render_wordmark()
full_coin = coin_frame(0.0)

HALF_TURNS = 4
FPH = 8
SPIN = HALF_TURNS * FPH

frames = []
durations = []

for i in range(SPIN):
    frames.append(coin_frame(i * math.pi / FPH))
    durations.append(60)

FADE = 7

# sequential, never overlapping: the coin clears the frame before the name arrives,
# otherwise the wordmark prints on top of the coin and neither one reads
for k in range(1, FADE + 1):
    frames.append(dim(full_coin, 1 - k / FADE))
    durations.append(55)

for k in range(1, FADE + 1):
    frames.append(dim(text_img, k / FADE))
    durations.append(55)

for _ in range(8):
    frames.append(text_img.copy())
    durations.append(90)

for k in range(1, FADE + 1):
    frames.append(dim(text_img, 1 - k / FADE))
    durations.append(55)

for k in range(1, FADE + 1):
    frames.append(dim(full_coin, k / FADE))
    durations.append(55)

# one palette built from samples across the whole timeline, so fades never band or shift
picks = [0, 4, 8, SPIN - 2, SPIN + FADE - 1, SPIN + 2 * FADE + 2, len(frames) - 3]
sample = Image.new("RGB", (SIZE, SIZE * len(picks)), BG)
for i, p in enumerate(picks):
    sample.paste(frames[p], (0, i * SIZE))
palette = sample.quantize(colors=256)

paletted = [f.quantize(palette=palette, dither=DITHER) for f in frames]

OUT = "just-flip.gif"
paletted[0].save(
    OUT,
    save_all=True,
    append_images=paletted[1:],
    duration=durations,
    loop=0,
    disposal=2,
    optimize=True,
)

print("frames:", len(paletted))
print("phases: spin", SPIN, "| fade", FADE, "| hold 8 | fade back", FADE)
print("total duration:", round(sum(durations) / 1000, 2), "s")
print("bytes:", os.path.getsize(OUT))
