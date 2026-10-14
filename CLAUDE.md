# lily58-zmk

bekh's Lily58 keyboard config, and the Karabiner half that turns its QWERTY
scancodes into Gallium on the mac. Forked from mctechnology17's zmk-config, so
most of the tree (corne, sofle, dongles, `src/`, `snippets/`) is upstream
ballast. The parts that are actually ours are `config/lily58.keymap`,
`tools/zmkctl.py`, `stats/` and `docs/`.

## The one thing to understand first

**The board is the source of truth, not this repo.** The live keymap lives in
ZMK Studio's flash settings on the board, and Studio's saved state overrides
the keymap file, even after a reflash. `config/lily58.keymap` is a mirror kept
by hand, and a Studio GUI edit never reaches it.

**Working order, every session: dump the board → change the board → bring the
file up to it → `verify`.** bekh edits in Studio between sessions and during
them, so the keymap file and these docs are stale by default. Whatever drift
`verify` finds is bekh's edits, not noise: fold it in.

```bash
.venv/bin/python tools/zmkctl.py dump      # all layers as grids
.venv/bin/python tools/zmkctl.py verify    # MATCH = the mirror is true
```

Layer content is always runtime (RPC, seconds). Only a genuinely new behavior
needs a build and a flash, and that path is in `docs/board.md`.

## Setup

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python zmk-studio-api
```

Left half on USB (only the central exposes the port). **ZMK Studio's GUI holds
the port exclusively and relaunches itself to grab it again. Standing
authorization: kill it, don't ask, before every `zmkctl` call:**

```bash
P=$(lsof -t /dev/tty.usbmodem* 2>/dev/null | head -1); [ -n "$P" ] && kill $P
```

Kill by the PID, never `pkill -f zmk`: the shell matches its own pattern.
Studio writes every edit straight to the board, so there's nothing unsaved to
lose.

## Two alphabets

Karabiner rules, `config/lily58.keymap` and every `zmkctl dump` are QWERTY
scancodes. Karabiner turns them into Gallium, and bekh reads and speaks
Gallium. **Never tell bekh a key by its name in the file: translate**, or bekh
presses the wrong key and a correct binding looks broken.

| file / karabiner | q w e r t | y u i o p | a s d f g | h j k l ; | z x c v b | n m , . / |
|---|---|---|---|---|---|---|
| **what bekh presses** | b l d c v | j y o u , | n r t s g | p h a e i | x q m w z | k f ' ; . |

Digits, number-row symbols, modifiers and thumbs are the same in both.
**Chords go through the table too**: Karabiner translates cmd, ctrl and alt
chords, baked or held. So a cell `LA(LG(C))` is alt+cmd+m. Keypad and arrows
read literally.

## Map

- **Working the board** → `docs/board.md`: before any RPC edit, build, flash,
  settings wipe or keymap push. Holds the hold-tap ladders, the hex chord
  encoding, the Studio/api traps and the keymap-drawer force-push dance.
- **Karabiner** → `docs/karabiner.md`: before touching any rule, or deciding
  whether something belongs on the board or in macOS. Karabiner is a git repo
  in place, and the agent commits after every edit.
- **The layers** → `docs/layers.md`: before seating anything. What's on each
  layer, where the doors are, and the rule that decides seats (the right hand
  is on the mouse; left hand only).
- **Thumbs and holds** → `docs/dual-role-thumbs.md`: before putting a hold on
  any key or retuning a term. Mechanism limits, keypress measurements, why
  the thumb row is what it is.
- **Russian and symbols** → `docs/musings_over_ru_layout.md`: before touching
  the number row or anything cross-language. Holds the custom ЙЦУКЕН
  `.keylayout`, built and never cut over. bekh barely uses Russian now.
- **Measurements** → `stats/keycount-2026-07.md`: when arguing a layout
  choice. Don't argue from feel.

## Resume pointer

Mirror is true (`verify` MATCH). Five layers: 0 `ground`, 1 `CURSE`,
2 `HEAVEN`, 3 `shit`, 4 `FUCK`. Space holds a real alt; shit is on both outer
thumbs, FUCK on both home-row pinkies, HEAVEN on Enter, CURSE is a dead slot.
Wired; Bluetooth isn't paired.

Open:

- **Not pressed through yet:** the real alt on Space, the Karabiner alt numpad,
  alt+`=`, CAPS on shit, shit+m → hyprshit's mode. All verified only by
  `verify` and Karabiner's reload.
- Space at 280: vanishing spaces or rolls turning into alt chords → a rung up.
- Karabiner cleanup: the list is in `docs/karabiner.md`, waiting on bekh's picks.
- CURSE's slot is free for a new tenant; HEAVEN pos 2's stray `0xCE` is undecided.
- The Arch machine was wired against the old baked alt cells; its alt
  bindings need re-deriving from "hold Space + the key bekh calls X → alt+X".
- Parked, in bekh's words: alt+Z fullscreen sim, "think later".
