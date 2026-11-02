import sys, json, math, random, numpy as np

# seats are QWERTY scancodes, what the board sends; (hand, finger 0=pinky..3=index, row, x, effort)
# row: 0 num, 1 top, 2 home, 3 bottom, 3.5 the inner bottom keys
SEATS = {
    "q": ("L", 0, 1, 0, 3.0), "w": ("L", 1, 1, 1, 2.3), "e": ("L", 2, 1, 2, 2.0), "r": ("L", 3, 1, 3, 2.2), "t": ("L", 3, 1, 4, 3.0),
    "a": ("L", 0, 2, 0, 1.6), "s": ("L", 1, 2, 1, 1.3), "d": ("L", 2, 2, 2, 1.1), "f": ("L", 3, 2, 3, 1.0), "g": ("L", 3, 2, 4, 2.2),
    "z": ("L", 0, 3, 0, 3.0), "x": ("L", 1, 3, 1, 2.6), "c": ("L", 2, 3, 2, 2.1), "v": ("L", 3, 3, 3, 1.8), "b": ("L", 3, 3, 4, 3.0),
    "`": ("L", 0, 2, -1, 3.5), "=": ("L", 3, 3.5, 5, 3.8),
    "y": ("R", 3, 1, 4, 3.0), "u": ("R", 3, 1, 3, 2.2), "i": ("R", 2, 1, 2, 2.0), "o": ("R", 1, 1, 1, 2.3), "p": ("R", 0, 1, 0, 3.0),
    "h": ("R", 3, 2, 4, 2.2), "j": ("R", 3, 2, 3, 1.0), "k": ("R", 2, 2, 2, 1.1), "l": ("R", 1, 2, 1, 1.3), ";": ("R", 0, 2, 0, 1.6),
    "n": ("R", 3, 3, 4, 3.0), "m": ("R", 3, 3, 3, 1.8), ",": ("R", 2, 3, 2, 2.1), ".": ("R", 1, 3, 1, 2.6), "/": ("R", 0, 3, 0, 3.0),
    "[": ("R", 0, 1, -1, 4.0), "]": ("R", 0, 0, -1, 6.0), "-": ("R", 3, 3.5, 5, 3.8),
}
NAMES = list(SEATS)
GALLIUM = dict(zip("qwertyuiopasdfghjkl;zxcvbnm,./", "bldcvjyou,nrtsgphaeixqmwzkf';."))

W = dict(effort=1.0, sfb=14.0, sfs=4.0, lsb=5.0, scissor=4.0, redirect=3.0, redirect_bad=6.0, inroll=-1.5, outroll=-0.8)


def tables():
    S = len(NAMES)
    E = np.array([SEATS[n][4] for n in NAMES])
    sfb = np.zeros((S, S)); lsb = np.zeros((S, S)); sci = np.zeros((S, S)); roll = np.zeros((S, S))
    for i, a in enumerate(NAMES):
        ha, fa, ra, xa, _ = SEATS[a]
        for j, b in enumerate(NAMES):
            hb, fb, rb, xb, _ = SEATS[b]
            if ha != hb or i == j:
                continue
            if fa == fb:
                sfb[i, j] = 1 + math.hypot(xa - xb, ra - rb)
            elif abs(fa - fb) == 1:
                if abs(ra - rb) >= 2 and min(ra, rb) >= 1:
                    sci[i, j] = 1
                if {fa, fb} == {2, 3} and (xa == 4 or xb == 4 or xa == 5 or xb == 5):
                    lsb[i, j] = 1
            roll[i, j] = 1 if fb > fa else -1
    tri = np.zeros((S, S, S)); bad = np.zeros((S, S, S)); inr = np.zeros((S, S, S)); outr = np.zeros((S, S, S))
    hand = np.array([SEATS[n][0] == "L" for n in NAMES])
    fing = np.array([SEATS[n][1] for n in NAMES])
    for i in range(S):
        for j in range(S):
            for k in range(S):
                if hand[i] == hand[j] == hand[k]:
                    if fing[i] != fing[j] != fing[k] and fing[i] != fing[k]:
                        if (fing[j] - fing[i]) * (fing[k] - fing[j]) < 0:
                            tri[i, j, k] = 1
                            if 3 not in (fing[i], fing[j], fing[k]):
                                bad[i, j, k] = 1
                elif hand[i] == hand[j] != hand[k] or hand[i] != hand[j] == hand[k]:
                    a, b = (i, j) if hand[i] == hand[j] else (j, k)
                    if fing[a] != fing[b]:
                        (inr if fing[b] > fing[a] else outr)[i, j, k] = 1
    return E, sfb, lsb, sci, tri, bad, inr, outr


class Model:
    def __init__(self, stats):
        z = np.load(stats)
        self.alpha = "".join(z["alpha"])
        self.uni, self.bi, self.sk, self.tri = z["uni"], z["bi"], z["sk"], z["tri"]
        self.T = tables()
        self.compile()

    def metrics(self, pos):
        E, sfb, lsb, sci, tri, bad, inr, outr = self.T
        P = np.asarray(pos)
        bi_ix = np.ix_(P, P)
        tr_ix = np.ix_(P, P, P)
        return dict(
            effort=100 * (self.uni * E[P]).sum(),
            sfb=100 * (self.bi * sfb[bi_ix]).sum(),
            sfs=100 * (self.sk * sfb[bi_ix]).sum(),
            lsb=100 * (self.bi * lsb[bi_ix]).sum(),
            scissor=100 * (self.bi * sci[bi_ix]).sum(),
            redirect=100 * (self.tri * tri[tr_ix]).sum(),
            redirect_bad=100 * (self.tri * bad[tr_ix]).sum(),
            inroll=100 * (self.tri * inr[tr_ix]).sum(),
            outroll=100 * (self.tri * outr[tr_ix]).sum(),
        )

    def compile(self):
        E, sfb, lsb, sci, tri, bad, inr, outr = self.T
        self.C2 = 100 * (W["sfb"] * sfb + W["lsb"] * lsb + W["scissor"] * sci)
        self.C2s = 100 * W["sfs"] * sfb
        C3 = 100 * (W["redirect"] * tri + W["redirect_bad"] * bad + W["inroll"] * inr + W["outroll"] * outr)
        S = C3.shape[0]
        flat = self.tri.ravel()
        keep = np.argsort(-flat)[:6000]
        self.t_a, self.t_b, self.t_c = np.unravel_index(keep, self.tri.shape)
        self.t_f = flat[keep]
        self.C3flat = C3.ravel()
        self.S = S
        self.E100 = 100 * W["effort"] * E

    def fast(self, pos):
        P = np.asarray(pos)
        return ((self.uni * self.E100[P]).sum()
                + (self.bi * self.C2[np.ix_(P, P)]).sum()
                + (self.sk * self.C2s[np.ix_(P, P)]).sum()
                + (self.t_f * self.C3flat[(P[self.t_a] * self.S + P[self.t_b]) * self.S + P[self.t_c]]).sum())

    def score(self, pos):
        m = self.metrics(pos)
        return sum(W[k] * m[k] for k in W), m


def anneal(model, pins, iters, seed):
    rng = random.Random(seed)
    n = len(model.alpha)
    free_seats = [NAMES.index(s) for s in NAMES if s not in pins.values()]
    free_chars = [i for i, c in enumerate(model.alpha) if c not in pins]
    pos = [0] * n
    for c, s in pins.items():
        pos[model.alpha.index(c)] = NAMES.index(s)
    seats = free_seats[:]
    rng.shuffle(seats)
    for c, s in zip(free_chars, seats):
        pos[c] = s
    cur = model.fast(pos)
    best, best_pos = cur, pos[:]
    t0, t1 = 3.0, 0.005
    for it in range(iters):
        t = t0 * (t1 / t0) ** (it / iters)
        a, b = rng.sample(free_chars, 2)
        pos[a], pos[b] = pos[b], pos[a]
        new = model.fast(pos)
        if new <= cur or rng.random() < math.exp((cur - new) / t):
            cur = new
            if cur < best:
                best, best_pos = cur, pos[:]
        else:
            pos[a], pos[b] = pos[b], pos[a]
    return model.score(best_pos)[0], best_pos


def draw(model, pos):
    at = {NAMES[s]: model.alpha[c] for c, s in enumerate(pos)}
    g = lambda k: at.get(k, "·")
    rows = [
        f"                                  {g(']')}",
        f"    {g('q')} {g('w')} {g('e')} {g('r')} {g('t')}     {g('y')} {g('u')} {g('i')} {g('o')} {g('p')} {g('[')}",
        f"  {g('`')} {g('a')} {g('s')} {g('d')} {g('f')} {g('g')}     {g('h')} {g('j')} {g('k')} {g('l')} {g(';')}",
        f"    {g('z')} {g('x')} {g('c')} {g('v')} {g('b')} {g('=')} {g('-')} {g('n')} {g('m')} {g(',')} {g('.')} {g('/')}",
    ]
    return "\n".join(rows)


def fmt(m):
    return "  ".join(f"{k} {v:.2f}" for k, v in m.items())


if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1]))
    model = Model(cfg.get("stats", "stats.npz"))
    pins = cfg["pins"]
    runs, iters = cfg.get("runs", 8), cfg.get("iters", 20000)
    results = sorted(anneal(model, pins, iters, s) for s in range(runs))
    best, pos = results[0]
    print("scores:", " ".join(f"{r[0]:.1f}" for r in results))
    print(draw(model, pos))
    print(fmt(model.score(pos)[1]))
    json.dump({model.alpha[c]: NAMES[s] for c, s in enumerate(pos)}, open(cfg.get("out", "best.json"), "w"), ensure_ascii=False, indent=1)
