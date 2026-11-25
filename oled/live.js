// live screens: small programs, not baked loops. one tick every 50 ms draws a 32x128 1-bit
// buffer, and keys push them. integer math and one xorshift only, so each ports to c line for line.
(() => {
const W = 32, H = 128, TICK = 50;

function xs(seed) {
  let s = (seed >>> 0) || 0x9e3779b9;
  return n => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s % n; };
}
const put = (b, x, y) => { if (x >= 0 && x < W && y >= 0 && y < H) b[y * W + x] = 1; };
function line(b, x0, y0, x1, y1, keep) {
  const dx = Math.abs(x1 - x0), sx = x0 < x1 ? 1 : -1, dy = -Math.abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
  let e = dx + dy;
  for (;;) {
    if (!keep || keep()) put(b, x0, y0);
    if (x0 === x1 && y0 === y1) return;
    const e2 = 2 * e;
    if (e2 >= dy) { e += dy; x0 += sx; }
    if (e2 <= dx) { e += dx; y0 += sy; }
  }
}
const rect = (b, x, y, w, h) => { for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) put(b, x + i, y + j); };

// rain: sixteen drops, most of them streaks; the long ones fall faster. keys whip it up, it calms back.
function drop(s, d) {
  const r = s.r;
  d.x = r(W);
  if (r(5) === 0) { d.len = 1 + r(2); d.v = 3 + r(3); }
  else { d.len = 4 + r(11); d.v = 4 + (d.len >> 1) + r(3); }
  d.y = -r(48) << 4;
}
const rain = {
  init(r) {
    const s = { r, boost: 0, drops: [], splash: [] };
    for (let i = 0; i < 16; i++) { const d = {}; drop(s, d); d.y = r(H + d.len) << 4; s.drops.push(d); }
    return s;
  },
  key(s) { s.boost = Math.min(s.boost + 12, 112); },
  step(s) {
    s.boost -= (s.boost + 15) >> 4;
    for (const d of s.drops) {
      const was = d.y >> 4;
      d.y += (d.v * (16 + s.boost)) >> 4;
      const now = d.y >> 4;
      if (was < H && now >= H && d.len > 3) s.splash.push({ x: d.x, t: 4 });
      if (now - d.len >= H) drop(s, d);
    }
    for (const p of s.splash) p.t--;
    s.splash = s.splash.filter(p => p.t > 0);
  },
  draw(s, b) {
    for (const d of s.drops) { const y = d.y >> 4; for (let i = 0; i < d.len; i++) put(b, d.x, y - i); }
    for (const p of s.splash) { const k = p.t > 2 ? 1 : 2; put(b, p.x - k, H - k); put(b, p.x + k, H - k); }
  },
  info: s => `wind ${(1 + s.boost / 16).toFixed(1)}×`,
};

// lightning: a still sky with a few specks drifting down, and now and then a bolt.
// at rest about one in 45 min, a storm at most one in 9; typing builds a charge, and a long hard session is a storm.
function bolt(s) {
  const r = s.r, segs = [];
  const walk = (x, y, n, lean, br) => {
    while (n-- > 0 && y < H - 1) {
      const ny = Math.min(H - 1, y + 3 + r(6) - (br ? 1 : 0));
      const nx = Math.max(0, Math.min(W - 1, x + r(9) - 4 + (br ? lean : (W / 2 - x) >> 3)));
      segs.push({ x0: x, y0: y, x1: nx, y1: ny, br });
      if (!br && r(4) === 0) walk(nx, ny, 2 + r(5), r(2) ? 2 : -2, true);
      x = nx; y = ny;
    }
  };
  walk(8 + r(16), 0, r(3) ? 99 : 10 + r(10), 0, false);
  s.segs = segs;
}
const lightning = {
  init(r) {
    const s = { r, charge: 0, n: 0, t: -1, segs: [], force: false, specks: [] };
    for (let i = 0; i < 7; i++) s.specks.push({ x: r(W), y: r(H), wait: r(80) });
    return s;
  },
  key(s) { s.charge = Math.min(s.charge + 2, 1024); },
  strike(s) { s.force = true; },
  step(s) {
    const r = s.r;
    if (s.charge && (++s.n & 15) === 0) s.charge--;
    for (const p of s.specks) if (--p.wait <= 0) {
      p.y = (p.y + 1) % H;
      if (r(4) === 0) p.x = (p.x + W + r(3) - 1) % W;
      p.wait = 50 + r(60);
    }
    if (s.t >= 0) { if (++s.t > 16) s.t = -1; }
    else if (s.force || r(54000) < 1 + (s.charge >> 8)) { s.force = false; bolt(s); s.t = 0; }
  },
  draw(s, b) {
    for (const p of s.specks) put(b, p.x, p.y);
    const t = s.t, r = s.r;
    if (t < 0 || t === 1 || t === 4) return;
    if (t === 0) for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (((x + 3 * y) & 7) === 0) put(b, x, y);
    const fade = t > 6 ? t - 6 : 0;
    const keep = fade ? () => r(10) >= fade : null;
    for (const g of s.segs) {
      if (g.br && t > 8) continue;
      line(b, g.x0, g.y0, g.x1, g.y1, keep);
      if (!g.br && t <= 3) line(b, g.x0 + 1, g.y0, g.x1 + 1, g.y1, keep);
    }
  },
  info: s => `charge ${s.charge}/1024 · a strike every ~${Math.round(54000 / (1 + (s.charge >> 8)) * TICK / 60000)} min`,
};

// sand: every key drops a grain; they pile up. when the glass is full the floor opens.
const CAP = 2600;
const sand = {
  init(r) { return { r, g: new Uint8Array(W * H), pending: 0, count: 0, drain: false, flip: 0 }; },
  key(s) { if (s.pending < 64) s.pending++; },
  step(s) {
    const { r, g } = s;
    for (let k = 0; k < 2 && s.pending; k++) {
      const x = 12 + r(8);
      if (!g[x]) { g[x] = 1; s.pending--; s.count++; }
    }
    for (let pass = 0; pass < 2; pass++) {
      s.flip ^= 1;
      for (let y = H - 1; y >= 0; y--) for (let i = 0; i < W; i++) {
        const x = s.flip ? i : W - 1 - i, at = y * W + x;
        if (!g[at]) continue;
        if (y === H - 1) { if (s.drain) { g[at] = 0; s.count--; } continue; }
        const below = at + W;
        if (!g[below]) { g[below] = 1; g[at] = 0; continue; }
        const d = r(2) ? 1 : -1;
        for (const dx of [d, -d]) {
          const nx = x + dx;
          if (nx >= 0 && nx < W && !g[below + dx]) { g[below + dx] = 1; g[at] = 0; break; }
        }
      }
    }
    if (!s.drain && s.count >= CAP) s.drain = true;
    if (s.drain && s.count < 8) s.drain = false;
  },
  draw(s, b) { b.set(s.g); },
  info: s => `${s.count}/${CAP} grains${s.drain ? ' · draining' : ''}`,
};

// the wire: paper tape crawling up out of a punch. every key punches a row of five holes,
// the sprocket line runs regardless. bursts pull the tape through fast, pauses leave it blank.
// the tape wanders a pixel sideways now and then, so no column carries the sprockets all day.
const HX = [0, 5, 14, 19, 24], SPR = 10, HEAD = H - 8, ROW = 5;
const wire = {
  init(r) { return { r, pos: 0, rows: new Uint8Array(64), xo: new Uint8Array(64).fill(2), queue: [], last: -1, x0: 2, wander: 2400 }; },
  key(s, code) { if (s.queue.length < 24) s.queue.push(1 + (code % 31)); },
  step(s) {
    const r = s.r, rh = Math.floor((s.pos >> 4) / ROW), i = rh & 63;
    if (rh !== s.last) { s.rows[i] = 0; s.xo[i] = s.x0; s.last = rh; }
    if (s.queue.length && !s.rows[i]) s.rows[i] = s.queue.shift();
    s.pos += 4 + (s.queue.length ? 24 : 0);
    if (--s.wander <= 0) { s.wander = 1200 + r(2400); s.x0 = Math.max(0, Math.min(5, s.x0 + (r(2) ? 1 : -1))); }
  },
  draw(s, b) {
    const p = s.pos >> 4, rh = Math.floor(p / ROW);
    for (let row = rh; row >= 0 && row > rh - 30; row--) {
      const i = row & 63, top = HEAD - p + ROW * row, x0 = s.xo[i];
      rect(b, x0 + SPR, top + 2, 2, 2);
      for (let k = 0; k < 5; k++) if ((s.rows[i] >> k) & 1) rect(b, x0 + HX[k], top + 1, 3, 3);
    }
  },
  info: s => `queue ${s.queue.length}`,
};

window.LIVE = { wire, lightning, sand, rain };
window.LIVE_TICK = TICK;
window.LIVE_XS = xs;
})();
