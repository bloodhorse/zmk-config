# lily58-zmk

bekh's Lily58 keyboard config. Forked from mctechnology17's zmk-config, so most
of the tree (corne, sofle, dongles, `src/`, `snippets/`) is upstream ballast —
the parts that are actually ours are `config/lily58.keymap`, `tools/zmkctl.py`,
`stats/`, and `docs/`.

## The one thing to understand first

**The board is the source of truth, not this repo.** The live keymap lives in
ZMK Studio's flash settings on the board itself, and Studio's saved state
*overrides* the keymap file's defaults — including right after a reflash.
`config/lily58.keymap` is a mirror kept by hand.

That means edits go one of two ways:

- **runtime** (`&kp`, `&mo`, layer-taps that already exist) — set over Studio
  RPC with `tools/zmkctl.py`, live in seconds, revert in seconds
- **new behaviors and conditional layers** (a mod-morph, a hold-tap with a
  custom flavor, a tri-layer node) — those must be compiled in, so: edit the
  keymap → push → GitHub Actions builds → flash both halves → **then bind over
  RPC** where a binding changed (a conditional_layers node needs no rebinding —
  it lives in firmware, not settings)

Layer *content* is always runtime. The hold-taps are ladders — `ltb` (layer
hold, balanced, five terms) for Enter and the FUCK doors, `mtb` (alt hold,
balanced, 240/280/320) for Space — so tuning a hold term is rebinding the key
to another rung over RPC; only a genuinely new behavior needs a build.

Studio's saved state only holds cells that were edited. A cell nobody touched
follows the firmware default, so after a flash it takes the new keymap value
with no RPC at all — "bind over RPC" is only needed where the cell had been
edited before. New behaviors appended at the end of the `behaviors` block left
every saved binding intact (verified by `verify` after the 2026-10-14 flash);
pruning or reordering is still what shifts ids.

Flashing: only the left half (central) exposes Studio's serial port, so all
`zmkctl` work happens with the left half on USB. The bootloader mounts as
`/Volumes/NICENANO`; a background loop that waits for it and copies
`lily58_{left,right}_nice_oled.uf2` in turn lets bekh just double-tap.

After anything, run the checker:

```bash
.venv/bin/python tools/zmkctl.py verify      # MATCH — mirror is true
.venv/bin/python tools/zmkctl.py dump        # all layers as grids
```

`verify` compares all 58 positions on every bound layer as numeric
`(page, id, mods)`, never display names. It is what makes a reflash safe: if the
mirror is true, `settings_reset` costs nothing but BT bonds. Keep it honest —
**a Studio GUI edit never reaches this repo.**

**Working order, every session: dump the board → change the board → bring the
file up to it.** bekh edits in Studio a lot between sessions — and during
them — so the keymap file and this doc are stale by default, and a plan drawn
from the doc lands on keys that moved. Whatever drift `verify` finds is bekh's
edits, not noise: fold it in.

## Setup

`.venv` is gitignored and will not exist on a fresh clone:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python zmk-studio-api
```

The board must be plugged in and **ZMK Studio's GUI must not be running** — it
holds the serial port exclusively, and `zmkctl` fails with "Device or resource
busy" while it is open.

**Standing authorization: when the port is busy, kill ZMK Studio. Don't ask.**

```bash
P=$(lsof -t /dev/tty.usbmodem* 2>/dev/null | head -1); [ -n "$P" ] && kill $P
```

Kill by the PID `lsof` reports, never `pkill -f zmk` — the shell running it
matches its own pattern. Studio writes every GUI edit straight to the board, so
there is no unsaved buffer to lose. It also relaunches itself and grabs the port
again mid-session; re-run the kill before each `zmkctl` call rather than assuming
the port stayed free.

The usbmodem node moves between ports; `zmkctl` globs for it, `ZMKCTL_SERIAL`
overrides.

## Board vs Karabiner — where a thing belongs

- **The board owns anything physical**: layers, key positions, hold behavior.
  Travels with the keyboard, one source of truth.
- **Karabiner owns anything that depends on macOS state**: the active input
  source, the app, which device sent the event. The board cannot see any of it —
  the EN-gated `shift+7 → ?` rule is the standing example, and it is why one
  physical key gives `?` in both languages.

Don't emulate a layer in Karabiner. It has no layers, only variables, so a layer
becomes N hand-enumerated conditional remaps — a second copy of the layout that
will drift from the first.

The one deliberate exception is the rule "Lily58: alt numpad + …": when Space
became a real Alt, CURSE's non-alt cells moved there as static option remaps,
scoped to the Lily58 — alt + the right-hand block types bare digits (`0` on
alt+RGUI), alt+Enter types `'`, alt+`=` sends alt+Space (the launcher). Ten-odd
remaps that won't rot; the left-hand Enter is the global alt+v = Enter rule.
The numpad `.` was dropped.

**Karabiner rules get edited and enabled directly**, never handed back to the
GUI: enabling is inserting the rule object into
`profiles[0].complex_modifications.rules` at the index that gives it the right
precedence.

**`~/.config/karabiner` is a git repo in place** (`bloodhorse/karabiner`) — the
live directory *is* the repo, no mirror, no symlink, no daemon. bekh edits
Karabiner only from sessions in this project, so the agent is the committer:

- **commit and push immediately after each edit**, not at session end — a
  session can die mid-way
- whenever a session touches Karabiner, `git -C ~/.config/karabiner status
  --short` first — anything dirty gets swept into the next commit with a message
  that says what it was
- no `.bak` files next to `karabiner.json` — git is the history
- `automatic_backups/` is gitignored; `assets/complex_modifications/` is tracked
  (it holds the importable rule sources)

Rollback is `git -C ~/.config/karabiner checkout HEAD~1 -- karabiner.json`;
Karabiner reloads on its own.

## Traps that have already cost time

- **Two alphabets.** Karabiner rules AND `config/lily58.keymap` AND every
  `zmkctl dump` are QWERTY scancodes — the board sends QWERTY, Karabiner turns
  it into Gallium. bekh reads and speaks Gallium. **Never tell bekh a key by the
  name in the file: translate**, or bekh presses the wrong keys and a correct
  binding looks broken.

  | file / karabiner | q w e r t | y u i o p | a s d f g | h j k l ; | z x c v b | n m , . / |
  |---|---|---|---|---|---|---|
  | **what bekh presses** | b l d c v | j y o u , | n r t s g | p h a e i | x q m w z | k f ' ; . |

  Digits, symbols on the number row, modifiers and thumbs are the same in both.

  **Alt chords go through the table too.** Space-hold is a real Alt, and
  Karabiner's "Gallium mod-combos (Lily58)" rule translates option like cmd
  and ctrl — it cannot tell a held mod from a baked one, so a baked `LA()`
  cell is named in QWERTY like every other cell: HEAVEN's `LA(Y)` is alt+j,
  `LA(LG(U))` alt+cmd+y, shit's `LA(LG(C))` alt+cmd+m. Keypad and arrow keys
  aren't in the table, so FUCK's alt+keypad tiling cells read literally. No
  Karabiner rule is split per device for alt any more.
- **Password fields kill alt-only hotkeys.** Secure input makes macOS drop any
  global hotkey whose modifiers are only Option or Option+Shift; one with Ctrl
  or Cmd in it still fires (measured 2026-10-05 with test Carbon hotkeys and
  synthetic key events). It cannot be switched off from outside the app. The
  fix costs no latency: a Karabiner rule turns the alt chord into the same key
  with ctrl+opt+cmd, and the target app's hotkey is rebound to that. Done for
  alt+g (Maccy clipboard history — it replaced Raycast's because its popup
  draws above the floating iTerm drop-down) and alt+t (iTerm drop-down). Not done for
  the AeroSpace alt bindings — same recipe if bekh asks. Don't go through
  shell commands or AppleScript for this: iTerm's hidden hotkey window is not
  reachable from AppleScript, and each `osascript` call costs ~130 ms.
- **Rule order in Karabiner is precedence.** A physical-key rule belongs *above*
  the Gallium block: up there it sees raw scancodes and behaves identically under
  EN and ЙЦУКЕН. Below, it fires on the wrong keys in English only.
- **A rule sitting in `karabiner.json` proves nothing** — it may be disabled, or
  shadowed. Verify by pressing keys.
- **Positional reasoning must account for ЙЦУКЕН.** Every Gallium/Colemak rule is
  `input_source_if ^en$`, so under Russian the physical positions are plain
  ЙЦУКЕН: `[` is х, `;` is ж, `/` is `.`. A key that looks free in English is
  often a live Cyrillic letter. Modifier seats are the only ones free in both.
- **Layers themselves are Studio-GUI-only, and they are sticky.** The python
  api (`zmk-studio-api` 0.5.1) has get/set key, save, discard, reset — no add,
  rename, remove or reorder. Adding or naming a layer is bekh in the GUI, then
  the agent binds cells over RPC. Read names back from `get_keymap_bytes` (the
  printable runs, in slot order) before trusting one from the doc. A layer
  deleted in Studio comes back on a reflash while the keymap file defines it,
  and one added in Studio cannot be deleted from the GUI at all: removing a
  layer for good takes a build without it plus a reset of the saved keymap.
- **The api's `Keycode` enum only knows named values.** A baked chord like
  `LA(LG(M))` (`0x0C070010`: mods in the top byte, then page, then id) raises
  `ValueError` through `KeyPress`. `zmkctl kp L POS 0x…` sends any 0x value as
  `Raw` on the Key Press behavior instead; `zmkctl set` takes a keycode name
  for both params (`set 0 53 mod_tap_balanced_280 LALT SPACE`).
- **A layer Studio created holds zeroed bindings, and they fall through.**
  Its cells read back as `Unknown { behavior_id: 0 }`. In effect that is
  `&trans`, not `&none` (ZMK v0.3.0 `behavior.c` returns 1 for a missing
  behavior, so the keymap loop continues downward). `cell_from_board` maps it
  to `&none` only as a naming convention for `verify` — when such a layer goes
  into the keymap file, write its empty cells as `&trans`.
- **Wiping saved settings: ask at the moment of doing it, even when it is in
  the plan.** `settings_reset.uf2` erases the saved keymap AND every Bluetooth
  bond, including the halves' bond to each other — so wiping one half forces
  the same wipe on the other. The api's `reset` call should restore the keymap
  to firmware defaults without touching bonds; it is untested here, try it
  first next time. Either way `verify` must say MATCH before the wipe, and the
  board cannot be read once it is in bootloader mode — check before bekh
  double-taps.
- **A `conditional_layers` node owns its then-layer.** ZMK deactivates the
  then-layer whenever the if-layers aren't all held, so any other door to that
  slot opens and closes in the same tick, silently. None is compiled in now;
  if one comes back, its then-layer can carry no door of its own.
- **The keymap-drawer Action rewrites the commit you just pushed.** On any push
  touching `config/*.keymap` it regenerates `keymap-drawer/lily58.{svg,yaml}`,
  amends them into *your* commit and force-pushes: same content, new SHA, and
  your local branch is now a sibling of the remote one. **After every keymap
  push, wait for the run, then `git fetch origin && git reset --hard
  origin/main` — never merge or pull**, the remote commit already contains
  yours. Skip the reset and the next session's first push is rejected.
- **Push keymap changes once.** A second push within ~40s makes the drawer's
  `--force-with-lease` amend fail: your commits land, the run goes red, and the
  SVG is silently stale. Stack local commits and push them together. If it
  happened, re-run by hand, then reset:

  ```bash
  gh workflow run "Draw ZMK keymaps" --ref main   # wait for it, then:
  git fetch origin && git reset --hard origin/main
  ```

## Deciding what goes where

**bekh's right hand lives on the mouse.** Every shortcut, chord and layer
combo goes on the left hand alone — door and target both. Cross-hand chords
are out, and "the free hand is more comfortable" is not an argument here,
because the right hand is not free. A left-pinky hold plus left ring/middle/
index is the shape to design for; it is the shift chord the hand already knows.

Don't argue layout from feel — there is a measurement.
[`stats/keycount-2026-07.md`](stats/keycount-2026-07.md) is a 16-day,
79k-keypress character-frequency ledger with the blind spots documented. The
collector is `~/.hammerspoon/keycount.lua`, retired on purpose and commented out
at `init.lua:52`; uncomment it to run another window.

[`docs/dual-role-thumbs.md`](docs/dual-role-thumbs.md) carries the thumb design:
mechanism limits, why the eight thumb seats are arithmetically closed, where the
current layout landed and why, and what is still open.

## Resume pointer

**Mirror true as of 2026-10-14**, after a flash that kept Studio's saved state:
`verify` returns MATCH, and a MISMATCH from here on is bekh's Studio edits —
dump, then fold them in. `docs/kitchen-dump-2026-09-01.txt` is a record of the
kitchen mid-cook, superseded by `config/lily58.keymap`.
[`docs/dual-role-thumbs.md`](docs/dual-role-thumbs.md) still describes Space
holding CURSE; the thumb arithmetic in it holds, the Space seat does not.

Five layers, names from firmware: 0 `ground`, 1 `CURSE`, 2 `HEAVEN`, 3 `shit`,
4 `FUCK`. bekh uses the board wired; Bluetooth is not paired.

**Space (pos 53) is `mtb280 LALT SPACE`: tap Space, hold a real Left Alt.**
Every alt chord works without a cell and every real mod stacks in any order.
The misfire profile is the one CURSE's alt fill already had — a fast roll off
Space that releases the next key first becomes an alt chord.

Where the doors are:

- **`shit` (slot 3)** — `&mo 3` on both outer thumbs, pos 50 and 57. Num row
  is F1–F12 with **F1–F10 under the digit they are named after**; F11 on the
  `]` corner, F12 under it. Row below is shift+digit baked in (the symbol row).
  **CAPS sits on the left-shift seat (pos 36).** The Esc corner is `BT_SEL 3`
  (bekh's Studio edit), so Esc does not work with shit held. shit + the key
  bekh calls m is `LA(LG(C))` = alt+cmd+m, hyprshit's mode. Volume lives on
  the rotary encoder, bound on every layer.
- **`FUCK` (slot 4)** — two doors, mirrored on the home-row pinkies: pos 24
  held (`ltb280 4 GRAVE`) and pos 35 held (`ltb280 4 LS(N7)`, the tap is `?`).
  Studio's add-layer is capped — this firmware has no spare slot, so a sixth
  layer is a build. Carries cmd+1..5 on the left home row, each under its
  digit: hold the key and press **n r t s g**. One-handed tab switching, the
  reason the layer exists. Num row has cmd+shift+3 and cmd+shift+4 under their
  digits; alt+keypad 4 5 6 8 2 are tiling cells.
- **HEAVEN** — Enter-hold (pos 54, `ltb280 2 RET`). Arrow cross on the right.
- **CURSE** — no hold door any more. The only way in is `&tog 1` at HEAVEN
  pos 55. Its content (the alt cells, numpad, left-hand Enter) is dead weight
  now that alt is real and the rest moved to Karabiner.

Number row is plain digits and `]`; the unshifted-symbols row was tried and
reverted on 2026-09-02 because it broke cmd+digit — that, the cross-language
symbol problem and the custom ЙЦУКЕН plan live in
[`docs/musings_over_ru_layout.md`](docs/musings_over_ru_layout.md) — read it
before touching either. bekh barely uses Russian now.

Parked, in bekh's words: alt+Z fullscreen sim — "think later".

Open threads:

- **nothing from 2026-10-14 has been pressed through yet** — real alt, the
  Karabiner rewrite, the alt numpad, alt+`=`, CAPS on shit are verified by
  `verify` and Karabiner's reload log only
- **alt+tab opens nothing right now.** The Karabiner alt+tab → alt+F20 rule
  is gone (bekh wants plain alt+tab), but hyprshit's switcher still binds
  `f20` / `alt-f20` in `~/tower/forge/hyprshit/config/keys`; the fix is
  `alt-tab launch windows` there plus the F20 paragraph in its
  `docs/launcher.md` — waiting on bekh's ok to touch hyprshit
- **Karabiner cleanup** — bekh wants the dead rules gone and has not picked
  them yet. Off already: the old F17/F18 pair, Colemak Mod-DH, tap-cmd → Clear.
  Likely dead: "Lily58 spares → EN symbols" (the inert RU-scheme half),
  ctrl+cmd+esc → force quit (a no-alt workaround). Ask about: side pad, AB
  Shutter3, side-keyboard Num5, the four EN/RU toggles (Space+[, F17,
  ctrl+shift tap, cmd+tab), ctrl+shift+P TTS pause, F16 → Raycast, cmd+shift+3
  main display, the second profile "hop"
- the launcher on alt+Space dies in password fields like any alt-only hotkey —
  same ctrl+opt+cmd recipe if bekh wants it
- Space at 280: spaces vanishing or rolls turning into alt chords → a rung up,
  `zmkctl set 0 53 mod_tap_balanced_320 LALT SPACE`; same question for the
  FUCK door eating slow taps (any `ltb` rung)
- HEAVEN pos 2's stray `0xCE` (Keypad @, ignored by macOS)
- the Arch machine was wired against the old baked alt cells; a message for
  that session describing the switch was handed to bekh — its alt bindings
  need re-deriving from "hold Space + the key bekh calls X → alt+X"
