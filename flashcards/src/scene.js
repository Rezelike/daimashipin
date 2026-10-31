// scene.js — timeline of 「单词卡分小叠背更好？」 (six/plan.md 第 6 条). All times in beats (bt). 128 BPM -> 1 beat =
// 0.46875 s; 160 beats = 75 s. Beat grid of 睡还是背 (lessons 13, six/plan.md): reveal 1 at beat 4.5 (2.11 s), reveal 2 at
// 8.5 (3.98 s), the check at 10.5 (4.92 s), the other label at 11.5 (5.39 s), the source at 13 (6.1 s), the answer from 17
// (8.0 s), the evidence card at 26.5 (12.4 s), steps at 32 / 64 / 96, the summary 128-160.
// One adult figure (kit/figure.js, look B = neon line) standing behind a card table like a dealer; never seated.
// Numbers: six/facts/06_flashcards.md (six-videos branch) = Kornell 2009 (Applied Cognitive Psychology 23:1297-1317) and
// Kornell & Bjork 2008 (Memory 16:125-136).
const TOTAL_BEATS = 160;
const HERO_S = 1.3;
const GROUND = 1028;    // his feet (hidden by the table): pelvis at ~742 = the table's back edge (TB.back 740)

// ---------- poses (absolute angles, see figure.js) ----------
const P_DECK = { uaF: 26, faF: 96, uaB: 18, faB: 84 };                    // the deck in both hands at the waist
const P_SPRING = { uaF: 55, faF: 96, uaB: 2, faB: 62 };                   // hands apart: cards spring from the low hand up
const P_PRESENT = { uaF: 66, faF: 70, uaB: 18, faB: 84, head: 6 };        // front hand open toward the small stacks
const P_WOW = { lean: -7, head: -14, uaB: -16, faB: 52, uaF: 34, faF: 150 };
const P_GATHER = { lean: 14, head: 12, uaF: 44, faF: 52, uaB: 34, faB: 46 };
const P_TOSS = { uaF: 84, faF: 92, uaB: 18, faB: 84, head: 2 };           // the flick that sends a card out
const withPose = (...ps) => Object.assign({}, POSES.stand, ...ps);
const poseMix = (a, b, t) => lerpPose(a, b, clamp(t));
// pose window: like win(), but the fade-out also starts fast, so every pose change begins ON its beat (rhythm check)
function pw(bt, a, b, fi = 0.5, fo = 0.5) {
  if (bt <= a || bt >= b) return 0;
  return Math.min(EASE.out(seg(bt, a, a + fi)), 1 - EASE.out(seg(bt, b - fo, b)));
}
function mixHex(a, b, t) {
  const A = hexToRgb(a), B = hexToRgb(b);
  return '#' + A.map((v, i) => Math.round(lerp(v, B[i], clamp(t))).toString(16).padStart(2, '0')).join('');
}
const mixPal = (a, b, t) => ({ c: mixHex(a.c, b.c, t), hi: mixHex(a.hi, b.hi, t) });

// ---------- the hook (0-17): one big deck of 20 vs four small stacks of 5 (Kornell 2009, Exp 3) ----------
// predictions after the first study day (24 people, p. 1308): small 66 %, big 51 %; test on day 6 (25 people, p. 1307):
// big 65 %, small 34 %. All three experiments: 63 of 70 people scored higher with the big deck (p. 1310).
const HOOK = { bigX: 430, smallX: [1265, 1415, 1565, 1715], smallC: 1490, base: 842, placY: 560 };
const hookA = (bt) => (bt < 17 ? 1 : 0);   // the hook's props cut out on the bar line, with the title flip
// the dealer's springs in the hook: [-0.5, 0.5], [0.5, 1.5], [1.5, 2.5], [2.5, 3.5] (frame 0 = mid-spring)
const SPRINGS_HOOK = [[-0.5, 0.5, 1], [0.5, 1.5, -1], [1.5, 2.5, 1], [2.5, 3.5, -1]];
// section 2: the four small stacks slide over to him (land 18.5 / 19 / 19.5 / 20), he lifts them as one deck
const MERGE = { x: 1120, y: 792 };
const MERGE_AT = [17.5, 18, 18.5, 19];
const mergeP = (bt, i) => EASE.inOut(seg(bt, MERGE_AT[i], MERGE_AT[i] + 1));
const SPRING_S2 = [20.5, 21.5, 1];
// overview tags, dealt to the left (he faces left from 21.5): launch, land 1 beat later
const TAGS = [
  { n: 1, s: '怎么叠', at: 22, pos: [430, 478] },
  { n: 2, s: '怎么排', at: 23.5, pos: [430, 604] },
  { n: 3, s: '怎么翻', at: 25, pos: [430, 730] },
];
// evidence card (12.4 s): after the first session, 42 of the 58 people who rated the two differently thought the small
// stacks worked better (72 %; abstract, p. 1310; three experiments together)
const EV = { x: 1166, y: 446, w: 690, h: 252 };

// ---------- the hero ----------
// x / facing / pose for every beat, plus what is in his hands: deck = { n, pal } in both hands, spring = [a, b, dir]
function heroAt(bt) {
  const st = { x: 960, y: GROUND, s: HERO_S, dir: 1, pose: withPose(P_DECK), deck: { n: 20, pal: BIG }, spring: null, bob: 0 };
  if (bt < 17) return heroHook(bt, st);
  if (bt < 32.5) return heroS2(bt, st);
  return heroSteps(bt, st);   // sections.js
}
// screen positions of his hands / head at any beat without drawing (a card thrown at beat L starts where his hand was
// at L, so it does not follow the hand afterwards); memoised per beat
const HANDS_MEMO = new Map();
function handsAt(bt) {
  const k = Math.round(bt * 1000);
  if (HANDS_MEMO.has(k)) return HANDS_MEMO.get(k);
  const st = heroAt(bt), p = { ...POSES.stand, ...st.pose };
  const J = rigJoints(p), py = pelvisHeight(p), s = st.s, dir = st.dir;
  const toS = (q) => [st.x + dir * s * q[0], st.y + (st.bob || 0) + s * (q[1] - py)];
  const r = { F: toS(J.armF[2]), B: toS(J.armB[2]), head: toS(J.head) };
  HANDS_MEMO.set(k, r);
  return r;
}
function springAt(bt, list) {
  for (const s of list) if (bt >= s[0] && bt < s[1]) return { p: (bt - s[0]) / (s[1] - s[0]), dir: s[2] };
  return null;
}
function heroHook(bt, st) {
  st.dir = bt < 9.5 ? 1 : bt < 14.5 ? -1 : 1;
  let p = withPose(P_DECK);
  const sp = springAt(bt, SPRINGS_HOOK);
  // springs until 3.5, then the deck is squared (4.0)
  const k = bt < 3.5 ? 1 : 1 - EASE.inOut(seg(bt, 3.5, 4));
  p = poseMix(p, withPose(P_SPRING), k);
  if (sp) st.spring = sp;
  p = poseMix(p, withPose(P_PRESENT), pw(bt, 5, 8.5, 0.5, 0.5));
  p = poseMix(p, withPose(P_WOW), pw(bt, 8.5, 10, 0.4, 0.5));
  p = poseMix(p, withPose(POSES.point, { uaB: 18, faB: 84 }), pw(bt, 10.5, 13, 0.5, 0.5));
  if (bt >= 14.5) p = poseMix(p, withPose(P_DECK, { lean: 6, head: 10 }), pw(bt, 14.5, 17.5, 0.5, 0.5));
  st.pose = p;
  // his own deck goes with the hook's props (on beat 17): his hands are free to gather the small stacks
  st.deck = { n: 20, pal: BIG, hands: 'both', alpha: hookA(bt) };
  return st;
}
function heroS2(bt, st) {
  st.dir = bt < 21.5 ? 1 : bt < 26 ? -1 : bt < 29.5 ? 1 : bt < 32.5 ? -1 : 1;
  let p = withPose(P_DECK);
  // he puts his own deck down (it fades with the hook) and gathers the four small stacks as they slide over
  p = poseMix(p, withPose(P_GATHER), pw(bt, 17, 20.5, 0.5, 0.5));
  const lifted = bt >= 20;
  st.deck = lifted ? { n: 20, pal: mixPal(SMALL, BIG, seg(bt, 20, 20.5)), hands: 'both' } : null;
  const sp = springAt(bt, [SPRING_S2]);
  if (sp) { st.spring = sp; st.deck.hands = 'spring'; }
  p = poseMix(p, withPose(P_SPRING), pw(bt, 20.5, 22, 0.25, 0.5));
  // deals the three tags to the left: a flick on each launch
  for (const tg of TAGS) p = poseMix(p, withPose(P_TOSS), pw(bt, tg.at - 0.5, tg.at + 1, 0.5, 0.5));
  // looks over at the evidence card
  if (bt >= 26.5 && bt < 29.5) p = poseMix(p, withPose(P_DECK, { head: -4, lean: -2 }), pw(bt, 26.5, 29.5, 0.5, 0.5));
  // walks behind the table to the left side (x 300) for the steps: his legs are hidden, the body bobs once per beat
  if (bt >= 29.5) {
    const w = seg(bt, 29.5, 32.5);
    st.x = lerp(960, 300, EASE.inOut(w));
    st.bob = -5 * Math.abs(Math.sin(Math.PI * (bt - 29.5))) * Math.sin(Math.PI * w);
    p = poseMix(withPose(P_DECK), withPose(walkPose(bt - 29.5, 0.5), P_DECK), Math.sin(Math.PI * w));
  }
  st.pose = p;
  return st;
}

// ---------- the title block (0-32): question, then the answer (the second line turns over like a card at 17) ----------
function drawTitleBlock(bt) {
  const outA = bt < 32 ? 1 : 0;
  if (outA <= 0) return;
  withAlpha(outA, () => {
    txt('单词卡', 960, 150, { size: 100, weight: 900, color: COL.cream, align: 'center' });
    const y2 = 288, f = seg(bt, 16.5, 17.5), sy = Math.abs(Math.cos(Math.PI * f));
    ctx.save(); ctx.translate(960, y2); ctx.scale(1, Math.max(0.02, sy)); ctx.translate(-960, -y2);
    const a = clamp(sy * 1.6);
    if (f < 0.5) rich([{ s: '分小叠', color: COL.cyan, glow: 26 }, { s: '背更好？' }], 960, y2, { size: 142, weight: 900, align: 'center', alpha: a });
    else rich([{ s: '洗成' }, { s: '一大叠', color: COL.yellow, glow: 28 }, { s: '，分几天过' }], 960, y2, { size: 128, weight: 900, align: 'center', alpha: a });
    ctx.restore();
    const en1 = 'Smaller flashcard stacks work better?', en2 = 'One big deck, over several days.';
    const second = bt >= 17, s = second ? en2 : en1;
    const fw = measure(s, 34, 500, 'mono');
    const p1 = second ? seg(bt, 17.25, 20) : lerp(8 / en1.length, 1, seg(bt, 0, 2.4));
    typeText(s, p1, 960 - fw / 2, 388, { size: 34, weight: 500, fam: 'mono', color: COL.cyan, keepCursor: true }, bt);
  });
}

// ---------- hook drawing ----------
// on the felt: the two arrangements, their printed labels, the 63-of-70 line, the source
function drawHookTable(bt) {
  const A = hookA(bt);
  const flipped = bt >= 8.5;
  if (A > 0) {
    deckStack(HOOK.bigX, HOOK.base, 20, { pal: BIG, alpha: A, lit: flipped ? 0.7 * win(bt, 8.5, 16.5, 0.5, 0.5) : 0 });
    feltText('一大叠 · 20 张', HOOK.bigX, 912, { color: BIG.c, alpha: A });
    feltText('四小叠 · 每叠 5 张', HOOK.smallC, 912, { color: SMALL.c, alpha: A });
    const ma = popA(bt, 11.5, 0.35) * A;
    if (ma > 0) feltText('三个实验 70 人里，63 人大叠分更高', 960, 912, { size: 36, color: COL.cream, alpha: ma });
    sourceNote('Kornell 2009 实验 3 · 美国 25 名大学生 · GRE 难词', 960, 984, { align: 'center', alpha: popA(bt, 13, 0.8) * A });
  }
  // the four small stacks stay until they slide over to him in section 2
  HOOK.smallX.forEach((x, i) => {
    if (bt > MERGE_AT[i] + 1) return;
    const m = mergeP(bt, i);
    const cx = lerp(x, MERGE.x, m), cy = lerp(HOOK.base, MERGE.y, m);
    const dim = flipped && bt < 17 ? 0.35 * win(bt, 8.5, 16.5, 0.5, 0.5) : 0;
    const lit = bt < 8.5 ? 0.6 * win(bt, 4.5, 8.5, 0.2, 0.25) : 0;
    deckStack(cx, cy, 5, { pal: SMALL, lit, alpha: 1 - dim });
  });
  // the merged pile in front of him (5, 10, 15, 20 cards as the stacks land), until he lifts it
  if (bt >= MERGE_AT[0] + 1 && bt < 20) {
    let n = 0; MERGE_AT.forEach((a) => { if (bt >= a + 1) n += 5; });
    deckStack(MERGE.x, MERGE.y, n, { pal: SMALL, lit: 0.4 });
  }
}
// the big standing cards: 「我估计能记住」 (reveal 1) turn over to the test score (reveal 2)
function hookCaption(bt) {
  const a = popA(bt, 4.5, 0.3) * hookA(bt);
  if (a <= 0) return;
  const f = seg(bt, 8.5, 9.0), sy = Math.abs(Math.cos(Math.PI * f)), y = 440;
  const s = f < 0.5 ? '第 1 天学完，大家估计' : '第 6 天考试';
  const w = measure(s, 42, 900);
  withAlpha(a * clamp(sy * 1.6), () => {
    ctx.save(); ctx.translate(960, y); ctx.scale(1, Math.max(0.02, sy)); ctx.translate(-960, -y);
    txt(s, 960, y, { size: 42, weight: 900, color: COL.cream, align: 'center' });
    ctx.restore();
  });
  withAlpha(a, () => {
    line(960 - w / 2 - 110, y + 2, 960 - w / 2 - 26, y + 2, rgba(COL.cream, 0.45), 2.5);
    line(960 + w / 2 + 26, y + 2, 960 + w / 2 + 110, y + 2, rgba(COL.cream, 0.45), 2.5);
  });
}
function drawHookFront(bt, hero) {
  const A = hookA(bt);
  if (A <= 0 || bt < 4.4) return;
  withAlpha(A, () => {
    const sc = popS(bt, 4.5, 0.6), pa = popA(bt, 4.5, 0.3);
    const flip = EASE.inOut(seg(bt, 8.5, 9.0)), valueP = seg(bt, 4.5, 5.2);
    const after = flip >= 0.5;
    placard(HOOK.bigX, HOOK.placY, { pal: BIG, tab: '一大叠', front: { head: '我估计能记住', value: 51 }, back: { head: '考试答对', value: 65 },
      flip, lit: after ? 0.4 + 0.6 * win(bt, 8.5, 10.5, 0.25, 1.0) : 0, alpha: pa, scale: sc, valueP });
    placard(HOOK.smallC, HOOK.placY, { pal: SMALL, tab: '四小叠', front: { head: '我估计能记住', value: 66 }, back: { head: '考试答对', value: 34 },
      flip, lit: after ? 0 : 0.45 + 0.55 * win(bt, 4.5, 5.6, 0.05, 0.9), dim: after ? 1 : 0, alpha: pa, scale: sc, valueP });
    // ✓ 赢了 at the big card's left edge (4.92 s)
    const cx = HOOK.bigX - PLAC.w / 2 + 2, cy = HOOK.placY + 10, cs = popS(bt, 10.5, 0.6);
    if (cs > 0) withScale(cx, cy, cs, () => okMark(cx, cy, 30, seg(bt, 10.5, 11.2)));
    const la = popA(bt, 10.5, 0.35);
    if (la > 0) txt('赢了', cx - 42 + (1 - la) * 20, cy + 2, { size: 50, weight: 900, color: COL.yellow, alpha: la, glow: 16, align: 'right' });
    sparkleBurst(cx, cy, seg(bt, 10.5, 12), COL.yellow);
  });
  hookCaption(bt);
}

// ---------- section 2 drawing (17-32) ----------
function drawS2Front(bt, hero) {
  if (bt < 21.5 || bt > 32.5) return;
  const out = bt < 32 ? 1 : 0;
  // the three tags: dealt face down from his hand, turning face up as they land
  TAGS.forEach((tg, i) => {
    if (bt < tg.at) return;
    const e = EASE.out(seg(bt, tg.at, tg.at + 1));
    const w = tagCardW(tg.s), h0 = handsAt(tg.at).F;
    let x = lerp(h0[0] - 20, tg.pos[0], e), y = lerp(h0[1], tg.pos[1], e) - Math.sin(Math.PI * e) * 70;
    let sc = lerp(0.3, 1, e), a = popA(bt, tg.at, 0.2);
    const flip = 1 - EASE.inOut(seg(bt, tg.at + 0.5, tg.at + 1));
    if (bt > 31) {
      // ① becomes the index card of the step-① header (top left); ② ③ fade on the bar line
      // (left first, then up the left edge, so it never crosses the title)
      const qx = EASE.inOut(seg(bt, 31, 31.5)), qy = EASE.inOut(seg(bt, 31.5, 32));
      if (i === 0) { x = lerp(tg.pos[0], 178, qx); y = lerp(tg.pos[1], 134, qy); sc = lerp(1, 0.55, qx); }
      a *= bt < 32 ? 1 : 0;
    }
    if (flip > 0.5) withAlpha(a, () => withScale(x, y, sc, () => uprightCard(x, y, w, 118, { pal: BIG, flip: 1, back: plainFace(BIG), front: null, r: 16 })));
    else {
      const sx = Math.abs(Math.cos(Math.PI * flip));
      withAlpha(a, () => { ctx.save(); ctx.translate(x, y); ctx.scale(Math.max(0.03, sx), 1); ctx.translate(-x, -y);
        tagCard(x, y, tg.n, tg.s, { scale: sc, lit: win(bt, tg.at + 1, tg.at + 2.5, 0.1, 1) }); ctx.restore(); });
    }
  });
  // evidence card (12.4 s): what people believed after the first session
  const ea = popA(bt, 26.5, 0.4) * out, es = lerp(0.85, 1, EASE.back(seg(bt, 26.5, 27.1)));
  if (ea > 0) withAlpha(ea, () => withScale(EV.x + EV.w / 2, EV.y + EV.h / 2, es, () => {
    ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 22;
    rrect(EV.x, EV.y, EV.w, EV.h, 18, 'rgba(12,24,54,0.94)', rgba(COL.cyanHi, 0.7), 2.6); ctx.restore();
    txt('第一轮学完：估计有高低的 58 人里', EV.x + 30, EV.y + 44, { size: 34, weight: 900, color: COL.grayHi });
    voteStrip(EV.x + 30, EV.y + 96, 58, 42, seg(bt, 27, 28.5), { cols: 29, cw: 15, ch: 22, gap: 6, pal: SMALL });
    const ra = popA(bt, 28.5, 0.35);
    if (ra > 0) rich([{ s: '42 人（72%）觉得' }, { s: '小叠', color: COL.cyan, glow: 14 }, { s: '记得更多' }], EV.x + 30, EV.y + 180,
      { size: 40, weight: 900, alpha: ra });
    sourceNote('Kornell 2009 · 三个实验合计 · 学完第一轮时的估计', EV.x + 30, EV.y + 226, { alpha: popA(bt, 29, 0.6) });
  }));
}

// ---------- the dealer: figure clipped at the table edge, the table, then his arms where they reach over the felt ----------
function drawArmsOverTable(o) {
  const p = { ...POSES.stand, ...o.pose };
  const J = rigJoints(p), py = pelvisHeight(p), s = o.s ?? 1, dir = o.dir ?? 1;
  ctx.save(); ctx.beginPath(); ctx.rect(0, TB.back, W, H - TB.back); ctx.clip();
  ctx.translate(o.x, o.y); ctx.scale(dir * s, s); ctx.translate(0, -py); ctx.rotate((p.rot || 0) * D2R);
  const stroke = (pts, w, a) => withAlpha(a, () => { ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 16; polyline(pts, w, COL.cream); ctx.restore(); });
  stroke(J.armB, 9, 0.45); stroke(J.armF, 9, 1);
  ctx.restore();
}
// what is in his hands: the deck between both hands, or the spring between them
// hands: 'both' (between the hands), 'B' (back hand only: the front hand deals / shows a card), 'spring', 'fan' (drawn by
// sections.js), 'none'
function drawHeld(bt, hero) {
  const d = hero.deck;
  if (!d || d.hands === 'none' || d.hands === 'fan') return;
  const A = d.alpha ?? 1;
  if (A <= 0.003) return;
  withAlpha(A, () => {
    if (hero.spring) {
      const { p, dir } = hero.spring;
      const lo = [hero.handB[0] + hero.dir * 6, hero.handB[1] - 6], hi = [hero.handF[0], hero.handF[1] - 10];
      const [a, b] = dir > 0 ? [lo, hi] : [hi, lo];
      handDeck(a[0], a[1], 20 * (1 - p), { pal: d.pal, w: 84 });
      handDeck(b[0], b[1], 20 * p, { pal: d.pal, w: 84 });
      cardSpring(a, b, p, { pal: d.pal, lift: 92 });
      return;
    }
    if (d.hands === 'B') { handDeck(hero.handB[0] + hero.dir * 10, hero.handB[1] - 10, d.n, { pal: d.pal, w: 100, tilt: hero.dir * -0.1 }); return; }
    const mid = [(hero.handF[0] + hero.handB[0]) / 2, (hero.handF[1] + hero.handB[1]) / 2 - 8];
    handDeck(mid[0], mid[1], d.n, { pal: d.pal, w: 110, tilt: hero.dir * -0.06 });
  });
}

// ---------- main ----------
function renderFrame(t) {
  const bt = t / BEAT;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  drawBackground(t);
  const info = { t, bt, hero: false };

  drawTitleBlock(bt);
  if (typeof drawSectionsBack === 'function') drawSectionsBack(bt, t);   // sections.js: above the table, behind him

  const st = heroAt(bt);
  const figO = { x: st.x, y: st.y + (st.bob || 0), s: st.s, dir: st.dir, pose: st.pose, style: 'B', shadow: false, alpha: st.alpha ?? 1 };
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, TB.back); ctx.clip();
  const fig = drawFigure(figO);
  ctx.restore();
  info.hero = (st.alpha ?? 1) > 0.5;
  const hero = { ...st, ...fig, mouth: [fig.head[0] + st.dir * 15 * st.s, fig.head[1] + 8 * st.s] };

  drawTable();
  if (bt < 20.5) drawHookTable(bt);
  if (typeof drawSectionsTable === 'function') drawSectionsTable(bt, t, hero);   // sections.js: on the felt
  drawArmsOverTable(figO);
  drawHeld(bt, hero);

  if (bt < 17) drawHookFront(bt, hero);
  drawS2Front(bt, hero);
  if (typeof drawSectionsFront === 'function') drawSectionsFront(bt, t, hero);

  drawChapterBar(bt);
  window.__frameInfo = info;
}
