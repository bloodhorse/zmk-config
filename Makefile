# The chord index and flashing. Firmware is built by GitHub Actions
# (build.yaml): download the run's artifact and unzip the uf2s into
# firmware/ before `make flash`. Run `zmkctl verify` first; the board can't
# be read once it's in bootloader mode (docs/board.md).

MOUNT = /Volumes/NICENANO

chords:
	.venv/bin/python tools/chords.py

flash: flash_left flash_right

flash_left flash_right: flash_%:
	@printf "double-tap reset on the $* half, waiting for $(MOUNT).."
	@while [ ! -d $(MOUNT) ]; do sleep 1; printf "."; done; printf "\n"
	cp -v firmware/lily58_$*_nice_oled.uf2 $(MOUNT)
	@while [ -d $(MOUNT) ]; do sleep 1; done

.PHONY: chords flash flash_left flash_right
