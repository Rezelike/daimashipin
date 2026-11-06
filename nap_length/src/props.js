// props.js — nap_length's own stage and props: a pool of water (the deeper the mattress sinks, the deeper the sleep),
// an inflatable mattress, a depth gauge, three score boards on the deck, bubble tags, a curtain, a task board, splashes.
// Nothing here is reused from the earlier episodes' screens (no bars, wall clock, timer ring, alarm clock, calendar,
// HUD panel, outlined numbers, list table, word cards or window).
const WY = 640;            // water surface (calm)
const DECK_X = 1100;       // the pool's right wall = the deck's left edge
const DECK_TOP = 616;      // deck surface (24 px above the water)
const POOL_BOTTOM = 1000;  // pool floor
const GX = 96;             // depth gauge line
const MAT = { w: 400, h: 44 };
// mattress centre depths (screen y): floating, after 10 / 30 / 60 minutes asleep (deep sleep: <1 / ~11 / ~22 min)
const DEPTH = { float: WY - 10, m10: 690, m30: 890, m60: 958 };

// ---------- small icons / marks ----------
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
function iconCheck(x, y, s, color, lw = null) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = lw || s * 0.14; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.3, y + s * 0.02); ctx.lineTo(x - s * 0.08, y + s * 0.24); ctx.lineTo(x + s * 0.32, y - s * 0.22);
  ctx.stroke(); ctx.restore();
}
function okMark(x, y, r, p = 1, color = COL.yellow) {
  ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 18; circle(x, y, r, color); ctx.restore();
  checkBadge(x, y, r, { color: '#0d1838', p, lw: Math.max(3, r * 0.16) });
}
function sourceNote(s, x, y, o = {}) {
  const { alpha = 1, align = 'left', size = 24 } = o;
  txt(s, x, y, { size, weight: 500, color: 'rgba(181,191,214,0.8)', align, alpha });
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

// ---------- the pool ----------
function surfaceY(x, t) {
  return WY + 2.2 * Math.sin(x * 0.011 + t * 1.3) + 1.4 * Math.sin(x * 0.027 - t * 1.9);
}
function surfacePath(t, x0 = -10, x1 = DECK_X) {
  ctx.beginPath();
  ctx.moveTo(x0, surfaceY(x0, t));
  for (let x = x0; x <= x1; x += 20) ctx.lineTo(x, surfaceY(x, t));
  ctx.lineTo(x1, surfaceY(x1, t));
}
function waterRegion(t) {
  surfacePath(t);
  ctx.lineTo(DECK_X, POOL_BOTTOM); ctx.lineTo(-10, POOL_BOTTOM); ctx.closePath();
}
// light shafts drifting slowly through the water
const RAYS = Array.from({ length: 7 }, (_, i) => ({ x: 80 + i * 150 + (i % 2) * 40, w: 40 + (i * 37) % 50, ph: i * 1.7 }));
function drawPoolBack(t) {
  // the pool floor band under everything
  ctx.fillStyle = '#081430'; ctx.fillRect(0, POOL_BOTTOM, W, H - POOL_BOTTOM);
  ctx.save();
  waterRegion(t);
  const g = ctx.createLinearGradient(0, WY, 0, POOL_BOTTOM);
  g.addColorStop(0, '#1a527c'); g.addColorStop(0.35, '#123b63'); g.addColorStop(1, '#0a1b3d');
  ctx.fillStyle = g; ctx.fill();
  ctx.clip();
  for (const r of RAYS) {
    const sway = 26 * Math.sin(t * 0.35 + r.ph);
    const a = 0.045 + 0.025 * Math.sin(t * 0.6 + r.ph * 2);
    const lg = ctx.createLinearGradient(0, WY, 0, POOL_BOTTOM);
    lg.addColorStop(0, `rgba(140,225,255,${a})`); lg.addColorStop(1, 'rgba(140,225,255,0)');
    ctx.fillStyle = lg;
    ctx.beginPath(); ctx.moveTo(r.x + sway, WY); ctx.lineTo(r.x + sway + r.w, WY);
    ctx.lineTo(r.x + sway + r.w + 120, POOL_BOTTOM); ctx.lineTo(r.x + sway + 120, POOL_BOTTOM); ctx.closePath(); ctx.fill();
  }
  ctx.restore();
  // floor line
  const fg = ctx.createLinearGradient(0, 0, DECK_X, 0);
  fg.addColorStop(0, 'rgba(80,180,235,0.1)'); fg.addColorStop(0.5, 'rgba(80,180,235,0.35)'); fg.addColorStop(1, 'rgba(80,180,235,0.15)');
  ctx.fillStyle = fg; ctx.fillRect(0, POOL_BOTTOM - 1, DECK_X, 2);
}
// tint over everything under the surface + the bright surface line
function drawPoolFront(t) {
  ctx.save();
  waterRegion(t);
  ctx.fillStyle = 'rgba(24,96,160,0.30)'; ctx.fill();
  ctx.clip();
  const hg = ctx.createLinearGradient(0, WY - 4, 0, WY + 40);
  hg.addColorStop(0, 'rgba(150,230,255,0.22)'); hg.addColorStop(1, 'rgba(150,230,255,0)');
  ctx.fillStyle = hg; ctx.fillRect(0, WY - 6, DECK_X, 48);
  ctx.restore();
  ctx.save();
  surfacePath(t);
  ctx.strokeStyle = 'rgba(165,236,255,0.9)'; ctx.lineWidth = 3; ctx.shadowColor = COL.cyan; ctx.shadowBlur = 10; ctx.stroke();
  ctx.restore();
}
function drawDeck(t) {
  ctx.save();
  const g = ctx.createLinearGradient(0, DECK_TOP, 0, H);
  g.addColorStop(0, '#1a2b58'); g.addColorStop(0.25, '#132248'); g.addColorStop(1, '#0b1532');
  ctx.fillStyle = g; ctx.fillRect(DECK_X, DECK_TOP, W - DECK_X, H - DECK_TOP);
  ctx.strokeStyle = 'rgba(120,170,230,0.07)'; ctx.lineWidth = 1;
  ctx.beginPath();
  for (let y = DECK_TOP + 64; y < H; y += 64) { ctx.moveTo(DECK_X, y + 0.5); ctx.lineTo(W, y + 0.5); }
  ctx.stroke();
  rrect(DECK_X - 8, DECK_TOP - 8, W - DECK_X + 20, 18, 6, '#2a3f73');
  ctx.shadowColor = COL.cyan; ctx.shadowBlur = 8;
  line(DECK_X - 8, DECK_TOP - 8, W, DECK_TOP - 8, 'rgba(110,215,245,0.75)', 2.5);
  line(DECK_X - 1, DECK_TOP + 10, DECK_X - 1, POOL_BOTTOM, 'rgba(110,215,245,0.45)', 2);
  ctx.restore();
}

// ---------- depth gauge on the left wall: "睡了几分钟" ----------
// marks: [{ y, s, lit (0..1), color }]; ptr: { y, a } the yellow pointer at the mattress depth
function drawGauge(marks, o = {}) {
  const { alpha = 1, label = '睡了几分钟', ptr = null, zone = null } = o;
  withAlpha(alpha, () => {
    txt(label, 52, WY - 48, { size: 34, weight: 900, color: COL.cream });
    if (zone && zone.a > 0) withAlpha(zone.a, () => {
      rrect(GX - 12, zone.y0, 30, zone.y1 - zone.y0, 8, 'rgba(247,185,62,0.22)', 'rgba(247,185,62,0.8)', 2);
    });
    line(GX, WY + 4, GX, POOL_BOTTOM - 16, 'rgba(200,232,255,0.75)', 3);
    for (let y = WY + 20; y < POOL_BOTTOM - 16; y += 20) line(GX, y, GX + 9, y, 'rgba(200,232,255,0.45)', 2);
    for (const m of marks) {
      const lit = m.lit || 0, c = m.color || COL.yellow;
      line(GX - 4, m.y, GX + 24, m.y, lerpColor('#c8e8ff', c, lit), 4);
      txt(m.s, GX + 34, m.y + 1, { size: 34, weight: 900, color: lerpColor('#c8e8ff', c, lit), glow: 14 * lit, glowColor: c });
    }
    if (ptr && ptr.a > 0) withAlpha(ptr.a, () => {
      ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 12;
      ctx.beginPath(); ctx.moveTo(GX - 6, ptr.y); ctx.lineTo(GX - 26, ptr.y - 13); ctx.lineTo(GX - 26, ptr.y + 13); ctx.closePath();
      ctx.fillStyle = COL.yellow; ctx.fill(); ctx.restore();
    });
  });
}

// ---------- inflatable mattress (yellow, ribbed, pillow at the left end); x, y = centre ----------
function drawMattress(x, y, o = {}) {
  const { alpha = 1, w = MAT.w, h = MAT.h, tilt = 0, color = COL.yellow } = o;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(tilt);
    const g = ctx.createLinearGradient(0, -h / 2, 0, h / 2);
    g.addColorStop(0, '#ffe39c'); g.addColorStop(0.45, color); g.addColorStop(1, '#c98420');
    rrect(-w / 2, -h / 2, w, h, h / 2, g);
    ctx.strokeStyle = 'rgba(150,90,10,0.35)'; ctx.lineWidth = 3;
    ctx.beginPath();
    for (let k = 1; k < 9; k++) { const xx = -w / 2 + 70 + k * ((w - 90) / 9); ctx.moveTo(xx, -h / 2 + 7); ctx.lineTo(xx, h / 2 - 7); }
    ctx.stroke();
    // pillow
    const pg = ctx.createLinearGradient(0, -h / 2 - 14, 0, -h / 2 + 10);
    pg.addColorStop(0, '#fff2c8'); pg.addColorStop(1, '#f1c45a');
    rrect(-w / 2 + 10, -h / 2 - 12, 64, 26, 13, pg);
    // highlight
    rrect(-w / 2 + 90, -h / 2 + 5, w - 130, 6, 3, 'rgba(255,255,255,0.35)');
    ctx.restore();
  });
}
function drawMiniMattress(x, y, w, o = {}) {
  const { alpha = 1, color = COL.yellow } = o;
  withAlpha(alpha, () => {
    const h = w * 0.13;
    rrect(x - w / 2, y - h / 2, w, h, h / 2, color);
    rrect(x - w / 2 + 3, y - h / 2 - h * 0.45, w * 0.18, h * 0.6, h * 0.3, '#fff0c4');
  });
}

// ---------- bubbles ----------
function drawBubble(x, y, r, a = 1) {
  if (a <= 0.01 || r <= 0.5) return;
  withAlpha(a, () => {
    circle(x, y, r, 'rgba(160,230,255,0.10)', 'rgba(190,240,255,0.85)', Math.max(1.5, r * 0.12));
    ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.lineWidth = Math.max(1.2, r * 0.14); ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(x, y, r * 0.62, Math.PI * 1.1, Math.PI * 1.45); ctx.stroke(); ctx.restore();
  });
}
// a stream of bubbles rising from (x, y) while `on`; deterministic: bubble k leaves at k * gap beats
function bubbleStream(x0, y0, bt, from, to, o = {}) {
  const { gap = 0.22, rise = 150, spread = 150, seed = 3, top = WY + 8 } = o;
  const rng = mulberry32(seed);
  const n = Math.ceil((to - from) / gap);
  for (let k = 0; k < n; k++) {
    const b0 = from + k * gap, dx = (rng() - 0.5) * spread, r = 4 + rng() * 7, sp = rise * (0.8 + rng() * 0.5), wob = rng() * TAU;
    const age = bt - b0;
    if (age < 0 || age > 2.6) continue;
    const y = y0 - age * sp;
    if (y < top) continue;
    const x = x0 + dx + 6 * Math.sin(age * 4 + wob);
    drawBubble(x, y, r, Math.min(1, age * 4) * (1 - seg(age, 2.0, 2.6)));
  }
}

// ---------- score board on the deck (opening) ----------
// value: number or null (blank); hi: highlight 0..1; tone: colour of the top band
function drawScoreBoard(cx, top, label, value, o = {}) {
  const { w = 220, h = 140, tone = COL.cyan, hi = 0, alpha = 1, numColor = COL.cream, glow = 0, post = true, labelSize = 34, numSize = 78 } = o;
  withAlpha(alpha, () => {
    const x = cx - w / 2;
    if (post) rrect(cx - 6, top + h, 12, DECK_TOP - 8 - top - h, 3, '#33467a');
    ctx.save(); ctx.shadowColor = tone; ctx.shadowBlur = 10 + 24 * hi;
    rrect(x, top, w, h, 18, 'rgba(9,20,46,0.95)', lerpColor('#5c6887', tone, 0.35 + 0.65 * hi), 3);
    ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.roundRect(x, top, w, h, 18); ctx.clip();
    const band = Math.round(labelSize * 1.42);
    ctx.fillStyle = rgba(tone, 0.32 + 0.6 * hi); ctx.fillRect(x, top, w, band);
    ctx.restore();
    txt(label, cx, top + band / 2 + 1, { size: labelSize, weight: 900, color: hi > 0.5 ? '#0b1736' : COL.cream, align: 'center' });
    const ny = top + band + (h - band) / 2 + 2;
    if (value === null) txt('—', cx, ny, { size: 60, weight: 800, fam: 'mono', color: '#5c6887', align: 'center' });
    else txt(String(value), cx, ny, { size: numSize, weight: 800, fam: 'mono', color: numColor, align: 'center', glow });
    lintPanel('board:' + label, x, top, x + w, top + h);
  });
}

// ---------- bubble tag (①②③ in the answer section, then the summary rows) ----------
function bubbleTagWidth(s, size = 42) { return measure(s, size, 900) + 120; }
function drawBubbleTag(cx, cy, num, s, o = {}) {
  const { alpha = 1, scale = 1, hi = 0, size = 42, color = COL.cyanHi } = o;
  if (alpha <= 0.001 || scale <= 0.001) return;
  withAlpha(alpha, () => withScale(cx, cy, scale, () => {
    const w = bubbleTagWidth(s, size), h = 84, x = cx - w / 2;
    ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 14 + hi * 26;
    rrect(x, cy - h / 2, w, h, h / 2, 'rgba(16,58,98,0.78)', color, 3);
    ctx.restore();
    ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.55)'; ctx.lineWidth = 4; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x + 46, cy - h / 2 + 12); ctx.lineTo(x + 92, cy - h / 2 + 10); ctx.stroke(); ctx.restore();
    circle(x + 46, cy, 25, COL.cyan);
    txt(String(num), x + 46, cy + 1, { size: 30, weight: 800, fam: 'mono', color: '#0b1736', align: 'center' });
    txt(s, x + 86, cy + 1, { size, weight: 900, color: COL.cream });
    lintPanel('tag:' + s, x, cy - h / 2, x + w, cy + h / 2);
  }));
}

// ---------- step header: a big bubble with the number, title, line 2, typed English ----------
function stepHeader(num, title, line2, sub, o = {}) {
  const { alpha = 1, dx = 0, typeP = 1, bt = 0, bubble = 1 } = o;
  withAlpha(alpha, () => {
    const bx = 196 + dx, by = 150;
    withScale(bx, by, bubble, () => {
      ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 26;
      circle(bx, by, 62, 'rgba(18,64,108,0.85)', COL.cyanHi, 4); ctx.restore();
      ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth = 6; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.arc(bx, by, 46, Math.PI * 1.08, Math.PI * 1.42); ctx.stroke(); ctx.restore();
      if (num) txt(num, bx, by + 3, { size: 70, weight: 800, fam: 'mono', color: COL.cream, align: 'center' });
      else iconCheck(bx, by + 2, 64, COL.yellow, 9);
    });
    const tx = bx + 92;
    txt(title, tx, 102, { size: 60, weight: 900, color: COL.cream });
    rich(line2, tx, 172, { size: 52, weight: 900 });
    typeText(sub, typeP, tx + 2, 232, { size: 34, weight: 500, fam: 'mono', color: COL.cyan }, bt);
    lintPanel('header', bx - 62, 70, tx + Math.max(measure(title, 60, 900), richWidth(line2, 52, 900)), 252);
  });
}

// ---------- the figure's states ----------
// three "?" circling above his head (groggy)
function drawDizzy(x, y, bt, a = 1) {
  if (a <= 0.01) return;
  withAlpha(a, () => {
    for (let k = 0; k < 3; k++) {
      const an = bt * Math.PI + (k * TAU) / 3, front = Math.sin(an);
      const px = x + Math.cos(an) * 52, py = y + front * 12;
      txt('?', px, py, { size: 34 + 10 * (front + 1) / 2, weight: 900, color: COL.yellowHi, align: 'center', alpha: 0.55 + 0.45 * (front + 1) / 2, glow: 10 });
    }
  });
}
function drawZz(x, y, bt, a = 1) {
  if (a <= 0.01) return;
  withAlpha(a, () => {
    for (let k = 0; k < 2; k++) {
      const age = ((bt * 0.5 + k * 0.5) % 1);
      txt(k ? 'z' : 'Z', x + age * 30 + k * 16, y - age * 60, { size: 40 - k * 8, weight: 800, fam: 'mono', color: COL.cyanHi, align: 'center', alpha: Math.sin(age * Math.PI) });
    }
  });
}
// speech bubble with a check: "醒了！"
function drawSpeech(x, y, s, o = {}) {
  const { alpha = 1, scale = 1, check = true } = o;
  if (alpha <= 0.01 || scale <= 0.01) return;
  withAlpha(alpha, () => withScale(x, y + 40, scale, () => {
    const w = measure(s, 40, 900) + (check ? 96 : 48), h = 74;
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 16;
    rrect(x - w / 2, y - h / 2, w, h, 22, COL.cream);
    ctx.beginPath(); ctx.moveTo(x - 16, y + h / 2 - 2); ctx.lineTo(x + 4, y + h / 2 + 22); ctx.lineTo(x + 14, y + h / 2 - 2); ctx.closePath();
    ctx.fillStyle = COL.cream; ctx.fill(); ctx.restore();
    if (check) okMark(x - w / 2 + 40, y, 20, 1, COL.green);
    txt(s, x - w / 2 + (check ? 70 : 24), y + 1, { size: 40, weight: 900, color: '#14213f' });
    lintPanel('speech', x - w / 2, y - h / 2, x + w / 2, y + h / 2);
  }));
}

// ---------- water effects ----------
function drawSplash(x, y, p, o = {}) {
  const { n = 12, size = 1, color = 'rgba(200,240,255,0.95)' } = o;
  if (p <= 0 || p >= 1) return;
  const rng = mulberry32(Math.round(x * 7 + y));
  withAlpha(1 - EASE.in(p), () => {
    for (let i = 0; i < n; i++) {
      const an = -Math.PI / 2 + (rng() - 0.5) * 2.2, v = (140 + rng() * 160) * size;
      const tt = p * 0.9;
      const px = x + Math.cos(an) * v * tt, py = y + Math.sin(an) * v * tt + 420 * size * tt * tt;
      const r = (3 + rng() * 4) * size;
      ctx.fillStyle = color; ctx.beginPath(); ctx.ellipse(px, py, r * 0.8, r * 1.15, an + Math.PI / 2, 0, TAU); ctx.fill();
    }
  });
}
function drawRipple(x, y, p, o = {}) {
  const { r = 160 } = o;
  if (p <= 0 || p >= 1) return;
  for (let k = 0; k < 2; k++) {
    const q = clamp(p * 1.25 - k * 0.25);
    if (q <= 0) continue;
    ctx.save(); ctx.globalAlpha *= (1 - q) * 0.8;
    ctx.strokeStyle = 'rgba(190,240,255,0.9)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.ellipse(x, y, 20 + q * r, 4 + q * r * 0.08, 0, 0, TAU); ctx.stroke(); ctx.restore();
  }
}

// ---------- phone on the deck, used as the alarm (step ①) ----------
function drawPhone(x, y, buzz, o = {}) {
  const { alpha = 1, lit = 0 } = o;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(-0.08);
    rrect(-34, -62, 68, 124, 14, '#1d2742', '#8d99b5', 3);
    rrect(-27, -52, 54, 98, 8, lerpColor('#0e1a36', '#3fcbe8', 0.25 + 0.75 * lit));
    if (lit > 0.05) withAlpha(lit, () => iconBellLocal(0, 0, 40, '#0b1736'));
    ctx.restore();
    if (buzz > 0.01) withAlpha(buzz, () => {
      for (const sgn of [-1, 1]) for (let k = 0; k < 2; k++) {
        ctx.save(); ctx.strokeStyle = COL.cyanHi; ctx.lineWidth = 4; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.arc(x, y, 80 + k * 22, sgn > 0 ? -0.5 : Math.PI - 0.5, sgn > 0 ? 0.5 : Math.PI + 0.5); ctx.stroke(); ctx.restore();
      }
    });
    lintPanel('phone', x - 34, y - 62, x + 34, y + 62);
  });
}
function iconBellLocal(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.12; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(x - s * 0.36, y + s * 0.2); ctx.quadraticCurveTo(x - s * 0.3, y + s * 0.1, x - s * 0.3, y - s * 0.08);
  ctx.quadraticCurveTo(x - s * 0.28, y - s * 0.38, x, y - s * 0.38); ctx.quadraticCurveTo(x + s * 0.28, y - s * 0.38, x + s * 0.3, y - s * 0.08);
  ctx.quadraticCurveTo(x + s * 0.3, y + s * 0.1, x + s * 0.36, y + s * 0.2); ctx.closePath();
  ctx.moveTo(x - s * 0.08, y + s * 0.32); ctx.lineTo(x + s * 0.08, y + s * 0.32);
  ctx.stroke(); ctx.restore();
}

// ---------- curtain on the deck (step ③): open 0 = closed, 1 = pulled aside; light pours in from behind ----------
const CURTAIN = { x0: 1660, x1: 1880, top: 270, bottom: DECK_TOP - 8 };
function drawCurtainLight(open, o = {}) {
  const { alpha = 1 } = o;
  if (open <= 0.01) return;
  withAlpha(alpha * open, () => {
    const { x0, x1, top, bottom } = CURTAIN;
    const g = ctx.createLinearGradient(x1, 0, x0 - 700, 0);
    g.addColorStop(0, 'rgba(255,214,140,0.42)'); g.addColorStop(1, 'rgba(255,214,140,0)');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.moveTo(x0 + 10, top + 10); ctx.lineTo(x1 - 6, top + 10); ctx.lineTo(x1 - 6, bottom);
    ctx.lineTo(x0 - 760, DECK_TOP + 2); ctx.lineTo(x0 - 420, top + 120); ctx.closePath(); ctx.fill();
  });
}
function drawCurtain(open, o = {}) {
  const { alpha = 1 } = o;
  withAlpha(alpha, () => {
    const { x0, x1, top, bottom } = CURTAIN;
    // the bright opening behind it
    const lg = ctx.createLinearGradient(0, top, 0, bottom);
    lg.addColorStop(0, lerpColor('#1a2b58', '#ffe9b8', open)); lg.addColorStop(1, lerpColor('#13224a', '#ffd38a', open));
    ctx.save(); ctx.shadowColor = '#ffd58a'; ctx.shadowBlur = 50 * open;
    rrect(x0 + 8, top + 8, x1 - x0 - 16, bottom - top - 8, 6, lg); ctx.restore();
    // the fabric: its leading edge moves from x0 (closed) to x1 - 46 (bunched at the right)
    const edge = lerp(x0 + 4, x1 - 46, open), cw = x1 - edge;
    const folds = 6;
    for (let k = 0; k < folds; k++) {
      const fx = edge + (cw * k) / folds, fw = cw / folds + 1;
      const fg = ctx.createLinearGradient(fx, 0, fx + fw, 0);
      fg.addColorStop(0, '#5a3fa0'); fg.addColorStop(0.5, '#7b5fd6'); fg.addColorStop(1, '#4a3388');
      ctx.fillStyle = fg; ctx.fillRect(fx, top + 4, fw, bottom - top - 4);
    }
    line(x0 - 20, top, x1 + 16, top, '#c4cfe6', 7);
    circle(x0 - 20, top, 7, '#c4cfe6'); circle(x1 + 16, top, 7, '#c4cfe6');
  });
}

// ---------- task board on the deck (step ③): the experiment's symbol -> digit task, then easy / hard cards ----------
const BOARD = { x: 1240, y: 336, w: 380, h: 250 };
// shapes for the symbol-digit key (drawn, not font glyphs)
function shapeIcon(k, x, y, s, color) {
  ctx.save(); ctx.fillStyle = color; ctx.beginPath();
  if (k === 0) { ctx.moveTo(x, y - s); ctx.lineTo(x + s, y); ctx.lineTo(x, y + s); ctx.lineTo(x - s, y); }
  else if (k === 1) { ctx.moveTo(x, y - s); ctx.lineTo(x + s, y + s * 0.8); ctx.lineTo(x - s, y + s * 0.8); }
  else if (k === 2) ctx.arc(x, y, s * 0.85, 0, TAU);
  else if (k === 3) ctx.rect(x - s * 0.8, y - s * 0.8, s * 1.6, s * 1.6);
  else { iconStar(x, y, s, color); ctx.restore(); return; }
  ctx.closePath(); ctx.fill(); ctx.restore();
}
function drawBoardFrame(o = {}) {
  const { alpha = 1 } = o;
  const { x, y, w, h } = BOARD;
  withAlpha(alpha, () => {
    rrect(x + 40, y + h, 10, DECK_TOP - 8 - y - h, 3, '#33467a');
    rrect(x + w - 50, y + h, 10, DECK_TOP - 8 - y - h, 3, '#33467a');
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 20;
    rrect(x, y, w, h, 16, '#f2eee4'); ctx.restore();
    lintPanel('task board', x, y, x + w, y + h);
  });
}
