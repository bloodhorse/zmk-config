import sys, json, random, re
import numpy as np
from opt import SEATS, NAMES, GALLIUM, W, Model

TWIN = """
] ё
q б w л e д r с t ц y й u ю i о o у p , [ э
` к a н s р d т f ж g г h п j в k а l е ; и
z х x ч c м v ш b з = щ - ъ n ь m ф , я . ы / .
"""
MINE = """
] ё
q б w л e м r с t ш y ф u ю i а o у p , [ щ
` к a н s р d т f ч g г h я j е k о l и ; в
z п x й c д v з b ж = ц - ъ n э m х , ы . ь / .
"""
YCUKEN = dict(zip("йцукенгшщзхфывапролджячсмитьбю.ъё", "qwertyuiop[asdfghjkl;zxcvbnm,./]`"))
YCUKEN.update({"э": "=", ",": "-"})


def parse(s):
    t = s.split()
    return {t[i + 1]: t[i] for i in range(0, len(t), 2)}


def sample_lines(path, n=600):
    rng = random.Random(7)
    ok = re.compile(r"^[а-яё ,.]+$")
    out = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip().lstrip("- ").lower().replace("!", ".").replace("?", ".")
            line = re.sub(r"\s+", " ", line)
            if 25 <= len(line) <= 70 and ok.match(line):
                out.append(line)
    rng.shuffle(out)
    return out[:n]


def main(subs, out="layout.html"):
    m = Model("stats.npz")
    r = lambda a: [float(f"{v:.6g}") for v in np.asarray(a).ravel()]
    data = dict(
        alpha=list(m.alpha),
        seats=[dict(n=n, h=v[0], f=v[1], r=v[2], x=v[3], e=v[4]) for n, v in SEATS.items()],
        gallium=GALLIUM, W=W,
        uni=r(m.uni), bi=r(m.bi), sk=r(m.sk),
        ta=m.t_a.tolist(), tb=m.t_b.tolist(), tc=m.t_c.tolist(), tf=r(m.t_f),
        lines=sample_lines(subs),
        presets={
            "twin draft": dict(map=parse(TWIN), pins=list("стнр,.ёмлдпзбгфаеиоуйяы")),
            "your four": dict(map=parse(MINE), pins=list("стнр,.ё")),
            "йцукен": dict(map=YCUKEN, pins=[]),
        },
    )
    tw = parse(TWIN)
    pos = [NAMES.index(tw[c]) for c in m.alpha]
    print(f"python fast(twin) = {m.fast(pos):.3f}")
    html = open("page.tmpl.html").read()
    html = html.replace("/*SCORE*/", open("score.js").read()).replace("/*DATA*/", json.dumps(data, ensure_ascii=False))
    open(out, "w").write(html)
    json.dump(data, open("page_data.json", "w"), ensure_ascii=False)


if __name__ == "__main__":
    main(*sys.argv[1:])
