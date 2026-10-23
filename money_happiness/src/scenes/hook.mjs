// 片头：大标题 → 两位学者 → "$75,000" 砸进画面 → 裂开 → 一分为二。
import { createCanvas } from '@napi-rs/canvas';
import { clamp, lerp, ease, smin } from '../engine/util.mjs';
import { FONT } from '../engine/fonts.mjs';
import { C, glowText, drawStage, strokeGlowPath } from '../engine/draw.mjs';
import { drawPerson, PEOPLE } from '../engine/people.mjs';
import { cue } from '../cues.mjs';

const TITLE = '钱能买到快乐吗？';
const NX = 960;
const NY = 430;
const NUM_W = 1200;
const NUM_H = 360;
const FLOOR = 728;
const NUM_TEXT = '$75,000';
const NUM_FONT = FONT.zh(200, 'SemiBold');

let numImgs = null;
let CRACK = null; // jagged split line, placed right after the comma: "$75," | "000"
let HALF_X = null; // screen x of each fragment's glyph centre once fully split

// "到底谁对？": the 2010 and 2021 authors stand under the two fragments.
const FO_FLOOR = 752;
const FO_S = 0.56;
const SPLIT_DX = 70;

/** Wrap crisp glyphs in their own glow. Applying the glow after cutting keeps each fragment's halo intact. */
function withGlow(src) {
  const c = createCanvas(NUM_W, NUM_H);
  const g = c.getContext('2d');
  g.shadowColor = C.goldGlow;
  g.shadowBlur = 46;
  g.drawImage(src, 0, 0);
  g.drawImage(src, 0, 0);
  g.shadowBlur = 0;
  g.drawImage(src, 0, 0);
  return c;
}

function crispNumber(side) {
  const c = createCanvas(NUM_W, NUM_H);
  const g = c.getContext('2d');
  if (side !== undefined) {
    const edge = side === 0 ? 0 : NUM_W;
    g.beginPath();
    g.moveTo(edge, 0);
    for (const [x, y] of CRACK) g.lineTo(x, y);
    g.lineTo(edge, NUM_H);
    g.closePath();
    g.clip();
  }
  g.font = NUM_FONT;
  g.fillStyle = C.gold;
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  g.fillText(NUM_TEXT, NUM_W / 2, NUM_H / 2);
  return c;
}

/** Full number + its two fragments (left "$75," / right "000"), each with its own glow. */
function numberImages() {
  if (numImgs) return numImgs;
  const g = createCanvas(8, 8).getContext('2d');
  g.font = NUM_FONT;
  const total = g.measureText(NUM_TEXT).width;
  const cut = NUM_W / 2 - total / 2 + g.measureText('$75,').width + 4;
  CRACK = [
    [cut - 4, 0],
    [cut + 12, 70],
    [cut - 6, 130],
    [cut + 14, 185],
    [cut - 2, 242],
    [cut + 15, 300],
    [cut + 4, 360],
  ];
  const left = NUM_W / 2 - total / 2;
  const right = NUM_W / 2 + total / 2;
  HALF_X = [NX - NUM_W / 2 + (left + cut) / 2 - SPLIT_DX, NX - NUM_W / 2 + (cut + right) / 2 + SPLIT_DX];
  numImgs = {
    full: withGlow(crispNumber()),
    halves: [withGlow(crispNumber(0)), withGlow(crispNumber(1))],
  };
  return numImgs;
}

export function hookShakes() {
  return [
    { t0: cue('h3').t0 + 0.17, amp: 7, dur: 0.35 },
    { t0: cue('h4').t0 + 0.12, amp: 4, dur: 0.25 },
  ];
}

function drawTitle(ctx, t, tMove) {
  const font = FONT.zh(108, 'SemiBold');
  const chars = [...TITLE];
  ctx.save();
  ctx.font = font;
  ctx.letterSpacing = '0px';
  const widths = chars.map((ch) => ctx.measureText(ch).width);
  const total = widths.reduce((a, b) => a + b, 0);
  const m = ease.inOutCubic(clamp((t - tMove) / 0.55));
  const s = lerp(1, 0.4, m);
  ctx.translate(960, lerp(520, 176, m));
  ctx.scale(s, s);
  let x = -total / 2;
  chars.forEach((ch, i) => {
    const p = clamp((t - (0.12 + i * 0.07)) / 0.42);
    if (p > 0) {
      const e = ease.outCubic(p);
      ctx.save();
      if (p < 1) ctx.filter = `blur(${((1 - e) * 8).toFixed(2)}px)`;
      glowText(ctx, ch, x, (1 - e) * 22, {
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
  const ca = clamp((t - 0.75) / 0.4) * (1 - clamp((t - (tMove - 0.25)) / 0.3));
  glowText(ctx, 'CAN MONEY BUY HAPPINESS?', 0, 96, {
    font: FONT.mono(19),
    color: 'rgba(235,215,170,0.62)',
    alpha: ca,
    letterSpacing: 9,
    baseline: 'middle',
  });
  ctx.restore();
}

function drawDuo(ctx, t, tIn, tOut) {
  const stageA = clamp((t - tIn) / 0.35) * (1 - clamp((t - tOut) / 0.3));
  if (stageA <= 0) return;
  drawStage(ctx, FLOOR, stageA);
  const duo = [
    { ...PEOPLE.kahneman, x: 830 },
    { ...PEOPLE.deaton, x: 1090 },
  ];
  duo.forEach((p, i) => {
    const pin = ease.outCubic(clamp((t - tIn - 0.1 - i * 0.12) / 0.45));
    const pout = ease.inCubic(clamp((t - tOut) / 0.3));
    const a = pin * (1 - pout);
    if (a <= 0) return;
    const y = FLOOR + (1 - pin) * 40 + pout * 30;
    drawPerson(ctx, { ...p, y, s: 1.02 }, t, a);
    glowText(ctx, p.zh, p.x, y + 44, {
      font: FONT.zh(26),
      color: C.white,
      alpha: a * 0.92,
      baseline: 'middle',
    });
    glowText(ctx, p.tag, p.x, y + 74, {
      font: FONT.mono(13),
      color: 'rgba(214,220,234,0.55)',
      alpha: a,
      letterSpacing: 3,
      baseline: 'middle',
    });
  });
}

function drawFaceOff(ctx, t, tIn) {
  const stageA = clamp((t - tIn) / 0.3);
  if (stageA <= 0) return;
  numberImages();
  drawStage(ctx, FO_FLOOR, stageA * 0.8);
  const pair = [
    { ...PEOPLE.kahneman, x: HALF_X[0], look: 1, tag: '2010' },
    { ...PEOPLE.killingsworth, x: HALF_X[1], look: -1, tag: '2021' },
  ];
  pair.forEach((p, i) => {
    const k = clamp((t - tIn - 0.05 - i * 0.1) / 0.38);
    if (k <= 0) return;
    const pin = ease.outBack(k);
    const a = clamp(k * 2.5);
    const y = FO_FLOOR + (1 - pin) * 36;
    drawPerson(ctx, { ...p, y, s: FO_S, mood: 0, browTilt: 1 }, t, a);
    glowText(ctx, p.zh, p.x, FO_FLOOR + 40, {
      font: FONT.zh(24),
      color: C.white,
      alpha: a * 0.92,
      baseline: 'middle',
    });
    glowText(ctx, p.tag, p.x, FO_FLOOR + 68, {
      font: FONT.mono(15, 'SemiBold'),
      color: C.gold,
      glow: C.goldGlow,
      blur: 8,
      alpha: a * 0.85,
      letterSpacing: 3,
      baseline: 'middle',
    });
  });
}

function drawMiniPlateau(ctx, t, t0, tFade) {
  const a = clamp((t - t0) / 0.3) * (1 - clamp((t - tFade) / 0.35));
  if (a <= 0) return;
  const x0 = 560;
  const x1 = 1360;
  const xb = 960;
  const yb = 740;
  const yTop = 590;
  ctx.save();
  ctx.globalAlpha *= a;
  ctx.strokeStyle = 'rgba(232,206,150,0.35)';
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.moveTo(x0, yb);
  ctx.lineTo(x1, yb);
  ctx.stroke();

  const pts = [];
  for (let i = 0; i <= 140; i++) {
    const u = i / 140;
    pts.push([lerp(x0, x1, u), lerp(yb - 12, yTop, smin(u / 0.5, 1, 0.14))]);
  }
  const head = strokeGlowPath(ctx, pts, ease.inOutCubic(clamp((t - t0) / 1.1)), {
    color: C.cyan,
    glow: C.cyanGlow,
    width: 3,
    blur: 16,
  });
  const dp = ease.outCubic(clamp((t - t0 - 0.55) / 0.3));
  if (dp > 0) {
    ctx.save();
    ctx.setLineDash([6, 7]);
    ctx.strokeStyle = C.gold;
    ctx.lineWidth = 1.6;
    ctx.shadowColor = C.goldGlow;
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.moveTo(xb, yb);
    ctx.lineTo(xb, lerp(yb, yTop - 18, dp));
    ctx.stroke();
    ctx.restore();
    glowText(ctx, '$75K', xb, yb + 32, {
      font: FONT.mono(20, 'SemiBold'),
      color: C.gold,
      glow: C.goldGlow,
      blur: 10,
      alpha: dp,
    });
  }
  if (head && t - t0 < 1.15) {
    ctx.shadowColor = C.cyanGlow;
    ctx.shadowBlur = 16;
    ctx.fillStyle = '#E8F8FF';
    ctx.beginPath();
    ctx.arc(head[0], head[1], 4.5, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

function drawCrack(ctx, progress, alpha) {
  if (progress <= 0 || alpha <= 0) return;
  numberImages();
  const pts = CRACK.map(([x, y]) => [NX - NUM_W / 2 + x, NY - NUM_H / 2 + y]);
  ctx.save();
  ctx.globalAlpha *= alpha;
  strokeGlowPath(ctx, pts, progress, { color: '#FFE3D2', glow: C.coralGlow, width: 3.2, blur: 22 });
  ctx.restore();
}

function drawNumber(ctx, t, tIn, tCrack, tSplit) {
  const tSlam = tIn + 0.15;
  if (t < tSlam) return;
  const imgs = numberImages();

  const sw = clamp((t - tSlam - 0.05) / 0.9);
  if (sw > 0 && sw < 1) {
    ctx.save();
    ctx.globalAlpha *= (1 - sw) * 0.6;
    ctx.strokeStyle = C.gold;
    ctx.lineWidth = lerp(3, 0.6, sw);
    ctx.shadowColor = C.goldGlow;
    ctx.shadowBlur = 20;
    ctx.beginPath();
    ctx.arc(NX, NY, lerp(60, 900, ease.outCubic(sw)), 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }

  drawMiniPlateau(ctx, t, tIn + 0.55, tSplit);

  const scale = lerp(1.9, 1, ease.outCubic(clamp((t - tSlam) / 0.3)));
  const appear = clamp((t - tSlam) / 0.1);
  const flicker = t > tCrack + 0.1 && t < tCrack + 0.5 ? 0.55 + 0.45 * Math.abs(Math.sin(t * 90)) : 1;
  const dim = t > tCrack + 0.45 ? 0.72 : 1;
  const sp = ease.inOutCubic(clamp((t - (tSplit + 0.1)) / 0.7));

  ctx.save();
  ctx.globalAlpha *= appear * flicker * dim;
  if (sp <= 0) {
    ctx.translate(NX, NY);
    ctx.scale(scale, scale);
    ctx.drawImage(imgs.full, -NUM_W / 2, -NUM_H / 2);
  } else {
    for (const side of [0, 1]) {
      const dir = side ? 1 : -1;
      ctx.save();
      ctx.translate(NX + dir * SPLIT_DX * sp, NY + dir * 16 * sp);
      ctx.rotate(dir * 0.04 * sp);
      ctx.globalAlpha *= lerp(1, 0.55, sp);
      ctx.drawImage(imgs.halves[side], -NUM_W / 2, -NUM_H / 2);
      ctx.restore();
    }
  }
  ctx.restore();

  drawCrack(ctx, ease.outCubic(clamp((t - (tCrack + 0.1)) / 0.35)), 1 - sp);
}

export function drawHook(ctx, t) {
  const h2 = cue('h2');
  const h3 = cue('h3');
  const h4 = cue('h4');
  const h5 = cue('h5');
  const out = 1 - clamp((t - (h5.t1 - 0.25)) / 0.45);
  if (out <= 0) return;
  ctx.save();
  ctx.globalAlpha *= out;
  drawTitle(ctx, t, h2.t0);
  drawDuo(ctx, t, h2.t0, h3.t0);
  drawNumber(ctx, t, h3.t0, h4.t0, h5.t0);
  drawFaceOff(ctx, t, h5.t0 + 0.1);
  ctx.restore();
}
