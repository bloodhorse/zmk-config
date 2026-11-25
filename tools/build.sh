#!/usr/bin/env bash
# local zmk build, the github actions matrix on this mac: tools/build.sh [left|right]
# workspace and sdk live outside ~/tower; PRISTINE=auto for an incremental build
set -euo pipefail

LEFT="lily58_left"
RIGHT="lily58_right"
BOARD=nice_nano_v2
SNIPPET=studio-rpc-usb-uart
CMAKE_ARGS=(-DCONFIG_ZMK_STUDIO=y)

REPO=$(cd "$(dirname "$0")/.." && pwd)
WS=${ZMK_WS:-$HOME/.local/share/zmk-ws}
export ZEPHYR_SDK_INSTALL_DIR=${ZEPHYR_SDK_INSTALL_DIR:-$HOME/.local/share/zephyr-sdk-0.16.3}
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr
export PATH="$WS/.venv/bin:$PATH"

case "${1:-both}" in
  left) halves=(left) ;;
  right) halves=(right) ;;
  both) halves=(left right) ;;
  *) echo "usage: $0 [left|right]" >&2; exit 2 ;;
esac

rsync -a --delete "$REPO/config/" "$WS/config/"
cd "$WS"
sum=$(shasum -a 256 config/west.yml | cut -d' ' -f1)
if [ "$(cat .west-yml.sha 2>/dev/null)" != "$sum" ]; then
  west update --fetch-opt=--filter=tree:0
  west zephyr-export
  echo "$sum" > .west-yml.sha
fi

mkdir -p "$REPO/firmware"
for half in "${halves[@]}"; do
  if [ "$half" = left ]; then shield=$LEFT; else shield=$RIGHT; fi
  name=${shield// /_}
  build="$WS/build/$half"
  echo "=== $shield"
  west build -p "${PRISTINE:-always}" -s zmk/app -d "$build" -b "$BOARD" -S "$SNIPPET" -- \
    -DZMK_CONFIG="$WS/config" -DSHIELD="$shield" -DZMK_EXTRA_MODULES="$REPO" "${CMAKE_ARGS[@]}"
  cp "$build/zephyr/zmk.uf2" "$REPO/firmware/$name.uf2"
  echo "=== $REPO/firmware/$name.uf2 ($(stat -f %z "$REPO/firmware/$name.uf2") bytes)"
done
