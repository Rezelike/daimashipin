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
const ICONS = { clock: iconClock, paper: iconPaper, calendar: iconCalendar, book: iconBook, bell: iconBell, zz: iconZz, alarm: iconAlarm, moon: iconMoonX, bolt: iconBolt, brain: iconBrain };

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
function drawMeter(x, bottom, w, hMax, level, o = {}) {
  const { color = COL.cyan, colorHi = COL.cyanHi, alpha = 1, label = '记住了', labelAlpha = 1, q = 0, glow = 1 } = o;
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
