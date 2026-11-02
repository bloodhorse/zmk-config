import sys
from opt import Model, anneal, GALLIUM
INV = {g: q for q, g in GALLIUM.items()}
m = Model("stats.npz")
BASE = {",": INV[","], ".": INV["."], "ё": "`"}
MINE = {"с": INV["c"], "т": INV["t"], "н": INV["n"], "р": INV["r"]}
TWINS = {"к": "k", "м": "m", "л": "l", "д": "d", "в": "v", "п": "p", "з": "z", "б": "b", "г": "g",
         "ф": "f", "х": "h", "а": "a", "е": "e", "и": "i", "о": "o", "у": "u", "й": "j", "ы": "y", "с": "s"}
def best(p, runs=6, iters=30000):
    return min(anneal(m, p, iters, s)[0] for s in range(runs))
free = best(BASE)
mine = best({**BASE, **MINE})
print(f"free {free:.1f}   with your four {mine:.1f}  (+{mine-free:.1f})")
for c, q in MINE.items():
    rest = {k: v for k, v in MINE.items() if k != c}
    print(f"  drop {c}: {best({**BASE, **rest}) - mine:+.1f}", flush=True)
for c, g in TWINS.items():
    q = INV[g]
    if q in MINE.values() or c in MINE:
        print(f"  {c}→{g}: seat taken"); continue
    print(f"  {c}→{g}: {best({**BASE, **MINE, c: q}) - mine:+.1f}", flush=True)
