"""
Pixel Art Gesture Frame Generator
Generates 128x64 pixel art hand gesture animations for the smart glasses display.
Each gesture gets multi-frame animations depicting simplified ASL signs.
"""
from PIL import Image, ImageDraw
from pathlib import Path

W, H = 128, 64
BG = (0, 0, 0)
SKIN = (220, 180, 140)
SKIN_DARK = (180, 140, 100)
WHITE = (255, 255, 255)
ACCENT = (100, 200, 100)

OUT = Path(__file__).parent / "gestures" / "data" / "frames"


def new_frame():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def draw_palm(d, cx, cy, size=14):
    d.rounded_rectangle([cx - size, cy - size, cx + size, cy + size], radius=4, fill=SKIN)


def draw_finger(d, x1, y1, x2, y2, width=4):
    d.line([(x1, y1), (x2, y2)], fill=SKIN, width=width)
    d.ellipse([x2 - 2, y2 - 2, x2 + 2, y2 + 2], fill=SKIN)


def draw_fist(d, cx, cy, size=12):
    h = int(size * 0.7)
    d.rounded_rectangle([cx - size, cy - h, cx + size, cy + h], radius=min(4, h), fill=SKIN)
    knuckle_h = max(int(size * 0.2), 2)
    d.rectangle([cx - size + 2, cy - h, cx + size - 2, cy - h + knuckle_h], fill=SKIN_DARK)


def draw_label(d, text):
    d.text((4, H - 10), text.upper(), fill=(120, 120, 120))


# ── HELLO: Open hand wave side-to-side ──
def gen_hello():
    folder = OUT / "hello"
    folder.mkdir(parents=True, exist_ok=True)
    offsets = [-8, 0, 8, 0]
    for i, ox in enumerate(offsets):
        img, d = new_frame()
        cx, cy = 64 + ox, 28
        draw_palm(d, cx, cy, 12)
        for angle, dx, dy in [(-2, -8, -18), (-1, -3, -20), (0, 3, -20), (1, 8, -18), (2, 14, -14)]:
            draw_finger(d, cx + dx, cy - 10, cx + dx + angle * 2, dy + cy - 8)
        draw_label(d, "hello")
        img.save(folder / f"f{i+1}.png")


# ── THANK YOU: Hand from chin forward ──
def gen_thank_you():
    folder = OUT / "thank_you"
    folder.mkdir(parents=True, exist_ok=True)
    positions = [(64, 44), (64, 38), (64, 30), (64, 24), (64, 20)]
    for i, (cx, cy) in enumerate(positions):
        img, d = new_frame()
        draw_palm(d, cx, cy, 11)
        for dx in [-6, -2, 2, 6]:
            draw_finger(d, cx + dx, cy - 9, cx + dx, cy - 22)
        if i < 2:
            d.arc([cx - 18, cy + 6, cx + 18, cy + 18], 0, 180, fill=SKIN_DARK, width=2)
        draw_label(d, "thank you")
        img.save(folder / f"f{i+1}.png")


# ── YES: Fist nodding up and down ──
def gen_yes():
    folder = OUT / "yes"
    folder.mkdir(parents=True, exist_ok=True)
    y_offsets = [0, -8, 0]
    for i, oy in enumerate(y_offsets):
        img, d = new_frame()
        cx, cy = 64, 30 + oy
        draw_fist(d, cx, cy)
        d.line([(cx, cy + 10), (cx, cy + 24)], fill=SKIN_DARK, width=5)
        draw_label(d, "yes")
        img.save(folder / f"f{i+1}.png")


# ── NO: Index+middle finger snap closed ──
def gen_no():
    folder = OUT / "no"
    folder.mkdir(parents=True, exist_ok=True)
    gaps = [10, 5, 0]
    for i, gap in enumerate(gaps):
        img, d = new_frame()
        cx, cy = 64, 32
        d.rounded_rectangle([cx - 8, cy, cx + 8, cy + 14], radius=3, fill=SKIN)
        draw_finger(d, cx - 3, cy, cx - 3 - gap, cy - 18)
        draw_finger(d, cx + 3, cy, cx + 3 + gap, cy - 18)
        d.ellipse([cx + 6, cy + 2, cx + 14, cy + 12], fill=SKIN_DARK)
        draw_label(d, "no")
        img.save(folder / f"f{i+1}.png")


# ── PLEASE: Circular motion on chest ──
def gen_please():
    folder = OUT / "please"
    folder.mkdir(parents=True, exist_ok=True)
    import math
    for i in range(4):
        img, d = new_frame()
        angle = i * (math.pi / 2)
        cx = 64 + int(10 * math.cos(angle))
        cy = 32 + int(6 * math.sin(angle))
        draw_palm(d, cx, cy, 11)
        for dx in [-6, -2, 2, 6]:
            draw_finger(d, cx + dx, cy - 9, cx + dx, cy - 20)
        d.ellipse([50, 22, 78, 46], outline=(60, 60, 60), width=1)
        draw_label(d, "please")
        img.save(folder / f"f{i+1}.png")


# ── SORRY: Fist circular on chest ──
def gen_sorry():
    folder = OUT / "sorry"
    folder.mkdir(parents=True, exist_ok=True)
    import math
    for i in range(4):
        img, d = new_frame()
        angle = i * (math.pi / 2)
        cx = 64 + int(10 * math.cos(angle))
        cy = 30 + int(8 * math.sin(angle))
        draw_fist(d, cx, cy, 10)
        d.ellipse([50, 18, 78, 42], outline=(60, 60, 60), width=1)
        draw_label(d, "sorry")
        img.save(folder / f"f{i+1}.png")


# ── HELP: One fist on open palm, lifting up ──
def gen_help():
    folder = OUT / "help"
    folder.mkdir(parents=True, exist_ok=True)
    lifts = [0, -5, -10, -14]
    for i, oy in enumerate(lifts):
        img, d = new_frame()
        draw_palm(d, 56, 38, 13)
        for dx in [-8, -3, 2, 7]:
            draw_finger(d, 56 + dx, 26, 56 + dx, 18)
        draw_fist(d, 72, 34 + oy, 9)
        d.line([(72, 34 + oy + 8), (72, 50 + oy)], fill=SKIN_DARK, width=4)
        draw_label(d, "help")
        img.save(folder / f"f{i+1}.png")


# ── LOVE: ILY handshape (thumb + index + pinky extended) ──
def gen_love():
    folder = OUT / "love"
    folder.mkdir(parents=True, exist_ok=True)
    scales = [0.85, 1.0, 1.0]
    for i, s in enumerate(scales):
        img, d = new_frame()
        cx, cy = 64, 36
        sz = int(12 * s)
        draw_palm(d, cx, cy, sz)
        draw_finger(d, cx - sz + 2, cy - 4, cx - sz - 8, cy - 22)
        draw_finger(d, cx - 2, cy - sz, cx - 2, cy - sz - 16)
        draw_finger(d, cx + sz - 2, cy - 4, cx + sz + 8, cy - 22)
        d.rounded_rectangle([cx - 4, cy - sz, cx + 4, cy - sz + 6], radius=2, fill=SKIN_DARK)
        if i == 0:
            d.text((cx - 8, cy + sz + 4), "♥", fill=(200, 60, 60))
        draw_label(d, "love")
        img.save(folder / f"f{i+1}.png")


# ── HAPPY: Both hands patting upward on chest ──
def gen_happy():
    folder = OUT / "happy"
    folder.mkdir(parents=True, exist_ok=True)
    y_offsets = [0, -6, 0]
    for i, oy in enumerate(y_offsets):
        img, d = new_frame()
        for side in [-1, 1]:
            cx = 64 + side * 20
            cy = 34 + oy
            draw_palm(d, cx, cy, 10)
            for dx in [-5, -1, 3, 7]:
                draw_finger(d, cx + dx, cy - 8, cx + dx, cy - 18)
        if i == 1:
            d.text((56, 8), "^ ^", fill=ACCENT)
        draw_label(d, "happy")
        img.save(folder / f"f{i+1}.png")


# ── GOOD: Flat hand from chin forward ──
def gen_good():
    folder = OUT / "good"
    folder.mkdir(parents=True, exist_ok=True)
    positions = [(64, 42), (64, 34), (64, 26)]
    for i, (cx, cy) in enumerate(positions):
        img, d = new_frame()
        draw_palm(d, cx, cy, 12)
        for dx in [-7, -3, 1, 5, 9]:
            draw_finger(d, cx + dx, cy - 10, cx + dx, cy - 22)
        if i == 0:
            d.arc([cx - 14, cy + 8, cx + 14, cy + 16], 0, 180, fill=SKIN_DARK, width=2)
        draw_label(d, "good")
        img.save(folder / f"f{i+1}.png")


if __name__ == "__main__":
    generators = [
        gen_hello, gen_thank_you, gen_yes, gen_no, gen_please,
        gen_sorry, gen_help, gen_love, gen_happy, gen_good,
    ]
    for gen in generators:
        name = gen.__name__.replace("gen_", "")
        gen()
        print(f"✓ Generated: {name}")
    print(f"\nAll frames saved to: {OUT}")
