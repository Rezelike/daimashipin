// scene.js — timeline. All times in beats (bt). 128 BPM -> 1 beat = 0.46875 s; 160 beats = 75 s.
const TOTAL_BEATS = 160;

// ---------- hero boy (persists through the whole video) ----------
const BOY = {
  x: KB([[0, 1360], [14, 1360], [15.5, 960], [30.5, 960], [32.5, 470], [126.5, 470], [128.5, 400]]),
  y: KB([[0, 860], [14, 860], [15.5, 872], [30.5, 872], [32.5, 842], [126.5, 842], [128.5, 852]]),
  s: KB([[0, 1], [14, 1], [15.5, 1.12], [30.5, 1.12], [32.5, 0.9], [126.5, 0.9], [128.5, 0.92]]),
  sleep: KB([[0, 1], [16, 1], [16.9, 0, 'out'], [50.6, 0], [52, 1], [100.4, 1], [101.2, 0, 'out'],
    [133.9, 0], [135, 1], [138, 1], [138.8, 0, 'out']]),
  stretch: KB([[18.8, 0], [19.8, 1, 'out'], [22.2, 1], [23, 0]]),
  read: KB([[23, 0], [24, 1, 'out'], [49.4, 1], [50.4, 0], [129.4, 0], [130.3, 1, 'out'], [133.2, 1], [134, 0]]),
  write: KB([[102, 0], [102.9, 1], [125.2, 1], [125.9, 0], [138.7, 0], [139.5, 1], [149, 1], [149.6, 0]]),
  tap: KB([[100.6, 0], [101.1, 1, 'out'], [101.8, 1], [102.3, 0]]),
  point: KB([[149.6, 0], [150.4, 1, 'out'], [152, 1], [152.6, 0]]),
  thumb: KB([[121, 0], [121.7, 1, 'back'], [124.6, 1], [125.2, 0], [153, 0], [153.8, 1, 'back']]),
  happy: KB([[8.5, 0], [9, 1], [14, 1], [15, 0.4], [118, 0.4], [118.6, 1], [126, 1], [127, 0.4], [152, 0.4], [152.6, 1]]),
};
// blink schedule (beats) while awake
const BLINKS = [17.6, 25.2, 29.3, 37.1, 43.9, 102.4, 109.6, 113.3, 120.2, 131.2, 144.6, 156.2];
function blinkAt(bt) {
  let v = 0;
  for (const b of BLINKS) { const d = Math.abs(bt - b); if (d < 0.35) v = Math.max(v, 1 - d / 0.35); }
  return v;
}

const T0 = {
  title1: '学累了',
};

// ---------- opening (0–15 beats) ----------
const OPEN = {
  pill: KB([[0, 0], [4.5, 0], [5.0, 1, 'out'], [6.5, 1], [7.0, 2, 'out']]),
  cram: KB([[0, 0], [4.5, 0], [5.4, 0.82, 'back'], [6.5, 0.82], [7.5, 0.44, 'bounce']]),
  nap: KB([[0, 0], [4.5, 0], [5.4, 0.82, 'back']]),
  clock: KB([[0, 15.0], [4.5, 15.0], [5.6, 16.5, 'inOut'], [6.5, 16.5], [8.0, 16.5 + 9, 'inOut']]),
  outA: KB([[0, 1], [13.5, 1], [14.6, 0, 'out']]),
  girlX: KB([[0, 560], [13.5, 560], [15, 300, 'in']]),
};

function drawTitleBlock(bt, t) {
  // line 1
  const outA = 1 - EASE.out(seg(bt, 30.5, 31.4));
  const dyOut = -40 * EASE.in(seg(bt, 30.5, 31.4));
  if (outA <= 0) return;
  withAlpha(outA, () => {
    txt('学累了', 960, 150 + dyOut, { size: 100, weight: 900, color: COL.cream, align: 'center' });
    // line 2: flip at beat 15
    const p = seg(bt, 14.6, 15.4);
    const e = EASE.inOut(p);
    const y2 = 288 + dyOut;
    ctx.save();
    ctx.beginPath(); ctx.rect(0, y2 - 100, W, 200); ctx.clip();
    if (e < 1) {
      const answer = seg(bt, 8.5, 9.3);
      const spans = [
        { s: '睡', color: COL.yellow, glow: 26 + answer * 20 },
        { s: '还是', color: COL.cream },
        { s: '背', color: lerpColor(COL.cyan, '#6f7b99', answer), glow: 22 * (1 - answer) },
        { s: '？', color: COL.cream },
      ];
      rich(spans, 960, y2 - e * 180, { size: 142, weight: 900, align: 'center', alpha: 1 - e });
    }
    if (e > 0) {
      rich([{ s: '先睡一觉', color: COL.yellow, glow: 30 }], 960, y2 + (1 - e) * 180, { size: 142, weight: 900, align: 'center', alpha: e });
    }
    ctx.restore();
    // english typewriter (left-aligned at centred origin to avoid jitter)
    const en1 = 'Tired? Nap, or keep cramming?';
    const en2 = 'Tired? Take a nap first.';
    const useSecond = bt >= 15;
    const s = useSecond ? en2 : en1;
    const fw = measure(s, 34, 500, 'mono');
    const p1 = useSecond ? seg(bt, 15.2, 18) : lerp(7 / en1.length, 1, seg(bt, 0, 2.6));
    typeText(s, p1, 960 - fw / 2, 388 + dyOut, { size: 34, weight: 500, fam: 'mono', color: COL.cyan, keepCursor: true }, bt);
  });
}

function drawOpening(bt, t) {
  const A = OPEN.outA(bt);
  if (A <= 0 && bt > 15) return;
  // wall clock (right)
  const clockH = OPEN.clock(bt);
  const spinning = (bt > 4.5 && bt < 5.6) || (bt > 6.5 && bt < 8.0);
  const tickJit = bt < 4.5 ? 0 : 0;
  drawWallClock(1700, 560, 72, clockH + tickJit, { alpha: A, blur: spinning ? 3 : 0 });

  // pill
  const pIdx = OPEN.pill(bt);
  const flash = Math.max(0, 1 - Math.abs(bt - 4.75) / 0.5) + Math.max(0, 1 - Math.abs(bt - 6.75) / 0.5);
  drawPill(960, 464, [
    { s: '下午 3 点', icon: 'clock' },
    { s: '30 分钟后考试', icon: 'paper' },
    { s: '一周后', icon: 'calendar' },
  ], pIdx, { alpha: A, flash: clamp(flash) });

  // meters
  const bottom = 640, hMax = 190, mw = 84;
  const restY = bottom - 0.42 * hMax;
  const grayK = seg(bt, 6.6, 7.3);
  const q = bt < 4.5 ? 0.6 + 0.4 * Math.sin(bt * Math.PI) : 1 - seg(bt, 4.5, 4.9);
  drawMeter(OPEN.girlX(bt), bottom, mw, hMax, OPEN.cram(bt), {
    color: lerpColor(COL.cyan, '#66728f', grayK), colorHi: lerpColor(COL.cyanHi, '#8994ad', grayK), alpha: A, q: bt < 4.9 ? q : 0,
    glow: 1 - grayK,
  });
  drawMeter(1360, bottom, mw, hMax, OPEN.nap(bt), { color: COL.yellow, colorHi: COL.yellowHi, alpha: A, q: bt < 4.9 ? q : 0, glow: 1 + seg(bt, 8.5, 9) * 0.6 });
  drawRestLine(470, 1450, restY, seg(bt, 4.6, 5.5), { alpha: A });

  // reactions
  const napTop = bottom - OPEN.nap(bt) * hMax;
  withAlpha(A, () => {
    const cs = popS(bt, 8.5, 0.6);
    if (cs > 0) withScale(1360, napTop, cs, () => {
      ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 24;
      circle(1360, napTop, 27, COL.yellow); ctx.restore();
      checkBadge(1360, napTop, 27, { color: '#0d1838', p: seg(bt, 8.5, 9.2), lw: 4 });
    });
    const la = popA(bt, 8.6, 0.4);
    if (la > 0) txt('还领先', 1418 + (1 - la) * -20, napTop, { size: 40, weight: 900, color: COL.yellow, alpha: la, glow: 16 });
    const lb = popA(bt, 9.5, 0.4);
    if (lb > 0) txt('优势没了', 502 + (1 - lb) * 20, restY - 30, { size: 32, weight: 700, color: COL.grayHi, align: 'right', alpha: lb });
  });
  sourceNote('Cousins 等 2019 · 《Sleep》 · 新加坡杜克-国大医学院', 1800, 988, { align: 'right', alpha: A * popA(bt, 11, 0.8) });
}

function drawGirl(bt, t) {
  const A = OPEN.outA(bt);
  if (A <= 0) return;
  const reciting = bt < 6.5;
  const cyc = ((bt - 0.5) % 2 + 2) % 2;
  const flip = reciting && bt > 0.5 ? clamp(cyc / 0.9) : 0;
  const worry = seg(bt, 6.8, 7.6);
  const x = OPEN.girlX(bt);
  drawKid({
    type: 'girl', x, y: 860, s: 1, t, alpha: A,
    read: lerp(1, 0.82, worry), flip: flip >= 1 ? 0 : flip,
    talk: reciting ? Math.max(0, Math.sin(bt * Math.PI * 2.2)) * 0.45 : 0,
    worry, blink: blinkAtGirl(bt), bookColor: '#3d9bd6',
  });
  namePlate(x, 922, '接着背 1 小时', lerpColor(COL.cyan, COL.grayHi, seg(bt, 6.6, 7.3)), { alpha: A });
}
function blinkAtGirl(bt) {
  let v = 0;
  for (const b of [1.6, 5.2, 10.4, 12.6]) { const d = Math.abs(bt - b); if (d < 0.35) v = Math.max(v, 1 - d / 0.35); }
  return v;
}

// ---------- S1 tags ----------
const TAGS = [
  { n: 1, s: '什么时候睡', slot: [560, 548], at: 17.0 },
  { n: 2, s: '睡多久', slot: [960, 548], at: 20.0 },
  { n: 3, s: '醒来干嘛', slot: [1360, 548], at: 24.0 },
];
function tagOrigin(i, boy) {
  if (i === 0) return [boy.headX, boy.headY];
  if (i === 1) return [960, 872 - 230 * 1.12];
  return [960 + 40, 872 - 40 * 1.12];
}
function drawS1(bt, t, boy) {
  if (bt < 16 || bt > 33) return;
  TAGS.forEach((tg, i) => {
    if (bt < tg.at) return;
    const fly = EASE.out(seg(bt, tg.at, tg.at + 0.8));
    const [ox, oy] = tagOrigin(i, boy);
    let x = lerp(ox, tg.slot[0], fly), y = lerp(oy, tg.slot[1], fly);
    let sc = popS(bt, tg.at, 0.8), a = popA(bt, tg.at, 0.25);
    let hi = i === 0 ? win(bt, 29.2, 31, 0.4, 0.4) : 0;
    if (bt > 30.5) {
      const q = EASE.inOut(seg(bt, 30.5, 32.2));
      if (i === 0) {
        x = lerp(tg.slot[0], 560, q); y = lerp(tg.slot[1], 132, q);
        sc = lerp(1, 0.9, q); a = 1 - seg(bt, 31.6, 32.3);
      } else {
        sc = 1 - q * 0.3; a = 1 - seg(bt, 30.5, 31.3);
      }
    }
    drawTag(x, y, tg.n, tg.s, { alpha: a, scale: sc, hi });
  });
  // evidence card
  const ea = popA(bt, 26, 0.5) * (1 - seg(bt, 30.4, 31.1));
  if (ea > 0) {
    const s = popS(bt, 26, 0.8);
    withAlpha(ea, () => withScale(1520, 790, 0.9 + 0.1 * s, () => {
      rrect(1262, 712, 516, 156, 14, 'rgba(12,26,58,0.9)', 'rgba(63,203,232,0.45)', 2);
      iconBrain(1306, 752, 46, COL.cyan);
      txt('不止一个实验', 1342, 752, { size: 34, weight: 900, color: COL.cyan });
      txt('多项研究汇总：午睡后认知测验整体更好', 1290, 804, { size: 26, weight: 700, color: COL.cream });
      txt('效应量 d = 0.38 · Leong 等 2022', 1290, 842, { size: 22, weight: 500, fam: 'mono', color: COL.gray });
    }));
  }
}

// ---------- main ----------
function boyParams(bt, t) {
  const sleep = BOY.sleep(bt);
  return {
    type: 'boy', x: BOY.x(bt), y: BOY.y(bt), s: BOY.s(bt), t,
    sleep, stretch: BOY.stretch(bt), read: BOY.read(bt), write: BOY.write(bt),
    tap: BOY.tap(bt), point: BOY.point(bt), thumb: BOY.thumb(bt),
    happy: BOY.happy(bt), blink: sleep < 0.1 ? blinkAt(bt) : 0,
    bubble: sleep > 0.8 ? 7 + 6 * (0.5 + 0.5 * Math.sin(t * TAU / (BEAT * 4))) : 0,
    bookColor: '#7b5fd6', pencil: true,
    flip: 0,
  };
}

function renderFrame(t) {
  const bt = t / BEAT;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  drawBackground(t);
  const info = { t, bt, kid: false };

  if (bt < 16) drawOpening(bt, t);
  drawTitleBlock(bt, t);
  if (bt < 15) drawGirl(bt, t);

  // sections drawn behind the boy
  if (typeof drawPanelLayer === 'function') drawPanelLayer(bt, t);

  const bp = boyParams(bt, t);
  if (typeof decorateBoy === 'function') decorateBoy(bp, bt, t);
  const boy = drawKid(bp);
  info.kid = (bp.alpha ?? 1) > 0.5;
  if (bt < 15) namePlate(bp.x, 922, '午睡 1 小时', COL.yellow, { alpha: OPEN.outA(bt) });

  drawS1(bt, t, boy);
  if (typeof drawSections === 'function') drawSections(bt, t, boy);

  drawChapterBar(bt);
  window.__frameInfo = info;
}
