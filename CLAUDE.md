# lily58-zmk

bekh's Lily58 keyboard config, and the Karabiner half that turns its QWERTY
scancodes into Gallium on the mac. Forked from mctechnology17's zmk-config, so
most of the tree (corne, sofle, dongles, `src/`, `snippets/`) is upstream
ballast. The parts that are actually ours are `config/lily58.keymap`,
`tools/zmkctl.py`, `stats/` and `docs/`.

This file is also the front door for any keyboard question on bekh's desk: the
global CLAUDE.md routes every session that touches keys, chords or bindings here.

## The chain, finger to action

1. **The board** (this repo): layers and hold-taps, emitting QWERTY scancodes,
   some of them baked chords. A chord nobody types by hand, only one seat
   sends, is a *wire*: ugly is fine there, and F13–F20 are the best wires.
2. **Karabiner** (`docs/karabiner.md`): turns those scancodes into Gallium,
   chords included, gated per device and by the `gallium_off` / `game`
   variables.
3. **shitd** (`~/tower/forge/hyprshit/config/keys`): the desk's global chords,
   heard on an HID tap *after* Gallium, so they name Gallium letters. Under
   secure input (a password field) the tap is blind and only its carbon twins
   fire.
4. **macOS and the apps**: their own hotkeys (iTerm's drop-down, the
   screenshots, mission control).
5. **The mini** takes the same board through keyd on Arch, which does its
   Gallium in `[main]` and its own `[fuck]` layer on held F20; anything bound
   on the mac may have a keyd or Hyprland twin there, kept by hand.

**`docs/chords.txt` is who holds what across 3 and 4** (`make chords`); grep it
before seating or binding anything. "hyper" means ctrl+alt+cmd+shift.

bekh's side of it: he reads and speaks Gallium, and with a modifier held the
keys are **still Gallium**, since Karabiner translates chords. His fingers
remember a Cyrillic-era habit of transposing to QWERTY under a modifier, so
when a chord he binds by name "doesn't fire", check the log for its Gallium
twin first: the physical E sends `d`, so alt-e landed on alt-d. A chord he
presses from muscle memory belongs on an F-key, which Gallium leaves alone.
Keyboard sessions start ad hoc, from whatever project he's in.

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
Killing Studio loses nothing, but **a Studio edit bekh hasn't saved lives
only in the board's RAM**: `dump`/`verify` read it as if it were real, and the
next reboot or flash drops it back to the saved cell (FUCK+e went that way).
When `verify` finds drift right before a flash, fold it into the file *and*
re-set it with `zmkctl` (which saves) before bekh double-taps.

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

## Adding a binding

bekh says the intent in his words ("put Finder on FUCK+e"). Then:

1. `grep` `docs/chords.txt` for the chord.
2. A line in hyprshit's `config/keys`, spelled with the Gallium letter:
   `alt-x …` for a Space chord, `fuck-x …` for a pinky one, `shit-x …` for
   an outer thumb. The board isn't
   touched. Only something no chord can reach gets a board seat (`zmkctl`,
   which saves), on an F-key.
3. `make chords`, and commit both repos.
4. Ask "mini too?": a fuck or shit chord there is a line in keyd's
   `[fuck]` / `[shit]` (`docs/layers.md`).

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
- **Which chords are taken** → `docs/chords.txt`: grep it before binding or
  seating any chord. Generated by `make chords` from hyprshit's keys, macOS's
  shortcuts (the untouched defaults too), iTerm's hotkey window and
  `docs/chords.hand`, the hand list for app hotkeys no script can read. Karabiner
  rules and the board's seats are not in it yet. Spelled as shitd hears it,
  after Gallium, so a letter there goes back through the table above before
  bekh presses it.
- **Russian and symbols** → `docs/musings_over_ru_layout.md`: before touching
  the number row or anything cross-language. Holds the custom ЙЦУКЕН
  `.keylayout`, built and never cut over. bekh barely uses Russian now.
- **Measurements** → `stats/keycount-2026-07.md`: when arguing a layout
  choice. Don't argue from feel.

## Resume pointer

Mirror is true (`verify` MATCH). Five layers: 0 `ground`, 1 `CURSE`,
2 `HEAVEN`, 3 `shit`, 4 `FUCK`. Space holds a real alt, HEAVEN is on Enter, CURSE is a dead slot.
Wired; Bluetooth isn't paired. **The pinkies hold F20, the outer thumbs F19**:
fuck and shit are shitd's own modifiers on the mac and keyd layers on the
mini; slots 3 and 4 are empty (`docs/layers.md`, which also has the F-row rule).

**Soaking: every door on hold-preferred, `mtp150`/`ltp150`.** Flashed and
bound; bekh's first pass says it works. What to watch, from `docs/board.md`:
a space after a pause rolling into an alt chord (→ `200`), a hotkey right
after typing coming out as a tap (→ `100`), `?`/`~` mid-word, FUCK runs
(l l l), quick-tap repeat. A week with neither misfire → it's the regime.

Next, each waiting on bekh's go:

- **The chord index learns the rest:** the board's seats joined to each chord
  (which board seat sends which chord), Karabiner's non-Gallium rules, and the mini
  (keyd + Hyprland binds over ssh) as a parity view of what has no twin there.
- **The chord cleanup:** one table of every multi-modifier chord; bekh calls
  each one a wire (keep, or move to an F-key) or a hand chord (rename to
  something natural now that alt is under the thumb). A talking session.

Open:

- **Not pressed through yet:** the Karabiner alt numpad, alt+`=` / alt+shift+`=` (shitd's launchers), every fuck
  and shit chord through the real board, mac and mini (only synthetic fuck-x
  and shit-x are seen firing; shit-x flipped caps). The alt on
  Space is in daily use (alt-w, alt-tab, alt-d in shitd's log).
- **F18 answers twice:** neru's hints and gamevoice's push-to-talk both bind
  bare F18 (`chords.txt` shows it as the one clash). Unless gamevoice only
  listens in games, one of them moves to F14–F17.
- Karabiner cleanup: the list is in `docs/karabiner.md`, waiting on bekh's picks.
- CURSE's slot is free for a new tenant; HEAVEN pos 2's stray `0xCE` is undecided.
- The Arch machine was wired against the old baked alt cells; its alt
  bindings need re-deriving from "hold Space + the key bekh calls X → alt+X".
- Parked, in bekh's words: alt+Z fullscreen sim, "think later".
