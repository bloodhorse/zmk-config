#!/usr/bin/env python3
"""Every global chord on the desk in one flat index: docs/chords.txt.

Sources: hyprshit's keys, macOS's own shortcuts, iTerm's hotkey window, and
docs/chords.hand for the claims no script can see. Chords are spelled the way
shitd spells them (alt-ctrl-shift-cmd-<key>), keys as the US layout types them,
which is what everything after Karabiner's Gallium remap sees.
"""
import os
import plistlib
import subprocess
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/chords.txt"
HAND = ROOT / "docs/chords.hand"
HYPRSHIT_KEYS = Path.home() / ".config/hyprshit/keys"

MODS = ["fuck", "alt", "ctrl", "shift", "cmd"]
FKEYS = [f"f{n}" for n in range(13, 21)]

KEYCODES = {
    0: "a", 1: "s", 2: "d", 3: "f", 4: "h", 5: "g", 6: "z", 7: "x", 8: "c", 9: "v",
    11: "b", 12: "q", 13: "w", 14: "e", 15: "r", 16: "y", 17: "t", 18: "1", 19: "2",
    20: "3", 21: "4", 22: "6", 23: "5", 24: "=", 25: "9", 26: "7", 27: "-", 28: "8",
    29: "0", 30: "]", 31: "o", 32: "u", 33: "[", 34: "i", 35: "p", 36: "return",
    37: "l", 38: "j", 39: "'", 40: "k", 41: ";", 42: "\\", 43: ",", 44: "/", 45: "n",
    46: "m", 47: ".", 48: "tab", 49: "space", 50: "`", 51: "delete", 53: "esc",
    71: "clear", 115: "home", 116: "pageup", 117: "fdelete", 119: "end", 121: "pagedown",
    123: "left", 124: "right", 125: "down", 126: "up",
    122: "f1", 120: "f2", 99: "f3", 118: "f4", 96: "f5", 97: "f6", 98: "f7", 100: "f8",
    101: "f9", 109: "f10", 103: "f11", 111: "f12", 105: "f13", 107: "f14", 113: "f15",
    106: "f16", 64: "f17", 79: "f18", 80: "f19", 90: "f20",
}
COCOA_MODS = {"shift": 1 << 17, "ctrl": 1 << 18, "alt": 1 << 19, "cmd": 1 << 20}
COCOA_FN = 1 << 23

MACOS_NAMES = {
    7: "focus menu bar", 8: "focus dock", 9: "focus active window", 10: "focus toolbar",
    11: "focus floating window", 13: "change tab focus", 27: "next window",
    28: "screenshot to file", 29: "screenshot to clipboard", 30: "area screenshot to file",
    31: "area screenshot to clipboard", 32: "mission control", 33: "app windows",
    36: "show desktop", 52: "dock hiding", 57: "focus status menus", 59: "voiceover",
    60: "previous input source", 61: "next input source", 64: "spotlight",
    65: "finder search", 79: "space left", 81: "space right", 160: "launchpad",
    162: "accessibility shortcuts", 163: "notification center", 175: "do not disturb",
    184: "screenshot options", 190: "quick note", 222: "stage manager",
    **{118 + i: f"desktop {i + 1}" for i in range(16)},
}
# an id missing from the plist was never touched, so macOS's own default is live
MACOS_DEFAULTS = {
    27: "cmd-`", 28: "shift-cmd-3", 29: "ctrl-shift-cmd-3", 31: "ctrl-shift-cmd-4",
    32: "ctrl-up", 33: "ctrl-down", 36: "f11", 64: "cmd-space", 65: "alt-cmd-space",
    184: "shift-cmd-5", 190: "fn-q",
}


def spell(mods, key, fn=False):
    return ("fn-" if fn else "") + "".join(m + "-" for m in MODS if m in mods) + key


def parse(text):
    """'ctrl--' → ({'ctrl'}, '-'), 'alt-shift-f18' → ({'alt','shift'}, 'f18')."""
    parts = text.split("-")
    if parts[-1] == "" and len(parts) > 1:
        parts = parts[:-2] + ["-"]
    mods = {p for p in parts[:-1] if p}
    fn = "fn" in mods
    mods.discard("fn")
    return mods, parts[-1], fn


def hyprshit():
    claims = []
    for line in HYPRSHIT_KEYS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        words = line.split(None, 2)
        if words[0] == "hold" and len(words) > 2:
            claims.append((words[2], "hyprshit", f"held as {words[1]} (eaten, a modifier of ours)"))
        elif words[0] == "mode" and len(words) > 2:
            mods, key, _ = parse(words[1])
            claims.append(("mode " + spell(mods, key), "hyprshit", words[2]))
        elif len(words) > 1:
            mods, key, _ = parse(words[0])
            claims.append((spell(mods, key), "hyprshit", line.split(None, 1)[1]))
    return claims


def cocoa(keycode, flags):
    key = KEYCODES.get(keycode, f"key{keycode}")
    return spell({m for m, b in COCOA_MODS.items() if flags & b}, key, bool(flags & COCOA_FN))


def plist(domain):
    xml = subprocess.run(["defaults", "export", domain, "-"], capture_output=True).stdout
    # the xml can carry raw control characters (iTerm's "HotKey Characters"), which expat refuses
    out = subprocess.run(["plutil", "-convert", "binary1", "-o", "-", "-"], input=xml, capture_output=True).stdout
    return plistlib.loads(out) if out else {}


def macos():
    claims = []
    keys = plist("com.apple.symbolichotkeys").get("AppleSymbolicHotKeys", {})
    for sid, v in keys.items():
        params = v.get("value", {}).get("parameters", [])
        if not v.get("enabled") or len(params) != 3 or params[1] == 65535:
            continue
        name = MACOS_NAMES.get(int(sid)) or ("window tiling" if 235 <= int(sid) <= 260 else "")
        claims.append((cocoa(params[1], params[2]), "macos", f"{name} #{sid}".strip()))
    for sid, chord in MACOS_DEFAULTS.items():
        if str(sid) not in keys:
            mods, key, fn = parse(chord)
            claims.append((spell(mods, key, fn), "macos", f"{MACOS_NAMES[sid]} #{sid} (default)"))
    return claims


def iterm():
    claims = []
    for p in plist("com.googlecode.iterm2").get("New Bookmarks", []):
        if p.get("Has Hotkey"):
            claims.append((cocoa(p["HotKey Key Code"], p["HotKey Modifier Flags"]), "iterm",
                           f"hotkey window ({p.get('Name', '?')})"))
    return claims


def hand():
    claims = []
    if HAND.exists():
        for line in HAND.read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                chord, owner, what = (line.split(None, 2) + ["", ""])[:3]
                mods, key, fn = parse(chord)
                claims.append((spell(mods, key, fn), owner, what))
    return claims


def bare(chord):
    """The chord as shitd hears it: fn is ignored."""
    return chord.removeprefix("fn-")


def keyof(chord):
    return parse(bare(chord))[1]


def main():
    claims = hyprshit() + macos() + iterm() + hand()
    owners = defaultdict(set)
    for chord, owner, _ in claims:
        owners[bare(chord)].add((owner, _))
    clash = {c for c, o in owners.items() if len(o) > 1}

    def order(c):
        mods, key, fn = parse(c[0].removeprefix("mode "))
        return (key, len(mods), spell(mods, key), fn)

    def rows(sel):
        return [("!! " if bare(c) in clash else "   ") + f"{c:<26}{o:<10}{w}"
                for c, o, w in sorted(sel, key=order)]

    glob = [c for c in claims if not c[0].startswith("mode ")]
    fk = [c for c in glob if keyof(c[0]) in FKEYS]
    rest = [c for c in glob if keyof(c[0]) not in FKEYS]
    mode = [c for c in claims if c[0].startswith("mode ")]

    real = [m for m in MODS if m != "fuck"]
    combos = [set(s) for n in range(len(real) + 1) for s in combinations(real, n)]
    free = []
    held = {c for c, _, w in claims if w.startswith("held as")}
    for f in FKEYS:
        if f in held:
            free.append(f"   {f:<5}none: held as a modifier, every chord on it is eaten")
            continue
        open_ = [spell(m, "") or "bare" for m in combos if spell(m, f) not in owners]
        free.append(f"   {f:<5}" + " ".join(s.rstrip("-") for s in open_))

    lines = [
        "# generated by tools/chords.py (`make chords`): don't edit, hand claims go in docs/chords.hand",
        "# spelled as shitd hears it, after Gallium. !! = two claims on one chord. fn is ignored when matching.",
        "",
        "## f-keys",
        *rows(fk),
        "",
        "## free f-seats (modifier sets nobody holds; f21+ do not exist on macOS)",
        *free,
        "",
        "## everything else",
        *rows(rest),
        "",
        "## inside hyprshit's mode (only after the mode chord)",
        *rows(mode),
    ]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"{OUT.relative_to(ROOT)}: {len(claims)} claims, {len(clash)} clashes")


if __name__ == "__main__":
    main()
