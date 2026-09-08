#!/bin/zsh
# Switch the Mac from Apple's "Russian - PC" to RussianWinPlus. One command,
# idempotent, stops at the first failed step. Run AFTER a logout/login that
# followed the bundle install (verify.sh tells you if that has not happened).
#
# What it does, in order — every step has its mirror in rollback.sh:
#   1. verify.sh must say MATCH (the installed layout is exactly the generated one)
#   2. enable RussianWinPlus, select it once so macOS registers it, disable RussianWin
#   3. Karabiner: every reference to the RussianWin source id -> the new id, and
#      rule 12 ("shift+7 -> ?", EN) is removed — with RU shift+7 now '&', that rule
#      was the last thing making EN shift+7 differ from RU. One commit, pushed.
#   4. board: base pos 35 (the '?' key) LS(N7) -> INT_RO, so it reaches '?' through
#      the spare in both languages instead of through rule 12
set -euo pipefail
cd "$(dirname "$0")"
REPO="$(cd .. && pwd)"
NEW="org.bekh.keylayout.RussianWinPlus"
OLD="com.apple.keylayout.RussianWin"
KB="$HOME/.config/karabiner"

[ -x ./tis ] && [ ./tis -nt ./tis.swift ] || swiftc -O -o tis tis.swift 2>/dev/null

echo "== 1. layout verify =="
./verify.sh

echo "== 2. input sources =="
./tis enable "$NEW"
./tis select "$NEW"; sleep 0.5
./tis select com.apple.keylayout.ABC
./tis disable "$OLD" || echo "   (RussianWin already off)"
./tis list

echo "== 3. karabiner =="
if grep -q "$OLD" "$KB/karabiner.json" || python3 -c "
import json,sys; r=json.load(open('$KB/karabiner.json'))['profiles'][0]['complex_modifications']['rules']
sys.exit(0 if any(x.get('description','').startswith('shift+7 → ?') for x in r) else 1)"; then
  python3 - "$KB/karabiner.json" "$OLD" "$NEW" <<'EOF'
import json, sys
p, old, new = sys.argv[1:4]
s = open(p).read().replace(old, new)
d = json.loads(s)
rules = d['profiles'][0]['complex_modifications']['rules']
before = len(rules)
rules[:] = [r for r in rules if not r.get('description', '').startswith('shift+7 → ?')]
json.dump(d, open(p, 'w'), indent=4, ensure_ascii=False)
print(f"   source id refs rewritten; rule 12 removed: {before - len(rules)}")
EOF
  git -C "$KB" add karabiner.json
  git -C "$KB" commit -q -m "cutover to RussianWinPlus: source id refs, drop rule 12 (shift+7 -> ?)" && git -C "$KB" push -q origin HEAD
  echo "   committed + pushed"
else
  echo "   already cut over"
fi

echo "== 4. board pos 35 -> INT_RO =="
P=$(lsof -t /dev/tty.usbmodem* 2>/dev/null | head -1); [ -n "$P" ] && kill $P; sleep 0.5
"$REPO/.venv/bin/python" "$REPO/tools/zmkctl.py" kp 0 35 INT_RO

echo
echo "CUTOVER DONE. Type-check, both layouts (⌘Tab flips): shift+2..7 -> @ # $ ^ & ; the '?' key -> ?"
echo "config/lily58.keymap pos 35 now reads LS(N7) and must be changed to INT_RO before verify goes green."
