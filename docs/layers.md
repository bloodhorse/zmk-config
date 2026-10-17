# The layers

What's on the board and why it's seated where it is. This doc drifts as soon
as bekh opens Studio: `zmkctl dump` is the truth, and this file is the reasoning
behind it. Key names below are what bekh presses (Gallium); cell names in the
keymap are QWERTY, so translate through the table in `CLAUDE.md`.

## The rule that decides seats

**bekh's right hand lives on the mouse.** Every shortcut, chord and layer combo
goes on the left hand alone, door and target both. Cross-hand chords are out,
and "the free hand is more comfortable" isn't an argument here, because the
right hand isn't free. The shape to design for is a left-pinky or left-thumb
hold plus left ring/middle/index: the shift chord the hand already knows.

Don't argue layout from feel; there's a measurement.
[`../stats/keycount-2026-07.md`](../stats/keycount-2026-07.md) is a 16-day,
79k-keypress character-frequency ledger with its blind spots documented. The
collector is `~/.hammerspoon/keycount.lua`, retired and commented out in
`init.lua`. Uncomment it to run another window.

## ground (slot 0)

Plain QWERTY scancodes; Karabiner makes them Gallium. The number row is plain
digits and `]`. An unshifted-symbols row was tried and reverted because it
broke cmd+digit. That, the cross-language symbol problem and the custom
ЙЦУКЕН plan live in [`musings_over_ru_layout.md`](musings_over_ru_layout.md).

- **Thumbs:** `50 shit · 51 LCTRL · 52 LGUI · 53 Space/LALT | 54 Enter/HEAVEN ·
  55 RGUI · 56 BSPC · 57 shit`. Space is `mtp150 LALT SPACE`: tap Space, hold
  a real Left Alt, so every alt chord works without a cell. The misfire to
  watch for: after a pause, a roll off Space into the next word becomes an alt
  chord (`docs/board.md` has the regime).
- **pos 24**, the left home-row pinky: `~` on tap, F20 on hold (`mtp150 F20 GRAVE`).
- **pos 35**, the right home-row pinky: `?` on tap (`LS(N7)`, which is the
  ЙЦУКЕН chord, and Karabiner's EN-gated `shift+7 → ?` covers English), F20 on
  hold. It had to be a modifier seat: every symbol seat is a live Cyrillic
  letter under ЙЦУКЕН.

## shit (slot 3), the junk drawer

Door: `&mo 3` on both outer thumbs (50, 57). This is the layer bekh actually
reaches.

- Number row: F1–F10 **under the digit they're named after**, F11 on the `]`
  corner, F12 under it. The Esc corner is `BT_SEL 3`, so Esc does nothing
  with shit held.
- Row below: shift+digit baked in, a second number row with shift pre-pressed.
  The `&` cell is `RS(N7)`, not `LS(N7)`, and that's load-bearing: Karabiner's
  `shift+7 → ?` is keyed on left shift, so the right shift slips past and `&`
  comes out.
- CAPS on the left-shift seat (pos 36). **shit + m is alt+cmd+m, hyprshit's
  mode** (cell `LA(LG(C))`). Next to it, ctrl+e (pos 38); on the home row
  above, cmd+a (pos 27).
- Volume is on the rotary encoder, bound on every layer.

## FUCK — a held F20, not a layer

The home-row pinkies (pos 24, pos 35) hold **F20** (`mtp150 F20 …`), and
slot 4 is empty, kept only so the slot ids don't move. The meaning lives off
the board: on the mac shitd reads held F20 as its own modifier `fuck` and the
bindings are `fuck-<key>` lines in hyprshit's `config/keys` (Gallium letters,
like every other chord there); on the mini keyd's `[fuck]` layer in
`/etc/keyd/default.conf` keys on the physical QWERTY spot and emits what the
old layer's chords became there. The two are kept in step by hand.

What sits on it (Gallium names):

- n → summon Arc on the mac; ctrl+shift+n (kitty's new window) on the mini.
- 3 / 4 → screenshots (full / region).
- l → dim the centre Mi Monitor on the mac, blackout on the mini; d → dim the
  built-in (mac only); c → the mini's `desk` (mac: nothing).
- e → Finder (mac only), shift+e closes every Finder window.
- Space → the special workspace.

A run (door + l l l) toggles in a run: every press while F20 is down fires.
Under secure input (a password field) the mac's fuck chords are dead, since
the tap is blind there. On the mini F20 is xkb's `XF86AudioMicMute`: if keyd
is down, a held pinky flips the mic.

## HEAVEN (slot 2)

Door: Enter held (pos 54, `ltp150 2 RET`). An inverted-T arrow cross on the
right with alt+arrows beside it, BT controls on the number row, and `&tog 1`
at pos 55, the only door to CURSE. Pos 2 holds a stray `0xCE` (Keypad @,
ignored by macOS); undecided.

## CURSE (slot 1), dead weight

No hold door; reachable only through HEAVEN's `&tog 1`. Its alt cells,
numpad and left-hand Enter all became redundant once Space turned into a real
alt and the rest moved to Karabiner. It's a free slot for whatever comes next
(a sixth layer would need a build).
