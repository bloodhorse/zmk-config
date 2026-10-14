# Karabiner

The macOS half of the keyboard: what belongs there, how to edit it, and the
rules that make up the live stack. Read before touching any rule.

## Where a thing belongs

- **The board owns anything physical**: layers, key positions, hold behavior.
  It travels with the keyboard, and it's the one source of truth.
- **Karabiner owns anything that depends on macOS state**: the active input
  source, the app, which device sent the event. The board can't see any of
  it. The EN-gated `shift+7 → ?` rule is the standing example: it's why one
  physical key gives `?` in both languages.

Don't emulate a layer in Karabiner. It has no layers, only variables, so a
layer turns into N hand-enumerated conditional remaps: a second copy of the
layout that will drift from the first.

The one deliberate exception is **"Lily58: alt numpad + …"**. When Space
became a real Alt, CURSE's non-alt cells moved there as static option remaps
scoped to the Lily58. Alt plus the right-hand block types bare digits (`0` on
alt+RGUI), alt+Enter types `'`, and alt+`=` sends alt+Space (the launcher).
It's ten-odd remaps that won't rot. The left-hand Enter is the global
alt+v = Enter rule.

## Editing

**`~/.config/karabiner` is a git repo in place** (`bloodhorse/karabiner`): the
live directory *is* the repo. bekh edits Karabiner only from sessions in this
project, so the agent is the committer:

- run `git -C ~/.config/karabiner status --short` first. Anything dirty gets
  swept into the next commit with a message that says what it was
- **commit and push right after each edit**, not at session end. A session
  can die mid-way
- no `.bak` files. Git is the history (`automatic_backups/` is ignored,
  `assets/complex_modifications/` is tracked)
- rollback: `git -C ~/.config/karabiner checkout HEAD~1 -- karabiner.json`.
  Karabiner reloads on its own

Rules get edited and enabled directly, never handed back to the GUI. Enabling
a rule means inserting the rule object into
`profiles[0].complex_modifications.rules` at the index that gives it the
right precedence.

## How the stack behaves

- **Rule order is precedence.** A physical-key rule belongs *above* the
  Gallium block. Up there it sees raw scancodes and behaves the same under EN
  and ЙЦУКЕН. Below, it fires on the wrong keys in English only.
- **"Gallium mod-combos (Lily58)" translates cmd, ctrl and option chords**
  through the Gallium table, under any input source. It can't tell a held mod
  from one baked into a board cell, so baked chords are written in QWERTY like
  everything else (see the table in `CLAUDE.md`). Keypad and arrow keys aren't
  in the table and pass through literally.
- **Plain letters are Gallium only under `^en$`.** Under Russian the physical
  positions are plain ЙЦУКЕН: `[` is х, `;` is ж, `/` is `.`. A key that looks
  free in English is often a live Cyrillic letter. Modifier seats are the only
  ones free in both.
- **A rule sitting in `karabiner.json` proves nothing.** It may be disabled
  or shadowed. Verify by pressing keys.
- **Password fields kill alt-only hotkeys.** Secure input makes macOS drop any
  global hotkey whose modifiers are only Option or Option+Shift. One with Ctrl
  or Cmd in it still fires, and it can't be switched off from outside the app.
  The fix costs no latency: a Karabiner rule turns the alt chord into the same
  key with ctrl+opt+cmd, and the target app's hotkey gets rebound to that.
  It's done for alt+g (Maccy) and alt+t (iTerm drop-down). Not done for the
  launcher on alt+Space or hyprshit's alt bindings: same recipe if bekh asks.
  Don't route this through shell commands or AppleScript. iTerm's hotkey
  window isn't reachable from AppleScript, and each `osascript` call costs
  ~130 ms.

## The rules, and what's up for cleanup

bekh wants the dead ones gone and hasn't picked them yet.

- **Off already:** F17→EN / F18→RU (the old pair), Colemak Mod-DH, tap-cmd → Clear.
- **Likely dead:** "Lily58 spares → EN symbols" (the inert half of the RU
  scheme), ctrl+cmd+esc → force quit (a workaround from when there was no alt).
- **Ask about:** side pad, AB Shutter3, side-keyboard Num5, the four EN/RU
  toggles (Space+[, F17, ctrl+shift tap, cmd+tab), ctrl+shift+P TTS pause,
  F16 → Raycast, cmd+shift+3 main display, the second profile "hop".
