// sections.js — 睡前背 room (17–32), 怎么背 ①②③ (32–128) and 照着做 (128–160). Redesigned 2026-10-27 (user: 「后面也改，
// 不要和前面做的那些视频一样」): a bedroom whose window shows the time of day, the boy in bed with word cards, flash-card
// headers. Not used any more: HUD panel, outlined step numbers, wall clock / timer ring / alarm clock / calendar, list table.
const PAPER = '#f4efe6', PAPER_INK = '#14213f', AMBER = '#b87208', ROSE = '#cf3a69';
const ink = (s) => ({ s, color: PAPER_INK });
const hl = (s, color = AMBER) => ({ s, color });

// ---------- header: a cream flash card with a coloured number tab ----------
function titleCard(num, title, line2, sub, o = {}) {
  const { alpha = 1, dx = 0, typeP = 1, bt = 0 } = o;
  withAlpha(alpha, () => {
    const x = 140 + dx, y = 64, h = 184, tab = num ? 96 : 0, w = num ? 790 : 560, tx = x + tab + 32;
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 8;
    rrect(x, y, w, h, 18, PAPER); ctx.restore();
    if (num) {
      rrect(x, y, tab, h, [18, 0, 0, 18], COL.yellow);
      txt(num, x + tab / 2, y + h / 2 + 2, { size: 76, weight: 800, fam: 'mono', color: PAPER_INK, align: 'center' });
    }
    txt(title, tx, y + 50, { size: 54, weight: 900, color: PAPER_INK });
    rich(line2, tx, y + 112, { size: 46, weight: 900 });
    typeText(sub, typeP, tx + 2, y + 158, { size: 22, weight: 500, fam: 'mono', color: '#6b7690' }, bt);
  });
}
const HEADERS = [
  { from: 32, to: 64, num: '1', title: '睡前背什么', sub: 'Before bed: the hard words, until all right',
    line2: () => [ink('睡前背'), hl('难背的生词'), ink('，背到全对')] },
  { from: 64, to: 96, num: '2', title: '背完多久睡', sub: 'Sleep within a few hours, no all-nighter',
    line2: (bt) => {
      if (bt >= 88) return [ink('背完'), hl('几小时内'), ink('就睡，别'), hl('熬通宵', ROSE)];
      const q = { s: ' ？ ', color: '#8d97b0', alpha: 0.55 + 0.45 * Math.sin(bt * Math.PI) };
      return [ink('背完'), q, ink('就睡，别'), q];
    } },
  { from: 96, to: 126.8, num: '3', title: '醒来干嘛', sub: 'Morning: test yourself until all right',
    line2: () => [ink('醒来先'), hl('默一遍'), ink('，错的背到全对')] },
  { from: 126.9, to: 161, num: null, title: '照着做', sub: 'Screenshot it, then follow it',
    line2: () => [ink('背单词时间表')] },
];
function drawHeaders(bt) {
  for (const h of HEADERS) {
    const inP = EASE.out(seg(bt, h.from - 0.2, h.from + 0.7)), outP = EASE.in(seg(bt, h.to - 0.6, h.to));
    const a = inP * (1 - outP);
    if (a <= 0) continue;
    titleCard(h.num, h.title, h.line2(bt), h.sub, { alpha: a, dx: (1 - inP) * -40 - outP * 40, typeP: seg(bt, h.from + 0.4, h.from + 2.8), bt });
  }
}

// ---------- the room: his window shows the time of day, his reading lamp ----------
// 17–31: morning window on the right (the sun rises as he wakes). 32–128: window above his bed: night for ① and ②,
// sunrise for ③ (97–99), then seven days and nights in seven beats (108–115) = 一周后.
const DAY_STEPS = KB([[32, 0], [97, 0], [99, 1, 'inOut']]);
function stageDay(bt) {
  if (bt >= 108 && bt < 115) return 0.5 + 0.5 * Math.cos(TAU * (bt - 108));
  return DAY_STEPS(bt);
}
const LAMP = { x: 760, top: 840 };
function drawRoom(bt, t) {
  const a1 = popA(bt, 16.6, 0.8) * (1 - seg(bt, 30.4, 31.2));
  if (a1 > 0) drawWindow(1640, 600, 210, 250, seg(bt, 17, 18.6), { alpha: a1, t });
  const a2 = popA(bt, 31.5, 0.8) * (1 - seg(bt, 126, 127));
  if (a2 <= 0) return;
  drawBedLamp(LAMP.x, LAMP.top, 1 - seg(bt, 52, 52.12), { alpha: a2 });
  drawWindow(470, 440, 200, 230, stageDay(bt), { alpha: a2, t });
  let label = null, c = COL.cream;
  if (bt < 52) label = '晚上 9 点';
  else if (bt >= 97 && bt < 108) label = '早上';
  else if (bt >= 108 && bt < 115) label = `第 ${Math.min(7, 1 + Math.floor(bt - 108))} 天`;
  else if (bt >= 115) { label = '一周后'; c = COL.yellow; }
  if (label) txt(label, 470, 606, { size: 30, weight: 900, color: c, align: 'center', alpha: a2 });
}

// the girl's notebook in the opening (kid-local coords)
function drawNotebookLocal(x, y) {
  ctx.save(); ctx.translate(x, y);
  ctx.beginPath(); ctx.moveTo(-70, 0); ctx.lineTo(70, 0); ctx.lineTo(58, -14); ctx.lineTo(-58, -14); ctx.closePath();
  ctx.fillStyle = '#f7f4ec'; ctx.fill();
  ctx.strokeStyle = 'rgba(239,140,60,0.8)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(-50, -9); ctx.lineTo(30, -9); ctx.moveTo(-46, -4); ctx.lineTo(10, -4); ctx.stroke();
  ctx.restore();
}
function sparkleBurst(x, y, p, color = COL.yellow) {
  if (p <= 0 || p >= 1) return;
  withAlpha(1 - p, () => {
    for (let i = 0; i < 10; i++) {
      const an = (i / 10) * TAU + 0.3, d = 30 + EASE.out(p) * 90;
      iconStar(x + Math.cos(an) * d, y + Math.sin(an) * d, 9 * (1 - p * 0.5), color);
    }
  });
}
// a cross mark (for the ✗ verdicts)
function crossMark(x, y, r, color) {
  circle(x, y, r, color);
  line(x - r * 0.38, y - r * 0.38, x + r * 0.38, y + r * 0.38, '#0d1838', 4.5);
  line(x + r * 0.38, y - r * 0.38, x - r * 0.38, y + r * 0.38, '#0d1838', 4.5);
}
function okMark(x, y, r, p = 1) {
  ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 18; circle(x, y, r, COL.yellow); ctx.restore();
  checkBadge(x, y, r, { color: '#0d1838', p, lw: 4 });
}

// ---------- ① 睡前背什么: one word acted out on a big flash card (nyanya = 番茄, the paper's own example) ----------
// 36 nyanya · 39.5 a wrong guess (西瓜？, illustration) · 41 back into his hand (错的再来) · 42 nyanya again · 44 番茄 ✓ ·
// 45.5 into the 「全对」 pile; the pile counts to 16 by beat 48 and moves to the centre.
const BIG = { x: 1300, y: 470, w: 600, h: 330 }, PILE = { x: 1715, y: 470 };
function drawBigCard(cx, cy, sx, face, scale) {
  if (sx < 0.02 || scale < 0.01) return;
  const { w, h } = BIG;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(sx * scale, scale);
  const top = face === 'ok' ? COL.yellow : face === 'wrong' ? COL.pink : COL.cyan;
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 10;
  rrect(-w / 2, -h / 2, w, h, 26, face === 'ok' ? '#fff0c4' : face === 'wrong' ? '#ffe1e8' : PAPER); ctx.restore();
  rrect(-w / 2, -h / 2, w, 24, [26, 26, 0, 0], top);
  if (face === 'front') {
    txt('nyanya', 0, -10, { size: 104, weight: 800, fam: 'mono', color: PAPER_INK, align: 'center' });
    txt('斯瓦希里语 · 是什么意思？', 0, 100, { size: 34, weight: 700, color: '#5d6886', align: 'center' });
  } else if (face === 'wrong') {
    txt('西瓜？', 0, 0, { size: 112, weight: 900, color: ROSE, align: 'center' });
    crossMark(w / 2 - 58, -h / 2 + 70, 30, COL.pink);
  } else {
    txt('番茄', 0, 0, { size: 124, weight: 900, color: PAPER_INK, align: 'center' });
    okMark(w / 2 - 58, -h / 2 + 70, 30);
  }
  ctx.restore();
}
function drawStep1(bt) {
  if (bt < 35 || bt > 64) return;
  const out = 1 - seg(bt, 62.6, 63.4);
  let st = null;
  if (bt >= 36 && bt < 42) {
    const go = EASE.in(seg(bt, 41, 42));
    st = { f: flipFace(bt, 39.5, 0.4, 'front', 'wrong'), x: lerp(BIG.x, 520, go), y: lerp(BIG.y, 770, go), sc: popS(bt, 36, 0.6) * lerp(1, 0.18, go), a: 1 - seg(bt, 41.7, 42) };
  } else if (bt >= 42 && bt < 46.5) {
    const go = EASE.in(seg(bt, 45.5, 46.5));
    st = { f: flipFace(bt, 44, 0.4, 'front', 'ok'), x: lerp(BIG.x, PILE.x, go), y: lerp(BIG.y, PILE.y, go), sc: popS(bt, 42, 0.6) * lerp(1, 0.2, go), a: 1 - seg(bt, 46.2, 46.5) };
  }
  if (st) withAlpha(out * st.a, () => drawBigCard(st.x, st.y, st.f.sx, st.f.face, st.sc));
  if (bt >= 44 && bt < 45.4) sparkleBurst(BIG.x, BIG.y, seg(bt, 44, 45.4), COL.yellow);
  // the 「全对」 pile: one card per beat; when all 16 are right it moves to the centre
  const n = Math.floor(16 * seg(bt, 35.5, 48)), mv = EASE.inOut(seg(bt, 48, 49)), done = n >= 16;
  const px = lerp(PILE.x, BIG.x, mv), py = PILE.y, ps = 1 + 0.8 * mv;
  withAlpha(popA(bt, 35, 0.5) * out, () => withScale(px, py, ps, () => {
    for (let k = 0; k < Math.min(Math.max(n, 1), 6); k++) {
      ctx.save(); if (done) { ctx.shadowColor = COL.yellow; ctx.shadowBlur = 20; }
      rrect(px - 55, py - 35 - k * 7, 110, 70, 10, n ? COL.yellow : 'rgba(255,255,255,0.06)', n ? COL.yellowHi : 'rgba(200,212,236,0.4)', 2);
      ctx.restore();
    }
    txt('全对', px, py - 98, { size: 30, weight: 900, color: COL.cream, align: 'center' });
    txt(`${n}/16`, px, py + 72, { size: 40, weight: 800, fam: 'mono', color: done ? COL.yellow : COL.cream, align: 'center', glow: done ? 12 : 0 });
  }));
  if (done) dingBurst(BIG.x - 180, BIG.y - 140, seg(bt, 48, 50.5), { size: 50 });
  // captions under the card, then two notes once he is asleep
  const cap = bt < 39.5 ? [{ s: '遮住答案，先' }, hl('默出来', COL.yellow)] : bt < 42 ? [hl('默错了', COL.pink), { s: ' → 放回去，等会儿再来' }]
    : bt < 44 ? [{ s: '再默一次……' }] : bt < 48 ? [hl('对了', COL.yellow), { s: ' → 放进「全对」那叠' }] : [hl('16 个都对了', COL.yellow), { s: '，就去睡' }];
  if (bt >= 36 && bt < 52) rich(cap, BIG.x, 712, { size: 40, weight: 900, align: 'center', alpha: out * popA(bt, 36, 0.4) });
  const na = popA(bt, 53, 0.6) * out;
  if (na > 0) {
    txt('实验里：16 个从没见过的斯瓦希里语单词', 1000, 790, { size: 30, weight: 700, color: COL.grayHi, alpha: na });
    txt('晚上 9 点背到全对，然后回家睡觉', 1000, 838, { size: 30, weight: 700, color: COL.grayHi, alpha: popA(bt, 54, 0.6) * out });
    sourceNote('Mazza 等 2016 · 《Psychological Science》 · nyanya（番茄）是论文里的例子', 1000, 948, { alpha: na });
  }
}

// ---------- ② 背完多久睡: how long from 背完 (book) to 睡着 (moon), one bar per case (Gais et al. 2006) ----------
// lengths in hours, 38 px each: "a few hours" (drawn as 3 h; the paper gives no number), the all-nighter (8 pm -> ~6 am),
// learning at 8 am and sleeping at night (>= 14 h). Each bar grows over the 1.5 beats before its mark.
const GAP = { x0: 1180, pxh: 38, chipX: 960 };
const GAP_ROWS = [
  { y: 320, h: 3, label: '几小时内', c: COL.yellow, at: 70, ok: true,
    verdict: [{ s: '睡着：' }, { s: '忘得少', color: COL.yellow }], note: '晚上 8 点背，当晚就睡' },
  { y: 470, h: 10, label: '熬通宵', c: COL.pink, at: 78, ok: false,
    verdict: [{ s: '再补觉：' }, { s: '补不回来', color: COL.pink }], note: '背完熬一夜、白天补觉，两天后还是记得少' },
  { y: 620, h: 14, label: '14 小时', c: COL.grayHi, at: 86, ok: false,
    verdict: [{ s: '早上背、晚上才睡：' }, { s: '忘得多', color: COL.grayHi }], note: '关键不是几点背，是背完多久睡' },
];
function drawStep2(bt) {
  if (bt < 64 || bt > 97) return;
  const out = 1 - seg(bt, 95.2, 95.8);
  GAP_ROWS.forEach((r, i) => {
    const a = popA(bt, 65 + i * 0.4, 0.5) * out;
    if (a <= 0) return;
    withAlpha(a, () => {
      const lit = bt >= r.at, cw = measure(r.label, 30, 900) + 36;
      rrect(GAP.chipX, r.y - 26, cw, 52, 26, lit ? r.c : 'rgba(255,255,255,0.06)', lit ? null : 'rgba(200,212,236,0.35)', 2);
      txt(r.label, GAP.chipX + cw / 2, r.y + 1, { size: 30, weight: 900, color: lit ? '#0b1736' : COL.gray, align: 'center' });
      const len = r.h * GAP.pxh, p = EASE.out(seg(bt, r.at - 1.5, r.at));
      rrect(GAP.x0, r.y - 9, len, 18, 9, 'rgba(255,255,255,0.08)');
      if (p > 0) {
        ctx.save(); ctx.shadowColor = r.c; ctx.shadowBlur = 12;
        rrect(GAP.x0, r.y - 9, Math.max(18, len * p), 18, 9, r.c); ctx.restore();
      }
      circle(GAP.x0, r.y, 24, '#0d1838', COL.cyan, 3); iconBook(GAP.x0, r.y, 28, COL.cyan);
      if (p > 0.05) {
        const ex = GAP.x0 + len * p;
        circle(ex, r.y, 24, '#0d1838', r.c, 3); iconMoonX(ex, r.y, 42, r.c);
      }
      if (lit) {
        const v = popA(bt, r.at, 0.4), mx = GAP.x0 + len + 50;
        withAlpha(v, () => (r.ok ? okMark(mx, r.y, 20, seg(bt, r.at, r.at + 0.6)) : crossMark(mx, r.y, 20, r.c)));
        rich(r.verdict, GAP.x0, r.y + 52, { size: 36, weight: 900, alpha: v });
        txt(r.note, GAP.x0, r.y + 92, { size: 24, weight: 500, color: 'rgba(200,212,236,0.75)', alpha: popA(bt, r.at + 0.8, 0.5) });
      }
    });
    if (r.ok) sparkleBurst(GAP.x0 + r.h * GAP.pxh, r.y, seg(bt, r.at, r.at + 1.6), r.c);
  });
  const na = popA(bt, 71, 0.6) * out;
  if (na > 0) sourceNote('Gais 等 2006 · 《Learning & Memory》 · 美国高中生背德语单词（英—德词表）', GAP.chipX, 948, { alpha: na });
}

// ---------- ③ 醒来干嘛: the morning test, round by round, on his 16 cards ----------
// Round 1 (103) lights the 10 he kept overnight (the same 10 as in the opening; the sleep group's mean was 10.3), round 2
// (105) four more, round 3 (107) the last two: 全对 in 3 rounds (mean 3.05). The week (111) turns them face down; one week
// later (115.6) 15 are still right (mean 15.2). The gray grid: 11 (the wake group 11.25 and the one-pass control 11.25).
const KEPT = [0, 2, 3, 5, 6, 8, 9, 11, 12, 15], ROUND2 = [1, 4, 10, 14], ROUND3 = [7, 13], GRAY_LOST = [2, 6, 9, 12, 14];
const G3 = { x: 1180, y: 520 }, G3B = { x: 1600, y: 520 };
function step3Card(i, bt) {
  if (bt < 111) {
    const t1 = 103 + (i % 8) * 0.06;
    if (bt < t1 + 0.3) return flipFace(bt, t1, 0.3, 'blank', KEPT.includes(i) ? 'lit' : 'lost');
    if (KEPT.includes(i)) return { face: 'lit', sx: 1 };
    const k2 = ROUND2.indexOf(i);
    return flipFace(bt, k2 >= 0 ? 105 + k2 * 0.1 : 107 + ROUND3.indexOf(i) * 0.15, 0.3, 'lost', 'lit');
  }
  if (bt < 115.6) return flipFace(bt, 111 + (i % 8) * 0.05, 0.3, 'lit', 'blank');
  return flipFace(bt, 115.6 + (i % 8) * 0.07, 0.3, 'blank', i === 13 ? 'lost' : 'lit');
}
function drawStep3(bt) {
  if (bt < 102 || bt > 128) return;
  const out = 1 - seg(bt, 126, 126.8);
  withAlpha(popA(bt, 102.4, 0.5) * out, () => {
    for (let i = 0; i < 16; i++) {
      const [x, y] = cardCentre(G3.x, G3.y, i), c = step3Card(i, bt);
      drawWordCard(x, y, c.face, { sx: c.sx, glow: 1 + 0.6 * win(bt, 107.6, 109, 0.1, 1) });
    }
    if (bt < 111) {
      const right = bt < 105 ? '第 1 轮：10/16' : bt < 107.6 ? '第 2 轮' : '第 3 轮：全对';
      txt(right, G3.x, 670, { size: 38, weight: 900, color: bt >= 107.6 ? COL.yellow : COL.cream, align: 'center', glow: bt >= 107.6 ? 12 : 0 });
      txt('实验里平均 3 轮就全对；早上背的也能全对，但要 6 轮', 1390, 742, { size: 28, weight: 700, color: COL.grayHi, align: 'center', alpha: popA(bt, 104, 0.6) * (1 - seg(bt, 110.4, 111)) });
    }
  });
  if (bt >= 107.6 && bt < 110) dingBurst(G3.x + 170, G3.y - 120, seg(bt, 107.6, 110), { size: 46 });
  // one week later: his 15 and the gray 11
  const wa = popA(bt, 115.8, 0.4) * out;
  if (wa > 0) withAlpha(wa, () => {
    txt('15 个', G3.x, 384, { size: 50, weight: 800, fam: 'mono', color: COL.yellow, align: 'center', glow: 12 });
    txt('睡前背 + 早上默到全对', G3.x, 670, { size: 30, weight: 900, color: COL.yellow, align: 'center' });
    const cs = popS(bt, 117.5, 0.6);
    if (cs > 0) withScale(G3.x + 96, 384, cs, () => okMark(G3.x + 96, 384, 24, seg(bt, 117.5, 118.2)));
    const la = popA(bt, 117.7, 0.4);
    if (la > 0) txt('还领先', G3.x + 132, 384, { size: 36, weight: 900, color: COL.yellow, alpha: la, glow: 12 });
  });
  const ga = popA(bt, 119, 0.5) * out;
  if (ga > 0) withAlpha(ga, () => {
    for (let i = 0; i < 16; i++) {
      const [x, y] = cardCentre(G3B.x, G3B.y, i);
      const c = flipFace(bt, 119.2 + (i % 8) * 0.06, 0.3, 'blank', GRAY_LOST.includes(i) ? 'lost' : 'lit');
      drawWordCard(x, y, c.face, { sx: c.sx, color: '#66728f', colorHi: '#8994ad', glow: 0 });
    }
    txt('11 个', G3B.x, 384, { size: 50, weight: 800, fam: 'mono', color: COL.grayHi, align: 'center' });
    txt('早上只过一遍的 · 早上背的', G3B.x, 670, { size: 30, weight: 900, color: COL.grayHi, align: 'center' });
  });
  const na = popA(bt, 120, 0.6) * out;
  if (na > 0) {
    txt('半年后：8.7 个 vs 早上背的 3.4 个', 1390, 742, { size: 30, weight: 900, color: COL.cream, align: 'center', alpha: na });
    sourceNote('Mazza 等 2016 · 都是平均数', 960, 948, { alpha: na });
  }
}

// ---------- 照着做: the night as three stops on one line (evening -> night -> morning), filled while he acts each ----------
const STOPS = [
  { x: 905, at: 130, when: '晚上', icon: 'moon', main: '睡前背难背的生词', sub: '遮住答案默，背到全对' },
  { x: 1255, at: 134, when: '夜里', icon: 'zz', main: '背完几小时内睡着', sub: '别熬通宵，补觉补不回来' },
  { x: 1605, at: 138, when: '早上', icon: 'sun', main: '早上默到全对', sub: '先默一遍，错的再背' },
];
function drawTable(bt) {
  const inP = EASE.out(seg(bt, 126.3, 128));
  if (inP <= 0) return;
  withAlpha(inP, () => {
    const p = EASE.inOut(seg(bt, 130, 138.6));
    if (p > 0) {
      ctx.save(); ctx.setLineDash([16, 12]); ctx.strokeStyle = 'rgba(243,238,227,0.45)'; ctx.lineWidth = 5; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(905, 400); ctx.lineTo(905 + 700 * p, 400); ctx.stroke(); ctx.restore();
    }
    STOPS.forEach((s) => {
      const a = popA(bt, s.at, 0.35);
      if (a <= 0) return;
      withAlpha(a, () => {
        txt(s.when, s.x, 318, { size: 34, weight: 900, color: COL.cream, align: 'center' });
        withScale(s.x, 400, popS(bt, s.at, 0.6), () => {
          ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 22;
          circle(s.x, 400, 50, '#0d1838', COL.yellow, 4); ctx.restore();
          ICONS[s.icon](s.x, 400, s.icon === 'zz' ? 60 : 56, COL.yellow, 3, 0);
        });
        txt(s.main, s.x, 494, { size: 40, weight: 900, color: COL.cream, align: 'center' });
        txt(s.sub, s.x, 542, { size: 26, weight: 700, color: 'rgba(200,212,236,0.85)', align: 'center' });
      });
    });
    const wa = popA(bt, 142, 0.35);
    if (wa > 0) withAlpha(wa, () => withScale(1265, 643, 0.9 + 0.1 * popS(bt, 142, 0.6), () => {
      rrect(760, 600, 1010, 86, 16, 'rgba(255,111,158,0.12)', 'rgba(255,111,158,0.75)', 2.5);
      txt('早上只过一遍不够', 800, 643, { size: 44, weight: 900, color: COL.cream });
      txt('一周后优势就没了', 1740, 645, { size: 28, weight: 700, color: COL.pink, align: 'right' });
    }));
    const fa = popA(bt, 144, 0.6);
    if (fa > 0) {
      txt('仅供参考 · 换成背知识点（不是单词），一周后差距不显著', 760, 752, { size: 26, weight: 700, color: COL.gray, alpha: fa });
      txt('Mazza 2016 · Gais 2006 · Cousins 2021', 760, 794, { size: 22, weight: 500, fam: 'mono', color: COL.grayDim, alpha: fa });
    }
    const fl = win(bt, 146, 147.4, 0.04, 1.2);
    if (fl > 0) rrect(730, 270, 1070, 560, 22, `rgba(255,255,255,${0.08 * fl})`, `rgba(255,250,235,${0.9 * fl})`, 5);
  });
}

// ---------- wiring ----------
function drawPanelLayer(bt, t) {
  if (bt >= 16.6) drawRoom(bt, t);
}
function decorateBoy(bp, bt, t) {
  // the book's pages in the hook, then the word card in his hands turns over every 2 beats
  if (bp.read > 0.9) {
    const cyc = bt < 8 ? ((bt - 1.5) % 2 + 2) % 2 : ((bt - 24.5) % 2 + 2) % 2;
    bp.flip = cyc < 0.9 ? cyc / 0.9 : 0;
  }
  // head shake "no" for 「早上只过一遍不够」
  if (bt > 142 && bt < 144.5) bp.headTilt = Math.sin((bt - 142) * Math.PI * 2.2) * 0.12 * (1 - seg(bt, 143.6, 144.5));
  bp.worry = win(bt, 142, 144.6, 0.3, 0.6) * 0.6;
}
function drawSections(bt, t, boy) {
  if (bt < 31) return;
  drawHeaders(bt);
  drawStep1(bt);
  drawStep2(bt);
  drawStep3(bt);
  if (bt >= 126.2) drawTable(bt);
}
