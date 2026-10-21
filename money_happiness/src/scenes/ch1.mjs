// 研究 01 · Kahneman & Deaton 2010：45 万份问卷 → 两个问题 → 收入-幸福感示意图 → $75K 平台。
import { clamp, lerp, ease, env, mulberry32, gauss, fmtInt } from '../engine/util.mjs';
import { FONT } from '../engine/fonts.mjs';
import { C, rr, glowText, glowDot, drawChapterLabel, drawPill, strokeGlowPath, drawFixedDigits } from '../engine/draw.mjs';
import { PLOT, X, Y, U75, lifeCurve, emoCurve, curvePoints, drawLogAxes } from '../engine/chart.mjs';
import { CUES } from '../cues.mjs';

const T = Object.fromEntries(CUES.map((c) => [c.id, c]));

const LIFE_PTS = curvePoints(lifeCurve);
const EMO_PTS = curvePoints(emoCurve);

/* ---------- particles: each dot stands for a slice of the 450,000 responses ---------- */

const N = 2400;
const PARTS = (() => {
  const r = mulberry32(2010);
  const out = [];
  for (let i = 0; i < N; i++) {
    const g = i % 2; // 0 = life rating (gold), 1 = happy yesterday (cyan)
    const u = 0.004 + r() * 0.992;
    const v = (g === 0 ? lifeCurve(u) : emoCurve(u)) + gauss(r) * 0.042;
    const th = r() * Math.PI * 2;
    const rad = Math.sqrt(r());
    const cx = 960 + Math.cos(th) * rad * 600;
    const cy = 500 + Math.sin(th) * rad * 210;
    out.push({
      g,
      u,
      cx,
      cy,
      sx: cx + (r() - 0.5) * 80,
      sy: -40 - r() * 380,
      dr: r() * 1.7,
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
  if (base <= 0) return;
  const cardDim = 1 - 0.78 * env(t, T.c1b.t0 - 0.1, T.c1e.t0 + 0.35, 0.35, 0.3);
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (const group of [0, 1]) {
    ctx.fillStyle = group === 0 ? 'rgb(255,214,140)' : 'rgb(150,222,255)';
    for (const p of PARTS) {
      if (p.g !== group) continue;
      const t0 = T.c1a.t0 + 0.05 + p.dr;
      if (t < t0) continue;
      const pr = ease.outCubic(clamp((t - t0) / 0.9));
      let x = lerp(p.sx, p.cx, pr) + Math.sin(t * 0.6 + p.ph) * 6 * pr;
      let y = lerp(p.sy, p.cy, pr) + Math.cos(t * 0.5 + p.ph * 1.3) * 4 * pr;
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

function drawCounter(ctx, t) {
  const t0 = T.c1a.t0 + 0.25;
  const a = clamp((t - t0) / 0.25) * (1 - clamp((t - (T.c1b.t0 - 0.05)) / 0.3));
  if (a <= 0) return;
  const v = 450000 * ease.outCubic(clamp((t - t0) / 1.85));
  ctx.save();
  ctx.globalAlpha *= a;
  ctx.translate(960, 515);
  ctx.scale(1, 0.5);
  const back = ctx.createRadialGradient(0, 0, 0, 0, 0, 430);
  back.addColorStop(0, 'rgba(5,8,15,0.78)');
  back.addColorStop(1, 'rgba(5,8,15,0)');
  ctx.fillStyle = back;
  ctx.fillRect(-430, -430, 860, 860);
  ctx.restore();
  drawFixedDigits(ctx, fmtInt(v), 960, 500, {
    font: FONT.zh(150, 'SemiBold'),
    color: C.gold,
    glow: C.goldGlow,
    blur: 36,
    alpha: a,
  });
  // y=614: the comma tail reaches y≈585 (150px SerifSC, baseline middle at 500).
  glowText(ctx, 'RESPONSES · 份问卷', 960, 614, {
    font: FONT.mono(16),
    color: 'rgba(235,215,170,0.62)',
    alpha: a,
    letterSpacing: 6,
    baseline: 'middle',
  });
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
  glowText(ctx, String(Math.round(level)), x + 120, y + 228, {
    font: FONT.mono(92, 'SemiBold'),
    color: C.gold,
    glow: C.goldGlow,
    blur: 26,
    baseline: 'middle',
    alpha: clamp((t - T.c1c.t0) / 0.3),
  });
  glowText(ctx, '/ 10', x + 120, y + 292, {
    font: FONT.mono(16),
    color: 'rgba(214,220,234,0.5)',
    letterSpacing: 3,
    baseline: 'middle',
    alpha: clamp((t - T.c1c.t0) / 0.3),
  });
  ctx.restore();
}

function drawYesNo(ctx, x, y, t) {
  const cx = x + 260;
  const py = y + 222;
  const sel = ease.outCubic(clamp((t - T.c1d.t0 - 0.45) / 0.25));
  glowText(ctx, '昨天 · YESTERDAY', cx, y + 150, {
    font: FONT.mono(15),
    color: 'rgba(214,220,234,0.5)',
    letterSpacing: 4,
    baseline: 'middle',
  });
  [
    ['是', 'YES', -105, sel],
    ['否', 'NO', 105, 0],
  ].forEach(([zh, en, off, on]) => {
    const px = cx + off;
    ctx.save();
    rr(ctx, px - 88, py - 34, 176, 68, 34);
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
  glowText(ctx, '只能二选一 · YES / NO ONLY', cx, y + 300, {
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
    ctx.save();
    ctx.globalAlpha *= a;
    rr(ctx, x, y, W_, H_, 20);
    ctx.fillStyle = 'rgba(9,14,26,0.74)';
    ctx.fill();
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
    if (side === 0) drawLadder(ctx, x, y, t);
    else drawYesNo(ctx, x, y, t);
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
  const ma = clamp((t - mt) / 0.3);
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
  const chartDim = lerp(1, 0.12, ease.inOutCubic(clamp((t - T.c1i.t0) / 0.45)));
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
  drawBigNumber(ctx, t, fadeOut);
}
