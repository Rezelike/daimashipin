// sections.js — 怎么睡 ①②③ (32–128) and 照着做 (128–160), plus the layers every section shares (gauge, bubbles, the
// figure's states). Each step is acted out on the pool stage; no STEP pages.
const INK = '#14213f';
const hl = (s, color = COL.yellow) => ({ s, color });
const cr = (s) => ({ s, color: COL.cream });

// ---------- headers ----------
const HEADERS = [
  { from: 32, to: 63.5, num: '1', title: '睡多久', sub: 'Need it right away? 10 minutes asleep.',
    line2: () => [cr('马上要用：'), hl('睡着 10 分钟')] },
  { from: 64, to: 95.5, num: '2', title: '睡久了怎么办', sub: 'Long nap? Give it 30 minutes, then the hard stuff.',
    line2: () => [cr('醒来先'), hl('缓 30 分钟'), cr('，再做难题')] },
  { from: 96, to: 126.5, num: '3', title: '醒来先干嘛', sub: "Feeling awake isn't being awake. Start easy.",
    line2: (bt) => (bt < 117.0 ? [cr('觉得醒了，'), hl('不等于真醒了', COL.pink)] : [cr('醒来：'), hl('先做简单的')]) },
  { from: 127, to: 161, num: null, title: '照着做', sub: 'How long to nap, and what to do after.',
    line2: () => [cr('午睡'), hl('睡多久'), cr('，醒来做什么')] },
];
function drawHeaders(bt) {
  for (const h of HEADERS) {
    const inP = EASE.out(seg(bt, h.from, h.from + 0.6)), outP = EASE.in(seg(bt, h.to - 0.5, h.to));
    const a = inP * (1 - outP);
    if (a <= 0) continue;
    // line 2 of ③ turns into the action at 117.0
    stepHeader(h.num, h.title, h.line2(bt), h.sub, {
      alpha: a, dx: (1 - inP) * -40 - outP * 40, typeP: seg(bt, h.from + 0.5, h.from + 3.0), bt,
      bubble: h.num === '1' ? 1 : popS(bt, h.from, 0.7),
    });
  }
}

// ---------- the gauge and bubbles (drawn on top of the water tint) ----------
function gaugeState(bt, my) {
  const marks10 = { y: DEPTH.m10, s: '10 分钟' }, marks30 = { y: DEPTH.m30, s: '30 分钟' };
  if (bt < 16.6) {
    // opening: each mark lights up as the mattress passes it on the way down
    marks10.lit = bt < 4.5 ? seg(my, DEPTH.m10 - 12, DEPTH.m10) : 1;
    marks30.lit = bt < 4.5 ? seg(my, DEPTH.m30 - 12, DEPTH.m30) : 1;
    marks30.color = COL.pink;
    return { marks: [marks10, marks30], ptr: { y: my, a: 1 } };
  }
  if (bt < 32) {
    marks10.lit = popA(bt, 26.5, 0.4); marks30.lit = popA(bt, 27.5, 0.4); marks30.color = COL.pink;
    return { marks: [marks10, marks30], ptr: { y: my, a: 1 - seg(bt, 16.5, 17.0) } };
  }
  if (bt < 64) {
    marks10.lit = seg(my, DEPTH.m10 - 12, DEPTH.m10) * (bt < 47 ? 1 : 1 - seg(bt, 47, 48)) + (bt >= 47 ? 0.25 : 0);
    return { marks: [marks10, { ...marks30, lit: 0 }], ptr: { y: my, a: popA(bt, 33.5, 0.5) } };
  }
  if (bt < 96) {
    marks10.lit = 0;
    const za = popA(bt, 70, 0.5);
    return { marks: [marks10], ptr: { y: my, a: 1 }, zone: { y0: 868, y1: 980, a: za } };
  }
  return { marks: [marks10, marks30], ptr: null, alpha: lerp(0.55, 0, seg(bt, 125.5, 126.5)) };
}
function drawInWater(bt, t, pts, hp) {
  const g = gaugeState(bt, hp.my);
  if ((g.alpha ?? 1) > 0) drawGauge(g.marks, { alpha: g.alpha ?? 1, ptr: g.ptr, zone: g.zone });
  if (bt >= 64 && bt < 96) {
    const za = popA(bt, 70, 0.5) * (1 - seg(bt, 95.0, 95.5));
    if (za > 0) {
      txt('为了记得牢', 124, 898, { size: 34, weight: 900, color: COL.cream, alpha: za });
      txt('睡 30–60 分钟', 124, 944, { size: 36, weight: 900, color: COL.yellow, alpha: popA(bt, 70.5, 0.5) * (1 - seg(bt, 95.0, 95.5)), glow: 12 });
    }
  }
  // air bubbles from the mattress while it sinks
  const mx = hp.mx, my = hp.my;
  bubbleStream(mx + 40, my - 30, bt, 0, 4.4, { seed: 11, gap: 0.16, spread: 260 });
  bubbleStream(mx + 40, my - 30, bt, 38.5, 46, { seed: 12, gap: 0.6, spread: 200 });
  bubbleStream(mx + 40, my - 30, bt, 66, 72, { seed: 13, gap: 0.16, spread: 260 });
  bubbleStream(mx + 40, my - 30, bt, 134.5, 136.2, { seed: 14, gap: 0.18, spread: 220 });
  if (bt > 153.5) bubbleStream(pts.head[0], pts.head[1] - 20, bt, 153.5, 160, { seed: 15, gap: 0.5, spread: 60, rise: 120 });
  // ② the six bubbles on the surface pop one by one: 醒来 5, 10, ... 30 分钟
  if (bt >= 72.5 && bt < 96) drawSurfaceBubbles(bt, hp);
  // summary footer (in the water, under the rows)
  if (bt >= 143.5) {
    const fa = popA(bt, 144, 0.6);
    txt('仅供参考：被试都是缺觉的成年人', 680, 700, { size: 30, weight: 700, color: COL.grayHi, alpha: fa });
    txt('10 分钟指真睡着的时间', 680, 742, { size: 30, weight: 700, color: COL.grayHi, alpha: popA(bt, 144.5, 0.6) });
  }
}

// ---------- ① 睡多久: lie down -> falling asleep (no sinking) -> asleep 10 minutes (sinks a little) -> phone -> up at once ----------
const STRIP = { x0: 700, xA: 980, xB: 1480, y: 330, phone: 1580 };
function stripCursor(bt) {
  if (bt < 34) return STRIP.x0;
  if (bt < 38) return lerp(STRIP.x0, STRIP.xA, (bt - 34) / 4);
  return lerp(STRIP.xA, STRIP.xB, seg(bt, 38, 46));
}
function drawStep1(bt, t, pts, hp) {
  if (bt < 33 || bt > 64) return;
  const out = 1 - seg(bt, 63.0, 63.5);
  const sa = popA(bt, 34, 0.5) * out;
  if (sa > 0) withAlpha(sa, () => {
    const { x0, xA, xB, y, phone } = STRIP, cx = stripCursor(bt);
    rrect(x0, y - 11, xB - x0, 22, 11, 'rgba(255,255,255,0.08)', 'rgba(200,215,240,0.3)', 2);
    if (cx > x0) rrect(x0, y - 11, Math.min(cx, xA) - x0, 22, 11, '#7b86a3');
    if (cx > xA) { ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 14; rrect(xA, y - 11, cx - xA, 22, 11, COL.yellow); ctx.restore(); }
    line(xA, y - 26, xA, y + 26, 'rgba(243,238,227,0.8)', 3);
    ctx.save(); ctx.shadowColor = COL.cyanHi; ctx.shadowBlur = 16; circle(cx, y, 15, COL.cream); ctx.restore();
    txt('躺下', x0, y - 50, { size: 34, weight: 900, color: COL.cream });
    txt('睡着', xA, y - 50, { size: 34, weight: 900, color: bt >= 38 ? COL.yellow : COL.grayHi, align: 'center' });
    txt('入睡', (x0 + xA) / 2, y + 48, { size: 34, weight: 900, color: COL.grayHi, align: 'center' });
    txt('睡着 10 分钟', (xA + xB) / 2, y + 50, { size: 40, weight: 900, color: COL.yellow, align: 'center', alpha: popA(bt, 38, 0.4), glow: 12 });
    const ring = bt >= 46 && bt < 47.5 ? 1 - seg(bt, 47, 47.5) : 0;
    drawPhone(phone, y, ring * (0.6 + 0.4 * Math.abs(Math.sin(bt * Math.PI * 4))), { lit: bt >= 46 ? 1 : 0.15 });
    txt('闹钟', phone, y + 92, { size: 34, weight: 900, color: COL.cream, align: 'center' });
    lintPanel('strip', x0, y - 66, xB, y + 72);
  });
  // falling asleep, then asleep
  if (bt >= 38 && bt < 46.4) drawZz(pts.head[0] + 30, pts.head[1] - 60, bt, popA(bt, 38, 0.4) * (1 - seg(bt, 46, 46.4)));
  // up at once: splash + check
  drawSplash(hp.mx, WY, seg(bt, 47.0, 48.0), { n: 10, size: 0.8 });
  drawRipple(hp.mx, WY + 4, seg(bt, 47.0, 48.5), { r: 220 });
  const ok = popS(bt, 47.5, 0.6) * out;
  if (ok > 0) withScale(pts.head[0] + 70, pts.head[1] - 70, ok, () => okMark(pts.head[0] + 70, pts.head[1] - 70, 26, seg(bt, 47.5, 48.1)));
  const na = popA(bt, 48.5, 0.6) * out;
  if (na > 0) txt('10 分钟是真睡着的时间，闹钟要多留入睡的时间', 1130, 474, { size: 34, weight: 900, color: COL.cream, align: 'center', alpha: na });
  // Brooks & Lack 2006 p. 834: tests (of 7) better than no nap, 5 min after waking: 10-min nap 5, 30-min nap 0
  const ba = popA(bt, 54, 0.5) * out;
  if (ba > 0) withAlpha(ba, () => {
    txt('醒来 5 分钟，7 项测验里好过没睡的', 1130, 672, { size: 34, weight: 900, color: COL.cream });
    const rows = [{ y: 748, s: '睡 10 分钟', n: 5, c: COL.yellow, at: 54.5 }, { y: 832, s: '睡 30 分钟', n: 0, c: COL.pink, at: 57.5 }];
    for (const r of rows) {
      const ra = popA(bt, r.at, 0.4);
      if (ra <= 0) continue;
      withAlpha(ra, () => {
        txt(r.s, 1130, r.y, { size: 36, weight: 900, color: r.c });
        for (let k = 0; k < 7; k++) {
          const lit = k < r.n && bt >= r.at + k * 0.5, cx = 1330 + k * 40;
          if (lit) { const sc = popS(bt, r.at + k * 0.5, 0.5); withScale(cx, r.y, sc, () => { ctx.save(); ctx.shadowColor = r.c; ctx.shadowBlur = 12; circle(cx, r.y, 15, r.c); ctx.restore(); }); }
          else circle(cx, r.y, 15, 'rgba(255,255,255,0.05)', 'rgba(200,215,240,0.45)', 2);
        }
        const ca = popA(bt, r.at + Math.max(1, r.n) * 0.5, 0.4);
        txt(`${r.n} 项`, 1630, r.y + 2, { size: 40, weight: 900, color: r.c, alpha: ca, glow: r.n ? 12 : 0 });
      });
    }
    lintPanel('brooks', 1130, 650, 1720, 856);
    sourceNote('Brooks & Lack 2006 · 24 名大学生 · 5 到 30 分钟里，10 分钟总体最好', 1130, 984, { alpha: popA(bt, 59, 0.6) });
  });
}

// ---------- ② 睡久了怎么办: sinks deep, wakes groggy, rises slowly while six surface bubbles pop (醒来 5 … 30 分钟) ----------
const SB = { x0: 840, dx: 46, n: 6, pop0: 76, step: 2 };
function drawSurfaceBubbles(bt, hp) {
  const out = 1 - seg(bt, 95.0, 95.5);
  withAlpha(out, () => {
    for (let k = 0; k < SB.n; k++) {
      const tx = SB.x0 + k * SB.dx, ty = WY - 14, popAt = SB.pop0 + k * SB.step;
      const rise = EASE.out(seg(bt, 72.5 + k * 0.5, 74.0 + k * 0.5));
      if (rise <= 0) continue;
      if (bt < popAt) {
        const x = lerp(hp.mx + 60, tx, rise), y = lerp(hp.my - 40, ty, rise);
        drawBubble(x, y, 17, 1);
      } else if (bt < popAt + 0.5) {
        const p = seg(bt, popAt, popAt + 0.5);
        withAlpha(1 - p, () => {
          ctx.save(); ctx.strokeStyle = COL.cyanHi; ctx.lineWidth = 3; ctx.lineCap = 'round';
          for (let i = 0; i < 6; i++) { const an = (i / 6) * TAU, r0 = 12 + p * 20; ctx.beginPath(); ctx.moveTo(tx + Math.cos(an) * r0, ty + Math.sin(an) * r0); ctx.lineTo(tx + Math.cos(an) * (r0 + 9), ty + Math.sin(an) * (r0 + 9)); ctx.stroke(); }
          ctx.restore();
        });
      }
    }
    // counter
    const popped = Math.max(0, Math.min(SB.n, Math.floor((bt - SB.pop0) / SB.step) + 1));
    const ca = popA(bt, SB.pop0, 0.4);
    if (ca > 0) {
      const done = popped >= SB.n;
      rich([{ s: '醒来 ' }, { s: `${popped * 5} 分钟`, color: done ? COL.yellow : COL.cream, glow: done ? 12 : 0 }], 955, 572, { size: 40, weight: 900, align: 'center', alpha: ca });
      lintPanel('counter', 840, 548, 1070, 596);
    }
  });
}
function drawStep2(bt, t, pts, hp) {
  if (bt < 64 || bt > 96) return;
  const out = 1 - seg(bt, 95.0, 95.5);
  drawDizzy(pts.head[0], pts.head[1] - 62, bt, popA(bt, 72.5, 0.4) * (1 - seg(bt, 86.5, 87.0)) * out);
  const ok = popS(bt, 88.0, 0.6) * out;
  if (ok > 0) withScale(1010, 520, ok, () => { okMark(900, 520, 22, seg(bt, 88.0, 88.6), COL.yellow); txt('缓过来了', 934, 521, { size: 36, weight: 900, color: COL.yellow, glow: 10 }); });
  // the deck face: what the experiment measured
  const ea = popA(bt, 76, 0.5) * out;
  if (ea > 0) withAlpha(ea, () => {
    txt('睡 30、60 分钟的：', 1130, 672, { size: 34, weight: 900, color: COL.grayHi });
    txt('醒来 5 分钟，做题变慢', 1130, 728, { size: 40, weight: 900, color: COL.pink });
    txt('30 分钟内缓过来', 1130, 786, { size: 40, weight: 900, color: COL.yellow, alpha: popA(bt, 86, 0.5), glow: 10 });
    lintPanel('leong', 1130, 650, 1600, 810);
    sourceNote('Leong 等 2023 · 32 名成年人 · 不睡 / 10 / 30 / 60 分钟', 1130, 984, { alpha: popA(bt, 78, 0.6) });
  });
  // 再做难题: the card in his raised hand
  const ha = popA(bt, 90.0, 0.4) * out;
  if (ha > 0) withAlpha(ha, () => {
    const cx = pts.handF[0], cy = pts.handF[1] - 50;
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 14; rrect(cx - 78, cy - 46, 156, 92, 14, '#f2eee4'); ctx.restore();
    rrect(cx - 78, cy - 46, 156, 16, [14, 14, 0, 0], COL.pink);
    txt('难题', cx, cy + 8, { size: 44, weight: 900, color: INK, align: 'center' });
    const cs = popS(bt, 91.5, 0.6);
    if (cs > 0) withScale(cx + 74, cy - 42, cs, () => okMark(cx + 74, cy - 42, 22, seg(bt, 91.5, 92.1)));
    lintPanel('hard card', cx - 78, cy - 46, cx + 78, cy + 46);
  });
}

// ---------- ③ 醒来先干嘛: on the deck. 醒了！ but the task goes slowly; curtain open, splash the face, easy ones first ----------
const S3 = {
  x: KB([[97.0, 810], [97.5, 810], [100.5, 1170, 'lin'], [107.5, 1170], [110.5, 1543, 'lin'], [111.0, 1543], [112.5, 1713, 'out'],
    [112.5, 1713], [116.5, 1150, 'lin'], [160, 1150]]),
  dir: (bt) => (bt >= 112.5 && bt < 117.6 ? -1 : 1),
  pose: PT([[97.0, 'sitLong'], [97.5, 'stand', 'out'], [100.5, 'stand'], [102.5, 'stand'], [103.0, 'write', 'out'], [107.2, 'write'],
    [107.5, 'stand'], [110.5, 'stand'], [111.0, 'pull', 'out'], [112.4, 'pull'], [112.5, 'stand'], [116.5, 'stand'], [117.0, 'scoop', 'out'],
    [117.2, 'scoop'], [117.5, 'splash', 'out'], [118.5, 'splash'], [119.0, 'stand', 'out'], [119.5, 'write', 'out'], [122.5, 'write'], [123.0, 'stand', 'out']]),
};
// one step per beat, walks start on half beats so the footfalls land on the beats (98, 99, 100 / 108, 109, 110 / 113–116)
const WALKS = [[97.5, 100.5], [107.5, 110.5], [112.5, 116.5]];
function walkAt(bt) {
  for (const [a, b] of WALKS) if (bt > a && bt < b) return { phase: bt - a, k: Math.min(1, (bt - a) * 6, (b - bt) * 6) };
  return null;
}
// the experiment's task, done slowly: key (shape -> digit) and a row to fill in
const KEY = [3, 7, 1, 5, 9];
const TASK = [2, 0, 4, 1, 3, 0];
const SLOW = [104.0, 105.5, 107.0];   // only three digits in three beats
const EASY = [{ s: '收拾桌面', at: 120.0 }, { s: '翻一遍错题', at: 121.0 }];
function drawTaskBoard(bt) {
  const a = popA(bt, 102.0, 0.5) * (1 - seg(bt, 126.0, 126.5));
  if (a <= 0) return;
  const { x, y, w, h } = BOARD;
  withAlpha(a, () => {
    drawBoardFrame();
    const fl = flipSX(bt, 117.0, 0.5);
    ctx.save(); ctx.translate(x + w / 2, 0); ctx.scale(Math.max(0.02, fl.sx), 1); ctx.translate(-(x + w / 2), 0);
    if (fl.side === 0) {
      txt('把符号换成数字', x + w / 2, y + 32, { size: 34, weight: 900, color: INK, align: 'center' });
      KEY.forEach((d, k) => {
        const cx = x + 66 + k * 62;
        rrect(cx - 26, y + 62, 52, 76, 8, '#e3dccb');
        shapeIcon(k, cx, y + 86, 13, '#3d4a6b');
        txt(String(d), cx, y + 120, { size: 30, weight: 800, fam: 'mono', color: INK, align: 'center' });
      });
      TASK.forEach((s, k) => {
        const cx = x + 60 + k * 52;
        shapeIcon(s, cx, y + 170, 13, '#3d4a6b');
        rrect(cx - 21, y + 192, 42, 46, 6, '#ffffff', '#9aa3b8', 2);
        const at = SLOW[k];
        if (at !== undefined && bt >= at) txt(String(KEY[s]), cx, y + 216, { size: 30, weight: 800, fam: 'mono', color: '#1f5fbf', align: 'center', alpha: popA(bt, at, 0.3) });
      });
    } else {
      txt('先做简单的', x + w / 2, y + 36, { size: 34, weight: 900, color: INK, align: 'center' });
      EASY.forEach((e, k) => {
        const cy = y + 86 + k * 58;
        rrect(x + 20, cy - 24, w - 40, 48, 10, '#dff3e7', '#59d68f', 2);
        txt(e.s, x + 40, cy + 1, { size: 34, weight: 900, color: INK });
        const c = popS(bt, e.at, 0.5);
        if (c > 0) withScale(x + w - 48, cy, c, () => okMark(x + w - 48, cy, 17, seg(bt, e.at, e.at + 0.5), COL.green));
      });
      const hy = y + 86 + 2 * 58, slide = EASE.out(seg(bt, 122.5, 123.0));
      rrect(x + 20 + slide * 20, hy - 24, w - 40, 48, 10, '#ffe1e8', COL.pink, 2);
      txt('难题', x + 40 + slide * 20, hy + 1, { size: 34, weight: 900, color: INK });
      txt('缓过来再做', x + w - 34 + slide * 20, hy + 1, { size: 34, weight: 900, color: '#b2335d', align: 'right', alpha: popA(bt, 122.5, 0.4) });
    }
    ctx.restore();
    txt('常见做法', x + w - 16, y + h - 14, { size: 24, weight: 700, color: '#7b8499', align: 'right', alpha: fl.side === 1 ? popA(bt, 118, 0.4) : 0 });
  });
}
function flipSX(bt, t0, d) {
  const p = seg(bt, t0, t0 + d);
  return { side: p < 0.5 ? 0 : 1, sx: Math.abs(Math.cos(Math.PI * p)) };
}
function drawStep3(bt, t, pts, hp) {
  if (bt < 96 || bt > 128) return;
  const out = 1 - seg(bt, 126.0, 126.5);
  drawTaskBoard(bt);
  drawCurtain(EASE.out(seg(bt, 111.0, 112.5)), { alpha: popA(bt, 96.5, 0.6) * out });
  // 醒了！ (he says so) — the speech bubble with a check over his head
  const sp = popS(bt, 101.0, 0.6) * (1 - seg(bt, 106.5, 107.0));
  if (sp > 0) drawSpeech(pts.head[0] + 10, pts.head[1] - 96, '醒了！', { scale: sp, alpha: clamp(sp * 2) });
  // the deck face: labels under each action, the note, the source
  withAlpha(out, () => {
    const l1 = popA(bt, 105.0, 0.4);
    if (l1 > 0) txt('做得很慢', BOARD.x + BOARD.w / 2, 664, { size: 40, weight: 900, color: COL.pink, align: 'center', alpha: l1 });
    const l2 = popA(bt, 112.5, 0.4);
    if (l2 > 0) txt('见光', 1770, 664, { size: 40, weight: 900, color: COL.yellow, align: 'center', alpha: l2, glow: 12 });
    const l3 = popA(bt, 117.5, 0.4);
    if (l3 > 0) txt('洗把脸', 1180, 664, { size: 40, weight: 900, color: COL.cyanHi, align: 'center', alpha: l3 });
    const n1 = popA(bt, 106.0, 0.5);
    if (n1 > 0) txt('睡 60 分钟的：醒来不觉得困，做题却最慢', 1130, 742, { size: 34, weight: 700, color: COL.grayHi, alpha: n1 });
    const n2 = popA(bt, 123.5, 0.5);
    if (n2 > 0) txt('见光、洗脸有点用（小研究，效果小）', 1130, 800, { size: 34, weight: 900, color: COL.cream, alpha: n2 });
    sourceNote('Leong 等 2023 · 见光、洗脸：Hayashi 等 2003', 1130, 984, { alpha: popA(bt, 107, 0.6) });
  });
  // splash
  drawSplash(1020, WY - 10, seg(bt, 117.0, 118.0), { n: 8, size: 0.6 });
  drawSplash(pts.head[0], pts.head[1], seg(bt, 117.5, 118.5), { n: 12, size: 0.55 });
  drawRipple(1030, WY + 4, seg(bt, 117.0, 118.5), { r: 120 });
}

// ---------- 照着做: three bubble rows (the ①②③ tags with their answers); he acts each, points, jumps in ----------
const ROWS = [
  { y: 318, at: 130, n: 1, spans: [cr('马上要用 → '), hl('睡 10 分钟')], depth: 0.18 },
  { y: 434, at: 134, n: 2, spans: [cr('为了记 → '), hl('睡 30–60 分钟'), cr('，醒来缓 30 分钟')], depth: 0.8 },
  { y: 550, at: 140.5, n: 3, spans: [cr('醒来 → '), hl('先做简单的')], depth: -1 },
];
const ROW_X = 600;
function depthGlyph(x, y, depth, a = 1) {
  withAlpha(a, () => {
    ctx.save(); ctx.beginPath(); ctx.roundRect(x - 34, y - 34, 68, 68, 12); ctx.clip();
    ctx.fillStyle = '#0d1a3c'; ctx.fillRect(x - 34, y - 34, 68, 68);
    const g = ctx.createLinearGradient(0, y - 18, 0, y + 34);
    g.addColorStop(0, '#2a74a8'); g.addColorStop(1, '#0f2d55');
    ctx.fillStyle = g; ctx.fillRect(x - 34, y - 18, 68, 52);
    line(x - 34, y - 18, x + 34, y - 18, 'rgba(165,236,255,0.9)', 2.5);
    if (depth >= 0) drawMiniMattress(x, y - 18 + 6 + depth * 36, 46);
    else { iconSun(x, y - 2, 40, COL.yellow); }
    ctx.restore();
    rrect(x - 34, y - 34, 68, 68, 12, null, 'rgba(165,236,255,0.6)', 2);
  });
}
function drawSummary(bt, t, pts, hp) {
  if (bt < 126.2) return;
  ROWS.forEach((r) => {
    const a = popA(bt, r.at, 0.35);
    if (a <= 0) return;
    const sc = lerp(0.6, 1, EASE.back(clamp((bt - r.at) / 0.7)));
    const rise = EASE.out(seg(bt, r.at, r.at + 0.7));
    const tw = richWidth(r.spans, 48, 900), w = tw + 196, h = 92, y = r.y + (1 - rise) * 60;
    withAlpha(a, () => withScale(ROW_X + w / 2, y, sc, () => {
      ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 16;
      rrect(ROW_X, y - h / 2, w, h, h / 2, 'rgba(16,58,98,0.82)', COL.cyanHi, 3); ctx.restore();
      ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.5)'; ctx.lineWidth = 4; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(ROW_X + 50, y - h / 2 + 12); ctx.lineTo(ROW_X + 100, y - h / 2 + 10); ctx.stroke(); ctx.restore();
      circle(ROW_X + 48, y, 27, COL.cyan);
      txt(String(r.n), ROW_X + 48, y + 1, { size: 32, weight: 800, fam: 'mono', color: '#0b1736', align: 'center' });
      rich(r.spans, ROW_X + 92, y + 1, { size: 48, weight: 900 });
      depthGlyph(ROW_X + w - 56, y, r.depth);
      lintPanel('row' + r.n, ROW_X, y - h / 2, ROW_X + w, y + h / 2);
    }));
  });
  sourceNote('Tietzel & Lack 2001 · Brooks & Lack 2006 · Leong 等 2023', 1130, 984, { alpha: popA(bt, 144.5, 0.6) });
  // the acted rows: a quick splash when he pops up (row 1), the dizzy rise (row 2), the face splash (row 3)
  drawDizzy(pts.head[0], pts.head[1] - 62, bt, popA(bt, 136.5, 0.4) * (1 - seg(bt, 139.5, 140.0)));
  drawSplash(hp.mx, WY, seg(bt, 132.0, 133.0), { n: 8, size: 0.7 });
  drawSplash(pts.head[0], pts.head[1], seg(bt, 141.0, 142.0), { n: 12, size: 0.55 });
  // the jump: splash where he enters the water
  drawSplash(JUMP.x1, WY, seg(bt, 153.5, 155.0), { n: 16, size: 1.1 });
  drawRipple(JUMP.x1, WY + 4, seg(bt, 153.5, 156.0), { r: 260 });
}

// ---------- hero overrides: on the deck in ③, back on the mattress for the summary, the jump ----------
const SUM_POSE = PT([[127.0, 'sitLong'], [130.0, 'sitLong'], [130.5, 'lie', 'out'], [131.5, 'lie'], [132.0, 'sitLong', 'out'], [134.0, 'sitLong'],
  [134.5, 'lie', 'out'], [136.5, 'lie'], [137.0, 'sitSlump', 'out'], [139.5, 'sitSlump'], [140.0, 'sitLong', 'out'], [140.5, 'sitLong'],
  [141.0, 'sitSplash', 'out'], [142.5, 'sitSplash'], [143.0, 'sitLong', 'out'], [145.5, 'sitLong'], [146.0, 'sitPoint', 'out'], [150.0, 'sitPoint'],
  [150.5, 'sitLong', 'out'], [151.0, 'sitLong'], [151.5, 'stand', 'out'], [152.0, 'stand'], [152.5, 'crouch', 'out'], [153.0, 'tuck', 'out'],
  [154.5, 'tuck'], [155.0, 'swim', 'out'], [160, 'swim']]);
const JUMP = { t0: 152.5, t1: 153.5, x0: 230, x1: 540, peak: 120 };
function decorateHero(hp, bt, t) {
  const f = hp.fig;
  if (bt >= 97.0 && bt < 127.5) {
    // ③: he stands up on the mattress (now by the deck) and walks onto the deck
    const wk = walkAt(bt);
    const pose = wk ? lerpPose(S3.pose(bt), walkPose(wk.phase), wk.k) : S3.pose(bt);
    Object.assign(f, { x: S3.x(bt), y: lerp(hp.my - MAT.h / 2 + 3, DECK_TOP - 8, seg(bt, 99.6, 100.0)),
      dir: S3.dir(bt), pose, face: faceAt(bt, bt >= 101 && bt < 104 ? 'happy' : bt >= 104 && bt < 107 ? 'tired' : 'calm') });
    if (bt >= 104 && bt < 107) f.pose = withHead(f.pose, 10);   // droopy while the task goes slowly
    if (bt >= 126.5) {
      // cross-fade to the summary position on the mattress (one of the two is always at least half visible)
      f.alpha = 1 - seg(bt, 127.0, 127.5);
      const g = summaryFig(hp, bt);
      g.alpha = seg(bt, 126.5, 127.0);
      hp.figs = [f, g];
    }
    hp.matA = 1;
    return;
  }
  if (bt >= 127.5) hp.fig = summaryFig(hp, bt);
}
function summaryFig(hp, bt) {
  const pose = SUM_POSE(bt);
  const lying = clamp(Math.abs(pose.rot || 0) / 90);
  const f = { x: hp.mx + lerp(-70, -15, lying), y: hp.my - MAT.h / 2 + 3, s: 0.8, dir: 1, style: 'A', pose, alpha: 1,
    face: faceAt(bt, bt >= 146 ? 'happy' : 'calm') };
  if (bt >= JUMP.t0) {
    const p = seg(bt, JUMP.t0, JUMP.t1);
    f.x = lerp(JUMP.x0, JUMP.x1, p);
    if (bt < JUMP.t1) f.y = lerp(hp.my - 19, WY + 40, p) - JUMP.peak * 4 * p * (1 - p);
    else {
      // under water: glides down, then swims slowly to the right, legs kicking (not on the beat)
      const g = EASE.out(seg(bt, JUMP.t1, 154.5));
      f.x = lerp(JUMP.x1, 600, EASE.inOut(seg(bt, 154.0, 155.5))) + 12 * Math.max(0, bt - 155.5);
      f.y = lerp(WY + 40, 925, g) + 6 * Math.sin((bt - 153.5) * 0.8) * seg(bt, 155.0, 156.0);
      const kick = 9 * Math.sin((bt - 153.5) * Math.PI * 0.9) * seg(bt, 155.0, 155.8);
      f.pose = { ...f.pose, thB: f.pose.thB + kick, thF: f.pose.thF - kick };
    }
    f.face = 'happy';
  }
  return f;
}

// ---------- wiring ----------
function drawBehind(bt, t) {
  if (bt >= 111.0 && bt < 127) drawCurtainLight(EASE.out(seg(bt, 111.0, 112.5)), { alpha: 1 - seg(bt, 126.0, 126.5) });
}
function drawSections(bt, t, pts, hp) {
  // the groggy "?" of the opening
  if (bt < 17) drawDizzy(pts.head[0], pts.head[1] - 62, bt, popA(bt, 4.5, 0.4) * (1 - seg(bt, 8.5, 9.0)));
  if (bt >= 31) drawHeaders(bt);
  drawStep1(bt, t, pts, hp);
  drawStep2(bt, t, pts, hp);
  drawStep3(bt, t, pts, hp);
  drawSummary(bt, t, pts, hp);
}
