import opt
opt.SEATS["'"] = ("R", 0, 2, -1, 1.8)
opt.NAMES.append("'")
from opt import Model, NAMES, anneal
from build_page import TWIN, parse

ROWS = ("qwertyuiop[]", "asdfghjkl;'", "zxcvbnm,./")

def grid(top, home, bot, extra):
    mp = {}
    for keys, row in zip(ROWS, (top, home, bot)):
        for k, ch in zip(keys, row.split()):
            mp[ch] = k
    mp.update(extra)
    return mp

LAYOUTS = {
    "йцукен": grid("й ц у к е н г ш щ з х ъ", "ф ы в а п р о л д ж э", "я ч с м и т ь б ю .", {"ё": "`", ",": "/"}),
    "диктор": grid("ц ь я , . з в к д ч ш щ", "у и е о а л н т с р й", "ф э х ы ю б м п ж г", {"ё": "`", "ъ": "w"}),
    "зубачёв": grid("ф ы а я , й м р п х ц щ", "г и е о у л т с н з ж", "ш ь ю . э б д в к ч", {"ё": "`", "ъ": "x"}),
    "редактор": grid("ц ы я й ь з д в к г ш щ", "у и о е а л р т н с х", "ф ю э , . ч м п б ж", {"ё": "`", "ъ": "]"}),
}
m = Model("stats.npz")
pos = lambda mp: [NAMES.index(mp[c]) for c in m.alpha]
rows = [(name, m.score(pos(mp))) for name, mp in LAYOUTS.items()]
rows.append(("русский галлий", m.score(pos(parse(TWIN)))))
free = min(anneal(m, {"э": "alt+⏎", "ё": "chord"}, 40000, s) for s in range(8))
rows.append(("free optimum", m.score(free[1])))
for name, (sc, mt) in sorted(rows, key=lambda r: r[1][0]):
    print(f"{name:15} {sc:6.1f}   same finger {mt['sfb']:5.2f}   effort {mt['effort']:6.1f}   skip {mt['sfs']:5.2f}")
