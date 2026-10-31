// scene.js — timeline. All times in beats (bt). 128 BPM -> 1 beat = 0.46875 s; 160 beats = 75 s.
// Same beat grid as sleep_or_cram / bedtime_words (lessons 13): reveal 1 at beat 4.5 (2.11 s), reveal 2 four beats later
// at 8.5 (3.98 s), the check at 10.5 (4.92 s), the answer from beat 17 (8.0 s), steps at 32 / 64 / 96, the summary at 128.
// Stage (six/plan.md, item 4): a pool of water; the longer he sleeps, the deeper his mattress sinks (= more deep sleep).
const TOTAL_BEATS = 160;

// ---------- pose tracks ----------
// keys: [[beat, pose (object or POSES name)], ...]; eased blend between neighbours, held outside
function PT(keys) {
  const ks = keys.map(([b, p, e]) => [b, typeof p === 'string' ? { ...POSES.stand, ...POSES[p] } : { ...POSES.stand, ...p }, e]);
  return (bt) => {
    if (bt <= ks[0][0]) return ks[0][1];
    for (let i = 1; i < ks.length; i++) {
      if (bt <= ks[i][0]) {
        const [b0, p0] = ks[i - 1], [b1, p1, e] = ks[i];
        return lerpPose(p0, p1, EASE[e || 'inOut'](b1 === b0 ? 1 : (bt - b0) / (b1 - b0)));
      }
    }
    return ks[ks.length - 1][1];
  };
}
const withHead = (p, d) => ({ ...p, head: (p.head || 0) + d });

// ---------- the mattress (in the pool the whole video) ----------
const MAT_X = KB([[0, 600], [15.5, 600], [17.5, 380], [31.0, 380], [32.5, 480], [63, 480], [64.5, 560], [95.0, 560],
  [97.0, 880], [126.0, 880], [127.5, 300], [160, 300]]);
const F = DEPTH.float;
const MAT_Y = KB([
  // opening: sinking from frame 0 (the first 10 minutes barely sink it), groggy rise after reveal 1
  [0, F], [1.5, DEPTH.m10, 'lin'], [3.0, 820, 'lin'], [4.0, 884, 'lin'], [4.4, DEPTH.m30, 'out'], [4.5, DEPTH.m30], [8.4, F, 'inOut'],
  // ① asleep 10 minutes: sinks only a little, pops up when the phone buzzes
  [38, F], [46, DEPTH.m10, 'inOut'], [46.5, DEPTH.m10], [47.0, F, 'out'],
  // ② long nap: down into the 30-60 zone, then the slow rise
  [66, F], [72, 924, 'inOut'], [74, 924], [88, F, 'inOut'],
  // summary: a dip for 10 minutes, a deep sink and a slow rise for 30-60 minutes, a bob when he jumps off
  [130.5, F], [131.5, 668, 'out'], [132.0, F, 'out'], [134.5, F], [136.0, 770, 'inOut'], [136.5, 770], [140.0, F, 'inOut'],
  [152.5, F], [153.0, F + 14, 'out'], [154.0, F, 'inOut'],
]);
function matTilt(bt) {
  // a slow rock while floating (no beat pulse)
  return 0.012 * Math.sin(bt * BEAT * 1.1);
}

// ---------- hero (one adult figure, style A; on screen in every frame) ----------
const POSE = PT([
  [0, 'lie'], [4.5, 'lie'], [5.5, 'sitSlump', 'out'], [8.5, 'sitSlump'], [9.0, 'sitLong', 'out'],
  [18.0, 'sitLong'], [18.5, 'sitStretch', 'out'], [20.5, 'sitStretch'], [21.0, 'sitLong', 'out'],
  // ①
  [32.5, 'sitLong'], [33.5, 'lie', 'out'], [46.5, 'lie'], [47.0, 'sitLong', 'out'], [54.0, 'sitLong'], [54.5, 'sitPoint', 'out'], [57.0, 'sitPoint'], [57.5, 'sitLong', 'out'],
  // ②
  [64.5, 'sitLong'], [65.5, 'lie', 'out'], [72.5, 'lie'], [73.5, 'sitSlump', 'out'], [86.5, 'sitSlump'], [87.0, 'sitLong', 'out'], [89.5, 'sitLong'],
  [90.0, 'sitHold', 'out'], [94.0, 'sitHold'], [94.5, 'sitLong', 'out'],
]);
// the face: asleep (eyes shut) while lying, blinks otherwise
const SLEEP = [[0, 4.5], [37.5, 46.5], [67.0, 72.5], [130.5, 131.5], [134.5, 136.5]];
const BLINKS = [11.5, 14.5, 22.5, 27.5, 35.0, 36.5, 50.0, 56.0, 61.0, 92.5, 102.5, 108.0, 119.5, 124.5, 142.0, 147.5, 157.0];
function faceAt(bt, base = 'calm') {
  for (const [a, b] of SLEEP) if (bt >= a && bt < b) return 'tired';
  for (const b of BLINKS) if (bt >= b && bt < b + 0.3) return 'tired';
  return base;
}
// head shake: "awake now" (reveal 2), and at the end of the slow rise in ②
function headShake(bt) {
  for (const b of [8.5, 87.0]) if (bt > b && bt < b + 0.9) return 13 * Math.sin((bt - b) * Math.PI * 4) * (1 - seg(bt, b + 0.5, b + 0.9));
  return 0;
}

// ---------- title block (0–31.4) ----------
function drawTitleBlock(bt, t) {
  const outA = 1 - EASE.out(seg(bt, 30.5, 31.4));
  const dyOut = -40 * EASE.in(seg(bt, 30.5, 31.4));
  if (outA <= 0) return;
  withAlpha(outA, () => {
    txt('午睡醒来', 960, 150 + dyOut, { size: 100, weight: 900, color: COL.cream, align: 'center' });
    const p = seg(bt, 16.5, 17.25), e = EASE.out(p), y2 = 288 + dyOut;
    ctx.save();
    ctx.beginPath(); ctx.rect(0, y2 - 100, W, 200); ctx.clip();
    if (e < 1) {
      rich([{ s: '反而', color: COL.cream }, { s: '更懵', color: COL.yellow, glow: 26 }, { s: '？', color: COL.cream }],
        960, y2 - e * 180, { size: 142, weight: 900, align: 'center', alpha: 1 - e });
    }
    if (e > 0) {
      rich([{ s: '马上要用脑，', color: COL.cream }, { s: '睡 10 分钟', color: COL.yellow, glow: 30 }],
        960, y2 + (1 - e) * 180, { size: 120, weight: 900, align: 'center', alpha: e });
    }
    ctx.restore();
    const en1 = 'Groggier after a nap?', en2 = 'Need your brain right away? Nap for 10 minutes.';
    const useSecond = bt >= 16.75, s = useSecond ? en2 : en1;
    const fw = measure(s, 34, 500, 'mono');
    const p1 = useSecond ? seg(bt, 17.0, 20.5) : lerp(6 / en1.length, 1, seg(bt, 0, 2.2));
    typeText(s, p1, 960 - fw / 2, 388 + dyOut, { size: 34, weight: 500, fam: 'mono', color: COL.cyan, keepCursor: true }, bt);
  });
}

// ---------- opening (0–17): the depth gauge, the three score boards on the deck ----------
// Tietzel & Lack 2001, table 3: symbol -> digit substitutions in 90 s (12 students, same people in every condition)
//   5 min after waking: no nap 55.0, 10-min nap 65.3, 30-min nap 50.6 (all pairwise different)
//   35 min after waking: 54.4, 66.9, 60.8 (the 30-min nap has recovered; vs no nap not significant -> 「缓过来了」, not 「反超」)
const BOARDS = [
  { label: '没睡', x: 1250, tone: COL.grayHi, v1: 55, v2: 54, litAt: 0 },
  { label: '睡 10 分钟', x: 1500, tone: COL.yellow, v1: 65, v2: 67, litAt: 1.5 },
  { label: '睡 30 分钟', x: 1750, tone: COL.pink, v1: 51, v2: 61, litAt: 4.0 },
];
const BOARD_TOP = 480, BOARD_H = 128;
// a number that rolls from a to b over [t0, t0 + d]
const roll = (bt, t0, d, a, b) => (bt < t0 ? a : bt >= t0 + d ? b : Math.round(lerp(a, b, EASE.out((bt - t0) / d))));
function drawOpening(bt, t) {
  const A = 1 - seg(bt, 15.5, 16.5);
  if (A <= 0) return;
  withAlpha(A, () => {
    // caption: 醒来 5 分钟 (reveal 1) -> 醒来 35 分钟 (reveal 2)
    const ca = popA(bt, 4.5, 0.3);
    if (ca > 0) {
      ctx.save(); ctx.beginPath(); ctx.rect(1130, 360, 760, 74); ctx.clip();
      const f = EASE.inOut(seg(bt, 8.5, 8.95));
      if (f < 1) rich([{ s: '醒来 ' }, { s: '5 分钟', color: COL.yellow }, { s: '，做同一种题' }], 1500, 396 - f * 70, { size: 42, weight: 900, align: 'center', alpha: ca * (1 - f) });
      if (f > 0) rich([{ s: '醒来 ' }, { s: '35 分钟', color: COL.yellow }, { s: '，再做一次' }], 1500, 396 + (1 - f) * 70, { size: 42, weight: 900, align: 'center', alpha: f });
      ctx.restore();
      txt('90 秒内把符号换成数字，换对几个', 1500, 450, { size: 34, weight: 700, color: COL.grayHi, align: 'center', alpha: popA(bt, 5.0, 0.4) });
    }
    BOARDS.forEach((b, i) => {
      const pre = bt < 4.5 ? (bt >= b.litAt && (i === 2 || bt < BOARDS[i + 1].litAt) ? 1 : 0.15) : 1;
      const hi = bt < 4.5 ? lerp(0.15, 1, clamp(pre)) : 1;
      let v = null;
      if (bt >= 4.5) v = bt < 8.5 ? roll(bt, 4.5 + i * 0.12, 0.4, 0, b.v1) : roll(bt, 8.6 + i * 0.12, 0.5, b.v1, b.v2);
      const lose = i === 2 && bt >= 4.5 && bt < 8.6;
      const win = i === 1 && bt >= 4.5;
      drawScoreBoard(b.x, BOARD_TOP, b.label, v, {
        h: BOARD_H, tone: b.tone, hi,
        numColor: win ? COL.yellowHi : lose ? COL.pink : COL.cream, glow: win ? 16 : lose ? 10 : 0,
      });
    });
    // reactions under the boards (on the deck face)
    const lo = popA(bt, 5.0, 0.4) * (1 - seg(bt, 8.5, 8.9));
    if (lo > 0) txt('比没睡还差', 1750, 660, { size: 36, weight: 900, color: COL.pink, align: 'center', alpha: lo });
    const cs = popS(bt, 10.5, 0.6);
    if (cs > 0) withScale(1600, BOARD_TOP + 2, cs, () => okMark(1600, BOARD_TOP + 2, 28, seg(bt, 10.5, 11.2)));
    const wa = popA(bt, 10.5, 0.4);
    if (wa > 0) txt('一醒就好', 1500 + (1 - wa) * 16, 660, { size: 40, weight: 900, color: COL.yellow, align: 'center', alpha: wa, glow: 14 });
    const ra = popA(bt, 11.5, 0.4);
    if (ra > 0) txt('缓过来了', 1750 - (1 - ra) * 16, 660, { size: 36, weight: 900, color: COL.cream, align: 'center', alpha: ra });
    sourceNote('Tietzel & Lack 2001 · 12 名大学生 · 前一晚只睡约 5 小时', 1130, 984, { alpha: popA(bt, 13, 0.8) });
  });
}

// ---------- answer section 「睡 10 分钟」 (17–32): tags ①②③ rise as bubbles, the deep-sleep evidence in the water ----------
const TAGS = [
  { n: 1, s: '睡多久', at: 19.0 },
  { n: 2, s: '睡久了怎么办', at: 21.5 },
  { n: 3, s: '醒来先干嘛', at: 24.0 },
];
const TAG_Y = 505;
function tagSlots() {
  const ws = TAGS.map((tg) => bubbleTagWidth(tg.s));
  const gap = 30, total = ws.reduce((a, b) => a + b, 0) + gap * 2;
  let x = 1340 - total / 2;
  return ws.map((w) => { const c = x + w / 2; x += w + gap; return c; });
}
function drawAnswer(bt, t) {
  if (bt < 18 || bt > 33) return;
  const slots = tagSlots();
  TAGS.forEach((tg, i) => {
    if (bt < tg.at) return;
    const rise = EASE.out(seg(bt, tg.at, tg.at + 0.9));
    let x = slots[i], y = lerp(760, TAG_Y, rise);
    let sc = lerp(0.35, 1, EASE.back(clamp((bt - tg.at) / 0.9))), a = popA(bt, tg.at, 0.25);
    const hi = i === 0 ? win(bt, 29.0, 31, 0.3, 0.4) : 0;
    if (bt > 30.5) {
      const q = EASE.inOut(seg(bt, 30.5, 32.2));
      if (i === 0) { x = lerp(slots[0], 196, q); y = lerp(TAG_Y, 150, q); sc = lerp(1, 0.6, q); a = 1 - seg(bt, 31.6, 32.2); }
      else { sc = 1 - q * 0.3; a = 1 - seg(bt, 30.5, 31.3); }
    }
    if (rise < 1 && bt < 30) drawBubble(x - 60, y + 50, 10 * (1 - rise), 1 - rise);
    drawBubbleTag(x, y, tg.n, tg.s, { alpha: a, scale: sc, hi });
  });
  // evidence (12.4 s): Brooks & Lack 2006 table 4 — deep sleep (stages 3 + 4) inside a 30-min nap ~11.4 min, a 10-min nap 0.9 min
  const ea = popA(bt, 26.5, 0.5) * (1 - seg(bt, 30.5, 31.0));
  if (ea > 0) withAlpha(ea, () => {
    const rows = [
      { y: DEPTH.m10, at: 26.5, a: '睡 10 分钟', b: '深睡不到 1 分钟', c: COL.yellow },
      { y: DEPTH.m30, at: 27.5, a: '睡 30 分钟', b: '深睡约 11 分钟', c: COL.pink },
    ];
    for (const r of rows) {
      const ra = popA(bt, r.at, 0.4);
      if (ra <= 0) continue;
      withAlpha(ra, () => {
        ctx.save(); ctx.setLineDash([8, 8]);
        line(GX + 24, r.y, 640, r.y, rgba(r.c, 0.55), 2.5); ctx.restore();
        drawMiniMattress(700, r.y, 110, { color: r.c });
        txt(r.a, 780, r.y - 22, { size: 40, weight: 900, color: r.c });
        txt(r.b, 780, r.y + 24, { size: 36, weight: 900, color: COL.cream });
        lintPanel('evidence:' + r.a, 640, r.y - 48, 1090, r.y + 48);
      });
    }
    sourceNote('Brooks & Lack 2006 · 脑电测的深睡（慢波睡眠）', 640, 984, { alpha: popA(bt, 28.5, 0.6) });
  });
}

// ---------- main ----------
// mattress + figure; returns the figure's screen points (head, hands) for props
function heroParams(bt, t) {
  const mx = MAT_X(bt), my = MAT_Y(bt);
  const pose = POSE(bt);
  const lying = clamp(Math.abs(pose.rot || 0) / 90);
  const s = 0.8;
  const fig = {
    x: mx + lerp(-70, -15, lying), y: my - MAT.h / 2 + 3, s, dir: 1, style: 'A',
    pose: withHead(pose, headShake(bt)), face: faceAt(bt), alpha: 1,
  };
  return { mx, my, fig };
}

function renderFrame(t) {
  const bt = t / BEAT;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  drawBackground(t);
  drawPoolBack(t);
  const info = { t, bt, kid: false };

  if (typeof drawBehind === 'function') drawBehind(bt, t);
  drawDeck(t);

  const hp = heroParams(bt, t);
  if (typeof decorateHero === 'function') decorateHero(hp, bt, t);
  if (hp.matA !== 0) drawMattress(hp.mx, hp.my, { tilt: matTilt(bt), alpha: hp.matA ?? 1 });
  const figs = hp.figs || [hp.fig];
  let pts = null;
  for (const f of figs) {
    const r = drawFigure(f);
    if ((f.alpha ?? 1) >= 0.5) { pts = r; info.kid = true; }
    if (!pts) pts = r;
  }
  lintPanel('head:hero', pts.head[0] - 26, pts.head[1] - 28, pts.head[0] + 26, pts.head[1] + 28);
  drawPoolFront(t);

  if (typeof drawInWater === 'function') drawInWater(bt, t, pts, hp);
  if (bt < 17) drawOpening(bt, t);
  drawTitleBlock(bt, t);
  drawAnswer(bt, t);
  if (typeof drawSections === 'function') drawSections(bt, t, pts, hp);

  drawChapterBar(bt);
  window.__frameInfo = info;
}
