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

- **Thumbs:** `50 F19/shit · 51 LCTRL · 52 LGUI · 53 Space/LALT | 54 Enter/HEAVEN ·
  55 RGUI · 56 BSPC · 57 F19/shit`. Space is `mtb280 LALT SPACE`: tap Space, hold
  a real Left Alt, so every alt chord works without a cell. Balanced, so a
  roll off Space stays a space (`docs/board.md` has the regime).
- **pos 24**, the left home-row pinky: `~` on tap, F20 on hold (`mtb280 F20 GRAVE`).
- **pos 35**, the right home-row pinky: `?` on tap (`LS(N7)`, which is the
  ЙЦУКЕН chord, and Karabiner's EN-gated `shift+7 → ?` covers English), F20 on
  hold. It had to be a modifier seat: every symbol seat is a live Cyrillic
  letter under ЙЦУКЕН.

## shit — a held F19, not a layer

The outer thumbs (50, 57) send a plain **F19** (`&kp F19`, zero delay), and
slot 3 is empty. On the mac shitd reads held F19 as its modifier `shit`
(`shit-<key>` lines in hyprshit's `config/keys`); on the mini keyd's `[shit]`
layer in `/etc/keyd/default.conf` (and `shit.*` lines for kitty and dropterm
in `~/.config/keyd/app.conf`) keys on the physical seat. Kept in step by hand.

What sits on it (Gallium names):

- digits 1..0, `]`, `[` → the F row's media meaning: brightness −/+, mission
  control, spotlight, dictation, F6, rewind, play, forward, mute, volume −/+.
  On the mac this is Karabiner's top rule, not shitd: it sets `shit` while
  F19 is down and sends the real media keys. A key shitd posts lands after
  Karabiner's fn table, so a posted F1 is a bare F1 that nothing listens to;
  that's how the row died once. On the mini keyd turns them into brightness,
  playback, mute and volume.
- t → cmd+a, q → ctrl+e, `=` (the left centre key) → ctrl+alt+space.
- m → hyprshit's mode (the mini: its mode submap).
- x → caps lock (moved off the shift seat: shitd can't key on a modifier).
- **alt + a tap of shit toggles caps lock** (mac): shitd fires the
  `alt-f19 caps` line when F19 goes down and up within 500 ms with no key,
  click, media key or modifier between, spelled with the modifiers held at
  release. A bare tap does nothing: it flipped caps by accident. The mini
  does the same in keyd: `f19 = overload(shit, capslock)` in `[sup:M]`, with
  `overload_tap_timeout = 500`. It's not a board hold-tap on purpose: the
  doors' prior-idle window would turn a shit chord right after typing into a
  tap and flip caps.
- Volume stays on the rotary encoder, bound on every layer.

**The F-row rule:** one key that fires something is an F-key wire; anything
pressed as a combination is an `alt-`/`fuck-`/`shit-` line in `config/keys`.
F13 is dictation, F18 neru's hints and gamevoice's push-to-talk, F19 shit,
F20 fuck; F14–F17 are free.

A key that becomes a hold is eaten under **every** modifier, so it needs a key
nothing uses at all, bare or chorded. The spare keycodes in
`musings_over_ru_layout.md` are no escape: Karabiner's dormant "Lily58 spares
→ EN symbols" rule turns `keypad_comma`, `international1` and `international3`
into symbols, so a hold there arrives as a quote. Help (keycode 114) is the
one untouched spare.

On the mini, a keyd layer's output never goes back through `[main]` or the
bridges: a `[fuck]`/`[shit]` seat must emit what keyd *used to make* of the
old baked chord (meta+digit there was ctrl+digit), never the raw chord the
board sent. Its F-keys: F18 is xkb's `XF86Launch9` (hints), F20 is
`XF86AudioMicMute`, F19 has no consumer; with keyd down, a held pinky flips
the mic.

## FUCK — a held F20, not a layer

The home-row pinkies (pos 24, pos 35) hold **F20** (`mtb280 F20 …`), and
slot 4 is empty, kept only so the slot ids don't move. The meaning lives off
the board: on the mac shitd reads held F20 as its own modifier `fuck` and the
bindings are `fuck-<key>` lines in hyprshit's `config/keys` (Gallium letters,
like every other chord there); on the mini keyd's `[fuck]` layer in
`/etc/keyd/default.conf` keys on the physical QWERTY spot and emits what the
old layer's chords became there. The two are kept in step by hand.

What sits on it (Gallium names):

- n → summon Arc on the mac; ctrl+shift+n (kitty's new window) on the mini.
- 3 / 4 → screenshots (main display / region) to a file; with ctrl, to the
  clipboard. Mini: keyd's `[control+fuck]` sends hyper+Pause / hyper+Scroll_Lock.
- l → dim the centre Mi Monitor on the mac, blackout on the mini; d → dim the
  built-in (mac only); c → the mini's `desk` (mac: nothing).
- e → Finder (mac only), shift+e closes every Finder window.
- Space → the special workspace.

A run (door + l l l) toggles in a run: every press while F20 is down fires.
Under secure input (a password field) the mac's fuck chords are dead, since
the tap is blind there. On the mini F20 is xkb's `XF86AudioMicMute`: if keyd
is down, a held pinky flips the mic.

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
