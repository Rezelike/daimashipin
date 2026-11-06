// props.js — this episode's props (all new: day plates, flags, the 不用想就会做 bar, signposts, hanging road signs, cards,
// footprints). Small helpers (sourceNote, dingBurst, sparkle, marks, a few line icons) are copied from bedtime_words.
// Not used here (plan rule): the earlier panels, outlined numbers, bars/pillars, clocks, timer ring, calendar, list table,
// word-card grid, windows.

// ---------- small helpers (from bedtime_words) ----------
function sourceNote(s, x, y, o = {}) {
  const { alpha = 1, align = 'left', size = 22, color = 'rgba(190,198,222,0.8)' } = o;
  txt(s, x, y, { size, weight: 500, color, align, alpha });
}
function iconStar(x, y, r, fill) {
  ctx.save(); ctx.beginPath();
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + (i * Math.PI) / 5, rr = i % 2 === 0 ? r : r * 0.45;
    const px = x + Math.cos(a) * rr, py = y + Math.sin(a) * rr;
    i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
  }
  ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); ctx.restore();
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
function crossMark(x, y, r, color) {
  circle(x, y, r, color);
  line(x - r * 0.38, y - r * 0.38, x + r * 0.38, y + r * 0.38, '#0d1838', 4.5);
  line(x + r * 0.38, y - r * 0.38, x - r * 0.38, y + r * 0.38, '#0d1838', 4.5);
}
function okMark(x, y, r, p = 1) {
  ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 18; circle(x, y, r, COL.yellow); ctx.restore();
  checkBadge(x, y, r, { color: '#0d1838', p, lw: 4 });
}
function iconSun(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.09; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(x, y, s * 0.2, 0, TAU); ctx.stroke();
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * TAU;
    ctx.beginPath(); ctx.moveTo(x + Math.cos(a) * s * 0.31, y + Math.sin(a) * s * 0.31);
    ctx.lineTo(x + Math.cos(a) * s * 0.44, y + Math.sin(a) * s * 0.44); ctx.stroke();
  }
  ctx.restore();
}
// a small mountain peak with a flag: "the top" (at the end of the 不用想就会做 bar)
function iconPeak(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = s * 0.09; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.48, y + s * 0.34); ctx.lineTo(x - s * 0.08, y - s * 0.22); ctx.lineTo(x + s * 0.1, y + s * 0.02);
  ctx.lineTo(x + s * 0.22, y - s * 0.1); ctx.lineTo(x + s * 0.48, y + s * 0.34); ctx.closePath(); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x - s * 0.08, y - s * 0.22); ctx.lineTo(x - s * 0.08, y - s * 0.5); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x - s * 0.08, y - s * 0.5); ctx.lineTo(x + s * 0.18, y - s * 0.42); ctx.lineTo(x - s * 0.08, y - s * 0.34); ctx.closePath(); ctx.fill();
  ctx.restore();
}

// ---------- day plates along the road (the hook): a thin post with a glowing number ----------
function drawDayPlate(d, label, o = {}) {
  const { alpha = 1, lit = 0 } = o;
  const z = zoomK(), x = sx(d), y = sy(d);
  if (x < -80 || x > W + 80 || alpha <= 0.001) return;
  withAlpha(alpha, () => {
    const ph = 118 * z, pw = 72 * z, th = 44 * z;
    line(x, y - 2, x, y - ph, 'rgba(160,175,210,0.55)', 4 * z);
    ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = (8 + 16 * lit) * z;
    rrect(x - pw / 2, y - ph - th, pw, th, 8 * z, lit ? 'rgba(63,203,232,0.28)' : 'rgba(12,24,52,0.92)', rgba(COL.cyan, 0.75 + 0.25 * lit), 2.5 * z);
    ctx.restore();
    txt(label, x, y - ph - th / 2 + 1, { size: 34 * z, weight: 800, fam: 'mono', color: lit ? COL.cyanHi : COL.cream, align: 'center' });
    lintPanel('plate ' + label, x - pw / 2, y - ph - th, x + pw / 2, y - 2);
  });
}

// ---------- flags on the road: a pole and a cloth with text ----------
// o.side: 1 = cloth to the right of the pole, -1 = to the left; o.h: pole height (px at zoom 1); o.size: text size
function drawFlag(d, text, o = {}) {
  const { alpha = 1, side = 1, h = 300, size = 50, color = COL.yellow, ink = '#14100a', glow = 1, wave = 0, t = 0, scaleText = true } = o;
  const z = o.zoom ?? zoomK(), x = sx(d), y = sy(d);
  if (alpha <= 0.001 || x < -500 || x > W + 500) return null;
  const ph = h * z, fs = scaleText ? size * z : size;
  const tw = measure(text, fs, 900) + 44 * (scaleText ? z : 1), fh = fs + 34 * (scaleText ? z : 1);
  const top = y - ph, x0 = side > 0 ? x + 2 : x - 2 - tw;
  withAlpha(alpha, () => {
    line(x, y, x, top - 6 * z, '#c9d2ea', 5 * z);
    circle(x, top - 8 * z, 6 * z, COL.cream);
    // the cloth ripples slowly (its own motion, not on the beat)
    ctx.save();
    ctx.shadowColor = color; ctx.shadowBlur = 22 * glow * z;
    ctx.beginPath();
    const N = 12, amp = 5 * z * (0.6 + 0.4 * wave);
    for (let i = 0; i <= N; i++) {
      const u = i / N, xx = x0 + tw * u, dy = Math.sin(u * 5 + t * 2.2) * amp * (side > 0 ? u : 1 - u);
      i ? ctx.lineTo(xx, top + dy) : ctx.moveTo(xx, top + dy);
    }
    for (let i = N; i >= 0; i--) {
      const u = i / N, xx = x0 + tw * u, dy = Math.sin(u * 5 + t * 2.2) * amp * (side > 0 ? u : 1 - u);
      ctx.lineTo(xx, top + fh + dy);
    }
    ctx.closePath(); ctx.fillStyle = color; ctx.fill();
    ctx.restore();
    txt(text, x0 + tw / 2, top + fh / 2 + 1, { size: fs, weight: 900, color: ink, align: 'center' });
    lintPanel('flag ' + text, x0, top - 14 * z, x0 + tw, top + fh + 6 * z);
  });
  return { x0, x1: x0 + tw, top, bottom: top + fh, poleX: x, base: y };
}

// ---------- the 不用想就会做 bar above his head (his automaticity as a share of his own top) ----------
function drawHabitBar(cx, y, fill, o = {}) {
  const { alpha = 1, w = 330, flash = 0, label = '不用想就会做', note = null, noteColor = COL.yellow, dip = 0 } = o;
  if (alpha <= 0.001) return;
  withAlpha(alpha, () => {
    const x0 = cx - w / 2, h = 22;
    txt(label, x0, y - 38, { size: 34, weight: 900, color: COL.cream });
    rrect(x0, y - h / 2, w, h, h / 2, 'rgba(8,14,34,0.85)', 'rgba(243,238,227,0.55)', 2.5);
    const fw = Math.max(h, w * clamp(fill));
    const g = ctx.createLinearGradient(x0, 0, x0 + fw, 0);
    g.addColorStop(0, '#d98a1e'); g.addColorStop(1, COL.yellowHi);
    ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 14 + 24 * flash;
    rrect(x0 + 3, y - h / 2 + 3, fw - 6, h - 6, (h - 6) / 2, g); ctx.restore();
    if (dip > 0) rrect(x0 + fw - 6, y - h / 2 + 3, Math.max(3, dip), h - 6, 2, COL.pink);
    iconPeak(x0 + w + 30, y - 4, 44, COL.cream);
    if (note) txt(note, x0 + w + 64, y, { size: 36, weight: 900, color: noteColor });
    lintPanel('habit bar', x0, y - 58, x0 + w + 56, y + 14);
  });
}

// ---------- a direction signpost with arrow boards (the answer's ①②③ and, at the top, the summary) ----------
// boards: [{ n, s, at, sub }] ; arrows point right (the way he walks)
function arrowBoard(x, y, w, h, fill, stroke, lw = 3) {
  const tip = h * 0.42;
  ctx.beginPath();
  ctx.moveTo(x, y + 8); ctx.quadraticCurveTo(x, y, x + 8, y);
  ctx.lineTo(x + w - tip, y); ctx.lineTo(x + w, y + h / 2); ctx.lineTo(x + w - tip, y + h);
  ctx.lineTo(x + 8, y + h); ctx.quadraticCurveTo(x, y + h, x, y + h - 8); ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
}
function drawSignpost(x, base, top, boards, bt, o = {}) {
  const { alpha = 1, size = 44, bw = 470, bh = 88, gap = 22, lit = () => 0, numColor = COL.yellow } = o;
  if (alpha <= 0.001) return;
  withAlpha(alpha, () => {
    rrect(x - 7, top - 10, 14, base - top + 10, 5, '#2a3150');
    line(x + 3, top - 6, x + 3, base, 'rgba(255,200,150,0.35)', 2);
    boards.forEach((b, i) => {
      const a = popA(bt, b.at, 0.3), sc = popS(bt, b.at, 0.6);
      if (a <= 0) return;
      const y = top + i * (bh + gap), L = lit(i);
      withAlpha(a, () => withScale(x, y + bh / 2, 0.6 + 0.4 * sc, () => {
        ctx.save(); ctx.shadowColor = L > 0 ? COL.yellow : 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 18 + 20 * L;
        arrowBoard(x - 24, y, bw, bh, lerpColor('#14204a', '#3a2c10', L * 0.6), lerpColor('#c9d2ea', COL.yellow, L), 3);
        ctx.restore();
        circle(x + 22, y + bh / 2, 26, numColor);
        txt(String(b.n), x + 22, y + bh / 2 + 1, { size: 34, weight: 800, fam: 'mono', color: '#0b1736', align: 'center' });
        txt(b.s, x + 62, y + bh / 2 + 1, { size, weight: 900, color: L > 0.5 ? COL.yellowHi : COL.cream });
      }));
      lintPanel('board ' + b.s, x - 24, y, x - 24 + bw, y + bh);
    });
  });
}
