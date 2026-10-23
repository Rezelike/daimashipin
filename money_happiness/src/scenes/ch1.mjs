// 研究 01 · Kahneman & Deaton 2010：45 万份问卷 → 两个问题 → 收入-幸福感示意图 → $75K 平台。
import { clamp, lerp, ease, env, mulberry32, gauss, fmtInt } from '../engine/util.mjs';
import { FONT } from '../engine/fonts.mjs';
import { C, rr, glowText, glowDot, drawChapterLabel, drawPill, strokeGlowPath, drawFixedDigits } from '../engine/draw.mjs';
import { PLOT, X, Y, U75, lifeCurve, emoCurve, curvePoints, drawLogAxes } from '../engine/chart.mjs';
import { drawFolk, drawFolkSprite, makeFolk, ARM_DOWN, ARM_OUT, ARM_UP } from '../engine/folk.mjs';
import { CUES } from '../cues.mjs';

const T = Object.fromEntries(CUES.map((c) => [c.id, c]));

const LIFE_PTS = curvePoints(lifeCurve);
const EMO_PTS = curvePoints(emoCurve);

/* ---------- crowd: 450 figures, each one = 1,000 of the 450,000 responses ---------- */

const CROWD_N = 450;
const COUNT_T0 = () => T.c1a.t0 + 0.25;
const COUNT_DUR = 1.85;
const CROWD_X0 = 250;
const CROWD_X1 = 1670;

const CROWD = (() => {
  const rng = mulberry32(450);
  const ROWS = 8;
  const rows = Array.from({ length: ROWS }, (_, r) => {
    const k = r / (ROWS - 1);
    const s = lerp(0.36, 0.56, k);
    const half = lerp(650, 760, k);
    return { k, s, half, y: lerp(560, 838, k), want: (2 * half) / (58 * s) };
  });
  const total = rows.reduce((a, r) => a + r.want, 0);
  let left = CROWD_N;
  rows.forEach((r, i) => {
    r.n = i === ROWS - 1 ? left : Math.round((r.want * CROWD_N) / total);
    left -= r.n;
  });
  const out = [];
  for (const r of rows) {
    const step = (2 * r.half) / r.n;
    for (let i = 0; i < r.n; i++) {
      const f = makeFolk(rng);
      f.mood = clamp(0.3 + gauss(rng) * 0.45, -0.9, 1);
      f.look = (rng() - 0.5) * 1.2;
      out.push({
        f,
        x: 960 - r.half + (i + 0.5) * step + (rng() - 0.5) * step * 0.5,
        y: r.y + (rng() - 0.5) * 6,
        s: r.s * (0.94 + rng() * 0.12),
        ph: rng() * Math.PI * 2,
      });
    }
  }
  // Pop-in order is random, but synced to the counter: figure #k appears as the count passes k × 1,000.
  const order = out.map((_, i) => i).sort(() => rng() - 0.5);
  order.forEach((idx, rank) => {
    const q = (rank + 1) / CROWD_N;
    out[idx].tIn = COUNT_T0() + COUNT_DUR * (1 - Math.cbrt(1 - q)) - 0.05;
  });
  // Left to right, the crowd dissolves into dots as the chart starts drawing.
  for (const p of out) p.tOut = T.c1e.t0 + 0.12 + clamp((p.x - CROWD_X0) / (CROWD_X1 - CROWD_X0)) * 0.6;
  return out;
})();

const BY_X = [...CROWD].sort((a, b) => a.x - b.x);

/** Dims the crowd (and the dots it turns into) while the question cards are up. */
const cardDimAt = (t) => 1 - 0.84 * env(t, T.c1b.t0 - 0.1, T.c1e.t0 + 0.35, 0.35, 0.3);

function drawCrowd(ctx, t) {
  if (t < T.c1a.t0 || t > T.c1e.t0 + 1.2) return;
  const dim = cardDimAt(t);
  for (const p of CROWD) {
    if (t < p.tIn) continue;
    const e = clamp((t - p.tIn) / 0.22);
    const pop = ease.outBack(e);
    const gone = clamp((t - p.tOut) / 0.25);
    if (gone >= 1) continue;
    const s = p.s * pop * (1 - 0.35 * gone);
    const y = p.y - (1 - ease.outCubic(e)) * 10 + Math.sin(t * 2.1 + p.ph) * 0.6;
    drawFolkSprite(ctx, p.f, p.x, y, s, clamp(e * 3) * (1 - gone) * dim);
  }
}

/* ---------- particles: the crowd turns into data points ---------- */

const N = 2400;
const PARTS = (() => {
  const r = mulberry32(2010);
  const out = [];
  for (let i = 0; i < N; i++) {
    const g = i % 2; // 0 = life rating (gold), 1 = happy yesterday (cyan)
    const u = 0.004 + r() * 0.992;
    const v = (g === 0 ? lifeCurve(u) : emoCurve(u)) + gauss(r) * 0.042;
    // Born from a figure at roughly the same left-to-right position as its income.
    const j = clamp(Math.round(u * (CROWD_N - 1) + (r() - 0.5) * 24), 0, CROWD_N - 1);
    const src = BY_X[j];
    out.push({
      g,
      u,
      cx: src.x + (r() - 0.5) * 22 * src.s,
      cy: src.y - (12 + r() * 70) * src.s,
      td: src.tOut + r() * 0.08,
      tx: X(u),
      ty: Y(clamp(v, -0.02, 1.02)),
      wx: X(u),
      wy: PLOT.B - 6 - r() * 16,
      size: 1.2 + r() * 1.5,
      a: 0.35 + r() * 0.5,
      ph: r() * Math.PI * 2,
      fd: 0.65 + r() * 0.3,
      arc: (r() - 0.5) * 90,
    });
  }
  return out;
})();

function segmentsOf(p) {
  if (p.g === 0) return [{ t: T.c1e.t0 + 0.3 + p.u * 1.2, x: p.tx, y: p.ty }];
  const rise =
    p.u <= U75 ? T.c1f.t0 + 0.2 + (p.u / U75) * 1.1 : T.c1g.t0 + 0.2 + ((p.u - U75) / (1 - U75)) * 0.7;
  return [
    { t: T.c1e.t0 + 0.2 + p.u * 0.6, x: p.wx, y: p.wy },
    { t: rise, x: p.tx, y: p.ty },
  ];
}

function drawParticles(ctx, t, dimAll) {
  const base = ctx.globalAlpha * dimAll;
  if (base <= 0 || t < T.c1e.t0) return;
  const cardDim = cardDimAt(t);
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (const group of [0, 1]) {
    ctx.fillStyle = group === 0 ? 'rgb(255,214,140)' : 'rgb(150,222,255)';
    for (const p of PARTS) {
      if (p.g !== group) continue;
      if (t < p.td) continue;
      const pr = ease.outCubic(clamp((t - p.td) / 0.25));
      let x = p.cx + Math.sin(t * 0.6 + p.ph) * 3 * pr;
      let y = p.cy + Math.cos(t * 0.5 + p.ph * 1.3) * 2 * pr;
      let flown = false;
      let landed = false;
      const segs = segmentsOf(p);
      for (let i = 0; i < segs.length; i++) {
        const s = segs[i];
        const k = ease.inOutCubic(clamp((t - s.t) / p.fd));
        if (k <= 0) break;
        flown = true;
        x = lerp(x, s.x, k);
        y = lerp(y, s.y, k) + Math.sin(Math.PI * k) * p.arc * 0.3;
        landed = i === segs.length - 1 && k >= 1;
      }
      if (landed) {
        x += Math.sin(t * 1.1 + p.ph) * 0.7;
        y += Math.cos(t * 1.3 + p.ph) * 0.7;
      }
      let a = p.a * (0.75 + 0.25 * Math.sin(t * 2.2 + p.ph * 3)) * clamp(pr * 1.6);
      if (!flown) a *= cardDim;
      ctx.globalAlpha = base * a;
      ctx.fillRect(x - p.size / 2, y - p.size / 2, p.size, p.size);
    }
  }
  ctx.restore();
}

/* ---------- 450,000 counter ---------- */

const LEGEND_FOLK = makeFolk(mulberry32(1000), { hairStyle: 'short', top: '#E09A46', skin: '#F1CBA4', hair: '#3F2C22' });

function drawCounter(ctx, t) {
  const t0 = COUNT_T0();
  const a = clamp((t - t0) / 0.25) * (1 - clamp((t - (T.c1b.t0 - 0.05)) / 0.3));
  if (a <= 0) return;
  const v = CROWD_N * 1000 * ease.outCubic(clamp((t - t0) / COUNT_DUR));
  const cy = 318;
  drawFixedDigits(ctx, fmtInt(v), 960, cy, {
    font: FONT.zh(150, 'SemiBold'),
    color: C.gold,
    glow: C.goldGlow,
    blur: 36,
    alpha: a,
  });
  // +114: the comma tail reaches ≈ +85 below the digits' middle (150px SerifSC).
  glowText(ctx, 'RESPONSES · 份问卷', 960, cy + 114, {
    font: FONT.mono(16),
    color: 'rgba(235,215,170,0.62)',
    alpha: a,
    letterSpacing: 6,
    baseline: 'middle',
  });
  // Legend: one figure = 1,000 responses.
  const la = a * clamp((t - (t0 + 0.35)) / 0.3);
  if (la > 0) {
    const text = '= 1,000 份';
    ctx.save();
    ctx.font = FONT.mono(20);
    ctx.letterSpacing = '1px';
    const tw = ctx.measureText(text).width;
    ctx.restore();
    const iconW = 22;
    const gap = 10;
    const x0 = 960 - (iconW + gap + tw) / 2;
    drawFolk(ctx, LEGEND_FOLK, { x: x0 + iconW / 2, y: cy + 172, s: 0.34, mood: 0.6, alpha: la });
    glowText(ctx, text, x0 + iconW + gap, cy + 156, {
      font: FONT.mono(20),
      color: 'rgba(236,230,214,0.82)',
      align: 'left',
      baseline: 'middle',
      letterSpacing: 1,
      alpha: la,
    });
  }
}

/* ---------- the two survey questions ---------- */

function drawLadder(ctx, x, y, t) {
  const lx = x + 262;
  const rx = x + 330;
  const top = y + 128;
  const bot = y + 304;
  const level = 7 * ease.outCubic(clamp((t - T.c1c.t0 - 0.15) / 0.9));
  ctx.save();
  ctx.strokeStyle = 'rgba(232,206,150,0.45)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(lx, top - 10);
  ctx.lineTo(lx, bot + 10);
  ctx.moveTo(rx, top - 10);
  ctx.lineTo(rx, bot + 10);
  ctx.stroke();
  for (let i = 0; i <= 10; i++) {
    const yy = lerp(bot, top, i / 10);
    const lit = clamp(level - i + 1);
    ctx.strokeStyle = lit > 0 ? `rgba(244,196,106,${0.35 + 0.65 * lit})` : 'rgba(232,206,150,0.28)';
    ctx.shadowColor = C.goldGlow;
    ctx.shadowBlur = lit > 0.5 ? 10 * lit : 0;
    ctx.beginPath();
    ctx.moveTo(lx, yy);
    ctx.lineTo(rx, yy);
    ctx.stroke();
    ctx.shadowBlur = 0;
    if (i % 2 === 0) {
      glowText(ctx, String(i), lx - 18, yy, {
        font: FONT.mono(14),
        color: 'rgba(214,220,234,0.5)',
        align: 'right',
        baseline: 'middle',
      });
    }
  }
  if (level > 0.05) glowDot(ctx, (lx + rx) / 2, lerp(bot, top, level / 10), 6.5, C.gold, C.goldGlow);
  glowText(ctx, '最好的人生', rx + 22, top, {
    font: FONT.zh(18),
    color: 'rgba(236,236,240,0.62)',
    align: 'left',
    baseline: 'middle',
  });
  glowText(ctx, '最糟的人生', rx + 22, bot, {
    font: FONT.zh(18),
    color: 'rgba(236,236,240,0.62)',
    align: 'left',
    baseline: 'middle',
  });
  ctx.restore();
  return level;
}

const JUDGE = makeFolk(mulberry32(7), { hairStyle: 'short', top: '#3F6FA6', skin: '#E4B286', hair: '#2B2422' });
const RECALLER = makeFolk(mulberry32(8), { hairStyle: 'long', top: '#4A9A8E', skin: '#F1CBA4', hair: '#B98C55' });

/** Card ①: the respondent scores their own life and holds the score up like a judge. */
function drawJudge(ctx, x, y, t, level) {
  const tc = T.c1c.t0;
  const raise = ease.outBack(clamp((t - tc) / 0.28));
  const arm = lerp(ARM_DOWN, ARM_UP, raise);
  const k = ease.outBack(clamp((t - tc - 0.08) / 0.3));
  const mood = lerp(0.15, 0.55, ease.outCubic(clamp((t - tc - 0.9) / 0.3)));
  drawFolk(ctx, JUDGE, {
    x: x + 125,
    y: y + 322,
    s: 1.12,
    t,
    mood,
    look: 0.6 * clamp((t - tc) / 0.2),
    armR: arm,
    prop: k > 0 ? { kind: 'paddle', side: 1, text: Math.round(level), sub: '/10', k, w: 58, h: 46, fs: 32, dx: 13, lift: 54 } : null,
  });
}

function drawSun(ctx, x, y, r, alpha) {
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.strokeStyle = C.gold;
  ctx.lineWidth = 2;
  ctx.lineCap = 'round';
  ctx.beginPath();
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    ctx.moveTo(x + Math.cos(a) * r * 1.45, y + Math.sin(a) * r * 1.45);
    ctx.lineTo(x + Math.cos(a) * r * 1.9, y + Math.sin(a) * r * 1.9);
  }
  ctx.stroke();
  ctx.shadowColor = C.goldGlow;
  ctx.shadowBlur = 10;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fillStyle = C.gold;
  ctx.fill();
  ctx.restore();
}

/** Card ②: a thought bubble ("yesterday"), then the respondent taps 是 and lights up. */
function drawRecaller(ctx, x, y, t) {
  const td = T.c1d.t0;
  const px = x + 120;
  const bub = ease.outBack(clamp((t - td - 0.05) / 0.3));
  if (bub > 0) {
    ctx.save();
    ctx.globalAlpha *= clamp(bub * 2);
    ctx.fillStyle = 'rgba(236,240,248,0.1)';
    ctx.strokeStyle = 'rgba(214,220,234,0.55)';
    ctx.lineWidth = 1.5;
    [
      [x + 150, y + 192, 4],
      [x + 166, y + 174, 6.5],
    ].forEach(([bx, by, r]) => {
      ctx.beginPath();
      ctx.arc(bx, by, r * bub, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    });
    ctx.translate(x + 205, y + 138);
    ctx.scale(bub, bub);
    rr(ctx, -64, -28, 128, 56, 28);
    ctx.fill();
    ctx.stroke();
    ctx.restore();
    drawSun(ctx, x + 168, y + 138, 8 * bub, clamp(bub * 2));
    glowText(ctx, '昨天', x + 222, y + 139, {
      font: FONT.zh(24, 'Medium'),
      color: '#EDE7DA',
      baseline: 'middle',
      alpha: clamp(bub * 2),
    });
  }
  const reach = ease.outCubic(clamp((t - td - 0.33) / 0.12)) * (1 - ease.inOutCubic(clamp((t - td - 0.95) / 0.3)));
  const joy = ease.outCubic(clamp((t - td - 0.47) / 0.2));
  const hop = Math.sin(Math.PI * clamp((t - td - 0.5) / 0.32)) * 8;
  drawFolk(ctx, RECALLER, {
    x: px,
    y: y + 322 - hop,
    s: 1.12,
    t,
    mood: lerp(lerp(0, 0.2, clamp((t - td) / 0.2)), 0.92, joy),
    look: 0.5 * clamp((t - td) / 0.2),
    lookY: -0.6 * clamp((t - td) / 0.2) * (1 - joy),
    armR: lerp(ARM_DOWN, ARM_OUT, reach),
  });
}

function drawYesNo(ctx, x, y, t) {
  const cx = x + 385;
  const sel = ease.outCubic(clamp((t - T.c1d.t0 - 0.45) / 0.25));
  const tap = clamp((t - T.c1d.t0 - 0.45) / 0.5);
  if (tap > 0 && tap < 1) {
    ctx.save();
    ctx.globalAlpha *= (1 - tap) * 0.8;
    ctx.strokeStyle = C.cyan;
    ctx.lineWidth = 2;
    rr(ctx, cx - 84 - 14 * ease.outCubic(tap), y + 162 - 10 * ease.outCubic(tap), 168 + 28 * ease.outCubic(tap), 56 + 20 * ease.outCubic(tap), 38);
    ctx.stroke();
    ctx.restore();
  }
  [
    ['是', 'YES', y + 190, sel],
    ['否', 'NO', y + 262, 0],
  ].forEach(([zh, en, py, on]) => {
    const px = cx;
    ctx.save();
    rr(ctx, px - 84, py - 28, 168, 56, 28);
    ctx.fillStyle = on > 0 ? `rgba(98,212,255,${0.1 + 0.16 * on})` : 'rgba(255,255,255,0.03)';
    ctx.fill();
    ctx.lineWidth = 1.6;
    ctx.strokeStyle = on > 0 ? `rgba(98,212,255,${0.35 + 0.6 * on})` : 'rgba(214,220,234,0.3)';
    ctx.shadowColor = C.cyanGlow;
    ctx.shadowBlur = 18 * on;
    ctx.stroke();
    ctx.restore();
    glowText(ctx, zh, px - 24, py + 1, {
      font: FONT.zh(30, 'Medium'),
      color: on > 0.5 ? '#E9F8FF' : 'rgba(236,236,240,0.75)',
      baseline: 'middle',
    });
    glowText(ctx, en, px + 28, py + 2, {
      font: FONT.mono(15),
      color: 'rgba(214,220,234,0.55)',
      baseline: 'middle',
      letterSpacing: 2,
    });
  });
  glowText(ctx, '只能二选一 · YES / NO ONLY', cx, y + 316, {
    font: FONT.mono(13),
    color: 'rgba(98,212,255,0.6)',
    letterSpacing: 3,
    baseline: 'middle',
    alpha: clamp((t - T.c1d.t0 - 0.9) / 0.4),
  });
}

function drawCards(ctx, t) {
  const tIn = T.c1b.t0 + 0.1;
  const out = ease.inCubic(clamp((t - T.c1e.t0) / 0.35));
  if (t < tIn || out >= 1) return;
  const W_ = 520;
  const H_ = 340;
  [650, 1270].forEach((cx, side) => {
    const pin = ease.outCubic(clamp((t - tIn - side * 0.12) / 0.45));
    if (pin <= 0) return;
    const mine = side === 0 ? env(t, T.c1c.t0, T.c1d.t0, 0.2, 0.2) : env(t, T.c1d.t0, T.c1e.t0 + 0.4, 0.2, 0.2);
    const other = side === 0 ? env(t, T.c1d.t0, T.c1e.t0 + 0.4, 0.2, 0.2) : env(t, T.c1c.t0, T.c1d.t0, 0.2, 0.2);
    const a = pin * (1 - out) * (1 - 0.55 * other);
    const x = cx - W_ / 2;
    const y = 330 + (1 - pin) * 26 - out * 10;
    const accent = side === 0 ? [244, 196, 106] : [98, 212, 255];
    // Opaque backing (not dimmed with the content) so the crowd behind never shows through.
    ctx.save();
    ctx.globalAlpha *= pin * (1 - out);
    rr(ctx, x, y, W_, H_, 20);
    ctx.fillStyle = 'rgba(9,14,26,0.93)';
    ctx.fill();
    ctx.restore();
    ctx.save();
    ctx.globalAlpha *= a;
    rr(ctx, x, y, W_, H_, 20);
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = `rgba(${accent.join(',')},${0.25 + 0.45 * mine})`;
    ctx.shadowColor = side === 0 ? C.goldGlow : C.cyanGlow;
    ctx.shadowBlur = 24 * mine;
    ctx.stroke();
    ctx.shadowBlur = 0;
    glowText(ctx, side === 0 ? '①  人生评分' : '②  昨天的情绪', x + 34, y + 52, {
      font: FONT.zh(28, 'Medium'),
      color: side === 0 ? C.gold : C.cyan,
      align: 'left',
      baseline: 'middle',
    });
    glowText(ctx, side === 0 ? 'LIFE EVALUATION' : 'EMOTIONAL WELL-BEING', x + 34, y + 88, {
      font: FONT.mono(13),
      color: 'rgba(214,220,234,0.5)',
      align: 'left',
      letterSpacing: 4,
      baseline: 'middle',
    });
    if (side === 0) drawJudge(ctx, x, y, t, drawLadder(ctx, x, y, t));
    else {
      drawYesNo(ctx, x, y, t);
      drawRecaller(ctx, x, y, t);
    }
    ctx.restore();
  });
}

/* ---------- chart ---------- */

function drawLegend(ctx, a) {
  if (a <= 0) return;
  [
    [C.gold, C.goldGlow, '人生评分', 'LIFE RATING'],
    [C.cyan, C.cyanGlow, '昨天开心吗', 'HAPPY YESTERDAY'],
  ].forEach(([col, glow, zh, en], i) => {
    const yy = PLOT.T + 6 + i * 38;
    const xx = PLOT.L + 28;
    ctx.save();
    ctx.globalAlpha *= a;
    ctx.strokeStyle = col;
    ctx.lineWidth = 3;
    ctx.shadowColor = glow;
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.moveTo(xx, yy);
    ctx.lineTo(xx + 30, yy);
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.font = FONT.zh(20);
    ctx.letterSpacing = '0px';
    const w = ctx.measureText(zh).width;
    ctx.restore();
    glowText(ctx, zh, xx + 44, yy, { font: FONT.zh(20), color: col, align: 'left', baseline: 'middle', alpha: a });
    glowText(ctx, en, xx + 56 + w, yy + 1, {
      font: FONT.mono(12),
      color: 'rgba(214,220,234,0.45)',
      align: 'left',
      baseline: 'middle',
      letterSpacing: 3,
      alpha: a,
    });
  });
}

/** The gap between "satisfied" and "happy" past $75K: additive gold→cyan wash + hatching, swept left→right. */
function drawGap(ctx, t) {
  const ga = ease.inOutCubic(clamp((t - (T.c1h.t0 + 0.1)) / 0.6));
  if (ga <= 0) return 0;
  const uEnd = lerp(U75, 1, ga);
  const vg = ctx.createLinearGradient(0, Y(lifeCurve(1)), 0, Y(emoCurve(U75)));
  vg.addColorStop(0, 'rgb(244,196,106)');
  vg.addColorStop(1, 'rgb(98,212,255)');

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.beginPath();
  for (let i = 0; i <= 60; i++) {
    const u = lerp(U75, uEnd, i / 60);
    if (i === 0) ctx.moveTo(X(u), Y(lifeCurve(u)));
    else ctx.lineTo(X(u), Y(lifeCurve(u)));
  }
  for (let i = 60; i >= 0; i--) {
    const u = lerp(U75, uEnd, i / 60);
    ctx.lineTo(X(u), Y(emoCurve(u)));
  }
  ctx.closePath();
  ctx.globalAlpha *= 0.07;
  ctx.fillStyle = vg;
  ctx.fill();
  ctx.restore();

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.globalAlpha *= 0.3;
  ctx.strokeStyle = vg;
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  const x0 = X(U75);
  const x1 = X(uEnd);
  for (let x = x0 + 18; x < x1 - 2; x += 18) {
    const u = (x - PLOT.L) / (PLOT.R - PLOT.L);
    const yTop = Y(lifeCurve(u)) + 6;
    const yBot = Y(emoCurve(u)) - 6;
    if (yBot - yTop < 6) continue;
    ctx.moveTo(x, yTop);
    ctx.lineTo(x, yBot);
  }
  ctx.stroke();
  ctx.restore();
  return ga;
}

function drawCurvesAndMarks(ctx, t, gapA) {
  const lifeP = ease.inOutCubic(clamp((t - (T.c1e.t0 + 0.3)) / 1.25));
  const lifeHead = strokeGlowPath(ctx, LIFE_PTS, lifeP, { color: C.gold, glow: C.goldGlow, width: 3.2 });
  const e1 = ease.inOutCubic(clamp((t - (T.c1f.t0 + 0.2)) / 1.15));
  const e2 = ease.inOutCubic(clamp((t - (T.c1g.t0 + 0.2)) / 0.75));
  const emoP = e2 > 0 ? U75 + (1 - U75) * e2 : U75 * e1;
  const emoHead = strokeGlowPath(ctx, EMO_PTS, emoP, { color: C.cyan, glow: C.cyanGlow, width: 3.2 });
  if (lifeHead && lifeP < 1) glowDot(ctx, lifeHead[0], lifeHead[1], 5, '#FFF1D6', C.goldGlow);
  if (emoHead && ((e1 > 0 && e1 < 1) || (e2 > 0 && e2 < 1))) glowDot(ctx, emoHead[0], emoHead[1], 5, '#E8F8FF', C.cyanGlow);

  const mt = T.c1g.t0 + 0.15;
  // The verdict row has its own "$75K"; hide the chart's marker while the row is up.
  const ma = clamp((t - mt) / 0.3) * (1 - verdictA(t));
  if (ma > 0) {
    const mx = X(U75);
    const my = Y(emoCurve(U75));
    const dp = ease.outCubic(clamp((t - mt - 0.1) / 0.35));
    ctx.save();
    ctx.globalAlpha *= ma;
    ctx.setLineDash([6, 7]);
    ctx.strokeStyle = C.gold;
    ctx.lineWidth = 1.6;
    ctx.shadowColor = C.goldGlow;
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.moveTo(mx, my);
    ctx.lineTo(mx, lerp(my, PLOT.B, dp));
    ctx.stroke();
    ctx.restore();
    const rp = clamp((t - mt) / 0.8);
    if (rp < 1) {
      ctx.save();
      ctx.globalAlpha *= (1 - rp) * 0.7;
      ctx.strokeStyle = C.gold;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(mx, my, lerp(8, 64, ease.outCubic(rp)), 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
    glowDot(ctx, mx, my, 7 * (1 + 0.15 * Math.sin((t - mt) * 6)), C.gold, C.goldGlow, ma);
    glowText(ctx, '$75K', mx, PLOT.B + 74, {
      font: FONT.mono(24, 'SemiBold'),
      color: C.gold,
      glow: C.goldGlow,
      blur: 12,
      alpha: ma,
    });
  }

  if (gapA > 0) {
    const la = clamp((t - (T.c1h.t0 + 0.35)) / 0.4);
    glowText(ctx, '买得到 · 满意', PLOT.R + 26, Y(lifeCurve(1)), {
      font: FONT.zh(24, 'Medium'),
      color: C.gold,
      glow: C.goldGlow,
      blur: 12,
      align: 'left',
      baseline: 'middle',
      alpha: la,
    });
    glowText(ctx, '买不到 · 快乐', PLOT.R + 26, Y(emoCurve(1)), {
      font: FONT.zh(24, 'Medium'),
      color: C.cyan,
      glow: C.cyanGlow,
      blur: 12,
      align: 'left',
      baseline: 'middle',
      alpha: la,
    });
  }
}

/* ---------- verdict: three people act the chart out ---------- */

const VERDICT_T0 = () => T.c1h.t0 + 0.85;
const V_FEET = 792;
const V_S = 1.4;
// Schematic levels (the chart is schematic too): life rating keeps rising, happiness stops at $75K.
const VERDICT = [
  { x: 700, label: '$25K', meter: 0.42, mood: 0.05, f: makeFolk(mulberry32(25), { hairStyle: 'curly', top: '#C9A04B', skin: '#AC7149', hair: '#2B2422' }) },
  { x: 1010, label: '$75K', meter: 0.7, mood: 0.72, f: makeFolk(mulberry32(75), { hairStyle: 'bun', top: '#B65D72', skin: '#F6D9BC', hair: '#6B4A30' }) },
  { x: 1320, label: '$150K', meter: 0.9, mood: 0.72, f: makeFolk(mulberry32(150), { hairStyle: 'short', top: '#6B7E9E', skin: '#E4B286', hair: '#3F2C22' }) },
];
// Paddle centre and face centre heights for the row labels / comparison marks (see folk.mjs geometry).
const V_PADDLE_Y = V_FEET - 117 * V_S;
const V_FACE_Y = V_FEET - 79 * V_S;

/** Visibility of the verdict row; it clears out just before the big number comes in. */
const verdictA = (t) => clamp((t - VERDICT_T0()) / 0.2) * (1 - clamp((t - (T.c1i.t0 - 0.05)) / 0.2));

function drawVerdict(ctx, t) {
  const t0 = VERDICT_T0();
  const rowA = verdictA(t);
  if (rowA <= 0) return;

  ctx.save();
  ctx.globalAlpha *= rowA;
  ctx.translate(960, 700);
  ctx.scale(1, 0.3);
  const back = ctx.createRadialGradient(0, 0, 0, 0, 0, 760);
  back.addColorStop(0, 'rgba(5,8,15,0.6)');
  back.addColorStop(1, 'rgba(5,8,15,0)');
  ctx.fillStyle = back;
  ctx.fillRect(-760, -760, 1520, 1520);
  ctx.restore();

  ctx.save();
  ctx.globalAlpha *= rowA;
  glowText(ctx, '满意', 600, V_PADDLE_Y, { font: FONT.zh(26, 'Medium'), color: C.gold, glow: C.goldGlow, blur: 10, align: 'right', baseline: 'middle' });
  glowText(ctx, '快乐', 600, V_FACE_Y, { font: FONT.zh(26, 'Medium'), color: C.cyan, glow: C.cyanGlow, blur: 10, align: 'right', baseline: 'middle' });

  VERDICT.forEach((p, i) => {
    const k = clamp((t - t0 - i * 0.1) / 0.35);
    if (k <= 0) return;
    const pin = ease.outBack(k);
    const raise = ease.outBack(clamp((t - t0 - 0.3 - i * 0.08) / 0.28));
    const pk = ease.outBack(clamp((t - t0 - 0.38 - i * 0.08) / 0.3));
    const fill = p.meter * ease.inOutCubic(clamp((t - t0 - 0.5 - i * 0.12) / 0.5));
    const mood = lerp(0.2, p.mood, ease.outCubic(clamp((t - t0 - 0.55 - i * 0.12) / 0.3)));
    drawFolk(ctx, p.f, {
      x: p.x,
      y: V_FEET + (1 - pin) * 30,
      s: V_S,
      t,
      alpha: clamp(k * 3),
      mood,
      armR: lerp(ARM_DOWN, ARM_UP, raise),
      prop: pk > 0 ? { kind: 'paddle', side: 1, meter: fill, k: pk } : null,
    });
    glowText(ctx, p.label, p.x, V_FEET + 34, {
      font: FONT.mono(21, 'SemiBold'),
      color: p.label === '$75K' ? C.gold : 'rgba(236,230,214,0.8)',
      glow: p.label === '$75K' ? C.goldGlow : null,
      blur: 10,
      alpha: clamp(k * 3),
      baseline: 'middle',
    });
  });

  // Between neighbours: satisfaction ↑ ↑, happiness ↑ then =.
  [
    [(VERDICT[0].x + VERDICT[1].x) / 2 + 20, '↑', '↑', 0],
    [(VERDICT[1].x + VERDICT[2].x) / 2 + 20, '↑', '=', 1],
  ].forEach(([mx, top, bot, i]) => {
    const a = ease.outCubic(clamp((t - t0 - 1.05 - i * 0.35) / 0.25));
    if (a <= 0) return;
    glowText(ctx, top, mx, V_PADDLE_Y + (1 - a) * 8, { font: FONT.mono(34, 'SemiBold'), color: C.gold, glow: C.goldGlow, blur: 12, alpha: a, baseline: 'middle' });
    glowText(ctx, bot, mx, V_FACE_Y + (1 - a) * 8, { font: FONT.mono(34, 'SemiBold'), color: C.cyan, glow: C.cyanGlow, blur: 12, alpha: a, baseline: 'middle' });
  });
  ctx.restore();
}

function drawBigNumber(ctx, t, fadeOut) {
  const t0 = T.c1i.t0 + 0.15;
  const a = clamp((t - t0) / 0.35) * fadeOut;
  if (a <= 0) return;
  // Dark halo so the dimmed chart lines don't run through the digits.
  ctx.save();
  ctx.globalAlpha *= a;
  ctx.translate(960, 490);
  ctx.scale(1, 0.42);
  const back = ctx.createRadialGradient(0, 0, 0, 0, 0, 720);
  back.addColorStop(0, 'rgba(5,8,15,0.92)');
  back.addColorStop(0.62, 'rgba(5,8,15,0.74)');
  back.addColorStop(1, 'rgba(5,8,15,0)');
  ctx.fillStyle = back;
  ctx.fillRect(-720, -720, 1440, 1440);
  ctx.restore();
  const s = lerp(1.18, 1, ease.outCubic(clamp((t - t0) / 0.5)));
  ctx.save();
  ctx.translate(960, 470);
  ctx.scale(s, s);
  glowText(ctx, '$75,000', 0, 0, {
    font: FONT.zh(190, 'SemiBold'),
    color: C.gold,
    glow: C.goldGlow,
    blur: 44,
    passes: 2,
    alpha: a,
    baseline: 'middle',
  });
  ctx.restore();
  glowText(ctx, '2010  →  2021', 960, 624, {
    font: FONT.mono(20),
    color: 'rgba(235,215,170,0.66)',
    letterSpacing: 8,
    baseline: 'middle',
    alpha: a * clamp((t - (T.c1i.t0 + 0.45)) / 0.3),
  });
}

export function drawCh1(ctx, t) {
  const fadeOut = 1 - clamp((t - (T.c1i.t1 - 0.2)) / 0.45);
  if (fadeOut <= 0) return;
  const head = clamp((t - T.c1a.t0) / 0.4) * fadeOut;
  // Chapter label names the claim; the pill carries the source (paper + dataset), so nothing repeats.
  drawChapterLabel(ctx, '研究 01 · 快乐的天花板', 'A CEILING ON HAPPINESS', head);
  drawPill(ctx, 'Kahneman & Deaton · 2010', 'PNAS · GALLUP 2008–09', 960, 152, clamp((t - T.c1a.t0 - 0.2) / 0.4) * fadeOut);

  const chartT0 = T.c1e.t0 + 0.05;
  // The chart steps back twice: for the verdict row (→ 0.22), then for the big number (→ 0.12).
  const chartDim =
    lerp(1, 0.22, ease.inOutCubic(clamp((t - (VERDICT_T0() - 0.1)) / 0.45))) *
    lerp(1, 0.55, ease.inOutCubic(clamp((t - T.c1i.t0) / 0.45)));
  if (t >= chartT0) {
    ctx.save();
    ctx.globalAlpha *= clamp((t - chartT0) / 0.3) * chartDim * fadeOut;
    drawLogAxes(ctx, t, chartT0);
    drawLegend(ctx, clamp((t - (T.c1e.t0 + 0.3)) / 0.4));
    ctx.restore();
  }
  ctx.save();
  ctx.globalAlpha *= chartDim * fadeOut;
  const gapA = drawGap(ctx, t);
  ctx.restore();

  drawCrowd(ctx, t);

  ctx.save();
  ctx.globalAlpha *= fadeOut;
  drawParticles(ctx, t, chartDim);
  ctx.restore();

  if (t >= chartT0) {
    ctx.save();
    ctx.globalAlpha *= chartDim * fadeOut;
    drawCurvesAndMarks(ctx, t, gapA);
    ctx.restore();
  }

  drawCards(ctx, t);
  drawCounter(ctx, t);
  drawVerdict(ctx, t);
  drawBigNumber(ctx, t, fadeOut);
}
