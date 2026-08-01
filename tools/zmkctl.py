#!/usr/bin/env python3
"""zmkctl — talk to the Lily58 over ZMK Studio RPC (runtime, no flashing).

Usage:
  .venv/bin/python tools/zmkctl.py dump           # print all layers as grids
  .venv/bin/python tools/zmkctl.py get L POS      # read one key
  (set/save live in here too — used from sessions, see set_key/save)

The board must be free (ZMK Studio GUI disconnected) and unlocked.
Positions are keymap indices, row-major:
  0-11 num row | 12-23 top | 24-35 home | 36-49 bottom row incl. the two
  center keys at 42 (left) / 43 (right) | 50-57 thumbs.
"""

import sys

sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__file__), "..", ".venv", "lib", "python3.12", "site-packages"))
import zmk_studio_api as z

SERIAL = "/dev/cu.usbmodem21201"

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
        m = re.search(r"MomentaryLayer\((\d+)\)", s)
        return f"mo{m.group(1)}" if m else "mo?"
    if "ToggleLayer" in s:
        import re
        m = re.search(r"ToggleLayer\((\d+)\)", s)
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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "dump"
    c = connect()
    if cmd == "dump":
        dump(c)
    elif cmd == "get":
        print(c.get_key_at(int(sys.argv[2]), int(sys.argv[3])))
    else:
        print(f"unknown command: {cmd}")
