// scene.js — timeline of 「背书要读出声吗？」. All times in beats (bt). 128 BPM -> 1 beat = 0.46875 s; 160 beats = 75 s.
// Beat grid of 睡还是背 (lessons 13, six/plan.md): reveal 1 at beat 4.5 (2.11 s), reveal 2 at 8.5 (3.98 s), the check at
// 10.5 (4.92 s), the other label at 11.5 (5.39 s), the source at 13 (6.1 s), the answer from 17 (8.0 s), the evidence card
// at 26.5 (12.4 s), steps at 32 / 64 / 96, the summary 128-160.
// One adult figure (kit/figure.js, look B = neon line), never seated. Numbers: six/facts/03_read_aloud.md (six-videos branch).
const TOTAL_BEATS = 160;
const GROUND = 930;
const HERO_S = 0.95;

// ---------- poses (absolute angles, see figure.js) ----------
const HOLD_SHEET = { uaF: 16, faF: 118 };            // a word sheet held in front of the chest
const RAISE_PAGE = { uaF: 108, faF: 128, head: -8 };  // the floating page raised beside his head
const PEN_AIM = { uaF: 92, faF: 100, head: 6 };       // the light pen aimed at the page
const SPEAK_LEAN = { lean: 4, head: -6 };
const withPose = (...ps) => Object.assign({}, POSES.stand, ...ps);
const poseMix = (a, b, t) => lerpPose(a, b, clamp(t));
// pose window: like win(), but the fade-out also starts fast, so every pose change begins ON its beat (rhythm check)
function pw(bt, a, b, fi = 0.5, fo = 0.5) {
  if (bt <= a || bt >= b) return 0;
  return Math.min(EASE.out(seg(bt, a, a + fi)), 1 - EASE.out(seg(bt, b - fo, b)));
}

// ---------- the sound-wave stage: every word said aloud sends a ripple along the horizon ----------
// SPEECH = [[beat, x, loudness 0..1]]; filled by the sections below, sorted once.
const SPEECH = [];
function addSpeech(b, x, k) { SPEECH.push([b, x, k]); }
function stageWave(x, t) {
  const bt = t / BEAT;
  let y = 0;
  for (const [b, x0, k] of SPEECH) {
    const age = bt - b;
    if (age < 0 || age > 5) continue;
    const front = 220 * age * BEAT * 8;               // px travelled (fast ripple)
    const d = Math.abs(x - x0);
    if (d > front + 40) continue;
    const env = Math.exp(-age * 1.15) * Math.exp(-Math.max(0, front - d) / 260);
    y += -k * 26 * env * Math.sin((d - front) / 26) * Math.exp(-((d - front) ** 2) / (2 * 140 ** 2) * 0.15);
  }
  return y;
}

// ---------- opening (0-17): one list, half said aloud, half read silently (MacLeod et al. 2010, Exp. 1) ----------
// Left pair: MacLeod 2010 Exp 1A+1B, recognition hit rates silent 59.8 % / aloud 76.0 % (n = 44).
// Right pair: Icht et al. 2014, the group that read 80 % of the list aloud: silent 63.1 % / aloud 65.3 % (n.s.).
const PAIR_L = { q: 290, a: 470, bottom: 872, cx: 380 }, PAIR_R = { q: 1450, a: 1630, bottom: 872, cx: 1540 };
const LV = { lq: 0.598, la: 0.760, rq: 0.631, ra: 0.653 };
const WORDS = ['apple', 'river', 'candle', 'tiger', 'pencil', 'garden', 'bottle', 'cloud', 'hammer', 'ladder', 'orange',
  'island', 'rocket', 'button', 'jacket', 'mirror', 'basket', 'violin'];
// flights: [launch beat, kind, column x, slot, duration]; each lands one beat later (on a beat or half beat)
const FLIGHTS = [];
// a word appears over his sheet as a dashed box on beat `b`; aloud ones fill solid (voice) and fly on b + 0.5, silent
// ones drift off on b + 0.5; both land on b + 1. Aloud words fill on beats 0, 1, 2, 3 (frame 0 = the first one).
for (let i = 0; i < 4; i++) {
  FLIGHTS.push({ b: i - 0.5, kind: 'aloud', to: PAIR_L.a, slot: 6 + i, d: 0.5, word: WORDS[2 * i] });
  FLIGHTS.push({ b: i, kind: 'silent', to: PAIR_L.q, slot: 6 + i, d: 0.5, word: WORDS[2 * i + 1] });
}
// reveal 2 setup: he reads the next list almost all aloud (3 of 4 here), fed into the right pair while it builds
[[6.0, 'aloud'], [6.5, 'aloud'], [7.0, 'silent'], [7.5, 'aloud']].forEach(([b, kind], i) => {
  FLIGHTS.push({ b, kind, to: kind === 'aloud' ? PAIR_R.a : PAIR_R.q, slot: 9, d: 0.5, word: WORDS[10 + i], merge: true });
});

const OPEN = {
  outA: KB([[0, 1], [15.5, 1], [16.5, 0, 'out']]),
  rightA: KB([[0, 0], [6.5, 0], [7.0, 1, 'out']]),
};

// ---------- the hero ----------
// x / facing / pose for every beat. Hook: paces while reading (one step per beat), stops for reveal 1, turns to the right
// pair for reveal 2, points back at the left pair (挑着念), shrugs at the right one (全念：差不多), walks to the left.
function heroAt(bt) {
  const st = { x: 960, dir: -1, pose: withPose(HOLD_SHEET), hold: 'sheet', s: HERO_S, y: GROUND };
  if (bt < 4.5) {
    // pacing: left from 1150 (beat -2) to 910 (beat 2), turn, right to 1040 (beat 4), stop
    const walkK = bt < 4 ? 0.42 : 0.42 * (1 - EASE.out(seg(bt, 4, 4.5)));
    if (bt < 2) { st.x = lerp(1150, 910, (bt + 2) / 4); st.dir = -1; } else { st.x = lerp(910, 1040, EASE.out(seg(bt, 2, 4.4))); st.dir = 1; }
    st.pose = withPose(walkPose(bt, walkK), HOLD_SHEET);
    return st;
  }
  if (bt < 17.5) {
    st.x = 1040;
    st.dir = bt < 6.5 ? -1 : bt < 10 ? 1 : -1;
    let p = withPose(HOLD_SHEET);
    if (bt >= 6.5 && bt < 8.5) p = poseMix(p, withPose(HOLD_SHEET, SPEAK_LEAN), pw(bt, 6.5, 8.5, 0.5, 0.5));
    if (bt >= 10 && bt < 11.5) p = poseMix(p, withPose(POSES.point), pw(bt, 10, 11.5, 0.5, 0.5));
    if (bt >= 11.5 && bt < 13.5) p = poseMix(p, withPose(POSES.shrug), pw(bt, 11.5, 13.5, 0.5, 0.5));
    if (bt >= 14) {
      // walks to the section-2 spot (x 600), one step per beat, turns to face right on arrival
      const w = seg(bt, 14, 17);
      st.x = lerp(1040, 600, EASE.inOut(w));
      st.dir = bt < 17 ? -1 : 1;
      const k = 0.85 * Math.sin(Math.PI * w);
      p = withPose(walkPose(bt - 14, k), HOLD_SHEET);
      st.hold = bt < 16.4 ? 'sheet' : null;
      if (bt >= 16.4) p = withPose(walkPose(bt - 14, k));
    }
    st.pose = p;
    return st;
  }
  if (bt < 32) return heroS1(bt, st);
  return heroSteps(bt, st);  // sections.js
}

// ---------- section 2 「挑着念」 (17-32): he raises a floating page, ① ② ③ come out of it, evidence card ----------
const PAGE2 = { x: 880, y: 620, w: 300, h: 360 };
function heroS1(bt, st) {
  st.x = 600; st.dir = 1; st.hold = null;
  const up = EASE.inOut(seg(bt, 17.5, 18.5)) * (1 - EASE.inOut(seg(bt, 30.5, 31.5)));
  let p = poseMix(withPose(), withPose(RAISE_PAGE), up);
  // looks over at the evidence card while it builds
  if (bt >= 26.5 && bt < 30.5) p = poseMix(p, withPose(RAISE_PAGE, { head: 14 }), pw(bt, 26.5, 30.5, 0.5, 0.5) * up);
  st.pose = p;
  return st;
}
const TAGS = [
  { n: 1, s: '念哪些', at: 19, slot: [1100, 482] },
  { n: 2, s: '怎么念', at: 21, slot: [1100, 590] },
  { n: 3, s: '念了有什么用', at: 23, slot: [1100, 698] },
];
// Forrin & MacLeod 2018 (Memory 26:574-579), Fig. 1: own voice aloud 77 % > own recording 74 % > someone else 69 % > silent 65 %
const VOICES = [
  { s: '自己念', v: 77, b: 1.0, icon: 'speak' },
  { s: '听自己录音', v: 74, b: 0.7, icon: 'tape' },
  { s: '听别人念', v: 69, b: 0.45, icon: 'ear' },
  { s: '默读', v: 65, b: 0, icon: 'eye' },
];

// ---------- the title block (0-31): question, then the answer ----------
function drawTitleBlock(bt, t) {
  // section changes land on the bar line: what leaves fades in the last quarter beat before it
  const outA = 1 - seg(bt, 31.75, 32);
  const dyOut = 0;
  if (outA <= 0) return;
  withAlpha(outA, () => {
    txt('背书', 960, 150 + dyOut, { size: 100, weight: 900, color: COL.cream, align: 'center' });
    const e = EASE.inOut(seg(bt, 16.5, 17.5));
    const y2 = 288 + dyOut;
    ctx.save();
    ctx.beginPath(); ctx.rect(0, y2 - 100, W, 200); ctx.clip();
    if (e < 1) {
      rich([{ s: '要' }, { s: '读出声', color: COL.yellow, glow: 26 }, { s: '吗？' }], 960, y2 - e * 180,
        { size: 142, weight: 900, align: 'center', alpha: 1 - e });
    }
    if (e > 0) {
      rich([{ s: '只把' }, { s: '要背的几句', color: COL.yellow, glow: 28 }, { s: '读出声' }], 960, y2 + (1 - e) * 180,
        { size: 128, weight: 900, align: 'center', alpha: e });
    }
    ctx.restore();
    const en1 = 'Should you read it aloud?';
    const en2 = 'Read aloud only the lines you must remember.';
    const second = bt >= 17;
    const s = second ? en2 : en1;
    const fw = measure(s, 34, 500, 'mono');
    const p1 = second ? seg(bt, 17.2, 20) : lerp(6 / en1.length, 1, seg(bt, 0, 2.4));
    typeText(s, p1, 960 - fw / 2, 388 + dyOut, { size: 34, weight: 500, fam: 'mono', color: COL.cyan, keepCursor: true }, bt);
  });
}

// ---------- opening drawing ----------
function flightState(f, bt) {
  const go = f.b + 0.5, land = go + f.d;
  if (bt < f.b || bt > land + 0.05) return null;
  return { p: seg(bt, go, land), fill: f.kind === 'aloud' ? EASE.out(seg(bt, go, go + 0.15)) : 0, a: popA(bt, f.b, 0.2), go };
}
function drawFlights(bt, hero) {
  const A = OPEN.outA(bt);
  for (const f of FLIGHTS) {
    const s = flightState(f, bt);
    if (!s) continue;
    // start: above the sheet in his hand; end: the slot in the column
    const sx = hero.handF[0] + hero.dir * 30, sy = hero.handF[1] - 70;
    const ex = f.to, ey = colBlockY(PAIR_L.bottom, f.slot);
    const e = EASE.out(s.p);
    const x = lerp(sx, ex, e), y = lerp(sy, ey, e) - Math.sin(Math.PI * e) * 120;
    const w = lerp(176, COLM.w, e), h = lerp(62, COLM.h, e);
    const wordA = 1 - clamp(e / 0.35);
    withAlpha(A * s.a * (f.merge ? 1 - seg(s.p, 0.8, 1) : 1), () => {
      wordBlock(x, y, w, h, { solid: s.fill, word: wordA > 0.02 ? f.word : null, size: 40, alpha: 1, glyph: wordA <= 0.02 });
      if (wordA > 0.02 && wordA < 1) withAlpha(1 - wordA, () => wordBlock(x, y, w, h, { solid: s.fill, glyph: true }));
    });
    if (f.kind === 'aloud') soundRings(hero.mouth[0], hero.mouth[1], hero.dir, seg(bt, s.go, s.go + 0.8), 1);
  }
}
function slotsFilled(colX, bt) {
  // left pair: 6 at frame 0, then +1 as each flight lands; right pair: builds bottom-up 7.0-8.4
  if (colX === PAIR_L.a || colX === PAIR_L.q) {
    let n = 6;
    for (const f of FLIGHTS) if (f.to === colX && !f.merge && bt >= f.b + 0.5 + f.d) n += 1;
    return n;
  }
  return 10 * EASE.out(seg(bt, 6.5, 8.0));
}
function drawOpening(bt, t, hero) {
  const A = OPEN.outA(bt);
  if (A <= 0) return;
  withAlpha(A, () => {
    // left pair: 一半念，一半默读 (reveal 1)
    const scanL = seg(bt, 4.5, 5.2), flashL = win(bt, 4.5, 5.6, 0.1, 0.8);
    recogColumn(PAIR_L.q, PAIR_L.bottom, 'silent', { n: slotsFilled(PAIR_L.q, bt), level: bt >= 4.5 ? LV.lq : null, scan: scanL, flash: flashL });
    recogColumn(PAIR_L.a, PAIR_L.bottom, 'aloud', { n: slotsFilled(PAIR_L.a, bt), level: bt >= 4.5 ? LV.la : null, scan: scanL, flash: flashL });
    kindLabel(PAIR_L.q + 14, 906, '默读', 'silent');
    kindLabel(PAIR_L.a + 14, 906, '念出声', 'aloud');
    capPill(PAIR_L.cx, 446, ['同一张单词表：一半念，一半默读'], 0, { alpha: popA(bt, 4.5, 0.3), flash: win(bt, 4.5, 5.4, 0.05, 0.8) });
    // right pair: 几乎全念出声 (reveal 2)
    const RA = OPEN.rightA(bt);
    if (RA > 0) withAlpha(RA, () => {
      const scanR = seg(bt, 8.5, 9.2), flashR = win(bt, 8.5, 9.6, 0.1, 0.8);
      recogColumn(PAIR_R.q, PAIR_R.bottom, 'silent', { n: slotsFilled(PAIR_R.q, bt), level: bt >= 8.5 ? LV.rq : null, scan: scanR, flash: flashR });
      recogColumn(PAIR_R.a, PAIR_R.bottom, 'aloud', { n: slotsFilled(PAIR_R.a, bt), level: bt >= 8.5 ? LV.ra : null, scan: scanR, flash: flashR });
      kindLabel(PAIR_R.q + 14, 906, '默读', 'silent');
      kindLabel(PAIR_R.a + 14, 906, '念出声', 'aloud');
      capPill(PAIR_R.cx, 446, ['几乎全念出声？', '几乎全念出声？差别没了'], clamp((bt - 8.5) / 0.5), { flash: win(bt, 8.5, 9.4, 0.05, 0.8) });
    });
    // verdicts: ✓ 挑着念 on the left pair (4.92 s), 全念：差不多 on the right pair (5.39 s)
    const yL = levelY(PAIR_L.bottom, LV.la), cs = popS(bt, 10.5, 0.6);
    if (cs > 0) withScale(604, yL, cs, () => okMark(604, yL, 28, seg(bt, 10.5, 11.2)));
    const la = popA(bt, 10.5, 0.35);
    if (la > 0) txt('挑着念', 646 - (1 - la) * 20, yL + 1, { size: 50, weight: 900, color: COL.yellow, alpha: la, glow: 16 });
    sparkleBurst(604, yL, seg(bt, 10.5, 12), COL.yellow);
    const yR = levelY(PAIR_R.bottom, LV.ra), lb = popA(bt, 11.5, 0.35);
    if (lb > 0) withAlpha(lb, () => {
      txt('全念：差不多', 1352 + (1 - lb) * 20, yR + 1, { size: 42, weight: 900, color: COL.grayHi, align: 'right' });
    });
    sourceNote('MacLeod 等 2010（加拿大）· Icht 等 2014（以色列）· 大学生背单词 · 百分比 = 考试时认出学过的词的比例', 960, 972,
      { alpha: popA(bt, 13, 0.8), align: 'center' });
  });
}

// ---------- section 2 drawing ----------
function drawFloatingPage(x, y, w, h, o = {}) {
  const { alpha = 1, hi = 1 } = o;
  withAlpha(alpha, () => {
    ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 24;
    rrect(x - w / 2, y - h / 2, w, h, 14, 'rgba(14,30,66,0.78)', rgba(COL.cyanHi, 0.85), 3); ctx.restore();
    // text lines; the 3 to say aloud glow
    const rows = [0.56, 0.8, 0.42, 0.7, 0.62, 0.5, 0.74];
    rows.forEach((lw, i) => {
      const ly = y - h / 2 + 52 + i * 44, key = i === 1 || i === 3 || i === 5;
      const c = key ? rgba(COL.yellow, 0.35 + 0.65 * hi) : 'rgba(200,212,236,0.38)';
      ctx.save(); if (key && hi > 0) { ctx.shadowColor = COL.yellow; ctx.shadowBlur = 14 * hi; }
      line(x - w / 2 + 34, ly, x - w / 2 + 34 + (w - 68) * lw, ly, c, key ? 9 : 7); ctx.restore();
    });
  });
}
function drawSection2(bt, t, hero) {
  if (bt < 17 || bt > 32.5) return;
  const out = 1 - seg(bt, 31.75, 32);
  // the page floats up out of his hand and stays beside his head
  const up = EASE.out(seg(bt, 17.5, 18.5));
  const px = lerp(hero.handF[0] + 60, PAGE2.x, up), py = lerp(hero.handF[1], PAGE2.y, up);
  if (bt < 32) withAlpha(popA(bt, 17.5, 0.4) * out, () => withScale(px, py, lerp(0.3, 1, up), () =>
    drawFloatingPage(px, py, PAGE2.w, PAGE2.h, { hi: 0.4 + 0.6 * win(bt, 18.5, 30.5, 0.5, 0.5) })));
  TAGS.forEach((tg, i) => {
    if (bt < tg.at) return;
    const fly = EASE.out(seg(bt, tg.at, tg.at + 0.8));
    const ox = PAGE2.x + 60, oy = PAGE2.y - PAGE2.h / 2 + 52 + (1 + 2 * i) * 44;
    const w = tagWidth(tg.s);
    let x = lerp(ox, tg.slot[0] + w / 2, fly), y = lerp(oy, tg.slot[1], fly);
    let sc = lerp(0.4, 1, fly) * popS(bt, tg.at, 0.6), a = popA(bt, tg.at, 0.25);
    if (bt > 31) {
      // ① flies to where the step-① header will be; all three are gone on the bar line (beat 32)
      // (left first, below the title, then up the left edge, so it never crosses the title text)
      const qx = EASE.inOut(seg(bt, 31, 31.6)), qy = EASE.inOut(seg(bt, 31.5, 32));
      if (i === 0) { x = lerp(tg.slot[0] + w / 2, 186, qx); y = lerp(tg.slot[1], 134, qy); sc = lerp(1, 0.6, qx); }
      a = 1 - seg(bt, 31.75, 32);
    }
    tagChip(x, y, tg.n, tg.s, { alpha: a, scale: sc, hi: win(bt, tg.at, tg.at + 1.4, 0.1, 1) });
  });
  // evidence card (12.4 s): whose voice is remembered best — Forrin & MacLeod 2018
  const ea = popA(bt, 26.5, 0.5) * out;
  if (ea > 0) withAlpha(ea, () => {
    const x = 1100, y = 778, w = 740, h = 196;
    rrect(x, y, w, h, 16, 'rgba(12,24,54,0.86)', 'rgba(143,232,248,0.45)', 2);
    txt('同一批单词，哪种学法认得出最多？', x + 26, y + 34, { size: 34, weight: 900, color: COL.cream });
    VOICES.forEach((v, i) => {
      const cx = x + 98 + i * 182, cy = y + 104, at = 26.5 + i * 0.5, sc = popS(bt, at, 0.5);
      if (sc <= 0) return;
      withScale(cx, cy, sc, () => {
        wordBlock(cx, cy, 150, 58, { solid: v.b > 0 ? 1 : 0, bright: v.b, glyph: false });
        txt(`${v.v}%`, cx, cy + 2, { size: 40, weight: 800, fam: 'mono', color: v.b > 0.5 ? INK : COL.cream, align: 'center' });
      });
      txt(v.s, cx, cy + 62, { size: 34, weight: 900, color: v.b > 0.5 ? COL.yellow : COL.grayHi, align: 'center', alpha: popA(bt, at, 0.3) });
      if (i < 3) txt('>', cx + 91, cy + 2, { size: 34, weight: 800, fam: 'mono', color: COL.gray, align: 'center', alpha: popA(bt, at + 0.5, 0.3) });
    });
  });
  const na = popA(bt, 28.5, 0.6) * out;
  if (na > 0) sourceNote('Forrin、MacLeod 2018 · 加拿大 75 名大学生 · 认出学过的词的比例', 1100, 994, { alpha: na });
}

// ---------- main ----------
function renderFrame(t) {
  const bt = t / BEAT;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  drawBackground(t);
  const info = { t, bt, hero: false };

  drawTitleBlock(bt, t);
  if (typeof drawPanelLayer === 'function') drawPanelLayer(bt, t);   // sections.js: things behind him

  const st = heroAt(bt);
  const fig = drawFigure({ x: st.x, y: st.y, s: st.s, dir: st.dir, pose: st.pose, style: 'B', pointF: false, alpha: st.alpha ?? 1 });
  const hero = { ...st, ...fig, mouth: [fig.head[0] + st.dir * 15 * st.s, fig.head[1] + 8 * st.s] };
  if (st.hold === 'sheet') drawSheet(hero, bt);
  info.hero = (st.alpha ?? 1) > 0.5;

  if (bt < 17.5) { drawOpening(bt, t, hero); drawFlights(bt, hero); }
  drawSection2(bt, t, hero);
  if (typeof drawSections === 'function') drawSections(bt, t, hero);

  drawChapterBar(bt);
  window.__frameInfo = info;
}
// the small word sheet in his front hand
function drawSheet(hero, bt) {
  const [hx, hy] = hero.handF;
  ctx.save(); ctx.translate(hx + hero.dir * 4, hy - 26); ctx.rotate(hero.dir * -0.12);
  ctx.shadowColor = COL.cyan; ctx.shadowBlur = 12;
  rrect(-30, -38, 60, 76, 6, 'rgba(14,30,66,0.85)', rgba(COL.cyanHi, 0.9), 2.5);
  ctx.shadowBlur = 0;
  for (let i = 0; i < 4; i++) line(-18, -22 + i * 14, i % 2 ? 8 : 16, -22 + i * 14, i % 2 ? 'rgba(255,213,126,0.85)' : 'rgba(200,212,236,0.6)', 4);
  ctx.restore();
}

// speech events for the stage wave (aloud words in the opening), from where he stands at that beat
for (const f of FLIGHTS) if (f.kind === 'aloud') addSpeech(f.b + 0.5, heroAt(f.b + 0.5).x, f.merge ? 0.8 : 1);
