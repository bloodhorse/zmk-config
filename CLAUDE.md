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

## Setup

`.venv` is gitignored and will not exist on a fresh clone:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python zmk-studio-api
```

The board must be plugged in and **ZMK Studio's GUI must be closed** — it holds
the serial port exclusively, and `zmkctl` will fail with "Device or resource
busy" while it is open. The usbmodem node moves between ports; `zmkctl` globs
for it, `ZMKCTL_SERIAL` overrides.

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
precedence. Back the file up first and it is as reversible as anything else.

## Traps that have already cost time

- **Two alphabets.** Karabiner rules are written in QWERTY scancodes; bekh reads
  and speaks Gallium. `i j k l n` in a rule file are `O H A E K` in conversation.
  Same physical keys, and confusing them makes a discussion incoherent.
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
  with firmware defaults on the 2026-09-01 flash. Retired layer ids are never
  recycled either — Studio's next new layer takes the next reserved slot.
- **The keymap-drawer Action amends your pushed commit** to add the regenerated
  SVG. Every subsequent push conflicts; resolve by keeping your
  `config/lily58.keymap` and taking theirs for `keymap-drawer/`.

## Deciding what goes where

Don't argue layout from feel — there is a measurement.
[`stats/keycount-2026-07.md`](stats/keycount-2026-07.md) is a 16-day,
79k-keypress character-frequency ledger with the blind spots documented. The
collector is `~/.hammerspoon/keycount.lua`, retired on purpose and commented out
at `init.lua:52`; uncomment it to run another window.

[`docs/dual-role-thumbs.md`](docs/dual-role-thumbs.md) carries the thumb design:
mechanism limits, why the eight thumb seats are arithmetically closed, where the
current layout landed and why, and what is still open.

## Resume pointer

KITCHEN MODE, since 2026-08-31, until ~2026-09-end: bekh cooks GUI edits in
Studio on purpose — **the mirror is STALE, `verify` MISMATCH is expected and
correct, do not "fix" the board to match the file.** The real board state is
snapshotted read-only in [`docs/kitchen-dump-2026-09-01.txt`](docs/kitchen-dump-2026-09-01.txt);
refresh it (dump → commit) whenever the port is free — it is the only backup
his edits have. Cooked so far, beyond the file: thumb row reshuffled (LAlt↔LGui
swapped, RAlt→RGui, HEAVEN's pos-11 door traded for a plain `]`), CURSE's left
hand is aerospace sims (`LA(letter)`), CURSE num row is `LA(ESC)`/`LA(1-5)`
workspace switching, and **LIMBO** (fw slot 4) opens on Space+Enter held
together — a compiled conditional_layers node — carrying the alt-arrow
word-jump cross on HEAVEN's arrow positions. alt+shift+number works with no
cells: real shift composes (right shift any order; left shift before Space,
CAPS squats on CURSE's shift seat). Media (slot 3) is back after the reflash,
inert. The space-as-real-Alt idea is settled: simulate with `LA()` cells; a
balanced mod-tap build only ever pays if alt+mouse chords start mattering.

Number row is plain digits with `\` at pos 11; the unshifted-symbols row was
tried and reverted on 2026-09-02 because it broke cmd+digit — that, the
cross-language symbol problem and the custom ЙЦУКЕН plan live in
[`docs/musings_over_ru_layout.md`](docs/musings_over_ru_layout.md) — read it before touching either.

Parked, in bekh's words: seat 50 → `motog 1 1` (tap = latch CURSE numpad,
hold = momentary door) — approved, waiting; alt+Z fullscreen sim — "think
later"; CAPS off CURSE's shift seat if the left-shift ordering annoys.

Open threads: whether balanced@280 wears well (spaces vanishing = rebind a
rung up: `zmkctl set 0 53 layer_tap_balanced_320 1 SPACE`); the two stray
cells at HEAVEN pos 1-2; and the proper re-mirror at month end — dump → fold
into the keymap file → verify MATCH → delete the kitchen notes above.
