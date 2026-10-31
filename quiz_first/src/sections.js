// sections.js — the three rounds on the quiz stage (第 1 / 2 / 3 关, 32–128) and the summary (照着做, 128–160).
// Numbers: six/facts/01_quiz_first.md. ① only the asked content gains (St. Hilaire 2024 g = 0.54 vs 0.04; King-Shepard 2025).
// ② Richland, Kornell & Kao 2009 Exp 4: pretest 10% right; one week later 55% vs 45% for extended reading (same 10 minutes;
// only the items missed on the pretest scored). ③ St. Hilaire & Carpenter 2020 Exp 3: items whose answer was found and
// written down 84%, control 54%, items not found 50%. Summary: ManyClasses 2 (preprint) 73.7% vs 68.8% in 30 real classes.
const S2_X = 860;   // ② stands here (used by ① for the walk over)
const ink = (s) => ({ s, color: INK });
const hl = (s, color = AMBER) => ({ s, color });

// ---------- the hanging screen of the rounds ----------
const ROUNDS = [
  { from: 31.4, to: 64, chip: '第 1 关', title: [{ s: '挑 ' }, { s: '5 道', color: COL.yellow }, { s: '重点题' }],
    line2: [{ s: '只有' }, { s: '问到的', color: COL.yellow }, { s: '，才记得更牢' }], en: 'Pick 5 key questions. Only what is asked sticks.' },
  { from: 64, to: 96, chip: '第 2 关', title: [{ s: '先猜，' }, { s: '不翻书', color: COL.yellow }],
    line2: [{ s: '猜错', color: COL.pink }, { s: '没关系' }], en: 'Guess first, no peeking. Wrong is fine.' },
  { from: 96, to: 127.2, chip: '第 3 关', title: [{ s: '带着题读，' }, { s: '找到就圈', color: COL.yellow }],
    line2: [{ s: '再和自己猜的' }, { s: '对一下', color: COL.yellow }], en: 'Read with your questions. Circle each answer.' },
];
function drawRoundScreen(bt) {
  if (bt < 31.4 || bt > 127.6) return;
  const drop = seg(bt, 31.5, 32.3), out = 1 - seg(bt, 126.5, 127.0);
  for (const r of ROUNDS) {
    const a = (r.from < 32 ? 1 : seg(bt, r.from, r.from + 0.5)) * (r.to > 127 ? 1 : 1 - seg(bt, r.to - 0.5, r.to));
    if (a <= 0 || bt < r.from || bt > r.to) continue;
    drawHangingScreen({ alpha: a * out, drop, chip: r.chip, title: r.title, line2: r.line2, en: r.en, enP: seg(bt, r.from + 0.6, r.from + 3.2), bt });
  }
}

// ---------- ① 挑 5 道重点题: pull 5 cards out of the question bank, put the rest back ----------
const S1_X = 590, BOX = { x: 720, top: 640 }, PULL = [36, 38, 40, 42, 44], SLOT_Y = 440;
const slotX = (k) => 900 + k * 175;
function heroStep1(bt) {
  const st = { x: bt < 62 ? S1_X : walkX(bt, 62, 64, S1_X, S2_X), y: STAGE_Y, s: 1, prop: null };
  const at = (X, Y, base = {}) => () => armTo({ ...STANDP, ...base }, X, Y, st);
  const keys = [[32, STANDP], [34.5, { ...STANDP, head: 10 }]];
  for (const P of PULL) {
    keys.push([P - 1.0, at(BOX.x - 24, BOX.top - 44, { lean: 8, head: 16 })], [P - 0.5, at(BOX.x - 24, BOX.top - 36, { lean: 8, head: 16 })],
      [P, at(BOX.x - 80, BOX.top - 214, { lean: 2, head: -8 }), 'out']);
  }
  keys.push([45.0, at(BOX.x + 20, BOX.top - 70, { lean: 7, head: 14 })], [46.0, at(BOX.x + 20, BOX.top - 16, { lean: 9, head: 16 }), 'in'],
    [46.5, STANDP], [48.5, STANDP], [49.0, POSES.point], [51.5, POSES.point], [52.0, STANDP], [56, STANDP], [57, thinkPose], [59.5, thinkPose],
    [60.0, at(S1_X + 118, 600, { head: 4 })], [62, at(S1_X + 118, 600, {})], [64, at(S2_X + 118, 600, {})]);
  st.pose = walkOver(PT(keys)(bt), bt, 62, 64, 0.8);
  st.face = FT([[32, 'calm'], [48, 'happy'], [56, 'calm']])(bt);
  st.pointF = bt > 48.8 && bt < 51.8;
  if (bt >= 60.5) st.prop = { type: 'fan' };
  return st;
}
const handAt = (fn, b) => figureHands(fn(b)).handF;
const PULL_HAND = PULL.map((P) => handAt(heroStep1, P));
function drawStep1Back(bt) {
  if (bt < 31.8 || bt > 64.5) return;
  const out = 1 - seg(bt, 63.0, 63.8);
  const left = 10 - PULL.filter((P) => bt >= P - 0.5).length;
  withAlpha(popA(bt, 32.0, 0.6) * out, () => drawCardBox(BOX.x, BOX.top, { n: left, lid: EASE.inOut(seg(bt, 45.5, 46.0)), lift: 0 }));
  // the row of the 5 picked cards; they fly into his hand at 60–60.8
  const fanHand = handAt(heroStep1, 60.5);
  PULL.forEach((P, k) => {
    if (bt < P) return;
    const f = EASE.out(seg(bt, P, P + 0.6)), [hx, hy] = PULL_HAND[k];
    let x = lerp(hx, slotX(k), f), y = lerp(hy - 30, SLOT_Y, f) - 150 * Math.sin(Math.PI * f) * (k > 0), sc = lerp(0.6, 1, f);
    const g = EASE.inOut(seg(bt, 60, 60.5));
    if (g > 0) { x = lerp(slotX(k), fanHand[0], g); y = lerp(SLOT_Y, fanHand[1] - 30, g); sc = lerp(1, 0.6, g); }
    if (bt >= 60.5) return;
    withScale(x, y, sc, () => drawQCard(x, y, { n: k + 1, star: true, plain: g > 0 || (f < 1 && k > 0), glow: win(bt, 48, 60, 0.3, 0.6), mark: bt >= 48 ? 'ok' : null, markP: seg(bt, 48 + k * 0.1, 48.6 + k * 0.1) }));
  });
}
function drawStep1Front(bt, st, hands) {
  if (bt < 32 || bt > 64.5) return;
  const out = 1 - seg(bt, 63.0, 63.8);
  // the card on its way up in his hand
  PULL.forEach((P) => { if (bt >= P - 0.5 && bt < P) drawQCard(hands.handF[0], hands.handF[1] - 30, { w: 90, h: 62, n: 0, star: true, plain: true }); });
  withAlpha(out, () => {
    const la = popA(bt, 48, 0.4);
    if (la > 0) rich([{ s: '问到的：' }, { s: '记得更牢', color: COL.yellow, glow: 14 }], slotX(2), 548, { size: 44, weight: 900, align: 'center', alpha: la });
    const ba = popA(bt, 50, 0.4);
    if (ba > 0) withAlpha(ba, () => {
      line(842, 676, 826, 676, COL.grayHi, 4);
      ctx.save(); ctx.fillStyle = COL.grayHi; ctx.beginPath(); ctx.moveTo(818, 676); ctx.lineTo(834, 666); ctx.lineTo(834, 686); ctx.closePath(); ctx.fill(); ctx.restore();
      rich([{ s: '没问到的：', color: COL.grayHi }, { s: '不会多记住', color: COL.cream }], 856, 676, { size: 38, weight: 900 });
    });
    const ta = popA(bt, 52, 0.4);
    if (ta > 0) txt('建议：从课后题、老师划的重点里挑', 856, 760, { size: 36, weight: 700, color: COL.grayHi, alpha: ta });
    sourceNote('只有问到的才记得更牢：两项元分析（St. Hilaire 等 2024 · King-Shepard 等 2025）', 110, 988, { alpha: popA(bt, 54, 0.6), size: 24 });
  });
}

// ---------- ② 先猜，不翻书: write a guess on the paper's own example item, it is wrong, keep going ----------
const FLIPS2 = [72, 74, 76, 78], CARD2_SMALL = { x: 470, y: 400, s: 0.62 };
const GUESS_AT = [EX.x - EX.w / 2 + 58, EX.y - EX.h / 2 + 304];   // where the guess is written (screen)
function heroStep2(bt) {
  const st = { x: S2_X, y: STAGE_Y, s: 1, prop: null };
  const at = (X, Y, base = {}) => () => armTo({ ...STANDP, ...base }, X, Y, st);
  const scrib = (b0, b1, x0, x1) => (b) => {
    const p = seg(b, b0, b1);
    return armTo({ ...STANDP, lean: 4, head: 10 }, lerp(x0, x1, p) + 7 * Math.sin(b * Math.PI * 7), GUESS_AT[1] - 30 + 7 * Math.cos(b * Math.PI * 7), st);
  };
  const keys = [[64, at(S2_X + 118, 600, {})], [64.5, at(S2_X + 130, 560, { head: -4 })], [65.5, STANDP],
    [66.0, scrib(66.0, 68.5, GUESS_AT[0] - 40, GUESS_AT[0] + 40)], [68.5, scrib(66.0, 68.5, GUESS_AT[0] - 40, GUESS_AT[0] + 40)],
    [69.0, { ...STANDP, lean: -6, head: -10 }, 'out'], [69.5, { ...STANDP, lean: -4 }], [70.0, POSES.shrug], [71.5, POSES.shrug], [72.0, STANDP]];
  FLIPS2.forEach((b) => keys.push([b + 0.5, scrib(b + 0.5, b + 1.4, GUESS_AT[0] - 40, GUESS_AT[0] + 40)],
    [b + 1.4, scrib(b + 0.5, b + 1.4, GUESS_AT[0] - 40, GUESS_AT[0] + 40)], [b + 1.6, { ...STANDP, lean: -2, head: -4 }]));
  keys.push([80.0, STANDP], [85.5, STANDP], [86.0, { ...POSES.cheer, lift: 0 }, 'out'], [87.5, { ...POSES.cheer, lift: 0 }], [88.5, POSES.point], [91.5, POSES.point], [92.5, STANDP]);
  st.pose = PT(keys)(bt);
  st.face = FT([[64, 'calm'], [69.0, 'wow'], [69.5, 'happy'], [72, 'calm'], [86, 'happy']])(bt);
  st.pointF = bt > 88.3 && bt < 92;
  if (bt < 64.5) st.prop = { type: 'fan' };
  else if (bt >= 65.5 && bt < 80.5) st.prop = { type: 'marker' };
  return st;
}
// the example card: big at EX, the other questions flip by, then it shrinks to the top left (kept for ③)
function card2State(bt) {
  let qn = 1, sx = 1;
  for (const [k, b] of FLIPS2.entries()) { if (bt >= b + 0.15) qn = k + 2; if (bt >= b && bt < b + 0.3) sx = Math.abs(Math.cos(Math.PI * seg(bt, b, b + 0.3))); }
  if (bt >= 80.15) qn = 1;
  if (bt >= 80 && bt < 80.3) sx = Math.abs(Math.cos(Math.PI * seg(bt, 80, 80.3)));
  const fb = FLIPS2.find((b) => bt >= b && bt < b + 2);
  const shrink = EASE.inOut(seg(bt, 80.5, 81.5));
  return {
    qn, sx, guess: '红色？', guessP: seg(bt, 66.0, 68.0), wrong: seg(bt, 69, 69.45),
    scrib: fb !== undefined ? seg(bt, fb + 0.5, fb + 1.4) : 0, xMark: fb !== undefined ? seg(bt, fb + 1.5, fb + 1.85) : 0,
    x: lerp(EX.x, CARD2_SMALL.x, shrink), y: lerp(EX.y, CARD2_SMALL.y, shrink), scale: lerp(1, CARD2_SMALL.s, shrink),
  };
}
const SB2 = { a: [1170, 700], b: [1500, 700] }, MQ2 = [1335, 520];
function drawStep2Back(bt) {
  if (bt < 64.3 || bt >= 96) return;
  const pop = popS(bt, 64.5, 0.7), fanHand = handAt(heroStep2, 64.5);
  const c = card2State(bt);
  if (bt < 65.2) {
    const f = EASE.out(seg(bt, 64.5, 65.2));
    drawExampleCard({ ...c, x: lerp(fanHand[0], EX.x, f), y: lerp(fanHand[1], EX.y, f), scale: lerp(0.35, 1, f) * Math.min(1, pop + 0.4) });
  } else drawExampleCard(c);
  // one week later: two scoreboards under the marquee
  const out = 1 - seg(bt, 94.5, 95.5), A = popA(bt, 82, 0.5) * out;
  if (A <= 0) return;
  withAlpha(A, () => {
    drawMarquee(MQ2[0], MQ2[1], ['一周后，再考这几道'], 0, { turns: 3 * EASE.inOut(seg(bt, 82, 83.2)) + bt * 0.05, flash: win(bt, 82, 83.2, 0.05, 0.9), w: 600 });
    const va = bt < 82.5 ? null : `${Math.round(roll(bt, 82.5, 83.3, 0, 55))}%`, vb = bt < 83.0 ? null : `${Math.round(roll(bt, 83.0, 83.8, 0, 45))}%`;
    drawScoreboard(SB2.a[0], SB2.a[1], { label: '先猜再读', icon: 'card', color: COL.yellow, value: va, glow: 1 + seg(bt, 86, 86.5) * 0.8,
      sub: popA(bt, 83.5, 0.3) > 0 ? [{ s: '先猜只对 ' }, { s: '10%', color: COL.pink }] : null });
    drawScoreboard(SB2.b[0], SB2.b[1], { label: '一直看书', icon: 'book', color: COL.cyan, value: vb, dim: 0.55 * seg(bt, 86, 86.7),
      sub: popA(bt, 84.0, 0.3) > 0 ? '多看 2 分钟' : null });
    const cs = popS(bt, 86, 0.6);
    if (cs > 0) withScale(SB2.a[0] + 128, SB2.a[1] - 112, cs, () => okMark(SB2.a[0] + 128, SB2.a[1] - 112, 30, seg(bt, 86, 86.7)));
    sparkleBurst(SB2.a[0], SB2.a[1] + 20, seg(bt, 86, 87.5));
  });
}
function drawStep2Front(bt) {
  if (bt < 64 || bt > 96) return;
  const out = 1 - seg(bt, 94.5, 95.5);
  const na = popA(bt, 88, 0.5) * out;
  if (na > 0) txt('总时间一样（10 分钟）· 只算先猜时答错的题', MQ2[0], 872, { size: 34, weight: 700, color: COL.grayHi, align: 'center', alpha: na });
  sourceNote('Richland 等 2009 · 实验 4 · 美国大学生，读一篇讲全色盲画家的文章', 110, 988, { alpha: popA(bt, 90, 0.6) * out, size: 24 });
}

// ---------- ③ 带着题读，找到就圈: walk along the big page, circle the answer, check it against the guess ----------
const S3_X0 = 840, S3_X1 = 1615, WALK3 = [98.5, 103.5], TURN3 = 103.5;
// he walks the whole page with the highlighter up (the lit line follows its tip), passes the answer line, turns round
// at 103.5 and circles 「黑色」 from the right, so his body never covers the answer; facing left he then checks his guess
// (top left) and points at the scoreboards (left)
function heroStep3(bt) {
  const st = { x: bt < WALK3[0] ? S3_X0 : walkX(bt, WALK3[0], WALK3[1], S3_X0, S3_X1), y: STAGE_Y, s: 1, prop: null, dir: bt >= TURN3 ? -1 : 1 };
  const [ax, ay] = pageAnswerXY();
  const carry = (b) => armTo({ ...STANDP, head: 6 }, st.x + 112 * st.dir, scan3Y(b) + 36, st);
  const circ = (b) => {
    const th = -Math.PI * 0.6 + TAU * 1.04 * EASE.inOut(seg(b, 104.0, 105.5));
    return armTo({ ...STANDP, lean: 4, head: 8 }, ax + 72 * Math.cos(th) + 40, ay + 38 * Math.sin(th) + 34, st);
  };
  const keys = [[96.5, STANDP], [97.5, carry], [103.0, carry], [103.5, STANDP], [104.0, circ], [105.5, circ], [106.0, { ...STANDP, head: -6 }],
    [106.5, { ...POSES.cheer, lift: 0 }, 'out'], [108.0, { ...POSES.cheer, lift: 0 }], [109.0, STANDP], [114.5, STANDP],
    [115.0, { ...POSES.point, head: 4 }], [119.5, { ...POSES.point, head: 4 }], [120.0, STANDP]];
  st.pose = walkOver(PT(keys)(bt), bt, WALK3[0], WALK3[1], 0.75);
  st.face = FT([[96, 'calm'], [105.5, 'wow'], [106.5, 'happy']])(bt);
  if (bt >= 96.5 && bt < 106.5) st.prop = { type: 'highlighter' };
  st.pointF = bt > 114.8 && bt < 119.8;
  return st;
}
// height of the lit line while he walks: from the first line down to the answer line, which he passes at ~102
function scan3Y(b) { return lerp(PAGE.y - PAGE.h / 2 + 172, pageAnswerXY()[1], EASE.inOut(seg(b, 99, 102))); }
const SB3 = { a: [330, 725], b: [650, 725] };
function drawStep3Back(bt) {
  if (bt < 96 || bt > 128) return;
  const out = 1 - seg(bt, 126.5, 127.3);
  const pa = popA(bt, 96.0, 0.6) * out;
  const [ax, ay] = pageAnswerXY();
  const scan = bt > 99 && bt < 103.4 ? lerp(0, 2, EASE.inOut(seg(bt, 99, 102))) : -1;
  drawBookPage({ alpha: pa, found: seg(bt, 104.0, 105.5), scan });
  // the guess card from ② (top left): strike 红色？ and write 黑色 ✓
  const c = card2State(81.6);
  drawExampleCard({ ...c, alpha: out, fix: seg(bt, 107.0, 109.2) });
  // the result on the two scoreboards
  const A = popA(bt, 110, 0.5) * out;
  if (A > 0) withAlpha(A, () => {
    const va = bt < 110.5 ? null : `${Math.round(roll(bt, 110.5, 111.3, 0, 84))}%`, vb = bt < 111.0 ? null : `${Math.round(roll(bt, 111.0, 111.8, 0, 54))}%`;
    drawScoreboard(SB3.a[0], SB3.a[1], { label: '找到答案的题', color: COL.yellow, value: va, glow: 1 + seg(bt, 114, 114.5) * 0.8,
      sub: popA(bt, 112, 0.3) > 0 ? '看课时写下了答案' : null, subColor: COL.cream });
    drawScoreboard(SB3.b[0], SB3.b[1], { label: '对照组', color: COL.cyan, value: vb, dim: 0.55 * seg(bt, 114, 114.7) });
    const cs = popS(bt, 114, 0.6);
    if (cs > 0) withScale(SB3.a[0] + 128, SB3.a[1] - 112, cs, () => okMark(SB3.a[0] + 128, SB3.a[1] - 112, 30, seg(bt, 114, 114.7)));
    sparkleBurst(SB3.a[0], SB3.a[1] + 20, seg(bt, 114, 115.5));
  });
  if (bt >= 105.5 && bt < 107.3) sparkleBurst(ax, ay, seg(bt, 105.5, 107.3));
}
function drawStep3Front(bt) {
  if (bt < 96 || bt > 128) return;
  const out = 1 - seg(bt, 126.5, 127.3);
  const na = popA(bt, 116, 0.5) * out;
  if (na > 0) txt('没找到答案的题：50%，和对照组差不多', 490, 900, { size: 34, weight: 700, color: COL.grayHi, align: 'center', alpha: na });
  sourceNote('St. Hilaire & Carpenter 2020 · 大学生看 30 分钟视频课', 110, 988, { alpha: popA(bt, 118, 0.6) * out, size: 24 });
}

// ---------- 照着做 (128–160): the big screen with three flip panels, built while he acts each step ----------
const SUM = { x: 640, y: 44, w: 1160, h: 812 }, PANEL = { x: 680, w: 1080, h: 132, y: [212, 364, 516] }, FLIPS = [130, 134, 138];
const SUM_ITEMS = [
  [[ink('挑 '), hl('5 道'), ink('重点题')], '课后题、老师划的重点'],
  [[ink('先猜 '), hl('2 分钟'), ink('，不翻书')], '猜错没关系'],
  [[ink('带着题读，'), hl('找到就圈')], '再和自己猜的对一下'],
];
const SUM_X = 360;
function heroSummary(bt) {
  const st = { x: SUM_X, y: STAGE_Y, s: 1, prop: null };
  const at = (X, Y, base = {}) => () => armTo({ ...STANDP, ...base }, X, Y, st);
  const air = (b0, b1) => (b) => armTo({ ...STANDP, lean: 3, head: 4 }, SUM_X + 132 + 10 * Math.sin(b * Math.PI * 7), 590 + 8 * Math.cos(b * Math.PI * 7), st);
  const circle2 = (b) => { const th = TAU * 1.1 * EASE.inOut(seg(b, 137.5, 139.5)); return armTo({ ...STANDP, head: 2 }, SUM_X + 120 + 46 * Math.cos(th), 560 + 30 * Math.sin(th), st); };
  const T = PT([[128.5, STANDP], [129.5, at(SUM_X + 118, 580, { head: -4 })], [132.5, at(SUM_X + 118, 580, { head: -4 })], [133.0, air(133.0, 136.5)],
    [136.5, air(133.0, 136.5)], [137.5, circle2], [139.5, circle2], [140.5, STANDP], [146, STANDP], [146.5, { ...STANDP, head: -14 }], [148.5, { ...STANDP, head: -10 }],
    [149.5, POSES.point], [152.5, POSES.point], [153.5, STANDP], [154.0, POSES.cheer, 'out'], [160, POSES.cheer]]);
  st.pose = T(bt);
  st.pose.lift = hop(bt, 154.0, 1.0, 70) + hop(bt, 156.0, 1.0, 60);
  if (bt > 141.5 && bt < 144.5) st.pose.head = 6 * Math.sin((bt - 141.5) * Math.PI * 2) * (1 - seg(bt, 143.5, 144.5));
  st.face = FT([[128, 'calm'], [130, 'happy'], [141.5, 'calm'], [144.5, 'happy'], [146.0, 'wow'], [147.5, 'happy']])(bt);
  st.pointF = bt > 149.3 && bt < 152.8;
  if (bt >= 129.5 && bt < 132.5) st.prop = { type: 'fan' };
  else if (bt >= 133 && bt < 136.5) st.prop = { type: 'marker' };
  else if (bt >= 137.5 && bt < 140.5) st.prop = { type: 'highlighter' };
  return st;
}
function drawSummaryBack(bt) {
  if (bt < 127.5) return;
  const drop = seg(bt, 127.5, 128.3), fl = win(bt, 146, 148.6, 0.05, 1.8);
  const y = SUM.y - (1 - EASE.out(drop)) * 60;
  withAlpha(seg(bt, 127.5, 128.0), () => {
    line(SUM.x + 160, 0, SUM.x + 160, y, '#5c6887', 3); line(SUM.x + SUM.w - 160, 0, SUM.x + SUM.w - 160, y, '#5c6887', 3);
    lintPanel('大屏', SUM.x, y, SUM.w, SUM.h);
    ctx.save(); ctx.shadowColor = fl > 0 ? COL.yellow : COL.cyan; ctx.shadowBlur = 26 + 40 * fl;
    rrect(SUM.x, y, SUM.w, SUM.h, 26, '#081129', fl > 0 ? lerpColor('#8fe8f8', '#ffd57e', fl) : 'rgba(143,232,248,0.85)', 3.5 + 3 * fl); ctx.restore();
    const cw = measure('通关', 34, 900) + 44;
    ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 30 * fl;
    rrect(SUM.x + 40, y + 34, cw, 56, 28, COL.yellow); ctx.restore();
    txt('通关', SUM.x + 40 + cw / 2, y + 63, { size: 34, weight: 900, color: '#0b1736', align: 'center' });
    txt('学新一章，这样学', SUM.x + 70 + cw, y + 64, { size: 66, weight: 900, color: COL.cream });
    typeText('Before a new chapter: pick, guess, read.', seg(bt, 128.6, 131), SUM.x + 46, y + 132, { size: 28, weight: 500, fam: 'mono', color: COL.cyan }, bt);
    const dy = y - SUM.y;
    SUM_ITEMS.forEach(([main, sub], i) => drawFlipPanel(PANEL.x, PANEL.y[i] + dy, PANEL.w, PANEL.h, i + 1, main, sub, seg(bt, FLIPS[i], FLIPS[i] + 0.6), { hi: fl }));
    const wa = popA(bt, 142, 0.35);
    if (wa > 0) withAlpha(wa, () => withScale(1220, 712 + dy, 0.9 + 0.1 * popS(bt, 142, 0.6), () => {
      lintPanel('粉色提醒', PANEL.x, 674 + dy, PANEL.w, 78);
      rrect(PANEL.x, 674 + dy, PANEL.w, 78, 16, 'rgba(255,111,158,0.12)', 'rgba(255,111,158,0.8)', 2.5);
      txt('没问到的，不会多记住', PANEL.x + 34, 714 + dy, { size: 42, weight: 900, color: COL.cream });
      txt('只对问到的题有用', PANEL.x + PANEL.w - 34, 716 + dy, { size: 28, weight: 700, color: COL.pink, align: 'right' });
    }));
    const fa = popA(bt, 144, 0.6);
    if (fa > 0) {
      txt('仅供参考：多是大学生读短文；30 个真实班级平均多对约 5 个百分点（预印本）', PANEL.x, 790 + dy, { size: 26, weight: 700, color: COL.gray, alpha: fa });
      txt('Pan & Sana 2021 · Richland 2009 · St. Hilaire 2024 · ManyClasses 2', PANEL.x, 826 + dy, { size: 22, weight: 500, fam: 'mono', color: COL.grayDim, alpha: fa });
    }
  });
  if (fl > 0) for (let i = 0; i < 3; i++) sparkleBurst(PANEL.x + 180 + i * 360, PANEL.y[i] + 66, seg(bt, 146 + i * 0.25, 147.6 + i * 0.25));
}

// ---------- wiring ----------
function drawSectionsBack(bt, t, st) {
  drawRoundScreen(bt);
  drawStep1Back(bt);
  drawStep2Back(bt);
  drawStep3Back(bt);
  drawSummaryBack(bt);
}
function drawSectionsFront(bt, t, st, hands) {
  drawStep1Front(bt, st, hands);
  drawStep2Front(bt);
  drawStep3Front(bt);
}
