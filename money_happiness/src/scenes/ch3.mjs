// 研究 03 · Killingsworth, Kahneman & Mellers 2023（对抗式合作）：
// 两项研究结论相反 → 两位作者 + 裁判梅勒斯 → 按快乐程度分开看：只有最不快乐的约 20% 过了 $10 万变平，最快乐的反而加速
// → 2010 年的是/否问题有天花板效应，分不清有多开心。
import { clamp, lerp, ease, env, mulberry32, gauss, smin } from '../engine/util.mjs';
import { FONT } from '../engine/fonts.mjs';
import { C, rr, glowText, glowDot, drawChapterLabel, drawPill, strokeGlowPath, drawStage } from '../engine/draw.mjs';
import { PLOT, X, Y, AXIS_WIDE, W75, W100, PCTS, pctCurve, pctStraight, pctMean, emoWide, curvePoints, drawLogAxes } from '../engine/chart.mjs';
import { drawFolk, drawFolkSprite, makeFolk, ARM_DOWN, ARM_UP } from '../engine/folk.mjs';
import { drawPerson, PEOPLE } from '../engine/people.mjs';
import { CUES } from '../cues.mjs';

const T = Object.fromEntries(CUES.map((c) => [c.id, c]));

export function ch3Shakes() {
  return [
    { t0: T.c2j.t0 + 0.4, amp: 4, dur: 0.25 },
    { t0: T.c3l.t0 + 0.45, amp: 6, dur: 0.3 },
  ];
}

/* ---------- c2j: two studies, opposite answers ---------- */

const FLOOR3 = 790;
const S3 = 0.72;

function drawMiniPanel(ctx, cx, cy, year, alpha) {
  if (alpha <= 0) return;
  const w = 380;
  const h = 196;
  const is2010 = year === 2010;
  const col = is2010 ? C.cyan : C.mint;
  const glow = is2010 ? C.cyanGlow : C.mintGlow;
  ctx.save();
  ctx.globalAlpha *= alpha;
  rr(ctx, cx - w / 2, cy - h / 2, w, h, 18);
  ctx.fillStyle = 'rgba(9,14,26,0.88)';
  ctx.fill();
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = is2010 ? 'rgba(98,212,255,0.45)' : 'rgba(111,227,193,0.45)';
  ctx.stroke();
  const x0 = cx - w / 2 + 36;
  const x1 = cx + w / 2 - 30;
  const yb = cy + h / 2 - 34;
  const yt = cy - h / 2 + 56;
  ctx.strokeStyle = 'rgba(232,206,150,0.4)';
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.moveTo(x0, yt - 8);
  ctx.lineTo(x0, yb);
  ctx.lineTo(x1 + 8, yb);
  ctx.stroke();
  const pts = [];
  for (let i = 0; i <= 60; i++) {
    const u = i / 60;
    const v = is2010 ? 0.08 + 0.6 * smin(u / 0.55, 1, 0.14) : 0.08 + 0.85 * u;
    pts.push([lerp(x0, x1, u), lerp(yb, yt, v)]);
  }
  strokeGlowPath(ctx, pts, 1, { color: col, glow, width: 3 });
  ctx.restore();
  glowText(ctx, String(year), cx - w / 2 + 22, cy - h / 2 + 28, {
    font: FONT.mono(16, 'SemiBold'),
    color: C.gold,
    align: 'left',
    baseline: 'middle',
    letterSpacing: 2,
    alpha,
  });
  glowText(ctx, is2010 ? '有天花板' : '没有天花板', cx + w / 2 - 22, cy - h / 2 + 29, {
    font: FONT.zh(22, 'Medium'),
    color: col,
    glow,
    blur: 8,
    align: 'right',
    baseline: 'middle',
    alpha,
  });
}

const RIFT = [
  [960, 214],
  [976, 296],
  [949, 378],
  [973, 462],
  [947, 546],
  [971, 630],
  [951, 714],
  [966, 800],
];

function drawRift(ctx, t) {
  const p = ease.outCubic(clamp((t - (T.c2j.t0 + 0.35)) / 0.35));
  const heal = clamp((t - (T.c3a.t0 + 0.15)) / 0.4);
  if (p <= 0 || heal >= 1) return;
  const flick = t < T.c2j.t0 + 0.9 ? 0.6 + 0.4 * Math.abs(Math.sin(t * 80)) : 1;
  ctx.save();
  ctx.globalAlpha *= (1 - heal) * flick;
  strokeGlowPath(ctx, RIFT, p, { color: '#FFE3D2', glow: C.coralGlow, width: 3.2, blur: 22 });
  ctx.restore();
}

function nameTag(ctx, zh, tag, x, a) {
  glowText(ctx, zh, x, FLOOR3 + 40, { font: FONT.zh(24), color: C.white, alpha: a * 0.92, baseline: 'middle' });
  glowText(ctx, tag, x, FLOOR3 + 68, {
    font: FONT.mono(14, 'SemiBold'),
    color: C.gold,
    glow: C.goldGlow,
    blur: 8,
    alpha: a * 0.85,
    letterSpacing: 3,
    baseline: 'middle',
  });
}

const trioOut = (t) => ease.inCubic(clamp((t - (T.c3d.t0 - 0.05)) / 0.35));

function drawTrio(ctx, t) {
  const tIn = T.c2j.t0 + 0.05;
  const out = trioOut(t);
  if (t < tIn || out >= 1) return;
  drawStage(ctx, FLOOR3, clamp((t - tIn) / 0.35) * (1 - out) * 0.8);

  const panelsA = clamp((t - (T.c2j.t0 + 0.15)) / 0.35) * (1 - clamp((t - (T.c3a.t0 + 0.05)) / 0.3));
  drawMiniPanel(ctx, 560, 352, 2010, panelsA);
  drawMiniPanel(ctx, 1360, 352, 2021, panelsA);
  drawRift(ctx, t);

  // c3a: they walk towards each other and turn to the front; c3b: they glance at Mellers.
  const walk0 = T.c3a.t0 + 0.15;
  const wk = ease.inOutCubic(clamp((t - walk0) / 0.9));
  const hop = wk > 0 && wk < 1 ? Math.abs(Math.sin(wk * Math.PI * 3)) * 7 : 0;
  const front = clamp((t - (walk0 + 0.85)) / 0.3);
  const glance = env(t, T.c3b.t0 + 0.25, T.c3c.t0 + 0.2, 0.2, 0.25);
  const friendly = ease.outCubic(clamp((t - (T.c3a.t0 + 0.6)) / 0.4));
  [
    { p: PEOPLE.kahneman, from: 560, to: 720, face: 1, tag: '2010', ti: tIn },
    { p: PEOPLE.killingsworth, from: 1360, to: 1200, face: -1, tag: '2021', ti: tIn + 0.1 },
  ].forEach(({ p, from, to, face, tag, ti }) => {
    const k = clamp((t - ti) / 0.38);
    if (k <= 0) return;
    const pin = ease.outBack(k);
    const a = clamp(k * 2.5) * (1 - out);
    const x = lerp(from, to, wk);
    const look = lerp(lerp(face, 0, front), face * 0.8, glance);
    const y = FLOOR3 + (1 - pin) * 36 - hop + out * 24;
    drawPerson(ctx, { ...p, x, y, s: S3, look, mood: lerp(0, 0.45, friendly), browTilt: 1 - friendly }, t, a);
    nameTag(ctx, p.zh, tag, x, a);
  });

  const km = clamp((t - (T.c3b.t0 + 0.15)) / 0.4);
  if (km > 0) {
    const pin = ease.outBack(km);
    const a = clamp(km * 2.5) * (1 - out);
    drawPerson(ctx, { ...PEOPLE.mellers, x: 960, y: FLOOR3 + (1 - pin) * 36 + out * 24, s: S3, look: 0, mood: 0.5 }, t, a);
    nameTag(ctx, PEOPLE.mellers.zh, PEOPLE.mellers.tag, 960, a);
  }
}

/** The paper they wrote together; Mellers joins the author line. */
function drawPaper(ctx, t) {
  const k = ease.outCubic(clamp((t - (T.c3a.t0 + 0.7)) / 0.45));
  const out = trioOut(t);
  if (k <= 0 || out >= 1) return;
  const a = k * (1 - out);
  const cx = 960;
  const cy = 318 - (1 - k) * 30;
  const w = 700;
  const h = 176;
  ctx.save();
  ctx.globalAlpha *= a;
  rr(ctx, cx - w / 2, cy - h / 2, w, h, 16);
  ctx.fillStyle = 'rgba(9,14,26,0.92)';
  ctx.fill();
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = 'rgba(235,215,170,0.5)';
  ctx.stroke();
  ctx.restore();
  glowText(ctx, 'PNAS · 2023', cx - w / 2 + 28, cy - h / 2 + 28, {
    font: FONT.mono(13),
    color: 'rgba(235,215,170,0.7)',
    align: 'left',
    letterSpacing: 3,
    baseline: 'middle',
    alpha: a,
  });
  glowText(ctx, 'Income and emotional well-being:', cx, cy - 12, { font: FONT.en(34), color: '#F1EEE6', alpha: a, baseline: 'middle' });
  glowText(ctx, 'A conflict resolved', cx, cy + 28, { font: FONT.en(34), color: C.gold, glow: C.goldGlow, blur: 10, alpha: a, baseline: 'middle' });

  const base = 'KILLINGSWORTH · KAHNEMAN';
  const add = ' · MELLERS';
  ctx.save();
  ctx.font = FONT.mono(14);
  ctx.letterSpacing = '3px';
  const w1 = ctx.measureText(base).width;
  const w2 = ctx.measureText(base + add).width;
  ctx.restore();
  const am = ease.inOutCubic(clamp((t - (T.c3b.t0 + 0.45)) / 0.35));
  const x0 = cx - lerp(w1, w2, am) / 2;
  const ay = cy + h / 2 - 26;
  glowText(ctx, base, x0, ay, { font: FONT.mono(14), color: 'rgba(214,220,234,0.6)', align: 'left', letterSpacing: 3, baseline: 'middle', alpha: a });
  glowText(ctx, add, x0 + w1, ay, {
    font: FONT.mono(14, 'SemiBold'),
    color: '#C9B9F2',
    align: 'left',
    letterSpacing: 3,
    baseline: 'middle',
    alpha: a * am,
  });
}

/** c3c: "adversarial collaboration" stamped under the paper. */
function drawStampChip(ctx, t) {
  const t0 = T.c3c.t0 + 0.1;
  const k = clamp((t - t0) / 0.3);
  const out = trioOut(t);
  if (k <= 0 || out >= 1) return;
  const s = lerp(1.7, 1, ease.outBack(k));
  const a = clamp(k * 2.5) * (1 - out);
  ctx.save();
  ctx.translate(960, 462);
  ctx.rotate(-0.035);
  ctx.scale(s, s);
  ctx.globalAlpha *= a;
  rr(ctx, -232, -38, 464, 76, 14);
  ctx.fillStyle = 'rgba(244,196,106,0.1)';
  ctx.fill();
  ctx.lineWidth = 2.5;
  ctx.strokeStyle = C.gold;
  ctx.shadowColor = C.goldGlow;
  ctx.shadowBlur = 16;
  ctx.stroke();
  ctx.shadowBlur = 0;
  glowText(ctx, '对抗式合作', 0, -8, { font: FONT.zh(36, 'SemiBold'), color: C.gold, glow: C.goldGlow, blur: 12, baseline: 'middle' });
  glowText(ctx, 'ADVERSARIAL COLLABORATION', 0, 24, {
    font: FONT.mono(12),
    color: 'rgba(235,215,170,0.75)',
    letterSpacing: 4,
    baseline: 'middle',
  });
  ctx.restore();
}

/* ---------- c3d: sort a mixed crowd by how happy each person is ---------- */

const SORT_ROWS = [
  { p: 85, y: 396, mood: 1 },
  { p: 70, y: 480, mood: 0.68 },
  { p: 50, y: 564, mood: 0.34 },
  { p: 30, y: 648, mood: 0 },
  { p: 15, y: 732, mood: -0.75 },
];
const SORT_COLS = 10;
const SORT_X0 = 640;
const SORT_X1 = 1360;
const SORT_S = 0.8;
const ROW_TINT = { 85: '111,227,193', 70: '140,205,235', 50: '200,210,235', 30: '150,175,225', 15: '255,138,122' };

const SORT = (() => {
  const rng = mulberry32(2023);
  const slots = [];
  SORT_ROWS.forEach((r, ri) => {
    for (let c = 0; c < SORT_COLS; c++) slots.push({ ri, c, x: lerp(SORT_X0, SORT_X1, c / (SORT_COLS - 1)), y: r.y });
  });
  const perm = slots.map((_, i) => i).sort(() => rng() - 0.5);
  return slots.map((dst, i) => {
    const f = makeFolk(rng);
    f.mood = clamp(SORT_ROWS[dst.ri].mood + (rng() - 0.5) * 0.16, -1, 1);
    f.look = (rng() - 0.5) * 0.8;
    const src = slots[perm[i]];
    return {
      f,
      dst,
      src: { x: src.x + (rng() - 0.5) * 30, y: src.y + (rng() - 0.5) * 16 },
      delay: rng() * 0.35,
      tIn: rng() * 0.3,
      ph: rng() * Math.PI * 2,
      tOut: T.c3e.t0 + 0.05 + ((dst.x - SORT_X0) / (SORT_X1 - SORT_X0)) * 0.45,
    };
  });
})();

function sortPos(p, t) {
  const k = ease.inOutCubic(clamp((t - (T.c3d.t0 + 0.55 + p.delay)) / 0.85));
  return { x: lerp(p.src.x, p.dst.x, k), y: lerp(p.src.y, p.dst.y, k) - Math.sin(Math.PI * k) * 16 };
}

function drawSort(ctx, t) {
  if (t < T.c3d.t0 || t > T.c3e.t0 + 1) return;
  // Once sorted, each row sits on a faint band: coral (least happy) up to mint (happiest).
  const band = clamp((t - (T.c3d.t0 + 1.35)) / 0.35) * (1 - clamp((t - T.c3e.t0) / 0.35));
  if (band > 0) {
    for (const r of SORT_ROWS) {
      const g = ctx.createLinearGradient(SORT_X0 - 60, 0, SORT_X1 + 60, 0);
      g.addColorStop(0, `rgba(${ROW_TINT[r.p]},0)`);
      g.addColorStop(0.5, `rgba(${ROW_TINT[r.p]},0.11)`);
      g.addColorStop(1, `rgba(${ROW_TINT[r.p]},0)`);
      ctx.save();
      ctx.globalAlpha *= band;
      ctx.fillStyle = g;
      rr(ctx, SORT_X0 - 60, r.y - 74, SORT_X1 - SORT_X0 + 120, 78, 18);
      ctx.fill();
      ctx.restore();
    }
  }
  for (const p of SORT) {
    const ti = T.c3d.t0 + 0.05 + p.tIn;
    if (t < ti) continue;
    const e = clamp((t - ti) / 0.22);
    const gone = clamp((t - p.tOut) / 0.25);
    if (gone >= 1) continue;
    const q = sortPos(p, t);
    const y = q.y - (1 - ease.outCubic(e)) * 10 + Math.sin(t * 2.1 + p.ph) * 0.6;
    drawFolkSprite(ctx, p.f, q.x, y, SORT_S * ease.outBack(e) * (1 - 0.35 * gone), clamp(e * 3) * (1 - gone));
  }
  // Row labels once sorted: an arrow for "happier", percentiles per row.
  const la = clamp((t - (T.c3d.t0 + 1.55)) / 0.3) * (1 - clamp((t - T.c3e.t0) / 0.3));
  if (la <= 0) return;
  const ax = SORT_X0 - 120;
  ctx.save();
  ctx.globalAlpha *= la;
  const g = ctx.createLinearGradient(0, SORT_ROWS[4].y, 0, SORT_ROWS[0].y - 60);
  g.addColorStop(0, C.coral);
  g.addColorStop(1, C.mint);
  ctx.strokeStyle = g;
  ctx.lineWidth = 2.5;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(ax, SORT_ROWS[4].y - 10);
  ctx.lineTo(ax, SORT_ROWS[0].y - 66);
  ctx.moveTo(ax - 9, SORT_ROWS[0].y - 54);
  ctx.lineTo(ax, SORT_ROWS[0].y - 66);
  ctx.lineTo(ax + 9, SORT_ROWS[0].y - 54);
  ctx.stroke();
  ctx.restore();
  glowText(ctx, '最快乐', ax - 22, SORT_ROWS[0].y - 36, { font: FONT.zh(22, 'Medium'), color: C.mint, align: 'right', baseline: 'middle', alpha: la });
  glowText(ctx, '最不快乐', ax - 22, SORT_ROWS[4].y - 36, { font: FONT.zh(22, 'Medium'), color: C.coral, align: 'right', baseline: 'middle', alpha: la });
  SORT_ROWS.forEach((r) => {
    glowText(ctx, `P${r.p}`, SORT_X0 - 74, r.y - 36, {
      font: FONT.mono(15, 'SemiBold'),
      color: 'rgba(214,220,234,0.6)',
      baseline: 'middle',
      alpha: la,
    });
  });
  glowText(ctx, '快乐程度百分位 · HAPPINESS PERCENTILE', SORT_X1 + 60, SORT_ROWS[4].y + 28, {
    font: FONT.mono(12),
    color: 'rgba(214,220,234,0.42)',
    align: 'right',
    letterSpacing: 2,
    baseline: 'middle',
    alpha: la,
  });
}

/* ---------- chart: one line per happiness percentile ---------- */

const STYLE = {
  85: { col: '#7CF0C8', glow: 'rgba(80,220,180,0.85)', label: '最快乐 · P85' },
  70: { col: '#A9DCEB', glow: 'rgba(140,200,235,0.6)', label: 'P70' },
  50: { col: '#CBD5E8', glow: 'rgba(200,210,235,0.5)', label: 'P50' },
  30: { col: '#A9BCE0', glow: 'rgba(150,175,225,0.5)', label: 'P30' },
  15: { col: C.coral, glow: C.coralGlow, label: '最不快乐 · P15' },
};
const ROWS = Object.fromEntries(PCTS.map((r) => [r.p, r]));
const PTS = Object.fromEntries(PCTS.map((r) => [r.p, curvePoints(pctCurve(r))]));
const MEAN_PTS = curvePoints(pctMean);

const CH3_T0 = () => T.c3e.t0 - 0.1;
const DRAW = {
  70: () => [T.c3e.t0 + 0.55, 1.1],
  50: () => [T.c3e.t0 + 0.67, 1.1],
  30: () => [T.c3e.t0 + 0.79, 1.1],
  85: () => [T.c3f.t0 + 0.4, 1.0],
  15: () => [T.c3g.t0 + 0.45, 1.0],
};
const lineProg = (p, t) => {
  const [t0, d] = DRAW[p]();
  return ease.inOutCubic(clamp((t - t0) / d));
};

/** Dots: each sorted figure dissolves into a little cloud along its own percentile line. */
const PARTS3 = (() => {
  const r = mulberry32(120);
  const out = [];
  for (const p of SORT) {
    const row = SORT_ROWS[p.dst.ri];
    for (let i = 0; i < 24; i++) {
      const u = clamp((p.dst.c + r()) / SORT_COLS, 0.004, 0.996);
      const v = pctCurve(ROWS[row.p])(u) + gauss(r) * 0.016;
      out.push({
        p: row.p,
        cx: p.dst.x + (r() - 0.5) * 20 * SORT_S,
        cy: p.dst.y - (12 + r() * 70) * SORT_S,
        td: p.tOut + r() * 0.08,
        tx: X(u),
        ty: Y(v),
        size: 1.2 + r() * 1.4,
        a: 0.3 + r() * 0.4,
        ph: r() * Math.PI * 2,
        fd: 0.6 + r() * 0.3,
        arc: (r() - 0.5) * 70,
      });
    }
  }
  return out;
})();

function drawParts3(ctx, t, alpha) {
  if (t < T.c3e.t0 || alpha <= 0) return;
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const base = ctx.globalAlpha * alpha;
  for (const q of PARTS3) {
    if (t < q.td) continue;
    const k = ease.inOutCubic(clamp((t - q.td) / q.fd));
    let x = lerp(q.cx, q.tx, k);
    let y = lerp(q.cy, q.ty, k) + Math.sin(Math.PI * k) * q.arc * 0.3;
    if (k >= 1) {
      x += Math.sin(t * 1.1 + q.ph) * 0.6;
      y += Math.cos(t * 1.3 + q.ph) * 0.6;
    }
    ctx.fillStyle = STYLE[q.p].col;
    ctx.globalAlpha = base * q.a * clamp((t - q.td) / 0.15) * (k >= 1 ? 0.55 : 1);
    ctx.fillRect(x - q.size / 2, y - q.size / 2, q.size, q.size);
  }
  ctx.restore();
}

function strokeDashed(ctx, pts, color, width, alpha, dash = [9, 8]) {
  if (alpha <= 0) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.setLineDash(dash);
  ctx.lineCap = 'round';
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.stroke();
  ctx.restore();
}

function drawMarker100(ctx, alpha) {
  if (alpha <= 0) return;
  const x = X(W100);
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.setLineDash([6, 7]);
  ctx.strokeStyle = C.gold;
  ctx.lineWidth = 1.6;
  ctx.shadowColor = C.goldGlow;
  ctx.shadowBlur = 8;
  ctx.beginPath();
  ctx.moveTo(x, PLOT.B);
  ctx.lineTo(x, PLOT.T - 10);
  ctx.stroke();
  ctx.restore();
  glowText(ctx, '$100K', x, PLOT.B + 74, { font: FONT.mono(24, 'SemiBold'), color: C.gold, glow: C.goldGlow, blur: 12, alpha });
}

const END_FOLK = {
  85: makeFolk(mulberry32(85), { hairStyle: 'curly', top: '#4A9A8E', skin: '#CF9568', hair: '#2B2422' }),
  15: makeFolk(mulberry32(15), { hairStyle: 'short', top: '#6B7E9E', skin: '#F1CBA4', hair: '#6B4A30' }),
};

function drawEndFolk(ctx, t, p, tIn, alpha) {
  const k = clamp((t - tIn) / 0.35);
  if (k <= 0 || alpha <= 0) return;
  const x = X(1) - 16;
  const y = Y(pctCurve(ROWS[p])(1)) - 3;
  const happy = p === 85;
  const hop = happy ? Math.abs(Math.sin((t - tIn) * 7)) * 5 : 0;
  drawFolk(ctx, END_FOLK[p], {
    x,
    y: y - hop,
    s: 0.44 * ease.outBack(k),
    t,
    alpha: clamp(k * 3) * alpha,
    mood: happy ? 1 : -0.62,
    lookY: happy ? -0.4 : 0.8,
    armL: happy ? ARM_UP : ARM_DOWN,
    armR: happy ? ARM_UP : ARM_DOWN,
  });
}

function drawArrow(ctx, x, y0, y1, color, glow, alpha) {
  if (alpha <= 0 || Math.abs(y1 - y0) < 4) return;
  const dir = Math.sign(y1 - y0);
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = 2.4;
  ctx.lineCap = 'round';
  ctx.shadowColor = glow;
  ctx.shadowBlur = 10;
  ctx.beginPath();
  ctx.moveTo(x, y0);
  ctx.lineTo(x, y1);
  ctx.moveTo(x - 6, y1 - dir * 8);
  ctx.lineTo(x, y1);
  ctx.lineTo(x + 6, y1 - dir * 8);
  ctx.stroke();
  ctx.restore();
}

function drawPctChart(ctx, t) {
  const a = clamp((t - CH3_T0()) / 0.3) * (1 - clamp((t - T.c3i.t0) / 0.4));
  if (a <= 0) return;
  ctx.save();
  ctx.globalAlpha *= a;
  drawLogAxes(ctx, t, CH3_T0(), AXIS_WIDE);
  ctx.restore();

  ctx.save();
  ctx.globalAlpha *= a;
  drawParts3(ctx, t, 1);
  const m100 = clamp((t - (T.c3f.t0 + 0.1)) / 0.3);
  drawMarker100(ctx, m100);

  const midDim = lerp(1, 0.32, ease.inOutCubic(clamp((t - T.c3h.t0) / 0.4)));
  for (const p of [70, 50, 30, 85, 15]) {
    const pr = lineProg(p, t);
    if (pr <= 0) continue;
    const st = STYLE[p];
    const dim = p === 85 || p === 15 ? 1 : midDim;
    ctx.save();
    ctx.globalAlpha *= dim;
    const head = strokeGlowPath(ctx, PTS[p], pr, { color: st.col, glow: st.glow, width: p === 85 || p === 15 ? 3.4 : 2.6 });
    if (head && pr < 1) glowDot(ctx, head[0], head[1], 5, '#FFFFFF', st.glow);
    ctx.restore();
    glowText(ctx, st.label, PLOT.R + 26, Y(pctCurve(ROWS[p])(1)), {
      font: p === 85 || p === 15 ? FONT.zh(21, 'Medium') : FONT.mono(16, 'SemiBold'),
      color: st.col,
      align: 'left',
      baseline: 'middle',
      alpha: dim * clamp((pr - 0.85) / 0.15),
    });
  }

  // "Most people": bracket over the three middle lines.
  const ba = clamp((t - (T.c3e.t0 + 1.8)) / 0.3) * midDim;
  if (ba > 0) {
    const y0 = Y(pctCurve(ROWS[70])(1));
    const y1 = Y(pctCurve(ROWS[30])(1));
    const bx = PLOT.R + 84;
    ctx.save();
    ctx.globalAlpha *= ba;
    ctx.strokeStyle = 'rgba(214,220,234,0.6)';
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    ctx.moveTo(bx, y0);
    ctx.lineTo(bx + 10, y0);
    ctx.lineTo(bx + 10, y1);
    ctx.lineTo(bx, y1);
    ctx.stroke();
    ctx.restore();
    glowText(ctx, '大多数人', bx + 22, (y0 + y1) / 2, { font: FONT.zh(22, 'Medium'), color: '#E6EAF4', align: 'left', baseline: 'middle', alpha: ba });
  }

  // Past $100K: what a straight line would have done (dashed), and how the two ends actually bend.
  for (const [p, tg] of [
    [85, T.c3f.t0 + 1.15],
    [15, T.c3g.t0 + 1.2],
  ]) {
    const ga = clamp((t - tg) / 0.3);
    if (ga <= 0) continue;
    const pts = curvePoints(pctStraight(ROWS[p]), W100, 1, 40);
    strokeDashed(ctx, pts, STYLE[p].col, 1.8, ga * 0.6);
    const tag = p === 85 ? '加速 ↗' : '变平 →';
    const ty = p === 85 ? Y(pctCurve(ROWS[p])(0.88)) - 30 : Y(pctCurve(ROWS[p])(0.88)) + 30;
    glowText(ctx, tag, X(0.88), ty, {
      font: FONT.zh(22, 'Medium'),
      color: STYLE[p].col,
      glow: STYLE[p].glow,
      blur: 10,
      alpha: ga,
      baseline: 'middle',
    });
  }
  drawEndFolk(ctx, t, 85, T.c3f.t0 + 1.35, 1);
  drawEndFolk(ctx, t, 15, T.c3g.t0 + 1.4, 1);

  // c3h: the two bends offset each other; the average stays a straight line.
  const mp = ease.inOutCubic(clamp((t - (T.c3h.t0 + 0.35)) / 1.0));
  if (mp > 0) {
    const n = Math.max(1, Math.round((MEAN_PTS.length - 1) * mp));
    strokeDashed(ctx, MEAN_PTS.slice(0, n + 1), '#FFFFFF', 3, 0.9, [14, 9]);
    const la = clamp((t - (T.c3h.t0 + 1.0)) / 0.3);
    glowText(ctx, '平均：一条直线', X(0.4), Y(pctMean(0.4)) - 36, {
      font: FONT.zh(24, 'Medium'),
      color: '#FFFFFF',
      glow: 'rgba(255,255,255,0.5)',
      blur: 10,
      alpha: la,
      baseline: 'middle',
    });
    glowText(ctx, '= 2021 年看到的样子', X(0.4), Y(pctMean(0.4)) - 4, {
      font: FONT.zh(18),
      color: 'rgba(170,240,215,0.85)',
      alpha: la,
      baseline: 'middle',
    });
  }
  const da = clamp((t - (T.c3h.t0 + 0.2)) / 0.3);
  if (da > 0) {
    const xa = X(0.955);
    drawArrow(ctx, xa, Y(pctStraight(ROWS[15])(0.955)), Y(pctCurve(ROWS[15])(0.955)), C.coral, C.coralGlow, da);
    drawArrow(ctx, xa, Y(pctStraight(ROWS[85])(0.955)), Y(pctCurve(ROWS[85])(0.955)), STYLE[85].col, STYLE[85].glow, da);
  }
  ctx.restore();
}

/* ---------- c3i–c3m: a yes/no question can't tell happy from very happy ---------- */

const QC = { x: 960, y: 256, w: 760, h: 120 };
const qcA = (t) => clamp((t - (T.c3i.t0 + 0.25)) / 0.35) * (1 - clamp((t - T.c3n.t0) / 0.35));

function drawQuestionCard(ctx, t) {
  const a = qcA(t);
  if (a <= 0) return;
  const k = ease.outCubic(clamp((t - (T.c3i.t0 + 0.25)) / 0.45));
  const { x, w, h } = QC;
  const y = QC.y + (1 - k) * 24;
  ctx.save();
  ctx.globalAlpha *= a;
  rr(ctx, x - w / 2, y - h / 2, w, h, 18);
  ctx.fillStyle = 'rgba(9,14,26,0.93)';
  ctx.fill();
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = 'rgba(98,212,255,0.55)';
  ctx.shadowColor = C.cyanGlow;
  ctx.shadowBlur = 16;
  ctx.stroke();
  ctx.restore();
  glowText(ctx, '2010 · 盖洛普问卷 · GALLUP', x - w / 2 + 28, y - h / 2 + 24, {
    font: FONT.mono(13),
    color: 'rgba(98,212,255,0.75)',
    align: 'left',
    letterSpacing: 2,
    baseline: 'middle',
    alpha: a,
  });
  glowText(ctx, '昨天很多时候，你开心吗？', x - w / 2 + 34, y + 16, {
    font: FONT.zh(32, 'Medium'),
    color: '#F3F1EC',
    align: 'left',
    baseline: 'middle',
    alpha: a,
  });
  // Each button lights up when one of the people below gives that answer.
  const lit = (ans) => DEMO.reduce((m, d) => (d.ans === ans ? Math.max(m, env(t, d.tIn() + 0.28, d.tIn() + 0.8, 0.1, 0.3)) : m), 0);
  [
    ['是', x + 205, lit('是')],
    ['否', x + 305, lit('否')],
  ].forEach(([zh, bx, on]) => {
    ctx.save();
    ctx.globalAlpha *= a;
    rr(ctx, bx - 42, y - 8, 84, 48, 24);
    ctx.fillStyle = `rgba(98,212,255,${(0.05 + 0.2 * on).toFixed(3)})`;
    ctx.fill();
    ctx.lineWidth = 1.6;
    ctx.strokeStyle = `rgba(98,212,255,${(0.4 + 0.55 * on).toFixed(3)})`;
    ctx.shadowColor = C.cyanGlow;
    ctx.shadowBlur = 18 * on;
    ctx.stroke();
    ctx.restore();
    glowText(ctx, zh, bx, y + 17, { font: FONT.zh(26, 'Medium'), color: on > 0.4 ? '#E9F8FF' : 'rgba(236,236,240,0.8)', baseline: 'middle', alpha: a });
  });
  glowText(ctx, '只能二选一 · YES / NO ONLY', x, y + h / 2 + 24, {
    font: FONT.mono(13),
    color: 'rgba(98,212,255,0.65)',
    letterSpacing: 3,
    baseline: 'middle',
    alpha: a * clamp((t - (T.c3j.t0 + 0.2)) / 0.3),
  });
}

const D_FEET = 812;
const D_S = 1.3;
const BAR_B = 612;
const BAR_H = 200;
const CEIL_LV = 0.42;
// c3j: one unhappy person answers 否, one happy person 是; c3k: two happier people can still only say 是.
const DEMO = [
  { x: 640, mood: -0.55, level: 0.18, ans: '否', label: '不开心', tIn: () => T.c3j.t0 + 0.35 },
  { x: 900, mood: 0.45, level: 0.55, ans: '是', label: '开心', tIn: () => T.c3j.t0 + 0.95 },
  { x: 1140, mood: 0.8, level: 0.78, ans: '是', label: '很开心', tIn: () => T.c3k.t0 + 0.2 },
  { x: 1380, mood: 1, level: 1, ans: '是', label: '非常开心', tIn: () => T.c3k.t0 + 0.6 },
].map((d, i) => ({ ...d, f: makeFolk(mulberry32(300 + i), { hairStyle: ['bald', 'long', 'curly', 'bun'][i] }) }));

const CEIL_T = () => T.c3l.t0 + 0.25;

function drawCeilingDemo(ctx, t) {
  const a = qcA(t);
  if (a <= 0 || t < T.c3j.t0) return;
  const ceilK = clamp((t - CEIL_T()) / 0.22);
  const yCeilRest = BAR_B - CEIL_LV * BAR_H;
  const yCeil = lerp(BAR_B - BAR_H - 30, yCeilRest, ease.outBack(ceilK, 2.2));
  // While it comes down, the ceiling pushes the happy bars down with it.
  const capY = ceilK > 0 ? yCeil : -Infinity;
  ctx.save();
  ctx.globalAlpha *= a;

  for (const d of DEMO) {
    const ti = d.tIn();
    const k = clamp((t - ti) / 0.35);
    if (k <= 0) continue;
    const pin = ease.outBack(k);
    const al = clamp(k * 3);
    const raise = ease.outBack(clamp((t - ti - 0.2) / 0.28));
    const pk = ease.outBack(clamp((t - ti - 0.28) / 0.3));
    drawFolk(ctx, d.f, {
      x: d.x,
      y: D_FEET + (1 - pin) * 30,
      s: D_S,
      t,
      alpha: al,
      mood: d.mood,
      armR: lerp(ARM_DOWN, ARM_UP, raise),
      prop: pk > 0 ? { kind: 'paddle', side: 1, text: d.ans, k: pk, fs: 26, w: 54, h: 42 } : null,
    });
    glowText(ctx, d.label, d.x, D_FEET + 36, {
      font: FONT.zh(22, 'Medium'),
      color: d.mood < 0 ? C.coral : 'rgba(236,236,240,0.85)',
      alpha: al,
      baseline: 'middle',
    });

    // How happy they really are (bar above the head).
    const fill = d.level * ease.inOutCubic(clamp((t - ti - 0.35) / 0.5));
    const bx = d.x - 9;
    rr(ctx, bx, BAR_B - BAR_H, 18, BAR_H, 9);
    ctx.fillStyle = `rgba(255,255,255,${(0.05 * al).toFixed(3)})`;
    ctx.fill();
    ctx.lineWidth = 1.2;
    ctx.strokeStyle = `rgba(214,220,234,${(0.25 * al).toFixed(3)})`;
    ctx.stroke();
    if (fill > 0.01) {
      const top = BAR_B - fill * BAR_H;
      const capped = d.mood >= 0 ? Math.min(BAR_B - 4, Math.max(top, capY)) : top;
      ctx.save();
      ctx.globalAlpha *= al;
      // Above the ceiling the measure can't see it: only an outline remains.
      if (capped > top) {
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = 'rgba(111,227,193,0.55)';
        ctx.lineWidth = 1.5;
        rr(ctx, bx + 1, top, 16, capped - top, 6);
        ctx.stroke();
        ctx.setLineDash([]);
      }
      const g = ctx.createLinearGradient(0, BAR_B, 0, BAR_B - BAR_H);
      g.addColorStop(0, d.mood < 0 ? C.coral : C.gold);
      g.addColorStop(1, C.mint);
      rr(ctx, bx + 1, capped, 16, BAR_B - capped, 7);
      ctx.fillStyle = g;
      ctx.fill();
      ctx.restore();
    }
  }

  const leg = clamp((t - (DEMO[1].tIn() + 0.6)) / 0.3);
  glowText(ctx, '真实感受', DEMO[1].x - 34, BAR_B - BAR_H + 12, {
    font: FONT.zh(20),
    color: 'rgba(170,240,215,0.85)',
    align: 'right',
    baseline: 'middle',
    alpha: leg,
  });

  // The ceiling: "yes" is the top score.
  if (ceilK > 0) {
    const x0 = DEMO[1].x - 70;
    const x1 = DEMO[3].x + 70;
    ctx.save();
    ctx.strokeStyle = C.coral;
    ctx.lineWidth = 6;
    ctx.lineCap = 'round';
    ctx.shadowColor = C.coralGlow;
    ctx.shadowBlur = 18;
    ctx.globalAlpha *= clamp(ceilK * 3);
    ctx.beginPath();
    ctx.moveTo(x0, yCeil);
    ctx.lineTo(x1, yCeil);
    ctx.stroke();
    ctx.restore();
    const la = clamp((t - (CEIL_T() + 0.25)) / 0.3);
    glowText(ctx, '天花板效应', x1 + 18, yCeilRest - 10, {
      font: FONT.zh(26, 'Medium'),
      color: C.coral,
      glow: C.coralGlow,
      blur: 10,
      align: 'left',
      baseline: 'middle',
      alpha: la,
    });
    glowText(ctx, 'CEILING EFFECT', x1 + 18, yCeilRest + 18, {
      font: FONT.mono(12),
      color: 'rgba(255,170,155,0.7)',
      align: 'left',
      letterSpacing: 3,
      baseline: 'middle',
      alpha: la,
    });
  }

  // c3m: the measure separates unhappy from happy, but not happy from happier.
  const okA = clamp((t - (T.c3m.t0 + 0.3)) / 0.3);
  if (okA > 0) {
    // Bracket from the 否 bar to the first 是 bar: that difference the question can see.
    const yb = BAR_B - BAR_H * 0.18 - 24;
    const bx0 = DEMO[0].x + 16;
    const bx1 = DEMO[1].x - 18;
    ctx.save();
    ctx.globalAlpha *= okA;
    ctx.strokeStyle = 'rgba(111,227,193,0.8)';
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    ctx.moveTo(bx0, yb + 8);
    ctx.lineTo(bx0, yb);
    ctx.lineTo(bx1, yb);
    ctx.lineTo(bx1, yb + 8);
    ctx.stroke();
    ctx.restore();
    glowText(ctx, '分得清', (DEMO[0].x + DEMO[1].x) / 2, yb - 20, {
      font: FONT.zh(22, 'Medium'),
      color: C.mint,
      glow: C.mintGlow,
      blur: 8,
      alpha: okA,
      baseline: 'middle',
    });
  }
  const ma = clamp((t - (T.c3m.t0 + 0.8)) / 0.3);
  if (ma > 0) {
    glowText(ctx, '分不清有多开心', DEMO[2].x, BAR_B - BAR_H - 32, {
      font: FONT.zh(24, 'Medium'),
      color: C.coral,
      glow: C.coralGlow,
      blur: 8,
      alpha: ma,
      baseline: 'middle',
    });
  }
  ctx.restore();
}

/* ---------- c3n: the 2010 curve has the same shape as the least happy line ---------- */

const GHOST_PTS = curvePoints(emoWide);

function drawRecap(ctx, t) {
  const t0 = T.c3n.t0;
  const a = clamp((t - (t0 - 0.05)) / 0.35);
  if (a <= 0) return;
  ctx.save();
  ctx.globalAlpha *= a;
  drawLogAxes(ctx, t, t0 - 0.05, AXIS_WIDE);
  const p15 = ease.inOutCubic(clamp((t - (t0 + 0.15)) / 0.7));
  strokeGlowPath(ctx, PTS[15], p15, { color: C.coral, glow: C.coralGlow, width: 3.4 });
  const gp = ease.inOutCubic(clamp((t - (t0 + 0.35)) / 0.7));
  if (gp > 0) {
    const n = Math.max(1, Math.round((GHOST_PTS.length - 1) * gp));
    strokeDashed(ctx, GHOST_PTS.slice(0, n + 1), C.cyan, 2.6, 0.85);
  }
  const la = clamp((t - (t0 + 0.9)) / 0.3);
  glowText(ctx, '2023 · 最不快乐的人', PLOT.R + 26, Y(pctCurve(ROWS[15])(1)), {
    font: FONT.zh(21, 'Medium'),
    color: C.coral,
    align: 'left',
    baseline: 'middle',
    alpha: la,
  });
  glowText(ctx, '2010 · 是/否问卷', PLOT.R + 26, Y(emoWide(1)), {
    font: FONT.zh(21, 'Medium'),
    color: C.cyan,
    align: 'left',
    baseline: 'middle',
    alpha: la,
  });
  for (const [u, v, col, glow] of [
    [W75, emoWide(W75), C.cyan, C.cyanGlow],
    [W100, pctCurve(ROWS[15])(W100), C.coral, C.coralGlow],
  ]) {
    glowDot(ctx, X(u), Y(v), 6, col, glow, la);
  }
  const ca = ease.outBack(clamp((t - (t0 + 1.2)) / 0.35));
  if (ca > 0) {
    ctx.save();
    ctx.translate(960, PLOT.T + 6);
    ctx.scale(ca, ca);
    rr(ctx, -200, -26, 400, 52, 26);
    ctx.fillStyle = 'rgba(244,196,106,0.1)';
    ctx.fill();
    ctx.lineWidth = 1.6;
    ctx.strokeStyle = 'rgba(244,196,106,0.7)';
    ctx.stroke();
    glowText(ctx, '同一个形状：先涨，后平', 0, 1, { font: FONT.zh(24, 'Medium'), color: C.gold, glow: C.goldGlow, blur: 8, baseline: 'middle' });
    ctx.restore();
  }
  ctx.restore();
}

/* ---------- scene ---------- */

export function drawCh3(ctx, t) {
  const fadeOut = 1 - clamp((t - (T.c3n.t1 - 0.2)) / 0.4);
  if (fadeOut <= 0 || t < T.c2j.t0) return;
  ctx.save();
  ctx.globalAlpha *= fadeOut;
  const head = clamp((t - T.c3a.t0) / 0.4);
  drawChapterLabel(ctx, '研究 03 · 握手言和', 'A CONFLICT RESOLVED', head);
  drawPill(ctx, 'Killingsworth, Kahneman & Mellers · 2023', 'PNAS', 960, 152, clamp((t - T.c3a.t0 - 0.2) / 0.4));

  drawTrio(ctx, t);
  drawPaper(ctx, t);
  drawStampChip(ctx, t);
  drawPctChart(ctx, t);
  drawSort(ctx, t);
  drawQuestionCard(ctx, t);
  drawCeilingDemo(ctx, t);
  drawRecap(ctx, t);
  ctx.restore();
}
