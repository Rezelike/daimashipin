// scene.js — timeline, camera, the figure's moves, the hook (0–17) and the answer (17–32). All times in beats (bt).
// 128 BPM -> 1 beat = 0.46875 s; 160 beats = 75 s. Beat grid of 睡还是背 (lessons 13, six/plan.md): reveal 1 at 4.5
// (2.11 s), reveal 2 four beats later at 8.5 (3.98 s), 4.92 / 5.39 s the check and the other two groups, 6.1 s the source,
// the answer from beat 17 (8.0 s), the evidence card at 26.5 (12.4 s), steps at 32 / 64 / 96, the summary at 128.
const TOTAL_BEATS = 160;

// beats where the picture cuts and he is somewhere else (the walker keeps his feet under him around these)
const CUTS = [32, 64, 96, 128];

// a walk from x0 to x1 starting at t0 (a half beat, so the heel strikes fall on the beats): cubic ease-in / ease-out over
// half a beat each, constant speed v in between (world units per beat). Returns { keys, t1, walk }.
function walkKeys(t0, x0, x1, v = 95) {
  const sgn = Math.sign(x1 - x0), d = Math.abs(x1 - x0), lin = Math.max(0, (d - v / 3) / v), t1 = t0 + 1 + lin;
  return {
    keys: [[t0, x0], [t0 + 0.5, x0 + (sgn * v) / 6, 'in'], [t1 - 0.5, x1 - (sgn * v) / 6, 'lin'], [t1, x1, 'out']],
    walk: [[t0, 0], [t0 + 0.4, 1], [t1 - 0.3, 1], [t1 + 0.2, 0]], t1,
  };
}

// ---------- the figure: where he is (pelvis x, world) and what he does ----------
// hook + reveal 2: outside in the yard (x -300), catching the falling words; answer: walks in through the door
const W_ANSWER = walkKeys(17.0, -300, 349);
const FIG_X_1 = [[0, -300], ...W_ANSWER.keys];
const FIG_WALK_1 = [[0, 0], ...W_ANSWER.walk];
const FIG_DIR_1 = [[0, 1]];
const POSE_UP = POSES;
const FIGURE = {};
function initFigure() {
  FIGURE.posX = KB([...FIG_X_1, ...FIG_X_2]);
  FIGURE.walk = KB([...FIG_WALK_1, ...FIG_WALK_2]);
  const dirs = [...FIG_DIR_1, ...FIG_DIR_2];
  FIGURE.dir = (bt) => { let d = 1; for (const [b, v] of dirs) if (bt >= b) d = v; return d; };
  FIGURE.s = (bt) => 0.8 * CAM.Z;
  FIGURE.up = (bt) => upperPose(bt);
  FIGURE.armHold = KB(ARM_HOLD);
  FIGURE.fk = KB(FK_W);
  FIGURE.fkPose = (bt) => fkPoseAt(bt);
}
// upper-body pose track: list of [beat, poseObject]; blends over 0.6 beat into each key, ease-out so the movement visibly
// starts ON its key beat (VERIFY rhythm measures where a change starts)
function poseTrack(keys, bt, blend = 0.6) {
  let cur = keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [b, p] = keys[i];
    if (bt < b) break;
    cur = lerpPose(cur, p, EASE.out(seg(bt, b, b + blend)));
  }
  return cur;
}
// catching the falling words: one arm up, then the other, on the beats
const REACH_A = { lean: -4, head: -18, uaB: -10, faB: 30, uaF: 150, faF: 168 };
const REACH_B = { lean: -2, head: -12, uaB: 140, faB: 160, uaF: 60, faF: 100 };
const HOLD_BUNDLE = { lean: 0, head: 10, uaB: 30, faB: 100, uaF: 40, faF: 108 };   // both arms around what he caught
const LOOK_UP = { ...POSES.stand, head: -24, lean: -3 };
const POINT_WIDE = { lean: 0, head: -6, uaB: -16, faB: 30, uaF: 112, faF: 118 };
const POINT_UP = { lean: -2, head: -14, uaB: -14, faB: 24, uaF: 128, faF: 136 };
const UP_KEYS_1 = [
  [0, REACH_A], [1, REACH_B], [2, REACH_A], [3, REACH_B], [4, HOLD_BUNDLE],
  [4.6, LOOK_UP],             // reveal 1: the words fly off to the string of lights; he looks up at it
  [6.0, POSES.shrug],         // only 26 of 72
  [7.5, POSES.stand],
  [9.0, POINT_WIDE],          // reveal 2: points at the house lighting up
  [13.0, POSES.stand],
  [25.0, POINT_UP],           // the answer: points up at the three pendant lamps
  [29.5, POSES.stand],
];

// ---------- camera ----------
const HOOK_CAM = { WX: -511, Z: 0.9 };     // the door at screen x 1420, he stands in the yard at 1150
const WIDE_CAM = { WX: 516, Z: 0.62 };     // the whole house, x 640–1818
function mixCam(a, b, t) { return { WX: lerp(a.WX, b.WX, t), Z: lerp(a.Z, b.Z, t) }; }
function camAt(bt) {
  if (bt < 8.5) return HOOK_CAM;
  if (bt < 15.5) return mixCam(HOOK_CAM, WIDE_CAM, EASE.inOut(seg(bt, 8.5, 9.6)));
  if (bt < 32) return mixCam(WIDE_CAM, { WX: FIGURE.posX(bt) - 140, Z: 1.0 }, EASE.inOut(seg(bt, 15.5, 17.4)));
  return sectionCam(bt);
}

// ---------- lamps: the level of each of the ten lamps (0..1) ----------
function lampOn(bt, at, d = 0.3) { return popA(bt, at, d); }
function lampLevels(bt) {
  const L = new Array(10).fill(0);
  for (let i = 0; i < 10; i++) {
    if (bt < 8.5) L[i] = 0;
    else if (bt < 17) L[i] = lampOn(bt, 8.5 + 0.2 * i) * (1 - seg(bt, 15.5, 16.2));
    else if (bt < 32) L[i] = lampOn(bt, i === 0 ? 21 : i === 1 ? 23 : 27 + 0.5 * (i - 2));
    else L[i] = sectionLamp(bt, i);
  }
  return L;
}

// ---------- title block (top left): the hook question, flipping to the answer at beat 17 ----------
function drawTitleBlock(bt) {
  const outA = 1 - EASE.out(seg(bt, 30.5, 31.4));
  const dyOut = -40 * EASE.in(seg(bt, 30.5, 31.4));
  if (outA <= 0) return;
  withAlpha(outA, () => {
    const X0 = 120;
    const flipLine = (y, clipH, a0, a1, p) => {
      const e = EASE.out(p);
      ctx.save(); ctx.beginPath(); ctx.rect(0, y - clipH / 2, 1000, clipH); ctx.clip();
      if (e < 1) withAlpha(1 - e, () => a0(y - e * clipH));
      if (e > 0) withAlpha(e, () => a1(y + (1 - e) * clipH));
      ctx.restore();
    };
    flipLine(130 + dyOut, 150,
      (y) => txt('记忆宫殿', X0, y, { size: 128, weight: 900, color: COL.yellow, glow: 28 }),
      (y) => rich([{ s: '有用：', color: COL.grayHi }, { s: '背清单', color: COL.cream }], X0, y, { size: 96, weight: 900 }),
      seg(bt, 17.0, 17.6));
    flipLine(268 + dyOut, 150,
      (y) => txt('真的有用吗？', X0, y, { size: 128, weight: 900, color: COL.cream }),
      (y) => txt('但要练', X0, y, { size: 128, weight: 900, color: COL.yellow, glow: 30 }),
      seg(bt, 17.0, 17.6));
    const en1 = 'Does the memory palace really work?', en2 = 'It works for lists, with practice.';
    const useSecond = bt >= 17;
    const s = useSecond ? en2 : en1;
    const p1 = useSecond ? seg(bt, 17.4, 20.2) : lerp(10 / en1.length, 1, seg(bt, 0, 2.4));
    typeText(s, p1, X0 + 4, 366 + dyOut, { size: 34, weight: 500, fam: 'mono', color: COL.cyan, keepCursor: true }, bt);
  });
}

// ---------- caption under the title: reveal 1 / reveal 2 (flips on the beat) ----------
const CAPTIONS = [
  { at: 4.5, main: [{ s: '没学过的人：' }, { s: '26.5 个', color: COL.cream, glow: 0 }], note: '72 个词，每个看 2 秒，20 分钟后写下来（平均）' },
  { at: 8.5, main: [{ s: '练 40 天后：' }, { s: '62.5 个', color: COL.yellow, glow: 22 }], note: '同一批人，每天练 30 分钟' },
];
function drawCaption(bt) {
  const A = 1 - EASE.out(seg(bt, 17.0, 17.5));
  if (A <= 0 || bt < 4.5) return;
  CAPTIONS.forEach((c, i) => {
    const next = CAPTIONS[i + 1];
    const pin = EASE.out(seg(bt, c.at, c.at + 0.45));
    const pout = next ? EASE.inOut(seg(bt, next.at - 0.05, next.at + 0.35)) : 0;
    const a = A * pin * (1 - pout);
    if (a <= 0.001) return;
    const dy = (1 - pin) * 50 - pout * 50;
    rich(c.main, 120, 520 + dy, { size: 66, weight: 900, alpha: a });
    txt(c.note, 124, 588 + dy, { size: 34, weight: 700, color: COL.grayHi, alpha: a * popA(bt, c.at + 0.5, 0.4) });
  });
}

// ---------- the falling words and the string of lights (hook) ----------
// caught words wait in his arms, then fly to bulbs 0..25 at reveal 1; 36 words from the floor fly to bulbs 26..61 at reveal 2
const HOLD_C = [1180, 640];
function holdSlot(j, bt) {
  const a = j * 2.39996 + bt * 0.9, r = 48 + (j % 5) * 16;
  return [HOLD_C[0] + Math.cos(a) * r * 1.25, HOLD_C[1] - 40 + Math.sin(a) * r * 0.7];
}
const FLY1 = 4.5, FLY2 = 8.5;
const arriveCaught = (j) => FLY1 + 0.32 + 0.012 * j;
const arriveFloor = (j) => FLY2 + 0.12 + 0.03 * j;
function flakeFall(f, bt) {
  const u = (bt - f.t0) / f.dur;
  return [f.x + Math.sin(bt * 1.6 + f.ph) * f.sway, lerp(380, FLOOR_Y - 10, u), f.rot + f.spin * bt, u];
}
function bezier(a, b, c, t) { return [lerp(lerp(a[0], b[0], t), lerp(b[0], c[0], t), t), lerp(lerp(a[1], b[1], t), lerp(b[1], c[1], t), t)]; }
function drawFlakes(bt) {
  if (bt > 10.5) return;
  FLAKES.forEach((f) => {
    if (f.caught) {
      const j = f.slot, start = f.catchAt - f.dur * 0.75;
      if (bt < start) return;
      let p, rot, glow = 0, sc = 1;
      if (bt < f.catchAt) {   // falls toward his arms
        const u = seg(bt, start, f.catchAt), slot = holdSlot(j, f.catchAt);
        p = [lerp(f.x, slot[0], EASE.inOut(u)), lerp(380, slot[1], u)];
        rot = f.rot + f.spin * bt;
      } else if (bt < FLY1) { // held: glowing, circling slowly
        p = holdSlot(j, bt); rot = f.rot * 0.3; glow = popA(bt, f.catchAt, 0.3);
      } else {                // flies up to its bulb
        const t1 = arriveCaught(j);
        if (bt >= t1) return;
        const u = EASE.inOut(seg(bt, FLY1, t1)), a = holdSlot(j, FLY1), b = bulbPos(j);
        p = bezier(a, [lerp(a[0], b[0], 0.3), b[1] - 120], b, u); rot = f.rot * (1 - u); glow = 1; sc = lerp(1, 0.5, u);
      }
      const fa = popA(bt, start, 0.3);
      drawFlakeAt(p[0], p[1], rot, f, { glow, alpha: fa, scale: sc });
    } else {
      if (bt < f.t0) return;
      const k = FLOOR_FLAKES.indexOf(f);
      const [x, y, rot, u] = flakeFall(f, Math.min(bt, f.t0 + f.dur));
      const landed = bt >= f.t0 + f.dur;
      const fa = popA(bt, f.t0, 0.4);
      if (bt < FLY2 || k >= 36) {
        const dim = landed ? 0.55 : 1;
        const out = k >= 36 ? 1 - seg(bt, FLY2, FLY2 + 0.6) : 1;
        drawFlakeAt(x, landed ? FLOOR_Y - 12 : y, landed ? 0.1 * Math.sin(f.ph) : rot, f, { alpha: fa * dim * out, scale: landed ? 0.85 : 1 });
      } else {
        const t1 = arriveFloor(k);
        if (bt >= t1) return;
        const u = EASE.inOut(seg(bt, FLY2, t1)), a = [x, FLOOR_Y - 12], b = bulbPos(26 + k);
        const p = bezier(a, [lerp(a[0], b[0], 0.2), lerp(a[1], b[1], 0.7)], b, u);
        drawFlakeAt(p[0], p[1], 0, f, { glow: 1, alpha: 1, scale: lerp(0.85, 0.5, u) });
      }
    }
  });
}
function hookBulbLit(k, bt) {
  if (k < 26) return popA(bt, arriveCaught(k), 0.15);
  if (k < 62) return popA(bt, arriveFloor(k - 26), 0.15);
  return 0;
}
// the count under the string of lights, the check, the other two groups (4.92 / 5.39 s)
function drawHookCount(bt) {
  const A = 1 - seg(bt, 16.5, 17.2);
  if (A <= 0 || bt < 4.5) return;
  const second = bt >= FLY2;
  const n = second ? lerp(26.5, 62.5, EASE.out(seg(bt, FLY2, FLY2 + 1.2))) : 26.5;
  const pin = popA(bt, 4.5, 0.4);
  withAlpha(A * pin, () => {
    const spans = [{ s: n.toFixed(1), fam: 'mono', size: 64, weight: 800, color: second ? COL.yellow : COL.cream, glow: second ? 18 : 0 },
      { s: ' / 72 个词', size: 36, color: COL.grayHi }];
    const wv = richWidth(spans, 36, 900);
    rich(spans, 1870, 372, { size: 36, weight: 900, align: 'right' });
    const ca = popA(bt, 10.5, 0.3);
    if (ca > 0) withScale(1870 - wv - 44, 372, 0.6 + 0.4 * popS(bt, 10.5), () => okMark(1870 - wv - 44, 372, 28, seg(bt, 10.5, 11.3)));
    const oa = popA(bt, 11.5, 0.4);
    if (oa > 0) {
      txt('不练的：36.6', 1870, 436, { size: 34, weight: 700, color: COL.grayHi, align: 'right', alpha: oa });
      txt('练别的记忆游戏（n-back）：42.7', 1870, 482, { size: 34, weight: 700, color: COL.grayHi, align: 'right', alpha: oa });
    }
  });
  lintPanel('count', 1400, 336, 1870, 408);
}
// reveal 2: his 40 days of practice, as afterimages walking the route (one per spot, in order)
function drawPracticeGhosts(bt) {
  if (bt < 8.5 || bt > 13) return;
  for (let i = 0; i < 10; i++) {
    const at = 8.5 + 0.2 * i, a = popA(bt, at, 0.15) * (1 - seg(bt, at + 1.2, at + 2.6));
    if (a <= 0.01) continue;
    const ph = i * 0.5;
    const spec = { posX: (b) => SPOT_X[i] - 40 + 95 * (b - ph), walk: () => 1, s: () => 0.8 * CAM.Z, dir: () => 1, up: () => POSES.stand, armHold: () => 0 };
    // a frozen walking frame: evaluate the walk at a fixed phase
    const { pose, pelvis, s } = walkerPose(ph, spec);
    drawFigure({ pelvis, x: pelvis[0], y: FLOOR_Y, s, dir: 1, pose, style: 'C', rim: COL.cyanHi, rimDx: -3.5, rimDy: -3.5, alpha: 0.55 * a, shadow: false });
  }
}

// ---------- the answer (17–32): ①②③ as three pendant lamps, the meta-analysis card ----------
const PENDANTS = [
  { n: 1, s: '选路线', at: 19.0, x: 1190, len: 92 },
  { n: 2, s: '放画面', at: 21.5, x: 1460, len: 120 },
  { n: 3, s: '走一遍', at: 25.0, x: 1730, len: 92 },
];
function drawAnswer(bt) {
  if (bt < 18.5 || bt > 32) return;
  const out = 1 - seg(bt, 30.4, 31.1);
  for (const p of PENDANTS) {
    const a = popA(bt, p.at, 0.3) * out;
    if (a <= 0) continue;
    const drop = EASE.back(clamp((bt - p.at) / 0.6));
    drawPendant(p.x, p.len * drop, p.n, p.s, { alpha: a, lit: popA(bt, p.at + 0.2, 0.3) });
  }
  const ea = popA(bt, 26.5, 0.5) * out;
  if (ea > 0) withAlpha(ea, () => withScale(470, 580, 0.85 + 0.15 * popS(bt, 26.5, 0.6), () => drawMetaCard(110, 450, 720, 270)));
}

// ---------- frame ----------
function renderFrame(t) {
  const bt = t / BEAT;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  setCam(camAt(bt));
  const L = lampLevels(bt);
  drawSky(bt, t);
  drawHouse(bt, L);
  drawFurniture(L);
  drawItems(bt);
  drawLamps(L);
  drawLampCones(L);
  drawSpotTags(bt, spotTagAlpha(bt));
  drawPracticeGhosts(bt);
  drawSectionsBehind(bt, t);
  const info = { t, bt, kid: false };

  const fig = drawWalker(bt, FIGURE, figureLook(bt));
  info.kid = true;
  const hs = FIGURE.s(bt);
  lintPanel('head:figure', fig.head[0] - 26 * hs, fig.head[1] - 28 * hs, fig.head[0] + 26 * hs, fig.head[1] + 28 * hs);

  drawFlakes(bt);
  if (bt < 17.2) drawGarland(bt, (k) => hookBulbLit(k, bt), { alpha: 1 - seg(bt, 16.5, 17.2) });
  drawHookCount(bt);
  drawTitleBlock(bt);
  drawCaption(bt);
  sourceNote('Dresler 等 2017 · 德国 51 名男大学生，每组 17 人', 124, 640, { alpha: popA(bt, 13, 0.8) * (1 - EASE.out(seg(bt, 17, 17.5))) });
  drawAnswer(bt);
  drawSections(bt, t, fig);
  drawVignette();
  drawChapterBar(bt);
  window.__frameInfo = info;
}
