// sections.js — 怎么念 ① ② ③ (32-128) and 照着做 (128-160). Each step opens on the action (no STEP page): its header is a
// karaoke line, outlined text that fills solid from the left the way a word turns solid when it is said aloud.
// Numbers only from six/facts/03_read_aloud.md (+ Roberts 2024 Table 1, checked in the paper).

// ---------- headers ----------
const ink = (s, color = COL.cream) => ({ s, color });
const HEADERS = [
  { from: 32, to: 64, num: 1, spans: [ink('先默读，'), ink('圈出', COL.yellow), ink('要原样记住的几句')],
    en: 'Read it once silently, then circle what must stay word for word.' },
  { from: 64, to: 96, num: 2, spans: [ink('一字一字', COL.yellow), ink('念出来')], en: 'Say every word out loud.' },
  { from: 96, to: 128, num: 3, spans: [ink('念出声帮你'), ink('记原话', COL.yellow), ink('，不帮你'), ink('读懂', COL.pink)],
    en: 'It helps you remember the words, not understand them.' },
  { from: 128, to: 161, num: null, spans: [ink('照着做')], en: 'Memorising a page? Do this.' },
];
function drawHeaders(bt) {
  for (const h of HEADERS) {
    const inP = EASE.out(seg(bt, h.from, h.from + 0.5)), outP = seg(bt, h.to - 0.25, h.to);
    const a = inP * (1 - outP);
    if (a <= 0) continue;
    const dx = (1 - inP) * -40 - outP * 40, x0 = h.num ? 250 : 140;
    withAlpha(a, () => {
      if (h.num) numBlock(178 + dx, 134, h.num, { size: 96 });
      karaoke(h.spans, x0 + dx, 118, seg(bt, h.from + 0.5, h.from + 3.5), { size: 64 });
      typeText(h.en, seg(bt, h.from + 1, h.from + 4), x0 + 2 + dx, 190, { size: 34, weight: 500, fam: 'mono', color: COL.cyan }, bt);
    });
  }
}

// ---------- hero in the steps ----------
const THINK_READ = { ...POSES.think, head: 14 };
const WHISPER = { head: 12, lean: 7 };   // leans in and speaks softly (the strip stays in his hand)
function heroSteps(bt, st) {
  st.dir = 1; st.hold = null; st.y = GROUND; st.s = HERO_S;
  let p = withPose();
  if (bt < 64) {
    // ① 念哪些: reads the page silently (hand on chin), then circles three lines with the light pen
    st.x = lerp(600, 520, EASE.inOut(seg(bt, 31, 33)));
    if (bt < 33) p = withPose(walkPose(bt - 31, 0.5 * Math.sin(Math.PI * seg(bt, 31, 33))));
    p = poseMix(p, withPose(THINK_READ), pw(bt, 33, 41.5, 0.5, 0.5));
    p = poseMix(p, withPose(PEN_AIM, PEN_TILT(bt)), pw(bt, 41.5, 53.5, 0.5, 0.5));
    p = poseMix(p, withPose(POSES.point), pw(bt, 56, 59.5, 0.5, 0.5));
    if (bt > 62.5) { st.x = lerp(520, 380, EASE.inOut(seg(bt, 62.5, 64.5))); p = withPose(walkPose(bt - 62.5, 0.55 * Math.sin(Math.PI * seg(bt, 62.5, 64.5)))); }
    st.pen = pw(bt, 41.5, 53.5, 0.5, 0.5);
  } else if (bt < 96) {
    // ② 怎么念: says the circled line aloud, then whispers it (hand at his mouth), then only mouths it, then reads silently
    st.x = 380; st.hold = 'strip';
    p = poseMix(p, withPose(HOLD_SHEET, SPEAK_LEAN), pw(bt, 65.5, 71.5, 0.5, 0.5));
    p = poseMix(p, withPose(HOLD_SHEET, WHISPER), pw(bt, 71.5, 77.5, 0.5, 0.5));
    p = poseMix(p, withPose(HOLD_SHEET, { head: 4 + 3 * Math.sin(bt * Math.PI * 2) }), pw(bt, 77.5, 83.5, 0.5, 0.5));
    p = poseMix(p, withPose(HOLD_SHEET, { head: 16 }), pw(bt, 83.5, 86.5, 0.5, 0.5));
    if (bt < 65.5 || bt > 86.5) p = poseMix(withPose(HOLD_SHEET), p, 1);
    p = poseMix(p, withPose(POSES.point), pw(bt, 89, 92.5, 0.5, 0.5));
    if (bt >= 88.5 && bt <= 93) st.hold = null;
    if (bt > 94.5) { st.x = lerp(380, 400, seg(bt, 94.5, 96)); st.hold = null; }
  } else if (bt < 128) {
    // ③ 念了有什么用: reads a passage aloud; the blocks pile up on 记住原话, bounce off 读懂意思; shrug, think
    st.x = 400; st.hold = bt > 96.5 && bt < 106.5 ? 'sheet' : null;
    p = poseMix(p, withPose(HOLD_SHEET), pw(bt, 96.5, 106.5, 0.5, 0.5));
    p = poseMix(p, withPose(HOLD_SHEET, SPEAK_LEAN), pw(bt, 98.5, 106.5, 0.5, 0.5));
    p = poseMix(p, withPose(POSES.shrug), pw(bt, 109, 111.5, 0.5, 0.5));
    p = poseMix(p, withPose(POSES.think), pw(bt, 113, 118.5, 0.5, 0.5));
    p = poseMix(p, withPose(POSES.point), pw(bt, 120, 123.5, 0.5, 0.5));
    if (bt > 126) { st.x = lerp(400, 380, seg(bt, 126, 128)); }
  } else {
    // 照着做: acts each clip of the track as it appears, points at it, then jumps
    st.x = 380;
    st.hold = (bt > 137.5 && bt < 141.5) ? 'sheet' : null;
    p = poseMix(p, withPose(THINK_READ), pw(bt, 129.5, 133.5, 0.5, 0.5));
    p = poseMix(p, withPose(PEN_AIM, { faF: 92 }), pw(bt, 133.5, 137.5, 0.5, 0.5));
    st.pen = pw(bt, 133.5, 137.5, 0.5, 0.5);
    p = poseMix(p, withPose(HOLD_SHEET, SPEAK_LEAN), pw(bt, 137.5, 141.5, 0.5, 0.5));
    if (bt > 142 && bt < 144.6) p.head = (p.head || 0) + Math.sin((bt - 142) * Math.PI * 2.2) * 9 * (1 - seg(bt, 143.6, 144.6));
    p = poseMix(p, withPose(POSES.point), pw(bt, 150, 153.5, 0.5, 0.5));
    if (bt >= 153) {
      // the jump: crouch on 153.5, up on 154, land on 155, arms stay up to the end
      const up = EASE.out(seg(bt, 153.5, 154.1)) * (1 - EASE.in(seg(bt, 154.4, 155)));
      p = poseMix(withPose(), withPose(POSES.cheer, { lift: 0 }), EASE.out(seg(bt, 153, 154)));
      p.lift = 70 * up;
    }
  }
  st.pose = p;
  return st;
}
// the pen hand follows the loop being drawn (a little higher for the first line)
function PEN_TILT(bt) {
  const r = bt < 45 ? 0 : bt < 49 ? 1 : 2;
  return { uaF: [100, 94, 84][r], faF: [108, 100, 90][r] };
}

// ---------- ① 念哪些: 复习笔记 page ----------
const PAGE = { x: 760, y: 286, w: 880, h: 584 };
const PAGE_ROWS = [
  { s: '速度：路程与时间之比', key: '定义', y: 420 },
  { s: 'v = s / t', key: '公式', y: 496, mono: true },
  { s: '单位：m/s，1 m/s = 3.6 km/h', y: 572 },
  { s: '例：50 米跑了 10 秒，v = 5 m/s', y: 648 },
  { s: 'abandon  放弃', key: '单词', y: 724, mono: true },
  { s: '例句：Don\'t abandon your plan.', y: 800 },
];
const LOOPS = [{ row: 0, at: 42 }, { row: 1, at: 46 }, { row: 4, at: 50 }];
function rowWidth(r) { return measure(r.s, r.mono ? 44 : 40, r.mono ? 800 : 900, r.mono ? 'mono' : 'cjk'); }
function loopGeom(r) { const w = rowWidth(r); return { cx: PAGE.x + 60 + w / 2, cy: r.y, rx: w / 2 + 34, ry: 36 }; }
function drawStep1(bt, hero) {
  if (bt < 32 || bt > 64) return;
  const inA = EASE.out(seg(bt, 32, 32.5)), out = 1 - seg(bt, 63.75, 64);
  const a = inA * out;
  if (a <= 0) return;
  withAlpha(a, () => {
    // the page (grows out of the floating page of 8-15 s)
    const sc = lerp(0.6, 1, inA);
    withScale(PAGE.x + PAGE.w / 2, PAGE.y + PAGE.h / 2, sc, () => {
      ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 26;
      rrect(PAGE.x, PAGE.y, PAGE.w, PAGE.h, 18, 'rgba(14,30,66,0.82)', rgba(COL.cyanHi, 0.8), 3); ctx.restore();
      txt('复习笔记', PAGE.x + 60, 344, { size: 40, weight: 900, color: COL.cyanHi });
      line(PAGE.x + 60, 372, PAGE.x + PAGE.w - 60, 372, 'rgba(143,232,248,0.3)', 2);
      const dimRest = 1 - 0.55 * seg(bt, 53, 54);
      PAGE_ROWS.forEach((r, i) => {
        const k = r.key ? 1 : dimRest;
        txt(r.s, PAGE.x + 60, r.y, { size: r.mono ? 44 : 40, weight: r.mono ? 800 : 900, fam: r.mono ? 'mono' : 'cjk', color: COL.cream, alpha: k });
      });
      // silent read-through: a dashed box moves down the rows, one per beat (34-39)
      if (bt >= 34 && bt < 40.5) {
        const i = clamp(Math.floor(bt - 34), 0, 5), r = PAGE_ROWS[i], w = rowWidth(r);
        const fa = win(bt, 34, 40.5, 0.25, 0.5);
        withAlpha(fa, () => {
          ctx.save(); ctx.setLineDash([10, 8]); ctx.strokeStyle = QUIET.hi; ctx.lineWidth = 2.5;
          ctx.beginPath(); ctx.roundRect(PAGE.x + 40, r.y - 32, w + 40, 64, 10); ctx.stroke(); ctx.restore();
          iconEye(PAGE.x + 60 + w + 60, r.y, 34, QUIET.hi);
        });
      }
      // the three loops and their labels
      LOOPS.forEach((L, j) => {
        const r = PAGE_ROWS[L.row], g = loopGeom(r), p = seg(bt, L.at, L.at + 1.5);
        penLoop(g.cx, g.cy, g.rx, g.ry, p, COL.cyan, j + 1);
        const la = popA(bt, L.at + 1.5, 0.3);
        if (la > 0) withAlpha(la, () => {
          const lx = g.cx + g.rx + 22, w = measure(r.key, 34, 900) + 30;
          rrect(lx, r.y - 25, w, 50, 25, rgba(COL.cyan, 0.2), COL.cyan, 2);
          txt(r.key, lx + w / 2, r.y + 1, { size: 34, weight: 900, color: COL.cyanHi, align: 'center' });
        });
      });
    });
  });
  // the light pen and its beam onto the loop being drawn
  if (hero.pen > 0.01) {
    let tx = PAGE.x + 40, ty = PAGE_ROWS[0].y, beam = 0;
    for (const [j, L] of LOOPS.entries()) {
      const r = PAGE_ROWS[L.row], g = loopGeom(r);
      if (bt >= L.at - 0.6 && bt < L.at + 1.9) {
        const p = seg(bt, L.at, L.at + 1.5);
        [tx, ty] = p > 0 ? penLoopEnd(g.cx, g.cy, g.rx, g.ry, p, j + 1) : [g.cx - g.rx, g.cy];
        beam = win(bt, L.at - 0.3, L.at + 1.8, 0.2, 0.3);
      }
    }
    withAlpha(hero.pen * out, () => lightPen(hero.handF[0], hero.handF[1], tx, ty, beam));
  }
  const na = popA(bt, 54, 0.5) * out;
  if (na > 0) txt('挑重点念是作者的建议，没单独测过', PAGE.x, 918, { size: 34, weight: 700, color: COL.grayHi, alpha: na });
}

// ---------- ② 怎么念: the circled definition, said four ways ----------
const LINE2 = '速度是路程与时间之比'.split('');
const WAYS = [
  { s: '出声', y: 404, solid: 1, bright: 1, ring: 1, b0: 66, step: 0.5, num: '66%', color: COL.yellow },
  { s: '小声', y: 514, solid: 1, bright: 0.42, ring: 0.4, b0: 72, step: 0.5, num: '57%', color: '#e9c77e' },
  { s: '只动嘴', y: 624, solid: 1, bright: 0.12, ring: 0, b0: 78, step: 0.5, num: null, color: '#b9a57e' },
  { s: '默读', y: 734, solid: 0, bright: 0, ring: 0, b0: 84, step: 0.12, num: '43%', color: COL.grayHi },
];
const ROW2 = { x0: 866, dx: 82, bw: 70, numX: 1700 };
function drawStep2(bt, hero) {
  if (bt < 64 || bt > 96) return;
  const out = 1 - seg(bt, 95.75, 96), inA = popA(bt, 64, 0.5);
  withAlpha(inA * out, () => {
    WAYS.forEach((wy, r) => {
      const la = popA(bt, wy.b0 - 0.5, 0.4);
      if (la <= 0) return;
      txt(wy.s, 806, wy.y + 1, { size: 40, weight: 900, color: wy.color, align: 'right', alpha: la });
      for (let i = 0; i < LINE2.length; i++) {
        const b = wy.b0 + i * wy.step, x = ROW2.x0 + i * ROW2.dx;
        if (wy.solid === 0) {
          const a = popA(bt, b, 0.3);
          if (a > 0) wordBlock(x, wy.y, ROW2.bw, ROW2.bw, { solid: 0, word: LINE2[i], size: 40, fam: 'cjk', weight: 900, alpha: a });
          continue;
        }
        // flies from his mouth to its slot over half a beat
        if (bt < b - 0.05) continue;
        const e = EASE.out(seg(bt, b, b + 0.5));
        const sx = hero.mouth[0] + 30, sy = hero.mouth[1];
        const fx = lerp(sx, x, e), fy = lerp(sy, wy.y, e) - Math.sin(Math.PI * e) * 60;
        const sz = lerp(36, ROW2.bw, e);
        // the character shows once the block has landed (in flight it would cross the label and the other blocks)
        wordBlock(fx, fy, sz, sz, { solid: wy.solid, bright: wy.bright, word: e > 0.97 ? LINE2[i] : null, glyph: false,
          size: 40, fam: 'cjk', weight: 900, alpha: (0.45 + 0.55 * wy.bright) * popA(bt, b, 0.15) });
      }
      if (wy.ring > 0) for (let i = 0; i < LINE2.length; i++) {
        const b = wy.b0 + i * wy.step;
        soundRings(hero.mouth[0], hero.mouth[1], 1, seg(bt, b, b + 0.7), wy.ring);
      }
      if (wy.ring === 0 && wy.solid && bt >= wy.b0 && bt < wy.b0 + LINE2.length * wy.step) {
        // mouthing: lips move, no sound
        const o = Math.abs(Math.sin((bt - wy.b0) * Math.PI * 2));
        ellipse(hero.mouth[0] + 4, hero.mouth[1] + 2, 7, 2 + 6 * o, rgba(COL.cream, 0.9));
      }
    });
    // the results (Forrin et al. 2012, Exp 2C: aloud 66.1 > whisper 56.7 > silent 42.8 %)
    WAYS.forEach((wy, r) => {
      const at = 87 + r * 0.5, a = popA(bt, at, 0.35);
      if (a <= 0) return;
      if (wy.num) txt(wy.num, ROW2.numX, wy.y + 2, { size: 54, weight: 800, fam: 'mono', color: r === 0 ? COL.yellowHi : wy.color, alpha: a, glow: r === 0 ? 14 : 0 });
      else txt('比默读好', ROW2.numX, wy.y + 1, { size: 34, weight: 900, color: wy.color, alpha: a });
    });
    const ca = popA(bt, 89.5, 0.4);
    if (ca > 0) rich([ink('小声、动嘴也有用，'), ink('正常出声最好', COL.yellow)], 806 - measure('只动嘴', 40, 900), 846, { size: 46, weight: 900, alpha: ca });
    const sa = popA(bt, 90.5, 0.6);
    if (sa > 0) sourceNote('Forrin 等 2012 · 加拿大大学生背单词 · 认出学过的词的比例；只动嘴是同一研究的另一组实验', 806 - measure('只动嘴', 40, 900), 912, { alpha: sa });
  });
}

// ---------- ③ 念了有什么用: two trays, 记住原话 / 读懂意思 (Roberts et al. 2024, Exp 2, Table 1) ----------
const TRAY = [
  { x: 1050, s: '记住原话', icon: 'brain', c: COL.yellow, q: '记忆题', a: 81, si: 74 },
  { x: 1530, s: '读懂意思', icon: 'bulb', c: COL.grayHi, q: '理解题', a: 82, si: 81 },
];
const TRAY_Y = 744, TB = { w: 240, h: 44, gap: 8 };
// spoken blocks: [beat, tray]; tray 0 stacks, tray 1 bounces off
const SHOTS = [[99, 0], [100, 0], [101, 0], [102, 0], [103, 0], [104.5, 1], [105.5, 1]];
const SHOT_WORDS = ['速度是', '路程', '与时间', '之比', 'v=s/t', '为什么？', '怎么用？'];
function drawStep3(bt, hero) {
  if (bt < 96 || bt > 128) return;
  const out = 1 - seg(bt, 127.75, 128), inA = popA(bt, 96, 0.5);
  withAlpha(inA * out, () => {
    TRAY.forEach((tr, k) => {
      ctx.save(); ctx.shadowColor = tr.c; ctx.shadowBlur = 16;
      line(tr.x - 150, TRAY_Y, tr.x + 150, TRAY_Y, tr.c, 5);
      line(tr.x - 150, TRAY_Y, tr.x - 150, TRAY_Y - 26, tr.c, 5); line(tr.x + 150, TRAY_Y, tr.x + 150, TRAY_Y - 26, tr.c, 5);
      ctx.restore();
      ICONS[tr.icon](tr.x - measure(tr.s, 44, 900) / 2 - 34, TRAY_Y + 50, 40, tr.c);
      txt(tr.s, tr.x + 8, TRAY_Y + 50, { size: 44, weight: 900, color: tr.c, align: 'center' });
    });
    let stacked = 0;
    SHOTS.forEach(([b, k], i) => {
      if (bt < b - 0.05) return;
      const tr = TRAY[k], e = EASE.out(seg(bt, b, b + 1));
      const slotY = TRAY_Y - TB.h / 2 - 6 - stacked * (TB.h + TB.gap);
      if (k === 0) stacked += 1;
      let x = lerp(hero.mouth[0] + 40, tr.x, e), y = lerp(hero.mouth[1], k === 0 ? slotY : TRAY_Y - 60, e) - Math.sin(Math.PI * e) * 150;
      let a = 1;
      if (k === 1 && bt > b + 1) {
        // bounces off and falls away
        const f = seg(bt, b + 1, b + 2.2);
        x = tr.x + 60 * f * (i % 2 ? -1 : 1); y = TRAY_Y - 60 - 90 * Math.sin(Math.PI * Math.min(f, 0.5)) + 380 * Math.max(0, f - 0.5) ** 2;
        a = 1 - f;
      }
      const w = lerp(150, TB.w, e), h = lerp(56, TB.h, e);
      const word = e < 0.4 ? SHOT_WORDS[i] : null;
      wordBlock(x, y, w, h, { solid: 1, word, size: 34, fam: word && /^[a-z]/i.test(word) ? 'mono' : 'cjk', weight: 900, glyph: !word, alpha: a });
      soundRings(hero.mouth[0], hero.mouth[1], 1, seg(bt, b, b + 0.7), 1);
    });
    // results
    TRAY.forEach((tr, k) => {
      const at = 106.5 + k * 1.5, a = popA(bt, at, 0.4);
      if (a <= 0) return;
      txt(tr.q, tr.x, TRAY_Y + 104, { size: 34, weight: 700, color: COL.grayHi, align: 'center', alpha: a });
      rich([ink(`出声 ${tr.a}%`, k ? COL.cream : COL.yellow), ink(` · 默读 ${tr.si}%`, COL.grayHi)], tr.x, TRAY_Y + 152,
        { size: 40, weight: 900, align: 'center', alpha: a });
      const my = TRAY_Y - (k ? 70 : 6 * (TB.h + TB.gap) + 40);
      if (k === 0) { const cs = popS(bt, at, 0.6); if (cs > 0) withScale(tr.x + 170, my, cs, () => okMark(tr.x + 170, my, 26, seg(bt, at, at + 0.7))); }
      else withAlpha(a, () => txt('≈ 差不多', tr.x, my, { size: 44, weight: 900, color: COL.grayHi, align: 'center' }));
    });
    const qa = win(bt, 113.5, 118.5, 0.5, 0.5);
    if (qa > 0) txt('?', TRAY[1].x, TRAY_Y - 150 - 10 * Math.sin(bt * Math.PI), { size: 96, weight: 900, color: COL.pink, align: 'center', alpha: qa, glow: 18 });
    const ra = popA(bt, 115, 0.5);
    if (ra > 0) txt('要读懂：另想办法', TRAY[1].x, TRAY_Y - 236, { size: 40, weight: 900, color: COL.pink, align: 'center', alpha: ra });
    const sa = popA(bt, 110, 0.6);
    if (sa > 0) sourceNote('Roberts 等 2024 实验 2 · 64 名成年人 · 英文短文，一部分出声读，读完做选择题', 760, 984, { alpha: sa });
  });
}

// ---------- 照着做: a track of three clips + the pink note ----------
const CLIPS = [
  { x: 640, w: 340, at: 130, s: '默读一遍', sub: '整页先过一遍', kind: 'silent' },
  { x: 1040, w: 380, at: 134, s: '圈出要背的', sub: '定义、公式、单词', kind: 'pen' },
  { x: 1480, w: 320, at: 138, s: '念出声', sub: '一字一字，正常出声', kind: 'aloud' },
];
const CLIP_Y = 430, CLIP_H = 140;
function drawSummary(bt, hero) {
  if (bt < 128) return;
  const inA = EASE.out(seg(bt, 128, 128.5));
  withAlpha(inA, () => {
    CLIPS.forEach((c, i) => {
      const a = popA(bt, c.at, 0.35), sc = popS(bt, c.at, 0.6);
      if (a <= 0) return;
      withAlpha(a, () => withScale(c.x + c.w / 2, CLIP_Y, 0.85 + 0.15 * sc, () => {
        const x = c.x, y = CLIP_Y - CLIP_H / 2;
        if (c.kind === 'silent') {
          wordBlock(x + c.w / 2, CLIP_Y, c.w, CLIP_H, { solid: 0, glyph: false, r: 20 });
          txt(c.s, x + c.w / 2, CLIP_Y, { size: 54, weight: 900, color: COL.grayHi, align: 'center' });
        } else if (c.kind === 'pen') {
          rrect(x, y, c.w, CLIP_H, 20, 'rgba(14,30,66,0.85)', rgba(COL.cyan, 0.8), 3);
          txt(c.s, x + c.w / 2, CLIP_Y, { size: 54, weight: 900, color: COL.cream, align: 'center' });
          penLoop(x + c.w / 2, CLIP_Y, c.w / 2 - 14, CLIP_H / 2 - 16, seg(bt, c.at + 0.5, c.at + 2), COL.cyan, 3);
        } else {
          wordBlock(x + c.w / 2, CLIP_Y, c.w, CLIP_H, { solid: 1, glyph: false, r: 20 });
          txt(c.s, x + c.w / 2, CLIP_Y, { size: 58, weight: 900, color: INK, align: 'center' });
        }
        txt(c.sub, x + c.w / 2, CLIP_Y + 112, { size: 36, weight: 700, color: c.kind === 'aloud' ? COL.yellow : COL.grayHi, align: 'center' });
      }));
      if (i < 2) {
        const aa = popA(bt, CLIPS[i + 1].at - 0.5, 0.3);
        if (aa > 0) txt('→', c.x + c.w + 30, CLIP_Y - 2, { size: 54, weight: 800, fam: 'mono', color: COL.cream, align: 'center', alpha: aa });
      }
    });
    const wa = popA(bt, 142, 0.35);
    if (wa > 0) withAlpha(wa, () => withScale(1220, 664, 0.9 + 0.1 * popS(bt, 142, 0.6), () => {
      rrect(640, 618, 1160, 92, 16, 'rgba(255,111,158,0.12)', 'rgba(255,111,158,0.8)', 2.5);
      rich([ink('读懂另想办法', COL.pink), ink('：念出声帮你记原话，不帮你读懂')], 678, 664, { size: 44, weight: 900 });
    }));
    const fa = popA(bt, 144, 0.6);
    if (fa > 0) {
      txt('仅供参考：国外的大学生和成年人；单词和英文短文；都是学完当场测', 640, 770, { size: 32, weight: 700, color: COL.gray, alpha: fa });
      txt('MacLeod 2010 · Icht 2014 · Forrin 2012 · Forrin & MacLeod 2018 · Roberts 2024', 640, 816, { size: 24, weight: 500, fam: 'mono', color: COL.grayDim, alpha: fa });
    }
  });
  // what he does for each clip: the dashed box, the pen loop, the spoken block
  if (bt >= 130 && bt < 133.5) withAlpha(win(bt, 130, 133.5, 0.5, 0.5), () => wordBlock(hero.handF[0] + 60, hero.handF[1] - 90, 120, 48, { solid: 0, glyph: true }));
  if (hero.pen > 0.01) {
    const c = CLIPS[1], p = seg(bt, c.at + 0.5, c.at + 2);
    const [tx, ty] = p > 0 && p < 1 ? penLoopEnd(c.x + c.w / 2, CLIP_Y, c.w / 2 - 14, CLIP_H / 2 - 16, p, 3) : [c.x + 20, CLIP_Y];
    withAlpha(hero.pen, () => lightPen(hero.handF[0], hero.handF[1], tx, ty, p > 0 && p < 1 ? 1 : 0.4));
  }
  for (const b of [138, 139, 140]) {
    const e = EASE.out(seg(bt, b, b + 1));
    if (bt >= b && bt < b + 1) {
      const c = CLIPS[2];
      wordBlock(lerp(hero.mouth[0] + 40, c.x + c.w / 2, e), lerp(hero.mouth[1], CLIP_Y, e) - Math.sin(Math.PI * e) * 130,
        lerp(120, 80, e), lerp(48, 34, e), { solid: 1, glyph: true, alpha: 1 - seg(bt, b + 0.8, b + 1) });
    }
    soundRings(hero.mouth[0], hero.mouth[1], 1, seg(bt, b, b + 0.7), 1);
  }
}

// ---------- wiring ----------
function drawPanelLayer(bt, t) {}
function drawStrip(hero) {
  // ② the circled line on a strip in his hand
  const [hx, hy] = hero.handF;
  ctx.save(); ctx.translate(hx + 6, hy - 22); ctx.rotate(-0.08);
  ctx.shadowColor = COL.cyan; ctx.shadowBlur = 12;
  rrect(-20, -30, 96, 52, 8, 'rgba(14,30,66,0.9)', rgba(COL.cyanHi, 0.9), 2.5);
  ctx.shadowBlur = 0;
  line(-6, -10, 62, -10, 'rgba(255,213,126,0.9)', 5); line(-6, 6, 40, 6, 'rgba(255,213,126,0.9)', 5);
  ctx.restore();
}
function drawSections(bt, t, hero) {
  if (bt < 31) return;
  if (hero.hold === 'strip') drawStrip(hero);
  drawHeaders(bt);
  drawStep1(bt, hero);
  drawStep2(bt, hero);
  drawStep3(bt, hero);
  drawSummary(bt, hero);
}

// speech events for the stage wave
WAYS.forEach((wy) => { if (wy.ring > 0) for (let i = 0; i < LINE2.length; i++) addSpeech(wy.b0 + i * wy.step, 395, wy.ring); });
SHOTS.forEach(([b]) => addSpeech(b, 415, 1));
[138, 139, 140].forEach((b) => addSpeech(b, 395, 1));
