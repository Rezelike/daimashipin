// scene.js — timeline, camera, the figure's moves, the hook (0–17) and the answer (17–32). All times in beats (bt).
// 128 BPM -> 1 beat = 0.46875 s; 160 beats = 75 s. Beat grid of 睡还是背 (lessons 13, six/plan.md): reveal 1 at 4.5
// (2.11 s), reveal 2 four beats later at 8.5 (3.98 s), 4.92 / 5.39 s the two labels, 6.1 s the source, the answer
// from beat 17 (8.0 s), the evidence card at 26.5 (12.4 s), steps at 32 / 64 / 96, the summary at 128.
const TOTAL_BEATS = 160;

// ---------- the figure: where he is on the road (pelvis day) and what he does ----------
// Walks are one step per beat; they start on half beats so the heel strikes (and their footstep sounds) are on the beats.
// Hook: day 12.9 -> 21 (1.8 days per step at K = 64); answer: 21 -> 29; the rest is written in sections.js (FIG_PATH_2).
const FIG_PATH_1 = [[0, 12.9], [4.0, 20.1, 'lin'], [5.0, 21.2, 'out'], [16.5, 21.2], [17.0, 21.6, 'in'], [20.5, 27.9, 'lin'], [21.5, 29.0, 'out']];
const FIG_WALK_1 = [[0, 1], [4.2, 1], [5.2, 0], [16.4, 0], [16.9, 1], [20.8, 1], [21.6, 0]];
const FIG_S_1 = [[0, 0.8], [8.5, 0.8], [9.6, 0.42, 'inOut'], [15.5, 0.42], [17.4, 0.8, 'inOut']];
// upper-body poses by time: [beat, name, weight-in beats]
const POSE_UP = POSES; // stand / point / think / cheer / slump / shrug + the ones added in sections.js
const FIGURE = {}; // filled once sections.js has added its keys (initFigure)
function initFigure() {
  const path = [...FIG_PATH_1, ...FIG_PATH_2], walk = [...FIG_WALK_1, ...FIG_WALK_2], sc = [...FIG_S_1, ...FIG_S_2];
  FIGURE.posD = KB(path);
  FIGURE.walk = KB(walk);
  FIGURE.s = KB(sc);
  FIGURE.up = (bt) => upperPose(bt);
  FIGURE.armHold = KB(ARM_HOLD);
  FIGURE.fk = KB(FK_W);
  FIGURE.fkPose = (bt) => fkPoseAt(bt);
  FIGURE.jump = (bt) => jumpAt(bt);
}
// upper-body pose track: list of [beat, poseObject]; blends over 0.6 beat into each key. The blend starts fast
// (ease-out) so the movement visibly starts ON its key beat (VERIFY rhythm measures where a change starts)
function poseTrack(keys, bt, blend = 0.6) {
  let cur = keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [b, p] = keys[i];
    if (bt < b) break;
    const q = EASE.out(seg(bt, b, b + blend));
    cur = lerpPose(cur, p, q);
  }
  return cur;
}
const LOOK_UP = { ...POSES.stand, head: -22, lean: -3 };
const POINT_WIDE = { lean: 0, head: -6, uaB: -16, faB: 30, uaF: 116, faF: 122, thB: -5, shB: -5, thF: 8, shF: 8 };
const UP_KEYS_1 = [
  [0, POSES.stand],
  [4.6, LOOK_UP],              // reveal 1: he looks up at the bar
  [6.0, POSES.shrug],          // 还没到顶
  [7.5, POSES.stand],
  [9.0, POINT_WIDE],           // reveal 2: points up the road at the 66 flag
  [12.6, POSES.stand],
  [22.0, POSES.point],         // the answer: points at the signpost boards
  [29.5, POSES.stand],
];

// ---------- camera ----------
const HOOK_CAM = { D: 21, X: 1300, Y: 790, K: 64, V: 1000 };
const WIDE_CAM = { D: 21, X: 640, Y: 760, K: 22, V: 560 };
function mixCam(a, b, t) {
  const o = {};
  for (const k of ['D', 'X', 'Y', 'K', 'V']) o[k] = lerp(a[k], b[k], t);
  return o;
}
function track(bt, X, Y, K, V) { return { D: FIGURE.posD(bt), X, Y, K, V }; }
function camAt(bt) {
  if (bt < 8.5) return HOOK_CAM;
  if (bt < 15.5) return mixCam(HOOK_CAM, WIDE_CAM, EASE.inOut(seg(bt, 8.5, 9.6)));
  if (bt < 31) return mixCam(WIDE_CAM, track(bt, 900, 900, 64, 1000), EASE.inOut(seg(bt, 15.5, 17.4)));
  return sectionCam(bt);
}

// ---------- title block (top left): the hook question, flipping to the answer at beat 17 ----------
function drawTitleBlock(bt) {
  const outA = 1 - EASE.out(seg(bt, 30.5, 31.4));
  const dyOut = -40 * EASE.in(seg(bt, 30.5, 31.4));
  if (outA <= 0) return;
  withAlpha(outA, () => {
    const X0 = 120;
    const flipLine = (y, clipH, a0, a1, p) => {
      const e = EASE.out(p);
      ctx.save(); ctx.beginPath(); ctx.rect(0, y - clipH / 2, W, clipH); ctx.clip();
      if (e < 1) withAlpha(1 - e, () => a0(y - e * clipH));
      if (e > 0) withAlpha(e, () => a1(y + (1 - e) * clipH));
      ctx.restore();
    };
    flipLine(130 + dyOut, 150,
      (y) => txt('21 天', X0, y, { size: 128, weight: 900, color: COL.yellow, glow: 28 }),
      (y) => rich([{ s: '不按 ', color: COL.grayHi }, { s: '21 天', color: COL.grayHi }], X0, y, { size: 96, weight: 900 }),
      seg(bt, 17.0, 17.6));
    flipLine(268 + dyOut, 150,
      (y) => txt('能养成习惯吗？', X0, y, { size: 128, weight: 900, color: COL.cream }),
      (y) => txt('按 2 个多月准备', X0, y, { size: 128, weight: 900, color: COL.yellow, glow: 30 }),
      seg(bt, 17.0, 17.6));
    const en1 = '21 days to build a habit?', en2 = 'Plan for two months, not three weeks.';
    const useSecond = bt >= 17;
    const s = useSecond ? en2 : en1;
    const p1 = useSecond ? seg(bt, 17.4, 20.2) : lerp(8 / en1.length, 1, seg(bt, 0, 2.4));
    typeText(s, p1, X0 + 4, 366 + dyOut, { size: 34, weight: 500, fam: 'mono', color: COL.cyan, keepCursor: true }, bt);
  });
}

// ---------- caption under the title: reveal 1 / reveal 2 (flips on the beat) ----------
const CAPTIONS = [
  { at: 4.5, main: [{ s: '第 21 天：' }, { s: '还没到顶', color: COL.yellow }], note: '按论文的曲线估算：约 2/3' },
  { at: 8.5, main: [{ s: '一般要 ' }, { s: '66 天', color: COL.yellow, glow: 22 }], note: '这是中位数：有人快，有人慢' },
];
function drawCaption(bt) {
  const A = 1 - EASE.out(seg(bt, 17.0, 17.5));
  if (A <= 0 || bt < 4.5) return;
  CAPTIONS.forEach((c, i) => {
    const next = CAPTIONS[i + 1];
    const pin = EASE.out(seg(bt, c.at, c.at + 0.45));
    const pout = next ? EASE.inOut(seg(bt, next.at - 0.05, next.at + 0.35)) : 0;
    const a = A * pin * (1 - pout);
    if (a <= 0.001) return;
    const dy = (1 - pin) * 50 - pout * 50;
    rich(c.main, 120, 528 + dy, { size: 66, weight: 900, alpha: a });
    txt(c.note, 124, 596 + dy, { size: 34, weight: 700, color: COL.grayHi, alpha: a * popA(bt, c.at + 0.5, 0.4) });
  });
}

// ---------- the hook's props on the road ----------
const PLATES = [9, 12, 15, 18, 24, 27, 30];
const FLAG21 = 23.2;   // a little ahead of where he stops (21.2); the cloth hangs above head height (he walks under it)
function drawHookProps(bt, t) {
  const plateA = 1 - seg(bt, 8.5, 9.2);
  if (plateA > 0) for (const d of PLATES) if (d !== 18 || bt < 10.5) drawDayPlate(d, String(d), { alpha: plateA });
  // the 21-day flag (he reaches it at reveal 1); 18 = the fastest person's top (lights at 4.92 s); 66 = the median top
  const flash21 = win(bt, 4.5, 5.6, 0.1, 0.9);
  // flags shrink with the camera when it pulls back (K 64 -> 22) and grow again when it closes in
  const wide = clamp((1 - zoomK()) / (1 - WIDE_CAM.K / 64));
  drawFlag(FLAG21, '第 21 天', { h: 440, size: lerp(50, 34, wide), t, glow: 1 + flash21, zoom: lerp(1, 0.35, wide), scaleText: false,
    alpha: 1 - seg(bt, 18.5, 19.3) });
  const farA = 1 - seg(bt, 15.5, 16.2);  // the far flags leave as the camera closes in again
  const a18 = popA(bt, 10.5, 0.3) * farA;
  if (a18 > 0) withScale(sx(18), sy(18), 0.7 + 0.3 * popS(bt, 10.5, 0.6), () =>
    drawFlag(18, '最快 18 天', { h: 300, size: 36, t, side: -1, color: COL.cyan, glow: 1.4, alpha: a18, zoom: 0.45, scaleText: false }));
  if (bt < 16.2) drawFlag(66.5, '第 66 天', { h: 440, size: 46, t, zoom: lerp(1, 0.55, wide), scaleText: false,
    glow: 1 + win(bt, 8.6, 9.8, 0.2, 0.8), alpha: farA });
}
// 「最慢 ≈254 天（推算）」: far beyond the right edge (the study lasted 84 days; anything after that is the fitted curve)
function drawSlowest(bt) {
  const a = popA(bt, 11.5, 0.4) * (1 - seg(bt, 15.5, 16.2));
  if (a <= 0) return;
  withAlpha(a, () => {
    const x1 = 1880, y = 700;
    ctx.save(); ctx.setLineDash([14, 12]); ctx.strokeStyle = 'rgba(181,191,214,0.8)'; ctx.lineWidth = 4; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(1560, y + 54); ctx.lineTo(x1 - 14, y + 54); ctx.stroke(); ctx.restore();
    ctx.beginPath(); ctx.moveTo(x1, y + 54); ctx.lineTo(x1 - 22, y + 40); ctx.lineTo(x1 - 22, y + 68); ctx.closePath();
    ctx.fillStyle = 'rgba(181,191,214,0.9)'; ctx.fill();
    txt('最慢 ≈254 天', x1, y - 20, { size: 42, weight: 900, color: COL.cream, align: 'right' });
    txt('（推算）', x1, y + 106, { size: 34, weight: 700, color: COL.grayHi, align: 'right' });
  });
  lintPanel('slowest', 1560, 670, 1880, 830);
}

// ---------- the answer (17–32): a signpost with three boards, the 1960 card ----------
const ANSWER_BOARDS = [
  { n: 1, s: '做什么', at: 19.0 },
  { n: 2, s: '怎么坚持', at: 21.5 },
  { n: 3, s: '漏了怎么办', at: 25.0 },
];
const SIGNPOST_DAY = 31.6;
function drawAnswer(bt) {
  if (bt < 17.5 || bt > 32) return;
  const out = 1 - seg(bt, 30.4, 31.1);
  const x = sx(SIGNPOST_DAY), base = sy(SIGNPOST_DAY);
  drawSignpost(x, base, 448, ANSWER_BOARDS, bt, { alpha: out * popA(bt, 18, 0.5), bw: 440 });
  const ea = popA(bt, 26.5, 0.5) * out;
  if (ea > 0) withAlpha(ea, () => withScale(470, 590, 0.85 + 0.15 * popS(bt, 26.5, 0.6), () => drawOriginCard(110, 470, 720, 240)));
}
// 「21 天」 comes from a 1960 book by a plastic surgeon (Maltz, Psycho-Cybernetics): patients took about three weeks to get
// used to their new face. Drawn as a yellowed note with a hand mirror.
function drawOriginCard(x, y, w, h) {
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 8;
  rrect(x, y, w, h, 14, '#efe3c6'); ctx.restore();
  rrect(x + 8, y + 8, w - 16, h - 16, 10, null, 'rgba(120,84,40,0.35)', 2);
  // hand mirror
  const mx = x + w - 92, my = y + 92;
  ctx.save(); ctx.translate(mx, my); ctx.rotate(0.5);
  rrect(-8, 34, 16, 70, 6, '#8a5a2b');
  circle(0, 0, 44, '#8a5a2b'); circle(0, 0, 35, '#bcd6e6');
  ctx.beginPath(); ctx.arc(-8, -10, 18, Math.PI * 1.05, Math.PI * 1.55); ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.lineWidth = 4; ctx.stroke();
  ctx.restore();
  txt('1960 年', x + 30, y + 46, { size: 38, weight: 900, color: '#8a5a2b' });
  txt('「21 天」出自一位整形医生：', x + 30, y + 104, { size: 36, weight: 900, color: '#2a1d10' });
  txt('病人约 3 周看惯新脸', x + 30, y + 156, { size: 36, weight: 900, color: '#2a1d10' });
  txt('不是习惯研究', x + 30, y + 208, { size: 40, weight: 900, color: '#c2365f' });
  lintPanel('origin card', x, y, x + w, y + h);
}

// ---------- frame ----------
function renderFrame(t) {
  const bt = t / BEAT;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  setCam(camAt(bt));
  const par = CAM.D * 30; // parallax reference: world days -> px for the far layers
  drawSky(bt, t, par);
  drawRanges(bt, par);
  drawRoad(bt, roadOptions(bt));
  const info = { t, bt, kid: false };

  if (bt < 32) drawHookProps(bt, t);
  drawSectionsBehind(bt, t);
  drawFog((1 - seg(bt, 8.5, 9.6)) * (bt < 10 ? 1 : 0), sx(25));

  const fig = drawWalker(bt, FIGURE, figureLook(bt));
  info.kid = true;
  lintPanel('head:figure', fig.head[0] - 26 * FIGURE.s(bt), fig.head[1] - 28 * FIGURE.s(bt), fig.head[0] + 26 * FIGURE.s(bt), fig.head[1] + 28 * FIGURE.s(bt));

  // the 不用想就会做 bar rides above him (fixed height above the road under him: it must not bob with his steps)
  const d = FIGURE.posD(bt);
  const barA = (1 - seg(bt, 8.5, 9.0)) * (bt < 10 ? 1 : 0) + barAlphaLater(bt);
  if (barA > 0.001) {
    const flash = win(bt, 4.5, 5.8, 0.1, 1.0);
    const note = barNote(bt);
    drawHabitBar(sx(d) + (bt < 17 ? -140 : 10), sy(d) - 420 * FIGURE.s(bt) - 70, habitE(d) - barDip(bt),
      { alpha: barA, flash, note: note ? note.s : null, noteColor: note ? note.c : COL.yellow, dip: barDip(bt) * 330 });
  }

  drawTitleBlock(bt);
  drawCaption(bt);
  drawSlowest(bt);
  sourceNote('Lally 等 2010 · 伦敦 82 人 · 每天做一件新的小事，跟踪 84 天', 120, 1000 - 22, { alpha: popA(bt, 13, 0.8) * (1 - EASE.out(seg(bt, 17, 17.5))) });
  drawAnswer(bt);
  drawSections(bt, t, fig);
  drawVignette();
  drawChapterBar(bt);
  window.__frameInfo = info;
}
