# The screens

Both halves carry a 0.91" SSD1306, 128x32, mounted portrait. They show our own
status screen: the void's star (`thevoid/mock/mark.html`, the pentagram with
its tips skewed to bekh's drawing), one per panel, 35% wider than the glass so
the arms are always cut, a full turn every 30 seconds. No info on them at all:
bekh looks at them for the vibe, and he turned down layer names, wpm, battery
and a language flag.

## The pipeline

- `oled/gen.py` draws every animation once as 1-bit 32x128 portrait frames
  (supersampled 8x, thresholded). It writes `oled/frames.js` for the emulator
  and, for the one named in `FIRMWARE`, `oled/fw/star_frames.{c,h}`.
  Run: `uv run --with pillow python oled/gen.py`.
- `oled/emu.html` (open the file in bare): both panels big, and a schematic
  Lily with them at true scale; per-half animation, panel colour, glow,
  speed, and a burn map (`b`) showing how much of the loop each pixel is lit.
  The emulator plays the same bytes the firmware gets, so a flash only checks
  orientation and pace.
- `oled/fw/stars.c` is the whole screen: an `lv_img` and an `lv_timer` that
  steps through the frames. It comes in through the module's cmake
  (`zephyr/CMakeLists.txt`), guarded on `CONFIG_ZMK_DISPLAY_STATUS_SCREEN_CUSTOM`.
- Then `tools/build.sh`, `make flash` (`docs/board.md`).

## What the glass confirmed

- **Rotation**: the panel is landscape; portrait is a quarter turn clockwise,
  the way nice_oled did it, so portrait (x, y) lands on landscape (127 − y, x).
  Portrait up is the same on both halves.
- **Palette**: the panel node has `inversion-on`, so in LVGL white is dark and
  black is lit. Each frame is `LV_IMG_CF_INDEXED_1BIT` with index 0 white,
  index 1 black, and a set bit is a lit pixel. The screen's background is set
  white for the same reason.
- 520 bytes a frame; the 180-frame star costs ~92 KB, left half at 51% flash.

## Gotchas

- **Nothing static on the glass.** A pixel lit all day burns in; the burn map
  is how to check a new design before it ships. The star's middle is empty
  (it's a stroke) and its lines sweep every pixel they touch.
- **Motion everywhere is too much.** A stream of stars drifting down the whole
  strip (`star-drift`) worked on the glass and bothered bekh within minutes:
  peripheral vision is built to catch motion. One slow star in place is the
  answer for now; if that's still too much, slow it further before anything else.
- **The halves don't stay in step.** Each runs its own timer and blanks on its
  own; true lockstep would need a split message. Not wanted so far.
- **What's out there was already tried.** nice_oled's menu (cat, gem, head,
  spaceman, pokemon, Luna, bongo cat) and the QMK collections hold nothing
  better for a vertical 32x128; bekh wanted bitmaps, not procedural code.
