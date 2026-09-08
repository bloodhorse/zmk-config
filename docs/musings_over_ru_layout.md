# musings over the RU layout

A custom ЙЦУКЕН `.keylayout` so that symbol keys give the same glyph regardless
of which language macOS is in. **Built 2026-09-08, not yet cut over** — pick up
from "Where it stands".

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
`\`, **the keypad page, and a handful of spare keycodes no key on the board
sends** (see below). Anything we want predictable across languages has to
arrive on one of these.

## What was measured (2026-09-08)

Everything here comes from asking macOS itself — `keylayout/dumplayout.swift`
runs UCKeyTranslate over all 128 virtual keycodes × 32 modifier states for a
named input source. No guessing from tables on the internet.

- **Shifted digits in RussianWin:** `2→" 3→№ 4→; 6→: 7→?`. The other five
  (`! % * ( )`) already agree with ABC.
- **The keypad page is uniform except one cell:** `KP_SLASH KP_ASTERISK
  KP_MINUS KP_PLUS KP_EQUAL` and the digits are identical in both layouts.
  **`KP_DOT` (keycode 65) is `,` in RussianWin** — the Russian decimal comma.
  HEAVEN's outer thumb has been typing a comma in Russian all along.
- **F21–F24 do not exist as macOS keycodes.** Carbon's table ends at
  `kVK_F20 = 0x5A`; the HID usages are swallowed. Spares have to come from
  slots macOS *does* assign.
- **Spare keycodes** — empty or junk in both layouts, with the HID usage the
  board sends to reach each (ZMK name):

  | keycode | HID | ZMK | ABC | RussianWin |
  |---|---|---|---|---|
  | 94 | 0x87 | `INT_RO` | — | ё (junk) |
  | 93 | 0x89 | `INT_YEN` | — | ё (junk) |
  | 95 | 0x85 | `KP_COMMA` | — | — |
  | 10 | 0x64 | `NON_US_BSLH` | `§` | ё (junk) |
  | 114 | 0x75 | `K_HELP` | ^E | ^E |
  | 102 / 104 | 0x91 / 0x90 | `LANGUAGE_2 / _1` | fn-marker | fn-marker |
  | 107 / 113 | 0x69 / 0x6A | `F14 / F15` | fn-marker | fn-marker |

  Nine slots, and shift doubles them. Four are used; the rest are reserve.
- RussianWin has no dead keys; every output is a single character.

## The design, as built

Three mechanisms, each used where it is the cheapest correct one:

1. **Keypad page** — `/ * - + =` and digits need nothing. Outsource `/` to a
   layer as `KP_SLASH` and it is `/` in both languages. (Not yet bound anywhere.)
2. **Custom RU layout, `keylayout/RussianWinPlus.bundle`** — Apple's
   RussianWin with a **57-cell delta** (`keylayout/verify.sh --delta` lists
   every one). In plain words:
   - shift+`2 3 4 6 7` → `@ # $ ^ &`. Casualties: RU `" № ; : ?` on those seats.
     `№` had zero presses in July; the other four come back on spares.
   - `KP_DOT` → `.` — the keypad page becomes the uniform zone it was
     supposed to be.
   - spares get their Russian meaning: `INT_RO → ?`, `INT_YEN → :`,
     `KP_COMMA → "`, `NON_US_BSLH → ;`.
   - **Nothing else moves.** ё stays on the backtick key (bekh parked
     backtick), `х ъ ж э` keep their seats (bekh dropped brackets rather than
     fight for them).
3. **Karabiner, EN half of the spares** — one rule at index 0, gated `^en$`:
   `international1 → shift+slash`, `international3 → shift+semicolon`,
   `keypad_comma → shift+quote`, `non_us_backslash → semicolon`. Under ABC
   the same spare produces the same glyph the RU layout gives it. The pair is
   what makes a spare-fed symbol uniform. **Live since 2026-09-08, inert until
   a layer sends those usages.**

The two halves meet on the board: a layer cell that sends `INT_RO` types `?`
in both languages. Base pos 35 (today `LS(N7)` + Karabiner rule 12) becomes
`INT_RO` at cutover — and rule 12 goes, because with RU shift+7 now `&`, that
rule was the last thing making EN shift+7 differ from RU.

Rejected on the way, for the record: alt+digit as a symbol layer (AeroSpace
owns alt+1-5); a custom EN layout as well (the Karabiner half does the same
job where every other EN remap already lives); the "full size" bare-row-symbols
plan (it needed two files and a device_if rule for the MacBook's own row, and
the spares make it unnecessary).

## Mechanics

- **Generator, not a hand-edited file:** `.venv/bin/python keylayout/gen_layout.py`
  dumps the RussianWin installed on this Mac and applies `DELTA` — the delta is
  the design, one screen long, at the top of the script. Output is the
  `.bundle` (Info.plist gives it the id `org.bekh.keylayout.RussianWinPlus`
  and language `ru`; the id keeps the substring "Russian" because ru_border
  greps for it) plus `expected.json` for the verifier.
- **XML 1.1 on purpose.** Control-character references (`&#x0008;` for
  backspace) are legal in 1.1 and rejected in 1.0; Apple's own layouts declare
  1.1 for the same reason. `xmllint` does not speak 1.1 — validate the
  *structure* with the control refs masked (verify.sh does not need to; the OS
  is the real oracle).
- **Install:** `rsync -a --delete keylayout/RussianWinPlus.bundle ~/Library/Keyboard\ Layouts/`
  then **log out and back in** — TIS rescans the directory on the spot (it even
  logs it) but a new *bundle* does not enter the source list until the login
  session restarts. Nothing short of that refreshes it.
- **Verify:** `keylayout/verify.sh` → MATCH/MISMATCH, comparing the installed
  layout cell by cell against `expected.json` through the same UCKeyTranslate
  call the generator used to read Apple's. Exit 2 = not visible yet.
- **`keylayout/tis`** (`tis.swift`): `list | enable | disable | select` an
  input source by id. **`disable` on the selected source does not fail — macOS
  silently selects another.** Always `select` the one you want active first.
  That was learned by knocking bekh into Russian for ten seconds.
- **Cutover / rollback are one command each:** `keylayout/cutover.sh`
  (verify → enable new, select ABC, disable RussianWin → Karabiner id refs +
  drop rule 12, committed and pushed → board pos 35 `INT_RO`) and
  `keylayout/rollback.sh` (board back to `LS(N7)` → `git revert` the cutover
  commit → RussianWin back on, RussianWinPlus off). The bundle stays installed
  either way; removing it would need another logout to mean anything.

## Why the unshifted row got reverted (2026-09-02)

The row ran as unshifted `! @ # $ % ^ & * ( )` for an evening. It fell to
cmd+digit: bekh uses cmd+1…9 constantly (tabs, workspaces), and a seat that
sends shift+digit makes that cmd+shift+digit. Two fixes exist, neither free:

- **Karabiner** — `cmd+shift+digit → cmd+digit`, ten manipulators, trivial.
  But it eats every real cmd+shift+digit too, and cmd+shift+3/4/5 are macOS
  screenshots; Karabiner cannot tell "cmd on the `$` seat" from a genuine
  cmd+shift+4 — same event. Only viable if the screenshot chords move.
- **Board mod-morph** — a per-seat behavior: plain digit while cmd is held,
  shifted symbol otherwise (`mod-morph`, mods `MOD_LGUI|MOD_RGUI`, ten nodes
  or one parametrised via `keep-mods`). Correct and lossless, but it is a
  compiled behavior: edit keymap → build → flash → bind over RPC.

bekh's call: not ready to solve it, revert to digits, decide later. The
mod-morph is the answer when he is.

## Where it stands (2026-09-08)

- **Bundle built, validated, installed to `~/Library/Keyboard Layouts`, not
  yet visible** — this login session predates the install. The next step is
  bekh's: **log out, log in, run `keylayout/verify.sh`**. MATCH → run
  `keylayout/cutover.sh`. Anything else → stop, read the cells it prints.
- Karabiner half of the spares is live (rule 0). Rule 12 (`shift+7 → ?`) is
  still in place until cutover removes it.
- Board: base pos 35 is still `LS(N7)`; cutover rebinds it to `INT_RO` and
  the mirror in `config/lily58.keymap` must follow by hand. `shit` layer row 1
  already carries shift+digit cells (`RS(N7)` on the `&` seat to dodge rule
  12 — once rule 12 is gone that dodge is cosmetic; leave it or normalise to
  `LS(N7)`, either verifies).
- Not bound anywhere yet, both free to place on a layer whenever: `KP_SLASH`
  (uniform `/`), and the spares `INT_YEN` `KP_COMMA` `NON_US_BSLH` for
  uniform `: " ;`. `INT_RO` takes pos 35 at cutover.
- Untested until real fingers: whether any app treats a spare-fed keypress as
  something other than text (keycode 114 is "Help" and 102/104 are JIS
  IME keys — with no Japanese IME installed they should be inert, and the
  four spares in use avoid them anyway); and modifier composition through a
  spare (cmd+? etc. — the physical key still works regardless).
- `zmkctl kp L POS NAME` binds by ZMK's own keycode names (`NUM_1`…`NUM_0`,
  `EXCL`, `ATSN`, `HASH`, `DLLR`, `PRCNT`, `AMPS`, `ASTRK`, `LPAR`, `RPAR`,
  `GRAV`, `TILD`, `DQT`, `APOSTROPHE`, `LBKT`, `RBKT`, `LBRC`, `RBRC`, `BSLH`,
  `INT_RO`, `INT_YEN`, `KP_COMMA`, `NON_US_BSLH`; `^` has no name, use
  `0x2070023`). **The `Keycode` enum is closed** — a modifier combination it
  has no member for (e.g. `RS(N7)`) fails in `kp`; write it raw:
  `zmkctl set L POS "Key Press" $((0xMMPPIIII)) 0`.
