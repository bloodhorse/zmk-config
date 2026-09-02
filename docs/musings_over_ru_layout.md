# musings over the RU layout

The parking spot for a fix we agreed on and have not built: a custom ЙЦУКЕН
`.keylayout` so that symbol keys give the same glyph regardless of which
`.keylayout` so that symbol keys give the same glyph regardless of which
language macOS is in. Pick up from "Where it stands".

## The problem in one line

The board sends scancodes; macOS picks the glyph by the active input source.
The same physical key therefore types `@` in English and `"` in Russian, and
bekh's hands cannot predict a key that changes meaning with the language.

## What is actually possible (the arithmetic)

Russian has 33 letters, QWERTY has 26 letter seats. Every ЙЦУКЕН variant parks
the spare seven on the punctuation keycodes: `[`→х `]`→ъ `;`→ж `'`→э `,`→б
`.`→ю `` ` ``→ё. A keycode that is a Russian letter can never give a uniform
symbol; you would be evicting a letter with nowhere to put it. **Letters are
off limits — decided, not open.**

The keycodes with no Russian letter on them: the digit row `1`–`0`, `-`, `=`,
`\`. These are the whole uniform zone. Anything we want predictable across
languages has to arrive on one of these keycodes.

## The fix, minimal size (agreed, not built)

One custom ЙЦУКЕН file. Five cells differ from Apple's Russian:

| keycode | EN | RU today | RU after |
|---|---|---|---|
| shift+2 | `@` | `"` | `@` |
| shift+3 | `#` | `№` | `#` |
| shift+4 | `$` | `;` | `$` |
| shift+6 | `^` | `:` | `^` |
| shift+7 | `&` | `?` | `&` |

`! % * ( )` already agree. After this the ten shifted-digit symbols are
identical in both languages, wherever the board puts them (today: unshifted
on the number row, and behind shift on HEAVEN's numpad).

EN layout untouched. No board change. Karabiner's Gallium rules act on
scancodes upstream of the layout and do not care.

### Casualties to settle before it ships

- `№` — zero presses in the July ledger. Drop it.
- RU `"` lives on shift+2 and is lost. Needs a Russian home, or bekh types
  `«»` and does not care. **Unknown — ask.**
- RU `?` is shift+7 and RU `:` is shift+6. Both lost. These are not optional
  in Russian prose. The `/` seat that Karabiner turns into `?` under EN is
  `.`/`,` under RU. **Where `?` and `:` go in Russian is the open design
  question — ask bekh how he types them today before writing the file.**

## The fix, full size (on the table, not chosen)

Make the *bare* row symbols predictable too (`` ` `` `~` `'` `"` and friends),
still without touching letters: the number row sends digit keycodes, and a
custom EN **and** custom RU layout both map bare-digit → symbol, shift-digit →
another symbol. 22 uniform glyphs. Digits then come only from HEAVEN's numpad,
which must switch to keypad codes (`KP_N1`…) so the OS can tell it from the
row; both layouts map keypad → digits and shift+keypad → `!@#$%^&*()`.

Costs: the MacBook's own digit row would type symbols → one Karabiner
`device_if` rule sending keypad digits; two files to install on any new Mac;
**shift+keypad being definable in a `.keylayout` is assumed, not verified —
verify in a real file before building on it.**

## Mechanics when we build it

- Format: `.keylayout` XML. Editor: Ukelele, or by hand — start from a copy of
  Apple's Russian layout so everything we do not touch is byte-identical.
- Install: drop into `~/Library/Keyboard Layouts`, log out/in, enable in
  System Settings → Keyboard → Input Sources. The file lives in this repo.
- Dead end already found: alt+digit combos as a symbol layer are out —
  AeroSpace owns alt+1-5 and alt+shift+digits.

## Where it stands (2026-09-02)

- Board side done, runtime, in the kitchen: number row is unshifted
  `! @ # $ % ^ & * ( )` with `\` at pos 11; HEAVEN's numpad is plain `N1`…`N0`
  (not keypad codes — the dump renders keypad as raw `p7uNN`, only `KP_DOT` at
  the outer thumb is one), so shift+numpad composes the same ten symbols.
  Under Russian the row types `!"№;%:?*()` — exactly the five cells above.
- `.keylayout` file: not started. Blocked on the RU `?` `:` `"` question.
- Backtick, tilde, quotes, brackets have no seat on the board right now
  (backtick sits on CURSE under the Space seat, unreachable). Positions are a
  separate fight, explicitly deferred by bekh.
- `zmkctl kp L POS NAME` binds a plain key press by ZMK's own keycode names
  (`EXCL`, `ATSN`, `HASH`, `DLLR`, `PRCNT`, `AMPS`, `ASTRK`, `LPAR`, `RPAR`;
  `^` has no name in the enum, use `0x2070023`).
