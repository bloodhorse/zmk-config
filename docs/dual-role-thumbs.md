# Dual-role thumbs — what's known

Working notes for the standing question: **can Space and Enter carry a second
meaning on hold, and what belongs there?** Facts only — measurements, mechanism,
and what's been settled. Opinions live in the chat, not here.

Everything measured comes from [`../stats/keycount-2026-07.md`](../stats/keycount-2026-07.md).

## Mechanism — the hard limits

- **A key that means two things must delay one of them.** A hold-tap's *tap*
  fires on **release**, not press. The cost equals your own dwell on the key,
  ~30-80ms. Irreducible: the board cannot send Enter on press and take it back.
- **`&mo` has no tapping term.** A momentary layer engages the instant it is
  pressed. The thumb layers as they exist today are already zero-delay.
- **Mod-morph has no tapping term either.** It reads modifier state at press
  time and branches immediately. Nothing waits.
- **Exactly two zero-delay ways to give a key a second meaning:** a key that
  does nothing else, or a modifier that is already held. There is no third.
- **`hold-trigger-key-positions` is a whitelist, not a bilateral rule.** It
  names which keys may cause a hold. Same-hand whitelists are legal — one-handed
  chording survives it. Bilateral combinations are one *use* of the property.
- **`require-prior-idle-ms`** short-circuits to tap-on-press when the previous
  key was recent. It removes felt latency inside a typing burst — at the price
  of behavior that depends on *how fast you were*. Rejected here on purpose:
  unpredictable-by-timing is worse than a constant cost.
- **Long tapping-term + positional whitelist** makes the outcome depend on
  *which key came next*, never on a clock. That is the shape to build.

## Measured — the two worst keys on the board for this

Cost of a dual-role key ≈ **tap frequency × latency**, plus misfires.

```
Space   421/day     Enter   382/day     Backspace  370/day
F13     335/day     Escape  260/day
-      15.2/day     ?       8.3/day     =          2.0/day
```

- Space and Enter are #1 and #2. Whatever sits behind the hold, the tap tax is
  charged on every one of those presses.
- **Cold content behind the hold does not reduce the tap tax.** It reduces
  *misfires*. Those are two separate bills.
- `=` (2.0/day) is the cheapest dual-role candidate on the board by frequency —
  and unusable for one-handed arrows, see geometry below.

## Geometry — why the seat arithmetic is closed

- Thumb mirror pairs: `50↔57, 51↔56, 52↔55, 53↔54`.
- Eight thumb seats, eight needs: SPACE, RET, BSPC, LALT, LGUI, RGUI, CURSE,
  HEAVEN. No slack. CURSE/HEAVEN symmetry can only be bought by demoting
  something else.
- **Only a thumb can hold a key while that same hand's fingers type.** So
  one-handed arrows *require* the trigger under the right thumb. Center keys
  (`=`/`-`) are finger keys — holding one occupies the hand that would press
  the arrows.
- The Lily58 thumb row is four keys in a straight line; realistically only the
  inner two are thumb-reachable. The outer two need a bend. This is the shape's
  known weakness, not a technique problem.

## Setup facts that bite

- **Two alphabets are in play and they look identical in writing.** Karabiner
  rules are written in QWERTY scancodes; bekh reads and speaks Gallium letters.
  The arrow cross below is one set of physical keys under two names — get this
  wrong and a conversation about bindings becomes nonsense:

  ```
  gallium   O    H    A    E    K        (what bekh sees and says)
  scancode  i    j    k    l    n        (what a Karabiner rule says)
  action    ↑    ←    ↓    →   F13
  ```

  Full table: the `Gallium Colstag (Lily58 Only)` rule in `karabiner.json`.
- **A rule placed above the Gallium rules is layout-independent** — it sees raw
  scancodes, so it behaves identically under EN and ЙЦУКЕН. Placed below, it
  fires on the wrong physical keys under EN only. Above is both correct and
  bilingual; there is no reason to put a physical-key rule below.

- **Karabiner carries 30 complex-modification rules.** Alpha remapping (Gallium
  Colstag, Colemak Mod-DH) is gated `input_source_if ^en$` and device-scoped, so
  **none of it fires under ЙЦУКЕН** — positional reasoning about Cyrillic holds.
- **Karabiner rules get edited and enabled directly — never handed back to the
  GUI.** Enabling is inserting the rule object into
  `profiles[0].complex_modifications.rules` at the index that gives it the right
  precedence; back up the file first and it is as reversible as anything else.

- **A rule present in `karabiner.json` proves nothing.** The space dual-role sat
  there inert for the whole investigation because it was disabled in the UI.
  Verify by pressing keys, never by reading config.
- `Right Option → double left_shift (Caramba)` — RAlt is bound, not free.
- Karabiner's `to_if_alone` is **stricter than ZMK's whitelist**: any intervening
  key swallows the tap entirely. ZMK would emit the tap and then the key.
  Consequence on Space→Command: a fast roll from space into the next letter
  yields `cmd+letter` and **no space**. `cmd+W` and `cmd+Q` are one roll away
  from a closed tab or a quit app, and English is full of `w` after a space.
- **ZMK Studio can only assign behaviors that already exist in firmware.** New
  behaviors (mod-morph, hold-tap variants) need a reflash. Behavior IDs come
  from devicetree order, so deleting one later probably shifts the rest under
  Studio's saved bindings — plan on prune = reflash + rebind, or don't prune.
- Studio's flash state overrides keymap defaults, so `config/lily58.keymap` only
  matters on the day of a reflash. `zmkctl verify` is what keeps it honest.

## Where it landed

The thumb row, and why each seat is what it is:

```
50 CURSE   51 LGUI   52 LALT    53 SPACE / hold = CURSE
57 RGUI    56 BSPC   55 RAlt    54 ENTER / hold = HEAVEN
```

- **`?` on pos 35**, the dead right-CTRL seat. It had to be a *modifier* seat:
  modifiers don't change with the host input source, and every symbol seat on
  the right half is a live Cyrillic letter under ЙЦУКЕН. Karabiner's EN-gated
  `shift+7 → ?` rule covers the other language, so one key serves both.
- **RAlt at seat 55**, mirror of LAlt at 52 — the symmetry the whole endeavour
  was chasing. It only became affordable once arrows stopped needing a layer key.
- **Arrows and F13 hang off RAlt in Karabiner**, mod stripped: `RAlt + O/H/A/E`
  (gallium) and `RAlt + K` for whisper, `RAlt + Enter` for `'`. Zero delay,
  one-handed, and above the Gallium rules so it is identical in both languages.
  F13 is off the board entirely; the dead `|` on HEAVEN went with it.
- **Space and Enter hold the two layers**, via `lt_curse` / `lt_heaven` in the
  keymap — `hold-preferred`, a position whitelist, and `tapping-term-ms = 1000`
  so the only remaining timer branch never fires by accident. Whitelists are
  derived from the board (every non-transparent position on the target layer),
  not hand-picked: **add a key to a layer, add its position to the whitelist.**
- **Seat 50 and pos 11 keep board-side doors** to the same two layers. Redundant
  and free, and they are the floor if anything upstream breaks.

The design rule underneath all of it: **hot key, cold hold.** SpaceFN earns its
bad reputation from people putting arrows and backspace behind Space. Only
deliberate, never-in-a-roll content goes behind a hold — which is exactly why
arrows had to leave HEAVEN before Space could carry a layer at all.

## Still open

- **Does the tap-on-release cost on Space register in daily use?** It is
  constant, ~your dwell time, and paid on all 421 presses. The one thing only
  a week of typing can answer.
- **What else belongs on those two layers.** `media_layer` (layer 3 —
  brightness, keyboard illumination, volume, transport) is built, flashed, and
  **still unreachable — nothing points at it.** Cold by nature, zero misfire
  surface, the obvious next tenant.
- **HEAVEN pos 2 is a bare Keypad @ that macOS ignores**, and pos 1 is blank.
  Reads like a Studio slip that ate F14/F15. Restore or clear, undecided.
- Seat 50 is redundant now. Reclaiming it would let `LGUI↔RGUI` and
  `DEL↔BSPC` mirror too, making all four thumb pairs symmetric — at the cost of
  CURSE's board-side door.
