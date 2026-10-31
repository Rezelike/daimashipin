// sections.js — ① 挑一件小事 (32–64), ② 天天做 (64–96), ③ 漏一天 (96–128) and 照着做 (128–160), all on the same road.
// Headers are road signs hanging from the top edge (this episode's own layout; not the flash-card / HUD headers of the
// earlier episodes). He stands, walks, hangs a card on a sign, stumbles into a gap and gets up, raises a hand to the sun.

// ---------- the figure after the answer (continues FIG_PATH_1 in scene.js) ----------
// ① walks to the 早饭 sign and stays there · ② one step = one day (K = 115) from day 36 to 60 · ③ steps into the gap at
// day 63.4 (heel strike on beat 100), falls forward past it, kneels, gets up, one more step · summary: the last steps to
// the top (day 69).
const FIG_PATH_2 = [
  [30.5, 29.0], [31.0, 29.4, 'in'], [34.0, 34.8, 'lin'], [35.0, 35.9, 'out'],
  [63.5, 35.9], [64.0, 36.3, 'in'], [87.0, 59.3, 'lin'], [88.0, 60.0, 'out'],
  [96.5, 60.0], [97.0, 60.4, 'in'], [99.5, 62.9, 'lin'], [100.0, 63.4, 'lin'], [101.0, 64.6, 'out'],  // falls past the gap
  [106.5, 64.6], [107.0, 64.95, 'in'], [108.0, 65.4, 'out'],
  [127.5, 65.4], [128.0, 65.9, 'in'], [129.5, 68.4, 'lin'], [130.3, 69.0, 'out'],
];
const FIG_WALK_2 = [
  [30.4, 0], [30.9, 1], [34.6, 1], [35.6, 0],
  [63.4, 0], [63.9, 1], [87.4, 1], [88.4, 0],
  [96.4, 0], [96.9, 1], [99.6, 1], [100.2, 0],
  [106.4, 0], [106.9, 1], [107.6, 1], [108.3, 0],
  [127.4, 0], [127.9, 1], [129.8, 1], [130.6, 0],
];
const FIG_S_2 = [[31, 0.8]];
// extra poses (same rig, same angle convention as kit POSES)
const HOLD_CARD = { lean: 0, head: 10, uaB: -6, faB: -2, uaF: 34, faF: 112 };
const HANG = { lean: -3, head: -4, uaB: -10, faB: -4, uaF: 92, faF: 100 };   // arm out at the hook's height
const POINT_UP = { lean: -2, head: -10, uaB: -14, faB: 24, uaF: 126, faF: 136 };
const WAVE = { lean: -5, head: -14, uaB: -12, faB: -6, uaF: 166, faF: 174 };
const NOD = { ...POSES.stand, head: 16 };
const UP_KEYS_2 = [
  [35.9, POSES.stand], [36.0, HOLD_CARD], [37.0, HANG], [38.7, POSES.stand], [40.0, POSES.point], [44.0, POSES.stand],
  [50.0, POSES.think], [55.0, POSES.stand],
  [88.6, NOD], [89.4, POSES.stand],
  [110.0, POINT_UP], [118.0, POSES.stand], [121.0, NOD], [121.8, POSES.stand],
  [130.5, POSES.point], [141.0, POSES.stand], [150.0, POSES.point], [152.5, POSES.stand], [153.5, WAVE],
];
function upperPose(bt) { return poseTrack([...UP_KEYS_1, ...UP_KEYS_2], bt); }
const ARM_HOLD = [[0, 0]];
// ③ the stumble: full-body poses (legs included), blended in over the walk
const TRIP = { lean: 38, head: -8, uaB: 70, faB: 60, uaF: 118, faF: 96, thB: -34, shB: -60, thF: 34, shF: 14 };
const KNEEL = { lean: 52, head: -24, uaB: 26, faB: 4, uaF: 34, faF: 10, thB: 4, shB: -92, thF: 10, shF: -88, ground: 24 };
const LUNGE = { lean: 18, head: -6, uaB: 6, faB: 4, uaF: 24, faF: 30, thB: 0, shB: -88, thF: 84, shF: 2 };
const FK_W = [[0, 0], [99.8, 0], [100.25, 1], [105.3, 1], [106.2, 0]];
const FK_KEYS = [[0, TRIP], [100.4, KNEEL], [104.3, LUNGE], [105.3, POSES.stand]];   // knees on the road at beat 101
function fkPoseAt(bt) { return poseTrack(FK_KEYS, bt, 0.7); }
// negative = sinks (his foot goes into the gap)
const JUMP = KB([[0, 0], [99.9, 0], [100.3, -26], [100.9, 0, 'out'], [153.5, 0], [154.0, 10, 'out'], [155.0, 0, 'in']]);
function jumpAt(bt) { return JUMP(bt) * FIGURE.s(bt); }
function figureLook(bt) {
  const pointing = (bt > 9 && bt < 12.8) || (bt > 22 && bt < 29.8) || (bt > 40 && bt < 44.2) || (bt > 110 && bt < 118.2) ||
    (bt > 130.5 && bt < 141.2) || (bt > 150 && bt < 152.7);
  return { pointF: pointing };
}

// ---------- camera after the answer ----------
const STEP_CAM = { X: 900, Y: 900, K: 64, V: 1000 };
const WALK_CAM = { X: 700, Y: 880, K: 115, V: 3370 };   // ②③: one step = one day, the slope visibly flattens
const TOP_CAM = { X: 520, Y: 830, K: 64, V: 1000 };
function sectionCam(bt) {
  const tr = (c) => ({ D: FIGURE.posD(bt), X: c.X, Y: c.Y, K: c.K, V: c.V });
  if (bt < 63.5) return tr(STEP_CAM);
  if (bt < 127.5) return mixCam(tr(STEP_CAM), tr(WALK_CAM), EASE.inOut(seg(bt, 63.5, 64.5)));
  return mixCam(tr(WALK_CAM), tr(TOP_CAM), EASE.inOut(seg(bt, 127.5, 128.7)));
}

// ---------- the road's gap (③) ----------
const GAP = { d: 63.4, w: 0.9 };
function roadOptions(bt) {
  return { gapDay: GAP.d, gapW: GAP.w, gapA: popA(bt, 96, 0.5) * (1 - seg(bt, 127.5, 128)) };
}

// ---------- header: a road sign hanging from the top edge on two chains ----------
function roadSignHeader(num, title, line2, sub, o = {}) {
  const { alpha = 1, drop = 1, typeP = 1, bt = 0 } = o;
  if (alpha <= 0.001) return;
  const x = 110, h = line2 ? 200 : 150;
  const tw = Math.max(measure(title, 58, 900), line2 ? richWidth(line2, 42, 900) : 0, measure(sub, 22, 500, 'mono'));
  const w = (num ? 150 : 50) + tw + 56, y = lerp(-20, 34, EASE.out(drop));
  withAlpha(alpha * drop * drop, () => {
    for (const cx of [x + 70, x + w - 70]) {
      ctx.save(); ctx.setLineDash([10, 6]); line(cx, -4, cx, y + 4, 'rgba(201,210,234,0.75)', 4); ctx.restore();
    }
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 8;
    rrect(x, y, w, h, 14, '#13265a'); ctx.restore();
    rrect(x + 8, y + 8, w - 16, h - 16, 9, null, 'rgba(243,238,227,0.85)', 3);
    const tx = x + (num ? 150 : 50);
    if (num) {
      ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 18; circle(x + 82, y + h / 2, 46, COL.yellow); ctx.restore();
      txt(num, x + 82, y + h / 2 + 2, { size: 58, weight: 800, fam: 'mono', color: '#13265a', align: 'center' });
    }
    txt(title, tx, y + 58, { size: 58, weight: 900, color: COL.cream });
    if (line2) rich(line2, tx, y + 122, { size: 42, weight: 900 });
    typeText(sub, typeP, tx + 2, y + h - 34, { size: 22, weight: 500, fam: 'mono', color: 'rgba(200,212,236,0.8)' }, bt);
  });
  lintPanel('header ' + title, x, y, x + w, y + h);
}
const Y_ = (s) => ({ s, color: COL.yellow });
const HEADERS = [
  { from: 32, to: 63.5, num: '1', title: '挑一件小事', line2: [{ s: '挂在' }, Y_('每天只发生一次'), { s: '的事后面' }],
    sub: 'One small thing, right after a once-a-day moment' },
  { from: 64, to: 95.5, num: '2', title: '天天做，别数天数', line2: null, sub: "Do it every day. Don't count the days." },
  { from: 96, to: 127.5, num: '3', title: '漏一天，第二天接上', line2: null, sub: 'Missed a day? Pick it up the next day.' },
  { from: 128, to: 161, num: null, title: '照着做', line2: [{ s: '按 ' }, Y_('10 周'), { s: '准备，不按 21 天' }], sub: 'Plan for ten weeks, not three.' },
];
function drawHeaders(bt) {
  for (const h of HEADERS) {
    const inP = seg(bt, h.from - 0.2, h.from + 0.6), outP = EASE.in(seg(bt, h.to - 0.6, h.to));
    if (inP <= 0 || outP >= 1) continue;
    roadSignHeader(h.num, h.title, h.line2, h.sub, { alpha: 1 - outP, drop: inP, typeP: seg(bt, h.from + 0.4, h.from + 2.6), bt });
  }
}

// ---------- ① 挑一件小事: the 早饭 sign, the card he hangs on it, the study's own examples ----------
const BREAKFAST_DAY = 39.5;
const CARD10 = { w: 236, h: 92 };
function drawSmallCard(cx, cy, s, rot, label, o = {}) {
  const { alpha = 1, color = COL.yellow, size = 38 } = o;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(s, s);
    ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 16;
    rrect(-CARD10.w / 2, -CARD10.h / 2, CARD10.w, CARD10.h, 12, '#fff6dc'); ctx.restore();
    rrect(-CARD10.w / 2, -CARD10.h / 2, 16, CARD10.h, [12, 0, 0, 12], color);
    txt(label, 8, 2, { size, weight: 900, color: '#2a1d10', align: 'center' });
    ctx.restore();
  });
}
// a roadside sign on a post: a plate with an icon and a word; returns the hook position under the plate
function roadsidePlate(d, word, o = {}) {
  const { alpha = 1, h = 430, w = 270, size = 52, icon = null, flip = null } = o;
  const x = sx(d), base = sy(d), top = base - h;
  if (alpha <= 0.001) return [x, top + 100];
  withAlpha(alpha, () => {
    rrect(x - 6, top + 40, 12, h - 40, 4, '#2a3150');
    // flip: { p (0..1), word2, icon2 } turns the plate around its vertical axis
    let face = word, ic = icon, sxp = 1;
    if (flip) { const p = flip.p; sxp = Math.abs(Math.cos(Math.PI * p)); if (p >= 0.5) { face = flip.word2; ic = flip.icon2; } }
    ctx.save(); ctx.translate(x, top + 50); ctx.scale(Math.max(0.02, sxp), 1);
    ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 16;
    rrect(-w / 2, -50, w, 100, 14, '#0f2a4a', COL.cyanHi, 3); ctx.restore();
    if (ic) ic(-w / 2 + 52, 0);
    txt(face, ic ? 26 : 0, 2, { size, weight: 900, color: COL.cream, align: 'center' });
    ctx.restore();
    circle(x, top + 108, 6, '#c9d2ea');
  });
  lintPanel('plate ' + word, x - w / 2, top, x + w / 2, top + 100);
  return [x, top + 108];
}
function iconBowl(x, y) {
  ctx.save(); ctx.strokeStyle = COL.cream; ctx.lineWidth = 4; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(x, y - 4, 22, 0, Math.PI); ctx.closePath(); ctx.stroke();
  for (const dx of [-9, 3]) { ctx.beginPath(); ctx.moveTo(x + dx, y - 14); ctx.quadraticCurveTo(x + dx - 6, y - 22, x + dx, y - 30); ctx.stroke(); }
  ctx.restore();
}
function iconClockSmall(x, y) {
  ctx.save(); ctx.strokeStyle = COL.cream; ctx.lineWidth = 4; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(x, y, 22, 0, TAU); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y - 13); ctx.moveTo(x, y); ctx.lineTo(x + 10, y + 6); ctx.stroke();
  ctx.restore();
}
const EXAMPLES = [
  { d: 44.6, word: '午饭', card: '吃一个水果', at: 42 },
  { d: 48.4, word: '晚饭前', card: '跑 15 分钟', at: 44 },
];
function drawStep1Behind(bt, t) {
  if (bt < 31 || bt > 64) return;
  const out = 1 - seg(bt, 62.5, 63.3);
  const flip = { p: seg(bt, 50, 50.4) - seg(bt, 55, 55.4), word2: '7:30', icon2: iconClockSmall };
  const hook = roadsidePlate(BREAKFAST_DAY, '早饭', { alpha: out * popA(bt, 31.5, 0.6), icon: iconBowl, flip });
  // the card: in his hand from beat 36, onto the hook at 38-38.6, then it stays there
  if (bt >= 38.6) {
    const sw = Math.sin((bt - 38.6) * 3.2) * Math.exp(-(bt - 38.6) * 2.2) * 0.12;
    withAlpha(out, () => drawSmallCard(hook[0], hook[1] + 6 + CARD10.h / 2, 1, sw, '背 10 个单词', { alpha: 1 }));
  }
  // the study's examples further up the road
  EXAMPLES.forEach((e) => {
    const a = popA(bt, e.at, 0.4) * (1 - seg(bt, 58.5, 59.3));
    if (a <= 0) return;
    const hk = roadsidePlate(e.d, e.word, { alpha: a, h: 380, w: 220, size: 42 });
    withAlpha(a, () => drawSmallCard(hk[0], hk[1] + 6 + 40, 0.86, 0, e.card, { size: 40, color: COL.cyan }));
  });
}
function drawStep1Front(bt, fig) {
  if (bt < 35.9 || bt > 64) return;
  const out = 1 - seg(bt, 62.5, 63.3);
  // card in his hand (36-38), flying to the hook (38-38.6)
  if (bt < 38.6) {
    const hookX = sx(BREAKFAST_DAY), hookY = sy(BREAKFAST_DAY) - 430 + 108 + 6 + CARD10.h / 2;
    const go = EASE.inOut(seg(bt, 38, 38.6));
    const x = lerp(fig.handF[0] + 40, hookX, go), y = lerp(fig.handF[1] - 30, hookY, go);
    drawSmallCard(x, y, popS(bt, 36, 0.5) * lerp(0.8, 1, go), lerp(-0.12, 0, go), '背 10 个单词');
  }
  const ea = popA(bt, 45, 0.5) * (1 - seg(bt, 58.5, 59.3));
  if (ea > 0) {
    txt('研究里的例子', (sx(EXAMPLES[0].d) + sx(EXAMPLES[1].d)) / 2, sy(EXAMPLES[1].d) - 430, { size: 36, weight: 900, color: COL.cyanHi, align: 'center', alpha: ea });
  }
  const na = popA(bt, 46, 0.6) * out;
  if (na > 0) sourceNote('Lally 等 2010 · 每人自选一件新的小事（吃、喝或运动），挂在每天一次的场景后', 120, 958, { alpha: na * (1 - seg(bt, 49.5, 50)) });
  const ka = popA(bt, 50.5, 0.5) * (1 - seg(bt, 57, 57.5)) * out;
  if (ka > 0) {
    rich([{ s: '定个钟点也行：' }, { s: '两种挂法差不多', color: COL.yellow }], 120, 952, { size: 40, weight: 900, alpha: ka });
    sourceNote('Keller 等 2021 · 192 人随机分组：挂在日常的事后面 vs 定钟点', 120, 1000 - 20, { alpha: ka });
  }
}

// ---------- ② 天天做: one step = one day; each step lights the slab under his foot ----------
const STEP2 = { from: 64, to: 88 };
function plantDay(n) { const P = FIGURE.posD; return P(n) + (P(n + 0.5) - P(n - 0.5)) / 2; }
function drawSlabs(bt) {
  if (bt < 63.9 || bt > 96) return;
  const out = 1 - seg(bt, 95, 95.6);
  const band = ROAD.band * clamp(Math.sqrt(zoomK()), 0.55, 1.4);
  for (let n = STEP2.from; n <= Math.min(STEP2.to, Math.floor(bt)); n++) {
    const d = plantDay(n), age = bt - n;
    const a = out * (0.35 + 0.65 * Math.exp(-age / 2.2)) * (1 - seg(bt, n, n) * 0);
    const x0 = sx(d - 0.32), x1 = sx(d + 0.32);
    if (x1 < -20 || x0 > W + 20) continue;
    ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 14 * a;
    ctx.beginPath(); ctx.moveTo(x0, sy(d - 0.32) + 2); ctx.lineTo(x1, sy(d + 0.32) + 2);
    ctx.lineTo(x1, sy(d + 0.32) + band - 2); ctx.lineTo(x0, sy(d - 0.32) + band - 2); ctx.closePath();
    ctx.fillStyle = rgba(COL.yellow, 0.75 * a); ctx.fill(); ctx.restore();
  }
}
// tiles in a row: 25 days, the missed ones dark; filled left to right over one beat starting on a beat
const MISS_88 = new Set([7, 16, 21]);       // 22 of 25 days done (88 %)
const MISS_60 = new Set([2, 5, 6, 9, 12, 14, 17, 19, 23, 24]); // 15 of 25 (60 %)
function drawStep2Front(bt) {
  if (bt < 70 || bt > 96) return;
  const out = 1 - seg(bt, 95, 95.6);
  const a = popA(bt, 72, 0.5) * out;
  if (a <= 0) return;
  withAlpha(a, () => {
    const x = 1110, y = 300;
    txt('研究里，做到的天数', x, y, { size: 36, weight: 900, color: COL.cream });
    const row = (yy, label, miss, at, color, val, valColor, size) => {
      txt(label, x, yy, { size: 34, weight: 900, color: valColor === COL.yellow ? COL.cream : COL.grayHi });
      const p = seg(bt, at, at + 1);
      for (let i = 0; i < 25; i++) {
        const on = !miss.has(i) && i < 25 * p;
        rrect(x + i * 22, yy + 50 - 14, 18, 28, 5, on ? color : 'rgba(255,255,255,0.06)', on ? null : 'rgba(200,212,236,0.35)', 2);
      }
      const va = popA(bt, at + 1, 0.4);
      if (va > 0) txt(val, x + 25 * 22 + 16, yy + 50, { size, weight: 900, color: valColor, alpha: va, glow: valColor === COL.yellow ? 14 : 0 });
    };
    row(y + 66, '曲线清楚的 39 人', MISS_88, 74, COL.yellow, '88%', COL.yellow, 48);
    row(y + 186, '曲线不清楚的人', MISS_60, 78, '#7d88a6', '60–63%', COL.grayHi, 36);
    const na = popA(bt, 82, 0.5);
    if (na > 0) {
      txt('（相关，不是因果）', x, y + 318, { size: 34, weight: 700, color: COL.pink, alpha: na });
    }
  });
  lintPanel('step2 box', 1100, 270, 1890, 640);
  const sa = popA(bt, 83, 0.6) * out;
  if (sa > 0) sourceNote('Lally 等 2010 · 82 人里 39 人画出了清楚的习惯曲线 · 中位数', 120, 978, { alpha: sa });
}

// ---------- ③ 漏一天: the gap, the stumble, the tiny dip on the 0–42 scale ----------
function drawStep3Front(bt) {
  if (bt < 101 || bt > 128) return;
  const out = 1 - seg(bt, 126.5, 127.2);
  const a = popA(bt, 102, 0.5) * out;
  if (a <= 0) return;
  withAlpha(a, () => {
    const x = 1060, y = 300;
    rich([{ s: '漏一次，只掉 ' }, { s: '0.29 分', color: COL.yellow, glow: 16 }], x, y, { size: 54, weight: 900 });
    txt('（满分 42）', x, y + 62, { size: 34, weight: 700, color: COL.grayHi });
    // the scale: 0..42, his level (the median top 35 x 95 % = 33) and the 0.29 he loses
    const rx = x, ry = y + 160, rw = 780, k = rw / 42, lvl = 33.2;
    const p = EASE.out(seg(bt, 104, 105));
    rrect(rx, ry - 13, rw, 26, 13, 'rgba(8,14,34,0.85)', 'rgba(243,238,227,0.5)', 2);
    if (p > 0) {
      const g = ctx.createLinearGradient(rx, 0, rx + lvl * k, 0);
      g.addColorStop(0, '#d98a1e'); g.addColorStop(1, COL.yellowHi);
      rrect(rx + 3, ry - 10, Math.max(20, (lvl * k - 6) * p), 20, 10, g);
    }
    for (let v = 0; v <= 42; v += 6) line(rx + v * k, ry + 18, rx + v * k, ry + 30, 'rgba(200,212,236,0.6)', 2);
    txt('0', rx, ry + 56, { size: 34, weight: 800, fam: 'mono', color: COL.grayHi, align: 'center' });
    txt('42', rx + rw, ry + 56, { size: 34, weight: 800, fam: 'mono', color: COL.grayHi, align: 'center' });
    const da = popA(bt, 106, 0.4);
    if (da > 0) {
      const dx = rx + lvl * k;
      withAlpha(da, () => {
        rrect(dx - 0.29 * k, ry - 16, Math.max(5, 0.29 * k), 32, 2, COL.pink);
        line(dx - 2, ry - 22, dx - 2, ry - 54, COL.pink, 3);
        txt('−0.29', dx, ry - 76, { size: 40, weight: 900, color: COL.pink, align: 'center' });
      });
    }
    const na = popA(bt, 112, 0.5);
    if (na > 0) rich([{ s: '第二天接着做，' }, { s: '照样往上涨', color: COL.yellow }], x, ry + 128, { size: 42, weight: 900, alpha: na });
  });
  lintPanel('step3 box', 1050, 260, 1890, 640);
  const sa = popA(bt, 107, 0.6) * out;
  if (sa > 0) sourceNote('Lally 等 2010 · 55 人一共漏做 140 次 · 0–42 分的「自动化」量表', 120, 978, { alpha: sa });
}

// ---------- 照着做: the top of the road; a signpost whose boards light up one by one while he points ----------
const SUM_BOARDS = [
  { n: 1, s: '小事 + 固定时机', at: 130 },
  { n: 2, s: '天天做', at: 134 },
  { n: 3, s: '漏了就接上', at: 138 },
];
const SUM_POST_DAY = 75.4;
function drawSummaryBehind(bt, t) {
  if (bt < 127.5) return;
  // the 66-day flag from the hook, now beside him at the top
  drawFlag(66.5, '第 66 天', { h: 440, size: 50, t, side: -1, scaleText: false, zoom: 1, alpha: popA(bt, 127.5, 0.8) });   // cloth above head height
  if (bt < 127) return;
  const a = popA(bt, 128.4, 0.6);
  drawSignpost(sx(SUM_POST_DAY), sy(SUM_POST_DAY), 404, SUM_BOARDS, bt, {
    alpha: a, bw: 640, bh: 96, gap: 26, size: 46, lit: (i) => popA(bt, SUM_BOARDS[i].at + 0.15, 0.4) });
}
function drawSummaryFront(bt) {
  if (bt < 128) return;
  // sunrise sweep across the finished signpost (146)
  const sw = seg(bt, 146, 147.4);
  if (sw > 0 && sw < 1) withAlpha(Math.min(1, sw / 0.08) * (1 - sw) * 0.6, () => {
    const cx = lerp(800, 1700, sw);
    const g = ctx.createLinearGradient(cx - 220, 0, cx + 220, 0);
    g.addColorStop(0, 'rgba(255,214,150,0)'); g.addColorStop(0.5, 'rgba(255,214,150,0.5)'); g.addColorStop(1, 'rgba(255,214,150,0)');
    ctx.fillStyle = g; ctx.fillRect(cx - 220, 380, 440, 380);
  });
  const fa = popA(bt, 143, 0.6);
  if (fa > 0) {
    txt('仅供参考：多为研究生、自评量表；254 天是曲线推算', 120, 930, { size: 30, weight: 700, color: COL.grayHi, alpha: fa });
    txt('Lally 2010 · Gardner 2012 · Singh 2024', 120, 976, { size: 22, weight: 500, fam: 'mono', color: COL.grayDim, alpha: fa });
  }
}

// ---------- the 不用想就会做 bar after the hook ----------
function barAlphaLater(bt) {
  return popA(bt, 65, 0.5) * (1 - seg(bt, 126.5, 127.1)) + popA(bt, 130, 0.5) * (1 - seg(bt, 141.5, 142));
}
function barNote(bt) {
  if (bt >= 101.6 && bt < 105.5) return { s: '−0.29', c: COL.pink };
  if (bt >= 130.5 && bt < 142) return { s: '到顶', c: COL.yellow };
  return null;
}
function barDip(bt) { return win(bt, 101.2, 106.4, 0.2, 1.2) * (0.29 / 35); }

// ---------- wiring ----------
function drawSectionsBehind(bt, t) {
  drawStep1Behind(bt, t);
  drawSlabs(bt);
  drawSummaryBehind(bt, t);
}
function drawSections(bt, t, fig) {
  if (bt < 31) return;
  drawHeaders(bt);
  drawStep1Front(bt, fig);
  drawStep2Front(bt);
  drawStep3Front(bt);
  drawSummaryFront(bt);
}
