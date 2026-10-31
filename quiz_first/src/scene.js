// scene.js — timeline in beats (bt). 128 BPM -> 1 beat = 0.46875 s; 160 beats = 75 s. Beat grid of plan.md:
// frame 0 the question + he is already moving; reveal 1 at beat 4.5 (2.11 s, held 4 beats); reveal 2 at 8.5 (3.98 s);
// check 10.5 (4.92 s) / other side 11.5 (5.39 s); source 13 (6.1 s); answer at 17 (8.0 s); evidence 26.5 (12.4 s);
// rounds at 32 / 64 / 96 (15 / 30 / 45 s); summary 128–160 (60–75 s), ends on the last bar.
// Numbers: six/facts/01_quiz_first.md (Pan & Sana 2021 Exp 4, tables 1–2: 31% vs 57% on the first test, 75% vs 53% 48 h
// later; St. Hilaire et al. 2024 meta-analysis g = 0.54 / 0.04).
const TOTAL_BEATS = 160;

// ---------- title block (0–31) ----------
function drawTitleBlock(bt) {
  const outA = 1 - EASE.out(seg(bt, 30.5, 31.4)), dy = -40 * EASE.in(seg(bt, 30.5, 31.4));
  if (outA <= 0) return;
  withAlpha(outA, () => {
    const e = EASE.inOut(seg(bt, 16.5, 17.5));
    const ans = seg(bt, 10.5, 11.3);
    ctx.save(); ctx.beginPath(); ctx.rect(0, 64 + dy, W, 144); ctx.clip();
    if (e < 1) txt('先看书', 960, 140 + dy - e * 80, { size: 128, weight: 900, align: 'center', alpha: 1 - e,
      color: lerpColor(COL.cyan, '#6f7b99', ans), glow: 22 * (1 - ans) });
    if (e > 0) txt('学新一章', 960, 140 + dy + (1 - e) * 80, { size: 104, weight: 900, color: COL.cream, align: 'center', alpha: e });
    ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.rect(0, 208 + dy, W, 150); ctx.clip();
    if (e < 1) rich([{ s: '还是' }, { s: '先做题', color: COL.yellow, glow: 26 + 20 * ans }, { s: '？' }], 960, 284 + dy - e * 150,
      { size: 142, weight: 900, align: 'center', alpha: 1 - e });
    if (e > 0) rich([{ s: '先猜几道题，再看书', color: COL.yellow, glow: 30 }], 960, 284 + dy + (1 - e) * 150, { size: 142, weight: 900, align: 'center', alpha: e });
    ctx.restore();
    const en1 = 'Read first, or quiz first?', en2 = 'Guess a few questions first, then read.';
    const second = bt >= 17, s = second ? en2 : en1;
    const fw = measure(s, 34, 500, 'mono');
    const p = second ? seg(bt, 17.2, 20) : lerp(5 / en1.length, 1, seg(bt, 0, 2.4));
    typeText(s, p, 960 - fw / 2, 386 + dy, { size: 34, weight: 500, fam: 'mono', color: COL.cyan, keepCursor: true }, bt);
  });
}

// ---------- opening (0–17): question card, buzzer, two scoreboards, marquee ----------
const CONTACTS = [[4.5, 'x'], [5.5, 'x'], [6.5, 'x'], [8.5, 'ok'], [9.5, 'ok']];
const SB = { quiz: [1275, 690], read: [1595, 690] }, MQ = [1435, 498];
function buzzerState(bt) {
  let press = 0, flash = 0, col = COL.pink;
  for (const [c, r] of CONTACTS) {
    if (bt >= c && bt < c + 0.45) { press = Math.max(press, 1 - seg(bt, c + 0.12, c + 0.42)); flash = Math.max(flash, 1 - seg(bt, c, c + 0.45)); col = r === 'x' ? COL.pink : COL.yellow; }
  }
  return { press, flash, flashColor: col };
}
// the card on the stand: three questions answered wrong (4.5 / 5.5 / 6.5), 48 h later the same set right (8.5 / 9.5)
function quizState(bt) {
  const flips = [[5.0, 2], [6.0, 3], [8.0, 1], [9.0, 2]];
  let qn = 1, sx = 1;
  for (const [b, n] of flips) {
    if (bt >= b + 0.15) qn = n;
    if (bt >= b && bt < b + 0.3) sx = Math.abs(Math.cos(Math.PI * seg(bt, b, b + 0.3)));
  }
  const opt = ['idle', 'idle', 'idle', 'idle'], focus = [0, 0, 0, 0];
  if (bt < 4.5) for (let i = 0; i < 4; i++) focus[i] = win(bt, i + 0.5 - 0.5 * (i === 0), i + 1.5, 0.15, 0.4);
  if (bt >= 4.5 && bt < 5.15) opt[1] = 'wrong';
  if (bt >= 5.5 && bt < 6.15) opt[2] = 'wrong';
  if (bt >= 6.5 && bt < 8.15) opt[0] = 'wrong';
  if (bt >= 8.5 && bt < 9.15) opt[3] = 'right';
  if (bt >= 9.5) opt[1] = 'right';
  return { qn, sx, opt, focus };
}
const roll = (bt, a, b, v0, v1) => lerp(v0, v1, EASE.out(seg(bt, a, b)));
function drawOpeningBack(bt, t, st, hands) {
  if (bt > 17.3) return;
  const A = 1 - seg(bt, 15.5, 16.5);
  // the stand with the question card; the card flies into his hand at 16.6–17.2
  const q = quizState(bt);
  const fly = EASE.inOut(seg(bt, 16.5, 17.0));
  if (fly <= 0) drawQuizStand({ ...q });
  else if (bt < 17.0) {
    const [hx, hy] = hands.handF;
    withAlpha(1 - fly, () => drawQuizStand({ ...q, card: false }));
    drawQuizStand({ ...q, cx: lerp(QSTAND.x, hx + 30, fly), cy: lerp(QSTAND.y, hy - 20, fly), scale: lerp(1, 0.34, fly), stand: 0, plain: fly > 0.5 });
  }
  if (A <= 0) return;
  withAlpha(A, () => {
    drawBuzzer(BUZ.x, BUZ.top, buzzerState(bt));
    // marquee: setup -> first test -> the hour counter rolls to 48
    const idx = KB([[0, 0], [4.5, 0], [5.0, 1, 'out'], [8.5, 1], [9.0, 2, 'out']])(bt);
    const n48 = Math.round(48 * EASE.inOut(seg(bt, 8.6, 9.6)));
    const flash = Math.max(win(bt, 4.5, 5.4, 0.05, 0.8), win(bt, 8.5, 9.6, 0.05, 1.0));
    drawMarquee(MQ[0], MQ[1], ['同一篇短文 · 8 道题', '第一次做这 8 道题', () => `${n48} 小时后，再考这 8 道`], idx,
      { turns: bt * 0.05 + 4 * EASE.inOut(seg(bt, 8.5, 9.6)), flash });
    // scoreboards
    const vq = bt < 4.5 ? null : bt < 8.6 ? roll(bt, 4.5, 5.3, 0, 31) : roll(bt, 8.6, 9.6, 31, 75);
    const vr = bt < 4.6 ? null : bt < 8.6 ? roll(bt, 4.6, 5.4, 0, 57) : roll(bt, 8.6, 9.4, 57, 53);
    const okA = popA(bt, 10.5, 0.3);
    drawScoreboard(SB.quiz[0], SB.quiz[1], { label: '先做题', icon: 'card', color: COL.yellow, value: vq === null ? null : `${Math.round(vq)}%`,
      glow: 1 + seg(bt, 10.5, 11) * 0.8, sub: okA > 0 ? [{ s: '反超', color: COL.yellow, alpha: okA }] : null });
    drawScoreboard(SB.read[0], SB.read[1], { label: '先看书', icon: 'book', color: COL.cyan, value: vr === null ? null : `${Math.round(vr)}%`,
      dim: 0.55 * seg(bt, 10.5, 11.2), sub: popA(bt, 11.5, 0.3) > 0 ? '57% → 53%' : null, subColor: COL.grayHi });
    const cs = popS(bt, 10.5, 0.6);
    if (cs > 0) withScale(SB.quiz[0] + 128, SB.quiz[1] - 112, cs, () => okMark(SB.quiz[0] + 128, SB.quiz[1] - 112, 30, seg(bt, 10.5, 11.2)));
    sparkleBurst(SB.quiz[0], SB.quiz[1] + 20, seg(bt, 10.5, 12));
  });
}
function drawOpeningFront(bt) {
  if (bt > 17.3) return;
  const A = 1 - seg(bt, 15.5, 16.5);
  const ca = popA(bt, 5.0, 0.4) * (1 - seg(bt, 8.4, 8.9));
  if (ca > 0) txt('四选一，蒙也有 25%', MQ[0], 862, { size: 34, weight: 700, color: COL.grayHi, align: 'center', alpha: ca * A });
  sourceNote('Pan & Sana 2021 · 美国大学生 · 同一篇短文、同一套题，只换先后', 110, 988, { alpha: A * popA(bt, 13, 0.8), size: 24 });
}

// ---------- answer section 「先猜再读」 (17–32): page, tags ①②③, evidence card ----------
const TAGS = [
  { n: 1, s: '挑哪些题', y: 520, at: 19.0 },
  { n: 2, s: '怎么猜', y: 630, at: 21.5 },
  { n: 3, s: '怎么读', y: 740, at: 24.0 },
];
const ANS_PAGE = { x: 1585, y: 655, w: 380, h: 470 };
function drawAnswerBack(bt) {
  if (bt < 17.5 || bt > 31.6) return;
  const a = popA(bt, 18.0, 0.8) * (1 - seg(bt, 30.5, 31.4));
  const dy = (1 - EASE.out(seg(bt, 18.0, 18.9))) * 60;
  drawBookPage({ ...ANS_PAGE, y: ANS_PAGE.y + dy, alpha: a, text: false });
}
function drawAnswerFront(bt, st, hands) {
  if (bt < 18.5 || bt > 31.6) return;
  const out = 1 - seg(bt, 30.5, 31.3);
  TAGS.forEach((tg, i) => {
    if (bt < tg.at) return;
    const fly = EASE.out(seg(bt, tg.at, tg.at + 0.8));
    const ox = st.x + 10, oy = st.y - 210;   // out of his pocket
    const x = lerp(ox, 300, fly), y = lerp(oy, tg.y, fly);
    drawCardTag(x, y, tg.n, tg.s, { alpha: popA(bt, tg.at, 0.25) * out, scale: popS(bt, tg.at, 0.8), hi: i === 0 ? win(bt, 29.0, 31, 0.4, 0.4) : 0 });
  });
  // evidence card (12.4 s): the meta-analysis
  const ea = popA(bt, 26.5, 0.5) * out;
  if (ea > 0) withAlpha(ea, () => withScale(760, 620, 0.92 + 0.08 * popS(bt, 26.5, 0.6), () => {
    const x = 480, y = 470, w = 560, h = 300;
    lintPanel('证据卡', x, y, w, h);
    rrect(x, y, w, h, 18, 'rgba(8,18,41,0.94)', 'rgba(243,238,227,0.4)', 2.5);
    txt('76 份研究汇总（元分析）', x + 30, y + 44, { size: 34, weight: 900, color: COL.cream });
    const rows = [['被问到的内容', 'g = 0.54', COL.yellow, 27.0], ['没被问到的', 'g = 0.04', COL.grayHi, 27.5]];
    rows.forEach(([l, v, c, at], i) => {
      const ry = y + 112 + i * 70, ra = popA(bt, at, 0.35);
      withAlpha(ra, () => {
        rrect(x + 30, ry - 22, 40, 44, 7, i ? '#66728f' : COL.yellow);
        txt(l, x + 88, ry, { size: 38, weight: 900, color: i ? COL.grayHi : COL.cream });
        txt(v, x + w - 30, ry + 2, { size: 44, weight: 800, fam: 'mono', color: c, align: 'right', glow: i ? 0 : 12 });
      });
    });
    txt('g 是效果大小：0.5 左右算中等，0 是没效果', x + 30, y + 248, { size: 26, weight: 700, color: COL.gray, alpha: popA(bt, 28, 0.4) });
    sourceNote('St. Hilaire 等 2024 · 预注册元分析 · 7,902 人', x + 30, y + 280, { alpha: popA(bt, 28, 0.4) });
  }));
}

// ---------- the hero ----------
function heroState(bt) {
  if (bt < 32) return heroOpening(bt);
  if (bt < 64) return heroStep1(bt);
  if (bt < 96) return heroStep2(bt);
  if (bt < 128) return heroStep3(bt);
  return heroSummary(bt);
}
// screen positions of head / hands without drawing (same maths as drawFigure)
function figureHands(st) {
  const p = full(st.pose), J = rigJoints(p), py = pelvisHeight(p), s = st.s, d = st.dir ?? 1;
  const S = (q) => [st.x + d * s * q[0], st.y + s * (q[1] - py)];
  return { head: S(J.head), handF: S(J.armF[2]), handB: S(J.armB[2]), elbowF: S(J.armF[1]) };
}
function drawHero(st, bt) {
  const r = drawFigure({ x: st.x, y: st.y, s: st.s, dir: st.dir ?? 1, pose: st.pose, style: 'A', face: st.face, pointF: st.pointF });
  const [hx, hy] = r.head;
  lintPanel('head:他', hx - 30 * st.s, hy - 34 * st.s, 60 * st.s, 68 * st.s);
  const h = figureHands(st);
  const pr = st.prop;
  if (pr) {
    const [x, y] = h.handF, [ex, ey] = h.elbowF, d = st.dir ?? 1, ang = Math.atan2(y - ey, x - ex);
    if (pr.type === 'qcard' && pr.s > 0.01) drawQuizStand({ ...quizState(bt), cx: x + 30, cy: y - 20, scale: pr.s, stand: 0, plain: true });
    if (pr.type === 'marker') drawMarker(x, y, ang - 0.5 * d);
    if (pr.type === 'highlighter') drawHighlighter(x, y, ang - 0.7 * d);
    if (pr.type === 'fan') for (let k = 0; k < 5; k++) drawQCard(x + 6 + (k - 2) * 14, y - 30, { w: 96, h: 68, n: k + 1, rot: (k - 2) * 0.22, star: true, plain: true });
  }
  return { ...r, ...h };
}

function renderFrame(t) {
  const bt = t / BEAT;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  drawBackground(t);
  const st = heroState(bt);
  drawStage(t, st.x, { glow: win(bt, 146, 149, 0.05, 1.6) });
  const pre = figureHands(st);
  drawOpeningBack(bt, t, st, pre);
  drawAnswerBack(bt);
  if (typeof drawSectionsBack === 'function') drawSectionsBack(bt, t, st, pre);
  const hands = drawHero(st, bt);
  drawTitleBlock(bt);
  drawOpeningFront(bt);
  drawAnswerFront(bt, st, hands);
  if (typeof drawSectionsFront === 'function') drawSectionsFront(bt, t, st, hands);
  drawChapterBar(bt);
  window.__frameInfo = { t, bt, fig: st.x > 60 && st.x < W - 60 };
}
