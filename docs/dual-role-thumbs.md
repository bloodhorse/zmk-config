# Dual-role thumbs

The standing question: **can a thumb key carry a second meaning on hold, and
what belongs there?** Mechanism, measurements, and where it landed. Read
before reseating any thumb or putting a hold on any key.

Measurements come from [`../stats/keycount-2026-07.md`](../stats/keycount-2026-07.md).

## Mechanism: the hard limits

- **A key that means two things has to delay one of them.** A hold-tap's tap
  fires on **release**, not press. The cost is your own dwell on the key,
  ~30-80ms, and it's irreducible: the board can't send Enter on press and take
  it back.
- **`&mo` and mod-morph have no tapping term.** A momentary layer engages on
  press; a mod-morph reads the modifier state at press time and branches
  immediately.
- **There are exactly two zero-delay ways to give a key a second meaning:** a
  key that does nothing else, or a modifier that's already held. No third.
- **`hold-trigger-key-positions` is a whitelist**, not a bilateral rule:
  same-hand whitelists are legal. Whitelist + long term decides by *which key
  came next*, never a clock, but the whitelist is compiled in, so every key
  added to a layer costs a build. Balanced + a timer decides most cases by key
  order too and needs no whitelist, so every layer edit is pure RPC. The board
  ran the whitelist shape first and dropped it: the build tax bit on every
  layer edit, while slow typing makes the timer's misfire window cheap.
- **`require-prior-idle-ms`** turns a hold-tap into tap-on-press when the
  previous key was recent. That removes felt latency inside a typing burst, at
  the price of behavior that depends on how fast you were going. In use on
  every door, paired with hold-preferred (below).
- **Balanced loses fast hotkeys.** It reads a flick that lets go of the door
  before the target (door down, key down, door up, key up) as typing, and a
  quick chord ends before the term can rescue it. Hold-preferred takes the
  hold the moment another key goes down; the prior-idle window is what keeps
  that from turning prose rolls into chords.
- **Karabiner's `to_if_alone` is stricter than ZMK**: any intervening key
  swallows the tap entirely. A Space→Command dual in Karabiner turns a fast
  roll into `cmd+letter` and no space, and `cmd+W`/`cmd+Q` are one roll away.
  Holds belong on the board.

## Measured: the two worst keys on the board for this

Cost of a dual-role key ≈ **tap frequency × latency**, plus misfires.

```text
Space   421/day     Enter   382/day     Backspace  370/day
F13     335/day     Escape  260/day
-      15.2/day     ?       8.3/day     =          2.0/day
```

- Space and Enter are #1 and #2, so the tap tax is charged on every one of
  those presses, whatever sits behind the hold.
- **Cold content behind the hold doesn't reduce the tap tax.** It reduces
  misfires. Those are two separate bills.

## Geometry

- Thumb mirror pairs: `50↔57, 51↔56, 52↔55, 53↔54`. Left thumb is 50-53.
- **Only a thumb can hold a key while the same hand's fingers type.** The
  center keys (`=`/`-`) are finger keys: holding one ties up the hand.
- The thumb row is four keys in a straight line, and realistically only the
  inner two are thumb-reachable; the outer two need a bend. That's the shape's
  known weakness, not a technique problem.

## Where it landed

```text
50 shit    51 LCTRL   52 LGUI    53 SPACE / hold = LALT
57 shit    56 BSPC    55 RGUI    54 ENTER / hold = HEAVEN
```

- **Space holds a real Left Alt** (`mtp150`). Every alt chord works without a
  cell and every mod stacks in any order, which made CURSE's baked alt cells
  pointless.
- **Enter holds HEAVEN** (`ltp150 2 RET`).
- **shit on both outer thumbs**, plain `&mo`: zero delay, and the bend to the
  outer seat doesn't matter for a deliberate layer.
- The home-row pinkies (24, 35) hold F20, hyprshit's `fuck`, on the same
  regime (`mtp150 F20`). They
  tap `~` and `?`, both rare enough that losing key repeat costs nothing.

The design rule underneath: **hot key, cold hold.** SpaceFN earns its bad
reputation from people putting arrows and backspace behind Space. Only
deliberate, never-in-a-roll content goes behind a hold; a real modifier
qualifies because it's always chorded.

## Still open

- **Does the 150 ms idle window wear well?** Watch for two things: a space
  after a pause that rolls into the next word and comes out as an alt chord
  (go to `200`), and a hotkey fired right after typing that comes out as a
  space (go to `100`). A solo press dwelling past 280 still eats the tap, on
  every door.
