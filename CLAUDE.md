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

Layer *content* is always runtime — retargeting, adding, or clearing any key
on CURSE or HEAVEN never needs a build. Since 2026-08-31 the thumb hold-taps
are the whitelist-free `ltb` ladder (balanced, five terms compiled in), so
there is no compiled position list left to outgrow; the only thing that still
needs a build is a genuinely new behavior. Tuning the hold term = rebinding
Space/Enter to another rung over RPC.

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
file up to it.** bekh edits in Studio a lot between sessions, so this file and
CLAUDE.md are stale by default; a plan drawn from memory of the doc lands on
keys that moved (2026-09-12: the doc said the `shit` door was pos 24, the board
had it on both outer thumbs and pos 24 was the backtick). `dump` first, then
act, then `verify`, then rewrite the mirror from what the board says — and fold
in whatever drift `verify` finds along the way, it is bekh's edits, not noise.

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

**Karabiner rules get edited and enabled directly**, never handed back to the
GUI: enabling is inserting the rule object into
`profiles[0].complex_modifications.rules` at the index that gives it the right
precedence.

**`~/.config/karabiner` is a git repo in place** (`bloodhorse/karabiner`) — the
live directory *is* the repo, no mirror, no symlink, no daemon. bekh edits
Karabiner only from sessions in this project, so the agent is the committer:

- **commit and push immediately after each edit**, not at session end — a
  session can die mid-way, and an uncommitted edit with a scratchpad `.bak` is
  exactly how the repo rotted for two weeks in Aug–Sep 2026
- whenever a session touches Karabiner, `git -C ~/.config/karabiner status
  --short` first — anything dirty gets swept into the next commit with a message
  that says what it was
- no `.bak` files next to `karabiner.json` — git is the history, and the pile
  has been killed twice now
- `automatic_backups/` is gitignored; `assets/complex_modifications/` is tracked
  (it holds the importable rule sources)

Rollback is `git -C ~/.config/karabiner checkout HEAD~1 -- karabiner.json`;
Karabiner reloads on its own.

## Traps that have already cost time

- **Two alphabets.** Karabiner rules AND `config/lily58.keymap` AND every
  `zmkctl dump` are QWERTY scancodes — the board sends QWERTY, Karabiner turns
  it into Gallium. bekh reads and speaks Gallium. **Never tell bekh a key by the
  name in the file: translate.** 2026-09-12 the agent said "hold backtick, tap
  A/S/D/F/G" for cells bound as `&kp A..G` — the physical keys are `n r t s g`,
  and bekh pressed the keys that *type* a s d f g, half of them on the other
  hand. Nothing worked, and the binding was right the whole time.

  | file / karabiner | q w e r t | y u i o p | a s d f g | h j k l ; | z x c v b | n m , . / |
  |---|---|---|---|---|---|---|
  | **what bekh presses** | b l d c v | j y o u , | n r t s g | p h a e i | x q m w z | k f ' ; . |

  Digits, symbols on the number row, modifiers and thumbs are the same in both.

  **The exception is any chord with alt in it** (since 2026-10-05). The board
  has no physical Alt, so every alt chord is a baked `LA()` cell, and Karabiner
  no longer translates option chords coming from the Lily58: the cell is
  literal. `LA(T)` is alt+t — in Studio, in the keymap file, in the dump — and
  `LA(LG(M))` is alt+cmd+m. Never run an alt cell through the table. Plain,
  cmd-only and ctrl-only cells (`LG(K)`, `LC(L)`) still go through it, because
  bekh holds real Cmd and Ctrl and Karabiner cannot tell a held key from a
  baked one. The three raw-scancode rules that key on option (kvmtype, alt+v,
  the screenshot chord) are split per device for the same reason.
- **Rule order in Karabiner is precedence.** A physical-key rule belongs *above*
  the Gallium block: up there it sees raw scancodes and behaves identically under
  EN and ЙЦУКЕН. Below, it fires on the wrong keys in English only.
- **A rule sitting in `karabiner.json` proves nothing** — it may be disabled, or
  shadowed. Verify by pressing keys.
- **Positional reasoning must account for ЙЦУКЕН.** Every Gallium/Colemak rule is
  `input_source_if ^en$`, so under Russian the physical positions are plain
  ЙЦУКЕН: `[` is х, `;` is ж, `/` is `.`. A key that looks free in English is
  often a live Cyrillic letter. Modifier seats are the only ones free in both.
- **Deleting a layer in Studio does not survive a reflash** while the keymap
  file still defines it: media (id 3) was deleted in the kitchen and came back
  with firmware defaults on the 2026-09-01 flash — it is now `shit`, the same
  slot renamed and reused. Retired layer ids are never recycled either — Studio's
  next new layer takes the next reserved slot.
- **A reserved slot Studio activated holds zeroed bindings, and they fall
  through.** Cells in such a layer read back as `Unknown { behavior_id: 0 }` —
  behavior id 0 is not in the board's behavior list, so the API cannot name it.
  In effect it is `&trans`, not `&none`: ZMK v0.3.0 `behavior.c` returns 1 for
  a missing behavior and the keymap loop continues to the next layer down.
  `cell_from_board` still maps that string to `&none` (a naming convention for
  `verify`, nothing more) — when such a layer goes into the keymap file for a
  build, write its empty cells as `&trans` or the flash changes how it feels.
- **Layers themselves are Studio-GUI-only.** The python api (`zmk-studio-api`
  0.5.1) has get/set key, save, discard, reset — no add, rename, remove or
  reorder of layers. Adding a layer or naming it is bekh in the GUI, then the
  agent binds cells over RPC. Read the names back from `get_keymap_bytes`
  (the printable runs are the layer names, in slot order) before trusting a
  name from the doc. A layer added in Studio cannot be deleted from the GUI;
  removing one for good takes a build without it plus a reset of Studio's
  saved keymap (done 2026-10-05, which is how the board got back to five).
- **Wiping saved settings: ask at the moment of doing it, even when it is in
  the plan.** `settings_reset.uf2` erases the saved keymap AND every Bluetooth
  bond, including the halves' bond to each other — so wiping one half forces
  the same wipe on the other. The api's `reset` call should restore the keymap
  to firmware defaults without touching bonds; it is untested here, try it
  first next time. Either way `verify` must say MATCH before the wipe, and the
  board cannot be read once it is in bootloader mode — check before bekh
  double-taps.
- **A `conditional_layers` node owns its then-layer.** ZMK's listener runs on
  every layer state change and *deactivates* the then-layer whenever the
  if-layers aren't all held — so no other door can open that slot: an `&mo` or
  a hold-tap to it turns it on and the listener turns it off in the same tick,
  and nothing tells you. 2026-09-12: FUCK sat in such a slot with a door that
  silently did nothing. No such node is compiled in since 2026-10-05; if one
  comes back, its then-layer can carry no door of its own.
- **The keymap-drawer Action rewrites the commit you just pushed.** It fires on
  any push touching `config/*.keymap`, regenerates `keymap-drawer/lily58.{svg,yaml}`,
  and — because the workflow sets `amend_commit: true` — folds them into *your*
  commit with `--amend`, then force-pushes. Same content, new SHA. Your local
  branch is left pointing at a commit that no longer exists upstream, and the two
  are siblings off the same parent, not parent-and-child.
  **Recovery is `git reset --hard origin/main`, never a merge** — the remote
  commit already contains everything yours did, so there is nothing to keep. A
  `git pull` instead invents a conflict in `keymap-drawer/`, files neither side
  hand-edited.
- **It pushes with `--force-with-lease`, so a fast second push kills the drawer.**
  Push a keymap change, then push again within ~40s, and the amend is rejected
  with `! [rejected] main -> main (stale info)`. Nothing is corrupted and your
  branch stays linear — but **the SVG is now stale**, silently, because the run
  went red while your commits went through. Fix: re-run it by hand, then reset.

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

**Mirror true as of 2026-10-05**, on freshly flashed firmware with Studio's
saved state wiped: the board is running the keymap file's defaults, `verify`
returns MATCH, and a MISMATCH from here on is bekh's Studio edits — dump, then
fold them in. `docs/kitchen-dump-2026-09-01.txt` is superseded by
`config/lily58.keymap` itself — kept only as a record of what the kitchen
looked like mid-cook.

Five layers, names from firmware: 0 `ground`, 1 `CURSE`, 2 `HEAVEN`, 3 `shit`,
4 `FUCK`. The Space+Enter tri-layer node and the empty slot it guarded are
gone. bekh uses the board wired; Bluetooth bonds were wiped with the flash and
not re-paired.

Where the doors are:

- **`shit` (slot 3)** — `&mo 3` on both outer thumbs, pos 50 and 57. Num row
  is F1–F12 with **F1–F10 under the digit they are named after**; F11 on the
  `]` corner, F12 under it. Row below is shift+digit baked in (the symbol row).
  The Esc corner is `BT_SEL 3` (bekh's Studio edit), so Esc does not work with
  shit held. Volume lives on the rotary encoder, bound on every layer.
- **`FUCK` (slot 4)** — pos 24 held (`ltb280 4 LS(GRAVE)`; the tap is `~`,
  bekh's Studio edit, it was the backtick). Carries cmd+1..5 on the left home
  row, each under its digit: hold the key and press **n r t s g**. One-handed
  tab switching, the reason the layer exists. Num row has cmd+shift+3 and
  cmd+shift+4 under their digits. Every other cell is `&trans`.
- **CURSE / HEAVEN** — only through the thumb hold-taps at pos 53/54, plus
  `&tog 1` at HEAVEN pos 55, the single escape hatch if a hold-tap misbehaves.
  The base layer has no plain `&mo` to either; pos 11 is `]`.
- **CURSE is the alt layer, filled once (2026-10-05): every letter seat that is
  not numpad is `LA(` its own Gallium letter `)`**, so Space-hold + a key is
  alt + that key and a new alt chord never needs a cell. The seats without it:
  the numpad's nine (y o u / h a e / f ' ;), and v, which is Enter (the
  left-hand Enter, and shift/cmd + it must stay shift/cmd+Enter). Num row is
  `LA(ESC)`/`LA(1-4)` for workspaces. Stacks need no cells either — real
  Shift, Cmd and Ctrl compose over an alt cell and pass through Karabiner
  untranslated (right shift any order; left shift before Space, since CAPS
  squats on CURSE pos 36). Don't add `LA(LG(x))`-style cells; hold the real mod.
- Space-hold as a real Alt was re-argued 2026-10-05 and left alone: a key gets
  one hold, and Space's is CURSE's door (numpad, CAPS, the left-hand Enter);
  a real Alt would also turn every fast roll off Space into an alt chord. bekh
  does not want alt+mouse. What hurt was naming cells in QWERTY and binding
  each new chord, and both are gone. Reopen only if that changes.

Number row is plain digits and `]`; the unshifted-symbols row was tried and
reverted on 2026-09-02 because it broke cmd+digit — that, the cross-language
symbol problem and the custom ЙЦУКЕН plan live in
[`docs/musings_over_ru_layout.md`](docs/musings_over_ru_layout.md) — read it before touching either.

Parked, in bekh's words: alt+Z fullscreen sim — "think later"; CAPS off CURSE's
shift seat if the left-shift ordering annoys. The old `motog 1 1` plan for seat
50 is **stale** — that seat is a `shit` door now and CURSE lost its board-side
door, so re-decide the seat before reviving it.

Open threads: whether balanced@280 wears well (spaces vanishing = rebind a rung up:
`zmkctl set 0 53 layer_tap_balanced_320 1 SPACE`); whether the FUCK door at 280
eats slow `~` taps (same fix, any rung); HEAVEN pos 2's stray `0xCE`
(Keypad @, ignored by macOS); whether fast rolls off Space now misfire as alt
chords on j p i k x q m b l, which were transparent or harmless before the
alt fill (the fix is the same rung up); shit's alt+cmd+f on the key that types
m, which looks like a QWERTY-naming slip for alt+cmd+m and bekh has not ruled
on; the alt changes of 2026-10-05 are verified by `verify` and Karabiner's
reload log only — bekh has not reported pressing through them.
