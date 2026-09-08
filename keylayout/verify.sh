#!/bin/zsh
# Verdict-only check of the INSTALLED RussianWinPlus layout against expected.json.
#
#   keylayout/verify.sh            MATCH / MISMATCH for the installed layout
#   keylayout/verify.sh --delta    show what the bundle changes vs Apple's RussianWin (no install needed)
#
# MATCH means macOS, asked through UCKeyTranslate for every keycode and every
# modifier state, produces exactly the table gen_layout.py intended. It is the
# same instrument the generator used to read Apple's layout in the first place,
# so a MATCH here is the layout, not a hope about the layout.
#
# "no input source" = the bundle is copied but this login session has not
# rescanned yet. Log out and back in; nothing else refreshes the source list.
set -uo pipefail
cd "$(dirname "$0")"

SRC_ID="org.bekh.keylayout.RussianWinPlus"
BASE_ID="com.apple.keylayout.RussianWin"

[ -x ./dumplayout ] && [ ./dumplayout -nt ./dumplayout.swift ] || swiftc -O -o dumplayout dumplayout.swift 2>/dev/null

compare() {  # $1 = json A, $2 = json B, $3 = label -> prints differing cells, returns count
  python3 - "$1" "$2" "$3" <<'EOF'
import json, sys
a = {r["code"]: r for r in json.load(open(sys.argv[1]))}
b = {r["code"]: r for r in json.load(open(sys.argv[2]))}
n = 0
for c in range(128):
    for s in sorted(k for k in a[c] if k != "code"):
        if a[c][s] != b[c].get(s):
            n += 1
            print(f"  keycode {c:3d}  [{s or 'plain'}]  {sys.argv[3]}: {a[c][s]!r} -> {b[c].get(s)!r}")
sys.exit(1 if n else 0)
EOF
}

if [ "${1:-}" = "--delta" ]; then
  ./dumplayout "$BASE_ID" full 2>/dev/null > /tmp/rwp-base.json || { echo "cannot dump $BASE_ID"; exit 2; }
  echo "expected.json vs Apple's $BASE_ID:"
  compare /tmp/rwp-base.json expected.json "apple"
  exit 0
fi

if ! ./dumplayout "$SRC_ID" full 2>/dev/null > /tmp/rwp-live.json; then
  echo "no input source $SRC_ID — bundle not seen by this login session yet (log out / in), or not installed"
  exit 2
fi
if compare expected.json /tmp/rwp-live.json "expected"; then
  echo "MATCH — installed $SRC_ID is exactly what gen_layout.py intended"
else
  echo "MISMATCH — installed layout differs from expected.json (cells above)"
  exit 1
fi
