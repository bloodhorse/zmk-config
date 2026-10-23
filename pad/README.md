# the pad

The three-key pad with a knob from temu: `SIDE-KEYBOARD` by SDINNOVATION, usb `6d7b:dcfa`.
Its vendor wants you in chrome at huali-tech.com every time you rewire it; that page is VIA's
WebHID code with the names filed off, so `pad` speaks the same bytes from the shell instead.

```bash
pad/pad                 # keys 0-2 and the knob, by name
pad/pad set 0 f17       # f1..f24, a..z, 0..9, mute, volup, voldown, play, m<N>, or type:c1:c2:c3
pad/pad -l 1 set 2 f16  # another layer
```

A uv script: its one dependency (hidapi) comes with it, nothing to set up. The vendor page sends
no save command after a key write, so it should hold across a replug; not proven yet.

## what's on it

| key | sends | for |
|---|---|---|
| 0 (left) | F17 | the couch key: a take for the talk-engine room (`f17 dictate room` in hyprshit's `config/keys`) |
| 1 | F13 | VoiceInk |
| 2 | F18 | neru's hints |
| 16-18 | macros 14, 12, 15 | the knob, probably; untouched |
| 19-21 | mute, vol up, vol down | the knob |

Key 0 was macro 0 before F17. Before giving it a new key, check `docs/chords.txt` and the F-row
owners: F13 VoiceInk, F18 neru, F19 the lily's shit, F20 fuck. F16 and F17 were the free ones;
F17 is the pad's now. F14/F15 are brightness on some keyboards, stay off them.

## the protocol

hidapi on the vendor interface (usage page `0xff00`), 64-byte reports `[6, ...data]`, each one
answered (`0xaa ...`). No permission prompt, the keyboard interfaces aren't touched.

- **set a key**: `[6, 0x10, 7, idx*4 lo, idx*4 hi, 0, layer, 0, type, c1, c2, c3]`
- **read layer `l`'s keymap**: `[6, 8, 58, off lo, off hi, 0, l]` per 56 bytes, 4 bytes a key from
  byte 8 of the reply
- **types**: `32` a plain key (`c1` modifiers, `c2` the HID usage: F13 = 104 ... F17 = 108),
  `48` a consumer key (`c1`: 226 mute, 233/234 volume), `96` a macro (`c1` its number, `c2` 1),
  `19` with zeros is an empty slot
- `[6, 5]` answers the config (version, pid, firmware, mode). Lighting, macros' contents and the
  rest are in the vendor's bundle (`page-*.js`, search `setKeyInfo`), unexplored.
