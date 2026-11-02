import sys, numpy as np

ALPHA = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя,."
SPACE, BREAK = len(ALPHA), len(ALPHA) + 1
N = len(ALPHA)

def encode(text):
    a = np.frombuffer(text.lower().encode("utf-32-le"), dtype=np.uint32)
    table = np.full(0x500, BREAK, dtype=np.int64)
    for i, ch in enumerate(ALPHA):
        table[ord(ch)] = i
    table[ord(" ")] = SPACE
    table[ord("ё")] = ALPHA.index("е")
    a = np.where(a < 0x500, a, ord("\x00"))
    return table[a]

def counts(codes):
    M = N + 2
    uni = np.bincount(codes, minlength=M)[:N].astype(float)
    a, b = codes[:-1], codes[1:]
    bi = np.bincount(a * M + b, minlength=M * M).reshape(M, M)[:N, :N].astype(float)
    a, x, c = codes[:-2], codes[1:-1], codes[2:]
    ok = x != BREAK
    sk = np.bincount((a * M + c)[ok], minlength=M * M).reshape(M, M)[:N, :N].astype(float)
    tri = np.bincount((a * M + x) * M + c, minlength=M ** 3).reshape(M, M, M)[:N, :N, :N].astype(float)
    tot = uni.sum()
    return uni / tot, bi / tot, sk / tot, tri / tot

def main(out, *paths):
    parts = []
    for p in paths:
        text = open(p, encoding="utf-8", errors="ignore").read()
        if "sentences" in p:
            text = "\n".join(l.split("\t", 1)[-1] for l in text.splitlines())
        parts.append(counts(encode(text)))
    stats = [sum(p[i] for p in parts) / len(parts) for i in range(4)]
    np.savez_compressed(out, alpha=np.array(list(ALPHA)), uni=stats[0], bi=stats[1], sk=stats[2], tri=stats[3])
    top = np.argsort(-stats[0])
    print(" ".join(f"{ALPHA[i]}{100*stats[0][i]:.1f}" for i in top))

if __name__ == "__main__":
    main(*sys.argv[1:])
