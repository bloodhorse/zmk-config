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
  55 RGUI · 56 BSPC · 57 shit`. Space is `mtb280 LALT SPACE`: tap Space, hold
  a real Left Alt, so every alt chord works without a cell. The misfire to
  watch for: a fast roll off Space that releases the next key first becomes an
  alt chord.
- **pos 24**, the left home-row pinky: `~` on tap, FUCK on hold (`ltb280 4`).
- **pos 35**, the right home-row pinky: `?` on tap (`LS(N7)`, which is the
  ЙЦУКЕН chord, and Karabiner's EN-gated `shift+7 → ?` covers English), FUCK on
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

## FUCK (slot 4), one-handed tab switching

Doors: either home-row pinky held (pos 24, pos 35).

- cmd+2..5 on the left home row, each under its digit: hold `~` and press
  r t s g. Under the 1 (the key bekh calls n) sits ctrl+shift+n, which
  summons Arc through hyprshit.
- Number row: cmd+shift+3 and cmd+shift+4 under their digits.
- **Monitor toggles on the top row, b l d, laid out like the screens.** l
  (pos 14) is hyper+F14, the centre Mi Monitor; d (pos 15) is hyper+F15, the
  MacBook's built-in on the right; b (pos 13) is held for a third screen and
  stays transparent. They live on a held layer and not in hyprshit's mode
  because door + l l l has to toggle in a run, and the mode closes after
  every key. Hyper, because bare F14/F15 are brightness on macOS and shit's
  b l d are `! @ #`. On the mac hyprshit dims the screen; on the mini the
  chord arrives through keyd and runs blackout.
- The right hand is all transparent. Tiling focus and carry went to
  cmd+alt / ctrl+alt + CURSE's numpad seats through keyd on the mini.
- Space with FUCK held is alt+`, hyprshit's special workspace.

## HEAVEN (slot 2)

Door: Enter held (pos 54, `ltb280 2 RET`). An inverted-T arrow cross on the
right with alt+arrows beside it, BT controls on the number row, and `&tog 1`
at pos 55, the only door to CURSE. Pos 2 holds a stray `0xCE` (Keypad @,
ignored by macOS); undecided.

## CURSE (slot 1), dead weight

No hold door; reachable only through HEAVEN's `&tog 1`. Its alt cells,
numpad and left-hand Enter all became redundant once Space turned into a real
alt and the rest moved to Karabiner. It's a free slot for whatever comes next
(a sixth layer would need a build).
