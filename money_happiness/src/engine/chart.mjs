// 收入-幸福感示意图。曲线形状依据论文结论绘制（示意），不是逐点还原原始数据。
import { clamp, lerp, ease, smin } from './util.mjs';
import { FONT } from './fonts.mjs';
import { glowText } from './draw.mjs';

export const PLOT = { L: 360, R: 1560, T: 270, B: 700 };

/** Log-scaled income axis: income (USD) → u in 0..1 across the plot. */
export function makeLogAxis(minUsd, maxUsd, ticks) {
  const lmin = Math.log(minUsd);
  const lmax = Math.log(maxUsd);
  return { uOf: (usd) => (Math.log(usd) - lmin) / (lmax - lmin), ticks };
}

// 2010 data top out at "$120,000 and above", so the 2010 chart stops at $160K.
const AXIS_2010 = makeLogAxis(10000, 160000, [
  [10000, '$10K'],
  [25000, '$25K'],
  [50000, '$50K'],
  [100000, '$100K'],
  [150000, '$150K'],
]);

/** Household income (USD) → 0..1 on a log axis from $10K to $160K. */
export const uOf = AXIS_2010.uOf;
export const U75 = uOf(75000);
export const U100 = uOf(100000);

export const X = (u) => PLOT.L + u * (PLOT.R - PLOT.L);
export const Y = (v) => PLOT.B - v * (PLOT.B - PLOT.T);

/** Kahneman & Deaton 2010: life evaluation rises steadily with log income. */
export const lifeCurve = (u) => 0.12 + 0.7 * u;
/** Kahneman & Deaton 2010: emotional well-being rises, then flattens near $75K. */
export const emoCurve = (u) => 0.1 + 0.4 * smin(u / U75, 1, 0.12);

export function curvePoints(fn, u0 = 0, u1 = 1, n = 180) {
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const u = lerp(u0, u1, i / n);
    pts.push([X(u), Y(fn(u))]);
  }
  return pts;
}

/* ---------- 2021 / 2023: these analyses cover incomes well above $160K, so their charts run to $250K ---------- */

export const AXIS_WIDE = makeLogAxis(10000, 250000, [
  [10000, '$10K'],
  [25000, '$25K'],
  [50000, '$50K'],
  [100000, '$100K'],
  [200000, '$200K'],
]);
export const W75 = AXIS_WIDE.uOf(75000);
export const W80 = AXIS_WIDE.uOf(80000);
export const W100 = AXIS_WIDE.uOf(100000);
export const W160 = AXIS_WIDE.uOf(160000);

/** Kahneman & Deaton 2010 drawn on the wide axis (as a ghost): rises, then flattens near $75K. */
export const emoWide = (u) => 0.1 + 0.4 * smin(u / W75, 1, 0.12);
/** The 2010 plateau height on the wide axis ("the ceiling"). */
export const CEIL_V = emoWide(1);
// Same rise as the 2010 curve below $75K, so the two part ways exactly where 2010 flattened.
const SLOPE21 = 0.4 / W75;
/** Killingsworth 2021: how people feel right now rises linearly with log income, equally steep above and below $80K. */
export const nowCurve = (u) => 0.1 + SLOPE21 * u;
/** Killingsworth 2021: life satisfaction rises too; no income at which the two diverge. */
export const life21Curve = (u) => 0.22 + SLOPE21 * u;
/** Where the 2021 line passes the 2010 ceiling. */
export const U_CROSS = (CEIL_V - 0.1) / SLOPE21;

/**
 * Killingsworth, Kahneman & Mellers 2023: percentiles of happiness (15th…85th). Every percentile rises until $100K;
 * above it the 15th flattens and the 85th steepens. `post` is the slope multiplier past $100K; the posts average 1,
 * so the mean of the five lines stays a straight line ("complementary nonlinearities").
 */
export const PCTS = [
  { p: 15, base: 0.04, post: 0 },
  { p: 30, base: 0.145, post: 0.9 },
  { p: 50, base: 0.25, post: 0.95 },
  { p: 70, base: 0.355, post: 0.95 },
  { p: 85, base: 0.46, post: 2.2 },
];
const PSLOPE = 0.34;
const softKnee = (x, k = 0.035) => (x + Math.sqrt(x * x + k * k) - k) / 2;
export const pctCurve = (row) => (u) => row.base + PSLOPE * u + PSLOPE * (row.post - 1) * softKnee(u - W100);
/** The same percentile line if nothing changed at $100K. */
export const pctStraight = (row) => (u) => row.base + PSLOPE * u;
export const pctMean = (u) => PCTS.reduce((s, r) => s + pctCurve(r)(u), 0) / PCTS.length;

/** Axes that draw themselves in starting at t0. Pass AXIS_WIDE for the 2021 / 2023 charts. */
export function drawLogAxes(ctx, t, t0, axis = AXIS_2010) {
  const px = ease.inOutCubic(clamp((t - t0) / 0.6));
  const py = ease.inOutCubic(clamp((t - t0) / 0.45));
  if (px <= 0) return;
  ctx.save();
  ctx.strokeStyle = 'rgba(232,206,150,0.5)';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(PLOT.L, PLOT.B);
  ctx.lineTo(lerp(PLOT.L, PLOT.R + 12, px), PLOT.B);
  ctx.moveTo(PLOT.L, PLOT.B);
  ctx.lineTo(PLOT.L, lerp(PLOT.B, PLOT.T - 24, py));
  ctx.stroke();

  const la = clamp((t - t0 - 0.3) / 0.4);
  if (la > 0) {
    ctx.globalAlpha *= la;
    ctx.strokeStyle = 'rgba(232,206,150,0.4)';
    for (const [v] of axis.ticks) {
      const x = X(axis.uOf(v));
      ctx.beginPath();
      ctx.moveTo(x, PLOT.B);
      ctx.lineTo(x, PLOT.B + 8);
      ctx.stroke();
    }
    ctx.restore();
    ctx.save();
    for (const [v, label] of axis.ticks) {
      glowText(ctx, label, X(axis.uOf(v)), PLOT.B + 36, {
        font: FONT.mono(17),
        color: 'rgba(210,210,222,0.55)',
        alpha: la,
      });
    }
    glowText(ctx, '家庭年收入 · INCOME', PLOT.R + 26, PLOT.B + 6, {
      font: FONT.mono(15),
      color: 'rgba(232,206,150,0.62)',
      align: 'left',
      letterSpacing: 3,
      alpha: la,
    });
    glowText(ctx, '对数刻度 · LOG SCALE', PLOT.R + 26, PLOT.B + 34, {
      font: FONT.mono(12),
      color: 'rgba(214,220,234,0.36)',
      align: 'left',
      letterSpacing: 3,
      alpha: la,
    });
    ['幸', '福', '感'].forEach((ch, i) => {
      glowText(ctx, ch, PLOT.L - 52, 452 + i * 34, {
        font: FONT.zh(25),
        color: 'rgba(236,236,240,0.78)',
        alpha: la,
        baseline: 'middle',
      });
    });
    glowText(ctx, '示意图 · SCHEMATIC', PLOT.R, PLOT.T - 26, {
      font: FONT.mono(13),
      color: 'rgba(214,220,234,0.52)',
      align: 'right',
      letterSpacing: 3,
      alpha: la,
    });
  }
  ctx.restore();
}
