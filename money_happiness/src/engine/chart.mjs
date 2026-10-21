// 收入-幸福感示意图。曲线形状依据论文结论绘制（示意），不是逐点还原原始数据。
import { clamp, lerp, ease, smin } from './util.mjs';
import { FONT } from './fonts.mjs';
import { glowText } from './draw.mjs';

export const PLOT = { L: 360, R: 1560, T: 270, B: 700 };

const LMIN = Math.log(10000);
const LMAX = Math.log(160000);

/** Household income (USD) → 0..1 on a log axis from $10K to $160K. */
export const uOf = (usd) => (Math.log(usd) - LMIN) / (LMAX - LMIN);
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

const TICKS = [
  [10000, '$10K'],
  [25000, '$25K'],
  [50000, '$50K'],
  [100000, '$100K'],
  [150000, '$150K'],
];

/** Axes that draw themselves in starting at t0. */
export function drawLogAxes(ctx, t, t0) {
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
    for (const [v] of TICKS) {
      const x = X(uOf(v));
      ctx.beginPath();
      ctx.moveTo(x, PLOT.B);
      ctx.lineTo(x, PLOT.B + 8);
      ctx.stroke();
    }
    ctx.restore();
    ctx.save();
    for (const [v, label] of TICKS) {
      glowText(ctx, label, X(uOf(v)), PLOT.B + 36, {
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
