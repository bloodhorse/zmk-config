function makeScorer(D) {
  const N = D.alpha.length, S = D.seats.length, W = D.W;
  const E = D.seats.map(s => s.e);
  const SFB = new Float64Array(S * S), LSB = new Float64Array(S * S), SCI = new Float64Array(S * S);
  for (let i = 0; i < S; i++) for (let j = 0; j < S; j++) {
    const a = D.seats[i], b = D.seats[j];
    if (a.h !== b.h || i === j) continue;
    if (a.f === b.f) SFB[i * S + j] = 1 + Math.hypot(a.x - b.x, a.r - b.r);
    else if (Math.abs(a.f - b.f) === 1) {
      if (Math.abs(a.r - b.r) >= 2 && Math.min(a.r, b.r) >= 1) SCI[i * S + j] = 1;
      if (((a.f === 2 && b.f === 3) || (a.f === 3 && b.f === 2)) && (a.x === 4 || b.x === 4 || a.x === 5 || b.x === 5)) LSB[i * S + j] = 1;
    }
  }
  const S3 = S * S * S;
  const RED = new Float64Array(S3), BAD = new Float64Array(S3), INR = new Float64Array(S3), OUTR = new Float64Array(S3);
  const hand = D.seats.map(s => s.h), fing = D.seats.map(s => s.f);
  for (let i = 0; i < S; i++) for (let j = 0; j < S; j++) for (let k = 0; k < S; k++) {
    const ix = (i * S + j) * S + k;
    if (hand[i] === hand[j] && hand[j] === hand[k]) {
      if (fing[i] !== fing[j] && fing[j] !== fing[k] && fing[i] !== fing[k] && (fing[j] - fing[i]) * (fing[k] - fing[j]) < 0) {
        RED[ix] = 1;
        if (fing[i] !== 3 && fing[j] !== 3 && fing[k] !== 3) BAD[ix] = 1;
      }
    } else if ((hand[i] === hand[j] && hand[j] !== hand[k]) || (hand[i] !== hand[j] && hand[j] === hand[k])) {
      const [a, b] = hand[i] === hand[j] ? [i, j] : [j, k];
      if (fing[a] !== fing[b]) (fing[b] > fing[a] ? INR : OUTR)[ix] = 1;
    }
  }
  const C2 = new Float64Array(S * S), C2s = new Float64Array(S * S), C3 = new Float64Array(S3);
  for (let i = 0; i < S * S; i++) {
    C2[i] = 100 * (W.sfb * SFB[i] + W.lsb * LSB[i] + W.scissor * SCI[i]);
    C2s[i] = 100 * W.sfs * SFB[i];
  }
  for (let i = 0; i < S3; i++) C3[i] = 100 * (W.redirect * RED[i] + W.redirect_bad * BAD[i] + W.inroll * INR[i] + W.outroll * OUTR[i]);
  const E100 = E.map(e => 100 * W.effort * e);
  const pairs = [];
  for (let a = 0; a < N; a++) for (let b = 0; b < N; b++) {
    const f = D.bi[a * N + b], g = D.sk[a * N + b];
    if (f || g) pairs.push([a, b, f, g]);
  }
  const T = D.ta.length;

  function fast(pos) {
    let s = 0;
    for (let c = 0; c < N; c++) s += D.uni[c] * E100[pos[c]];
    for (const [a, b, f, g] of pairs) { const ix = pos[a] * S + pos[b]; s += f * C2[ix] + g * C2s[ix]; }
    for (let t = 0; t < T; t++) s += D.tf[t] * C3[(pos[D.ta[t]] * S + pos[D.tb[t]]) * S + pos[D.tc[t]]];
    return s;
  }

  function metrics(pos) {
    const m = { effort: 0, sfb: 0, sfs: 0, lsb: 0, scissor: 0, redirect: 0, redirect_bad: 0, inroll: 0, outroll: 0 };
    for (let c = 0; c < N; c++) m.effort += 100 * D.uni[c] * E[pos[c]];
    for (const [a, b, f, g] of pairs) {
      const ix = pos[a] * S + pos[b];
      m.sfb += 100 * f * SFB[ix]; m.sfs += 100 * g * SFB[ix];
      m.lsb += 100 * f * LSB[ix]; m.scissor += 100 * f * SCI[ix];
    }
    for (let t = 0; t < T; t++) {
      const ix = (pos[D.ta[t]] * S + pos[D.tb[t]]) * S + pos[D.tc[t]], f = 100 * D.tf[t];
      m.redirect += f * RED[ix]; m.redirect_bad += f * BAD[ix]; m.inroll += f * INR[ix]; m.outroll += f * OUTR[ix];
    }
    let total = 0;
    for (const k in W) total += W[k] * m[k];
    return { total, m };
  }

  function sfbList(pos, n) {
    const out = [];
    for (const [a, b, f] of pairs) {
      const w = SFB[pos[a] * S + pos[b]];
      if (w && f) out.push([D.alpha[a] + D.alpha[b], 100 * f, w]);
    }
    out.sort((x, y) => y[1] * y[2] - x[1] * x[2]);
    return out.slice(0, n);
  }

  function anneal(start, pinned, iters, rnd) {
    const pos = start.slice();
    const free = [];
    for (let c = 0; c < N; c++) if (!pinned[c]) free.push(c);
    const seats = free.map(c => pos[c]);
    for (let i = seats.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [seats[i], seats[j]] = [seats[j], seats[i]]; }
    free.forEach((c, i) => pos[c] = seats[i]);
    let cur = fast(pos), best = cur, bestPos = pos.slice();
    const t0 = 3.0, t1 = 0.005;
    for (let it = 0; it < iters; it++) {
      const t = t0 * Math.pow(t1 / t0, it / iters);
      const a = free[Math.floor(rnd() * free.length)];
      let b = free[Math.floor(rnd() * free.length)];
      if (a === b) continue;
      [pos[a], pos[b]] = [pos[b], pos[a]];
      const nw = fast(pos);
      if (nw <= cur || rnd() < Math.exp((cur - nw) / t)) {
        cur = nw;
        if (cur < best) { best = cur; bestPos = pos.slice(); }
      } else[pos[a], pos[b]] = [pos[b], pos[a]];
    }
    return [best, bestPos];
  }

  return { fast, metrics, sfbList, anneal, SFB, S, N };
}
if (typeof module !== "undefined") module.exports = { makeScorer };
