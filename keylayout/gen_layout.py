#!/usr/bin/env python3
"""Generate RussianWinPlus.bundle — Apple's "Russian - PC" with a small delta.

Run from the repo root with the project venv:

    .venv/bin/python keylayout/gen_layout.py

The base is not a hand-copied file: it is a fresh dump of the RussianWin layout
that is installed on THIS Mac, taken through UCKeyTranslate for all 128 virtual
keycodes x 32 modifier states (keylayout/dumplayout.swift). Everything DELTA
does not name is emitted byte-for-byte as Apple has it, so the delta below is
the entire design and the only thing worth reading.

Why a custom layout at all: the board sends scancodes and macOS picks the glyph
per input source, so the same key types '@' in English and '"' in Russian.
bekh's hands cannot track a key that changes meaning with the language. See
docs/musings_over_ru_layout.md for the arithmetic of what can and cannot be made
uniform; the short version is that letters are untouchable and everything else
either rides the keypad page, a Karabiner borrow, or a spare keycode.
"""
import json
import os
import subprocess
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_ID = "com.apple.keylayout.RussianWin"
NAME = "RussianWinPlus"                       # keylayout name attr, bundle file names, KLInfo_ key
DISPLAY = "Russian – PC+"                     # what the input-source menu shows
SOURCE_ID = "org.bekh.keylayout.RussianWinPlus"   # keep "Russian" in it: ru_border greps for that
LAYOUT_ID = -25107                            # any unique negative; collisions only matter between installed layouts

# --- THE DELTA -----------------------------------------------------------
# (keycode, predicate over the modifier-state name) -> output
# "plain" states = no option, no command, no control. Shift and caps are allowed,
# which is what makes shift+digit land in every plain typing situation.
def plain(state):
    return not any(m in state for m in ("anyOption", "command", "anyControl"))

def shifted(state):
    return "anyShift" in state and plain(state)

DELTA = [
    # 1. shift+digit = the English symbol. Casualties: RU " (shift+2), № (shift+3,
    #    zero presses in the July ledger), ; (shift+4), : (shift+6), ? (shift+7).
    #    ! % * ( ) already agreed. The casualties that matter come back on spares below.
    (19, shifted, "@"),
    (20, shifted, "#"),
    (21, shifted, "$"),
    (22, shifted, "^"),
    (26, shifted, "&"),
    # 2. keypad '.' — RussianWin maps it to ',' (the Russian decimal comma), so
    #    HEAVEN's KP_DOT thumb typed a comma in Russian. The keypad page is
    #    supposed to be the language-independent one; make it so.
    (65, lambda s: True, "."),
    # 3. spares: keycodes no key on the board sends by default and that mean nothing
    #    useful in either layout. The board sends the HID usage on a layer, this file
    #    gives it a Russian meaning, and an EN-gated Karabiner rule gives it the same
    #    meaning under ABC. The pair is what makes the symbol uniform.
    #      keycode  HID usage (ZMK name)     RU here   EN via Karabiner
    (94, plain, "?"),   # INT_RO     0x87                ?         shift+slash
    (93, plain, ":"),   # INT_YEN    0x89                :         shift+semicolon
    (95, plain, '"'),   # KP_COMMA   0x85                "         shift+quote
    (10, plain, ";"),   # NON_US_BSLH 0x64               ;         semicolon
    # Not in the delta on purpose: backtick (keycode 50 stays ё — bekh parked it),
    # brackets (х ъ ж э are live letters; bekh dropped the brackets instead).
]

# --- dump the base --------------------------------------------------------
def dump(source_id):
    exe = os.path.join(HERE, "dumplayout")
    src = os.path.join(HERE, "dumplayout.swift")
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(src):
        subprocess.run(["swiftc", "-O", "-o", exe, src], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = subprocess.run([exe, source_id, "full"], check=True, capture_output=True, text=True).stdout
    rows = json.loads(out)
    states = [k for k in rows[0] if k != "code"]
    table = {r["code"]: {s: r[s] for s in states} for r in rows}
    return states, table

# --- build ----------------------------------------------------------------
def apply_delta(table, states):
    for code, pred, out in DELTA:
        for s in states:
            if pred(s):
                table[code][s] = out
    return table

def xml_escape_char(ch):
    o = ord(ch)
    if ch.isalnum() and o < 0x80:
        return ch
    return f"&#x{o:04X};"

def build_keylayout(table, states):
    # Dedupe identical per-state tables so the file stays readable: one keyMap per
    # distinct column, and every modifier combo that maps to it listed under it.
    columns = OrderedDict()
    for s in states:
        col = tuple(table[c][s] for c in range(128))
        columns.setdefault(col, []).append(s)
    # index 0 must be the unmodified state
    ordered = sorted(columns.items(), key=lambda kv: ("" not in kv[1], states.index(kv[1][0])))
    lines = []
    lines.append('<?xml version="1.1" encoding="UTF-8"?>')
    lines.append('<!DOCTYPE keyboard SYSTEM "file://localhost/System/Library/DTDs/KeyboardLayout.dtd">')
    lines.append(f'<keyboard group="126" id="{LAYOUT_ID}" name="{NAME}" maxout="1">')
    lines.append('  <layouts>')
    lines.append('    <layout first="0" last="255" mapSet="ANSI" modifiers="Modifiers"/>')
    lines.append('  </layouts>')
    lines.append('  <modifierMap id="Modifiers" defaultIndex="0">')
    for idx, (_, names) in enumerate(ordered):
        lines.append(f'    <keyMapSelect mapIndex="{idx}">')
        for n in names:
            lines.append(f'      <modifier keys="{n}"/>')
        lines.append('    </keyMapSelect>')
    lines.append('  </modifierMap>')
    lines.append('  <keyMapSet id="ANSI">')
    for idx, (col, names) in enumerate(ordered):
        lines.append(f'    <keyMap index="{idx}">  <!-- {" | ".join(n or "(none)" for n in names)} -->')
        for code, out in enumerate(col):
            if out == "":
                continue
            lines.append(f'      <key code="{code}" output="{"".join(xml_escape_char(c) for c in out)}"/>')
        lines.append('    </keyMap>')
    lines.append('  </keyMapSet>')
    lines.append('</keyboard>')
    return "\n".join(lines) + "\n"

INFO_PLIST = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>{SOURCE_ID}</string>
	<key>CFBundleName</key>
	<string>{NAME}</string>
	<key>CFBundleVersion</key>
	<string>1.0</string>
	<key>KLInfo_{NAME}</key>
	<dict>
		<key>TISInputSourceID</key>
		<string>{SOURCE_ID}</string>
		<key>TISIntendedLanguage</key>
		<string>ru</string>
	</dict>
</dict>
</plist>
"""

def write_bundle(xml):
    bundle = os.path.join(HERE, f"{NAME}.bundle")
    res = os.path.join(bundle, "Contents", "Resources")
    os.makedirs(os.path.join(res, "en.lproj"), exist_ok=True)
    with open(os.path.join(bundle, "Contents", "Info.plist"), "w") as f:
        f.write(INFO_PLIST)
    with open(os.path.join(res, f"{NAME}.keylayout"), "w") as f:
        f.write(xml)
    with open(os.path.join(res, "en.lproj", "InfoPlist.strings"), "w") as f:
        f.write(f'"{NAME}" = "{DISPLAY}";\n')
    return bundle

def main():
    states, base = dump(BASE_ID)
    before = {c: dict(v) for c, v in base.items()}
    table = apply_delta(base, states)
    xml = build_keylayout(table, states)
    bundle = write_bundle(xml)
    # expected.json is what verify.sh diffs the INSTALLED layout against
    with open(os.path.join(HERE, "expected.json"), "w") as f:
        json.dump([{"code": c, **table[c]} for c in range(128)], f, ensure_ascii=False, sort_keys=True)
    changed = sum(1 for c in range(128) for s in states if before[c][s] != table[c][s])
    print(f"wrote {bundle}")
    print(f"{changed} (keycode, state) cells differ from {BASE_ID}; everything else is Apple's, verbatim")

if __name__ == "__main__":
    main()
