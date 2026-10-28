// props.js — clocks, meters, pills, HUD pieces, icons
// ---------- icons (line style, centred at x,y, size s) ----------
function iconClock(x, y, s, color, hours = 3, minutes = 0) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.11; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(x, y, s * 0.45, 0, TAU); ctx.stroke();
  const ha = ((hours % 12) + minutes / 60) / 12 * TAU - Math.PI / 2, ma = minutes / 60 * TAU - Math.PI / 2;
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(ha) * s * 0.22, y + Math.sin(ha) * s * 0.22);
  ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(ma) * s * 0.32, y + Math.sin(ma) * s * 0.32); ctx.stroke();
  ctx.restore();
}
function iconPaper(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.1; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.strokeRect(x - s * 0.32, y - s * 0.42, s * 0.64, s * 0.84);
  for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.moveTo(x - s * 0.18, y - s * 0.2 + i * s * 0.2); ctx.lineTo(x + s * 0.18, y - s * 0.2 + i * s * 0.2); ctx.stroke(); }
  ctx.restore();
}
function iconCalendar(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.1; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.strokeRect(x - s * 0.42, y - s * 0.32, s * 0.84, s * 0.74);
  ctx.beginPath(); ctx.moveTo(x - s * 0.42, y - s * 0.08); ctx.lineTo(x + s * 0.42, y - s * 0.08);
  ctx.moveTo(x - s * 0.2, y - s * 0.46); ctx.lineTo(x - s * 0.2, y - s * 0.24);
  ctx.moveTo(x + s * 0.2, y - s * 0.46); ctx.lineTo(x + s * 0.2, y - s * 0.24); ctx.stroke();
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
function iconBell(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.1; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(x - s * 0.36, y + s * 0.2); ctx.quadraticCurveTo(x - s * 0.3, y + s * 0.1, x - s * 0.3, y - s * 0.08);
  ctx.quadraticCurveTo(x - s * 0.28, y - s * 0.38, x, y - s * 0.38); ctx.quadraticCurveTo(x + s * 0.28, y - s * 0.38, x + s * 0.3, y - s * 0.08);
  ctx.quadraticCurveTo(x + s * 0.3, y + s * 0.1, x + s * 0.36, y + s * 0.2); ctx.closePath();
  ctx.moveTo(x - s * 0.08, y + s * 0.32); ctx.lineTo(x + s * 0.08, y + s * 0.32);
  ctx.stroke(); ctx.restore();
}
function iconZz(x, y, s, color) {
  txt('Z', x - s * 0.12, y + s * 0.08, { size: s * 0.62, weight: 800, fam: 'mono', color, align: 'center' });
  txt('z', x + s * 0.24, y - s * 0.2, { size: s * 0.42, weight: 800, fam: 'mono', color, align: 'center' });
}
function iconAlarm(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.09; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(x, y + s * 0.05, s * 0.33, 0, TAU); ctx.stroke();
  ctx.beginPath(); ctx.arc(x - s * 0.3, y - s * 0.3, s * 0.12, Math.PI * 0.9, Math.PI * 1.9); ctx.stroke();
  ctx.beginPath(); ctx.arc(x + s * 0.3, y - s * 0.3, s * 0.12, Math.PI * 1.1, Math.PI * 2.1); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x, y + s * 0.05); ctx.lineTo(x, y - s * 0.12); ctx.moveTo(x, y + s * 0.05); ctx.lineTo(x + s * 0.12, y + s * 0.12); ctx.stroke();
  ctx.restore();
}
function iconMoonX(x, y, s, color) {
  // crescent = disc minus offset disc (clip, so nothing behind gets erased)
  ctx.save();
  ctx.beginPath(); ctx.rect(x - s, y - s, s * 2, s * 2);
  ctx.arc(x + s * 0.17, y - s * 0.12, s * 0.3, 0, TAU, true);
  ctx.clip('evenodd');
  ctx.fillStyle = color;
  ctx.beginPath(); ctx.arc(x, y, s * 0.36, 0, TAU); ctx.fill();
  ctx.restore();
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
function iconBrain(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.09; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath();
  ctx.arc(x - s * 0.16, y - s * 0.12, s * 0.2, Math.PI * 0.8, Math.PI * 1.9);
  ctx.arc(x + s * 0.16, y - s * 0.12, s * 0.2, Math.PI * 1.1, Math.PI * 0.2);
  ctx.arc(x + s * 0.14, y + s * 0.14, s * 0.2, Math.PI * 1.7, Math.PI * 0.6);
  ctx.arc(x - s * 0.14, y + s * 0.14, s * 0.2, Math.PI * 0.4, Math.PI * 1.3);
  ctx.closePath();
  ctx.moveTo(x, y - s * 0.3); ctx.lineTo(x, y + s * 0.32);
  ctx.stroke(); ctx.restore();
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
function iconCheck(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.12; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.3, y + s * 0.02); ctx.lineTo(x - s * 0.08, y + s * 0.24); ctx.lineTo(x + s * 0.32, y - s * 0.22);
  ctx.stroke(); ctx.restore();
}
const ICONS = { clock: iconClock, paper: iconPaper, calendar: iconCalendar, book: iconBook, bell: iconBell, zz: iconZz, alarm: iconAlarm, moon: iconMoonX, bolt: iconBolt, brain: iconBrain, sun: iconSun, check: iconCheck };

// ---------- window on the back wall (bedtime_words): day = 1 morning sun, 0 night moon + stars ----------
const WIN_STARS = Array.from({ length: 9 }, (_, i) => [((i * 0.37 + 0.11) % 1), ((i * 0.53 + 0.07) % 0.62)]);
function drawWindow(cx, cy, w, h, day, o = {}) {
  const { alpha = 1, t = 0 } = o;
  withAlpha(alpha, () => {
    const x = cx - w / 2, y = cy - h / 2;
    // light spilling onto the wall
    const glow = ctx.createRadialGradient(cx, cy, 20, cx, cy, w * 1.15);
    glow.addColorStop(0, day > 0.5 ? `rgba(255,214,150,${0.16 * day})` : `rgba(120,160,255,${0.12 * (1 - day)})`);
    glow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = glow; ctx.fillRect(cx - w * 1.2, cy - h * 1.2, w * 2.4, h * 2.4);
    ctx.save();
    ctx.beginPath(); ctx.roundRect(x, y, w, h, 10); ctx.clip();
    const g = ctx.createLinearGradient(0, y, 0, y + h);
    g.addColorStop(0, lerpColor('#0a1534', '#5fb0e6', day));
    g.addColorStop(1, lerpColor('#1d2d63', '#ffd7a0', day));
    ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
    // stars
    for (const [sx, sy] of WIN_STARS) {
      const tw = 0.6 + 0.4 * Math.sin(t * 2.1 + sx * 17);
      circle(x + 14 + sx * (w - 28), y + 14 + sy * (h - 28), 2.2, `rgba(255,255,255,${(1 - day) * 0.85 * tw})`);
    }
    // sun rises from below as day -> 1, moon sinks
    const sunY = y + h * 0.36 + (1 - day) * h * 0.75, moonY = y + h * 0.32 + day * h * 0.8;
    ctx.save(); ctx.shadowColor = '#ffd36b'; ctx.shadowBlur = 30;
    circle(cx + w * 0.08, sunY, w * 0.17, '#ffcf5c'); ctx.restore();
    iconMoonX(cx - w * 0.06, moonY, w * 0.55, '#f4f1ff');
    // hills
    ctx.fillStyle = lerpColor('#0d1a3c', '#4f8f6a', day);
    ctx.beginPath(); ctx.moveTo(x, y + h); ctx.lineTo(x, y + h * 0.8);
    ctx.quadraticCurveTo(x + w * 0.3, y + h * 0.68, x + w * 0.6, y + h * 0.8);
    ctx.quadraticCurveTo(x + w * 0.82, y + h * 0.88, x + w, y + h * 0.76); ctx.lineTo(x + w, y + h); ctx.closePath(); ctx.fill();
    ctx.restore();
    // frame, mullions, sill
    rrect(x, y, w, h, 10, null, '#c4cfe6', 7);
    line(cx, y + 4, cx, y + h - 4, '#c4cfe6', 6);
    line(x + 4, cy, x + w - 4, cy, '#c4cfe6', 6);
    rrect(x - 16, y + h - 2, w + 32, 16, 5, '#9aa8c6');
  });
}

// ---------- wall clock ----------
// hours: float (e.g. 15.0 = 3 pm); spin blur when spinning fast
function drawWallClock(x, y, r, hours, o = {}) {
  const { alpha = 1, glow = 0, scale = 1, blur = 0 } = o;
  withAlpha(alpha, () => withScale(x, y, scale, () => {
    ctx.save();
    if (glow > 0) { ctx.shadowColor = COL.yellow; ctx.shadowBlur = 40 * glow; }
    circle(x, y, r, 'rgba(10,22,50,0.92)', glow > 0 ? lerpColor(COL.cyan, COL.yellow, glow) : COL.cyan, 5);
    ctx.restore();
    circle(x, y, r - 9, null, 'rgba(63,203,232,0.22)', 2);
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * TAU, big = i % 3 === 0;
      line(x + Math.cos(a) * (r - (big ? 22 : 17)), y + Math.sin(a) * (r - (big ? 22 : 17)),
        x + Math.cos(a) * (r - 12), y + Math.sin(a) * (r - 12), big ? COL.cream : 'rgba(243,238,227,0.55)', big ? 4 : 2.5);
    }
    const m = (hours % 1) * 60;
    const ha = (((hours % 12) + 12) % 12) / 12 * TAU - Math.PI / 2;
    const ma = (m / 60) * TAU - Math.PI / 2;
    if (blur > 0) {
      ctx.save(); ctx.globalAlpha *= 0.25;
      for (let k = 1; k <= 4; k++) {
        const a = ma - k * blur * 0.12;
        line(x, y, x + Math.cos(a) * r * 0.72, y + Math.sin(a) * r * 0.72, COL.cream, 5);
      }
      ctx.restore();
    }
    line(x, y, x + Math.cos(ha) * r * 0.45, y + Math.sin(ha) * r * 0.45, COL.cream, 8);
    line(x, y, x + Math.cos(ma) * r * 0.72, y + Math.sin(ma) * r * 0.72, COL.cream, 5);
    circle(x, y, 7, COL.yellow);
  }));
}

// ---------- memory meter (vertical bar) ----------
// num: optional count shown beside the top of the fill ({ s, side: -1 left / 1 right, alpha, color })
function drawMeter(x, bottom, w, hMax, level, o = {}) {
  const { color = COL.cyan, colorHi = COL.cyanHi, alpha = 1, label = '记住了', labelAlpha = 1, q = 0, glow = 1, num = null } = o;
  if (num && num.alpha > 0.001) withAlpha(alpha * num.alpha, () => {
    const ty = bottom - Math.max(0.12, level) * hMax + 4;
    txt(num.s, x + (num.side || -1) * (w / 2 + 14), ty, { size: num.size || 44, weight: 800, fam: 'mono', color: num.color || color, align: (num.side || -1) < 0 ? 'right' : 'left', glow: 10 });
  });
  withAlpha(alpha, () => {
    const top = bottom - hMax;
    rrect(x - w / 2, top, w, hMax, 12, 'rgba(255,255,255,0.045)', 'rgba(200,215,240,0.28)', 2);
    if (level > 0.003) {
      const hh = hMax * level;
      const g = ctx.createLinearGradient(0, bottom - hh, 0, bottom);
      g.addColorStop(0, colorHi); g.addColorStop(1, color);
      ctx.save();
      ctx.shadowColor = color; ctx.shadowBlur = 24 * glow;
      rrect(x - w / 2 + 5, bottom - hh + 5 - 5 * 0, w - 10, Math.max(6, hh - 5), 8, g);
      ctx.restore();
    }
    if (label) txt(label, x, top - 24, { size: 26, weight: 700, color: COL.grayHi, align: 'center', alpha: labelAlpha });
    if (q > 0.01) txt('?', x, bottom - hMax / 2, { size: 64, weight: 900, color: COL.cream, align: 'center', alpha: q * 0.55 });
  });
}
// dashed baseline across, with centred label
function drawRestLine(x1, x2, y, p, o = {}) {
  const { label = '只休息', alpha = 1, labelX = (x1 + x2) / 2 } = o;
  if (p <= 0) return;
  withAlpha(alpha, () => {
    const lw = measure(label, 28, 700) + 36;
    const mid = labelX;
    const half = ((x2 - x1) / 2) * EASE.out(p);
    const a = mid - half, b = mid + half;
    ctx.save(); ctx.setLineDash([12, 9]); ctx.strokeStyle = 'rgba(181,191,214,0.85)'; ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(a, y); ctx.lineTo(Math.max(a, mid - lw / 2), y);
    ctx.moveTo(Math.min(b, mid + lw / 2), y); ctx.lineTo(b, y);
    ctx.stroke(); ctx.restore();
    txt(label, mid, y, { size: 28, weight: 700, color: COL.grayHi, align: 'center', alpha: clamp(p * 2) });
  });
}

// ---------- pill (time badge) with flip between labels ----------
// items: [{s, icon}] ; idx float: transition from floor(idx) to ceil(idx)
function drawPill(cx, cy, items, idx, o = {}) {
  const { alpha = 1, flash = 0 } = o;
  const i0 = Math.floor(idx), i1 = Math.min(items.length - 1, i0 + 1), p = idx - i0;
  const wOf = (it) => measure(it.s, 36, 700) + 120;
  const w = lerp(wOf(items[i0]), wOf(items[i1]), EASE.inOut(p)), h = 66;
  withAlpha(alpha, () => {
    ctx.save();
    if (flash > 0) { ctx.shadowColor = COL.cream; ctx.shadowBlur = 30 * flash; }
    rrect(cx - w / 2, cy - h / 2, w, h, h / 2, `rgba(255,255,255,${0.06 + flash * 0.1})`, `rgba(243,238,227,${0.45 + flash * 0.4})`, 2.5);
    ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.roundRect(cx - w / 2, cy - h / 2, w, h, h / 2); ctx.clip();
    const drawItem = (it, dy, a) => withAlpha(a, () => {
      const tw = measure(it.s, 36, 700);
      const x0 = cx - (tw + 46) / 2;
      ICONS[it.icon](x0 + 16, cy + dy, 32, COL.cream, 3, 0);
      txt(it.s, x0 + 46, cy + dy + 1, { size: 36, weight: 700, color: COL.cream });
    });
    if (p <= 0.001) drawItem(items[i0], 0, 1);
    else {
      const e = EASE.inOut(p);
      drawItem(items[i0], -e * h, 1 - e);
      drawItem(items[i1], (1 - e) * h, e);
    }
    ctx.restore();
  });
}

// ---------- name plate on desk front ----------
function namePlate(cx, cy, s, color, o = {}) {
  const { alpha = 1, size = 34, prefix = '' } = o;
  withAlpha(alpha, () => {
    const w = measure(prefix + s, size, 900) + 48, h = size + 26;
    rrect(cx - w / 2, cy - h / 2, w, h, 12, 'rgba(10,20,46,0.82)', rgba(color.startsWith('#') ? color : '#ffffff', 0.7), 2.5);
    txt(prefix + s, cx, cy + 1, { size, weight: 900, color, align: 'center' });
  });
}

// ---------- tag chip (S1) ----------
function drawTag(cx, cy, num, s, o = {}) {
  const { alpha = 1, scale = 1, hi = 0, color = COL.cyan } = o;
  if (alpha <= 0.001 || scale <= 0.001) return;
  withAlpha(alpha, () => withScale(cx, cy, scale, () => {
    const tw = measure(s, 42, 900);
    const w = tw + 112, h = 84;
    ctx.save();
    ctx.shadowColor = color; ctx.shadowBlur = 18 + hi * 26;
    rrect(cx - w / 2, cy - h / 2, w, h, 20, 'rgba(12,26,58,0.92)', color, 3);
    ctx.restore();
    circle(cx - w / 2 + 44, cy, 22, color);
    txt(String(num), cx - w / 2 + 44, cy + 1, { size: 28, weight: 800, fam: 'mono', color: '#0b1736', align: 'center' });
    txt(s, cx - w / 2 + 80, cy + 1, { size: 42, weight: 900, color: COL.cream });
  }));
}

// ---------- HUD panel with corner brackets ----------
function hudPanel(x, y, w, h, p = 1, alpha = 1) {
  if (p <= 0) return;
  withAlpha(alpha, () => {
    const e = EASE.out(p);
    withAlpha(e, () => rrect(x, y, w, h, 6, 'rgba(14,30,66,0.45)', 'rgba(63,203,232,0.2)', 1.5));
    const L = 44 * e;
    ctx.save(); ctx.strokeStyle = COL.cyan; ctx.lineWidth = 3.5; ctx.lineCap = 'square';
    ctx.shadowColor = COL.cyan; ctx.shadowBlur = 8;
    const corners = [[x, y, 1, 1], [x + w, y, -1, 1], [x, y + h, 1, -1], [x + w, y + h, -1, -1]];
    for (const [cx, cy, sx, sy] of corners) {
      ctx.beginPath(); ctx.moveTo(cx + sx * L, cy); ctx.lineTo(cx, cy); ctx.lineTo(cx, cy + sy * L); ctx.stroke();
    }
    ctx.restore();
  });
}

// ---------- section header (outlined number + title + mono subtitle) ----------
function sectionHeader(num, title, sub, o = {}) {
  const { alpha = 1, dy = 0, numColor = COL.cyan, p = 1, bt = 0, typeP = 1 } = o;
  withAlpha(alpha, () => {
    const y = 132 + dy;
    if (num) txt(num, 140, y + 8, { size: 104, weight: 800, fam: 'mono', stroke: numColor, lw: 3, glow: 12 });
    const tx = num ? 298 : 140;
    rich(title, tx, y - 6, { size: 60, weight: 900 });
    typeText(sub, typeP, tx + 2, y + 58, { size: 30, weight: 500, fam: 'mono', color: COL.cyan }, bt);
    withAlpha(p, () => line(140, 238 + dy, 140 + 1640 * EASE.out(p), 238 + dy, 'rgba(63,203,232,0.35)', 2));
  });
}
// bullet line with check badge
function bulletLine(spans, sub, o = {}) {
  const { alpha = 1, p = 1, y = 328, typeP = 1, bt = 0, x = 140, textA = null } = o;
  withAlpha(alpha, () => {
    if (p > 0) checkBadge(x + 28, y, 26, { color: COL.cyan, p });
    else circle(x + 28, y, 26, null, 'rgba(63,203,232,0.35)', 3);
    rich(spans, x + 74, y - 2, { size: 54, weight: 900, alpha: textA ?? clamp(p * 1.6) });
    typeText(sub, typeP, x + 76, y + 50, { size: 26, weight: 500, fam: 'mono', color: 'rgba(200,212,236,0.62)' }, bt);
  });
}

// small source / caption text
function sourceNote(s, x, y, o = {}) {
  const { alpha = 1, align = 'left', size = 22 } = o;
  txt(s, x, y, { size, weight: 500, color: 'rgba(181,191,214,0.75)', align, alpha });
}

// "叮" burst
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

// ---------- word cards (bedtime_words opening): each kid's 16 words as a 4x4 grid ----------
const CARD = { w: 62, h: 44, gx: 9, gy: 9, r: 8 };
const CARD_GRID_W = 4 * CARD.w + 3 * CARD.gx, CARD_GRID_H = 4 * CARD.h + 3 * CARD.gy;
function cardCentre(cx, cy, i) {
  const c = i % 4, r = Math.floor(i / 4);
  return [cx - CARD_GRID_W / 2 + CARD.w / 2 + c * (CARD.w + CARD.gx), cy - CARD_GRID_H / 2 + CARD.h / 2 + r * (CARD.h + CARD.gy)];
}
// face: 'blank' (not learned yet) | 'lit' (remembered) | 'lost' (forgotten: "?") | 'half' (left half lit)
function drawWordCard(x, y, face, o = {}) {
  const { sx = 1, color = COL.yellow, colorHi = COL.yellowHi, glow = 1 } = o;
  if (sx < 0.02) return;
  const { w, h, r } = CARD;
  ctx.save();
  ctx.translate(x, y); ctx.scale(sx, 1);
  const lines = (c) => {
    line(-18, -7, 18, -7, c, 5); line(-18, 7, 6, 7, c, 5);
  };
  const litFace = () => {
    const g = ctx.createLinearGradient(0, -h / 2, 0, h / 2);
    g.addColorStop(0, colorHi); g.addColorStop(1, color);
    ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 14 * glow;
    rrect(-w / 2, -h / 2, w, h, r, g); ctx.restore();
    lines('rgba(11,23,54,0.55)');
  };
  const lostFace = () => {
    rrect(-w / 2, -h / 2, w, h, r, 'rgba(255,255,255,0.04)', 'rgba(141,153,181,0.6)', 2);
    txt('?', 0, 1, { size: 32, weight: 900, color: COL.gray, align: 'center' });
  };
  if (face === 'lit') litFace();
  else if (face === 'lost') lostFace();
  else if (face === 'half') {
    // left half still lit, right half empty with a small "?" of its own (a "?" cut in half read as a glitch)
    rrect(-w / 2, -h / 2, w, h, r, 'rgba(255,255,255,0.04)', 'rgba(141,153,181,0.6)', 2);
    txt('?', w / 4, 1, { size: 26, weight: 900, color: COL.gray, align: 'center' });
    ctx.save(); ctx.beginPath(); ctx.rect(-w / 2 - 20, -h / 2 - 20, w / 2 + 20, h + 40); ctx.clip();
    const g = ctx.createLinearGradient(0, -h / 2, 0, h / 2);
    g.addColorStop(0, colorHi); g.addColorStop(1, color);
    ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 14 * glow; rrect(-w / 2, -h / 2, w, h, r, g); ctx.restore();
    line(-18, -7, -6, -7, 'rgba(11,23,54,0.55)', 5); line(-18, 7, -6, 7, 'rgba(11,23,54,0.55)', 5);
    ctx.restore();
    line(0, -h / 2 + 4, 0, h / 2 - 4, 'rgba(243,238,227,0.75)', 2);
  } else {
    rrect(-w / 2, -h / 2, w, h, r, 'rgba(255,255,255,0.05)', 'rgba(200,215,240,0.3)', 2);
    lines('rgba(200,215,240,0.16)');
  }
  ctx.restore();
}
// a card turning from face a to face b over [t0, t0 + d] beats (flip around its vertical axis)
function flipFace(bt, t0, d, a, b) {
  const p = seg(bt, t0, t0 + d);
  return { face: p < 0.5 ? a : b, sx: Math.abs(Math.cos(Math.PI * p)) };
}

// ---------- bedside table + reading lamp (bedtime_words opening); top = table top (screen y), on = 0..1 ----------
function drawBedLamp(x, top, on, o = {}) {
  const { alpha = 1 } = o;
  withAlpha(alpha, () => {
    if (on > 0.01) {
      const g = ctx.createRadialGradient(x, top - 76, 10, x, top - 76, 430);
      g.addColorStop(0, `rgba(255,203,125,${0.32 * on})`);
      g.addColorStop(0.35, `rgba(255,190,110,${0.12 * on})`);
      g.addColorStop(1, 'rgba(255,190,110,0)');
      ctx.fillStyle = g; ctx.fillRect(x - 450, top - 520, 900, 720);
    }
    rrect(x - 48, top, 96, 104, 8, '#6c472f');
    rrect(x - 54, top - 8, 108, 14, 5, '#a9774f');
    line(x - 30, top + 52, x + 30, top + 52, 'rgba(40,24,14,0.6)', 3);
    circle(x, top + 34, 4, '#d9b48a');
    ellipse(x, top - 12, 24, 6, '#3a4766');
    line(x, top - 14, x, top - 56, '#8d99b5', 5);
    if (on > 0.01) {
      ctx.save(); ctx.shadowColor = '#ffd58a'; ctx.shadowBlur = 34 * on;
      ellipse(x, top - 54, 30, 7, rgba('#fff3d0', 0.9 * on)); ctx.restore();
    }
    ctx.beginPath(); ctx.moveTo(x - 42, top - 54); ctx.lineTo(x + 42, top - 54); ctx.lineTo(x + 25, top - 104); ctx.lineTo(x - 25, top - 104); ctx.closePath();
    ctx.fillStyle = lerpColor('#556080', '#ffd58a', on); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.18)'; ctx.lineWidth = 2; ctx.stroke();
  });
}

// ---------- breakfast on the girl's desk (kid-local coords, desk top at y = 0): toast on a plate, a glass of milk ----------
function drawBreakfastLocal() {
  ellipse(-152, -4, 48, 8, '#dfe6f2');
  ellipse(-152, -6, 40, 5, '#ffffff');
  rrect(-174, -48, 44, 42, [15, 15, 6, 6], '#c98a4b');
  rrect(-169, -43, 34, 33, [11, 11, 4, 4], '#f3d29a');
  ctx.beginPath(); ctx.moveTo(138, -54); ctx.lineTo(164, -54); ctx.lineTo(160, -4); ctx.lineTo(142, -4); ctx.closePath();
  ctx.fillStyle = 'rgba(220,235,255,0.3)'; ctx.fill();
  ctx.strokeStyle = 'rgba(230,240,255,0.85)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.beginPath(); ctx.moveTo(139.6, -38); ctx.lineTo(162.4, -38); ctx.lineTo(159.6, -5); ctx.lineTo(142.4, -5); ctx.closePath();
  ctx.fillStyle = '#fbfaf4'; ctx.fill();
}
