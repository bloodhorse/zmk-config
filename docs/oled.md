# The screens

Both halves carry a 0.91" SSD1306, 128x32, mounted portrait. They show our own
status screen, and no info at all: bekh looks at them for the vibe, and he
turned down layer names, wpm, battery and a language flag.

## What's on them

Four patterns, the same four on each half, cycled in this order:

- **storm**: slow rain, sixteen drops, most of them streaks, falling as a
  background that never hears the keys. Over it, lightning: every keypress
  strikes with a chance of one in 4 (`STRIKE_EVERY`), so a bolt lands about
  every 4th key and never on the beat. A strike flickers (strike, dark, strike
  again) and crumbles away over ~0.8 s; a hit during a strike queues the next.
  The lightning is bekh's favourite.
- **wire**: ticker tape crawling up out of a punch; every key punches a row of
  five holes, bursts pull the tape through fast, pauses leave it blank.
- **stars**: the baked column of three stars; one key turns it one frame (5°),
  and at rest it creeps one frame a minute so nothing sits still till blanking.
- **gem**: nice_oled's crystal, 16 frames at ~17 fps, its long axis down the
  strip, as the old peripheral screen showed it, without the battery and
  bluetooth rows.

The left starts on storm, the right on gem. **fuck+1 turns the left screen,
fuck+0 the right** (either pinky). Each half saves its pick (`oled/pick` in
settings), so it survives a reboot and a flash. **Both hands drive both
screens.** Idle blanking is 10 min.

## How it works

- `oled/live.js` is where patterns are designed: small programs, one tick per
  50 ms, drawing a 32x128 1-bit buffer, written in plain integer math and one
  xorshift so they port to C line for line.
- `oled/fw/screen.c` is that port, and the whole screen: an `lv_img` fed from a
  portrait buffer turned a quarter turn on the way out, an `lv_timer` at 50 ms,
  and a push to the panel only when the frame changed. It listens to
  `zmk_position_state_changed` for the keys and the switcher.
- **The keys reach both halves.** A half natively hears only its own matrix.
  The central hears both (the peripheral's presses arrive as events with a
  non-local source) and hands each of its own presses across by invoking
  `&scr_k`, a zero-param behavior with global locality, so the split carries
  it to the peripheral with the position in the event. One small message per
  left-hand keypress.
- **The switcher lives in `screen.c`, not the keymap.** The board doesn't know
  fuck (the pinkies send F20 and the mac makes fuck of it), but the central
  sees the pinky positions (24, 35) go down, so pinky held + pos 1 calls
  `oled_screen_next()` and pinky + pos 10 invokes `&scr_r`, which the split
  hands to the right half. The mac still gets F20+1 / F20+0, bound to nothing
  (`docs/chords.hand` lists them as the board's).
- `&scr_l` / `&scr_r` (Studio: "Left Screen", "Right Screen") are also
  bindable on any key; nothing binds them now. Behavior ids 45, 46, 47
  (`scr_k`). Node names stay under 9 characters: the split hands a behavior to
  the peripheral by name.
- `oled/gen.py` bakes the frame animations (1-bit 32x128 portrait, supersampled
  8x, thresholded) into `oled/frames.js` for the emulator, and the two the
  firmware uses (`star-column` and `gem`) into `oled/fw/frames.{c,h}`.
  The gem's source is `oled/assets/crystal.c` (MIT, credited in the file).
  Run: `uv run --with pillow python oled/gen.py`.
- Code comes in through the module's cmake (`zephyr/CMakeLists.txt`); the
  behaviors' bindings live in `dts/bindings/`, found through `dts_root` in
  `zephyr/module.yml`.
- Then `tools/build.sh`, `make flash` (`docs/board.md`).

## The emulator

`oled/emu.html`, opened in bare. Both panels big plus a schematic Lily at true
scale. Live patterns and baked loops in one list per half; typing anywhere on
the page is keypresses; a simulated typist; speed up to 600x so the burn map
can live through a day; a `strike` button; the strike rate slider; an "each
hand drives its own screen" box (off: both hands drive both, as the board
does). For a live pattern the burn map counts since reset. A change goes
emulator first, then `screen.c`.

## What the glass confirmed

- **Rotation**: the panel is landscape; portrait is a quarter turn clockwise,
  so portrait (x, y) lands on landscape (127 − y, x). Portrait up is the same
  on both halves.
- **Palette**: the panel node has `inversion-on`, so in LVGL white is dark and
  black is lit. The image is `LV_IMG_CF_INDEXED_1BIT` with index 0 white,
  index 1 black, a set bit lit, and the screen's background white.
- Flash: left 45%, right 37%. The baked frames cost 44 KB.

## Gotchas

- **The display must run on its own thread** (`ZMK_DISPLAY_WORK_QUEUE_DEDICATED`
  in `config/lily58.conf`). On the system work queue every frame's i2c push
  stalls the matrix scan, and the board goes sluggish and drops quick double
  taps. nice_oled's defconfig used to set this quietly, so dropping the shield
  dropped it too.
- **Nothing static on the glass.** A pixel lit all day burns in; check every
  design on the burn map. The gem lights some pixels in every frame (100%);
  it ran that way for months under nice_oled, and the fix if it ever matters
  is a slow drift.
- **Motion everywhere is too much.** A stream of stars down the whole strip
  bothered bekh within minutes: peripheral vision is built to catch motion.
  What works is motion the hands cause (the brain discounts it) or a slow
  background.
- **A timed lightning never fires.** Strikes on a clock (about two an hour,
  more with a typing "charge") were impossible to see; striking off the keys
  is what made it.
- **Dead ends, so nobody walks them twice:** sand (every key a grain piling
  up; the pile's bottom rows lit ~99% of the day, and bekh called it
  bollocks), specks drifting in the lightning's sky ("weird"), the gem
  stretched lengthwise (doubled lines), a single endlessly spinning star (it
  distracted), matrix rain and noise (5 characters wide reads as noise;
  noise is agitated).
- **What's out there was already tried.** nice_oled's menu and the QMK
  collections hold nothing better for a vertical 32x128.
