// sections.js — 怎么睡 ①②③ (32–128 beats) and 照着做 (128–160 beats)
const PANEL = { x: 140, y: 455, w: 1640, h: 520 };
const RC = { icon: 1062, text: 1112, ys: [548, 678, 808] };

// ---------- extra props ----------
function drawRing(x, y, r, minutes, o = {}) {
  const { alpha = 1, concl = 0, bt = 0 } = o;
  withAlpha(alpha, () => {
    circle(x, y, r + 26, 'rgba(10,22,50,0.7)');
    ctx.save(); ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.strokeStyle = 'rgba(255,255,255,0.1)'; ctx.lineWidth = 18; ctx.stroke();
    const a = (m) => -Math.PI / 2 + (m / 60) * TAU;
    const segs = [[0, 10, COL.cyan, concl], [10, 30, '#7ccfe6', 0], [30, 60, COL.yellow, concl]];
    for (const [m0, m1, c, g] of segs) {
      if (minutes <= m0) continue;
      ctx.beginPath(); ctx.arc(x, y, r, a(m0), a(Math.min(minutes, m1)));
      ctx.strokeStyle = c; ctx.lineWidth = 18 + g * 6;
      ctx.shadowColor = c; ctx.shadowBlur = 10 + g * 26; ctx.stroke();
    }
    ctx.restore();
    // ticks
    for (let i = 0; i < 12; i++) {
      const an = (i / 12) * TAU;
      line(x + Math.cos(an) * (r - 22), y + Math.sin(an) * (r - 22), x + Math.cos(an) * (r - 30), y + Math.sin(an) * (r - 30), 'rgba(243,238,227,0.35)', 2);
    }
    // marks
    const marks = [[10, COL.cyan, 70], [30, '#7ccfe6', 78], [60, COL.yellow, 86]];
    for (const [m, c, at] of marks) {
      const an = a(m), lit = bt >= at;
      const mx = x + Math.cos(an) * r, my = y + Math.sin(an) * r;
      const sc = lit ? 1 + 0.5 * (1 - EASE.out(seg(bt, at, at + 0.8))) : 1;
      ctx.save();
      if (lit) { ctx.shadowColor = c; ctx.shadowBlur = 22; }
      circle(mx, my, 13 * sc, lit ? c : '#1a2a52', lit ? '#ffffff' : 'rgba(243,238,227,0.5)', 3);
      ctx.restore();
      const lx = x + Math.cos(an) * (r + 46), ly = y + Math.sin(an) * (r + 46);
      txt(`${m} 分`, lx, ly, { size: 26, weight: 900, color: lit ? c : COL.gray, align: 'center' });
    }
    // centre readout
    txt(String(Math.round(minutes)), x, y - 8, { size: 78, weight: 800, fam: 'mono', color: COL.cream, align: 'center' });
    txt('分钟', x, y + 46, { size: 26, weight: 700, color: COL.gray, align: 'center' });
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
      // page flying up
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

// alarm clock in kid-local coords (drawn inside drawKid deskProps)
function drawAlarmLocal(x, y, r, ring, bt) {
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

// progress chip "第 1 段"
function segChip(x, y, label, p, o = {}) {
  const { alpha = 1 } = o;
  withAlpha(alpha, () => {
    const done = p >= 1;
    rrect(x, y, 250, 74, 14, 'rgba(12,26,58,0.88)', done ? COL.yellow : 'rgba(63,203,232,0.55)', 2.5);
    txt(label, x + 20, y + 24, { size: 26, weight: 900, color: COL.cream });
    txt(done ? '学完 ✓' : `${Math.round(p * 100)}%`, x + 230, y + 24, { size: 22, weight: 700, fam: 'mono', color: done ? COL.yellow : COL.cyan, align: 'right' });
    rrect(x + 20, y + 46, 210, 12, 6, 'rgba(255,255,255,0.1)');
    if (p > 0) {
      ctx.save(); ctx.shadowColor = done ? COL.yellow : COL.cyan; ctx.shadowBlur = 10;
      rrect(x + 20, y + 46, Math.max(12, 210 * p), 12, 6, done ? COL.yellow : COL.cyan); ctx.restore();
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

// S3 time-chip lines (placeholder until lit)
function ringLine(i, mins, color, spans, note, litAt, bt, out) {
  const appear = popA(bt, 65 + i * 0.4, 0.5) * (1 - seg(bt, out, out + 0.6));
  if (appear <= 0) return;
  const lit = bt >= litAt, y = RC.ys[i];
  withAlpha(appear, () => {
    const cw = measure(`${mins} 分钟`, 30, 900) + 36;
    const sc = lit ? 1 + 0.25 * (1 - EASE.out(seg(bt, litAt, litAt + 0.7))) : 1;
    withScale(RC.icon - 30 + cw / 2, y, sc, () => {
      ctx.save(); if (lit) { ctx.shadowColor = color; ctx.shadowBlur = 18; }
      rrect(RC.icon - 30, y - 26, cw, 52, 26, lit ? color : 'rgba(255,255,255,0.05)', lit ? null : 'rgba(200,212,236,0.35)', 2);
      ctx.restore();
      txt(`${mins} 分钟`, RC.icon - 30 + cw / 2, y + 1, { size: 30, weight: 900, color: lit ? '#0b1736' : COL.gray, align: 'center' });
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

// ---------- headers ----------
const HEADERS = [
  { from: 32, to: 64, num: '01', title: [{ s: '什么时候：学完一段再睡' }], sub: 'WHEN: after you finish a block' },
  { from: 64, to: 96, num: '02', title: [{ s: '睡多久：看你要什么' }], sub: 'HOW LONG: depends on your goal' },
  { from: 96, to: 126.8, num: '03', title: [{ s: '醒来干嘛：接着学下一段' }], sub: 'THEN: wake up, learn the next block' },
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

  // S2 wall clock -> S3 ring
  const morph = EASE.inOut(seg(bt, 62.5, 64.5));
  if (bt < 64.5) {
    let hours = 14;
    if (bt >= 36) {
      const k = bt - 36, n = Math.floor(k);
      const snap = EASE.back(clamp((k - n) / 0.24));
      hours = bt >= 48 ? 15 : 14 + (5 * n + 5 * snap) / 60;
    }
    const pulse = bt >= 48 ? 1 + 0.14 * (1 - EASE.out(seg(bt, 48, 48.9))) : 1;
    const cx = lerp(250, 840, morph), cy = lerp(592, 690, morph), cr = lerp(64, 120, morph);
    drawWallClock(cx, cy, cr, hours, { alpha: popA(bt, 31.8, 0.8) * (1 - seg(bt, 63, 64)), glow: win(bt, 48, 51, 0.1, 1.5), scale: pulse * (0.6 + 0.4 * EASE.back(seg(bt, 31.8, 32.8))) });
    dingBurst(250 + 96, 592 - 72, seg(bt, 48, 50.5), { size: 50 });
  }
  if (bt >= 63 && bt < 97.5) {
    const minutes = KB([[64, 0], [67, 0], [70, 10, 'out'], [75, 10], [78, 30, 'out'], [83, 30], [86, 60, 'out']])(bt);
    const m2 = EASE.inOut(seg(bt, 95, 97));
    // arrive from the wall clock (shared path with the clock above), leave toward the alarm on the desk
    let rx = lerp(250, 840, morph), ry = lerp(592, 690, morph), rs = lerp(64, 120, morph) / 120;
    if (m2 > 0) { rx = lerp(840, 470 + 165 * 0.9, m2); ry = lerp(690, 842 - 36 * 0.9, m2); rs = lerp(1, 0.22, m2); }
    const a = seg(bt, 63.2, 64.4) * (1 - seg(bt, 96.2, 97));
    ctx.save(); ctx.translate(rx, ry); ctx.scale(rs, rs); ctx.translate(-rx, -ry);
    drawRing(rx, ry, 120, minutes, { alpha: a, concl: seg(bt, 88, 89), bt });
    ctx.restore();
    // small burst when a mark is reached
    for (const [at, c] of [[70, COL.cyan], [78, '#7ccfe6'], [86, COL.yellow]]) {
      const m = at === 70 ? 10 : at === 78 ? 30 : 60;
      const an = -Math.PI / 2 + (m / 60) * TAU;
      sparkleBurst(840 + Math.cos(an) * 120, 690 + Math.sin(an) * 120, seg(bt, at, at + 1.6), c);
    }
  }

  // S2 segment chip
  if (bt > 34 && bt < 64) {
    const a = popA(bt, 35, 0.5) * (1 - seg(bt, 62, 63));
    segChip(600, 520, '第 1 段', seg(bt, 35.5, 48), { alpha: a });
  }

  // S4 calendar + meter
  if (bt > 105 && bt < 128) {
    const a = popA(bt, 106, 0.5) * (1 - seg(bt, 126, 127));
    const k = bt - 108;
    const day = bt < 108 ? 1 : Math.min(8, 1 + Math.floor(k) + 1);
    const flipP = bt >= 108 && bt < 115 ? clamp((k - Math.floor(k)) / 0.6) : 0;
    const shownDay = bt < 108 ? 1 : flipP < 0.5 ? Math.min(7, 1 + Math.floor(k)) : Math.min(7, 2 + Math.floor(k));
    drawCalendar(250, 600, bt >= 115 ? 8 : shownDay, flipP, { alpha: a, stamp: seg(bt, 115, 116) });
    const lvl = KB([[116, 0], [117, 0.78, 'back']])(bt);
    const ma = popA(bt, 115.8, 0.4) * (1 - seg(bt, 126, 127));
    const bottom = 650, hMax = 150, restY = bottom - 0.42 * hMax;
    drawMeter(470, bottom, 64, hMax, lvl, { color: COL.yellow, colorHi: COL.yellowHi, alpha: ma });
    withAlpha(ma, () => {
      // short rest line with label to the right
      const p = seg(bt, 116.2, 117);
      if (p > 0) {
        ctx.save(); ctx.setLineDash([10, 8]); ctx.strokeStyle = 'rgba(181,191,214,0.85)'; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(400, restY); ctx.lineTo(400 + 140 * EASE.out(p), restY); ctx.stroke(); ctx.restore();
        txt('只休息', 552, restY, { size: 26, weight: 700, color: COL.grayHi, alpha: p });
      }
      const top = bottom - lvl * hMax;
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
  // page flip while reading in S1/S2/S5
  if (bp.read > 0.9) {
    const cyc = ((bt - 24.5) % 4 + 4) % 4;
    bp.flip = cyc < 0.9 ? cyc / 0.9 : 0;
  }
  // head shake "no" for 午睡补不了熬夜
  if (bt > 142 && bt < 144.5) bp.headTilt = Math.sin((bt - 142) * Math.PI * 2.2) * 0.12 * (1 - seg(bt, 143.6, 144.5));
  bp.worry = win(bt, 142, 144.6, 0.3, 0.6) * 0.6;
  const ring = bt >= 98 && bt < 100.8 ? 1 : 0;
  const alarmA = bt >= 96.4 && bt < 126.6 ? 1 - seg(bt, 125.8, 126.6) : 0;
  const bookOnDesk = (bt > 50 && bt < 129.5) || bt > 134;
  const notebook = (bt > 101.5 && bt < 126.6) || bt > 138.4;
  bp.deskProps = () => {
    if (bookOnDesk && bp.read < 0.5) drawClosedBookLocal(-120, -3, bp.bookColor);
    if (notebook) withAlpha(bt > 126 && bt < 138.4 ? 0 : 1, () => drawNotebookLocal(20, -3));
    if (alarmA > 0) withAlpha(alarmA, () => drawAlarmLocal(165, -36, 30, ring, bt));
  };
}

// ---------- S5 table ----------
const TABLE = { x: 760, y: 262, w: 1010, h: 706 };
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
    txt('下午学习表', x + 48, y + 62, { size: 54, weight: 900, color: COL.cream });
    txt('AFTERNOON PLAN', x + w - 44, y + 66, { size: 24, weight: 600, fam: 'mono', color: COL.cyan, align: 'right' });
    line(x + 40, y + 112, x + w - 40, y + 112, 'rgba(63,203,232,0.35)', 2);

    const rows = [
      { at: 130, icon: 'book', main: [{ s: '学一段' }], sub: [{ s: '先把手上这一段学完' }] },
      { at: 134, icon: 'zz', main: [{ s: '睡 ' }, { s: '30–60 分钟', color: COL.yellow }], sub: [{ s: '只想提神：' }, { s: '10 分钟', color: COL.cyan }, { s: ' 就够' }] },
      { at: 138, icon: 'book', main: [{ s: '接着学' }], sub: [{ s: '醒来接着学下一段' }] },
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
    // warning row
    const wa = popA(bt, 142, 0.35);
    if (wa > 0) withAlpha(wa, () => {
      const wy = y + 560, s = popS(bt, 142, 0.6);
      withScale(x + w / 2, wy + 42, 0.9 + 0.1 * s, () => {
        rrect(x + 36, wy, w - 72, 86, 14, 'rgba(255,111,158,0.12)', 'rgba(255,111,158,0.7)', 2.5);
        iconMoonX(x + 86, wy + 43, 50, COL.pink);
        line(x + 66, wy + 64, x + 108, wy + 22, COL.pink, 4);
        txt('午睡补不了熬夜', x + 136, wy + 43, { size: 46, weight: 900, color: COL.cream });
        txt('晚上照样要睡够', x + w - 64, wy + 45, { size: 26, weight: 700, color: COL.pink, align: 'right' });
      });
    });
    // "screenshot" flash when the table is complete
    const fl = win(bt, 146, 147.4, 0.04, 1.2);
    if (fl > 0) {
      rrect(x, y, w, h, 18, `rgba(255,255,255,${0.1 * fl})`, `rgba(255,250,235,${0.9 * fl})`, 5);
    }
    const fa = popA(bt, 144, 0.6);
    if (fa > 0) {
      txt('仅供参考', x + 44, y + h - 30, { size: 24, weight: 700, color: COL.gray, alpha: fa });
      txt('Cousins 2019 · Leong 2022/2023 · Lo 2017', x + w - 44, y + h - 30, { size: 20, weight: 500, fam: 'mono', color: COL.grayDim, align: 'right', alpha: fa });
    }
    ctx.restore();
  });
}

function drawSaveButton(bt) {
  const a = popA(bt, 149.5, 0.35);
  if (a <= 0) return;
  const x = 560, y = 548, s = popS(bt, 149.5, 0.7);
  const tapped = bt >= 152;
  const press = tapped ? 1 - 0.08 * Math.sin(Math.PI * clamp((bt - 152) / 0.5)) : 1;
  withAlpha(a, () => withScale(x, y, s * press, () => {
    const w = 316, h = 84;
    ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = tapped ? 34 : 14;
    rrect(x - w / 2, y - h / 2, w, h, h / 2, tapped ? 'rgba(247,185,62,0.22)' : 'rgba(12,26,58,0.92)', COL.yellow, 3);
    ctx.restore();
    iconStar(x - w / 2 + 50, y, 24, tapped ? COL.yellow : null, COL.yellow, 3.5);
    txt('收藏这张表', x - w / 2 + 88, y + 1, { size: 38, weight: 900, color: COL.cream });
  }));
  sparkleBurst(x - 108, y, seg(bt, 152, 154));
  const ca = popA(bt, 153, 0.5);
  if (ca > 0) txt('下午学累了，照着做', x, y + 68, { size: 28, weight: 700, color: COL.grayHi, align: 'center', alpha: ca });
}

// ---------- foreground for sections ----------
function drawSections(bt, t, boy) {
  if (bt < 31) return;
  drawHeaders(bt);

  // S2
  if (bt < 64) {
    const bulletA = 1 - seg(bt, 63, 63.8);
    if (bt >= 34) bulletLine([{ s: '先' }, { s: '学完一段', color: COL.cyan, glow: 12 }, { s: '，再趴下睡' }], 'Finish one block, then put your head down.',
      { alpha: bulletA, p: seg(bt, 34, 35.2), typeP: seg(bt, 34.6, 37.5), bt });
    rcLine(0, 'book', [{ s: '先学一段' }], 36, bt, { out: 62.6 });
    rcLine(1, 'bell', [{ s: '下午 3 点，' }, { s: '叮', color: COL.yellow, glow: 14 }], 48, bt, { out: 62.6, color: COL.yellow });
    rcLine(2, 'zz', [{ s: '合上书，趴下睡' }], 52, bt, { out: 62.6 });
    const na = popA(bt, 54, 0.6) * (1 - seg(bt, 62.6, 63.2));
    if (na > 0) {
      txt('实验里也是先学一段，下午 3 点才分组', RC.icon - 30, 908, { size: 28, weight: 700, color: COL.grayHi, alpha: na });
      sourceNote('Cousins 等 2019 · 《Sleep》', RC.icon - 30, 948, { alpha: na });
    }
  }
  // S3
  if (bt >= 64 && bt < 97) {
    const filled = bt >= 88;
    const fp = seg(bt, 88, 88.6);
    const blankA = 0.55 + 0.45 * Math.sin(bt * Math.PI);
    const spans = [
      { s: '想提神睡 ' },
      filled ? { s: '10', color: COL.cyan, glow: 14 } : { s: '？', color: COL.grayDim, alpha: blankA },
      { s: ' 分钟，想记得牢睡 ' },
      filled ? { s: '30–60', color: COL.yellow, glow: 14 } : { s: '？', color: COL.grayDim, alpha: blankA },
      { s: ' 分钟' },
    ];
    bulletLine(spans, filled ? '10 min to perk up · 30–60 min to remember' : '', {
      alpha: popA(bt, 65.5, 0.6) * (1 - seg(bt, 95.4, 96)), p: filled ? seg(bt, 88, 89) : 0, typeP: seg(bt, 88.4, 91), bt, textA: 1,
    });
    if (fp > 0 && fp < 1) sparkleBurst(560, 326, fp, COL.cyan);
    const out = 95.2;
    ringLine(0, 10, COL.cyan, [{ s: '更清醒' }], '10–60 分钟都有这个效果', 70, bt, out);
    ringLine(1, 30, '#7ccfe6', [{ s: '醒来记新东西更好' }], '只有 30 分钟这组 · 被试平时睡得偏少', 78, bt, out);
    ringLine(2, 60, COL.yellow, [{ s: '一周后还记得更多' }], '实验里睡 1 小时', 86, bt, out);
    const na = popA(bt, 71, 0.6) * (1 - seg(bt, out, out + 0.6));
    if (na > 0) sourceNote('10 / 30 分钟：Leong 等 2023 · 60 分钟：Cousins 等 2019', RC.icon - 30, 948, { alpha: na });
  }
  // S4
  if (bt >= 96 && bt < 128) {
    const out = 126;
    if (bt >= 102) bulletLine([{ s: '闹钟一响，' }, { s: '接着学下一段', color: COL.cyan, glow: 12 }], 'Alarm rings -> keep learning.',
      { alpha: 1 - seg(bt, out, out + 0.8), p: seg(bt, 102, 103.2), typeP: seg(bt, 102.6, 105), bt });
    rcLine(0, 'alarm', [{ s: '闹钟响，起来' }], 100.6, bt, { out });
    rcLine(1, 'book', [{ s: '接着学第 2 段' }], 103, bt, { out });
    rcLine(2, 'calendar', [{ s: '一周后：' }, { s: '睡过的还领先', color: COL.yellow, glow: 14 }], 117.7, bt, { out, color: COL.yellow });
    const na = popA(bt, 119, 0.6) * (1 - seg(bt, out, out + 0.6));
    if (na > 0) {
      txt('实验里：睡完接着学，学完 30 分钟考一次，一周后再考', RC.icon - 30, 908, { size: 28, weight: 700, color: COL.grayHi, alpha: na });
      sourceNote('Cousins 等 2019 · 《Sleep》', RC.icon - 30, 948, { alpha: na });
    }
    dingBurst(470 + 165 * 0.9 + 40, 842 - 34 * 0.9 - 64, seg(bt, 98, 100.4), { s: '叮铃', size: 34 });
  }
  // S5
  if (bt >= 126.2) {
    drawTable(bt);
    drawSaveButton(bt);
  }
}
