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
  next new layer takes the next reserved slot, which is how LIMBO ended up in
  `extra_2` (slot 4).
- **A reserved slot Studio activated holds zeroed bindings, not `&none`.** Cells
  in such a layer read back as `Unknown { behavior_id: 0 }` — behavior id 0 is
  not in the board's behavior list at all, so the API cannot name it. It is an
  empty cell in effect; `cell_from_board` maps exactly that string to `&none` so
  the layer can be verified instead of skipped.
- **Layers themselves are Studio-GUI-only.** The python api (`zmk-studio-api`
  0.5.1) has get/set key, save, discard, reset — no add, rename, remove or
  reorder of layers. Adding a layer or naming it is bekh in the GUI, then the
  agent binds cells over RPC. Read the names back from `get_keymap_bytes`
  (the printable runs are the layer names, in slot order) before trusting a
  name from the doc: Studio renamed LIMBO to `WELL` on its own at some point,
  and a layer bekh added by hand in Studio on 2026-09-12 (slot 5) could not be
  deleted from the GUI either — it became FUCK's home instead. Only a reflash
  + `settings_reset` removes a layer for good.
- **The `conditional_layers` node OWNS its then-layer, slot 4.** ZMK's listener
  runs on every layer state change and *deactivates* the then-layer whenever
  the if-layers aren't all held — so no other door can open slot 4: an `&mo 4`
  or a hold-tap to 4 turns it on and the listener turns it off in the same
  tick, and nothing tells you. 2026-09-12: FUCK was bound into slot 4 with a
  backtick door that silently did nothing until it moved to slot 5. Never put
  a layer with its own door in slot 4 while that node is compiled in; dropping
  the node is a build.
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

**Mirror true as of 2026-09-12**: `verify` returns MATCH across all six bound
layers, so a MISMATCH from here on is bekh's Studio edits — dump, then fold them
in. `docs/kitchen-dump-2026-09-01.txt` is superseded by `config/lily58.keymap`
itself — kept only as a record of what the kitchen looked like mid-cook.

Six bound layers: 0 `ground`, 1 `CURSE`, 2 `HEAVEN`, 3 `shit`, 4 empty (the
tri-layer's slot, LIMBO in the file), 5 `FUCK`. Names come from the board, not
from here — and as of the last session the board still had slot 4 named FUCK
and slot 5 nameless; bekh renames them in Studio (4 → LIMBO, 5 → FUCK).

Where the doors are:

- **`shit` (slot 3)** — `&mo 3` on both outer thumbs, pos 50 and 57. Num row
  is F1–F12 with **F1–F10 under the digit they are named after**; F11 on the
  `]` corner, F12 under it. Row below is shift+digit baked in (the symbol row).
  Volume lives on the rotary encoder, bound on every layer.
- **`FUCK` (slot 5)** — backtick held at pos 24 (`ltb280 5 GRAVE`, tap is
  still backtick). Carries cmd+1..5 on the left home row, each under its digit:
  hold ` and press **n r t s g**. One-handed tab switching, the reason the
  layer exists. **The block in the keymap file only becomes firmware default
  on the next build**; today it lives solely in Studio flash settings.
- **Slot 4** — empty, opened by Space+Enter through the compiled tri-layer node
  and by nothing else (the node owns it, see traps). Was LIMBO's alt-arrow
  word-jump cross, erased 2026-09-12. Same build caveat.
- **CURSE / HEAVEN** — only through the thumb hold-taps at pos 53/54, plus
  `&tog 1` at HEAVEN pos 55, the single escape hatch if a hold-tap misbehaves.
  The base layer has no plain `&mo` to either; pos 11 is `]`.
- CURSE's left hand is aerospace sims (`LA(letter)`), num row `LA(ESC)`/`LA(1-5)`
  for workspaces. alt+shift+number needs no cells: real shift composes (right
  shift any order; left shift before Space, since CAPS squats on CURSE pos 36).
  The space-as-real-Alt idea is settled — simulate with `LA()` cells; a balanced
  mod-tap build only ever pays if alt+mouse chords start mattering.

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
eats slow backtick taps (same fix, any rung); HEAVEN pos 2's stray `0xCE`
(Keypad @, ignored by macOS); a build to land FUCK in firmware and, while at
it, drop the Space+Enter tri-layer node — it guards an empty slot now, and it
is the reason slot 4 can never hold a layer with a door.
