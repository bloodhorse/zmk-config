# Draws the OLED animations as 1-bit 32x128 frames, the one source both the emulator
# (frames.js) and, later, the firmware's C arrays are cut from. Run: uv run --with pillow oled/gen.py
import base64, json, math, pathlib
from PIL import Image, ImageDraw

W, H = 32, 128
SS = 8  # supersampling: draw big, shrink, threshold

# the void's star (thevoid/mock/mark.html): tip offsets measured off bekh's drawing
SKEW_DEG = [-1.4, -12.3, -0.4, -0.9, -5.6]
SKEW_R = [1.0, 0.993, 0.975, 0.982, 0.993]


def star_pts(cx, cy, r, rot, skewed=True):
    pts = []
    for k in range(5):
        a = math.radians(-90 + 72 * k + (SKEW_DEG[k] if skewed else 0) + rot)
        rr = r * (SKEW_R[k] if skewed else 1)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return [pts[i] for i in (0, 2, 4, 1, 3)]


def canvas():
    im = Image.new("L", (W * SS, H * SS), 0)
    return im, ImageDraw.Draw(im)


def star(d, cx, cy, r, rot, stroke):
    p = [(x * SS, y * SS) for x, y in star_pts(cx, cy, r, rot)]
    d.line(p + [p[0], p[1]], fill=255, width=round(stroke * SS), joint="curve")


def to_bits(im, cut=110):
    small = im.resize((W, H), Image.LANCZOS)
    px = small.load()
    out = bytearray(W * H // 8)
    for y in range(H):
        for x in range(W):
            if px[x, y] > cut:
                i = y * W + x
                out[i >> 3] |= 0x80 >> (i & 7)
    return base64.b64encode(bytes(out)).decode()


# r: a star 15% wider than the screen. tip-up width is 2r*cos18, so r = 32*1.15 / 1.902
R = 32 * 1.15 / (2 * math.cos(math.radians(18)))
STEP = 5  # degrees a frame; the skew breaks the symmetry, so a loop is a full turn


def one(stroke=2.0, cy=H / 2):
    frames = []
    for f in range(360 // STEP):
        im, d = canvas()
        star(d, W / 2, cy, R, f * STEP, stroke)
        frames.append(to_bits(im))
    return frames


def drift(stroke=2.0, gap=12):
    # sinks through the strip while turning; period = one star height + gap, so it tiles
    period = 2 * R + gap
    n = 360 // STEP
    frames = []
    for f in range(n):
        im, d = canvas()
        off = period * f / n
        y = -R + off
        while y < H + R:
            star(d, W / 2, y, R, f * STEP, stroke)
            y += period
        frames.append(to_bits(im))
    return frames


def column(stroke=2.0):
    n = 360 // STEP
    ys = [H / 6, H / 2, 5 * H / 6]
    frames = []
    for f in range(n):
        im, d = canvas()
        for i, y in enumerate(ys):
            star(d, W / 2, y, R, f * STEP * (1 if i != 1 else -1) + i * 24, stroke)
        frames.append(to_bits(im))
    return frames


ANIMS = {
    "star": dict(fps=12, frames=one()),
    "star-thin": dict(fps=12, frames=one(stroke=1.2)),
    "star-drift": dict(fps=12, frames=drift()),
    "star-column": dict(fps=12, frames=column()),
    "blank": dict(fps=1, frames=[to_bits(canvas()[0])]),
}

out = pathlib.Path(__file__).with_name("frames.js")
out.write_text("window.ANIMS = " + json.dumps({"w": W, "h": H, "anims": ANIMS}) + ";\n")
print(f"{out}: " + ", ".join(f"{k} {len(v['frames'])}f" for k, v in ANIMS.items()))
