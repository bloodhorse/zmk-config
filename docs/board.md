# Working the board

How a change gets onto the Lily58 and stays true: RPC vs build, flashing,
`zmkctl`, and the Studio/api/CI traps that have already cost time.

## Runtime or build

- **Runtime**: `&kp`, `&mo`, `&tog`, and any binding of a behavior that
  already exists in firmware. Set over Studio RPC with `tools/zmkctl.py`; it's
  live in seconds and reverts in seconds.
- **Build**: a genuinely new behavior (a mod-morph, a hold-tap with a new
  flavor or term, a `conditional_layers` node). Edit the keymap, push, let
  GitHub Actions build, flash both halves, **then bind over RPC** wherever a
  cell had been edited before. A conditional_layers node needs no rebinding,
  because it lives in firmware, not settings.

Hold terms are tuned at runtime because the hold-taps come as ladders,
compiled once at several terms:

- `ltb200…ltb360`: layer hold, balanced, quick-tap 200. Enter and the FUCK doors.
- `mtb240/280/320`: mod hold, balanced, quick-tap 200. Space = `mtb280 LALT SPACE`.
- `gtog*`, `motog`: unused. They stay compiled because pruning shifts ids.

Retuning a key is rebinding it to another rung:
`zmkctl set 0 53 mod_tap_balanced_320 LALT SPACE`.

Balanced, in one table:

```text
other key pressed AND released while held -> hold, no wait
held key released first (fast roll)       -> tap
held alone past the term                  -> hold
released alone within the term            -> tap, on release
```

The term's only real job is how long a solo press may dwell before the tap is
forfeited. If spaces vanish, go one rung up.

## Studio's saved state

- Studio's flash settings **override** the keymap file's defaults, even right
  after a reflash. The file only starts mattering on the day of a build, so it
  has to be true before one.
- Saved state holds only the cells someone edited. An untouched cell follows
  the firmware default and picks up a new keymap value on flash with no RPC.
- Saved bindings reference **behavior ids**, which come from devicetree order.
  Appending new behaviors at the end of `behaviors` leaves every saved binding
  intact. Pruning or reordering shifts the ids under them, so don't.
- A Studio GUI edit never reaches the repo. `verify` is the only bridge.

## zmkctl

```bash
.venv/bin/python tools/zmkctl.py dump                 # all layers as grids
.venv/bin/python tools/zmkctl.py verify               # MATCH / MISMATCH vs the keymap file
.venv/bin/python tools/zmkctl.py get L POS            # one cell
.venv/bin/python tools/zmkctl.py behaviors            # id + node name of every behavior
.venv/bin/python tools/zmkctl.py kp L POS NAME|0x…    # plain key press, saved
.venv/bin/python tools/zmkctl.py set L POS NODE P1 P2 # custom behavior, saved
```

Positions are row-major: `0-11` number row, `12-23` top, `24-35` home, `36-49`
bottom incl. the center keys 42/43, `50-57` thumbs (left 50-53, right 54-57).

`verify` compares all 58 positions on every bound layer as numeric
`(page, id, mods)`, never display names. If it says MATCH, a reflash or a
settings wipe costs nothing but BT bonds.

- **Baked chords go in as hex.** The api's `Keycode` enum only knows named
  values, so `LA(LG(C))` raises `ValueError` through `KeyPress`. `kp` sends any
  `0x…` as `Raw`. Layout: mods in the top byte (LC 01, LS 02, LA 04, LG 08,
  right-hand mods 10/20/40/80), then page `07`, then the id. So `LA(LG(C))` is
  `0x0C070006`.
- `set` takes keycode names for both params (`set 0 53 mod_tap_balanced_280 LALT SPACE`).
- The usbmodem node moves between ports. `zmkctl` globs for it and
  `ZMKCTL_SERIAL` overrides.

## Flashing

Only the left half (central) exposes Studio's serial port, so all `zmkctl`
work happens with the left half on USB. The bootloader mounts as
`/Volumes/NICENANO`. A background loop that waits for the mount and copies
`lily58_{left,right}_nice_oled.uf2` in turn lets bekh just double-tap.
The board can't be read once it's in bootloader mode, so run `verify` before
bekh double-taps.

## Traps

- **Wiping saved settings: ask at the moment of doing it, even when it's in
  the plan.** `settings_reset.uf2` erases the saved keymap AND every Bluetooth
  bond, including the halves' bond to each other, so wiping one half forces
  the same wipe on the other. The api's `reset` call should restore the keymap
  to firmware defaults without touching bonds. It's untested here, so try it
  first. Either way `verify` must say MATCH first.
- **Layers are Studio-GUI-only, and they're sticky.** The api (`zmk-studio-api`
  0.5.1) has get/set key, save, discard and reset, but no add, rename, remove
  or reorder. Adding or naming a layer is bekh in the GUI, then the agent binds
  cells over RPC. Read names back from `get_keymap_bytes` (the printable runs,
  in slot order). A layer deleted in Studio comes back on a reflash while the
  keymap file defines it. One added in Studio can't be deleted from the GUI at
  all: removing it takes a build without it plus a reset of the saved keymap.
  This firmware has no spare layer slot, so a sixth layer is a build.
- **A layer Studio created holds zeroed bindings, and they fall through.** Its
  cells read back as `Unknown { behavior_id: 0 }`, which acts as `&trans`, not
  `&none` (ZMK v0.3.0 `behavior.c` returns 1 for a missing behavior). `verify`
  names them `&none` only as a convention. In the keymap file, write them as
  `&trans`.
- **A `conditional_layers` node owns its then-layer.** ZMK deactivates the
  then-layer whenever the if-layers aren't all held, so any other door to that
  slot opens and closes in the same tick, silently. None is compiled in now.
- **Studio holds the serial port exclusively**, and it relaunches itself and
  grabs the port again mid-session. Re-run the kill (in `CLAUDE.md`) before
  every `zmkctl` call.

## Pushing the keymap

- **The keymap-drawer Action rewrites the commit you just pushed.** On any push
  touching `config/*.keymap` it regenerates `keymap-drawer/lily58.{svg,yaml}`,
  amends them into your commit and force-pushes. After every keymap push, wait
  for the run, then `git fetch origin && git reset --hard origin/main`. Never
  merge or pull: the remote commit already contains yours.
- **Push once.** A second push within ~40s makes the drawer's
  `--force-with-lease` amend fail: the commits land, the run goes red, and the
  SVG is silently stale. Stack local commits and push them together. If it
  happened anyway:

  ```bash
  gh workflow run "Draw ZMK keymaps" --ref main   # wait for it, then:
  git fetch origin && git reset --hard origin/main
  ```
