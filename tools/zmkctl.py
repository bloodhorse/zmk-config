#!/usr/bin/env python3
"""zmkctl — talk to the Lily58 over ZMK Studio RPC (runtime, no flashing).

Usage:
  .venv/bin/python tools/zmkctl.py dump           # print all layers as grids
  .venv/bin/python tools/zmkctl.py get L POS      # read one key
  .venv/bin/python tools/zmkctl.py verify         # MATCH/MISMATCH vs the keymap file
  .venv/bin/python tools/zmkctl.py behaviors      # id + node name of every behavior on the board
  .venv/bin/python tools/zmkctl.py set L POS NODE_NAME P1 P2   # bind custom behavior + save
      e.g. set 0 53 layer_tap_balanced_320 1 SPACE   (tune the Space hold term)

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
    # Layer ids can have holes: deleting a layer in Studio retires its id for
    # good (media was id 3), so a failed id means skip, never stop.
    for layer in range(max_layers):
        try:
            cells = {}
            for _, left, right in ROWS:
                for pos in left + right:
                    cells[pos] = label(client.get_key_at(layer, pos))
        except Exception:
            continue
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


# --- behavior directory --------------------------------------------------
# Behavior ids are assigned by devicetree order and shift when nodes are
# added or removed, so nothing may hardcode them: resolve by display name,
# per connection, every time.

def _details_name(data):
    """display_name out of a GetBehaviorDetailsResponse (field 2, length-delimited)."""
    i = 0
    while i < len(data):
        tag = data[i]; i += 1
        field, wt = tag >> 3, tag & 7
        if wt == 0:
            while data[i] & 0x80:
                i += 1
            i += 1
        elif wt == 2:
            ln = data[i]; i += 1
            if field == 2:
                return data[i:i + ln].decode()
            i += ln
        else:
            break
    return "?"


def behaviors(client):
    for bid in sorted(client.list_all_behaviors()):
        name = _details_name(bytes(client.get_behavior_details_bytes(bid)))
        print(f"{bid:3d}  {name}")


def behavior_id(client, name):
    for bid in client.list_all_behaviors():
        if _details_name(bytes(client.get_behavior_details_bytes(bid))) == name:
            return bid
    raise SystemExit(f"no behavior named {name!r} on the board — try 'behaviors'")


def _param2(token):
    """keycode name / 0xPPPPII raw usage / plain int -> u32 param."""
    if token in KEYCODES:
        page, kid = KEYCODES[token]
        return (page << 16) | kid
    return int(token, 0)


def set_kp(client, layer, pos, name):
    """Bind a plain &kp by ZMK keycode name and save.

    zmkctl kp L POS NAME   e.g. kp 0 4 GRAV / kp 0 3 DQT / kp 0 1 0x2070032
    NAME is a zmk_studio_api.Keycode member (ZMK's own spelling: GRAV, TILD,
    APOSTROPHE, DQT, LPAR, LBRC, BSLH, PIPE …) or a raw 0xMMPPIIII value —
    modifiers ride in the top byte, so shifted symbols are one keycode.
    """
    kc = z.Keycode(int(name, 0)) if name.startswith("0x") else getattr(z.Keycode, name, None)
    if kc is None:
        raise SystemExit(f"unknown keycode {name!r} — see dir(zmk_studio_api.Keycode)")
    client.set_key_at(layer, pos, z.KeyPress(kc))
    client.save_changes()
    print(client.get_key_at(layer, pos))


def set_custom(client, layer, pos, name, p1, p2):
    """Bind a custom (devicetree) behavior by display name and save.

    zmkctl set L POS NODE_NAME PARAM1 PARAM2
      e.g. set 0 53 layer_tap_balanced_280 1 SPACE
    NODE_NAME is the devicetree node name (what 'behaviors' prints), not the
    &label. PARAM2 takes a keycode name from KEYCODES, 0x-hex, or an int.
    """
    bid = behavior_id(client, name)
    client.set_key_at(layer, pos, z.Raw(bid, int(p1), _param2(p2)))
    client.save_changes()
    print(client.get_key_at(layer, pos))


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
    m = re.match(r"&([a-z_][a-z_0-9]*) (\d+) (.+)$", t)
    if m and m.group(1) not in ("lt", "mt", "mo", "tog", "kp", "bt"):
        cell = cell_from_token("&kp " + m.group(3).strip())
        return ("custom", m.group(1), int(m.group(2))) + cell[1:]
    m = re.match(r"&(lt|mt) (\S+) (.+)$", t)
    if m:
        kind, first, tap = m.group(1), m.group(2), m.group(3).strip()
        held = int(first) if kind == "lt" else KEYCODES.get(first, first)
        cell = cell_from_token("&kp " + tap)
        return (kind, held) + cell[1:]
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
    m = re.search(r'Custom \{ behavior_id: \d+, display_name: "([a-z_0-9]+)", param1: LayerId\((\d+)\), '
                  r'param2: Keycode\(HidUsage \{ page: (\d+), id: (\d+), modifiers: (\d+)', s)
    if m:
        return ("custom", m.group(1)) + tuple(int(g) for g in m.groups()[1:])
    m = re.search(r"LayerTap \{ layer_id: (\d+), tap: HidUsage \{ page: (\d+), id: (\d+), modifiers: (\d+)", s)
    if m:
        return ("lt",) + tuple(int(g) for g in m.groups())
    m = re.search(r"ModTap \{ hold: HidUsage \{ page: (\d+), id: (\d+), modifiers: (\d+) \}, tap: HidUsage \{ page: (\d+), id: (\d+), modifiers: (\d+)", s)
    if m:
        g = [int(x) for x in m.groups()]
        return ("mt", (g[0], g[1])) + tuple(g[3:])
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
    # devicetree label vs node name: the keymap binds &lt_curse, the board
    # reports "layer_tap_curse". Same behavior, two names — resolve the label.
    labels = dict(re.findall(r"^\s*([a-z_][a-z_0-9]*):\s*([a-z_][a-z_0-9]*)\s*\{", src, re.M))
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
            if want[0] == "custom":
                want = (want[0], labels.get(want[1], want[1])) + want[2:]
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
    elif cmd == "behaviors":
        behaviors(c)
    elif cmd == "kp":
        set_kp(c, int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "set":
        set_custom(c, int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6])
    else:
        print(f"unknown command: {cmd}")
