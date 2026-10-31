// sections.js — 怎么背 ① ② ③ (32-128) and 照着做 (128-160). Each step opens on the action (no STEP page): its header
// is a corner-index card that turns over, the line slides out from behind it as if dealt. He stands behind the table on
// the left (x 300) for all of it. Numbers only from six/facts/06_flashcards.md.

// ---------- headers ----------
const ink = (s, color = COL.cream) => ({ s, color });
const HEADERS = [
  { from: 32, to: 64, num: 1, spans: [ink('整批洗成'), ink('一大叠', COL.yellow), ink('，从头发到尾再来')],
    en: 'One deck: first card to last, then start again.' },
  { from: 64, to: 96, num: 2, spans: [ink('同一叠'), ink('分几天', COL.yellow), ink('过，每天一两遍')],
    en: 'The same deck over several days, once or twice a day.' },
  { from: 96, to: 128, num: 3, spans: [ink('先'), ink('说出答案', COL.yellow), ink('再翻；答对了也放回叠底')],
    en: 'Say it, then flip. Right? Back to the bottom.' },
  { from: 128, to: 161, num: null, spans: [ink('照着做')], en: 'Flashcards? Do this.' },
];
function drawHeaders(bt) {
  for (const h of HEADERS) {
    if (bt < h.from || bt > h.to) continue;
    const outP = bt < h.to ? 0 : 1, a = 1 - outP, dx = 0;
    const x0 = h.num ? 252 : 140;
    withAlpha(a, () => {
      if (h.num) indexCard(178 + dx, 134, h.num, { w: 88, h: 118, flip: 1 - EASE.inOut(seg(bt, h.from, h.from + 0.5)) });
      // the line slides out from behind the card (clip grows to the right)
      const spans = h.spans.map((sp) => ({ ...sp, glow: sp.color !== COL.cream ? 18 : 0 }));
      const total = richWidth(spans, 64, 900), p = EASE.out(seg(bt, h.from + 0.5, h.from + 1.5));
      ctx.save(); ctx.beginPath(); ctx.rect(x0 - 10 + dx, 60, (total + 20) * p, 110); ctx.clip();
      rich(spans, x0 + dx - (1 - p) * 60, 118, { size: 64, weight: 900 });
      ctx.restore();
      typeText(h.en, seg(bt, h.from + 1, h.from + 4), x0 + 2 + dx, 190, { size: 34, weight: 500, fam: 'mono', color: COL.cyan }, bt);
    });
  }
}

// ---------- hero in the steps ----------
const P_DEAL = (k) => ({ uaF: lerp(44, 74, k), faF: lerp(66, 86, k), uaB: 16, faB: 80, lean: lerp(4, 10, k), head: lerp(10, 4, k) });
const P_SHOW = { uaF: 68, faF: 80, uaB: 16, faB: 80, head: -2 };     // a card held up beside him, deck in the other hand
const P_FAN = { uaF: 58, faF: 118, uaB: 12, faB: 40, head: -4 };
const P_FAN_UP = { uaF: 104, faF: 126, uaB: 12, faB: 40, head: -10, lean: -3 };
const POINT_D = { ...POSES.point, uaB: 16, faB: 80 };                 // points with the free hand, deck in the other
// ① the 21 cards he deals: launch every half beat from 34, each slides for one beat
const SP = { x0: 620, dx: 55, yA: 792, yB: 880, w: 96 };
const DEAL1 = Array.from({ length: 21 }, (_, i) => 34 + 0.5 * i);
// ② days: four study days of 4 beats from 66, the test on day 5 at 82; the big deck goes through his hands twice a day
const DAY0 = 66, DAYS = [66, 70, 74, 78], TEST_DAY = 82;
const SPRINGS_2 = DAYS.flatMap((d, i) => [[d + 0.5, d + 1.5, 1], [d + 2, d + 3, -1]]);
// ③ two cards: [draw, say, flip, back]
const CARDS3 = [
  { draw: 97.5, say: 100, flip: 101.5, back: 103.5, front: 'effulgent', ans: 'brilliant', said: 'brilliant!' },
  { draw: 106, say: 107, flip: 108, back: 109.5, front: 'lucid', ans: 'clear', said: 'clear!' },
];
// summary: three cards dealt face up (launch 0.5 beat before they land on 130 / 134 / 138)
const SUMC = [
  { x: 760, w: 330, at: 130, s: '一大叠', sub: '别拆成小叠' },
  { x: 1175, w: 330, at: 134, s: '分几天', sub: '每天一两遍' },
  { x: 1615, w: 420, at: 138, s: '说出答案再翻', sub: '答对也放回叠底' },
];
const SUM_Y = 440, SUM_H = 200;
const SUM_SHOW = { draw: 138.5, flip: 139.5, back: 141.5 };
const SPRING_SUM = [134.5, 135.5, 1];

function heroSteps(bt, st) {
  st.x = 300; st.dir = 1; st.deck = { n: 20, pal: BIG, hands: 'both' };
  let p = withPose(P_DECK);
  if (bt < 64) {
    // ① deals the whole deck card by card along the table, then points at the result, then sweeps the cards back
    if (bt >= 33.5 && bt < 45.5) {
      st.deck.hands = 'B';
      const i = clamp(Math.floor((bt - 34) / 0.5), 0, 20), k = i / 20;
      const flick = bt >= 34 ? 1 - EASE.out(seg(bt, DEAL1[i], DEAL1[i] + 0.4)) : 0;
      const d = P_DEAL(k); d.faF += 12 * flick; d.uaF += 4 * flick;
      p = poseMix(p, withPose(d), pw(bt, 33.5, 45.5, 0.5, 0.5));
    }
    p = poseMix(p, withPose(POINT_D), pw(bt, 54, 58, 0.5, 0.5));
    p = poseMix(p, withPose(P_GATHER), pw(bt, 60, 62, 0.5, 0.5));
  } else if (bt < 96) {
    // ② each study day the whole deck goes through his hands twice (two springs); points at the scores
    const sp = springAt(bt, SPRINGS_2);
    if (sp) { st.spring = sp; st.deck.hands = 'spring'; }
    for (const d of DAYS) p = poseMix(p, withPose(P_SPRING), pw(bt, d, d + 3.5, 0.5, 0.5));
    p = poseMix(p, withPose(POINT_D), pw(bt, 90, 94, 0.5, 0.5));
  } else if (bt < 128) {
    // ③ draws a card, says the answer, turns the card over, puts it back under the deck — twice
    for (const c of CARDS3) {
      const w = pw(bt, c.draw, c.back + 1, 0.5, 0.5);
      p = poseMix(p, withPose(P_SHOW), w);
      if (bt >= c.say && bt < c.say + 1) p = poseMix(p, withPose(P_SHOW, { head: -12, lean: -3 }), pw(bt, c.say, c.say + 1, 0.25, 0.5));
      if (bt >= c.draw && bt < c.back + 1) st.deck.hands = 'B';
    }
    p = poseMix(p, withPose(P_DECK, { head: 14, lean: 6 }), pw(bt, 112, 115, 0.5, 0.5));
    p = poseMix(p, withPose(POINT_D), pw(bt, 119, 123, 0.5, 0.5));
  } else {
    // 照着做: deals the three cards, acts each (squares the deck / one pass / says + turns a card), fans the deck, points
    for (const c of SUMC) {
      p = poseMix(p, withPose(P_TOSS), pw(bt, c.at - 1, c.at + 0.5, 0.5, 0.5));
      if (bt >= c.at - 1 && bt < c.at + 0.5) st.deck.hands = 'B';
    }
    if (bt >= 130.5 && bt < 132) p = poseMix(p, withPose(P_DECK, { lean: 8, head: 12, uaF: 30, uaB: 22 }), pw(bt, 131, 132, 0.2, 0.5));
    const sp = springAt(bt, [SPRING_SUM]);
    if (sp) { st.spring = sp; st.deck.hands = 'spring'; }
    p = poseMix(p, withPose(P_SPRING), pw(bt, SPRING_SUM[0] - 0.5, SPRING_SUM[1] + 0.5, 0.5, 0.5));
    p = poseMix(p, withPose(P_SHOW), pw(bt, SUM_SHOW.draw, SUM_SHOW.back + 1, 0.5, 0.5));
    if (bt >= SUM_SHOW.draw && bt < SUM_SHOW.back + 1) st.deck.hands = 'B';
    if (bt >= 147.5) {
      st.deck.hands = 'fan';
      p = poseMix(p, withPose(P_FAN), EASE.inOut(seg(bt, 147.5, 148.5)));
      p = poseMix(p, withPose(P_FAN_UP), EASE.inOut(seg(bt, 150, 151)));
    }
  }
  st.pose = p;
  return st;
}

// ---------- ① 怎么叠: deal the whole deck along the table, the same card comes back after 19 others ----------
const slotX = (i) => SP.x0 + SP.dx * i;
function step1Fade(bt) { return bt < 64 ? 1 : 0; }
function drawStep1Table(bt, hero) {
  if (bt < 33.5 || bt > 64) return;
  const clear = EASE.inOut(seg(bt, 60, 61.5));        // the cards slide back to him
  const home = [500, 770];
  // row A: the big deck, dealt one by one (the same card first and last = yellow); each card leaves his hand and
  // slides over the felt to its place
  for (let i = 0; i < 21; i++) {
    const L = DEAL1[i];
    if (bt < L) continue;
    const e = EASE.out(seg(bt, L, L + 1)), h0 = handsAt(L).F;
    let x = lerp(h0[0] + 10, slotX(i), e), y = lerp(h0[1] + 14, SP.yA, EASE.out(clamp(e * 2.2)));
    if (clear > 0) { x = lerp(slotX(i), home[0], clear); y = lerp(SP.yA, home[1], clear); }
    const same = i === 0 || i === 20;
    flatCard(x, y, SP.w, { pal: BIG, solid: same ? 1 : 0, lit: same ? 0.6 : 0, alpha: (1 - seg(clear, 0.8, 1)) * popA(bt, L, 0.15) });
  }
  // row B: four small stacks — the first card comes back after 4 others (A at 0, 5, 10, 15; slot 20 = the next stack)
  const bA = popA(bt, 48, 0.3) * (1 - EASE.out(seg(bt, 60, 61)));
  if (bA > 0) for (let i = 0; i < 21; i++) {
    const a = popA(bt, 48 + i * 0.04, 0.2);
    const same = i % 5 === 0 && i < 20;
    flatCard(slotX(i), SP.yB, SP.w, { pal: i === 20 ? DIMC : SMALL, solid: same ? 1 : 0, lit: same ? 0.5 : 0, alpha: bA * a });
  }
  // hop arrows: A: 0 -> 20 (19 cards in between); B: 0 -> 5 -> 10 -> 15
  const fa = 1 - EASE.out(seg(bt, 60, 60.75));
  hopArrow(slotX(0), slotX(20), SP.yA - 24, 70, seg(bt, 45.5, 46.5), COL.yellow, { alpha: fa });
  for (let k = 0; k < 3; k++) hopArrow(slotX(5 * k), slotX(5 * k + 5), SP.yB - 22, 20, seg(bt, 48.5 + 0.5 * k, 49 + 0.5 * k), COL.cyan, { alpha: fa * bA, lw: 3.5 });
  const lb = popA(bt, 50, 0.35) * fa;
  if (lb > 0) rich([ink('四小叠：', COL.cyan), ink('隔 4 张', COL.cyanHi), ink('就回来', COL.cyan)], SP.x0 - SP.w / 2, 926, { size: 34, weight: 900, alpha: lb });
}
function drawStep1Front(bt, hero) {
  if (bt < 32 || bt > 64) return;
  const out = step1Fade(bt), fa = 1 - EASE.out(seg(bt, 60, 60.75));
  const la = popA(bt, 46.5, 0.35) * fa * out;
  if (la > 0) rich([ink('一大叠：同一张', COL.yellow), ink('隔 19 张', COL.yellowHi), ink('才回来', COL.yellow)], slotX(10), 652,
    { size: 40, weight: 900, align: 'center', alpha: la });
  withAlpha(out, () => {
    const ha = popA(bt, 51, 0.35);
    if (ha > 0) txt('遍数、时间都一样', 1240, 296, { size: 42, weight: 900, color: COL.grayHi, align: 'center', alpha: ha });
    scoreLine(1020, 400, '一大叠', 49, BIG, { alpha: popA(bt, 52, 0.3), p: seg(bt, 52, 52.6), lit: 0.6 });
    scoreLine(1460, 400, '四小叠', 36, SMALL, { alpha: popA(bt, 52.5, 0.3), p: seg(bt, 52.5, 53.1) });
    const cs = popS(bt, 53.5, 0.6);
    if (cs > 0) withScale(1150, 368, cs, () => okMark(1150, 368, 26, seg(bt, 53.5, 54.2)));
    sparkleBurst(1150, 368, seg(bt, 53.5, 55), COL.yellow);
    sourceNote('Kornell 2009 实验 1 · 20 名大学生 · 每张卡都过 4 遍，花的时间也一样 · 约 1 天后考', 1240, 552,
      { align: 'center', alpha: popA(bt, 54.5, 0.6) });
  });
}

// ---------- ② 怎么排: the same deck over four days vs a new small stack every day ----------
const LANE_B = { x: [1150, 1330, 1510, 1690], base: 842 };
const STAND = { x: 800, y: 800, w: 300 };
const DAY_LABELS = ['第 1 天', '第 2 天', '第 3 天', '第 4 天', '第 5 天考试'];
function dayIdx(bt) {
  let idx = 0;
  [70, 74, 78, TEST_DAY].forEach((b) => { idx += EASE.inOut(seg(bt, b, b + 0.5)); });
  return idx;
}
function drawStep2Table(bt, hero) {
  if (bt < 64 || bt > 96) return;
  const A = popA(bt, 65, 0.4) * (bt < 96 ? 1 : 0);
  if (A <= 0) return;
  withAlpha(A, () => {
    // the four small stacks: stack k is studied on day k only, 8 times in a row
    LANE_B.x.forEach((x, k) => {
      const d = DAYS[k], active = bt >= d && bt < d + 4;
      const lit = win(bt, d, d + 4, 0.15, 0.5) + (k === 3 ? 0.9 * win(bt, 86.5, 95.5, 0.2, 0.5) : 0);
      const done = bt >= d + 4;
      const ty = deckStack(x, LANE_B.base - (active ? 10 * EASE.out(seg(bt, d, d + 0.3)) * (1 - seg(bt, d + 3.5, d + 4)) : 0), 5,
        { pal: done && k < 3 ? mixPal(SMALL, DIMC, 0.6) : SMALL, lit: clamp(lit), w: 120 });
      if (active) {
        const n = Math.min(8, Math.floor((bt - d) * 2) + 1), q = ((bt - d) * 2) % 1;
        loopArrow(x, ty, 92, 36, q, COL.cyanHi, { lw: 4 });
        txt(`×${n}`, x, ty - 70, { size: 46, weight: 800, fam: 'mono', color: COL.cyanHi, align: 'center', glow: 12, glowColor: COL.cyan });
      }
    });
    dayStand(STAND.x, STAND.y, DAY_LABELS, dayIdx(bt), { w: STAND.w, alpha: popA(bt, 65.5, 0.3), lit: bt >= TEST_DAY ? 0.6 : 0.2 });
    feltText('一大叠：每天 2 遍', 430, 912, { color: BIG.c, alpha: popA(bt, 66, 0.3) });
    feltText('四小叠：每天换一叠，当天 8 遍', 1420, 912, { color: SMALL.c, alpha: popA(bt, 66.5, 0.3) });
    const na = popA(bt, 86.5, 0.35);
    if (na > 0) rich([ink('考前一天才背的那叠：只有 ', COL.cyan), ink('34%', COL.cyanHi)], 1520, 764, { size: 36, weight: 900, align: 'center', alpha: na });
  });
}
function drawStep2Front(bt, hero) {
  if (bt < 64 || bt > 96) return;
  const out = bt < 96 ? 1 : 0;
  withAlpha(out, () => {
    // the passes of the day for the big deck: ×1, ×2 over his hands
    if (bt >= DAY0 && bt < TEST_DAY) {
      const d = DAYS[clamp(Math.floor((bt - DAY0) / 4), 0, 3)], n = bt >= d + 2 ? 2 : bt >= d + 0.5 ? 1 : 0;
      if (n > 0) txt(`×${n}`, 610, 560, { size: 52, weight: 800, fam: 'mono', color: COL.yellowHi, align: 'center', glow: 14, glowColor: COL.yellow,
        alpha: popA(bt, n === 1 ? d + 0.5 : d + 2, 0.2) });
    }
    scoreLine(640, 400, '一大叠', 54, BIG, { alpha: popA(bt, 83, 0.3), p: seg(bt, 83, 83.6), lit: 0.6 });
    scoreLine(1420, 400, '四小叠', 21, SMALL, { alpha: popA(bt, 84, 0.3), p: seg(bt, 84, 84.6) });
    const cs = popS(bt, 85, 0.6);
    if (cs > 0) withScale(770, 368, cs, () => okMark(770, 368, 26, seg(bt, 85, 85.7)));
    sparkleBurst(770, 368, seg(bt, 85, 86.5), COL.yellow);
    sourceNote('Kornell 2009 实验 2 · 25 名大学生 · 每张卡都过 8 遍 · 第 5 天考', 1030, 552, { align: 'center', alpha: popA(bt, 88, 0.6) });
  });
}

// ---------- ③ 怎么翻: say the answer, then turn the card; right or not, it goes back under the deck ----------
const C3 = { x: 630, y: 566, w: 300, h: 188 };
const TRAY = { x: 1180, y: 826 }, KEEP = { x: 1620, base: 846 };
function drawStep3Table(bt, hero) {
  if (bt < 111.5 || bt > 128) return;
  const A = bt < 128 ? 1 : 0;
  withAlpha(A, () => {
    const ta = popA(bt, 112, 0.35);
    discardTray(TRAY.x, TRAY.y, { alpha: ta, w: 220, h: 70 });
    deckStack(KEEP.x, KEEP.base, 20, { pal: BIG, alpha: ta, lit: 0.6 * win(bt, 115.5, 127.5, 0.3, 0.5), w: 130 });
    // a card that was right once goes into the tray (what not to do)
    if (bt >= 112.5) {
      const e = EASE.inOut(seg(bt, 112.5, 113.5));
      flatCard(lerp(KEEP.x - 160, TRAY.x, e), lerp(KEEP.base - 90, TRAY.y - 2, e) - Math.sin(Math.PI * e) * 40, 110, { pal: DIMC, alpha: popA(bt, 112.5, 0.2) });
    }
    const xs = popS(bt, 113.5, 0.6);
    if (xs > 0) withScale(TRAY.x + 128, TRAY.y - 26, xs, () => noMark(TRAY.x + 128, TRAY.y - 26, 24));
  });
}
function card3State(bt, c) {
  // position: from the deck (in his back hand) up to C3, then back down under the deck
  if (bt < c.draw || bt > c.back + 1) return null;
  const up = EASE.out(seg(bt, c.draw, c.draw + 1)), down = EASE.inOut(seg(bt, c.back, c.back + 1));
  return { up, down, flip: EASE.inOut(seg(bt, c.flip, c.flip + 0.5)) };
}
function drawStep3Front(bt, hero) {
  if (bt < 96 || bt > 128) return;
  const out = bt < 128 ? 1 : 0;
  withAlpha(out, () => {
    for (const c of CARDS3) {
      const s = card3State(bt, c);
      if (!s) continue;
      const deck = [hero.handB[0] + 8, hero.handB[1] - 12];
      const x = lerp(lerp(deck[0], C3.x, s.up), deck[0], s.down), y = lerp(lerp(deck[1], C3.y, s.up), deck[1] + 8, s.down);
      const sc = lerp(lerp(0.3, 1, s.up), 0.25, s.down);
      const right = bt >= c.flip + 0.5;
      withScale(x, y, sc, () => uprightCard(x, y, C3.w, C3.h, { pal: BIG, flip: s.flip, lit: right ? 0.5 : 0, alpha: 1 - seg(s.down, 0.75, 1),
        front: wordFace(c.front, { size: 52, sub: '英语难词', subColor: COL.grayHi }), back: wordFace(c.ans, { size: 52, color: COL.yellowHi, sub: '意思' }) }));
      // he says it first
      const ba = win(bt, c.say, c.back, 0.2, 0.5);
      if (ba > 0) speechBubble(660, 384, c.said, hero.mouth, { alpha: ba, scale: lerp(0.6, 1, EASE.back(seg(bt, c.say, c.say + 0.4))), size: 48 });
      const cs = popS(bt, c.flip + 0.5, 0.6) * (1 - seg(bt, c.back, c.back + 0.3));
      if (cs > 0) withScale(C3.x + C3.w / 2 + 34, C3.y - C3.h / 2 + 10, cs, () => okMark(C3.x + C3.w / 2 + 34, C3.y - C3.h / 2 + 10, 28, seg(bt, c.flip + 0.5, c.flip + 1.2)));
    }
    // 放回叠底
    const ra = win(bt, 104.5, 111.5, 0.35, 0.5);
    if (ra > 0) rich([ink('答对了也'), ink('放回叠底', COL.yellow)], C3.x - 70, 680, { size: 40, weight: 900, alpha: ra });
    // 「先说答案再翻」 is what card users usually do (Kornell 2009 p. 1298; K&B 2008 p. 130); neither paper tested it alone
    const ca = popA(bt, 111.5, 0.5);
    if (ca > 0) txt('先说再翻：常见做法，这两项研究没单独测过', C3.x - 70, 700, { size: 34, weight: 700, color: COL.grayHi, alpha: ca });
    // results: dropped after one correct answer vs kept (Kornell & Bjork 2008, Exp 4, Table 1: 21 % vs 44 %, n = 8)
    scoreLine(TRAY.x, 400, '答对一次就抽走', 21, DIMC, { alpha: popA(bt, 114.5, 0.3), p: seg(bt, 114.5, 115.1), dim: 1 });
    scoreLine(KEEP.x, 400, '答对了也放回', 44, BIG, { alpha: popA(bt, 115.5, 0.3), p: seg(bt, 115.5, 116.1), lit: 0.6 });
    const cs = popS(bt, 116.5, 0.6);
    if (cs > 0) withScale(KEEP.x + 128, 368, cs, () => okMark(KEEP.x + 128, 368, 26, seg(bt, 116.5, 117.2)));
    sparkleBurst(KEEP.x + 128, 368, seg(bt, 116.5, 118), COL.yellow);
    sourceNote('Kornell & Bjork 2008 实验 4 · 只有 8 人 · 斯瓦希里语单词，电脑自动抽卡', 1400, 552, { align: 'center', alpha: popA(bt, 117.5, 0.6) });
  });
}

// ---------- 照着做: three cards dealt face up while he acts each one; the deck fanned in his hand at the end ----------
function drawSummary(bt, hero) {
  if (bt < 128) return;
  SUMC.forEach((c, i) => {
    const L = c.at - 0.5;
    if (bt < L) return;
    const e = EASE.out(seg(bt, L, c.at)), h0 = handsAt(L).F;
    const x = lerp(h0[0], c.x, e), y = lerp(h0[1], SUM_Y, e) - Math.sin(Math.PI * e) * 60;
    const sc = lerp(0.3, 1, e), flip = 1 - EASE.inOut(seg(bt, L, c.at));
    const lit = 0.25 + 0.75 * win(bt, c.at, c.at + 3.5, 0.1, 1);
    withScale(x, y, sc, () => uprightCard(x, y, c.w, SUM_H, { pal: BIG, flip, lit, r: 20, back: plainFace(BIG),
      front: (w, h) => {
        txt(c.s, 0, -24, { size: c.s.length > 3 ? 56 : 64, weight: 900, color: COL.yellowHi, align: 'center', glow: 16, glowColor: COL.yellow });
        txt(c.sub, 0, 52, { size: 36, weight: 700, color: COL.grayHi, align: 'center' });
      } }));
    if (i < 2) {
      const aa = popA(bt, SUMC[i + 1].at - 0.5, 0.3), ax = (c.x + c.w / 2 + SUMC[i + 1].x - SUMC[i + 1].w / 2) / 2;
      if (aa > 0) txt('→', ax, SUM_Y - 2, { size: 54, weight: 800, fam: 'mono', color: COL.cream, align: 'center', alpha: aa });
    }
  });
  // the card he lifts and turns for 「说出答案再翻」
  if (bt >= SUM_SHOW.draw && bt < SUM_SHOW.back + 0.75) {
    const up = EASE.out(seg(bt, SUM_SHOW.draw, SUM_SHOW.draw + 0.5)), down = EASE.inOut(seg(bt, SUM_SHOW.back, SUM_SHOW.back + 0.75));
    const deck = [hero.handB[0] + 8, hero.handB[1] - 12], tgt = [560, 610];
    const x = lerp(lerp(deck[0], tgt[0], up), deck[0], down), y = lerp(lerp(deck[1], tgt[1], up), deck[1], down);
    const right = bt >= SUM_SHOW.flip + 0.5;
    withScale(x, y, lerp(lerp(0.4, 1, up), 0.3, down), () => uprightCard(x, y, 150, 96, { pal: BIG, flip: EASE.inOut(seg(bt, SUM_SHOW.flip, SUM_SHOW.flip + 0.5)),
      lit: right ? 0.6 : 0, alpha: 1 - seg(down, 0.7, 1), front: plainFace(BIG), back: (w, h) => checkBadge(0, 0, 26, { color: COL.yellowHi, p: seg(bt, SUM_SHOW.flip + 0.5, SUM_SHOW.flip + 1.1), lw: 5 }) }));
  }
  // pink note + the caveats printed on the felt
  const wa = popA(bt, 142, 0.35);
  if (wa > 0) withAlpha(wa, () => withScale(1210, 642, 0.92 + 0.08 * popS(bt, 142, 0.6), () => {
    rrect(595, 596, 1230, 92, 16, 'rgba(255,111,158,0.12)', 'rgba(255,111,158,0.8)', 2.5);
    rich([ink('背的时候'), ink('更吃力', COL.pink), ink('，考的时候更好')], 1210, 642, { size: 46, weight: 900, align: 'center' });
  }));
  const fa = popA(bt, 144, 0.6);
  if (fa > 0) {
    feltText('仅供参考：每个实验 20–25 名美国大学生，电脑上的单词卡，学完隔一天考', 1210, 790, { size: 34, weight: 700, color: COL.gray, alpha: fa });
    feltText('抽卡那项（Kornell & Bjork 2008）只有 8 人', 1210, 838, { size: 34, weight: 700, color: COL.gray, alpha: fa });
    txt('Kornell 2009 · Kornell & Bjork 2008', 1210, 884, { size: 24, weight: 500, fam: 'mono', color: COL.grayDim, align: 'center', alpha: fa });
  }
}
// the fan of cards in his front hand (opens 147.5-148.5) and the sparkle when he raises it at the summary
function drawFan(bt, hero) {
  if (!hero.deck || hero.deck.hands !== 'fan') return;
  const [hx, hy] = hero.handF, open = EASE.out(seg(bt, 147.5, 148.6)), n = 7;
  for (let i = 0; i < n; i++) {
    const a = (i - (n - 1) / 2) * 0.2 * open - 0.25;
    const cx = hx + Math.sin(a) * 46, cy = hy - Math.cos(a) * 46;
    uprightCard(cx, cy, 52, 76, { pal: BIG, rot: a, r: 7, lw: 2.2, lit: 0.3 + 0.7 * win(bt, 151, 160, 0.3, 0.1), front: plainFace(BIG, 0.9) });
  }
  sparkleBurst(hx, hy - 60, seg(bt, 151, 152.5), COL.yellow);
}

// ---------- wiring ----------
function drawSectionsBack(bt, t) {}
function drawSectionsTable(bt, t, hero) {
  drawStep1Table(bt, hero);
  drawStep2Table(bt, hero);
  drawStep3Table(bt, hero);
}
function drawSectionsFront(bt, t, hero) {
  if (bt < 31.5) return;
  drawHeaders(bt);
  drawStep1Front(bt, hero);
  drawStep2Front(bt, hero);
  drawStep3Front(bt, hero);
  drawSummary(bt, hero);
  drawFan(bt, hero);
}
