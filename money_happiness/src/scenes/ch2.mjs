// 研究 02 · Killingsworth 2021：App 随机提醒 →「你现在感觉怎么样？」→ 1,725,994 次打分 → 过了 $75K 还在涨。
// 一天里的提醒时间（09:12 等）是演示用的，不是论文数据；论文只说"每天随机几次"。
import { clamp, lerp, ease, env, mulberry32, gauss, fmtInt } from '../engine/util.mjs';
import { FONT } from '../engine/fonts.mjs';
import {
  C,
  rr,
  circle,
  glowText,
  glowDot,
  drawChapterLabel,
  drawPill,
  strokeGlowPath,
  drawFixedDigits,
  drawStage,
} from '../engine/draw.mjs';
import {
  PLOT,
  X,
  Y,
  AXIS_WIDE,
  W75,
  W80,
  CEIL_V,
  U_CROSS,
  nowCurve,
  life21Curve,
  emoWide,
  curvePoints,
  drawLogAxes,
} from '../engine/chart.mjs';
import { drawFolk, drawFolkSprite, makeFolk, ARM_DOWN, ARM_UP, phoneCenter } from '../engine/folk.mjs';
import { drawPerson, PEOPLE } from '../engine/people.mjs';
import { CUES } from '../cues.mjs';

const T = Object.fromEntries(CUES.map((c) => [c.id, c]));
const uW = AXIS_WIDE.uOf;

const FLOOR2 = 772;
const LX = 600; // left actor: Killingsworth first, then the participant
const moodColor = (m) => (m < 0 ? C.coral : m < 0.4 ? C.gold : C.mint);
const moodGlow = (m) => (m < 0 ? C.coralGlow : m < 0.4 ? C.goldGlow : C.mintGlow);

/* ---------- Killingsworth ---------- */

function drawIntro(ctx, t) {
  const t0 = T.c2a.t0 + 0.2;
  const k = clamp((t - t0) / 0.4);
  const out = ease.inCubic(clamp((t - (T.c2b.t0 - 0.1)) / 0.3));
  if (k <= 0 || out >= 1) return;
  const pin = ease.outBack(k);
  const a = clamp(k * 2.5) * (1 - out);
  const y = FLOOR2 + (1 - pin) * 36 + out * 20;
  drawPerson(ctx, { ...PEOPLE.killingsworth, x: LX, y, s: 0.92, look: 0.7, mood: 0.45 }, t, a);
  glowText(ctx, PEOPLE.killingsworth.zh, LX, FLOOR2 + 42, {
    font: FONT.zh(26),
    color: C.white,
    alpha: a * 0.92,
    baseline: 'middle',
  });
  glowText(ctx, 'WHARTON · 2021', LX, FLOOR2 + 72, {
    font: FONT.mono(13),
    color: 'rgba(214,220,234,0.55)',
    alpha: a,
    letterSpacing: 3,
    baseline: 'middle',
  });
}

/* ---------- one participant's day: random pings ---------- */

const STRIP = { x0: 330, x1: 870, y: 352, h0: 7, h1: 23 };
const MOMENTS = [
  { t: () => T.c2b.t0 + 0.2, clock: '09:12', mood: 0.12 },
  { t: () => T.c2b.t0 + 0.9, clock: '13:47', mood: 0.62 },
  { t: () => T.c2b.t0 + 1.6, clock: '18:05', mood: -0.3 },
  { t: () => T.c2c.t0 + 0.05, clock: '21:30', mood: 0.78 },
];
const hourOf = (clock) => {
  const [h, m] = clock.split(':').map(Number);
  return h + m / 60;
};
const stripX = (clock) => lerp(STRIP.x0, STRIP.x1, (hourOf(clock) - STRIP.h0) / (STRIP.h1 - STRIP.h0));

function drawSun(ctx, x, y, r, alpha) {
  if (alpha <= 0) return;
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
  circle(ctx, x, y, r, C.gold);
  ctx.restore();
}

function drawMoon(ctx, x, y, r, alpha) {
  if (alpha <= 0) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.arc(x + r * 0.55, y - r * 0.3, r * 0.85, 0, Math.PI * 2, true);
  ctx.fillStyle = 'rgba(190,205,240,0.85)';
  ctx.fill('evenodd');
  ctx.restore();
}

function drawDayStrip(ctx, t) {
  const a = env(t, T.c2b.t0 - 0.05, T.c2f.t0 + 0.15, 0.3, 0.3);
  if (a <= 0) return;
  ctx.save();
  ctx.globalAlpha *= a;
  const g = ctx.createLinearGradient(STRIP.x0, 0, STRIP.x1, 0);
  g.addColorStop(0, 'rgba(244,196,106,0.6)');
  g.addColorStop(1, 'rgba(130,155,225,0.5)');
  ctx.strokeStyle = g;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(STRIP.x0, STRIP.y);
  ctx.lineTo(STRIP.x1, STRIP.y);
  ctx.stroke();
  ctx.lineWidth = 1.2;
  ctx.strokeStyle = 'rgba(214,220,234,0.3)';
  for (let h = STRIP.h0; h <= STRIP.h1; h += 2) {
    const x = lerp(STRIP.x0, STRIP.x1, (h - STRIP.h0) / (STRIP.h1 - STRIP.h0));
    ctx.beginPath();
    ctx.moveTo(x, STRIP.y - 5);
    ctx.lineTo(x, STRIP.y + 5);
    ctx.stroke();
  }
  ctx.restore();
  drawSun(ctx, STRIP.x0 - 34, STRIP.y, 7, a);
  drawMoon(ctx, STRIP.x1 + 34, STRIP.y, 9, a);
  for (const [txt, x] of [
    ['07:00', STRIP.x0],
    ['23:00', STRIP.x1],
  ]) {
    glowText(ctx, txt, x, STRIP.y + 30, { font: FONT.mono(13), color: 'rgba(214,220,234,0.45)', alpha: a, baseline: 'middle' });
  }
  glowText(ctx, '一天里随机提醒 · RANDOM PINGS', STRIP.x0 - 50, STRIP.y - 66, {
    font: FONT.mono(13),
    color: 'rgba(214,220,234,0.5)',
    align: 'left',
    letterSpacing: 2,
    alpha: a,
    baseline: 'middle',
  });
  for (const m of MOMENTS) {
    const tm = m.t();
    const k = clamp((t - tm) / 0.25);
    if (k <= 0) continue;
    const x = stripX(m.clock);
    const rp = clamp((t - tm) / 0.6);
    if (rp < 1) {
      ctx.save();
      ctx.globalAlpha *= a * (1 - rp) * 0.7;
      ctx.strokeStyle = moodColor(m.mood);
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, STRIP.y, lerp(6, 30, ease.outCubic(rp)), 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
    glowDot(ctx, x, STRIP.y, 6.5 * ease.outBack(k), moodColor(m.mood), moodGlow(m.mood), a);
    glowText(ctx, m.clock, x, STRIP.y - 28 + (1 - k) * 6, {
      font: FONT.mono(15, 'SemiBold'),
      color: moodColor(m.mood),
      alpha: a * k,
      baseline: 'middle',
    });
  }
}

const PARTICIPANT = makeFolk(mulberry32(2021), { hairStyle: 'bun', top: '#5E8F57', skin: '#E4B286', hair: '#3F2C22' });
const P_S = 2.3;
const ARM_REST = 0.5;
const ARM_LOOK = 2.1;

function participantPose(t) {
  let mood = 0.2;
  let up = 0;
  let lit = 0;
  MOMENTS.forEach((m, i) => {
    const tm = m.t();
    mood = lerp(mood, m.mood, ease.outCubic(clamp((t - tm - 0.2) / 0.25)));
    // The last ping stays up: that's the one being answered on the big phone.
    const hold = i === MOMENTS.length - 1 ? 99 : 0.42;
    up = Math.max(up, ease.outBack(clamp((t - tm) / 0.16)) * (1 - ease.inOutCubic(clamp((t - tm - hold) / 0.18))));
    lit = Math.max(lit, clamp((t - tm) / 0.06) * (1 - clamp((t - tm - hold - 0.1) / 0.2)));
  });
  return { mood, armR: lerp(ARM_REST, ARM_LOOK, up), lit, look: lerp(0.2, 1, up), lookY: lerp(0.3, -0.3, up) };
}

function drawParticipant(ctx, t) {
  const k = clamp((t - (T.c2b.t0 - 0.05)) / 0.35);
  const out = ease.inCubic(clamp((t - T.c2f.t0) / 0.35));
  if (k <= 0 || out >= 1) return;
  const pin = ease.outBack(k);
  const p = participantPose(t);
  drawFolk(ctx, PARTICIPANT, {
    x: LX,
    y: FLOOR2 + (1 - pin) * 30,
    s: P_S * (1 - 0.15 * out),
    t,
    alpha: clamp(k * 3) * (1 - out),
    mood: p.mood,
    look: p.look,
    lookY: p.lookY,
    armR: p.armR,
    prop: { kind: 'phone', side: 1, lit: p.lit },
  });
}

/** c2d: the 2010 way (recall yesterday) gets crossed out. */
function drawYesterdayBubble(ctx, t) {
  const t0 = T.c2d.t0;
  const k = ease.outBack(clamp((t - t0 - 0.05) / 0.3));
  const out = clamp((t - t0 - 1.5) / 0.3);
  if (k <= 0 || out >= 1) return;
  const a = clamp(k * 2) * (1 - out);
  const bx = LX - 175;
  const by = 476;
  ctx.save();
  ctx.globalAlpha *= a;
  ctx.fillStyle = 'rgba(236,240,248,0.1)';
  ctx.strokeStyle = 'rgba(214,220,234,0.55)';
  ctx.lineWidth = 1.5;
  [
    [LX - 62, 552, 5],
    [LX - 92, 526, 7.5],
  ].forEach(([x, y, r]) => {
    ctx.beginPath();
    ctx.arc(x, y, r * k, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  });
  ctx.translate(bx, by);
  ctx.scale(k, k);
  rr(ctx, -70, -30, 140, 60, 30);
  ctx.fill();
  ctx.stroke();
  ctx.restore();
  drawSun(ctx, bx - 38, by, 8 * k, a);
  glowText(ctx, '昨天', bx + 16, by + 1, { font: FONT.zh(26, 'Medium'), color: '#EDE7DA', baseline: 'middle', alpha: a });
  glowText(ctx, '2010 · 回想昨天', bx, by + 56, {
    font: FONT.mono(13),
    color: 'rgba(214,220,234,0.55)',
    letterSpacing: 2,
    baseline: 'middle',
    alpha: a,
  });
  const sp = ease.outCubic(clamp((t - t0 - 0.5) / 0.22));
  if (sp > 0) {
    ctx.save();
    ctx.globalAlpha *= a;
    ctx.strokeStyle = C.coral;
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.shadowColor = C.coralGlow;
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.moveTo(bx - 84, by + 26);
    ctx.lineTo(lerp(bx - 84, bx + 84, sp), lerp(by + 26, by - 26, sp));
    ctx.stroke();
    ctx.restore();
  }
}

/** c2e: the 2010 answer format (yes / no) gets crossed out. */
function drawGhostYesNo(ctx, t) {
  const t0 = T.c2e.t0;
  const k = ease.outCubic(clamp((t - t0 - 0.05) / 0.3));
  const out = clamp((t - (T.c2f.t0 - 0.15)) / 0.3);
  if (k <= 0 || out >= 1) return;
  const a = k * (1 - out);
  const cx = LX - 190;
  const ys = [500, 566];
  [
    ['是', 'YES', ys[0]],
    ['否', 'NO', ys[1]],
  ].forEach(([zh, en, y]) => {
    ctx.save();
    ctx.globalAlpha *= a;
    rr(ctx, cx - 76, y - 25 + (1 - k) * 10, 152, 50, 25);
    ctx.fillStyle = 'rgba(255,255,255,0.04)';
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = 'rgba(214,220,234,0.38)';
    ctx.stroke();
    ctx.restore();
    glowText(ctx, zh, cx - 20, y + 1 + (1 - k) * 10, { font: FONT.zh(26, 'Medium'), color: 'rgba(236,236,240,0.8)', baseline: 'middle', alpha: a });
    glowText(ctx, en, cx + 26, y + 2 + (1 - k) * 10, {
      font: FONT.mono(14),
      color: 'rgba(214,220,234,0.55)',
      baseline: 'middle',
      letterSpacing: 2,
      alpha: a,
    });
  });
  glowText(ctx, '2010 · 只能二选一', cx, 622, {
    font: FONT.mono(13),
    color: 'rgba(214,220,234,0.55)',
    letterSpacing: 2,
    baseline: 'middle',
    alpha: a,
  });
  const sp = ease.outCubic(clamp((t - t0 - 0.45) / 0.25));
  if (sp > 0) {
    ctx.save();
    ctx.globalAlpha *= a;
    ctx.strokeStyle = C.coral;
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.shadowColor = C.coralGlow;
    ctx.shadowBlur = 12;
    const [x0, y0, x1, y1] = [cx - 92, ys[0] - 40, cx + 92, ys[1] + 40];
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(lerp(x0, x1, sp), lerp(y0, y1, sp));
    const sp2 = ease.outCubic(clamp((t - t0 - 0.6) / 0.25));
    if (sp2 > 0) {
      ctx.moveTo(x1, y0);
      ctx.lineTo(lerp(x1, x0, sp2), lerp(y0, y1, sp2));
    }
    ctx.stroke();
    ctx.restore();
  }
}

/* ---------- the app on a big phone ---------- */

const PH = { x: 1250, y: 500, w: 320, h: 540 };

function sliderAt(t) {
  let v = 0.5;
  v = lerp(v, 0.78, ease.inOutCubic(clamp((t - (T.c2c.t0 + 0.45)) / 0.6)));
  // c2e: sweep the whole range, very bad → very good, then settle back.
  const s0 = T.c2e.t0 + 0.35;
  v = lerp(v, 0.03, ease.inOutCubic(clamp((t - s0) / 0.45)));
  v = lerp(v, 0.97, ease.inOutCubic(clamp((t - s0 - 0.5) / 0.7)));
  v = lerp(v, 0.78, ease.inOutCubic(clamp((t - s0 - 1.25) / 0.4)));
  return v;
}

function drawAppIcon(ctx, x, y, size, alpha) {
  if (alpha <= 0) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  rr(ctx, x - size / 2, y - size / 2, size, size, size * 0.26);
  const g = ctx.createLinearGradient(x, y - size / 2, x, y + size / 2);
  g.addColorStop(0, '#8BF0D2');
  g.addColorStop(1, '#2E9C86');
  ctx.fillStyle = g;
  ctx.shadowColor = C.mintGlow;
  ctx.shadowBlur = size * 0.3;
  ctx.fill();
  ctx.shadowBlur = 0;
  const ink = '#123A33';
  circle(ctx, x - size * 0.16, y - size * 0.08, size * 0.06, ink);
  circle(ctx, x + size * 0.16, y - size * 0.08, size * 0.06, ink);
  ctx.strokeStyle = ink;
  ctx.lineWidth = size * 0.06;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.arc(x, y + size * 0.02, size * 0.22, 0.18 * Math.PI, 0.82 * Math.PI);
  ctx.stroke();
  ctx.restore();
}

function drawFaceGauge(ctx, x, y, r, v, alpha) {
  const m = lerp(-1, 1, v);
  const col = v < 0.4 ? C.coral : v < 0.62 ? C.gold : C.mint;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.strokeStyle = col;
  ctx.lineWidth = 3;
  ctx.shadowColor = v < 0.4 ? C.coralGlow : v < 0.62 ? C.goldGlow : C.mintGlow;
  ctx.shadowBlur = 14;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.stroke();
  ctx.shadowBlur = 0;
  circle(ctx, x - r * 0.34, y - r * 0.18, r * 0.09, col);
  circle(ctx, x + r * 0.34, y - r * 0.18, r * 0.09, col);
  ctx.lineCap = 'round';
  ctx.beginPath();
  const my = y + r * 0.34;
  ctx.moveTo(x - r * 0.4, my - r * 0.12 * m);
  ctx.quadraticCurveTo(x, my + r * 0.36 * m, x + r * 0.4, my - r * 0.12 * m);
  ctx.stroke();
  ctx.restore();
}

function drawSlider(ctx, cy, v, alpha) {
  const x0 = -118;
  const x1 = 118;
  const tx = lerp(x0, x1, v);
  ctx.save();
  ctx.globalAlpha *= alpha;
  rr(ctx, x0, cy - 4, x1 - x0, 8, 4);
  ctx.fillStyle = 'rgba(255,255,255,0.12)';
  ctx.fill();
  const g = ctx.createLinearGradient(x0, 0, x1, 0);
  g.addColorStop(0, C.coral);
  g.addColorStop(0.5, C.gold);
  g.addColorStop(1, C.mint);
  rr(ctx, x0, cy - 4, Math.max(8, tx - x0), 8, 4);
  ctx.fillStyle = g;
  ctx.fill();
  ctx.shadowColor = v < 0.4 ? C.coralGlow : v < 0.62 ? C.goldGlow : C.mintGlow;
  ctx.shadowBlur = 16;
  circle(ctx, tx, cy, 14, '#F7F5EF');
  ctx.restore();
  const lo = 0.55 + 0.45 * clamp((0.2 - v) / 0.15);
  const hi = 0.55 + 0.45 * clamp((v - 0.8) / 0.15);
  glowText(ctx, '非常差', x0, cy + 40, { font: FONT.zh(18), color: C.coral, align: 'left', baseline: 'middle', alpha: alpha * lo });
  glowText(ctx, '非常好', x1, cy + 40, { font: FONT.zh(18), color: C.mint, align: 'right', baseline: 'middle', alpha: alpha * hi });
  glowText(ctx, 'VERY BAD', x0, cy + 64, { font: FONT.mono(11), color: 'rgba(214,220,234,0.45)', align: 'left', letterSpacing: 2, baseline: 'middle', alpha });
  glowText(ctx, 'VERY GOOD', x1, cy + 64, { font: FONT.mono(11), color: 'rgba(214,220,234,0.45)', align: 'right', letterSpacing: 2, baseline: 'middle', alpha });
}

function drawBigPhone(ctx, t) {
  const tin = T.c2a.t0 + 0.35;
  const k = ease.outCubic(clamp((t - tin) / 0.45));
  const out = ease.inCubic(clamp((t - T.c2f.t0) / 0.35));
  if (k <= 0 || out >= 1) return;
  const a = k * (1 - out);
  const { w, h } = PH;
  let shake = 0;
  let buzz = 1;
  MOMENTS.slice(0, 3).forEach((m) => {
    const d = t - m.t();
    if (d >= 0 && d < 0.32) shake += 0.035 * Math.sin(d * 70) * (1 - d / 0.32);
    if (d >= 0 && d < 0.5) buzz = Math.min(buzz, d / 0.5);
  });
  ctx.save();
  ctx.globalAlpha *= a;
  ctx.translate(PH.x, PH.y + (1 - k) * 60 + out * 40);
  ctx.rotate(shake);

  if (buzz < 1) {
    ctx.save();
    ctx.globalAlpha *= (1 - buzz) * 0.6;
    ctx.strokeStyle = C.mint;
    ctx.lineWidth = 2;
    const g = 8 + 22 * ease.outCubic(buzz);
    rr(ctx, -w / 2 - g, -h / 2 - g, w + 2 * g, h + 2 * g, 46 + g);
    ctx.stroke();
    ctx.restore();
  }
  rr(ctx, -w / 2, -h / 2, w, h, 46);
  ctx.fillStyle = 'rgba(9,14,26,0.97)';
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = 'rgba(214,220,234,0.42)';
  ctx.stroke();
  rr(ctx, -w / 2 + 12, -h / 2 + 12, w - 24, h - 24, 36);
  const sg = ctx.createLinearGradient(0, -h / 2, 0, h / 2);
  sg.addColorStop(0, '#15233D');
  sg.addColorStop(1, '#0B1322');
  ctx.fillStyle = sg;
  ctx.fill();
  rr(ctx, -42, -h / 2 + 22, 84, 20, 10);
  ctx.fillStyle = '#05080F';
  ctx.fill();

  let idx = -1;
  MOMENTS.forEach((m, i) => {
    if (t >= m.t()) idx = i;
  });
  const clock = idx >= 0 ? MOMENTS[idx].clock : '09:11';
  glowText(ctx, clock, -w / 2 + 40, -h / 2 + 33, { font: FONT.mono(14, 'SemiBold'), color: 'rgba(240,240,245,0.85)', align: 'left', baseline: 'middle' });
  rr(ctx, w / 2 - 66, -h / 2 + 27, 26, 12, 3);
  ctx.strokeStyle = 'rgba(240,240,245,0.6)';
  ctx.lineWidth = 1.4;
  ctx.stroke();
  rr(ctx, w / 2 - 64, -h / 2 + 29, 17, 8, 2);
  ctx.fillStyle = 'rgba(240,240,245,0.75)';
  ctx.fill();

  // Splash: the app's name (c2a).
  const sA = env(t, tin + 0.1, T.c2b.t0 + 0.15, 0.3, 0.2);
  drawAppIcon(ctx, 0, -40, 104, sA);
  glowText(ctx, 'TRACK YOUR', 0, 58, { font: FONT.mono(18, 'SemiBold'), color: '#EAF7F2', letterSpacing: 5, alpha: sA, baseline: 'middle' });
  glowText(ctx, 'HAPPINESS', 0, 86, { font: FONT.mono(18, 'SemiBold'), color: C.mint, glow: C.mintGlow, blur: 10, letterSpacing: 5, alpha: sA, baseline: 'middle' });

  // Lock screen + notification banner (c2b).
  const lA = env(t, T.c2b.t0 + 0.05, T.c2c.t0 + 0.3, 0.2, 0.25);
  if (lA > 0) {
    glowText(ctx, clock, 0, -160, { font: FONT.mono(64), color: 'rgba(244,244,248,0.92)', alpha: lA, baseline: 'middle' });
    glowText(ctx, '随机时刻 · RANDOM MOMENT', 0, -112, {
      font: FONT.mono(12),
      color: 'rgba(214,220,234,0.5)',
      letterSpacing: 2,
      alpha: lA,
      baseline: 'middle',
    });
    if (idx >= 0) {
      const d = t - MOMENTS[Math.min(idx, 2)].t();
      const drop = ease.outBack(clamp(d / 0.28));
      const bA = lA * clamp(d / 0.12);
      const by = -40 - (1 - drop) * 28;
      ctx.save();
      ctx.globalAlpha *= bA;
      rr(ctx, -w / 2 + 24, by, w - 48, 96, 22);
      ctx.fillStyle = 'rgba(236,240,248,0.1)';
      ctx.fill();
      ctx.lineWidth = 1.4;
      ctx.strokeStyle = 'rgba(111,227,193,0.45)';
      ctx.stroke();
      ctx.restore();
      drawAppIcon(ctx, -w / 2 + 52, by + 30, 32, bA);
      glowText(ctx, 'TRACK YOUR HAPPINESS', -w / 2 + 78, by + 30, {
        font: FONT.mono(10),
        color: 'rgba(214,220,234,0.6)',
        align: 'left',
        letterSpacing: 1,
        alpha: bA,
        baseline: 'middle',
      });
      glowText(ctx, '现在', w / 2 - 40, by + 30, { font: FONT.zh(13), color: 'rgba(214,220,234,0.55)', align: 'right', alpha: bA, baseline: 'middle' });
      glowText(ctx, '你现在感觉怎么样？', -w / 2 + 40, by + 68, { font: FONT.zh(22, 'Medium'), color: '#F3F1EC', align: 'left', alpha: bA, baseline: 'middle' });
    }
  }

  // The question itself (c2c → c2e).
  const qA = clamp((t - (T.c2c.t0 + 0.15)) / 0.3);
  if (qA > 0) {
    const rise = (1 - ease.outCubic(qA)) * 14;
    const nowA = ease.outBack(clamp((t - (T.c2d.t0 + 0.7)) / 0.3));
    if (nowA > 0) {
      ctx.save();
      ctx.translate(0, -186);
      ctx.scale(nowA, nowA);
      rr(ctx, -96, -18, 192, 36, 18);
      ctx.fillStyle = 'rgba(111,227,193,0.14)';
      ctx.fill();
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = 'rgba(111,227,193,0.75)';
      ctx.shadowColor = C.mintGlow;
      ctx.shadowBlur = 12;
      ctx.stroke();
      ctx.restore();
      glowDot(ctx, -70 * nowA, -186, 4.5 * nowA, C.mint, C.mintGlow, clamp(nowA));
      glowText(ctx, '此时此刻 · NOW', 10 * nowA, -185, { font: FONT.zh(17, 'Medium'), color: C.mint, alpha: clamp(nowA), baseline: 'middle' });
    }
    glowText(ctx, '你现在感觉怎么样？', 0, -118 + rise, { font: FONT.zh(28, 'Medium'), color: '#F3F1EC', alpha: qA, baseline: 'middle' });
    glowText(ctx, 'HOW DO YOU FEEL RIGHT NOW?', 0, -78 + rise, {
      font: FONT.mono(12),
      color: 'rgba(214,220,234,0.55)',
      letterSpacing: 2,
      alpha: qA,
      baseline: 'middle',
    });
    const v = sliderAt(t);
    drawFaceGauge(ctx, 0, 6 + rise, 36, v, qA);
    drawSlider(ctx, 98 + rise, v, qA);
    glowText(ctx, 'TRACK YOUR HAPPINESS', 0, h / 2 - 44, {
      font: FONT.mono(11),
      color: 'rgba(111,227,193,0.5)',
      letterSpacing: 3,
      alpha: qA,
      baseline: 'middle',
    });
  }
  ctx.restore();
}

/* ---------- 33,391 people with phones ---------- */

const CROWD2_X0 = 220;
const CROWD2_X1 = 1700;
const COUNT2_T0 = () => T.c2f.t0 + 0.25;
const COUNT2_DUR = 1.9;

const CROWD2 = (() => {
  const rng = mulberry32(33391);
  const ROWS = 5;
  const out = [];
  for (let r = 0; r < ROWS; r++) {
    const k = r / (ROWS - 1);
    const s = lerp(0.42, 0.6, k);
    const half = lerp(620, 740, k);
    const y = lerp(626, 842, k);
    const n = Math.round((2 * half) / (66 * s));
    const step = (2 * half) / n;
    for (let i = 0; i < n; i++) {
      const up = rng() < 0.55;
      const f = makeFolk(rng);
      f.mood = clamp(0.3 + gauss(rng) * 0.45, -0.9, 1);
      f.armR = up ? ARM_LOOK : -0.5;
      f.look = up ? 1 : 0;
      f.lookY = up ? -0.2 : 1;
      f.prop = { kind: 'phone', side: 1, lit: 0 };
      out.push({
        f,
        x: 960 - half + (i + 0.5) * step + (rng() - 0.5) * step * 0.5,
        y: y + (rng() - 0.5) * 6,
        s: s * (0.94 + rng() * 0.12),
        ph: rng() * Math.PI * 2,
        pings: [0, 1].map(() => T.c2f.t0 + 0.45 + rng() * 2.3),
      });
    }
  }
  const order = out.map((_, i) => i).sort(() => rng() - 0.5);
  order.forEach((idx, rank) => {
    const q = (rank + 1) / out.length;
    out[idx].tIn = COUNT2_T0() + COUNT2_DUR * 0.7 * (1 - Math.cbrt(1 - q)) - 0.05;
  });
  for (const p of out) p.tOut = T.c2g.t0 + 0.08 + clamp((p.x - CROWD2_X0) / (CROWD2_X1 - CROWD2_X0)) * 0.55;
  return out;
})();
const BY_X2 = [...CROWD2].sort((a, b) => a.x - b.x);

function phoneScreenOf(p) {
  const pc = phoneCenter(1, p.f.armR);
  return { x: p.x + pc.x * p.s, y: p.y + pc.y * p.s };
}

function drawCrowd2(ctx, t) {
  if (t < T.c2f.t0 || t > T.c2g.t0 + 1.2) return;
  for (const p of CROWD2) {
    if (t < p.tIn) continue;
    const e = clamp((t - p.tIn) / 0.22);
    const gone = clamp((t - p.tOut) / 0.25);
    if (gone >= 1) continue;
    const s = p.s * ease.outBack(e) * (1 - 0.35 * gone);
    const y = p.y - (1 - ease.outCubic(e)) * 10 + Math.sin(t * 2.1 + p.ph) * 0.6;
    const a = clamp(e * 3) * (1 - gone);
    drawFolkSprite(ctx, p.f, p.x, y, s, a);
    let lit = 0;
    for (const tp of p.pings) lit = Math.max(lit, env(t, tp, tp + 0.5, 0.05, 0.3));
    if (lit > 0 && e >= 1) {
      const sc = phoneScreenOf({ ...p, y, s });
      ctx.save();
      ctx.globalAlpha *= lit * a;
      ctx.shadowColor = C.mintGlow;
      ctx.shadowBlur = 10;
      ctx.fillStyle = '#A8F5DD';
      ctx.fillRect(sc.x - 3.6 * s, sc.y - 6.6 * s, 7.2 * s, 13.2 * s);
      ctx.restore();
    }
  }
}

/** Each ping sends a spark up into the counter. */
function drawPingSparks(ctx, t) {
  if (t < T.c2f.t0 || t > T.c2g.t0 + 0.6) return;
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.fillStyle = 'rgb(160,245,215)';
  for (const p of CROWD2) {
    if (t < p.tIn + 0.22) continue;
    for (const tp of p.pings) {
      const d = (t - tp) / 0.65;
      if (d < 0 || d > 1) continue;
      const sc = phoneScreenOf(p);
      const k = ease.inOutCubic(d);
      const x = lerp(sc.x, 960 + (sc.x - 960) * 0.18, k);
      const y = lerp(sc.y, 340, k) - Math.sin(Math.PI * k) * 40;
      ctx.globalAlpha = 0.85 * Math.sin(Math.PI * Math.min(1, d * 1.25)) * (1 - clamp((t - T.c2g.t0) / 0.3));
      ctx.fillRect(x - 1.6, y - 1.6, 3.2, 3.2);
    }
  }
  ctx.restore();
}

function drawCounter2(ctx, t) {
  const t0 = COUNT2_T0();
  const a = clamp((t - t0) / 0.25) * (1 - clamp((t - (T.c2g.t0 - 0.05)) / 0.3));
  if (a <= 0) return;
  const p = ease.outCubic(clamp((t - t0) / COUNT2_DUR));
  const cy = 318;
  drawFixedDigits(ctx, fmtInt(1725994 * p), 960, cy, {
    font: FONT.zh(140, 'SemiBold'),
    color: C.mint,
    glow: C.mintGlow,
    blur: 34,
    alpha: a,
  });
  glowText(ctx, 'REPORTS · 次打分', 960, cy + 106, {
    font: FONT.mono(16),
    color: 'rgba(170,240,215,0.7)',
    alpha: a,
    letterSpacing: 6,
    baseline: 'middle',
  });
  glowText(ctx, `${fmtInt(33391 * p)} 人 · EMPLOYED U.S. ADULTS`, 960, cy + 148, {
    font: FONT.mono(20),
    color: 'rgba(236,230,214,0.82)',
    alpha: a * clamp((t - t0 - 0.2) / 0.3),
    letterSpacing: 1,
    baseline: 'middle',
  });
}

/* ---------- chart: past $75K it keeps rising ---------- */

const NOW_PTS = curvePoints(nowCurve);
const LIFE21_PTS = curvePoints(life21Curve);
const GHOST_PTS = curvePoints(emoWide);
const CHART2_T0 = () => T.c2g.t0 + 0.05;
const NOW_T0 = () => T.c2g.t0 + 0.6;
const NOW_DUR = 1.5;
const CEIL_U0 = W75 - 0.1;

/** Time at which the 2021 line's head reaches u (inverts the stroke easing). */
function nowTimeAt(u) {
  let lo = 0;
  let hi = 1;
  for (let i = 0; i < 40; i++) {
    const mid = (lo + hi) / 2;
    if (ease.inOutCubic(mid) < u) lo = mid;
    else hi = mid;
  }
  return NOW_T0() + lo * NOW_DUR;
}
const CROSS_T = nowTimeAt(U_CROSS);

const N2 = 1300;
const PARTS2 = (() => {
  const r = mulberry32(118);
  const out = [];
  for (let i = 0; i < N2; i++) {
    const u = 0.004 + r() * 0.992;
    const v = nowCurve(u) + gauss(r) * 0.05;
    const j = clamp(Math.round(u * (BY_X2.length - 1) + (r() - 0.5) * 20), 0, BY_X2.length - 1);
    const src = BY_X2[j];
    out.push({
      cx: src.x + (r() - 0.5) * 20 * src.s,
      cy: src.y - (12 + r() * 70) * src.s,
      td: src.tOut + r() * 0.08,
      tx: X(u),
      ty: Y(clamp(v, -0.02, 1.02)),
      size: 1.2 + r() * 1.5,
      a: 0.3 + r() * 0.45,
      ph: r() * Math.PI * 2,
      fd: 0.6 + r() * 0.3,
      arc: (r() - 0.5) * 90,
    });
  }
  return out;
})();

function drawParticles2(ctx, t, dim) {
  if (t < T.c2g.t0 || dim <= 0) return;
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.fillStyle = 'rgb(150,240,210)';
  const base = ctx.globalAlpha * dim;
  for (const p of PARTS2) {
    if (t < p.td) continue;
    const k = ease.inOutCubic(clamp((t - p.td) / p.fd));
    let x = lerp(p.cx, p.tx, k);
    let y = lerp(p.cy, p.ty, k) + Math.sin(Math.PI * k) * p.arc * 0.3;
    if (k >= 1) {
      x += Math.sin(t * 1.1 + p.ph) * 0.7;
      y += Math.cos(t * 1.3 + p.ph) * 0.7;
    }
    ctx.globalAlpha = base * p.a * (0.75 + 0.25 * Math.sin(t * 2.2 + p.ph * 3)) * clamp((t - p.td) / 0.15) * (k >= 1 ? 0.8 : 1);
    ctx.fillRect(x - p.size / 2, y - p.size / 2, p.size, p.size);
  }
  ctx.restore();
}

function strokeDashed(ctx, pts, progress, color, width, alpha) {
  if (progress <= 0 || alpha <= 0) return;
  const n = Math.max(1, Math.round((pts.length - 1) * clamp(progress)));
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.setLineDash([9, 8]);
  ctx.lineCap = 'round';
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i <= n; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.stroke();
  ctx.restore();
}

const SHARDS = (() => {
  const r = mulberry32(75000);
  return Array.from({ length: 14 }, () => ({
    ang: -Math.PI / 2 + (r() - 0.5) * 2.4,
    v: 90 + r() * 160,
    len: 5 + r() * 9,
    rot: (r() - 0.5) * 9,
  }));
})();

/** The 2010 plateau, drawn as a ceiling slab that cracks where the 2021 line passes through. */
function drawCeiling(ctx, t) {
  const a = clamp((t - (CHART2_T0() + 0.35)) / 0.35);
  if (a <= 0) return;
  const yc = Y(CEIL_V);
  const xc = X(U_CROSS);
  const crack = clamp((t - CROSS_T) / 0.35);
  const gap = 16 * ease.outCubic(crack);
  // After the crack the slab dims, then clears out for the slope comparison.
  const fade = lerp(1, 0.35, ease.inOutCubic(clamp((t - CROSS_T - 0.25) / 0.5))) * (1 - clamp((t - T.c2h.t0) / 0.3));
  ctx.save();
  ctx.globalAlpha *= a * fade;
  ctx.strokeStyle = 'rgba(255,138,122,0.75)';
  ctx.lineWidth = 5;
  ctx.lineCap = 'round';
  ctx.shadowColor = C.coralGlow;
  ctx.shadowBlur = 14;
  ctx.beginPath();
  ctx.moveTo(X(CEIL_U0), yc);
  ctx.lineTo(xc - gap, yc + 2 * crack);
  ctx.moveTo(xc + gap, yc + 5 * crack);
  ctx.lineTo(X(1), yc + 10 * crack);
  ctx.stroke();
  ctx.restore();
  glowText(ctx, '2010 的天花板', X(0.9), yc - 22, {
    font: FONT.zh(21, 'Medium'),
    color: C.coral,
    glow: C.coralGlow,
    blur: 10,
    alpha: a * fade,
    baseline: 'middle',
  });
  const d = t - CROSS_T;
  if (d > 0 && d < 0.8) {
    ctx.save();
    ctx.strokeStyle = C.coral;
    ctx.lineWidth = 2.2;
    ctx.lineCap = 'round';
    ctx.shadowColor = C.coralGlow;
    ctx.shadowBlur = 8;
    ctx.globalAlpha *= (1 - d / 0.8) * a;
    for (const s of SHARDS) {
      const x = xc + Math.cos(s.ang) * s.v * d;
      const y = yc + Math.sin(s.ang) * s.v * d + 260 * d * d;
      const ang = s.rot * d;
      ctx.beginPath();
      ctx.moveTo(x - Math.cos(ang) * s.len, y - Math.sin(ang) * s.len);
      ctx.lineTo(x + Math.cos(ang) * s.len, y + Math.sin(ang) * s.len);
      ctx.stroke();
    }
    ctx.restore();
    const fl = clamp(d / 0.5);
    ctx.save();
    ctx.globalAlpha *= (1 - fl) * 0.8 * a;
    ctx.strokeStyle = '#FFE3D2';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(xc, yc, lerp(6, 56, ease.outCubic(fl)), 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }
}

function drawMarker(ctx, u, label, color, glow, alpha, yTop) {
  if (alpha <= 0) return;
  const x = X(u);
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.setLineDash([6, 7]);
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.6;
  ctx.shadowColor = glow;
  ctx.shadowBlur = 8;
  ctx.beginPath();
  ctx.moveTo(x, PLOT.B);
  ctx.lineTo(x, yTop);
  ctx.stroke();
  ctx.restore();
  glowText(ctx, label, x, PLOT.B + 74, { font: FONT.mono(24, 'SemiBold'), color, glow, blur: 12, alpha });
}

/** c2h: two equal steps in log income, one below $80K and one above, rise by the same amount. */
function drawSlopes(ctx, t) {
  const t0 = T.c2h.t0;
  const a = clamp((t - t0) / 0.2) * (1 - clamp((t - (T.c2i.t0 + 0.2)) / 0.35));
  if (a <= 0) return;
  const tris = [
    [uW(20000), uW(40000)],
    [uW(110000), uW(220000)],
  ];
  tris.forEach(([u1, u2], i) => {
    const k = ease.outCubic(clamp((t - t0 - 0.2 - i * 0.45) / 0.35));
    if (k <= 0) return;
    const ax = X(u1);
    const ay = Y(nowCurve(u1));
    const bx = X(u2);
    const cy = Y(nowCurve(u2));
    const hx = lerp(ax, bx, k);
    const hy = lerp(ay, cy, k);
    ctx.save();
    ctx.globalAlpha *= a;
    ctx.beginPath();
    ctx.moveTo(ax, ay);
    ctx.lineTo(hx, ay);
    ctx.lineTo(hx, hy);
    ctx.closePath();
    ctx.fillStyle = 'rgba(111,227,193,0.14)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(111,227,193,0.85)';
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    ctx.moveTo(ax, ay);
    ctx.lineTo(hx, ay);
    ctx.lineTo(hx, hy);
    ctx.stroke();
    ctx.restore();
    glowText(ctx, '×2 收入', (ax + bx) / 2, ay + 24, { font: FONT.mono(14), color: 'rgba(214,220,234,0.7)', alpha: a * k, baseline: 'middle' });
    glowText(ctx, '↑', bx + 18, (ay + cy) / 2, { font: FONT.mono(22, 'SemiBold'), color: C.mint, glow: C.mintGlow, blur: 8, alpha: a * k, baseline: 'middle' });
  });
  const eq = ease.outBack(clamp((t - t0 - 1.15) / 0.3));
  if (eq > 0) {
    const x = (X(uW(40000)) + X(uW(110000))) / 2;
    const y = (Y(nowCurve(uW(30000))) + Y(nowCurve(uW(150000)))) / 2 + 70;
    glowText(ctx, '=', x, y, { font: FONT.mono(54 * eq, 'SemiBold'), color: C.mint, glow: C.mintGlow, blur: 14, alpha: a, baseline: 'middle' });
    glowText(ctx, '一样陡 · SAME SLOPE', x, y + 44, {
      font: FONT.zh(20, 'Medium'),
      color: C.mint,
      alpha: a * clamp(eq),
      baseline: 'middle',
    });
  }
}

function drawSplit80(ctx, t) {
  const a = clamp((t - (T.c2h.t0 + 0.05)) / 0.3) * (1 - clamp((t - (T.c2i.t0 + 0.2)) / 0.35));
  if (a <= 0) return;
  const x = X(W80);
  ctx.save();
  ctx.globalAlpha *= a;
  ctx.setLineDash([6, 7]);
  ctx.strokeStyle = 'rgba(111,227,193,0.7)';
  ctx.lineWidth = 1.6;
  ctx.beginPath();
  ctx.moveTo(x, PLOT.B);
  ctx.lineTo(x, PLOT.T - 6);
  ctx.stroke();
  ctx.restore();
  glowText(ctx, '低于 $80K', x - 16, PLOT.T + 8, { font: FONT.zh(19), color: 'rgba(236,236,240,0.75)', align: 'right', alpha: a, baseline: 'middle' });
  glowText(ctx, '高于 $80K', x + 16, PLOT.T + 8, { font: FONT.zh(19), color: 'rgba(236,236,240,0.75)', align: 'left', alpha: a, baseline: 'middle' });
  glowText(ctx, '$80K', x, PLOT.B + 74, { font: FONT.mono(24, 'SemiBold'), color: C.mint, glow: C.mintGlow, blur: 12, alpha: a });
}

function drawCurves2(ctx, t) {
  // 2010, as a ghost
  const gA = clamp((t - (CHART2_T0() + 0.25)) / 0.3);
  strokeDashed(ctx, GHOST_PTS, ease.inOutCubic(clamp((t - (CHART2_T0() + 0.25)) / 0.6)), C.cyan, 2.2, gA * 0.55);
  glowText(ctx, '2010 · 昨天开心吗', PLOT.R + 26, Y(CEIL_V) + 4, {
    font: FONT.zh(19),
    color: 'rgba(98,212,255,0.7)',
    align: 'left',
    baseline: 'middle',
    alpha: gA * clamp((t - (CHART2_T0() + 0.7)) / 0.3),
  });
  drawCeiling(ctx, t);

  // 2021: how people feel right now
  const p = ease.inOutCubic(clamp((t - NOW_T0()) / NOW_DUR));
  const head = strokeGlowPath(ctx, NOW_PTS, p, { color: C.mint, glow: C.mintGlow, width: 3.4 });
  if (head && p < 1) glowDot(ctx, head[0], head[1], 5.5, '#EFFFF9', C.mintGlow);
  glowText(ctx, '2021 · 快乐（此刻感受）', PLOT.R + 26, Y(nowCurve(1)), {
    font: FONT.zh(21, 'Medium'),
    color: C.mint,
    glow: C.mintGlow,
    blur: 10,
    align: 'left',
    baseline: 'middle',
    alpha: clamp((t - (NOW_T0() + NOW_DUR - 0.15)) / 0.3),
  });

  // 2021: life satisfaction rises alongside (c2i)
  const lp = ease.inOutCubic(clamp((t - T.c2i.t0) / 0.7));
  const lh = strokeGlowPath(ctx, LIFE21_PTS, lp, { color: C.gold, glow: C.goldGlow, width: 3.2 });
  if (lh && lp < 1) glowDot(ctx, lh[0], lh[1], 5, '#FFF1D6', C.goldGlow);
  glowText(ctx, '2021 · 满意（人生评分）', PLOT.R + 26, Y(life21Curve(1)), {
    font: FONT.zh(21, 'Medium'),
    color: C.gold,
    glow: C.goldGlow,
    blur: 10,
    align: 'left',
    baseline: 'middle',
    alpha: clamp((t - (T.c2i.t0 + 0.55)) / 0.3),
  });

  const m75 = clamp((t - (CHART2_T0() + 0.3)) / 0.3) * (1 - clamp((t - T.c2h.t0) / 0.25));
  drawMarker(ctx, W75, '$75K', C.gold, C.goldGlow, m75, Y(CEIL_V) - 40);
  drawSplit80(ctx, t);
  drawSlopes(ctx, t);
}

/* ---------- c2i: the same three people as in 2010, now the richest one is happiest ---------- */

const ROW_T0 = () => T.c2i.t0 + 0.75;
const R_FEET = 792;
const R_S = 1.4;
const R_PADDLE_Y = R_FEET - 117 * R_S;
const R_FACE_Y = R_FEET - 79 * R_S;
// Same three figures (same seeds) as the 2010 verdict row in ch1.
const ROW = [
  { x: 700, label: '$25K', meter: 0.42, mood: 0.05, f: makeFolk(mulberry32(25), { hairStyle: 'curly', top: '#C9A04B', skin: '#AC7149', hair: '#2B2422' }) },
  { x: 1010, label: '$75K', meter: 0.7, mood: 0.72, f: makeFolk(mulberry32(75), { hairStyle: 'bun', top: '#B65D72', skin: '#F6D9BC', hair: '#6B4A30' }) },
  { x: 1320, label: '$150K', meter: 0.9, mood: 1, f: makeFolk(mulberry32(150), { hairStyle: 'short', top: '#6B7E9E', skin: '#E4B286', hair: '#3F2C22' }) },
];
const rowA = (t) => clamp((t - ROW_T0()) / 0.2);

function drawRow(ctx, t) {
  const t0 = ROW_T0();
  const a = rowA(t);
  if (a <= 0) return;
  ctx.save();
  ctx.globalAlpha *= a;
  ctx.translate(960, 700);
  ctx.scale(1, 0.3);
  const back = ctx.createRadialGradient(0, 0, 0, 0, 0, 760);
  back.addColorStop(0, 'rgba(5,8,15,0.6)');
  back.addColorStop(1, 'rgba(5,8,15,0)');
  ctx.fillStyle = back;
  ctx.fillRect(-760, -760, 1520, 1520);
  ctx.restore();

  ctx.save();
  ctx.globalAlpha *= a;
  glowText(ctx, '满意', 600, R_PADDLE_Y, { font: FONT.zh(26, 'Medium'), color: C.gold, glow: C.goldGlow, blur: 10, align: 'right', baseline: 'middle' });
  glowText(ctx, '快乐', 600, R_FACE_Y, { font: FONT.zh(26, 'Medium'), color: C.mint, glow: C.mintGlow, blur: 10, align: 'right', baseline: 'middle' });
  ROW.forEach((p, i) => {
    const k = clamp((t - t0 - i * 0.1) / 0.35);
    if (k <= 0) return;
    const pin = ease.outBack(k);
    const raise = ease.outBack(clamp((t - t0 - 0.3 - i * 0.08) / 0.28));
    const pk = ease.outBack(clamp((t - t0 - 0.38 - i * 0.08) / 0.3));
    const fill = p.meter * ease.inOutCubic(clamp((t - t0 - 0.5 - i * 0.12) / 0.5));
    const mood = lerp(0.2, p.mood, ease.outCubic(clamp((t - t0 - 0.55 - i * 0.12) / 0.3)));
    drawFolk(ctx, p.f, {
      x: p.x,
      y: R_FEET + (1 - pin) * 30,
      s: R_S,
      t,
      alpha: clamp(k * 3),
      mood,
      armR: lerp(ARM_DOWN, ARM_UP, raise),
      prop: pk > 0 ? { kind: 'paddle', side: 1, meter: fill, k: pk } : null,
    });
    glowText(ctx, p.label, p.x, R_FEET + 34, {
      font: FONT.mono(21, 'SemiBold'),
      color: 'rgba(236,230,214,0.8)',
      alpha: clamp(k * 3),
      baseline: 'middle',
    });
  });
  const marks = [(ROW[0].x + ROW[1].x) / 2 + 20, (ROW[1].x + ROW[2].x) / 2 + 20];
  marks.forEach((mx, i) => {
    const m = ease.outCubic(clamp((t - t0 - 1.0 - i * 0.3) / 0.25));
    if (m <= 0) return;
    glowText(ctx, '↑', mx, R_PADDLE_Y + (1 - m) * 8, { font: FONT.mono(34, 'SemiBold'), color: C.gold, glow: C.goldGlow, blur: 12, alpha: m, baseline: 'middle' });
    if (i === 0) {
      glowText(ctx, '↑', mx, R_FACE_Y + (1 - m) * 8, { font: FONT.mono(34, 'SemiBold'), color: C.mint, glow: C.mintGlow, blur: 12, alpha: m, baseline: 'middle' });
      return;
    }
    // 2010 said "=" here; 2021 flips it to "↑".
    const flip = ease.inOutCubic(clamp((t - t0 - 1.75) / 0.3));
    ctx.save();
    ctx.translate(mx, R_FACE_Y);
    ctx.scale(1, Math.abs(Math.cos(flip * Math.PI)) || 0.001);
    glowText(ctx, flip < 0.5 ? '=' : '↑', 0, 0, {
      font: FONT.mono(34, 'SemiBold'),
      color: flip < 0.5 ? C.cyan : C.mint,
      glow: flip < 0.5 ? C.cyanGlow : C.mintGlow,
      blur: 12,
      alpha: m,
      baseline: 'middle',
    });
    ctx.restore();
    if (flip > 0 && flip < 1) {
      ctx.save();
      ctx.globalAlpha *= (1 - flip) * 0.7;
      ctx.strokeStyle = C.mint;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(mx, R_FACE_Y, lerp(10, 48, flip), 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
  });
  ctx.restore();
}

/* ---------- scene ---------- */

export function drawCh2(ctx, t) {
  const fadeOut = 1 - clamp((t - (T.c2i.t1 - 0.2)) / 0.4);
  if (fadeOut <= 0 || t < T.c2a.t0 - 0.2) return;
  ctx.save();
  ctx.globalAlpha *= fadeOut;
  const head = clamp((t - T.c2a.t0) / 0.4);
  drawChapterLabel(ctx, '研究 02 · 没有天花板', 'NO CEILING', head);
  drawPill(ctx, 'Killingsworth · 2021', 'PNAS · TRACK YOUR HAPPINESS', 960, 152, clamp((t - T.c2a.t0 - 0.2) / 0.4));

  drawStage(ctx, FLOOR2, env(t, T.c2a.t0 + 0.1, T.c2f.t0 + 0.3, 0.35, 0.35) * 0.8);
  drawDayStrip(ctx, t);
  drawIntro(ctx, t);
  drawYesterdayBubble(ctx, t);
  drawGhostYesNo(ctx, t);
  drawParticipant(ctx, t);
  drawBigPhone(ctx, t);

  const chartDim = lerp(1, 0.22, ease.inOutCubic(clamp((t - (ROW_T0() - 0.1)) / 0.45)));
  const c0 = CHART2_T0();
  if (t >= c0) {
    ctx.save();
    ctx.globalAlpha *= clamp((t - c0) / 0.3) * chartDim;
    drawLogAxes(ctx, t, c0, AXIS_WIDE);
    ctx.restore();
  }
  drawCrowd2(ctx, t);
  drawPingSparks(ctx, t);
  drawParticles2(ctx, t, chartDim);
  if (t >= c0) {
    ctx.save();
    ctx.globalAlpha *= chartDim;
    drawCurves2(ctx, t);
    ctx.restore();
  }
  drawCounter2(ctx, t);
  drawRow(ctx, t);
  ctx.restore();
}
