from opt import Model, draw, fmt, NAMES
m = Model("stats.npz")
Y = dict(zip("йцукенгшщзхфывапролджячсмитьбю.ъё", "qwertyuiop[asdfghjkl;zxcvbnm,./]`"))
Y["э"] = "alt+⏎"
Y[","] = "/"
pos = [NAMES.index(Y[c]) for c in m.alpha]
print(draw(m, pos)); s, mm = m.score(pos); print(f"score {s:.1f}"); print(fmt(mm))
