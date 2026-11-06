// props.js — this episode's props (all new: the 72-bulb string of lights, the falling words, the ①②③ pendant lamps, the
// door-plate headers, the shopping note, milk / umbrella / piano, the practice curve). Small helpers (sourceNote, sparkle,
// dingBurst, okMark) are copied from habit_days / bedtime_words.
// Not used here (plan rule): the earlier panels, outlined numbers, bars/pillars, clocks, timer ring, calendar, list table,
// word-card grid, windows, road signs and flags.

// ---------- small helpers ----------
function sourceNote(s, x, y, o = {}) {
  const { alpha = 1, align = 'left', size = 22, color = 'rgba(190,198,222,0.8)' } = o;
  txt(s, x, y, { size, weight: 500, color, align, alpha });
}
function iconStar(x, y, r, fill) {
  ctx.save(); ctx.beginPath();
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + (i * Math.PI) / 5, rr = i % 2 === 0 ? r : r * 0.45;
    const px = x + Math.cos(a) * rr, py = y + Math.sin(a) * rr;
    i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
  }
  ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); ctx.restore();
}
function sparkleBurst(x, y, p, color = COL.yellow) {
  if (p <= 0 || p >= 1) return;
  withAlpha(1 - p, () => {
    for (let i = 0; i < 10; i++) {
      const an = (i / 10) * TAU + 0.3, d = 30 + EASE.out(p) * 90;
      iconStar(x + Math.cos(an) * d, y + Math.sin(an) * d, 9 * (1 - p * 0.5), color);
    }
  });
}
function okMark(x, y, r, p = 1) {
  ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 18; circle(x, y, r, COL.yellow); ctx.restore();
  checkBadge(x, y, r, { color: '#0d1838', p, lw: 4 });
}

// ---------- the string of lights: 72 bulbs = the 72 words of the test, lit = remembered ----------
// three swags hanging from the top edge, top right of the frame (fixed on screen, it is the scoreboard of the hook / summary)
const GARLAND = { x0: 1010, x1: 1870, rows: [118, 198, 278], sag: 26, n: 24 };
function bulbPos(k) {
  const r = Math.floor(k / GARLAND.n), i = k % GARLAND.n;
  const u = (i + 0.5) / GARLAND.n;
  const x = lerp(GARLAND.x0, GARLAND.x1, u), y = GARLAND.rows[r] + GARLAND.sag * Math.sin(Math.PI * u) + 10;
  return [x, y];
}
// lit(k) -> 0..1 ; o.flash: extra glow for a moment
function drawGarland(bt, lit, o = {}) {
  const { alpha = 1 } = o;
  if (alpha <= 0.001) return;
  withAlpha(alpha, () => {
    for (const x of [GARLAND.x0 - 8, GARLAND.x1 + 8]) line(x, -4, x, GARLAND.rows[2] + 4, 'rgba(150,165,210,0.4)', 2);
    GARLAND.rows.forEach((y0) => {
      ctx.save(); ctx.strokeStyle = 'rgba(150,165,210,0.55)'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(GARLAND.x0 - 8, y0);
      for (let u = 0; u <= 1.0001; u += 0.02) ctx.lineTo(lerp(GARLAND.x0 - 8, GARLAND.x1 + 8, u), y0 + GARLAND.sag * Math.sin(Math.PI * u));
      ctx.stroke(); ctx.restore();
    });
    for (let k = 0; k < 72; k++) {
      const [x, y] = bulbPos(k), l = clamp(lit(k));
      line(x, y - 14, x, y - 8, 'rgba(150,165,210,0.6)', 3);
      if (l > 0.01) {
        ctx.save(); ctx.shadowColor = '#ffc861'; ctx.shadowBlur = 18 * l;
        ellipse(x, y, 8.5, 11, lerpColor('#2a3158', '#ffd57e', l)); ctx.restore();
        ellipse(x - 2.5, y - 3, 2.5, 3.5, `rgba(255,250,230,${0.8 * l})`);
      } else {
        ellipse(x, y, 8.5, 11, '#1b2246');
        ctx.save(); ctx.strokeStyle = 'rgba(150,165,210,0.45)'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.ellipse(x, y, 8.5, 11, 0, 0, TAU); ctx.stroke(); ctx.restore();
      }
    }
  });
  lintPanel('garland', GARLAND.x0 - 12, GARLAND.rows[0] - 20, GARLAND.x1 + 12, GARLAND.rows[2] + GARLAND.sag + 26);
}

// ---------- the falling words (hook): 72 paper flakes, eight of them big enough to read ----------
const WORDS = ['苹果', '雨伞', '钢琴', '钥匙', '气球', '小狗', '书包', '帽子'];
const FLAKES = (() => {
  const r = mulberry32(72);
  const out = [];
  for (let i = 0; i < 72; i++) {
    const t0 = -2.6 + r() * 4.2;            // spawn beat (some are already falling on frame 0)
    const dur = 2.6 + r() * 0.8;            // beats to fall from y 380 to the floor
    out.push({ i, t0, dur, x: 880 + r() * 560, sway: 10 + r() * 22, ph: r() * TAU, rot: (r() - 0.5) * 1.2, spin: (r() - 0.5) * 2,
      word: null, caught: false });
  }
  // the words: spread over the fall, on readable spots
  // spread in time and across the column so two readable words never cover each other
  const WX_ = [930, 1310, 1030, 1390, 960, 1230, 1080, 1350];
  [3, 11, 19, 27, 36, 44, 53, 61].forEach((k, j) => {
    const f = out[k]; f.word = WORDS[j]; f.rot *= 0.25; f.spin *= 0.1; f.t0 = -2.5 + j * 0.5; f.dur = 3.0; f.x = WX_[j]; f.sway = 8;
  });
  return out;
})();
// 26 of 72 caught (26.5 on average); the catches land in his arms between beats 0.5 and 4
(() => {
  const r = mulberry32(265);
  const idx = FLAKES.map((f) => f.i).sort(() => r() - 0.5).slice(0, 26);
  idx.forEach((k, j) => { const f = FLAKES[k]; f.caught = true; f.catchAt = 0.5 + (j % 8) * 0.5; f.slot = j; });
})();
const FLOOR_FLAKES = FLAKES.filter((f) => !f.caught);  // 46 on the floor; 36 of them rise at reveal 2 (62.5 - 26.5)
function drawFlakeAt(x, y, rot, f, o = {}) {
  const { glow = 0, alpha = 1, scale = 1 } = o;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(scale, scale);
    if (glow > 0) { ctx.shadowColor = '#ffc861'; ctx.shadowBlur = 20 * glow; }
    if (f.word) {
      rrect(-56, -28, 112, 56, 8, lerpColor('#dfe6f7', '#fff1c4', glow));
      ctx.shadowBlur = 0;
      txt(f.word, 0, 2, { size: 36, weight: 900, color: '#16203f', align: 'center' });
    } else {
      rrect(-15, -10, 30, 20, 4, lerpColor('#c9d3ec', '#ffe39a', glow));
      line(-8, -2, 8, -2, 'rgba(22,32,63,0.45)', 2); line(-8, 4, 4, 4, 'rgba(22,32,63,0.45)', 2);
    }
    ctx.restore();
  });
}

// ---------- ①②③ of the answer: three pendant lamps hanging from the top edge, each with a tag ----------
function drawPendant(x, len, num, label, o = {}) {
  const { alpha = 1, lit = 1, w = 250 } = o;
  if (alpha <= 0.001) return;
  withAlpha(alpha, () => {
    line(x, -4, x, len, 'rgba(160,175,215,0.7)', 3);
    // dome shade + bulb
    ctx.save(); ctx.shadowColor = lit > 0 ? '#ffc861' : 'transparent'; ctx.shadowBlur = 30 * lit;
    ctx.beginPath(); ctx.moveTo(x - 46, len + 44); ctx.quadraticCurveTo(x - 44, len, x, len); ctx.quadraticCurveTo(x + 44, len, x + 46, len + 44); ctx.closePath();
    ctx.fillStyle = lerpColor('#232c58', '#e8a64e', lit); ctx.fill(); ctx.restore();
    if (lit > 0.01) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const g = ctx.createRadialGradient(x, len + 50, 4, x, len + 50, 120);
      g.addColorStop(0, `rgba(255,214,150,${0.45 * lit})`); g.addColorStop(1, 'rgba(255,214,150,0)');
      ctx.fillStyle = g; ctx.fillRect(x - 120, len - 70, 240, 240); ctx.restore();
      circle(x, len + 48, 10, `rgba(255,240,200,${0.5 + 0.5 * lit})`);
    }
    // the tag on two short wires
    const ty = len + 92, th = 84;
    line(x - w / 2 + 30, len + 44, x - w / 2 + 30, ty, 'rgba(160,175,215,0.6)', 2);
    line(x + w / 2 - 30, len + 44, x + w / 2 - 30, ty, 'rgba(160,175,215,0.6)', 2);
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 20; ctx.shadowOffsetY = 6;
    rrect(x - w / 2, ty, w, th, 12, lerpColor('#141c40', '#2e2310', lit * 0.7), lerpColor('#8d99b5', COL.yellow, lit), 3); ctx.restore();
    circle(x - w / 2 + 44, ty + th / 2, 25, COL.yellow);
    txt(String(num), x - w / 2 + 44, ty + th / 2 + 1, { size: 34, weight: 800, fam: 'mono', color: '#14100a', align: 'center' });
    txt(label, x - w / 2 + 84, ty + th / 2 + 1, { size: 44, weight: 900, color: lit > 0.5 ? COL.yellowHi : COL.cream });
    lintPanel('pendant ' + label, x - w / 2, ty, x + w / 2, ty + th);
  });
}

// ---------- header: a door plate (dark wood, brass edge) whose little lamp switches on; slides in from the left ----------
function plaqueHeader(num, title, line2, sub, o = {}) {
  const { alpha = 1, inP = 1, typeP = 1, bt = 0 } = o;
  if (alpha <= 0.001) return;
  const h = line2 ? 200 : 150;
  const tw = Math.max(measure(title, 58, 900), line2 ? richWidth(line2, 42, 900) : 0, measure(sub, 22, 500, 'mono'));
  const w = (num ? 150 : 50) + tw + 56, x = lerp(-80, 110, EASE.out(inP)), y = 34;
  withAlpha(alpha * EASE.out(inP), () => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 8;
    const g = ctx.createLinearGradient(0, y, 0, y + h); g.addColorStop(0, '#2a1d14'); g.addColorStop(1, '#1a120c');
    rrect(x, y, w, h, 16, g); ctx.restore();
    rrect(x + 7, y + 7, w - 14, h - 14, 11, null, 'rgba(232,180,100,0.75)', 3);
    for (const [cx, cy] of [[x + 22, y + 22], [x + w - 22, y + 22], [x + 22, y + h - 22], [x + w - 22, y + h - 22]]) circle(cx, cy, 4, 'rgba(232,180,100,0.8)');
    const tx = x + (num ? 150 : 50);
    if (num) {
      const on = clamp(inP * 1.4 - 0.4);
      ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 24 * on; circle(x + 82, y + h / 2, 46, lerpColor('#5a4520', COL.yellow, on)); ctx.restore();
      txt(num, x + 82, y + h / 2 + 2, { size: 58, weight: 800, fam: 'mono', color: '#1a120c', align: 'center' });
    }
    txt(title, tx, y + 58, { size: 58, weight: 900, color: COL.cream });
    if (line2) rich(line2, tx, y + 122, { size: 42, weight: 900 });
    typeText(sub, typeP, tx + 2, y + h - 34, { size: 22, weight: 500, fam: 'mono', color: 'rgba(232,210,170,0.8)' }, bt);
  });
  lintPanel('header ' + title, x, y, x + w, y + h);
}

// ---------- step ②: the shopping note (top right), the three crazy pictures ----------
const SHOP = ['牛奶', '雨伞', '钢琴'];
function drawShoppingNote(x, y, done, o = {}) {
  const { alpha = 1, rot = -0.03 } = o;
  if (alpha <= 0.001) return;
  const w = 520, h = 150;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.rotate(rot);
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 8;
    rrect(-w / 2, -h / 2, w, h, 6, '#f4ecd6'); ctx.restore();
    rrect(-w / 2, -h / 2, w, 14, [6, 6, 0, 0], '#f7b93e');
    txt('要买', -w / 2 + 28, -22, { size: 36, weight: 900, color: '#8a5a2b' });
    SHOP.forEach((s, i) => {
      const cx = -w / 2 + 110 + i * 140, cy = 34;
      txt(s, cx, cy, { size: 44, weight: 900, color: '#1c160c' });
      const d = done(i);
      if (d > 0) {
        const L = measure(s, 44, 900);
        line(cx - 4, cy + 2, cx - 4 + (L + 8) * EASE.out(d), cy + 2, 'rgba(194,54,95,0.85)', 5);
      }
    });
    ctx.restore();
  });
  lintPanel('shopping note', x, y, x + w, y + h);
}
// milk pouring out of the shoe cabinet (spot 2): the doors swing open, a carton tips, a puddle spreads on the floor
function drawMilk(p, glow) {
  if (p <= 0) return;
  const x = SPOT_X[1];
  const open = EASE.out(clamp(p * 3));
  // open doors (seen edge-on, swung toward the camera: drawn as narrowing panels)
  wPoly([[x - 80, 4], [x - 80 - 46 * open, -6], [x - 80 - 46 * open, 120], [x - 80, 108]], '#0e1634', edge(0.4 + 0.6 * glow), 2);
  wPoly([[x + 80, 4], [x + 80 + 46 * open, -6], [x + 80 + 46 * open, 120], [x + 80, 108]], '#0e1634', edge(0.4 + 0.6 * glow), 2);
  const sp = EASE.out(clamp((p - 0.15) * 1.6));
  // the puddle
  ctx.save(); if (glow > 0) { ctx.shadowColor = '#fff6dc'; ctx.shadowBlur = 24 * glow; }
  ellipse(wx(x + 20), wy(-6), (40 + 170 * sp) * CAM.Z, (6 + 10 * sp) * CAM.Z, 'rgba(246,244,236,0.95)');
  // the stream from the cabinet
  wPoly([[x - 30, 60], [x + 30, 60], [x + 50 + 40 * sp, 0], [x - 50 - 20 * sp, 0]], 'rgba(246,244,236,0.9)');
  ctx.restore();
  // a tipped carton in the cabinet mouth
  ctx.save(); ctx.translate(wx(x), wy(78)); ctx.rotate(-0.9 * open); ctx.scale(CAM.Z, CAM.Z);
  rrect(-26, -44, 52, 80, 4, '#f6f4ec'); rrect(-26, -10, 52, 26, 0, '#3f8fe8'); wPolyLocalRoof();
  ctx.restore();
  function wPolyLocalRoof() { ctx.beginPath(); ctx.moveTo(-26, -44); ctx.lineTo(0, -66); ctx.lineTo(26, -44); ctx.closePath(); ctx.fillStyle = '#e6e2d6'; ctx.fill(); }
}
// an umbrella springing open on the sofa (spot 4)
function drawUmbrella(p, glow) {
  if (p <= 0) return;
  const x = SPOT_X[3], open = EASE.back(clamp(p * 2.2));
  const cx = wx(x + 10), cy = wy(196), R = 130 * CAM.Z, sxp = clamp(open, 0.08, 1.15);
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(-0.18);
  // shaft + J handle
  line(0, -R * 1.08, 0, 120 * CAM.Z, '#c9d2ea', 6 * CAM.Z);
  ctx.beginPath(); ctx.arc(-16 * CAM.Z, 120 * CAM.Z, 16 * CAM.Z, 0, Math.PI); ctx.strokeStyle = '#c9d2ea'; ctx.lineWidth = 6 * CAM.Z; ctx.stroke();
  ctx.scale(sxp, 1);
  if (glow > 0) { ctx.shadowColor = '#ff6f9e'; ctx.shadowBlur = 30 * glow; }
  // canopy: six striped panels, scalloped rim
  const cols = ['#ff4f7e', '#ffd166'];
  for (let i = 0; i < 6; i++) {
    const a0 = Math.PI + (i / 6) * Math.PI, a1 = Math.PI + ((i + 1) / 6) * Math.PI;
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, R, a0, a1); ctx.closePath();
    ctx.fillStyle = cols[i % 2]; ctx.fill();
  }
  ctx.shadowBlur = 0;
  for (let i = 0; i < 6; i++) {
    const xa = -R + (i + 0.5) * (2 * R / 6);
    ellipse(xa, 2 * CAM.Z, R / 6, 14 * CAM.Z, '#0b1330');
  }
  ctx.restore();
}
// a grand piano crammed into the fridge (spot 7): the door swings open, keys stick out
function drawPiano(p, glow) {
  if (p <= 0) return;
  const x = SPOT_X[6], open = EASE.out(clamp(p * 2.5));
  // inside of the fridge (lit)
  wRect(x - 56, 6, x + 56, 306, `rgba(200,225,255,${0.25 + 0.35 * glow})`);
  // the piano body squeezed in: a black lid at an angle, white keys poking out of the front
  ctx.save(); if (glow > 0) { ctx.shadowColor = '#bfe4ff'; ctx.shadowBlur = 26 * glow; }
  wPoly([[x - 54, 60], [x + 54, 60], [x + 54, 250], [x - 30, 296], [x - 54, 270]], '#06070c', 'rgba(220,235,255,0.8)', 2);
  ctx.restore();
  wPoly([[x - 54, 250], [x + 40, 206], [x + 52, 220], [x - 50, 274]], '#111', 'rgba(220,235,255,0.6)', 1.5);
  // keys hanging out over the edge
  for (let k = 0; k < 9; k++) {
    const kx = x - 50 + k * 12;
    wRect(kx, 104, kx + 10, 150, '#f6f4ec');
    if (k % 3 !== 2) wRect(kx + 7, 126, kx + 13, 150, '#111');
  }
  wLine(x - 46, 0, x - 40, 60, '#c9d2ea', 4); wLine(x + 46, 0, x + 40, 60, '#c9d2ea', 4);
  // the open door, swung to the left toward the camera
  wPoly([[x - 62, 0], [x - 62 - 80 * open, -14], [x - 62 - 80 * open, 326], [x - 62, 312]], '#0e1634', edge(0.5 + 0.5 * glow), 2.5);
  // two music notes rising
  for (let j = 0; j < 2; j++) {
    const q = (p * 1.6 + j * 0.5) % 1;
    withAlpha(clamp(p * 3) * (1 - q), () => {
      const nx = wx(x + 30 + j * 40), ny = wy(330 + q * 160);
      ellipse(nx, ny, 9 * CAM.Z, 7 * CAM.Z, COL.cyanHi, -0.4); line(nx + 8 * CAM.Z, ny, nx + 8 * CAM.Z, ny - 34 * CAM.Z, COL.cyanHi, 3);
    });
  }
}

// ---------- step ③: the practice curve (Dresler 2017, p. e5 + figure S1): 5 minutes of random words, day 1 -> last week ----------
function drawPracticeCurve(bt, x, y, o = {}) {
  const { alpha = 1, at = 0 } = o;
  if (alpha <= 0.001) return;
  const w = 700, h = 270, ax = x + 20, ay = y + h;
  withAlpha(alpha, () => {
    txt('5 分钟背随机词，记住几个', x, y - 40, { size: 36, weight: 900, color: COL.cream });
    line(ax, ay, ax + w, ay, 'rgba(200,212,236,0.6)', 3);
    line(ax, ay, ax, y + 10, 'rgba(200,212,236,0.6)', 3);
    // values 16.6 -> 42.3 out of a 0..50 axis, rising fast then flatter (shape read off figure S1: an illustration)
    const v = (u) => 16.6 + (42.3 - 16.6) * (1 - Math.exp(-3.2 * u)) / (1 - Math.exp(-3.2));
    const X = (u) => ax + 40 + u * (w - 120), Y = (val) => ay - (val / 50) * (h - 20);
    const p = EASE.inOut(seg(bt, at + 2, at + 3.6));
    ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 16;
    ctx.beginPath();
    for (let u = 0; u <= p + 1e-6; u += 0.02) { const xx = X(u), yy = Y(v(u)); u ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); }
    ctx.strokeStyle = COL.yellow; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.stroke(); ctx.restore();
    const a1 = popA(bt, at + 1, 0.3);
    if (a1 > 0) {
      circle(X(0), Y(16.6), 10 * popS(bt, at + 1), COL.cream);
      txt('16.6 个', X(0) + 22, Y(16.6) - 40, { size: 40, weight: 900, color: COL.cream, alpha: a1 });
      txt('第 1 天', X(0), ay + 34, { size: 34, weight: 700, color: COL.grayHi, align: 'center', alpha: a1 });
    }
    const a2 = popA(bt, at + 4, 0.3);
    if (a2 > 0) {
      ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 20; circle(X(1), Y(42.3), 12 * popS(bt, at + 4), COL.yellow); ctx.restore();
      txt('42.3 个', X(1), Y(42.3) - 46, { size: 48, weight: 900, color: COL.yellow, align: 'center', alpha: a2, glow: 14 });
      txt('最后一周', X(1), ay + 34, { size: 34, weight: 700, color: COL.grayHi, align: 'center', alpha: a2 });
    }
  });
  lintPanel('practice curve', x, y - 64, x + w + 20, ay + 56);
}

// ---------- the evidence card of the answer (12.4 s): 13 randomized trials pooled ----------
function drawMetaCard(x, y, w, h) {
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 8;
  rrect(x, y, w, h, 16, '#101a3e'); ctx.restore();
  rrect(x + 8, y + 8, w - 16, h - 16, 11, null, 'rgba(143,232,248,0.55)', 2);
  // 13 small lamps in a row = 13 studies, all lit
  for (let i = 0; i < 13; i++) {
    const cx = x + 44 + i * 40, cy = y + 52;
    ctx.save(); ctx.shadowColor = '#ffc861'; ctx.shadowBlur = 12; circle(cx, cy, 11, '#ffd57e'); ctx.restore();
  }
  txt('13 项随机实验汇总', x + 32, y + 116, { size: 44, weight: 900, color: COL.cream });
  rich([{ s: '结果：' }, { s: '中等效果', color: COL.yellow }], x + 32, y + 178, { size: 44, weight: 900 });
  txt('g = 0.65 · Twomey & Kroneisen 2021', x + 32, y + 232, { size: 26, weight: 500, fam: 'mono', color: COL.grayHi });
  lintPanel('meta card', x, y, x + w, y + h);
}
