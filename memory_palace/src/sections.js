// sections.js — ① 选路线 (32–64), ② 放画面 (64–96), ③ 走一遍 (96–128) and 照着做 (128–160), all in the same house.
// Headers are door plates sliding in at the top left (this episode's own layout). He stands, walks the route, points,
// thinks with his head down while his imagined self walks the route again, and ends in front of the lit house.

// ---------- the figure after the answer (continues FIG_X_1 in scene.js) ----------
// ① the whole route, door to bed, two steps per spot (lamp n lights as he reaches spot n) · ② door -> next to the shoe
// cabinet -> the sofa -> the fridge · ③ stands at the door, head down · summary: walks out of the door into the yard.
const W1 = walkKeys(34.5, 70, 1811.7);          // t1 = 53.5; passes spot n at ≈ 37 + 2 (n - 2)
const W2a = walkKeys(66.5, 70, 150);            // t1 ≈ 68.0, beside the shoe cabinet
const W2b = walkKeys(70.5, 150, 514);           // t1 = 75.0, beside the sofa
const W2c = walkKeys(77.5, 514, 1116);          // t1 = 84.5, beside the fridge
const W4 = walkKeys(128.5, 181.7, -40);         // t1 = 131.5, out of the door, facing left (the summary is on the left)
const FIG_X_2 = [
  [31.9, 349], [32.0, 70, 'step'], ...W1.keys,
  [63.9, 1811.7], [64.0, 70, 'step'], ...W2a.keys, ...W2b.keys, ...W2c.keys,
  [95.9, 1116], [96.0, 70, 'step'],
  [127.9, 70], [128.0, 181.7, 'step'], ...W4.keys,
];
const FIG_WALK_2 = [[31.9, 0], ...W1.walk, ...W2a.walk, ...W2b.walk, ...W2c.walk, ...W4.walk];
const FIG_DIR_2 = [[32, 1], [54.5, -1], [64, 1], [128, -1], [150, 1]];
// extra poses (same rig, same angle convention as kit POSES)
const POINT_LOW = { lean: 2, head: 8, uaB: -10, faB: 20, uaF: 84, faF: 92 };
const THINK_DOWN = { ...POSES.think, head: 30, lean: 4 };
const LOOK_NOTE = { ...POSES.stand, head: -20, lean: -2 };
const CHEER = { lean: -4, head: -14, uaB: 150, faB: 164, uaF: 152, faF: 166 };
const NOD = { ...POSES.stand, head: 16 };
const UP_KEYS_2 = [
  [32, POSES.stand], [33.0, POINT_LOW], [34.2, POSES.stand],                 // ① the first lamp, by the door
  [55.0, POINT_WIDE], [60.5, POSES.stand],                                   // ① looks back along the lit route
  [64.5, LOOK_NOTE], [66.0, POSES.stand],                                    // ② the shopping note
  [68.3, POINT_LOW], [70.0, POSES.stand], [75.3, POINT_LOW], [77.0, POSES.stand], [85.3, POINT_LOW], [90.0, POSES.stand],
  [92.0, NOD], [92.8, POSES.stand],
  [97.0, POSES.think], [97.6, THINK_DOWN], [117.0, POSES.stand],            // ③ head down: the walk happens in his head
  [119.0, POINT_WIDE], [124.5, POSES.stand],
  [132.0, POINT_UP], [141.0, POSES.stand], [145.0, POINT_UP], [147.5, POSES.stand],
  [150.5, POINT_WIDE], [153.0, POSES.stand], [153.5, CHEER],
];
function upperPose(bt) { return poseTrack([...UP_KEYS_1, ...UP_KEYS_2], bt); }
const ARM_HOLD = [[0, 0]];
const FK_W = [[0, 0]];
function fkPoseAt(bt) { return POSES.stand; }
function figureLook(bt) {
  const pointing = (bt > 9 && bt < 13.2) || (bt > 25 && bt < 29.7) || (bt > 33 && bt < 34.4) || (bt > 55 && bt < 60.7) ||
    (bt > 68.3 && bt < 70.2) || (bt > 75.3 && bt < 77.2) || (bt > 85.3 && bt < 90.2) || (bt > 119 && bt < 124.7) ||
    (bt > 132 && bt < 141.2) || (bt > 145 && bt < 147.7) || (bt > 150.5 && bt < 153.2);
  return { pointF: pointing };
}

// ---------- camera after the answer (hard cuts on the bar downbeats 32 / 64 / 96 / 128) ----------
const STEP_CAM = { WX: 953, Z: 0.85 };   // the whole house, x 150–1765
const SUM_CAM = { WX: 286, Z: 0.56 };    // the house on the right (x 800–1864), the summary on the left
function sectionCam(bt) {
  if (bt < 64) return STEP_CAM;
  if (bt < 96) return { WX: FIGURE.posX(bt) + 381, Z: 1.05 };   // ②: follows him, he stays at screen x ≈ 560
  if (bt < 128) return STEP_CAM;
  return SUM_CAM;
}

// ---------- lamps after the answer ----------
function sweepLamp(bt, at, i) { return bt >= at && bt < at + 3 ? 0.3 + 0.7 * popA(bt, at + 0.1 * i, 0.2) : 1; }
function sectionLamp(bt, i) {
  if (bt < 64) return popA(bt, i === 0 ? 33 : 37 + 2 * (i - 1), 0.3);
  if (bt < 96) return 0.75;
  if (bt < 128) return Math.max(lerp(0.75, 0.1, seg(bt, 96, 96.6)), popA(bt, 98 + 2 * i, 0.3));
  return Math.min(sweepLamp(bt, 130, i), sweepLamp(bt, 153.5, i));
}
function spotTagAlpha(bt) {
  return SPOT_X.map((_, i) => (bt < 32 ? 0 : bt < 64 ? popA(bt, i === 0 ? 33 : 37 + 2 * (i - 1), 0.4) : 1));
}

// ---------- milk / umbrella / piano (② places them, ③ they light up again, the summary keeps them) ----------
const ITEM = [
  { name: '牛奶', spot: 1, at2: 68, at3: 100, draw: drawMilk, dur: 2.5 },
  { name: '雨伞', spot: 3, at2: 75, at3: 104, draw: drawUmbrella, dur: 2.0 },
  { name: '钢琴', spot: 6, at2: 85, at3: 110, draw: drawPiano, dur: 2.5 },
];
function itemState(it, bt) {
  if (bt < it.at2) return null;
  if (bt < 96) return { p: seg(bt, it.at2, it.at2 + it.dur), glow: 0.3 + 0.7 * win(bt, it.at2, it.at2 + 4, 0.2, 2), alpha: 1, label: popA(bt, it.at2 + 0.5, 0.3) };
  if (bt < 128) {
    const back = popA(bt, it.at3, 0.3);
    return { p: 1, glow: back * (0.3 + 0.7 * win(bt, it.at3, it.at3 + 4, 0.2, 2)), alpha: lerp(lerp(1, 0.3, seg(bt, 96, 96.6)), 1, back), label: back };
  }
  return { p: 1, glow: 0.3 + 0.7 * win(bt, 134, 137, 0.2, 1.5), alpha: 1, label: 0 };
}
function drawItems(bt) {
  for (const it of ITEM) {
    const s = itemState(it, bt);
    if (!s) continue;
    withAlpha(s.alpha, () => it.draw(s.p, s.glow));
  }
}
function drawItemLabels(bt) {
  for (const it of ITEM) {
    const s = itemState(it, bt);
    if (!s || s.label <= 0.001) continue;
    const x = wx(SPOT_X[it.spot]), y = wy(360);
    if (x < 60 || x > 1860) continue;
    withScale(x, y, 0.7 + 0.3 * popS(bt, bt < 96 ? it.at2 + 0.5 : it.at3, 0.5), () =>
      txt(it.name, x, y, { size: 40, weight: 900, color: COL.yellow, align: 'center', glow: 16, alpha: s.label }));
  }
}

// ---------- headers ----------
const Y_ = (s) => ({ s, color: COL.yellow });
const HEADERS = [
  { from: 32, to: 63.5, num: '1', title: '选一条闭眼能走的路线', line2: [{ s: '按顺序定好 ' }, Y_('10 个点')], sub: 'A route you could walk with your eyes closed' },
  { from: 64, to: 95.5, num: '2', title: '每样东西变成夸张的画面', line2: [{ s: '放到' }, Y_('一个点'), { s: '上' }], sub: 'Turn each item into a wild picture on a spot' },
  { from: 96, to: 127.5, num: '3', title: '回忆时，原路再走一遍', line2: [{ s: '多练，' }, Y_('几条路线轮换')], sub: 'Walk the same route again in your head' },
  { from: 128, to: 161, num: null, title: '照着做', line2: [{ s: '背' }, Y_('一串东西'), { s: '的时候用' }], sub: 'For lists: route, pictures, walk it again.' },
];
function drawHeaders(bt) {
  for (const h of HEADERS) {
    const inP = seg(bt, h.from, h.from + 0.6), outP = EASE.in(seg(bt, h.to - 0.6, h.to));
    if (inP <= 0 || outP >= 1) continue;
    plaqueHeader(h.num, h.title, h.line2, h.sub, { alpha: 1 - outP, inP, typeP: seg(bt, h.from + 0.4, h.from + 2.6), bt });
  }
}

// ---------- ① notes (top right, above the ceiling) ----------
function drawStep1(bt) {
  if (bt < 32 || bt > 64) return;
  const out = 1 - seg(bt, 62.5, 63.3);
  const a = popA(bt, 55, 0.5) * out;
  if (a > 0) rich([{ s: '常见做法：', color: COL.grayHi }, { s: '一个点只放 ' }, { s: '1 样', color: COL.yellow }, { s: '东西' }], 1000, 300, { size: 40, weight: 900, alpha: a });
  const sa = popA(bt, 57, 0.6) * out;
  if (sa > 0) sourceNote('Dresler 2017 的训练：先学 1 条路线，前 2 周再建 3 条', 1004, 356, { alpha: sa });
  if (a > 0) lintPanel('step1 note', 1000, 276, 1700, 370);
}

// ---------- ② the shopping note, the 「常见做法」 caveat ----------
function drawStep2(bt) {
  if (bt < 64 || bt > 96) return;
  const out = 1 - seg(bt, 95, 95.6);
  const done = (i) => seg(bt, [69, 76, 86][i], [69, 76, 86][i] + 0.5);
  drawShoppingNote(1330, 46, done, { alpha: popA(bt, 64.5, 0.4) * out });
  const na = popA(bt, 88, 0.5) * out;
  if (na > 0) {
    rich([{ s: '越夸张越好：', color: COL.cream }, { s: '常见做法，证据不一', color: COL.grayHi }], 1850, 262, { size: 36, weight: 900, alpha: na, align: 'right' });
    lintPanel('step2 caveat', 1290, 240, 1850, 285);
  }
}

// ---------- ③ the imagined walk (a see-through, cool-lit copy of him), the practice curve, the rotation note ----------
const W3 = walkKeys(97.5, 70, 1811.7);   // t1 = 116.5; passes spot n at ≈ 98 + 2 (n - 1)
const GHOST = {
  posX: KB(W3.keys), walk: KB(W3.walk), s: () => 0.8 * CAM.Z, dir: () => 1, up: () => POSES.stand, armHold: () => 0, cuts: [],
};
function drawGhost(bt) {
  if (bt < 97.5 || bt > 118.5) return;
  const a = popA(bt, 97.5, 0.5) * (1 - seg(bt, 116.8, 118.2));
  drawWalker(bt, GHOST, { rim: COL.cyanHi, alpha: 0.5 * a, shadow: false });
}
function drawStep3(bt) {
  if (bt < 96 || bt > 128) return;
  const out = 1 - seg(bt, 126.5, 127.2);
  drawPracticeCurve(bt, 1120, 130, { alpha: popA(bt, 112, 0.5) * out, at: 112 });
  const ra = popA(bt, 119, 0.5) * out;
  if (ra > 0) {
    rich([{ s: '训练里 ' }, { s: '4 条路线', color: COL.yellow }, { s: '轮换着用' }], 120, 300, { size: 40, weight: 900, alpha: ra });
    lintPanel('step3 note', 120, 276, 700, 370);
  }
  const sa = popA(bt, 120, 0.6) * out;
  if (sa > 0) sourceNote('Dresler 2017 · 训练期间 5 分钟背随机词的成绩（正文 p. e5，图 S1）', 124, 356, { alpha: sa });
}

// ---------- 照着做: three plates on the left, the string of lights comes back for the 4-month result ----------
const SUM_ROWS = [
  { n: 1, s: '选路线', at: 130 },
  { n: 2, s: '放画面', at: 134 },
  { n: 3, s: '原路走一遍', at: 138 },
];
function drawSummary(bt) {
  if (bt < 128) return;
  SUM_ROWS.forEach((r, i) => {
    const a = popA(bt, r.at, 0.3);
    if (a <= 0) return;
    const x = 110, y = 280 + i * 112, w = 470, h = 92, lit = popA(bt, r.at + 0.15, 0.4);
    withAlpha(a, () => withScale(x + 40, y + h / 2, 0.7 + 0.3 * popS(bt, r.at, 0.6), () => {
      ctx.save(); ctx.shadowColor = lit > 0 ? 'rgba(255,200,97,0.6)' : 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 22;
      rrect(x, y, w, h, 14, lerpColor('#141c40', '#2e2310', lit * 0.7), lerpColor('#8d99b5', COL.yellow, lit), 3); ctx.restore();
      ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 18 * lit; circle(x + 50, y + h / 2, 30, COL.yellow); ctx.restore();
      txt(String(r.n), x + 50, y + h / 2 + 1, { size: 38, weight: 800, fam: 'mono', color: '#14100a', align: 'center' });
      txt(r.s, x + 100, y + h / 2 + 1, { size: 52, weight: 900, color: lit > 0.5 ? COL.yellowHi : COL.cream });
    }));
    lintPanel('sum row ' + r.s, x, y, x + w, y + h);
    if (i < 2 && popA(bt, SUM_ROWS[i + 1].at, 0.3) > 0) {   // arrow down to the next plate
      withAlpha(popA(bt, SUM_ROWS[i + 1].at, 0.3), () => {
        const ax = x + 50, ay0 = y + h + 2, ay1 = y + 112 - 2;
        line(ax, ay0, ax, ay1 - 6, COL.yellow, 4);
      });
    }
  });
  // the string of lights again: 4 months later, the first list re-learned -> 50.3 remembered
  const ga = popA(bt, 140.5, 0.4);
  if (ga > 0) {
    drawGarland(bt, (k) => (k < 50 ? popA(bt, 141 + 0.02 * k, 0.15) : 0), { alpha: ga });
    const la = popA(bt, 141, 0.4);
    txt('4 个月后，重学第一张词表', 1870, 386, { size: 36, weight: 900, color: COL.cream, align: 'right', alpha: la });
    const na = popA(bt, 142, 0.4);
    rich([{ s: '还能记住 ' }, { s: '50.3', fam: 'mono', size: 60, weight: 800, color: COL.yellow, glow: 16 }, { s: ' 个' }], 1870, 452,
      { size: 44, weight: 900, align: 'right', alpha: na });
    lintPanel('sum garland text', 1380, 360, 1870, 490);
  }
  const pa = popA(bt, 145, 0.5);
  if (pa > 0) txt('背清单有用，理解课本没证据', 120, 664, { size: 44, weight: 900, color: COL.pink, alpha: pa });
  const fa = popA(bt, 148, 0.6);
  if (fa > 0) {
    txt('仅供参考：每组 17 人，背的是 72 个名词', 120, 724, { size: 30, weight: 700, color: COL.grayHi, alpha: fa });
    txt('Dresler 2017 · Twomey 2021 · Ondřej 2025', 120, 760, { size: 22, weight: 500, fam: 'mono', color: COL.grayDim, alpha: fa });
  }
}

// ---------- wiring ----------
function drawSectionsBehind(bt, t) {
  drawGhost(bt);
}
function drawSections(bt, t, fig) {
  if (bt < 31) return;
  drawItemLabels(bt);
  drawHeaders(bt);
  drawStep1(bt);
  drawStep2(bt);
  drawStep3(bt);
  drawSummary(bt);
}
