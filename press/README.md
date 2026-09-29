<div align="center">

<img src="social/x-header-1500x500.png" width="560" alt="Just Flip">

# Just Flip media kit

</div>

Everything here is drawn by `make_press.py`, not stored as source art. Change a colour or a size in that script and run it again, and the whole kit rebuilds.

```bash
cd press
python make_press.py
```

It needs Pillow, and it reads the coin drawing code from `../brand/make_coins.py`.

## What is in here

### `logo/` — transparent, for putting on top of things

Twelve files: the gold Heads coin, the silver Tails coin, and the split coin, each at 1024, 512, 256 and 128 pixels. The background is genuinely transparent, so these drop straight onto footage, a thumbnail, or a slide without a box around them.

Use the 1024 for anything that fills a screen and the 128 for a favicon or a corner mark. They are pixel art, so scale them by whole numbers where you can, and turn off smoothing in your editor or the edges go soft.

### `avatar/` — square, for profile pictures

`avatar-800.png` for X, Telegram and Discord. `avatar-400.png` for anywhere that asks for something smaller. Both are the two coins on the violet ground with the faint scatter behind.

### `social/` — sized to the slots the platforms actually use

`x-header-1500x500.png` is the X banner. Keep anything important away from the far left, that is where the profile picture sits on top.

`square-1080.png` is the Instagram feed post.

`og-1200x630.png` is the link preview card. This one is already wired into the site, so you only need it if you are making a variant.

### `video/` — plates to shoot over

`bg-1920x1080.png` and `bg-1080x1920.png` carry the coins and the wordmark. Horizontal for YouTube, vertical for Reels, TikTok and Shorts.

`plate-1920x1080.png` and `plate-1080x1920.png` are the same ground with the middle left empty and the scatter dimmed. These are the ones to put your own text, your screen recording or your face on.

### `palette.txt`

Every colour in Just Flip with its hex code, ready to paste into a video editor.

## A few things worth knowing

**The coins are pixel art.** Scaling them to 1.37x will smear the edges. Whole number scaling keeps them crisp, and most editors have a "nearest neighbour" or "no smoothing" option that fixes the rest.

**The wordmark has its own bitmap font.** It lives in `make_press.py` and only carries the letters `JUST FLIP` needs. If you want to set a different word, add its letters to the `FONT` table first.

**The violet ground is `#210F4B`.** If you need a plate at a size that is not here, add it to the script rather than stretching one of these.

## Using it

It is your game and your brand, so use these however you like. The one thing worth keeping consistent is the coin art itself: gold for Heads, silver for Tails, dark outline on both. That pairing is what people will start recognising.
