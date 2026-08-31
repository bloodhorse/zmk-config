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
- **new behaviors** (a mod-morph, a hold-tap with a custom flavor or whitelist) —
  those must be compiled in, so: edit the keymap → push → GitHub Actions builds →
  flash both halves → **then bind over RPC**, because Studio's saved state still
  holds the old binding for that position

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

The board runs the balanced ladder, flashed and verified 2026-08-31. Open
threads, in the order they matter: whether balanced@280 wears well over a
week (spaces vanishing = rebind a rung up: `zmkctl set 0 53
layer_tap_balanced_320 1 SPACE`); pointing something at `media_layer`, which
is built and flashed but still has nothing referencing it; and the two stray
cells at HEAVEN pos 1-2 (a blank and an inert Keypad @) that look like a
Studio slip which ate F14/F15.
