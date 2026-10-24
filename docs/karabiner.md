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
alt+RGUI), alt+Enter types `'`. alt+`=` is no longer here: shitd binds it straight (the kitty launcher, alt+shift+`=` the old one).
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
- a script edit through Python's `json.dump(indent=4)` reformats the whole
  file (a 20k-line diff for five deleted rules). Check `git diff --stat`
  before committing; a whole-file stat means the dump style is wrong for it

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
  It's done for alt+g (hyprshit's clip, bound as `ctrl-alt-cmd-g`; shitd holds
  it as a Carbon hotkey that fires when its key tap goes blind in a password
  field) and alt+t (iTerm drop-down). Not done for hyprshit's other alt
  bindings, the launcher on alt+Space among them: same recipe if bekh asks.
  Don't route this through shell commands or AppleScript. iTerm's hotkey
  window isn't reachable from AppleScript, and each `osascript` call costs
  ~130 ms.
- **Karabiner can't see fuck or shit unless told.** They're shitd's modifiers,
  not macOS's, so an alt rewrite eats shitd's fuck-alt chord too: fuck+alt+g
  arrived as fuck+ctrl-alt-cmd-g and opened the clipboard. Held F20 and F19
  set the `fuck` and `shit` variables; a rewrite that must step aside for a
  shitd chord gets `variable_unless` on them (Alt+G has it for fuck).

## The mouse in games

The MOU-302's back button (button5) is cmd+[ by Karabiner's own rules, and hyprshit's room key
when a game is up. With a game **frontmost**, a rule above them sends it as F17 instead (Slay
the Spire 2, forgeline's unity build, the Unity editor): a cmd chord in a game makes macOS drop
the keyUps of keys held through it, so the knight kept walking. With the game behind another
window it stays cmd+[, and hyprshit's gated `cmd-[` catches that case.

## The rules, and what's up for cleanup

bekh wants the dead ones gone and hasn't picked them yet.

- **Gone:** F16 → Raycast, the F17 toggle and the F17→EN / F18→RU pair, § → F19.
- **Off already:** Colemak Mod-DH, tap-cmd → Clear.
- **Likely dead:** "Lily58 spares → EN symbols" (the inert half of the RU
  scheme), ctrl+cmd+esc → force quit (a workaround from when there was no alt).
- **Ask about:** side pad, AB Shutter3, side-keyboard Num5, the three EN/RU
  toggles left (Space+[, ctrl+shift tap, cmd+tab), ctrl+shift+P TTS pause,
  cmd+shift+3 main display, the second profile "hop".
