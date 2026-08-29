#!/usr/bin/env python3
"""zmkctl — talk to the Lily58 over ZMK Studio RPC (runtime, no flashing).

Usage:
  .venv/bin/python tools/zmkctl.py dump           # print all layers as grids
  .venv/bin/python tools/zmkctl.py get L POS      # read one key
  .venv/bin/python tools/zmkctl.py verify         # MATCH/MISMATCH vs the keymap file
  (set/save live in here too — used from sessions, see set_key/save)

The board must be free (ZMK Studio GUI disconnected) and unlocked.
Positions are keymap indices, row-major:
  0-11 num row | 12-23 top | 24-35 home | 36-49 bottom row incl. the two
  center keys at 42 (left) / 43 (right) | 50-57 thumbs.
"""

import sys

sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__file__), "..", ".venv", "lib", "python3.12", "site-packages"))
import zmk_studio_api as z

# The usbmodem node changes with the USB port/enumeration order, so a pinned
# path goes stale silently. Glob it; override with ZMKCTL_SERIAL if several
# CDC devices are plugged in.
import glob as _glob
import os as _os

_ports = sorted(_glob.glob("/dev/cu.usbmodem*"))
SERIAL = _os.environ.get("ZMKCTL_SERIAL") or (_ports[0] if _ports else "/dev/cu.usbmodem-none")

# HID usage page 7 -> readable label (the ones a Lily58 actually uses)
HID = {
    4: "A", 5: "B", 6: "C", 7: "D", 8: "E", 9: "F", 10: "G", 11: "H", 12: "I",
    13: "J", 14: "K", 15: "L", 16: "M", 17: "N", 18: "O", 19: "P", 20: "Q",
    21: "R", 22: "S", 23: "T", 24: "U", 25: "V", 26: "W", 27: "X", 28: "Y",
    29: "Z",
    30: "1", 31: "2", 32: "3", 33: "4", 34: "5", 35: "6", 36: "7", 37: "8",
    38: "9", 39: "0",
    40: "Ret", 41: "Esc", 42: "BkSp", 43: "Tab", 44: "Spc",
    45: "-", 46: "=", 47: "[", 48: "]", 49: "\\", 50: "#~", 51: ";", 52: "'",
    53: "`", 54: ",", 55: ".", 56: "/", 57: "Caps",
    58: "F1", 59: "F2", 60: "F3", 61: "F4", 62: "F5", 63: "F6", 64: "F7",
    65: "F8", 66: "F9", 67: "F10", 68: "F11", 69: "F12",
    74: "Home", 75: "PgUp", 76: "Del", 77: "End", 78: "PgDn",
    79: "→", 80: "←", 81: "↓", 82: "↑",
    224: "LCtl", 225: "LSft", 226: "LAlt", 227: "LGui",
    228: "RCtl", 229: "RSft", 230: "RAlt", 231: "RGui",
}

MODS = {1: "LC", 2: "LS", 4: "LA", 8: "LG", 16: "RC", 32: "RS", 64: "RA", 128: "RG"}


def label(behavior):
    s = str(behavior)
    if "NoBehavior" in s:
        return "✗"
    if "Transparent" in s:
        return "▽"
    if "KeyPress" in s:
        import re
        m = re.search(r"page: (\d+), id: (\d+), modifiers: (\d+)", s)
        if m:
            page, usage, mods = int(m.group(1)), int(m.group(2)), int(m.group(3))
            name = HID.get(usage, f"p{page}u{usage}")
            prefix = "+".join(v for k, v in MODS.items() if mods & k)
            return f"{prefix}({name})" if prefix else name
    if "MomentaryLayer" in s:
        import re
        m = re.search(r"MomentaryLayer.*?(\d+)", s)
        return f"mo{m.group(1)}" if m else "mo?"
    if "ToggleLayer" in s:
        import re
        m = re.search(r"ToggleLayer.*?(\d+)", s)
        return f"tog{m.group(1)}" if m else "tog?"
    if "LayerTap" in s or "ModTap" in s or "StickyLayer" in s or "CapsWord" in s:
        return s[:18]
    return s[:14]


# Lily58 keymap geometry: (row label, [positions left], [positions right])
ROWS = [
    ("num ", list(range(0, 6)), list(range(6, 12))),
    ("top ", list(range(12, 18)), list(range(18, 24))),
    ("home", list(range(24, 30)), list(range(30, 36))),
    ("bot ", list(range(36, 42)) + [42], [43] + list(range(44, 50))),
    ("thmb", list(range(50, 54)), list(range(54, 58))),
]


def connect():
    return z.StudioClient.open_serial(SERIAL)


def dump(client, max_layers=10):
    for layer in range(max_layers):
        try:
            cells = {}
            for _, left, right in ROWS:
                for pos in left + right:
                    cells[pos] = label(client.get_key_at(layer, pos))
        except Exception:
            break
        print(f"=== layer {layer} ===")
        for name, left, right in ROWS:
            l = " ".join(f"{cells[p]:>7}" for p in left)
            r = " ".join(f"{cells[p]:>7}" for p in right)
            print(f"{name} {l}   |   {r}")
        print()


def set_key(client, layer, pos, behavior):
    """behavior: a zmk_studio_api behavior object, e.g. z.KeyPress/z.MomentaryLayer."""
    client.set_key_at(layer, pos, behavior)


def save(client):
    client.save_changes()


# --- mirror verification -------------------------------------------------
# The keymap file is documentation until something proves it. Studio GUI edits
# never reach it, so drift is silent — and only bites on the day of a reflash,
# when the file becomes the source of truth. Compare numeric (page, id, mods),
# never display names: alias tables are how a diff quietly lies.

_LETTERS = {c: (7, 4 + i) for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
KEYCODES = dict(_LETTERS)
KEYCODES.update({f"N{d}": (7, 30 + (d - 1) % 10) for d in list(range(1, 10)) + [0]})
KEYCODES.update({f"F{n}": (7, 57 + n) for n in range(1, 13)})
KEYCODES.update({f"F{n}": (7, 104 + n - 13) for n in range(13, 25)})
KEYCODES.update({
    "RET": (7, 40), "ESC": (7, 41), "BSPC": (7, 42), "TAB": (7, 43), "SPACE": (7, 44),
    "MINUS": (7, 45), "EQUAL": (7, 46), "LBKT": (7, 47), "RBKT": (7, 48), "BSLH": (7, 49),
    "SEMI": (7, 51), "SQT": (7, 52), "GRAVE": (7, 53), "COMMA": (7, 54), "DOT": (7, 55),
    "FSLH": (7, 56), "CAPS": (7, 57), "DEL": (7, 76),
    "RIGHT": (7, 79), "LEFT": (7, 80), "DOWN": (7, 81), "UP": (7, 82),
    "KP_PLUS": (7, 87), "KP_DOT": (7, 99),
    "LCTRL": (7, 224), "LSHFT": (7, 225), "LALT": (7, 226), "LGUI": (7, 227),
    "RCTRL": (7, 228), "RSHFT": (7, 229), "RALT": (7, 230), "RGUI": (7, 231),
    "C_BRI_UP": (12, 111), "C_BRI_DN": (12, 112), "C_FF": (12, 179), "C_RW": (12, 180),
    "C_PP": (12, 205), "C_MUTE": (12, 226), "C_VOL_UP": (12, 233), "C_VOL_DN": (12, 234),
})
MODBIT = {"LC": 1, "LS": 2, "LA": 4, "LG": 8, "RC": 16, "RS": 32, "RA": 64, "RG": 128}


def cell_from_token(t):
    import re
    t = t.strip()
    if t == "&trans":
        return ("trans",)
    if t == "&none":
        return ("none",)
    for name, kind in (("&mo ", "mo"), ("&tog ", "tog")):
        m = re.match(re.escape(name) + r"(\d+)$", t)
        if m:
            return (kind, int(m.group(1)))
    if t.startswith("&bt"):
        return ("bt",)
    m = re.match(r"&kp (.+)$", t)
    if m:
        arg, mods = m.group(1).strip(), 0
        while True:
            mm = re.match(r"^(LC|LS|LA|LG|RC|RS|RA|RG)\((.*)\)$", arg)
            if not mm:
                break
            mods |= MODBIT[mm.group(1)]
            arg = mm.group(2).strip()
        if arg.startswith("0x"):
            v = int(arg, 16)
            return ("kp", (v >> 16) & 0xFF, v & 0xFFFF, mods)
        if arg in KEYCODES:
            return ("kp",) + KEYCODES[arg] + (mods,)
        return ("UNKNOWN-NAME", arg)
    return ("other", t)


def cell_from_board(b):
    import re
    s = str(b)
    if "Transparent" in s:
        return ("trans",)
    if "NoBehavior" in s or "Behavior(None" in s:
        return ("none",)
    if "KeyPress" in s:
        m = re.search(r"page: (\d+), id: (\d+), modifiers: (\d+)", s)
        if m:
            return ("kp", int(m.group(1)), int(m.group(2)), int(m.group(3)))
    for needle, kind in (("MomentaryLayer", "mo"), ("ToggleLayer", "tog")):
        if needle in s:
            m = re.search(r"(\d+)", s)
            return (kind, int(m.group(1))) if m else (kind, None)
    if "Bluetooth" in s:
        return ("bt",)
    return ("other", s[:40])


def verify(client, keymap_path="config/lily58.keymap"):
    """Verdict-only: MATCH means the file is a true mirror of the board."""
    import re
    src = open(keymap_path).read()
    blocks = re.findall(r"bindings = <\n(.*?)>;", src, re.S)
    bad = 0
    for layer, block in enumerate(blocks):
        toks = ["&" + p.strip() for p in re.sub(r"//.*", "", block).split("&")[1:]]
        if len(toks) != 58:
            print(f"L{layer}: parsed {len(toks)} bindings, expected 58 — CANNOT VERIFY")
            bad += 1
            continue
        for pos in range(58):
            want = cell_from_token(toks[pos])
            got = cell_from_board(client.get_key_at(layer, pos))
            if want != got:
                bad += 1
                print(f"L{layer} pos {pos:2d}  file {want}  board {got}   {toks[pos]}")
    print("MATCH — mirror is true" if bad == 0 else f"MISMATCH — {bad} cells")
    return bad == 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "dump"
    c = connect()
    if cmd == "dump":
        dump(c)
    elif cmd == "verify":
        sys.exit(0 if verify(c) else 1)
    elif cmd == "get":
        print(c.get_key_at(int(sys.argv[2]), int(sys.argv[3])))
    else:
        print(f"unknown command: {cmd}")
