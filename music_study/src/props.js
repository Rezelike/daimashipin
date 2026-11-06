// props.js — music_study props: headphones icon, desk phone, notes, lyric bubbles, word chips, dictation sheets, the
// player bar of the opening, playlist rows, small badges. The earlier episodes' bars, wall clock, timer ring, alarm,
// calendar, window, word cards, HUD panel and list table were removed from this copy (Skill 2.3: own props per episode).
const PAPER = '#f4efe6', PAPER_INK = '#14213f';

// ---------- line icons (centred at x, y, size s) ----------
function iconPaper(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.1; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.strokeRect(x - s * 0.32, y - s * 0.42, s * 0.64, s * 0.84);
  for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.moveTo(x - s * 0.18, y - s * 0.2 + i * s * 0.2); ctx.lineTo(x + s * 0.18, y - s * 0.2 + i * s * 0.2); ctx.stroke(); }
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
function iconBolt(x, y, s, color) {
  ctx.save(); ctx.fillStyle = color; ctx.beginPath();
  ctx.moveTo(x + s * 0.08, y - s * 0.46); ctx.lineTo(x - s * 0.26, y + s * 0.06); ctx.lineTo(x - s * 0.02, y + s * 0.06);
  ctx.lineTo(x - s * 0.1, y + s * 0.46); ctx.lineTo(x + s * 0.26, y - s * 0.08); ctx.lineTo(x + s * 0.02, y - s * 0.08);
  ctx.closePath(); ctx.fill(); ctx.restore();
}
function iconCheck(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.12; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.3, y + s * 0.02); ctx.lineTo(x - s * 0.08, y + s * 0.24); ctx.lineTo(x + s * 0.32, y - s * 0.22);
  ctx.stroke(); ctx.restore();
}
// filled eighth note (head, stem, flag)
function iconNote(x, y, s, color) {
  ctx.save(); ctx.fillStyle = color; ctx.strokeStyle = color; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.ellipse(x - s * 0.13, y + s * 0.27, s * 0.17, s * 0.12, -0.35, 0, TAU); ctx.fill();
  ctx.lineWidth = s * 0.075;
  ctx.beginPath(); ctx.moveTo(x + s * 0.025, y + s * 0.22); ctx.lineTo(x + s * 0.025, y - s * 0.4); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x + s * 0.025, y - s * 0.4);
  ctx.bezierCurveTo(x + s * 0.1, y - s * 0.22, x + s * 0.34, y - s * 0.2, x + s * 0.27, y + s * 0.04); ctx.stroke();
  ctx.restore();
}
// two beamed eighth notes
function iconNotes(x, y, s, color) {
  ctx.save(); ctx.fillStyle = color; ctx.strokeStyle = color; ctx.lineCap = 'round';
  const heads = [[x - s * 0.27, y + s * 0.3], [x + s * 0.2, y + s * 0.2]];
  for (const [hx, hy] of heads) { ctx.beginPath(); ctx.ellipse(hx, hy, s * 0.15, s * 0.11, -0.35, 0, TAU); ctx.fill(); }
  ctx.lineWidth = s * 0.07;
  const sx1 = heads[0][0] + s * 0.13, sx2 = heads[1][0] + s * 0.13;
  ctx.beginPath(); ctx.moveTo(sx1, heads[0][1] - s * 0.04); ctx.lineTo(sx1, y - s * 0.32); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(sx2, heads[1][1] - s * 0.04); ctx.lineTo(sx2, y - s * 0.42); ctx.stroke();
  ctx.lineWidth = s * 0.13;
  ctx.beginPath(); ctx.moveTo(sx1, y - s * 0.3); ctx.lineTo(sx2, y - s * 0.4); ctx.stroke();
  ctx.restore();
}
function iconHeart(x, y, s, color) {
  ctx.save(); ctx.fillStyle = color; ctx.beginPath();
  ctx.moveTo(x, y + s * 0.36);
  ctx.bezierCurveTo(x - s * 0.58, y - s * 0.02, x - s * 0.32, y - s * 0.5, x, y - s * 0.2);
  ctx.bezierCurveTo(x + s * 0.32, y - s * 0.5, x + s * 0.58, y - s * 0.02, x, y + s * 0.36);
  ctx.fill(); ctx.restore();
}
function iconPlay(x, y, s, color) {
  ctx.save(); ctx.fillStyle = color; ctx.beginPath();
  ctx.moveTo(x - s * 0.2, y - s * 0.28); ctx.lineTo(x + s * 0.3, y); ctx.lineTo(x - s * 0.2, y + s * 0.28); ctx.closePath();
  ctx.lineJoin = 'round'; ctx.strokeStyle = color; ctx.lineWidth = s * 0.06; ctx.stroke(); ctx.fill(); ctx.restore();
}
function iconPause(x, y, s, color) {
  rrect(x - s * 0.24, y - s * 0.28, s * 0.16, s * 0.56, s * 0.04, color);
  rrect(x + s * 0.08, y - s * 0.28, s * 0.16, s * 0.56, s * 0.04, color);
}
function iconPencil(x, y, s, color) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(-0.78);
  rrect(-s * 0.09, -s * 0.42, s * 0.18, s * 0.62, s * 0.03, color);
  ctx.beginPath(); ctx.moveTo(-s * 0.09, s * 0.22); ctx.lineTo(s * 0.09, s * 0.22); ctx.lineTo(0, s * 0.44); ctx.closePath();
  ctx.fillStyle = color; ctx.fill(); ctx.restore();
}
// silence: a speaker with a cross
function iconQuiet(x, y, s, color) {
  ctx.save(); ctx.fillStyle = color; ctx.strokeStyle = color; ctx.lineCap = 'round'; ctx.lineWidth = s * 0.09;
  ctx.beginPath();
  ctx.moveTo(x - s * 0.42, y - s * 0.12); ctx.lineTo(x - s * 0.24, y - s * 0.12); ctx.lineTo(x - s * 0.02, y - s * 0.34);
  ctx.lineTo(x - s * 0.02, y + s * 0.34); ctx.lineTo(x - s * 0.24, y + s * 0.12); ctx.lineTo(x - s * 0.42, y + s * 0.12); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.moveTo(x + s * 0.14, y - s * 0.14); ctx.lineTo(x + s * 0.42, y + s * 0.14);
  ctx.moveTo(x + s * 0.42, y - s * 0.14); ctx.lineTo(x + s * 0.14, y + s * 0.14); ctx.stroke();
  ctx.restore();
}
// a speech bubble outline; inner = 'dots' (talking) | 'note' (singing = lyrics)
function iconBubble(x, y, s, color, inner = 'dots') {
  ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = s * 0.08; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.roundRect(x - s * 0.44, y - s * 0.34, s * 0.88, s * 0.56, s * 0.2);
  ctx.moveTo(x - s * 0.2, y + s * 0.22); ctx.lineTo(x - s * 0.3, y + s * 0.42); ctx.lineTo(x - s * 0.02, y + s * 0.22);
  ctx.stroke();
  if (inner === 'note') iconNote(x, y - s * 0.07, s * 0.5, color);
  else for (const dx of [-0.2, 0, 0.2]) circle(x + dx * s, y - s * 0.06, s * 0.055, color);
  ctx.restore();
}
function iconNoise(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.08; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  const ys = [0, -0.3, 0.22, -0.18, 0.34, -0.26, 0.12, -0.08, 0];
  ctx.beginPath();
  ys.forEach((v, i) => { const px = x - s * 0.42 + (i / (ys.length - 1)) * s * 0.84; i ? ctx.lineTo(px, y + v * s) : ctx.moveTo(px, y + v * s); });
  ctx.stroke(); ctx.restore();
}
// a picture (for the visual-memory task): frame, sun, hill
function iconImage(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = s * 0.08; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.roundRect(x - s * 0.42, y - s * 0.32, s * 0.84, s * 0.64, s * 0.08); ctx.stroke();
  circle(x + s * 0.18, y - s * 0.1, s * 0.08, color);
  ctx.beginPath(); ctx.moveTo(x - s * 0.36, y + s * 0.26); ctx.lineTo(x - s * 0.1, y - s * 0.02); ctx.lineTo(x + s * 0.06, y + s * 0.14);
  ctx.lineTo(x + s * 0.16, y + s * 0.06); ctx.lineTo(x + s * 0.36, y + s * 0.26); ctx.closePath(); ctx.fill();
  ctx.restore();
}
function iconLines(x, y, s, color) {
  for (let i = 0; i < 4; i++) line(x - s * 0.38, y - s * 0.27 + i * s * 0.18, x + s * (i === 3 ? 0.1 : 0.38), y - s * 0.27 + i * s * 0.18, color, s * 0.08);
}
function iconCalc(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = s * 0.08; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.roundRect(x - s * 0.3, y - s * 0.42, s * 0.6, s * 0.84, s * 0.08); ctx.stroke();
  rrect(x - s * 0.19, y - s * 0.3, s * 0.38, s * 0.16, s * 0.03, color);
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) rrect(x - s * 0.19 + c * s * 0.14, y - s * 0.04 + r * s * 0.13, s * 0.09, s * 0.08, s * 0.02, color);
  ctx.restore();
}
// over-ear headphones, line style (band + two filled cups)
function iconHeadphones(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.09; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(x, y + s * 0.06, s * 0.38, Math.PI * 1.05, Math.PI * 1.95); ctx.stroke();
  for (const sx of [-1, 1]) {
    line(x + sx * s * 0.37, y - s * 0.02, x + sx * s * 0.38, y + s * 0.12, color, s * 0.09);
    rrect(x + sx * s * 0.38 - s * 0.11, y + s * 0.06, s * 0.22, s * 0.34, s * 0.09, color);
  }
  ctx.restore();
}
const ICONS = { paper: iconPaper, book: iconBook, bolt: iconBolt, check: iconCheck, note: iconNote, notes: iconNotes,
  heart: iconHeart, play: iconPlay, pause: iconPause, pencil: iconPencil, quiet: iconQuiet, noise: iconNoise,
  speech: (x, y, s, c) => iconBubble(x, y, s, c, 'dots'), lyric: (x, y, s, c) => iconBubble(x, y, s, c, 'note'),
  image: iconImage, lines: iconLines, calc: iconCalc, phones: iconHeadphones };

// ---------- floating music: a lyric bubble (pink, "♪ 啦啦") and an instrumental note (green) ----------
function drawLyricBubble(x, y, o = {}) {
  const { alpha = 1, scale = 1, text = '啦啦', color = LYR, heart = false } = o;
  if (scale < 0.02) return;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(x, y); ctx.scale(scale, scale);
    const tw = measure(text, 34, 900) + 84, h = 58;
    ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 16;
    ctx.beginPath(); ctx.roundRect(-tw / 2, -h / 2, tw, h, 29);
    ctx.moveTo(-tw / 2 + 26, h / 2 - 4); ctx.lineTo(-tw / 2 + 14, h / 2 + 16); ctx.lineTo(-tw / 2 + 46, h / 2 - 4);
    ctx.fillStyle = color; ctx.fill(); ctx.restore();
    if (heart) iconHeart(-tw / 2 + 32, 2, 34, '#5a0f2c');
    else iconNote(-tw / 2 + 32, 0, 38, '#5a0f2c');
    txt(text, 18, 1, { size: 34, weight: 900, color: '#5a0f2c', align: 'center' });
    ctx.restore();
  });
}
function drawFloatNote(x, y, s, o = {}) {
  const { alpha = 1, color = INST, rot = 0, beamed = false } = o;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
    ctx.shadowColor = color; ctx.shadowBlur = 14;
    (beamed ? iconNotes : iconNote)(0, 0, s, color);
    ctx.restore();
  });
}
// a burst ring where a bubble pops
function popRing(x, y, p, color = LYR) {
  if (p <= 0 || p >= 1) return;
  withAlpha(1 - p, () => {
    circle(x, y, 14 + 40 * EASE.out(p), null, color, 4 * (1 - p) + 1);
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * TAU + 0.4, r = 24 + 36 * EASE.out(p);
      circle(x + Math.cos(a) * r, y + Math.sin(a) * r, 4 * (1 - p), color);
    }
  });
}

// ---------- a word being memorised (cream chip) ----------
function drawWordChip(x, y, word, o = {}) {
  const { alpha = 1, scale = 1, rot = 0 } = o;
  if (scale < 0.02) return;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(scale, scale);
    const tw = measure(word, 34, 900) + 32;
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 10; ctx.shadowOffsetY = 4;
    rrect(-tw / 2, -27, tw, 54, 14, PAPER); ctx.restore();
    txt(word, 0, 1, { size: 34, weight: 900, color: PAPER_INK, align: 'center' });
    ctx.restore();
  });
}

// ---------- dictation sheet: 20 ruled lines in two columns; fill = number of words written (fractions = a part-written word) ----------
const SHEET = { w: 300, h: 186 };
function handwriting(x, y, len, color, seed) {
  if (len < 1) return;
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x, y);
  for (let d = 4; d <= len; d += 4) {
    const k = d / 4 + seed * 3.7;
    ctx.lineTo(x + d, y + Math.sin(k * 1.9) * 3.2 + Math.sin(k * 0.7 + seed) * 1.4 - (Math.floor(k) % 5 === 0 ? 2.5 : 0));
  }
  ctx.stroke(); ctx.restore();
}
function drawSheet(cx, cy, fill, o = {}) {
  const { alpha = 1, sx = 1, accent = COL.cyan, glow = 0, name = 'sheet' } = o;
  if (sx < 0.02) return;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(cx, cy); ctx.scale(sx, 1);
    const { w, h } = SHEET;
    ctx.save(); ctx.shadowColor = glow > 0 ? accent : 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 18 + 22 * glow; ctx.shadowOffsetY = glow > 0 ? 0 : 6;
    rrect(-w / 2, -h / 2, w, h, 12, PAPER); ctx.restore();
    lintPanel(name, -w / 2, -h / 2, w / 2, h / 2);
    rrect(-w / 2, -h / 2, w, 12, [12, 12, 0, 0], accent);
    const colW = (w - 48) / 2, top = -h / 2 + 34, gap = (h - 46) / 10;
    for (let c = 0; c < 2; c++) for (let r = 0; r < 10; r++) {
      const lx = -w / 2 + 16 + c * (colW + 16), ly = top + r * gap;
      line(lx, ly + 7, lx + colW, ly + 7, 'rgba(110,122,156,0.32)', 1.5);
      const p = clamp(fill - (c * 10 + r));
      if (p > 0) handwriting(lx + 4, ly + 1, (colW - 10) * p, '#22305a', c * 10 + r);
    }
    ctx.restore();
  });
}

// ---------- player bar (the opening's status line): play button, label rolling between steps, progress line ----------
// items: [{ spans: [{s, color}], icon }]; idx float rolls from floor(idx) to ceil(idx); prog 0..1 of the current step
function drawPlayerBar(cx, cy, items, idx, prog, o = {}) {
  const { alpha = 1, flash = 0 } = o;
  const i0 = Math.floor(idx), i1 = Math.min(items.length - 1, i0 + 1), p = idx - i0;
  const wOf = (it) => richWidth(it.spans, 36, 900) + 150;
  const w = lerp(wOf(items[i0]), wOf(items[i1]), EASE.inOut(p)), h = 72;
  withAlpha(alpha, () => {
    ctx.save();
    ctx.shadowColor = flash > 0 ? COL.cream : 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 16 + 30 * flash;
    rrect(cx - w / 2, cy - h / 2, w, h, 20, `rgba(12,24,54,${0.92})`, `rgba(243,238,227,${0.42 + flash * 0.45})`, 2.5);
    ctx.restore();
    lintPanel('player', cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2);
    const bx = cx - w / 2 + 40;
    ctx.save(); ctx.beginPath(); ctx.roundRect(cx - w / 2, cy - h / 2, w, h, 20); ctx.clip();
    const drawItem = (it, dy, a) => withAlpha(a, () => {
      circle(bx, cy - 4 + dy, 22, COL.cream);
      ICONS[it.icon](bx + (it.icon === 'play' ? 2 : 0), cy - 4 + dy, it.icon === 'note' ? 30 : 26, '#0b1736');
      rich(it.spans, bx + 40, cy - 6 + dy, { size: 36, weight: 900 });
    });
    if (p <= 0.001) drawItem(items[i0], 0, 1);
    else { const e = EASE.inOut(p); drawItem(items[i0], -e * h, 1 - e); drawItem(items[i1], (1 - e) * h, e); }
    ctx.restore();
    const lx0 = bx + 40, lx1 = cx + w / 2 - 26, ly = cy + 24;
    line(lx0, ly, lx1, ly, 'rgba(200,212,236,0.22)', 4);
    if (prog > 0) { line(lx0, ly, lerp(lx0, lx1, prog), ly, COL.cream, 4); circle(lerp(lx0, lx1, prog), ly, 5.5, COL.cream); }
  });
}

// ---------- playlist row (the three steps): album square with the number, title, progress line ----------
const TRACK = { w: 540, h: 98 };
function drawTrackRow(x, y, n, title, color, o = {}) {
  const { alpha = 1, scale = 1, hi = 0, prog = 0 } = o;
  if (alpha <= 0.001 || scale <= 0.001) return;
  const { w, h } = TRACK;
  withAlpha(alpha, () => withScale(x + w / 2, y, scale, () => {
    ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 10 + hi * 26;
    rrect(x, y - h / 2, w, h, 20, 'rgba(12,26,58,0.92)', rgba(color, 0.5 + 0.45 * hi), 2.5);
    ctx.restore();
    lintPanel('track' + n, x, y - h / 2, x + w, y + h / 2);
    const a = 74, ax = x + 12, ay = y - a / 2;
    const g = ctx.createLinearGradient(ax, ay, ax + a, ay + a);
    g.addColorStop(0, rgba(color, 1)); g.addColorStop(1, lerpColor(color, '#0b1736', 0.35));
    rrect(ax, ay, a, a, 14, g);
    txt(String(n), ax + a / 2, ay + a / 2 + 2, { size: 46, weight: 800, fam: 'mono', color: '#0b1736', align: 'center' });
    const tx = ax + a + 22;
    txt(title, tx, y - 9, { size: 42, weight: 900, color: COL.cream });
    line(tx, y + 30, x + w - 26, y + 30, 'rgba(200,212,236,0.2)', 4);
    if (prog > 0) line(tx, y + 30, lerp(tx, x + w - 26, prog), y + 30, color, 4);
  }));
}

// ---------- the boy's phone on his desk (kid-local coords, desk top at y = -3); mode: lyrics | fave | inst | off ----------
const MODE_COL = { lyrics: LYR, fave: LYR, inst: INST, off: '#6b7795' };
function drawDeskPhoneLocal(x, mode, o = {}) {
  const { glow = 0, vol = 1 } = o;
  const w = 60, h = 98, y0 = -3 - h, c = MODE_COL[mode];
  ctx.beginPath(); ctx.moveTo(x - 8, -3); ctx.lineTo(x + 30, -3); ctx.lineTo(x + 18, y0 + 40); ctx.closePath();
  ctx.fillStyle = '#39445f'; ctx.fill();
  ctx.save(); if (glow > 0) { ctx.shadowColor = c; ctx.shadowBlur = 24 * glow; }
  rrect(x - w / 2, y0, w, h, 11, '#1a2340', '#5d6b93', 2); ctx.restore();
  rrect(x - w / 2 + 5, y0 + 6, w - 10, h - 14, 7, '#0c1430');
  rrect(x - 17, y0 + 14, 34, 34, 7, c);
  if (mode === 'inst') iconNote(x, y0 + 31, 26, '#0b1736');
  else if (mode === 'fave') iconHeart(x, y0 + 32, 26, '#5a0f2c');
  else if (mode === 'lyrics') iconBubble(x, y0 + 31, 28, '#5a0f2c', 'note');
  else iconPause(x, y0 + 31, 22, '#0b1736');
  // volume: a short line that empties when he turns it down
  line(x - 18, y0 + 64, x + 18, y0 + 64, 'rgba(200,212,236,0.25)', 4);
  if (mode !== 'off') line(x - 18, y0 + 64, x - 18 + 36 * vol, y0 + 64, c, 4);
  (mode === 'off' ? iconPlay : iconPause)(x, y0 + 80, 14, COL.cream);
}
// the girl's desk: a mug of water
function drawMugLocal(x) {
  rrect(x - 22, -46, 44, 43, [6, 6, 12, 12], '#e7ecf6');
  ctx.save(); ctx.strokeStyle = '#e7ecf6'; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(x + 24, -26, 11, -1.3, 1.3); ctx.stroke(); ctx.restore();
  rrect(x - 17, -40, 34, 8, 4, 'rgba(110,180,230,0.6)');
}
// a notebook on the desk (kid-local coords) for the dictation
function drawNotebookLocal(x, y) {
  ctx.save(); ctx.translate(x, y);
  ctx.beginPath(); ctx.moveTo(-70, 0); ctx.lineTo(70, 0); ctx.lineTo(58, -14); ctx.lineTo(-58, -14); ctx.closePath();
  ctx.fillStyle = '#f7f4ec'; ctx.fill();
  ctx.strokeStyle = 'rgba(80,110,170,0.7)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(-50, -9); ctx.lineTo(30, -9); ctx.moveTo(-46, -4); ctx.lineTo(10, -4); ctx.stroke();
  ctx.restore();
}

// ---------- small things ----------
function namePlate(cx, cy, s, color, o = {}) {
  const { alpha = 1, size = 34 } = o;
  withAlpha(alpha, () => {
    const w = measure(s, size, 900) + 48, h = size + 26;
    rrect(cx - w / 2, cy - h / 2, w, h, 12, 'rgba(10,20,46,0.82)', rgba(color.startsWith('#') ? color : '#ffffff', 0.7), 2.5);
    txt(s, cx, cy + 1, { size, weight: 900, color, align: 'center' });
  });
}
function sourceNote(s, x, y, o = {}) {
  const { alpha = 1, align = 'left', size = 22 } = o;
  txt(s, x, y, { size, weight: 500, color: 'rgba(181,191,214,0.78)', align, alpha });
}
function dingBurst(x, y, p, o = {}) {
  const { s = '叮', size = 46, color = COL.yellow } = o;
  if (p <= 0 || p >= 1) return;
  const a = p < 0.7 ? 1 : 1 - (p - 0.7) / 0.3;
  const sc = EASE.back(clamp(p / 0.35));
  withAlpha(a, () => {
    ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = 4; ctx.lineCap = 'round';
    for (let i = 0; i < 8; i++) {
      const an = (i / 8) * TAU + 0.2, r0 = 40 + p * 30, r1 = r0 + 18 * (1 - p);
      ctx.beginPath(); ctx.moveTo(x + Math.cos(an) * r0, y + Math.sin(an) * r0); ctx.lineTo(x + Math.cos(an) * r1, y + Math.sin(an) * r1); ctx.stroke();
    }
    ctx.restore();
    withScale(x, y, sc, () => txt(s, x, y, { size, weight: 900, color, align: 'center', glow: 18 }));
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
function crossMark(x, y, r, color = LYR) {
  circle(x, y, r, color);
  line(x - r * 0.38, y - r * 0.38, x + r * 0.38, y + r * 0.38, '#0d1838', Math.max(3, r * 0.17));
  line(x + r * 0.38, y - r * 0.38, x - r * 0.38, y + r * 0.38, '#0d1838', Math.max(3, r * 0.17));
}
function okMark(x, y, r, p = 1, color = COL.yellow) {
  ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 18; circle(x, y, r, color); ctx.restore();
  checkBadge(x, y, r, { color: '#0d1838', p, lw: Math.max(3, r * 0.16) });
}
// "about the same": a round badge with ≈
function aboutMark(x, y, r, color = INST) {
  ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 16; circle(x, y, r, color); ctx.restore();
  for (const dy of [-0.18, 0.18]) {
    ctx.save(); ctx.strokeStyle = '#0d1838'; ctx.lineWidth = Math.max(3, r * 0.16); ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x - r * 0.42, y + dy * r);
    ctx.bezierCurveTo(x - r * 0.18, y + dy * r - r * 0.2, x + r * 0.08, y + dy * r + r * 0.2, x + r * 0.42, y + dy * r);
    ctx.stroke(); ctx.restore();
  }
}
// a flip around the vertical axis: face a -> b over [t0, t0 + d] beats
function flipFace(bt, t0, d, a, b) {
  const p = seg(bt, t0, t0 + d);
  return { face: p < 0.5 ? a : b, sx: Math.abs(Math.cos(Math.PI * p)) };
}
