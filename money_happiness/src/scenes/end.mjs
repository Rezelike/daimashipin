// 结尾：标题回扣 → 大多数人收入越高越快乐 → 有钱却不快乐的人，钱帮不上忙 → 三篇论文 → 资料来源。
// 结论措辞来自 2023 年论文第一作者 Killingsworth 在 Penn 新闻稿里的总结。
import { clamp, lerp, ease, mulberry32 } from '../engine/util.mjs';
import { FONT } from '../engine/fonts.mjs';
import { C, rr, circle, glowText, strokeGlowPath, drawStage } from '../engine/draw.mjs';
import { drawFolk, makeFolk, ARM_DOWN } from '../engine/folk.mjs';
import { drawPerson, PEOPLE } from '../engine/people.mjs';
import { CUES } from '../cues.mjs';

const T = Object.fromEntries(CUES.map((c) => [c.id, c]));

/* ---------- e1: the title question comes back ---------- */

const TITLE = '钱能买到快乐吗？';

function drawEndTitle(ctx, t) {
  const t0 = T.e1.t0;
  const out = clamp((t - (T.e4.t0 - 0.1)) / 0.35);
  if (t < t0 || out >= 1) return;
  const font = FONT.zh(100, 'SemiBold');
  const chars = [...TITLE];
  ctx.save();
  ctx.font = font;
  ctx.letterSpacing = '0px';
  const widths = chars.map((ch) => ctx.measureText(ch).width);
  const total = widths.reduce((a, b) => a + b, 0);
  const m = ease.inOutCubic(clamp((t - (T.e2.t0 - 0.05)) / 0.55));
  const s = lerp(1, 0.48, m);
  ctx.globalAlpha *= 1 - out;
  ctx.translate(960, lerp(440, 268, m));
  ctx.scale(s, s);
  let x = -total / 2;
  chars.forEach((ch, i) => {
    const p = clamp((t - (t0 + 0.1 + i * 0.06)) / 0.38);
    if (p > 0) {
      const e = ease.outCubic(p);
      ctx.save();
      if (p < 1) ctx.filter = `blur(${((1 - e) * 8).toFixed(2)}px)`;
      glowText(ctx, ch, x, (1 - e) * 20, {
        font,
        color: C.gold,
        glow: C.goldGlow,
        blur: 34 * s,
        alpha: e,
        align: 'left',
        baseline: 'middle',
      });
      ctx.restore();
    }
    x += widths[i];
  });
  const ca = clamp((t - (t0 + 0.7)) / 0.4) * (1 - m);
  glowText(ctx, 'CAN MONEY BUY HAPPINESS?', 0, 92, {
    font: FONT.mono(19),
    color: 'rgba(235,215,170,0.62)',
    alpha: ca,
    letterSpacing: 9,
    baseline: 'middle',
  });
  ctx.restore();
}

/* ---------- e2: for most people, higher income goes with more happiness ---------- */

// Feet at 722 keeps the axis label (ROW_FEET + 92) clear of the subtitle block (top ≈ 866).
const ROW_FEET = 722;
const ROW_S = 1.25;
const INCOMES = ['$15K', '$25K', '$40K', '$60K', '$100K', '$150K', '$200K'];
const ROW = INCOMES.map((label, i) => ({
  label,
  x: 360 + i * 160,
  mood: lerp(-0.2, 1, i / (INCOMES.length - 1)),
  f: makeFolk(mulberry32(900 + i)),
}));
const rowOut = (t) => clamp((t - (T.e4.t0 - 0.1)) / 0.35);

function drawMostPeople(ctx, t) {
  const t0 = T.e2.t0 + 0.25;
  const out = rowOut(t);
  if (t < t0 || out >= 1) return;
  // e3: the row steps back so the exception stands out.
  const back = lerp(1, 0.4, ease.inOutCubic(clamp((t - T.e3.t0) / 0.4)));
  ctx.save();
  ctx.globalAlpha *= (1 - out) * back;
  const axA = clamp((t - t0) / 0.4);
  ctx.save();
  ctx.globalAlpha *= axA;
  ctx.strokeStyle = 'rgba(232,206,150,0.45)';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(ROW[0].x - 70, ROW_FEET + 64);
  ctx.lineTo(ROW[ROW.length - 1].x + 80, ROW_FEET + 64);
  ctx.lineTo(ROW[ROW.length - 1].x + 70, ROW_FEET + 58);
  ctx.moveTo(ROW[ROW.length - 1].x + 80, ROW_FEET + 64);
  ctx.lineTo(ROW[ROW.length - 1].x + 70, ROW_FEET + 70);
  ctx.stroke();
  ctx.restore();
  glowText(ctx, '家庭年收入 · INCOME', ROW[ROW.length - 1].x + 80, ROW_FEET + 92, {
    font: FONT.mono(13),
    color: 'rgba(232,206,150,0.6)',
    align: 'right',
    letterSpacing: 3,
    baseline: 'middle',
    alpha: axA,
  });
  ROW.forEach((p, i) => {
    const k = clamp((t - t0 - i * 0.09) / 0.35);
    if (k <= 0) return;
    const pin = ease.outBack(k);
    const mood = lerp(0.1, p.mood, ease.outCubic(clamp((t - t0 - 0.35 - i * 0.09) / 0.35)));
    drawFolk(ctx, p.f, { x: p.x, y: ROW_FEET + (1 - pin) * 26, s: ROW_S, t, alpha: clamp(k * 3), mood, look: 0.2 });
    glowText(ctx, p.label, p.x, ROW_FEET + 36, {
      font: FONT.mono(18, 'SemiBold'),
      color: 'rgba(236,230,214,0.8)',
      alpha: clamp(k * 3),
      baseline: 'middle',
    });
  });
  // A rising line over their heads.
  const pts = ROW.map((p) => [p.x, ROW_FEET - 146 * ROW_S + 40 - (p.mood + 0.2) * 50]);
  const ap = ease.inOutCubic(clamp((t - (t0 + 1.1)) / 0.7));
  strokeGlowPath(ctx, pts, ap, { color: C.mint, glow: C.mintGlow, width: 3 });
  if (ap >= 1) {
    const [x1, y1] = pts[pts.length - 1];
    const [x0, y0] = pts[pts.length - 2];
    const ang = Math.atan2(y1 - y0, x1 - x0);
    ctx.save();
    ctx.translate(x1, y1);
    ctx.rotate(ang);
    ctx.fillStyle = C.mint;
    ctx.shadowColor = C.mintGlow;
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.moveTo(10, 0);
    ctx.lineTo(-8, -8);
    ctx.lineTo(-8, 8);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }
  ctx.restore();
}

/* ---------- e3: rich and miserable: more money doesn't help ---------- */

const EX = { x: 1650, s: 1.55, f: makeFolk(mulberry32(20), { hairStyle: 'short', top: '#6B7E9E', skin: '#F1CBA4', hair: '#3F2C22' }) };
const COINS = (() => {
  const r = mulberry32(100000);
  return Array.from({ length: 6 }, (_, i) => ({ dt: 0.5 + i * 0.28, dx: (r() - 0.5) * 70, side: r() < 0.5 ? -1 : 1, spin: r() * 6 }));
})();

function drawCoin(ctx, x, y, r, spin, alpha) {
  if (alpha <= 0) return;
  const sx = Math.max(0.25, Math.abs(Math.cos(spin)));
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(x, y);
  ctx.scale(sx, 1);
  ctx.shadowColor = C.goldGlow;
  ctx.shadowBlur = 10;
  circle(ctx, 0, 0, r, C.gold);
  ctx.shadowBlur = 0;
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = '#B8862F';
  ctx.beginPath();
  ctx.arc(0, 0, r * 0.72, 0, Math.PI * 2);
  ctx.stroke();
  ctx.fillStyle = '#7A5418';
  ctx.font = FONT.mono(Math.round(r * 1.1), 'SemiBold');
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('$', 0, 1);
  ctx.restore();
}

function drawException(ctx, t) {
  const t0 = T.e3.t0 + 0.1;
  const out = rowOut(t);
  if (t < t0 || out >= 1) return;
  const k = clamp((t - t0) / 0.35);
  const a = clamp(k * 3) * (1 - out);
  ctx.save();
  ctx.globalAlpha *= a;
  ctx.setLineDash([6, 8]);
  ctx.strokeStyle = 'rgba(214,220,234,0.3)';
  ctx.lineWidth = 1.4;
  ctx.beginPath();
  ctx.moveTo(1480, 430);
  ctx.lineTo(1480, ROW_FEET + 70);
  ctx.stroke();
  ctx.restore();

  // Coins drop on them and bounce away; their face doesn't change.
  const FALL = 0.32;
  const hitY = ROW_FEET - 102 * EX.s;
  let flinch = 0;
  for (const c of COINS) {
    const b = t - (t0 + c.dt) - FALL;
    if (b >= 0 && b < 0.12) flinch = Math.max(flinch, 1 - b / 0.12);
  }
  drawFolk(ctx, EX.f, {
    x: EX.x,
    y: ROW_FEET + (1 - ease.outBack(k)) * 26 + flinch * 3,
    s: EX.s,
    t,
    alpha: a,
    mood: -0.55,
    lookY: 0.6,
    armL: ARM_DOWN,
    armR: ARM_DOWN,
  });
  for (const c of COINS) {
    const d = t - (t0 + c.dt);
    if (d < 0) continue;
    let x = EX.x + c.dx * 0.3;
    let y;
    let al = 1;
    if (d < FALL) {
      y = lerp(380, hitY, ease.inQuad(d / FALL));
    } else {
      const b = d - FALL;
      x += c.side * 160 * b;
      y = hitY - 260 * b + 900 * b * b;
      al = 1 - clamp((b - 0.3) / 0.3);
      if (b < 0.5) {
        glowText(ctx, '+$', EX.x + c.side * 52, hitY - 30 - b * 70, {
          font: FONT.mono(20, 'SemiBold'),
          color: C.gold,
          glow: C.goldGlow,
          blur: 8,
          alpha: a * (1 - b / 0.5),
          baseline: 'middle',
        });
      }
    }
    drawCoin(ctx, x, y, 16, c.spin + d * 14, a * al);
  }
  // Two-line caption under the feet; above the head is where the coins and "+$" pops fly.
  glowText(ctx, '收入很高', EX.x, ROW_FEET + 36, { font: FONT.zh(18, 'Medium'), color: 'rgba(236,230,214,0.8)', alpha: a, baseline: 'middle' });
  glowText(ctx, '却不快乐', EX.x, ROW_FEET + 74, { font: FONT.zh(28, 'Medium'), color: C.coral, glow: C.coralGlow, blur: 8, alpha: a, baseline: 'middle' });
  // Their happiness bar stays flat while the coins pile on.
  const bx = EX.x + 84;
  const by = ROW_FEET - 20;
  ctx.save();
  ctx.globalAlpha *= a;
  rr(ctx, bx - 8, by - 150, 16, 150, 8);
  ctx.fillStyle = 'rgba(255,255,255,0.05)';
  ctx.fill();
  ctx.lineWidth = 1.2;
  ctx.strokeStyle = 'rgba(214,220,234,0.3)';
  ctx.stroke();
  rr(ctx, bx - 7, by - 30, 14, 30, 7);
  ctx.fillStyle = C.coral;
  ctx.fill();
  ctx.restore();
  glowText(ctx, '快乐', bx, by + 20, { font: FONT.zh(14), color: 'rgba(255,170,155,0.8)', alpha: a, baseline: 'middle' });
}

/* ---------- e4: three papers, thirteen years ---------- */

const PAPERS = [
  { year: '2010', who: 'Kahneman & Deaton', finding: '快乐在 $75K 附近变平', col: C.cyan, glow: C.cyanGlow },
  { year: '2021', who: 'Killingsworth', finding: '过了 $75K，快乐还在涨', col: C.mint, glow: C.mintGlow },
  { year: '2023', who: 'Killingsworth, Kahneman & Mellers', finding: '只有最不快乐的约 20% 会变平', col: C.gold, glow: C.goldGlow },
];
const CARD = { y: 372, w: 440, h: 196, xs: [440, 960, 1480] };
const papersOut = (t) => clamp((t - (T.e5.t0 - 0.05)) / 0.35);

function drawPapers(ctx, t) {
  const t0 = T.e4.t0 + 0.15;
  const out = papersOut(t);
  if (t < t0 || out >= 1) return;
  PAPERS.forEach((p, i) => {
    const k = ease.outCubic(clamp((t - t0 - i * 0.22) / 0.4));
    if (k <= 0) return;
    const a = k * (1 - out);
    const cx = CARD.xs[i];
    const cy = CARD.y + (1 - k) * 24;
    ctx.save();
    ctx.globalAlpha *= a;
    rr(ctx, cx - CARD.w / 2, cy - CARD.h / 2, CARD.w, CARD.h, 18);
    ctx.fillStyle = 'rgba(9,14,26,0.9)';
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = p.col;
    ctx.globalAlpha *= 0.6;
    ctx.stroke();
    ctx.restore();
    glowText(ctx, p.year, cx, cy - 52, { font: FONT.mono(30, 'SemiBold'), color: p.col, glow: p.glow, blur: 10, letterSpacing: 4, alpha: a, baseline: 'middle' });
    glowText(ctx, p.who, cx, cy - 8, { font: FONT.en(i === 2 ? 22 : 26), color: '#EDE9E0', alpha: a, baseline: 'middle' });
    glowText(ctx, p.finding, cx, cy + 42, { font: FONT.zh(22, 'Medium'), color: '#F3F1EC', alpha: a, baseline: 'middle' });
    if (i < PAPERS.length - 1) {
      glowText(ctx, '→', (CARD.xs[i] + CARD.xs[i + 1]) / 2, CARD.y, {
        font: FONT.mono(30),
        color: 'rgba(235,215,170,0.6)',
        alpha: a * clamp((t - t0 - i * 0.22 - 0.3) / 0.3),
        baseline: 'middle',
      });
    }
  });

  // The four researchers, together.
  const crew = [
    [PEOPLE.kahneman, 750],
    [PEOPLE.deaton, 890],
    [PEOPLE.killingsworth, 1030],
    [PEOPLE.mellers, 1170],
  ];
  // Names sit at floor + 30; 776 leaves ~60px above the subtitle block.
  const floor = 776;
  const sa = clamp((t - (t0 + 0.6)) / 0.35) * (1 - out);
  drawStage(ctx, floor, sa * 0.7);
  crew.forEach(([p, x], i) => {
    const k = clamp((t - (t0 + 0.6 + i * 0.1)) / 0.38);
    if (k <= 0) return;
    const pin = ease.outBack(k);
    drawPerson(ctx, { ...p, x, y: floor + (1 - pin) * 30, s: 0.5, mood: 0.6 }, t, clamp(k * 2.5) * (1 - out));
    glowText(ctx, p.zh, x, floor + 30, { font: FONT.zh(17), color: 'rgba(236,236,240,0.75)', alpha: clamp(k * 2.5) * (1 - out), baseline: 'middle' });
  });
}

/* ---------- e5: sources ---------- */

const REFS = [
  {
    title: 'High income improves evaluation of life but not emotional well-being',
    meta: 'KAHNEMAN & DEATON · PNAS 107, 16489–16493 (2010) · DOI 10.1073/pnas.1011492107',
  },
  {
    title: 'Experienced well-being rises with income, even above $75,000 per year',
    meta: 'KILLINGSWORTH · PNAS 118, e2016976118 (2021) · DOI 10.1073/pnas.2016976118',
  },
  {
    title: 'Income and emotional well-being: A conflict resolved',
    meta: 'KILLINGSWORTH, KAHNEMAN & MELLERS · PNAS 120, e2208661120 (2023) · DOI 10.1073/pnas.2208661120',
  },
];
const NOTES = [
  '曲线都是按论文结论画的示意图，不是原始数据；三项研究的样本都来自美国。',
  '一天里的提醒时刻是演示；$75,000 是 2008–09 年的美元。',
  '2024 年 PNAS 又刊出两封商榷信和作者回复，讨论还在继续。',
];

function drawSources(ctx, t) {
  const t0 = T.e5.t0 + 0.1;
  if (t < t0) return;
  const a = clamp((t - t0) / 0.4);
  const x0 = 330;
  glowText(ctx, '资料来源', x0, 236, { font: FONT.zh(34, 'SemiBold'), color: C.gold, glow: C.goldGlow, blur: 10, align: 'left', baseline: 'middle', alpha: a });
  glowText(ctx, 'SOURCES', x0 + 156, 240, { font: FONT.mono(15), color: 'rgba(235,215,170,0.6)', align: 'left', letterSpacing: 6, baseline: 'middle', alpha: a });
  REFS.forEach((r, i) => {
    const k = ease.outCubic(clamp((t - t0 - 0.15 - i * 0.15) / 0.4));
    if (k <= 0) return;
    const y = 330 + i * 120 + (1 - k) * 16;
    glowText(ctx, String(i + 1).padStart(2, '0'), x0, y, { font: FONT.mono(20, 'SemiBold'), color: C.gold, align: 'left', baseline: 'middle', alpha: a * k });
    glowText(ctx, r.title, x0 + 60, y, { font: FONT.en(32), color: '#F1EEE6', align: 'left', baseline: 'middle', alpha: a * k });
    glowText(ctx, r.meta, x0 + 60, y + 40, {
      font: FONT.mono(15),
      color: 'rgba(214,220,234,0.6)',
      align: 'left',
      letterSpacing: 1,
      baseline: 'middle',
      alpha: a * k,
    });
  });
  const na = clamp((t - (t0 + 0.75)) / 0.4);
  ctx.save();
  ctx.globalAlpha *= na;
  ctx.strokeStyle = 'rgba(214,220,234,0.18)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(x0, 676);
  ctx.lineTo(1590, 676);
  ctx.stroke();
  ctx.restore();
  NOTES.forEach((n, i) => {
    glowText(ctx, n, x0, 716 + i * 40, { font: FONT.zh(20), color: 'rgba(214,220,234,0.62)', align: 'left', baseline: 'middle', alpha: na });
  });
}

/* ---------- scene ---------- */

export function drawEnd(ctx, t) {
  if (t < T.e1.t0 - 0.1) return;
  const fadeOut = 1 - clamp((t - (T.e5.t1 - 0.05)) / 0.4);
  if (fadeOut <= 0) return;
  ctx.save();
  ctx.globalAlpha *= fadeOut;
  drawEndTitle(ctx, t);
  drawMostPeople(ctx, t);
  drawException(ctx, t);
  drawPapers(ctx, t);
  drawSources(ctx, t);
  ctx.restore();
}

export const END_T = () => T.e5.t1 + 0.4;
