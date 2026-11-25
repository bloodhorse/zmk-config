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


def spin(over, turn_s, fps, stroke=2.0):
    # one star in the middle, `over` past the side edges at its widest, one turn in turn_s seconds
    r = W * (1 + over) / (2 * math.cos(math.radians(18)))
    n = round(turn_s * fps)
    frames = []
    for f in range(n):
        im, d = canvas()
        star(d, W / 2, H / 2, r, 360 * f / n, stroke)
        frames.append(to_bits(im))
    return dict(fps=fps, frames=frames)


def gem_frames():
    # nice_oled's crystal: 16 frames of 69x68, indexed 1-bit, index 1 lit
    import re
    src = pathlib.Path(__file__).with_name("assets").joinpath("crystal.c").read_text()
    out = []
    for body in re.findall(r"crystal_\d\d_map\[\] = \{(.*?)\};", src, re.S):
        body = re.sub(r"#if.*?#endif", "", body, flags=re.S)
        b = [int(x, 16) for x in re.findall(r"0x[0-9a-fA-F]{2}", body)]
        im = Image.new("L", (69, 68), 0)
        im.putdata([255 if (b[y * 9 + (x >> 3)] >> (7 - (x & 7))) & 1 else 0 for y in range(68) for x in range(69)])
        out.append(im)
    return out


def gem(length=1.0, width=1.0):
    # its long axis runs down the strip, the way the old peripheral screen showed it
    frames = []
    for g in gem_frames():
        g = g.rotate(90, expand=True)
        if (length, width) != (1.0, 1.0):
            g = g.resize((round(g.width * width * SS), round(g.height * length * SS)), Image.LANCZOS)
            g = g.resize((round(g.width / SS), round(g.height / SS)), Image.LANCZOS)
        im = Image.new("L", (W, H), 0)
        im.paste(g, ((W - g.width) // 2, (H - g.height) // 2))
        px = im.load()
        out = bytearray(W * H // 8)
        for y in range(H):
            for x in range(W):
                if px[x, y] > 100:
                    i = y * W + x
                    out[i >> 3] |= 0x80 >> (i & 7)
        frames.append(base64.b64encode(bytes(out)).decode())
    return dict(fps=round(16 / 0.96), frames=frames)


ANIMS = {
    "gem": gem(),
    "gem-tall": gem(length=1.45, width=0.88),
    **{
        f"spin-{int(over * 100)}%-{turn}s": spin(over, turn, fps)
        for over in (0.15, 0.35)
        for turn, fps in ((6, 12), (15, 8), (30, 6))
    },
    "star": dict(fps=12, frames=one()),
    "star-thin": dict(fps=12, frames=one(stroke=1.2)),
    "star-drift": dict(fps=12, frames=drift()),
    "star-column": dict(fps=12, frames=column()),
    "blank": dict(fps=1, frames=[to_bits(canvas()[0])]),
}

out = pathlib.Path(__file__).with_name("frames.js")
out.write_text("window.ANIMS = " + json.dumps({"w": W, "h": H, "anims": ANIMS}) + ";\n")
print(f"{out}: " + ", ".join(f"{k} {len(v['frames'])}f" for k, v in ANIMS.items()))

# the board: baked frames go into oled/fw/frames.c, portrait-packed exactly as in frames.js
# (row-major 32x128, msb first). fw/screen.c turns them a quarter turn on the way to the panel.
FIRMWARE = {"column": "star-column", "gem": "gem"}

c = ["// generated by oled/gen.py, don't edit", "#include <stdint.h>", '#include "frames.h"', ""]
h = ["#pragma once", "#include <stdint.h>", ""]
for cname, aname in FIRMWARE.items():
    anim = ANIMS[aname]
    n = len(anim["frames"])
    h.append(f"#define {cname.upper()}_FRAMES {n}")
    h.append(f"#define {cname.upper()}_FRAME_MS {round(1000 / anim['fps'])}")
    h.append(f"extern const uint8_t {cname}_frames[{cname.upper()}_FRAMES][{W * H // 8}];")
    c.append(f"const uint8_t {cname}_frames[{cname.upper()}_FRAMES][{W * H // 8}] = {{")
    for fr in anim["frames"]:
        data = base64.b64decode(fr)
        c.append("    {")
        for j in range(0, len(data), 16):
            c.append("        " + ", ".join(f"0x{b:02x}" for b in data[j : j + 16]) + ",")
        c.append("    },")
    c.append("};")
    c.append("")

fw = pathlib.Path(__file__).resolve().parent / "fw"
(fw / "frames.c").write_text("\n".join(c))
(fw / "frames.h").write_text("\n".join(h) + "\n")
print(f"{fw}/frames.c: " + ", ".join(f"{k} <- {v}" for k, v in FIRMWARE.items()))
