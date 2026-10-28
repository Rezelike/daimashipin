// scene.js — timeline. All times in beats (bt). 128 BPM -> 1 beat = 0.46875 s; 160 beats = 75 s.
// Same beat grid as sleep_or_cram (lessons 13): reveal 1 at beat 4.5 (2.11 s), reveal 2 four beats later at 8.5 (3.98 s),
// the check at 10.5 (4.92 s), the answer section from beat 17 (8.0 s), steps at 32 / 64 / 96, the table at 128.
const TOTAL_BEATS = 160;

// ---------- hero boy (on screen in every frame) ----------
const BOY = {
  x: KB([[0, 1360], [16, 1360], [17.5, 960], [30.5, 960], [32.5, 470], [126.5, 470], [128.5, 400]]),
  y: KB([[0, 860], [16, 860], [17.5, 872], [30.5, 872], [32.5, 842], [126.5, 842], [128.5, 852]]),
  s: KB([[0, 1], [16, 1], [17.5, 1.12], [30.5, 1.12], [32.5, 0.9], [126.5, 0.9], [128.5, 0.92]]),
  // lying down: right after 「都背到全对」 (the user's idea: 睡前背完就上床) until he wakes in the morning at 8.4 s;
  // step ① after 16 个全对 until the alarm in step ③; the table's row 2
  bed: KB([[0, 0], [5.4, 0], [6.4, 1, 'out'], [18, 1], [18.9, 0, 'out'], [50.6, 0], [52, 1], [100.4, 1], [101.2, 0, 'out'],
    [133.9, 0], [135, 1], [138, 1], [138.8, 0, 'out']]),
  // sitting up in bed with the lamp on from frame 0; once he lies down (bed = 1 at beat 6.4) sit is no longer visible
  sit: KB([[0, 1], [6.4, 1], [6.5, 0]]),
  stretch: KB([[20.3, 0], [21.3, 1, 'out'], [23.2, 1], [24, 0]]),
  read: KB([[0, 1], [4.6, 1], [5.3, 0], [24, 0], [25, 1, 'out'], [49.4, 1], [50.4, 0], [129.4, 0], [130.3, 1, 'out'], [133.2, 1], [134, 0]]),
  write: KB([[102, 0], [102.9, 1], [125.2, 1], [125.9, 0], [138.7, 0], [139.5, 1], [149, 1], [149.6, 0]]),
  point: KB([[149.6, 0], [150.4, 1, 'out'], [152, 1], [152.6, 0]]),
  thumb: KB([[121, 0], [121.7, 1, 'back'], [124.6, 1], [125.2, 0], [153, 0], [153.8, 1, 'back']]),
  happy: KB([[10.5, 0], [11, 1], [16, 1], [17, 0.4], [118, 0.4], [118.6, 1], [126, 1], [127, 0.4], [152, 0.4], [152.6, 1]]),
};
// blink schedule (beats) while awake
const BLINKS = [1.2, 3.6, 19.6, 25.6, 29.3, 37.1, 43.9, 102.4, 109.6, 113.3, 120.2, 131.2, 144.6, 156.2];
function blinkAt(bt) {
  let v = 0;
  for (const b of BLINKS) { const d = Math.abs(bt - b); if (d < 0.35) v = Math.max(v, 1 - d / 0.35); }
  return v;
}
// reciting: in the hook (both kids learn at frame 0) and while he tests himself in step ①
function talkAt(bt) {
  if (bt < 4.6) return Math.max(0, Math.sin((bt + 0.3) * Math.PI * 2.2)) * 0.45;
  if (bt > 36 && bt < 47.6) return Math.max(0, Math.sin(bt * Math.PI * 2)) * 0.3;
  return 0;
}

// ---------- opening (0–17 beats) ----------
// Mazza et al. 2016: both groups learned 16 Swahili–French words until each was right once (the tie, beat 4.5),
// 12 h later (wake group 9 am -> 9 pm, sleep group 9 pm -> sleep -> 9 am) they recalled 7.45 vs 10.3 (beat 8.5).
// Shown as each kid's 16 word cards (2026-10-27: the bars looked like the last episode): the cards light up row by row
// while they learn, all 16 are lit at reveal 1, and at reveal 2 the forgotten ones flip back to "?".
const OPEN = {
  pill: KB([[0, 0], [4.5, 0], [5.0, 1, 'out'], [8.5, 1], [9.0, 2, 'out']]),
  dayL: KB([[0, 1], [8.5, 1], [10.0, 0, 'inOut']]),   // her window: morning -> 9 pm
  dayR: KB([[0, 0], [8.5, 0], [10.0, 1, 'inOut']]),   // his window: night -> 9 am
  lamp: KB([[0, 1], [6.0, 1], [6.12, 0, 'lin']]),    // his reading lamp: off once he lies down
  outA: KB([[0, 1], [15.5, 1], [16.6, 0, 'out']]),
  girlX: KB([[0, 560], [15.5, 560], [17, 300, 'in']]),
};
const CARDS_Y = 538;
// learning: one row of 4 cards per beat, hers on the beat, his on the half beat -> all 16 lit before reveal 1
const LEARN = { girl: [0, 1, 2, 3], boy: [0.5, 1.5, 2.5, 3.5] };
const CARD_FLIP = 0.3, CARD_STAGGER = 0.08;
// reveal 2: the forgotten cards flip back in a scattered order. Her 7.45 is shown as 7.5 (the 9th card flips halfway).
const FORGET = {
  girl: { cards: [5, 0, 10, 15, 3, 12, 6, 9], half: 11, t0: 8.7, step: 0.11 },
  boy: { cards: [7, 13, 1, 10, 4, 14], half: null, t0: 8.76, step: 0.15 },
};
function cardState(who, i, bt) {
  const tl = LEARN[who][Math.floor(i / 4)] + (i % 4) * CARD_STAGGER;
  if (bt < tl + CARD_FLIP) return flipFace(bt, tl, CARD_FLIP, 'blank', 'lit');
  const F = FORGET[who], k = F.cards.indexOf(i);
  if (k >= 0) return flipFace(bt, F.t0 + k * F.step, CARD_FLIP, 'lit', 'lost');
  if (F.half === i) return flipFace(bt, F.t0 + F.cards.length * F.step, CARD_FLIP, 'lit', 'half');
  return { face: 'lit', sx: 1 };
}
// count next to a grid: a card counts as forgotten once it is past the middle of its flip
function cardsLeft(who, bt) {
  const F = FORGET[who];
  let n = 16;
  F.cards.forEach((c, k) => { if (bt >= F.t0 + k * F.step + CARD_FLIP / 2) n -= 1; });
  if (F.half !== null && bt >= F.t0 + F.cards.length * F.step + CARD_FLIP / 2) n -= 0.5;
  return n;
}
const countText = (n) => (n % 1 ? n.toFixed(1) : String(n));

function drawTitleBlock(bt, t) {
  const outA = 1 - EASE.out(seg(bt, 30.5, 31.4));
  const dyOut = -40 * EASE.in(seg(bt, 30.5, 31.4));
  if (outA <= 0) return;
  withAlpha(outA, () => {
    txt('背单词', 960, 150 + dyOut, { size: 100, weight: 900, color: COL.cream, align: 'center' });
    // line 2: the question, flips to the answer at beat 17
    const p = seg(bt, 16.6, 17.4);
    const e = EASE.inOut(p);
    const y2 = 288 + dyOut;
    ctx.save();
    ctx.beginPath(); ctx.rect(0, y2 - 100, W, 200); ctx.clip();
    if (e < 1) {
      const answer = seg(bt, 10.5, 11.3);
      const spans = [
        { s: '早上', color: lerpColor(COL.cyan, '#6f7b99', answer), glow: 22 * (1 - answer) },
        { s: '还是', color: COL.cream },
        { s: '睡前', color: COL.yellow, glow: 26 + answer * 20 },
        { s: '？', color: COL.cream },
      ];
      rich(spans, 960, y2 - e * 180, { size: 142, weight: 900, align: 'center', alpha: 1 - e });
    }
    if (e > 0) {
      rich([{ s: '睡前背，早上复习', color: COL.yellow, glow: 30 }], 960, y2 + (1 - e) * 180, { size: 142, weight: 900, align: 'center', alpha: e });
    }
    ctx.restore();
    // english typewriter (left-aligned at centred origin to avoid jitter)
    const en1 = 'Vocab: in the morning, or before bed?';
    const en2 = 'Learn before bed, review in the morning.';
    const useSecond = bt >= 17;
    const s = useSecond ? en2 : en1;
    const fw = measure(s, 34, 500, 'mono');
    const p1 = useSecond ? seg(bt, 17.2, 20) : lerp(7 / en1.length, 1, seg(bt, 0, 2.6));
    typeText(s, p1, 960 - fw / 2, 388 + dyOut, { size: 34, weight: 500, fam: 'mono', color: COL.cyan, keepCursor: true }, bt);
  });
}

function drawOpening(bt, t) {
  const A = OPEN.outA(bt);
  if (A <= 0 && bt > 17) return;
  // his bedside lamp (on while he reads in bed), then the two windows: her morning, his night; they swap at reveal 2
  drawBedLamp(1660, 846, OPEN.lamp(bt), { alpha: A });
  drawWindow(210, 585, 210, 250, OPEN.dayL(bt), { alpha: A, t });
  drawWindow(1710, 585, 210, 250, OPEN.dayR(bt), { alpha: A, t });

  // pill
  const pIdx = OPEN.pill(bt);
  const flash = Math.max(0, 1 - Math.abs(bt - 4.75) / 0.5) + Math.max(0, 1 - Math.abs(bt - 8.75) / 0.5);
  drawPill(960, 464, [
    { s: '16 个新单词', icon: 'book' },
    { s: '都背到全对', icon: 'check' },
    { s: '12 小时后再考', icon: 'clock' },
  ], pIdx, { alpha: A, flash: clamp(flash) });

  // the 16 word cards of each kid
  const gx = OPEN.girlX(bt), bx = 1360;
  const grayK = seg(bt, 8.6, 9.3);
  const done = win(bt, 4.5, 5.7, 0.1, 0.9);   // all lit: glow pulse on reveal 1
  withAlpha(A, () => {
    for (let i = 0; i < 16; i++) {
      const [x, y] = cardCentre(gx, CARDS_Y, i), c = cardState('girl', i, bt);
      drawWordCard(x, y, c.face, { sx: c.sx, color: COL.cyan, colorHi: COL.cyanHi, glow: 1 - 0.7 * grayK + done });
      const [x2, y2] = cardCentre(bx, CARDS_Y, i), c2 = cardState('boy', i, bt);
      drawWordCard(x2, y2, c2.face, { sx: c2.sx, color: COL.yellow, colorHi: COL.yellowHi, glow: 1 + done + seg(bt, 10.5, 11) * 0.6 });
    }
    // counts on the inner side of each grid, from reveal 1
    const gNumX = gx + CARD_GRID_W / 2 + 22, bNumX = bx - CARD_GRID_W / 2 - 22;
    const numA = popA(bt, 4.6, 0.4);
    if (numA > 0) {
      txt(countText(cardsLeft('girl', bt)), gNumX, 560, { size: 56, weight: 800, fam: 'mono', color: lerpColor(COL.cyanHi, COL.grayHi, grayK), alpha: numA, glow: 10 * (1 - grayK) });
      txt(countText(cardsLeft('boy', bt)), bNumX, 560, { size: 56, weight: 800, fam: 'mono', color: COL.yellowHi, align: 'right', alpha: numA, glow: 12 });
    }
    // reactions
    const ckx = bNumX - measure('10', 56, 800, 'mono') - 40;
    const cs = popS(bt, 10.5, 0.6);
    if (cs > 0) withScale(ckx, 560, cs, () => {
      ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 24;
      circle(ckx, 560, 26, COL.yellow); ctx.restore();
      checkBadge(ckx, 560, 26, { color: '#0d1838', p: seg(bt, 10.5, 11.2), lw: 4 });
    });
    const la = popA(bt, 10.6, 0.4);
    if (la > 0) txt('记得多', bNumX + (1 - la) * 20, 622, { size: 40, weight: 900, color: COL.yellow, align: 'right', alpha: la, glow: 16 });
    const lb = popA(bt, 11.5, 0.4);
    if (lb > 0) txt('忘了一半', gNumX - (1 - lb) * 20, 622, { size: 34, weight: 700, color: COL.grayHi, alpha: lb });
  });
  sourceNote('Mazza 等 2016 · 《Psychological Science》 · 法国 40 名年轻人 · 16 个里平均还记得几个', 110, 988, { alpha: A * popA(bt, 13, 0.8) });
}

function drawGirl(bt, t) {
  const A = OPEN.outA(bt);
  if (A <= 0) return;
  const reciting = bt < 4.6;
  const cyc = ((bt - 0.5) % 2 + 2) % 2;
  const flip = reciting && bt > 0.5 ? clamp(cyc / 0.9) : 0;
  const worry = seg(bt, 8.8, 9.6);
  const x = OPEN.girlX(bt);
  // she learns over breakfast; after 都背到全对 she closes the book and gets on with her day until the 9 pm test
  const read = KB([[0, 1], [4.6, 1], [5.3, 0]])(bt);
  const write = KB([[5.4, 0], [6.2, 1], [8.4, 1], [9.0, 0]])(bt);
  const notebook = write > 0.05 || (bt > 5.3 && bt < 9.2);
  drawKid({
    type: 'girl', x, y: 860, s: 1, t, alpha: A,
    read, write, pencil: true, flip: flip >= 1 ? 0 : flip,
    talk: reciting ? Math.max(0, Math.sin(bt * Math.PI * 2.2)) * 0.45 : 0,
    worry, blink: blinkAtGirl(bt), bookColor: '#3d9bd6',
    deskProps: () => { drawBreakfastLocal(); if (notebook) drawNotebookLocal(20, -3); },
  });
  namePlate(x, 922, '早上背', lerpColor(COL.cyan, COL.grayHi, seg(bt, 8.6, 9.3)), { alpha: A });
}
function blinkAtGirl(bt) {
  let v = 0;
  for (const b of [1.6, 5.2, 7.4, 12.4, 14.6]) { const d = Math.abs(bt - b); if (d < 0.35) v = Math.max(v, 1 - d / 0.35); }
  return v;
}

// ---------- answer section 「睡前背」 (17–32): tags ①②③ and the evidence card ----------
const TAGS = [
  { n: 1, s: '睡前背什么', slot: [560, 548], at: 19.0 },
  { n: 2, s: '背完多久睡', slot: [960, 548], at: 21.5 },
  { n: 3, s: '醒来干嘛', slot: [1360, 548], at: 25.0 },
];
function tagOrigin(i, boy) {
  if (i === 0) return [boy.headX, boy.headY];
  if (i === 1) return [960, 872 - 230 * 1.12];
  return [960 + 40, 872 - 40 * 1.12];
}
function drawS1(bt, t, boy) {
  if (bt < 18 || bt > 33) return;
  TAGS.forEach((tg, i) => {
    if (bt < tg.at) return;
    const fly = EASE.out(seg(bt, tg.at, tg.at + 0.8));
    const [ox, oy] = tagOrigin(i, boy);
    let x = lerp(ox, tg.slot[0], fly), y = lerp(oy, tg.slot[1], fly);
    let sc = popS(bt, tg.at, 0.8), a = popA(bt, tg.at, 0.25);
    const hi = i === 0 ? win(bt, 29.2, 31, 0.4, 0.4) : 0;
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
  // evidence card (12.4 s): what the boy is doing right now pays off — relearning took half the rounds
  const ea = popA(bt, 26.5, 0.5) * (1 - seg(bt, 30.4, 31.1));
  if (ea > 0) {
    const s = popS(bt, 26.5, 0.8);
    withAlpha(ea, () => withScale(1520, 790, 0.9 + 0.1 * s, () => {
      rrect(1262, 712, 516, 156, 14, 'rgba(12,26,58,0.9)', 'rgba(63,203,232,0.45)', 2);
      iconCheck(1304, 752, 44, COL.cyan);
      txt('早上复习：3 轮就全对', 1342, 752, { size: 34, weight: 900, color: COL.cyan });
      txt('早上背、晚上复习的：要 6 轮', 1290, 804, { size: 26, weight: 700, color: COL.cream });
      txt('重新背到全对的平均轮数 · Mazza 等 2016', 1290, 842, { size: 22, weight: 500, color: COL.gray });
    }));
  }
}

// ---------- main ----------
function boyParams(bt, t) {
  const bed = BOY.bed(bt);
  return {
    type: 'boy', x: BOY.x(bt), y: BOY.y(bt), s: BOY.s(bt), t,
    bed, sit: BOY.sit(bt), stretch: BOY.stretch(bt), read: BOY.read(bt), write: BOY.write(bt),
    point: BOY.point(bt), thumb: BOY.thumb(bt),
    happy: BOY.happy(bt), blink: bed < 0.1 ? blinkAt(bt) : 0, talk: talkAt(bt),
    bubble: bed > 0.8 ? 7 + 6 * (0.5 + 0.5 * Math.sin(t * TAU / (BEAT * 4))) : 0,
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

  if (bt < 18) drawOpening(bt, t);
  drawTitleBlock(bt, t);
  if (bt < 17) drawGirl(bt, t);

  // sections drawn behind the boy
  if (typeof drawPanelLayer === 'function') drawPanelLayer(bt, t);

  const bp = boyParams(bt, t);
  if (typeof decorateBoy === 'function') decorateBoy(bp, bt, t);
  const boy = drawKid(bp);
  info.kid = (bp.alpha ?? 1) > 0.5;
  if (bt < 17) namePlate(bp.x, 922, '睡前背', COL.yellow, { alpha: OPEN.outA(bt) });

  drawS1(bt, t, boy);
  if (typeof drawSections === 'function') drawSections(bt, t, boy);

  drawChapterBar(bt);
  window.__frameInfo = info;
}
