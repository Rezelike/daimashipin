// props.js — the quiz-show stage of 「先看书还是先做题？」 (plan.md 第 1 条: 答题闯关台) and its props.
// Everything here is this episode's own: stage disc + spotlights, question card on a stand, buzzer podium, LED scoreboards,
// LED marquee with a rolling hour counter, question-bank box, question cards, the big example card, the big book page,
// marker / highlighter, the hanging screen for the rounds (第 1/2/3 关) and the flip panels of the summary.
const PAPER = '#f4efe6', INK = '#14213f', INK_SOFT = '#5d6886', AMBER = '#b87208', ROSE = '#cf3a69';
const STAGE_Y = 905;   // the figure's ground line (top of the stage disc)

// ---------- small helpers ----------
function iconStar(x, y, r, fill, stroke, lw = 3) {
  ctx.save(); ctx.beginPath();
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + (i * Math.PI) / 5, rr = i % 2 === 0 ? r : r * 0.45;
    const px = x + Math.cos(a) * rr, py = y + Math.sin(a) * rr;
    i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
  }
  ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.stroke(); }
  ctx.restore();
}
function iconBook(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.09; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(x, y - s * 0.26); ctx.quadraticCurveTo(x - s * 0.22, y - s * 0.38, x - s * 0.46, y - s * 0.3);
  ctx.lineTo(x - s * 0.46, y + s * 0.32); ctx.quadraticCurveTo(x - s * 0.22, y + s * 0.24, x, y + s * 0.36);
  ctx.quadraticCurveTo(x + s * 0.22, y + s * 0.24, x + s * 0.46, y + s * 0.32); ctx.lineTo(x + s * 0.46, y - s * 0.3);
  ctx.quadraticCurveTo(x + s * 0.22, y - s * 0.38, x, y - s * 0.26); ctx.lineTo(x, y + s * 0.36);
  ctx.stroke(); ctx.restore();
}
// question-card icon (for the 先做题 board)
function iconCard(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.09; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.roundRect(x - s * 0.42, y - s * 0.3, s * 0.84, s * 0.6, s * 0.08); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x - s * 0.22, y - s * 0.06); ctx.lineTo(x + s * 0.22, y - s * 0.06); ctx.moveTo(x - s * 0.22, y + s * 0.1); ctx.lineTo(x + s * 0.08, y + s * 0.1); ctx.stroke();
  ctx.restore();
}
// stopwatch (the marquee's clock): hand angle in turns
function iconStopwatch(x, y, s, color, turns = 0) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.1; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(x, y + s * 0.06, s * 0.38, 0, TAU); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x, y - s * 0.32); ctx.lineTo(x, y - s * 0.46); ctx.moveTo(x - s * 0.12, y - s * 0.48); ctx.lineTo(x + s * 0.12, y - s * 0.48); ctx.stroke();
  const a = turns * TAU - Math.PI / 2;
  ctx.beginPath(); ctx.moveTo(x, y + s * 0.06); ctx.lineTo(x + Math.cos(a) * s * 0.27, y + s * 0.06 + Math.sin(a) * s * 0.27); ctx.stroke();
  ctx.restore();
}
function crossMark(x, y, r, color = COL.pink) {
  circle(x, y, r, color);
  line(x - r * 0.38, y - r * 0.38, x + r * 0.38, y + r * 0.38, '#0d1838', Math.max(3, r * 0.17));
  line(x + r * 0.38, y - r * 0.38, x - r * 0.38, y + r * 0.38, '#0d1838', Math.max(3, r * 0.17));
}
function okMark(x, y, r, p = 1, color = COL.yellow) {
  ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 18; circle(x, y, r, color); ctx.restore();
  checkBadge(x, y, r, { color: '#0d1838', p, lw: Math.max(3, r * 0.16) });
}
function sparkleBurst(x, y, p, color = COL.yellow, n = 10) {
  if (p <= 0 || p >= 1) return;
  withAlpha(1 - p, () => {
    for (let i = 0; i < n; i++) {
      const an = (i / n) * TAU + 0.3, d = 30 + EASE.out(p) * 90;
      iconStar(x + Math.cos(an) * d, y + Math.sin(an) * d, 9 * (1 - p * 0.5), color);
    }
  });
}
function sourceNote(s, x, y, o = {}) {
  const { alpha = 1, align = 'left', size = 22 } = o;
  txt(s, x, y, { size, weight: 500, color: 'rgba(181,191,214,0.78)', align, alpha });
}

// ---------- stage: disc on the floor, a spotlight that follows him, two faint side beams ----------
function drawStage(t, heroX, o = {}) {
  const { glow = 0 } = o;
  // side beams (static)
  for (const [x0, x1, c] of [[260, 420, '63,203,232'], [1660, 1500, '247,185,62']]) {
    const g = ctx.createLinearGradient(0, 0, 0, STAGE_Y);
    g.addColorStop(0, `rgba(${c},0.07)`); g.addColorStop(1, `rgba(${c},0.0)`);
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.moveTo(x0 - 22, -10); ctx.lineTo(x0 + 22, -10); ctx.lineTo(x1 + 170, STAGE_Y); ctx.lineTo(x1 - 170, STAGE_Y); ctx.closePath(); ctx.fill();
  }
  // stage disc
  ctx.save();
  ellipse(960, STAGE_Y + 22, 900, 70, 'rgba(6,12,32,0.55)');
  ellipse(960, STAGE_Y + 8, 900, 64, 'rgba(22,40,88,0.78)');
  ctx.beginPath(); ctx.ellipse(960, STAGE_Y + 8, 900, 64, 0, 0, TAU);
  ctx.strokeStyle = `rgba(63,203,232,${0.32 + 0.4 * glow})`; ctx.lineWidth = 2.5;
  if (glow > 0) { ctx.shadowColor = COL.cyan; ctx.shadowBlur = 24 * glow; }
  ctx.stroke(); ctx.restore();
  for (let i = 0; i < 25; i++) {   // little lamps along the front edge
    const a = Math.PI * (0.12 + 0.76 * (i / 24)), x = 960 + Math.cos(a) * 900, y = STAGE_Y + 8 + Math.sin(a) * 64;
    circle(x, y, 2.6, `rgba(255,220,150,${0.35 + 0.5 * glow})`);
  }
  // the spotlight on him
  const g = ctx.createLinearGradient(0, 0, 0, STAGE_Y);
  g.addColorStop(0, 'rgba(255,236,196,0.0)'); g.addColorStop(0.35, 'rgba(255,236,196,0.035)'); g.addColorStop(1, 'rgba(255,236,196,0.09)');
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.moveTo(heroX - 34, -10); ctx.lineTo(heroX + 34, -10); ctx.lineTo(heroX + 205, STAGE_Y); ctx.lineTo(heroX - 205, STAGE_Y); ctx.closePath(); ctx.fill();
  const pg = ctx.createRadialGradient(heroX, STAGE_Y, 10, heroX, STAGE_Y, 230);
  pg.addColorStop(0, 'rgba(255,226,170,0.26)'); pg.addColorStop(1, 'rgba(255,226,170,0)');
  ctx.save(); ctx.translate(heroX, STAGE_Y); ctx.scale(1, 0.17); ctx.translate(-heroX, -STAGE_Y);
  ctx.fillStyle = pg; ctx.fillRect(heroX - 240, STAGE_Y - 240, 480, 480); ctx.restore();
}

// ---------- question card on a stand (opening): 第 1 / 8 题, four options ----------
// opt: array of 4 states 'idle' | 'focus' | 'wrong' | 'right' (+ optional focus strength via o.focus[i])
const QSTAND = { x: 440, y: 640, w: 440, h: 300 };
function drawQuizStand(o = {}) {
  const { alpha = 1, opt = ['idle', 'idle', 'idle', 'idle'], focus = [0, 0, 0, 0], scale = 1, cx = QSTAND.x, cy = QSTAND.y, stand = 1, qn = 1, sx = 1, card = true, plain = false } = o;
  withAlpha(alpha, () => {
    const { w, h } = QSTAND;
    if (stand > 0) withAlpha(stand, () => {
      rrect(cx - 7, cy + h / 2 - 4, 14, STAGE_Y - (cy + h / 2) + 4, 5, '#3a4766');
      ellipse(cx, STAGE_Y, 70, 10, '#2b3654');
    });
    if (sx < 0.02 || !card) return;
    ctx.save(); ctx.translate(cx, cy); ctx.scale(sx * scale, scale); ctx.translate(-cx, -cy);
    {
      lintPanel('题卡架', cx - w / 2, cy - h / 2, w, h);
      ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 8;
      rrect(cx - w / 2, cy - h / 2, w, h, 20, PAPER); ctx.restore();
      rrect(cx - w / 2, cy - h / 2, w, 64, [20, 20, 0, 0], INK);
      if (plain) { for (let k = 0; k < 4; k++) rrect(cx - w / 2 + 28 + (k % 2) * (w / 2 - 22), cy - h / 2 + 156 + Math.floor(k / 2) * 64, w / 2 - 34, 50, 12, '#e4ddcf'); return; }
      txt(`第 ${qn} / 8 题`, cx - w / 2 + 26, cy - h / 2 + 33, { size: 36, weight: 900, color: COL.cream });
      rrect(cx + w / 2 - 150, cy - h / 2 + 10, 132, 46, 23, COL.yellow);
      txt('四选一', cx + w / 2 - 84, cy - h / 2 + 34, { size: 34, weight: 900, color: INK, align: 'center' });
      // the question (placeholder lines: the real items are not shown in the paper)
      rrect(cx - w / 2 + 28, cy - h / 2 + 88, w - 56, 14, 7, 'rgba(20,33,63,0.28)');
      rrect(cx - w / 2 + 28, cy - h / 2 + 114, w - 150, 14, 7, 'rgba(20,33,63,0.28)');
      ['A', 'B', 'C', 'D'].forEach((L, i) => {
        const ox = cx - w / 2 + 28 + (i % 2) * ((w - 56) / 2 + 6), oy = cy - h / 2 + 156 + Math.floor(i / 2) * 64;
        const ow = (w - 56) / 2 - 6, st = opt[i], f = focus[i] || 0;
        const fill = st === 'wrong' ? '#ffd9e3' : st === 'right' ? '#fff0c4' : lerpColor('#e4ddcf', '#d6f3fa', f);
        const edge = st === 'wrong' ? COL.pink : st === 'right' ? COL.yellow : f > 0.05 ? COL.cyan : 'rgba(20,33,63,0.18)';
        ctx.save(); if (f > 0.05 || st !== 'idle') { ctx.shadowColor = edge; ctx.shadowBlur = 14 * Math.max(f, st !== 'idle' ? 1 : 0); }
        rrect(ox, oy, ow, 50, 12, fill, edge, 3); ctx.restore();
        txt(L, ox + 28, oy + 26, { size: 34, weight: 800, fam: 'mono', color: INK, align: 'center' });
        rrect(ox + 56, oy + 20, ow - 120, 10, 5, 'rgba(20,33,63,0.22)');
        if (st === 'wrong') crossMark(ox + ow - 28, oy + 25, 17, COL.pink);
        if (st === 'right') okMark(ox + ow - 28, oy + 25, 17, 1);
      });
    }
    ctx.restore();
  });
}

// ---------- buzzer podium: press 0..1 squashes the dome; flash 0..1 with color ----------
function drawBuzzer(x, top, o = {}) {
  const { alpha = 1, press = 0, flash = 0, flashColor = COL.pink } = o;
  withAlpha(alpha, () => {
    lintPanel('抢答器', x - 75, top - 40, 150, STAGE_Y - top + 40);
    if (flash > 0.01) {
      const g = ctx.createRadialGradient(x, top - 14, 6, x, top - 14, 170);
      g.addColorStop(0, rgba(flashColor, 0.55 * flash)); g.addColorStop(1, rgba(flashColor, 0));
      ctx.fillStyle = g; ctx.fillRect(x - 180, top - 190, 360, 360);
    }
    // podium body
    ctx.beginPath(); ctx.moveTo(x - 58, top); ctx.lineTo(x + 58, top); ctx.lineTo(x + 74, STAGE_Y); ctx.lineTo(x - 74, STAGE_Y); ctx.closePath();
    const g = ctx.createLinearGradient(x - 74, 0, x + 74, 0);
    g.addColorStop(0, '#16244d'); g.addColorStop(0.5, '#22356b'); g.addColorStop(1, '#131f43');
    ctx.fillStyle = g; ctx.fill();
    ctx.strokeStyle = 'rgba(63,203,232,0.55)'; ctx.lineWidth = 2.5; ctx.stroke();
    rrect(x - 62, top + 40, 124, 16, 4, COL.yellow);
    rrect(x - 66, top - 8, 132, 14, 6, '#2c3f78');
    // the dome
    const sq = 1 - 0.45 * press;
    ctx.save(); if (flash > 0.01) { ctx.shadowColor = flashColor; ctx.shadowBlur = 30 * flash; }
    ctx.beginPath(); ctx.ellipse(x, top - 8, 34, 26 * sq, 0, Math.PI, TAU); ctx.closePath();
    ctx.fillStyle = flash > 0.01 ? lerpColor('#e2475f', flashColor === COL.yellow ? '#ffd57e' : '#ff8aa8', flash) : '#e2475f'; ctx.fill();
    ctx.restore();
    ellipse(x - 10, top - 8 - 15 * sq, 10, 5 * sq, 'rgba(255,255,255,0.45)');
  });
}

// ---------- LED scoreboard: label strip, big value, one sub line under it ----------
const BOARD = { w: 300, h: 250 };
function drawScoreboard(cx, cy, o = {}) {
  const { alpha = 1, label = '', icon = null, color = COL.yellow, value = null, sub = null, subColor = COL.grayHi, glow = 1,
    dim = 0, legs = true, w = BOARD.w, h = BOARD.h, valueSize = 104 } = o;
  withAlpha(alpha, () => {
    lintPanel('记分牌 ' + label, cx - w / 2, cy - h / 2, w, h);
    if (legs) { line(cx - w / 2 + 40, cy + h / 2, cx - w / 2 + 40, STAGE_Y, '#3a4766', 6); line(cx + w / 2 - 40, cy + h / 2, cx + w / 2 - 40, STAGE_Y, '#3a4766', 6); }
    const c = lerpColor(color, '#66728f', dim);
    ctx.save(); ctx.shadowColor = c; ctx.shadowBlur = 22 * glow * (1 - dim);
    rrect(cx - w / 2, cy - h / 2, w, h, 18, '#081229', c, 3.5); ctx.restore();
    // dot-matrix texture
    ctx.save(); ctx.beginPath(); ctx.roundRect(cx - w / 2 + 4, cy - h / 2 + 4, w - 8, h - 8, 15); ctx.clip();
    ctx.fillStyle = 'rgba(120,160,230,0.07)';
    for (let yy = cy - h / 2 + 70; yy < cy + h / 2; yy += 9) for (let xx = cx - w / 2 + 8; xx < cx + w / 2; xx += 9) ctx.fillRect(xx, yy, 2.4, 2.4);
    ctx.restore();
    rrect(cx - w / 2, cy - h / 2, w, 60, [18, 18, 0, 0], rgba(c.startsWith('#') ? c : '#8d99b5', 0.95));
    if (icon) { ICONS2[icon](cx - w / 2 + 36, cy - h / 2 + 30, 34, '#0b1736'); }
    txt(label, icon ? cx + 16 : cx, cy - h / 2 + 31, { size: 36, weight: 900, color: '#0b1736', align: 'center' });
    if (value !== null) txt(value, cx, cy + 24, { size: valueSize, weight: 800, fam: 'mono', color: lerpColor(color === COL.yellow ? COL.yellowHi : color === COL.cyan ? COL.cyanHi : color, '#8994ad', dim), align: 'center', glow: 16 * glow * (1 - dim) });
    else txt('– –', cx, cy + 24, { size: 84, weight: 800, fam: 'mono', color: 'rgba(200,212,236,0.25)', align: 'center' });
    if (sub) {
      if (typeof sub === 'string') txt(sub, cx, cy + h / 2 - 30, { size: 34, weight: 900, color: subColor, align: 'center' });
      else rich(sub, cx, cy + h / 2 - 30, { size: 34, weight: 900, align: 'center' });
    }
  });
}
const ICONS2 = { card: iconCard, book: iconBook };

// ---------- LED marquee above the scoreboards: items flip vertically; a stopwatch at the left ----------
function drawMarquee(cx, cy, items, idx, o = {}) {
  const { alpha = 1, w = 660, h = 80, turns = 0, flash = 0 } = o;
  withAlpha(alpha, () => {
    lintPanel('跑马灯', cx - w / 2, cy - h / 2, w, h);
    ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 10 + 26 * flash;
    rrect(cx - w / 2, cy - h / 2, w, h, 14, '#0a1026', `rgba(247,185,62,${0.55 + 0.45 * flash})`, 3); ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.roundRect(cx - w / 2 + 3, cy - h / 2 + 3, w - 6, h - 6, 12); ctx.clip();
    ctx.fillStyle = 'rgba(255,200,110,0.06)';
    for (let yy = cy - h / 2 + 6; yy < cy + h / 2; yy += 8) for (let xx = cx - w / 2 + 6; xx < cx + w / 2; xx += 8) ctx.fillRect(xx, yy, 2.2, 2.2);
    iconStopwatch(cx - w / 2 + 46, cy, 44, COL.yellowHi, turns);
    const i0 = Math.floor(idx), i1 = Math.min(items.length - 1, i0 + 1), p = idx - i0, e = EASE.inOut(p);
    const tx = cx + 34;
    const draw = (it, dy, a) => { if (a > 0.01) txt(typeof it === 'function' ? it() : it, tx, cy + dy + 1, { size: 38, weight: 900, color: COL.yellowHi, align: 'center', alpha: a, glow: 10 }); };
    if (p <= 0.001) draw(items[i0], 0, 1);
    else { draw(items[i0], -e * h, 1 - e); draw(items[i1], (1 - e) * h, e); }
    ctx.restore();
  });
}

// ---------- question cards ----------
// small card: w x h centred at (x, y); o: { n, star, guess, mark: 'x' | 'ok' | null, markP, gray, glow, scribble }
function drawQCard(x, y, o = {}) {
  const { w = 150, h = 104, n = 1, star = false, mark = null, markP = 1, gray = 0, glow = 0, scribble = 0, sx = 1, alpha = 1, rot = 0, back = false, plain = false } = o;
  if (sx < 0.02) return;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sx, 1);
    lintPanel('题卡', -w / 2, -h / 2, w, h);
    ctx.save(); ctx.shadowColor = glow > 0 ? COL.yellow : 'rgba(0,0,0,0.4)'; ctx.shadowBlur = glow > 0 ? 22 * glow : 12; ctx.shadowOffsetY = glow > 0 ? 0 : 4;
    rrect(-w / 2, -h / 2, w, h, 12, back ? '#22356b' : lerpColor(PAPER, '#8a93a8', gray)); ctx.restore();
    if (back) {
      rrect(-w / 2 + 8, -h / 2 + 8, w - 16, h - 16, 8, null, 'rgba(143,232,248,0.5)', 2);
      txt('?', 0, 2, { size: h * 0.5, weight: 900, color: 'rgba(143,232,248,0.8)', align: 'center' });
    } else {
      rrect(-w / 2, -h / 2, w, 22, [12, 12, 0, 0], lerpColor(COL.yellow, '#66728f', gray));
      if (!plain) txt('Q' + n, -w / 2 + 12, -h / 2 + 46, { size: 34, weight: 800, fam: 'mono', color: lerpColor(INK, '#3a4766', gray) });
      rrect(-w / 2 + 14, h / 2 - 34, w - 28, 9, 4.5, 'rgba(20,33,63,0.22)');
      rrect(-w / 2 + 14, h / 2 - 18, (w - 28) * 0.6, 9, 4.5, 'rgba(20,33,63,0.22)');
      if (star) iconStar(w / 2 - 24, -h / 2 + 46, 15, COL.yellow, '#8a5a00', 2);
      if (scribble > 0) {   // a guess scribbled on the card (pink handwriting squiggle)
        ctx.save(); ctx.strokeStyle = ROSE; ctx.lineWidth = 4; ctx.lineCap = 'round';
        ctx.beginPath();
        const n2 = Math.floor(28 * clamp(scribble));
        for (let k = 0; k <= n2; k++) { const xx = -w / 2 + 64 + k * 2.4, yy = -h / 2 + 44 + Math.sin(k * 1.3) * 7; k ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); }
        ctx.stroke(); ctx.restore();
      }
      if (mark === 'x') withScale(w / 2 - 22, h / 2 - 22, EASE.back(clamp(markP)), () => crossMark(w / 2 - 22, h / 2 - 22, 18, COL.pink));
      if (mark === 'ok') withScale(w / 2 - 22, h / 2 - 22, EASE.back(clamp(markP)), () => okMark(w / 2 - 22, h / 2 - 22, 18, markP));
    }
    ctx.restore();
  });
}

// the question bank: a box on a pedestal, cards standing in it; n = cards still in it, lid 0..1
function drawCardBox(x, top, o = {}) {
  const { alpha = 1, n = 10, lid = 0, lift = 0 } = o;
  withAlpha(alpha, () => {
    lintPanel('题库', x - 100, top - 70, 200, STAGE_Y - top + 70);
    rrect(x - 26, top + 70, 52, STAGE_Y - top - 70, 6, '#2b3a66');
    ellipse(x, STAGE_Y, 80, 11, '#22305a');
    ellipse(x, top + 72, 64, 10, '#3a4f8a');
    // cards standing up in the box (back row higher); the top one rises with `lift`
    for (let k = 0; k < n; k++) {
      const dx = -70 + (k % 5) * 35, dy = k < 5 ? -46 : -34;
      rrect(x + dx - 12, top + dy - (k === n - 1 ? lift * 40 : 0), 44, 60, 6, k < 5 ? '#d9d2c3' : PAPER, 'rgba(20,33,63,0.25)', 1.5);
      rrect(x + dx - 12, top + dy - (k === n - 1 ? lift * 40 : 0), 44, 8, [6, 6, 0, 0], COL.yellow);
    }
    // box front
    const g = ctx.createLinearGradient(0, top, 0, top + 74);
    g.addColorStop(0, '#2f4a8f'); g.addColorStop(1, '#1b2c5c');
    rrect(x - 96, top - 6, 192, 80, 12, g, 'rgba(143,232,248,0.6)', 2.5);
    txt('题库', x, top + 34, { size: 36, weight: 900, color: COL.cream, align: 'center' });
    if (lid > 0) {
      ctx.save(); ctx.translate(x - 96, top - 6); ctx.rotate(-(1 - lid) * 1.25);
      rrect(0, -14, 192, 18, 6, '#3a5aa8', 'rgba(143,232,248,0.6)', 2); ctx.restore();
    }
  });
}

// the big example card (step ②): the paper's own example item (Richland et al. 2009, appendix A)
const EX = { x: 1280, y: 520, w: 700, h: 360 };
function drawExampleCard(o = {}) {
  const { alpha = 1, guess = '', guessP = 0, wrong = 0, fix = 0, scale = 1, x = EX.x, y = EX.y, qn = 1, sx = 1, scrib = 0, xMark = 0 } = o;
  if (sx < 0.02) return;
  withAlpha(alpha, () => { ctx.save(); ctx.translate(x, y); ctx.scale(scale * sx, scale); ctx.translate(-x, -y); {
    const { w, h } = EX, x0 = x - w / 2, y0 = y - h / 2;
    lintPanel('例题卡', x0, y0, w, h);
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 10;
    rrect(x0, y0, w, h, 24, PAPER); ctx.restore();
    rrect(x0, y0, w, 26, [24, 24, 0, 0], COL.yellow);
    if (qn > 1) {   // the other questions: placeholder lines (the paper's items are not shown), a scribbled guess, a cross
      txt(`第 ${qn} 题`, x0 + 34, y0 + 70, { size: 40, weight: 900, color: INK_SOFT });
      rrect(x0 + 34, y0 + 118, w - 68, 22, 11, 'rgba(20,33,63,0.28)');
      rrect(x0 + 34, y0 + 162, w - 220, 22, 11, 'rgba(20,33,63,0.28)');
      line(x0 + 34, y0 + 330, x0 + w - 34, y0 + 330, 'rgba(20,33,63,0.35)', 3);
      txt('我猜：', x0 + 34, y0 + 252, { size: 34, weight: 900, color: INK_SOFT });
      if (scrib > 0) {
        ctx.save(); ctx.strokeStyle = ROSE; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
        ctx.beginPath();
        const n2 = Math.floor(60 * clamp(scrib));
        for (let k = 0; k <= n2; k++) { const xx = x0 + 40 + k * 4.2, yy = y0 + 300 + Math.sin(k * 0.9) * 14 * (0.6 + 0.4 * Math.sin(k * 0.23)); k ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); }
        ctx.stroke(); ctx.restore();
      }
      if (xMark > 0) withScale(x0 + w - 92, y0 + 270, EASE.back(clamp(xMark)), () => crossMark(x0 + w - 92, y0 + 270, 40, COL.pink));
    } else {
      txt('实验里的一道题 · 一位车祸后全色盲的画家', x0 + 34, y0 + 66, { size: 30, weight: 700, color: INK_SOFT });
      txt('番茄汁在他眼里', x0 + 34, y0 + 128, { size: 50, weight: 900, color: INK });
      txt('是什么颜色？', x0 + 34, y0 + 190, { size: 50, weight: 900, color: INK });
      line(x0 + 34, y0 + 330, x0 + w - 34, y0 + 330, 'rgba(20,33,63,0.35)', 3);
      txt('我猜：', x0 + 34, y0 + 252, { size: 34, weight: 900, color: INK_SOFT });
      if (guess && guessP > 0) {
        const n = Math.max(1, Math.round(guess.length * clamp(guessP)));
        txt(guess.slice(0, n), x0 + 34, y0 + 302, { size: 56, weight: 900, color: ROSE });
        if (fix > 0) line(x0 + 30, y0 + 304, x0 + 30 + (measure(guess, 56, 900) + 8) * EASE.out(clamp(fix * 2)), y0 + 304, INK, 6);
      }
      if (wrong > 0) withScale(x0 + w - 110, y0 + 262, EASE.back(clamp(wrong)), () => {
        ctx.save(); ctx.translate(x0 + w - 110, y0 + 262); ctx.rotate(-0.18);
        ctx.strokeStyle = COL.pink; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(0, 0, 54, 0, TAU); ctx.stroke();
        txt('错', 0, 2, { size: 62, weight: 900, color: COL.pink, align: 'center' });
        ctx.restore();
      });
      if (fix > 0.5) {
        const a = clamp((fix - 0.5) * 2);
        txt('黑色', x0 + 250, y0 + 302, { size: 56, weight: 900, color: INK, alpha: a });
        withScale(x0 + 400, y0 + 300, EASE.back(a), () => okMark(x0 + 400, y0 + 300, 26, a));
      }
    }
  } ctx.restore(); });
}

// ---------- the big upright book page (steps ③ and the answer section) ----------
// o.found 0..1 draws the highlighter circle round 「黑色」; o.lines: how many text lines are visible (writing in)
const PAGE = { x: 1340, y: 600, w: 720, h: 560 };
function drawBookPage(o = {}) {
  const { alpha = 1, found = 0, x = PAGE.x, y = PAGE.y, w = PAGE.w, h = PAGE.h, scan = -1, text = true } = o;
  withAlpha(alpha, () => {
    const x0 = x - w / 2, y0 = y - h / 2;
    lintPanel('大书页', x0, y0, w, h);
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 34; ctx.shadowOffsetY = 12;
    ctx.beginPath(); ctx.moveTo(x0, y0 + 18); ctx.quadraticCurveTo(x0, y0, x0 + 18, y0); ctx.lineTo(x0 + w - 70, y0);
    ctx.lineTo(x0 + w, y0 + 70); ctx.lineTo(x0 + w, y0 + h - 18); ctx.quadraticCurveTo(x0 + w, y0 + h, x0 + w - 18, y0 + h);
    ctx.lineTo(x0 + 18, y0 + h); ctx.quadraticCurveTo(x0, y0 + h, x0, y0 + h - 18); ctx.closePath();
    ctx.fillStyle = PAPER; ctx.fill(); ctx.restore();
    ctx.beginPath(); ctx.moveTo(x0 + w - 70, y0); ctx.lineTo(x0 + w - 70, y0 + 70); ctx.lineTo(x0 + w, y0 + 70); ctx.closePath();
    ctx.fillStyle = '#d9d0bf'; ctx.fill();
    // spine shadow on the left edge (the page belongs to a book)
    const sg = ctx.createLinearGradient(x0, 0, x0 + 40, 0);
    sg.addColorStop(0, 'rgba(20,33,63,0.22)'); sg.addColorStop(1, 'rgba(20,33,63,0)');
    ctx.fillStyle = sg; ctx.fillRect(x0, y0 + 10, 40, h - 20);
    if (text) {
      txt('全色盲的画家', x0 + 56, y0 + 62, { size: 44, weight: 900, color: INK });
      txt('实验里读的那篇文章', x0 + 56, y0 + 112, { size: 28, weight: 700, color: INK_SOFT });
    } else {
      rrect(x0 + 56, y0 + 50, w * 0.45, 26, 13, 'rgba(20,33,63,0.55)');
    }
    const rows = [0.92, 0.84, null, 0.95, 0.7, 0.9, 0.62];
    rows.forEach((r, i) => {
      const ly = y0 + 172 + i * 54;
      if (r === null && text) {   // the line with the answer
        rich([{ s: '在他眼里，番茄汁是', color: INK }, { s: '黑色', color: INK }, { s: '的', color: INK }], x0 + 56, ly + 4, { size: 40, weight: 900 });
        return;
      }
      if (r === null) r = 0.8;
      const lit = scan >= 0 && Math.abs(scan - i) < 0.6 ? 1 - Math.abs(scan - i) / 0.6 : 0;
      rrect(x0 + 56, ly - 7, (w - 112) * r, 14, 7, lit > 0 ? `rgba(63,150,210,${0.28 + 0.3 * lit})` : 'rgba(20,33,63,0.24)');
    });
    if (found > 0) {   // highlighter circle round 「黑色」
      const [ax, ay] = pageAnswerXY({ x, y, w, h });
      withAlpha(0.35, () => ellipse(ax, ay, 66, 34, COL.yellow));
      ctx.save(); ctx.strokeStyle = 'rgba(247,185,62,0.95)'; ctx.lineWidth = 9; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.ellipse(ax, ay, 72, 38, -0.08, -Math.PI * 0.6, -Math.PI * 0.6 + TAU * 1.04 * EASE.inOut(clamp(found))); ctx.stroke();
      ctx.restore();
    }
  });
}
// screen position of the answer word (for the hand / sparkles)
function pageAnswerXY(o = {}) {
  const { x = PAGE.x, y = PAGE.y, w = PAGE.w, h = PAGE.h } = o;
  const x0 = x - w / 2, y0 = y - h / 2;
  return [x0 + 56 + measure('在他眼里，番茄汁是', 40, 900) + measure('黑色', 40, 900) / 2, y0 + 172 + 2 * 54 + 4];
}

// marker (for writing) and the big highlighter, drawn in the hand; ang = direction of the tip (radians, screen)
function drawMarker(x, y, ang, o = {}) {
  const { len = 70, color = INK } = o;
  ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
  rrect(-len * 0.35, -6, len, 12, 5, color);
  rrect(len * 0.65 - 4, -4, 14, 8, 3, '#e2475f');
  rrect(-len * 0.35 - 6, -7, 14, 14, 4, '#c4cfe6');
  ctx.restore();
}
function drawHighlighter(x, y, ang, o = {}) {
  const { len = 130 } = o;
  ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
  rrect(-len * 0.4, -14, len, 28, 9, COL.yellow);
  rrect(-len * 0.4, -14, len * 0.32, 28, [9, 0, 0, 9], '#e3a52e');
  ctx.beginPath(); ctx.moveTo(len * 0.6, -10); ctx.lineTo(len * 0.6 + 22, -6); ctx.lineTo(len * 0.6 + 22, 4); ctx.lineTo(len * 0.6, 10); ctx.closePath();
  ctx.fillStyle = '#ffd57e'; ctx.fill();
  ctx.restore();
}

// ---------- hanging screen for the rounds (第 1 / 2 / 3 关) ----------
function drawHangingScreen(o = {}) {
  const { alpha = 1, drop = 1, chip = '', title = [], line2 = [], en = '', enP = 1, bt = 0, x = 330, w = 1260, h = 222 } = o;
  if (alpha <= 0.001) return;
  const y = 44 - (1 - EASE.out(drop)) * 50;
  withAlpha(alpha * clamp(drop * 2.5), () => {
    line(x + 140, 0, x + 140, y, '#5c6887', 3); line(x + w - 140, 0, x + w - 140, y, '#5c6887', 3);
    lintPanel('吊屏', x, y, w, h);
    ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 26;
    rrect(x, y, w, h, 24, '#081129', 'rgba(143,232,248,0.85)', 3.5); ctx.restore();
    rrect(x + 10, y + 10, w - 20, h - 20, 18, null, 'rgba(63,203,232,0.22)', 2);
    if (chip) {
      const cw = measure(chip, 34, 900) + 44;
      rrect(x + 40, y + 30, cw, 56, 28, COL.yellow);
      txt(chip, x + 40 + cw / 2, y + 59, { size: 34, weight: 900, color: '#0b1736', align: 'center' });
      rich(title, x + 70 + cw, y + 60, { size: 66, weight: 900 });
    } else rich(title, x + w / 2, y + 60, { size: 66, weight: 900, align: 'center' });
    rich(line2, x + 44, y + 136, { size: 46, weight: 900 });
    typeText(en, enP, x + 46, y + 190, { size: 28, weight: 500, fam: 'mono', color: COL.cyan }, bt);
  });
}

// ---------- overview tag (8–15 s): a small cream question card with its number ----------
function drawCardTag(cx, cy, n, s, o = {}) {
  const { alpha = 1, scale = 1, hi = 0 } = o;
  if (alpha <= 0.001 || scale <= 0.001) return;
  withAlpha(alpha, () => withScale(cx, cy, scale, () => {
    const w = measure(s, 42, 900) + 118, h = 86;
    lintPanel('标签' + n, cx - w / 2, cy - h / 2, w, h);
    ctx.save(); ctx.shadowColor = hi > 0 ? COL.yellow : 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 16 + 24 * hi; ctx.shadowOffsetY = hi > 0 ? 0 : 6;
    rrect(cx - w / 2, cy - h / 2, w, h, 16, PAPER); ctx.restore();
    rrect(cx - w / 2, cy - h / 2, 14, h, [16, 0, 0, 16], COL.yellow);
    circle(cx - w / 2 + 52, cy, 26, INK);
    txt(String(n), cx - w / 2 + 52, cy + 1, { size: 34, weight: 800, fam: 'mono', color: COL.yellowHi, align: 'center' });
    txt(s, cx - w / 2 + 90, cy + 1, { size: 42, weight: 900, color: INK });
  }));
}

// ---------- summary: flip panels on the big screen ----------
// p 0..1 = flip progress (0 = number side, 1 = text side)
function drawFlipPanel(x, y, w, h, n, main, sub, p, o = {}) {
  const { alpha = 1, hi = 0 } = o;
  withAlpha(alpha, () => {
    lintPanel('翻牌' + n, x, y, w, h);
    const sy = Math.abs(Math.cos(Math.PI * clamp(p)));
    const front = p < 0.5;
    ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.scale(1, Math.max(0.02, sy)); ctx.translate(-(x + w / 2), -(y + h / 2));
    if (front) {
      rrect(x, y, w, h, 16, '#16244d', 'rgba(143,232,248,0.55)', 2.5);
      ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 12;
      circle(x + w / 2, y + h / 2, 38, null, COL.cyanHi, 4); ctx.restore();
      txt(String(n), x + w / 2, y + h / 2 + 2, { size: 46, weight: 800, fam: 'mono', color: COL.cyanHi, align: 'center' });
    } else {
      ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 14 + 20 * hi;
      rrect(x, y, w, h, 16, PAPER); ctx.restore();
      rrect(x, y, 96, h, [16, 0, 0, 16], COL.yellow);
      txt(String(n), x + 48, y + h / 2 + 2, { size: 56, weight: 800, fam: 'mono', color: INK, align: 'center' });
      rich(main, x + 126, y + h / 2 - (sub ? 18 : 0), { size: 50, weight: 900 });
      if (sub) txt(sub, x + 128, y + h / 2 + 34, { size: 28, weight: 700, color: INK_SOFT });
    }
    ctx.restore();
  });
}
