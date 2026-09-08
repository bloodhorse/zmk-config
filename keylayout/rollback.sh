#!/bin/zsh
# Undo cutover.sh. Same steps, reversed, same one-command shape.
#   board pos 35 back to LS(N7); Karabiner: revert the cutover commit (restores
#   source ids and rule 12); re-enable RussianWin, disable RussianWinPlus.
# The bundle stays in ~/Library/Keyboard Layouts — disabled, harmless, and
# removing it would need another logout to take effect anyway.
set -uo pipefail
cd "$(dirname "$0")"
REPO="$(cd .. && pwd)"
NEW="org.bekh.keylayout.RussianWinPlus"
OLD="com.apple.keylayout.RussianWin"
KB="$HOME/.config/karabiner"

[ -x ./tis ] && [ ./tis -nt ./tis.swift ] || swiftc -O -o tis tis.swift 2>/dev/null

echo "== board pos 35 -> LS(N7) =="
P=$(lsof -t /dev/tty.usbmodem* 2>/dev/null | head -1); [ -n "$P" ] && kill $P; sleep 0.5
"$REPO/.venv/bin/python" "$REPO/tools/zmkctl.py" kp 0 35 0x02070024 || echo "   board step failed — rerun with the board plugged in"

echo "== karabiner =="
SHA=$(git -C "$KB" log --grep='^cutover to RussianWinPlus' -1 --format=%H)
if [ -n "$SHA" ] && ! git -C "$KB" log --grep="Revert \"cutover to RussianWinPlus" -1 --format=%H | grep -q .; then
  git -C "$KB" revert --no-edit "$SHA" && git -C "$KB" push -q origin HEAD && echo "   reverted $SHA"
else
  echo "   nothing to revert (no cutover commit, or already reverted)"
fi

echo "== input sources =="
./tis enable "$OLD"
./tis select com.apple.keylayout.ABC
./tis disable "$NEW" || true
./tis list

echo
echo "ROLLED BACK. If config/lily58.keymap pos 35 was edited to INT_RO, put LS(N7) back there too."
