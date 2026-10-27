// sections.js — 怎么背 ①②③ (32–128 beats) and 照着做 (128–160 beats)
const PANEL = { x: 140, y: 455, w: 1640, h: 520 };
const RC = { icon: 1062, text: 1112, ys: [548, 678, 808] };

// ---------- extra props ----------
// step ② dial: hours between finishing the words and falling asleep. Full turn = 16 h; marks at "a few hours" (the
// evening learners, Gais 2006 exp. 1), 10 h (learned 8 pm, stayed up until 6 am, exp. 2) and 14 h (learned in the
// morning, slept at night, exp. 1). No number on the first mark: the paper only says "within a few hours".
const GAP_MARKS = [[3, COL.yellow, 70, '几小时'], [10, COL.pink, 78, '熬通宵'], [14, COL.grayHi, 86, '14 小时']];
function drawGapRing(x, y, r, hours, o = {}) {
  const { alpha = 1, concl = 0, bt = 0 } = o;
  withAlpha(alpha, () => {
    circle(x, y, r + 26, 'rgba(10,22,50,0.7)');
    ctx.save(); ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.strokeStyle = 'rgba(255,255,255,0.1)'; ctx.lineWidth = 18; ctx.stroke();
    const a = (h) => -Math.PI / 2 + (h / 16) * TAU;
    const segs = [[0, 3, COL.yellow, concl], [3, 10, COL.pink, 0], [10, 14, '#8d99b5', 0]];
    for (const [h0, h1, c, g] of segs) {
      if (hours <= h0) continue;
      ctx.beginPath(); ctx.arc(x, y, r, a(h0), a(Math.min(hours, h1)));
      ctx.strokeStyle = c; ctx.lineWidth = 18 + g * 6;
      ctx.shadowColor = c; ctx.shadowBlur = 10 + g * 26; ctx.stroke();
    }
    ctx.restore();
    for (let i = 0; i < 8; i++) {
      const an = (i / 8) * TAU;
      line(x + Math.cos(an) * (r - 22), y + Math.sin(an) * (r - 22), x + Math.cos(an) * (r - 30), y + Math.sin(an) * (r - 30), 'rgba(243,238,227,0.35)', 2);
    }
    for (const [h, c, at, label] of GAP_MARKS) {
      const an = a(h), lit = bt >= at;
      const mx = x + Math.cos(an) * r, my = y + Math.sin(an) * r;
      const sc = lit ? 1 + 0.5 * (1 - EASE.out(seg(bt, at, at + 0.8))) : 1;
      ctx.save();
      if (lit) { ctx.shadowColor = c; ctx.shadowBlur = 22; }
      circle(mx, my, 13 * sc, lit ? c : '#1a2a52', lit ? '#ffffff' : 'rgba(243,238,227,0.5)', 3);
      ctx.restore();
      const lx = x + Math.cos(an) * (r + 54), ly = y + Math.sin(an) * (r + 46);
      txt(label, lx, ly, { size: 26, weight: 900, color: lit ? c : COL.gray, align: 'center' });
    }
    // centre: what the dial measures
    iconMoonX(x, y - 30, 64, COL.cream);
    txt('背完到睡着', x, y + 30, { size: 26, weight: 700, color: COL.grayHi, align: 'center' });
  });
}

function drawCalendar(x, y, day, flipP, o = {}) {
  const { alpha = 1, stamp = 0 } = o;
  withAlpha(alpha, () => {
    const w = 150, h = 158;
    rrect(x - w / 2, y - h / 2, w, h, 12, '#f4efe6');
    rrect(x - w / 2, y - h / 2, w, 44, [12, 12, 0, 0], '#e2556a');
    for (const dx of [-38, 38]) rrect(x + dx - 5, y - h / 2 - 12, 10, 26, 5, '#c9ced8');
    const d = Math.min(7, day);
    txt(`第 ${d} 天`, x, y - h / 2 + 22, { size: 24, weight: 900, color: '#ffffff', align: 'center' });
    txt(String(d), x, y + 30, { size: 74, weight: 800, fam: 'mono', color: '#2a3350', align: 'center', alpha: 1 - clamp(stamp * 2) * 0.6 });
    if (flipP > 0 && flipP < 1) {
      ctx.save(); ctx.translate(x, y - h / 2 + 44);
      const k = Math.cos(Math.PI * flipP);
      ctx.scale(1, k);
      rrect(-w / 2, 0, w, h - 44, 8, k > 0 ? '#ebe5d9' : '#d9d2c4');
      ctx.restore();
    }
    if (stamp > 0) {
      const s = 1 + (1 - EASE.out(clamp(stamp * 1.4))) * 0.8;
      withAlpha(clamp(stamp * 2), () => withScale(x + 4, y + 26, s, () => {
        ctx.save(); ctx.translate(x + 4, y + 26); ctx.rotate(-0.18);
        rrect(-70, -28, 140, 56, 10, 'rgba(247,185,62,0.15)', COL.yellow, 4);
        txt('一周后', 0, 1, { size: 34, weight: 900, color: COL.yellow, align: 'center' });
        ctx.restore();
      }));
    }
  });
}

// alarm clock (screen space), shakes while ringing
function drawAlarm(x, y, r, ring, bt) {
  const shake = ring > 0 ? Math.sin(bt * BEAT * TAU * 18) * 0.16 * ring : 0;
  ctx.save(); ctx.translate(x, y); ctx.rotate(shake);
  line(-r * 0.6, r * 0.8, -r * 0.85, r * 1.1, '#c9ced8', 6); line(r * 0.6, r * 0.8, r * 0.85, r * 1.1, '#c9ced8', 6);
  for (const s of [-1, 1]) {
    ctx.beginPath(); ctx.arc(s * r * 0.62, -r * 0.82, r * 0.36, Math.PI, 0); ctx.closePath(); ctx.fillStyle = '#e2556a'; ctx.fill();
  }
  circle(0, 0, r, '#e2556a'); circle(0, 0, r * 0.78, '#f7f3ea');
  line(0, 0, 0, -r * 0.55, '#2a3350', 4); line(0, 0, r * 0.38, r * 0.12, '#2a3350', 4);
  circle(0, 0, 3.5, '#2a3350');
  ctx.restore();
  if (ring > 0) {
    ctx.save(); ctx.strokeStyle = rgba(COL.yellow, 0.9 * ring); ctx.lineWidth = 4; ctx.lineCap = 'round';
    const ph = (bt * 3) % 1;
    for (const s of [-1, 1]) for (let k = 0; k < 2; k++) {
      const rr = r * (1.35 + k * 0.38 + ph * 0.2);
      ctx.beginPath(); ctx.arc(x, y, rr, s < 0 ? Math.PI * 1.05 : -Math.PI * 0.35, s < 0 ? Math.PI * 1.35 : -Math.PI * 0.05); ctx.stroke();
    }
    ctx.restore();
  }
}
// bedside table for the alarm (step ③), right of the bed
const STAND = { x: 760, top: 846 };
const RING = { x: 860, y: 690 };  // step ② dial centre (clear of the bed on its left, the chips on its right)
function drawNightstand(a) {
  withAlpha(a, () => {
    rrect(STAND.x - 48, STAND.top, 96, 104, 8, '#6c472f');
    rrect(STAND.x - 54, STAND.top - 8, 108, 14, 5, '#a9774f');
    line(STAND.x - 30, STAND.top + 52, STAND.x + 30, STAND.top + 52, 'rgba(40,24,14,0.6)', 3);
    circle(STAND.x, STAND.top + 34, 4, '#d9b48a');
  });
}

function drawClosedBookLocal(x, y, color) {
  rrect(x - 62, y - 15, 124, 17, 4, color);
  rrect(x - 56, y - 11, 112, 7, 2, '#f4efe6');
}
function drawNotebookLocal(x, y) {
  ctx.save(); ctx.translate(x, y);
  ctx.beginPath(); ctx.moveTo(-70, 0); ctx.lineTo(70, 0); ctx.lineTo(58, -14); ctx.lineTo(-58, -14); ctx.closePath();
  ctx.fillStyle = '#f7f4ec'; ctx.fill();
  ctx.strokeStyle = 'rgba(239,140,60,0.8)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(-50, -9); ctx.lineTo(30, -9); ctx.moveTo(-46, -4); ctx.lineTo(10, -4); ctx.stroke();
  ctx.restore();
}

// progress chip (step ①: 默对 n/16, step ③: rounds)
function progChip(x, y, w, label, right, p, done, o = {}) {
  const { alpha = 1 } = o;
  withAlpha(alpha, () => {
    rrect(x, y, w, 74, 14, 'rgba(12,26,58,0.88)', done ? COL.yellow : 'rgba(63,203,232,0.55)', 2.5);
    txt(label, x + 20, y + 24, { size: 26, weight: 900, color: COL.cream });
    txt(right, x + w - 20, y + 24, { size: 22, weight: 700, fam: 'mono', color: done ? COL.yellow : COL.cyan, align: 'right' });
    rrect(x + 20, y + 46, w - 40, 12, 6, 'rgba(255,255,255,0.1)');
    if (p > 0) {
      ctx.save(); ctx.shadowColor = done ? COL.yellow : COL.cyan; ctx.shadowBlur = 10;
      rrect(x + 20, y + 46, Math.max(12, (w - 40) * p), 12, 6, done ? COL.yellow : COL.cyan); ctx.restore();
    }
  });
}

// right-column line: icon circle + rich text (+ optional small note)
function rcLine(i, icon, spans, at, bt, o = {}) {
  const { note = null, noteAt = null, out = 1e9, color = COL.cyan } = o;
  if (bt < at) return;
  const a = popA(bt, at, 0.35) * (1 - seg(bt, out, out + 0.6));
  if (a <= 0) return;
  const y = RC.ys[i], dx = (1 - EASE.out(seg(bt, at, at + 0.6))) * 40;
  withAlpha(a, () => {
    const s = popS(bt, at, 0.6);
    withScale(RC.icon, y, s, () => {
      circle(RC.icon, y, 31, 'rgba(12,26,58,0.9)', color, 3);
      ICONS[icon](RC.icon, y, 34, color, 3, 0);
    });
    rich(spans, RC.text + dx, y - 1, { size: 46, weight: 900 });
    if (note) txt(note, RC.text + dx, y + 44, { size: 24, weight: 500, color: 'rgba(200,212,236,0.72)', alpha: popA(bt, noteAt ?? at + 0.6, 0.5) });
  });
}

// step ② lines: a chip that lights when the dial reaches its mark
function gapLine(i, label, color, spans, note, litAt, bt, out) {
  const appear = popA(bt, 65 + i * 0.4, 0.5) * (1 - seg(bt, out, out + 0.6));
  if (appear <= 0) return;
  const lit = bt >= litAt, y = RC.ys[i];
  withAlpha(appear, () => {
    const cw = measure(label, 30, 900) + 36;
    const sc = lit ? 1 + 0.25 * (1 - EASE.out(seg(bt, litAt, litAt + 0.7))) : 1;
    withScale(RC.icon - 30 + cw / 2, y, sc, () => {
      ctx.save(); if (lit) { ctx.shadowColor = color; ctx.shadowBlur = 18; }
      rrect(RC.icon - 30, y - 26, cw, 52, 26, lit ? color : 'rgba(255,255,255,0.05)', lit ? null : 'rgba(200,212,236,0.35)', 2);
      ctx.restore();
      txt(label, RC.icon - 30 + cw / 2, y + 1, { size: 30, weight: 900, color: lit ? '#0b1736' : COL.gray, align: 'center' });
    });
    const tx = RC.icon - 30 + cw + 24;
    if (lit) {
      const p = popA(bt, litAt, 0.4), dx = (1 - EASE.out(seg(bt, litAt, litAt + 0.6))) * 30;
      rich(spans, tx + dx, y - 1, { size: 44, weight: 900, alpha: p });
      if (note) txt(note, tx + dx, y + 42, { size: 24, weight: 500, color: 'rgba(200,212,236,0.72)', alpha: popA(bt, litAt + 0.8, 0.5) });
    } else {
      txt('· · ·', tx, y, { size: 40, weight: 900, color: COL.grayDim });
    }
  });
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
// small moon / sun badge on the wall clock: evening in step ①
function clockBadge(x, y, kind, a) {
  withAlpha(a, () => {
    circle(x, y, 26, 'rgba(10,22,50,0.95)', 'rgba(243,238,227,0.4)', 2);
    if (kind === 'moon') iconMoonX(x - 2, y, 46, COL.yellowHi);
    else iconSun(x, y, 40, COL.yellowHi);
  });
}

// ---------- headers ----------
const HEADERS = [
  { from: 32, to: 64, num: '01', title: [{ s: '睡前背什么：难背的生词' }], sub: 'WHAT: the hard new words, until all are right' },
  { from: 64, to: 96, num: '02', title: [{ s: '背完多久睡：几小时内' }], sub: 'WHEN: fall asleep within a few hours' },
  { from: 96, to: 126.8, num: '03', title: [{ s: '醒来干嘛：默到全对' }], sub: 'THEN: test yourself until all are right' },
  { from: 126.9, to: 161, num: null, title: [{ s: '照着做' }], sub: 'DO THIS: screenshot it, then follow it' },
];
function drawHeaders(bt) {
  HEADERS.forEach((h, i) => {
    const inP = EASE.out(seg(bt, h.from - 0.2, h.from + 0.7));
    const outP = EASE.in(seg(bt, h.to - 0.6, h.to));
    const a = inP * (1 - outP);
    if (a <= 0) return;
    const dy = (1 - inP) * 26 - outP * 26;
    sectionHeader(h.num, h.title, h.sub, { alpha: a, dy, p: i === 0 ? seg(bt, 32, 33.2) : 1, bt, typeP: seg(bt, h.from + 0.2, h.from + 2.6) });
  });
}

// ---------- layer behind the boy ----------
function drawPanelLayer(bt, t) {
  if (bt < 31 || bt > 161) return;
  const panelA = 1 - seg(bt, 126, 127.2);
  hudPanel(PANEL.x, PANEL.y, PANEL.w, PANEL.h, seg(bt, 31.6, 32.8), panelA);
  if (panelA > 0) withAlpha(panelA, () => line(PANEL.x + 30, 938, PANEL.x + 900, 938, 'rgba(63,203,232,0.18)', 2));

  // step ① wall clock (9 pm, 5 minutes per beat) -> step ② dial
  const morph = EASE.inOut(seg(bt, 62.5, 64.5));
  if (bt < 64.5) {
    let hours = 21;
    if (bt >= 36) {
      const k = bt - 36, n = Math.floor(k);
      const snap = EASE.back(clamp((k - n) / 0.24));
      hours = bt >= 48 ? 22 : 21 + (5 * n + 5 * snap) / 60;
    }
    const cx = lerp(250, RING.x, morph), cy = lerp(592, RING.y, morph), cr = lerp(64, 120, morph);
    const ca = popA(bt, 31.8, 0.8) * (1 - seg(bt, 63, 64));
    drawWallClock(cx, cy, cr, hours, { alpha: ca, glow: win(bt, 48, 51, 0.1, 1.5), scale: 0.6 + 0.4 * EASE.back(seg(bt, 31.8, 32.8)) });
    clockBadge(cx + cr * 0.86, cy - cr * 0.86, 'moon', ca * (1 - morph));
  }
  if (bt >= 63 && bt < 97.5) {
    const hours = KB([[64, 0], [67, 0], [70, 3, 'out'], [75, 3], [78, 10, 'out'], [83, 10], [86, 14, 'out']])(bt);
    const m2 = EASE.inOut(seg(bt, 95, 97));
    let rx = lerp(250, RING.x, morph), ry = lerp(592, RING.y, morph), rs = lerp(64, 120, morph) / 120;
    if (m2 > 0) { rx = lerp(RING.x, STAND.x, m2); ry = lerp(RING.y, STAND.top - 40, m2); rs = lerp(1, 0.22, m2); }
    const a = seg(bt, 63.2, 64.4) * (1 - seg(bt, 96.2, 97));
    ctx.save(); ctx.translate(rx, ry); ctx.scale(rs, rs); ctx.translate(-rx, -ry);
    drawGapRing(rx, ry, 120, hours, { alpha: a, concl: seg(bt, 88, 89), bt });
    ctx.restore();
    for (const [h, c, at] of GAP_MARKS) {
      const an = -Math.PI / 2 + (h / 16) * TAU;
      sparkleBurst(RING.x + Math.cos(an) * 120, RING.y + Math.sin(an) * 120, seg(bt, at, at + 1.6), c);
    }
  }

  // step ① progress: 默对 n/16 -> 16 个全对 (beat 48)
  if (bt > 34 && bt < 64) {
    const a = popA(bt, 35, 0.5) * (1 - seg(bt, 62, 63));
    const p = seg(bt, 35.5, 48), n = Math.round(16 * p), done = p >= 1;
    progChip(600, 520, 300, '16 个生词', done ? '全对' : `默对 ${n}/16`, p, done, { alpha: a });
    dingBurst(948, 500, seg(bt, 48, 50.5), { size: 46 });
  }

  // step ③ bedside table + alarm (arrives from the dial), rings at beat 98, stops when he wakes
  if (bt > 94 && bt < 127) {
    const sa = popA(bt, 94.5, 1) * (1 - seg(bt, 125.8, 126.6));
    drawNightstand(sa);
    if (bt >= 96.6) withAlpha(sa, () => drawAlarm(STAND.x, STAND.top - 40, 27, bt >= 98 && bt < 100.8 ? 1 : 0, bt));
    dingBurst(STAND.x + 42, STAND.top - 112, seg(bt, 98, 100.4), { s: '叮铃', size: 34 });
  }
  // step ③ rounds: 第 1 轮 10/16 -> 第 3 轮 全对 (the sleep group's means: 10.3 on the first round, 3.05 rounds)
  if (bt > 102.5 && bt < 113) {
    const a = popA(bt, 103, 0.5) * (1 - seg(bt, 111, 112));
    const p = KB([[103, 10 / 16], [105, 10 / 16], [105.6, 13.5 / 16, 'out'], [107, 13.5 / 16], [107.6, 1, 'out']])(bt);
    const done = bt >= 107.6;
    const right = bt < 105 ? '第 1 轮 10/16' : bt < 107 ? '第 2 轮' : '第 3 轮 全对';
    progChip(600, 520, 320, '早上默写', right, p, done, { alpha: a });
    dingBurst(948, 500, seg(bt, 107.6, 110), { size: 46 });
  }

  // step ③ calendar + meter: 一周后 15.2 / 16, the 「只过一遍」 control group 11.25 / 16 (= the wake group)
  if (bt > 105 && bt < 128) {
    const a = popA(bt, 106, 0.5) * (1 - seg(bt, 126, 127));
    const k = bt - 108;
    const flipP = bt >= 108 && bt < 115 ? clamp((k - Math.floor(k)) / 0.6) : 0;
    const shownDay = bt < 108 ? 1 : flipP < 0.5 ? Math.min(7, 1 + Math.floor(k)) : Math.min(7, 2 + Math.floor(k));
    drawCalendar(250, 600, bt >= 115 ? 8 : shownDay, flipP, { alpha: a, stamp: seg(bt, 115, 116) });
    const lvl = KB([[116, 0], [117, 15.2 / 16, 'back']])(bt);
    const ma = popA(bt, 115.8, 0.4) * (1 - seg(bt, 126, 127));
    const bottom = 650, hMax = 150, restY = bottom - (11.25 / 16) * hMax;
    drawMeter(470, bottom, 64, hMax, Math.min(1, lvl), {
      color: COL.yellow, colorHi: COL.yellowHi, alpha: ma,
      num: { s: '15', alpha: popA(bt, 117, 0.4), side: -1, size: 34, color: COL.yellowHi },
    });
    withAlpha(ma, () => {
      const p = seg(bt, 116.2, 117);
      if (p > 0) {
        ctx.save(); ctx.setLineDash([10, 8]); ctx.strokeStyle = 'rgba(181,191,214,0.85)'; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(400, restY); ctx.lineTo(400 + 140 * EASE.out(p), restY); ctx.stroke(); ctx.restore();
        txt('只过一遍', 552, restY, { size: 26, weight: 700, color: COL.grayHi, alpha: p });
      }
      const top = bottom - Math.min(1, lvl) * hMax;
      const cs = popS(bt, 117.5, 0.6);
      if (cs > 0) withScale(470, top, cs, () => {
        ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 20; circle(470, top, 23, COL.yellow); ctx.restore();
        checkBadge(470, top, 23, { color: '#0d1838', p: seg(bt, 117.5, 118.2), lw: 4 });
      });
      const la = popA(bt, 117.7, 0.4);
      if (la > 0) txt('还领先', 516, top - 2, { size: 34, weight: 900, color: COL.yellow, alpha: la, glow: 14 });
    });
  }
}

// ---------- boy decoration: desk props, extra motion ----------
function decorateBoy(bp, bt, t) {
  // page flips while reading: every 2 beats in the hook (between hers), every 4 beats later
  if (bp.read > 0.9) {
    if (bt < 8) { const cyc = ((bt - 1.5) % 2 + 2) % 2; bp.flip = cyc < 0.9 ? cyc / 0.9 : 0; }
    else { const cyc = ((bt - 24.5) % 4 + 4) % 4; bp.flip = cyc < 0.9 ? cyc / 0.9 : 0; }
  }
  // head shake "no" for 「早上只过一遍不够」
  if (bt > 142 && bt < 144.5) bp.headTilt = Math.sin((bt - 142) * Math.PI * 2.2) * 0.12 * (1 - seg(bt, 143.6, 144.5));
  bp.worry = win(bt, 142, 144.6, 0.3, 0.6) * 0.6;
  const bookOnDesk = (bt > 50 && bt < 129.5) || bt > 134;
  const notebook = (bt > 101.5 && bt < 126.6) || bt > 138.4;
  bp.deskProps = () => {
    if (bookOnDesk && bp.read < 0.5) drawClosedBookLocal(-120, -3, bp.bookColor);
    if (notebook) withAlpha(bt > 126 && bt < 138.4 ? 0 : 1, () => drawNotebookLocal(20, -3));
  };
}

// ---------- S5 table ----------
const TABLE = { x: 760, y: 250, w: 1010, h: 732 };
function drawTable(bt) {
  const inP = EASE.out(seg(bt, 126.3, 128));
  if (inP <= 0) return;
  const dx = (1 - inP) * 220;
  withAlpha(inP, () => {
    ctx.save(); ctx.translate(dx, 0);
    const { x, y, w, h } = TABLE;
    ctx.save(); ctx.shadowColor = 'rgba(63,203,232,0.35)'; ctx.shadowBlur = 30;
    rrect(x, y, w, h, 18, 'rgba(11,24,54,0.96)', 'rgba(63,203,232,0.6)', 2.5);
    ctx.restore();
    hudPanel(x - 6, y - 6, w + 12, h + 12, 1, 1);
    txt('背单词时间表', x + 48, y + 62, { size: 54, weight: 900, color: COL.cream });
    txt('WORD PLAN', x + w - 44, y + 66, { size: 24, weight: 600, fam: 'mono', color: COL.cyan, align: 'right' });
    line(x + 40, y + 112, x + w - 40, y + 112, 'rgba(63,203,232,0.35)', 2);

    const rows = [
      { at: 130, icon: 'moon', main: [{ s: '睡前背' }, { s: '难背的生词', color: COL.yellow }], sub: [{ s: '遮住答案默，错的再来，背到全对' }] },
      { at: 134, icon: 'zz', main: [{ s: '背完 ' }, { s: '几小时内', color: COL.yellow }, { s: ' 睡着' }], sub: [{ s: '别熬通宵：' }, { s: '补觉补不回来', color: COL.pink }] },
      { at: 138, icon: 'alarm', main: [{ s: '早上' }, { s: '默到全对', color: COL.yellow }], sub: [{ s: '先默一遍，错的再背（实验里约 3 轮）' }] },
    ];
    rows.forEach((r, i) => {
      const ry = y + 176 + i * 128;
      const a = popA(bt, r.at, 0.35);
      if (a <= 0) return;
      const ox = (1 - EASE.out(seg(bt, r.at, r.at + 0.6))) * 40;
      withAlpha(a, () => {
        withScale(x + 76, ry, popS(bt, r.at, 0.6), () => {
          circle(x + 76, ry, 30, COL.cyan);
          txt(String(i + 1), x + 76, ry + 1, { size: 32, weight: 800, fam: 'mono', color: '#0b1736', align: 'center' });
        });
        ICONS[r.icon](x + 158 + ox, ry, 46, COL.cyanHi, 3, 0);
        rich(r.main, x + 212 + ox, ry - 16, { size: 50, weight: 900 });
        rich(r.sub, x + 214 + ox, ry + 30, { size: 26, weight: 700, alpha: 0.85, fam: 'cjk' });
        if (i < 2) {
          const ay = ry + 64;
          ctx.save(); ctx.strokeStyle = 'rgba(63,203,232,0.7)'; ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
          ctx.beginPath(); ctx.moveTo(x + 66, ay - 6); ctx.lineTo(x + 76, ay + 4); ctx.lineTo(x + 86, ay - 6); ctx.stroke(); ctx.restore();
        }
      });
    });
    // warning row: the control group (slept, but only one pass in the morning) was no better than the wake group a week later
    const wa = popA(bt, 142, 0.35);
    if (wa > 0) withAlpha(wa, () => {
      const wy = y + 560, s = popS(bt, 142, 0.6);
      withScale(x + w / 2, wy + 42, 0.9 + 0.1 * s, () => {
        rrect(x + 36, wy, w - 72, 86, 14, 'rgba(255,111,158,0.12)', 'rgba(255,111,158,0.7)', 2.5);
        iconPaper(x + 86, wy + 43, 46, COL.pink);
        line(x + 64, wy + 66, x + 108, wy + 20, COL.pink, 4);
        txt('早上只过一遍不够', x + 136, wy + 43, { size: 46, weight: 900, color: COL.cream });
        txt('一周后优势就没了', x + w - 64, wy + 45, { size: 26, weight: 700, color: COL.pink, align: 'right' });
      });
    });
    // "screenshot" flash when the table is complete
    const fl = win(bt, 146, 147.4, 0.04, 1.2);
    if (fl > 0) {
      rrect(x, y, w, h, 18, `rgba(255,255,255,${0.1 * fl})`, `rgba(255,250,235,${0.9 * fl})`, 5);
    }
    const fa = popA(bt, 144, 0.6);
    if (fa > 0) {
      txt('仅供参考 · 换成背知识点（不是单词），一周后差距不显著', x + 44, y + h - 60, { size: 24, weight: 700, color: COL.gray, alpha: fa });
      txt('Mazza 2016 · Gais 2006 · Cousins 2021', x + 44, y + h - 26, { size: 20, weight: 500, fam: 'mono', color: COL.grayDim, alpha: fa });
    }
    ctx.restore();
  });
}

// ---------- foreground for sections ----------
function drawSections(bt, t, boy) {
  if (bt < 31) return;
  drawHeaders(bt);

  // ① 睡前背什么
  if (bt < 64) {
    const bulletA = 1 - seg(bt, 63, 63.8);
    if (bt >= 34) bulletLine([{ s: '睡前背' }, { s: '难背的生词', color: COL.cyan, glow: 12 }, { s: '，背到全对' }], 'Before bed: the hard new words, until every one is right.',
      { alpha: bulletA, p: seg(bt, 34, 35.2), typeP: seg(bt, 34.6, 37.5), bt });
    rcLine(0, 'book', [{ s: '挑出难背的生词' }], 36, bt, { out: 62.6, note: '实验里：16 个从没见过的斯瓦希里语单词' });
    // the paper's own example pair: nyanya - tomate (tomato)
    const ex = bt >= 44;
    rcLine(1, 'paper', [{ s: '遮住答案默：' }, { s: 'nyanya → ', color: COL.cyanHi, fam: 'mono', weight: 800 },
      ex ? { s: '番茄', color: COL.yellow, glow: 14 } : { s: '？', color: COL.grayDim }], 42, bt,
    { out: 62.6, note: '实验里的原词（斯瓦希里语）· 错的再来，直到 16 个全对', noteAt: 44.6 });
    if (ex) sparkleBurst(1112 + 520, 678, seg(bt, 44, 45.4), COL.yellow);
    rcLine(2, 'moon', [{ s: '全对就合上书，去睡' }], 52, bt, { out: 62.6 });
    const na = popA(bt, 54, 0.6) * (1 - seg(bt, 62.6, 63.2));
    if (na > 0) {
      txt('实验里：晚上 9 点背到全对，然后回家睡觉', RC.icon - 30, 908, { size: 28, weight: 700, color: COL.grayHi, alpha: na });
      sourceNote('Mazza 等 2016 · 《Psychological Science》', RC.icon - 30, 948, { alpha: na });
    }
  }
  // ② 背完多久睡
  if (bt >= 64 && bt < 97) {
    const filled = bt >= 88;
    const fp = seg(bt, 88, 88.6);
    const blankA = 0.55 + 0.45 * Math.sin(bt * Math.PI);
    const spans = [
      { s: '背完 ' },
      filled ? { s: '几小时内', color: COL.yellow, glow: 14 } : { s: '？', color: COL.grayDim, alpha: blankA },
      { s: ' 就睡，别' },
      filled ? { s: '熬通宵', color: COL.pink, glow: 14 } : { s: '？', color: COL.grayDim, alpha: blankA },
    ];
    bulletLine(spans, filled ? 'Sleep within a few hours · no all-nighters' : '', {
      alpha: popA(bt, 65.5, 0.6) * (1 - seg(bt, 95.4, 96)), p: filled ? seg(bt, 88, 89) : 0, typeP: seg(bt, 88.4, 91), bt, textA: 1,
    });
    if (fp > 0 && fp < 1) sparkleBurst(560, 326, fp, COL.yellow);
    const out = 95.2;
    gapLine(0, '几小时内', COL.yellow, [{ s: '睡着：' }, { s: '忘得少', color: COL.yellow }], '晚上 8 点背，当晚睡', 70, bt, out);
    gapLine(1, '熬通宵', COL.pink, [{ s: '再补觉：' }, { s: '补不回来', color: COL.pink }], '背完熬一夜，白天补觉，两天后还是记得少', 78, bt, out);
    gapLine(2, '14 小时', COL.grayHi, [{ s: '早上背、晚上才睡：忘得多' }], '关键不是几点背，是背完多久睡', 86, bt, out);
    const na = popA(bt, 71, 0.6) * (1 - seg(bt, out, out + 0.6));
    if (na > 0) sourceNote('Gais 等 2006 · 《Learning & Memory》 · 美国高中生背德语单词', RC.icon - 30, 948, { alpha: na });
  }
  // ③ 醒来干嘛
  if (bt >= 96 && bt < 128) {
    const out = 126;
    if (bt >= 102) bulletLine([{ s: '醒来先' }, { s: '默一遍', color: COL.cyan, glow: 12 }, { s: '，错的背到全对' }], 'Wake up: test yourself, redo the misses until all are right.',
      { alpha: 1 - seg(bt, out, out + 0.8), p: seg(bt, 102, 103.2), typeP: seg(bt, 102.6, 105), bt });
    rcLine(0, 'alarm', [{ s: '闹钟响，先默一遍' }], 100.6, bt, { out });
    rcLine(1, 'book', [{ s: '错的再背，直到全对' }], 103, bt, { out, note: '实验里平均 3 轮；早上背的也能全对，但要 6 轮' });
    rcLine(2, 'calendar', [{ s: '一周后：' }, { s: '还记得 15 个', color: COL.yellow, glow: 14 }], 117.7, bt, { out, color: COL.yellow });
    const na = popA(bt, 119, 0.6) * (1 - seg(bt, out, out + 0.6));
    if (na > 0) {
      txt('只过一遍的对照组、早上背的组：都只有 11 个', RC.icon - 30, 908, { size: 28, weight: 700, color: COL.grayHi, alpha: na });
      sourceNote('半年后：8.7 个 vs 早上背的 3.4 个 · Mazza 等 2016', RC.icon - 30, 948, { alpha: na });
    }
  }
  // 照着做
  if (bt >= 126.2) drawTable(bt);
}
