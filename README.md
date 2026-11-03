# lily58-zmk

bekh's Lily58 (nice!nano v2, nice_oled) and everything between its keys and
the screen: the ZMK config, the Karabiner half that makes it Gallium, the
chord index, a Russian layout built for it, and a three-key temu pad.

`CLAUDE.md` is the front door; `docs/` holds the rest. The board, not this
repo, is the source of truth: ZMK Studio's saved state wins, and
`tools/zmkctl.py verify` is how the keymap file is kept honest.

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python zmk-studio-api
.venv/bin/python tools/zmkctl.py dump      # the live layers
make chords                                # who holds which chord on the desk
```

Firmware builds in GitHub Actions (`build.yaml`); `make flash` copies the
downloaded uf2s onto each half as it shows up in bootloader mode.

Started from [mctechnology17/zmk-config](https://github.com/mctechnology17/zmk-config);
`boards/shields/lily58` is his.
