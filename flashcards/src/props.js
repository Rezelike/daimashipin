// props.js — this episode's own stage and props (six/plan.md 第 6 条: 发牌桌). A dealer's card table (felt, rail, printed
// labels), glowing flash cards lying on the felt / standing / flying, card stacks with their edges, the dealer's card
// spring, big standing cards that flip (the hook's 「我估计能记住」 → 考试), overview tag cards with a corner index, a day
// stand, a speech bubble, a discard tray, loop arrows for passes, a vote strip of tiny cards. Not used (plan rule): the
// earlier bars / pillars, clocks, timer ring, alarm, calendar, HUD panel, outlined numbers, list table, word-card grid,
// window, and none of the other five six-batch props (scoreboards, flags, sound blocks, pool, house).
// Small generic helpers at the end (marks, sparkle, source note) follow bedtime_words / read_aloud.
const INK = '#0b1736';
const BIG = { c: COL.yellow, hi: COL.yellowHi };     // 一大叠 (the deck that wins)
const SMALL = { c: COL.cyan, hi: COL.cyanHi };       // 四小叠
const DIMC = { c: '#6f7c99', hi: '#aeb8cc' };        // a side that lost / a card not in play
const PINKC = { c: COL.pink, hi: '#ffb3cb' };
const CARD_FILL = '#0d1a3a';

// ---------- the table ----------
// felt: a rounded trapezoid seen from the players' side; the dealer stands behind its straight back edge (TB.back is
// at his hips, so the table hides his legs). Front rail = a dark band under the front edge.
const TB = { back: 740, front: 948, bx0: 150, bx1: 1770, fx0: 46, fx1: 1874, rail: 22, r: 74 };
const FLAT_K = 0.36;      // height / width of a card lying on the felt (perspective)
const CARD_T = 3.3;       // screen thickness of one card in a stack
function norm2(v) { const l = Math.hypot(v[0], v[1]) || 1; return [v[0] / l, v[1] / l]; }
function tablePath(dy = 0) {
  const bl = [TB.bx0, TB.back + dy], br = [TB.bx1, TB.back + dy], fr = [TB.fx1, TB.front + dy], fl = [TB.fx0, TB.front + dy];
  const dR = norm2([fr[0] - br[0], fr[1] - br[1]]), dL = norm2([fl[0] - bl[0], fl[1] - bl[1]]), r = TB.r;
  ctx.beginPath();
  ctx.moveTo(...bl); ctx.lineTo(...br);
  ctx.lineTo(fr[0] - dR[0] * r, fr[1] - dR[1] * r);
  ctx.quadraticCurveTo(fr[0], fr[1], fr[0] - r, fr[1]);
  ctx.lineTo(fl[0] + r, fl[1]);
  ctx.quadraticCurveTo(fl[0], fl[1], fl[0] - dL[0] * r, fl[1] - dL[1] * r);
  ctx.closePath();
}
function drawTable() {
  // rail (thickness at the front)
  tablePath(TB.rail); ctx.fillStyle = '#070d22'; ctx.fill();
  tablePath(TB.rail * 0.5); ctx.fillStyle = '#0a1430'; ctx.fill();
  // felt
  const g = ctx.createLinearGradient(0, TB.back, 0, TB.front);
  g.addColorStop(0, '#0b2c3c'); g.addColorStop(1, '#09202f');
  tablePath(); ctx.fillStyle = g; ctx.fill();
  ctx.save(); tablePath(); ctx.clip();
  const rg = ctx.createRadialGradient(W / 2, TB.back + 40, 30, W / 2, TB.back + 40, 900);
  rg.addColorStop(0, 'rgba(63,203,232,0.10)'); rg.addColorStop(1, 'rgba(63,203,232,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, TB.back, W, TB.front - TB.back);
  // the printed arc of a card table
  ctx.strokeStyle = 'rgba(143,232,248,0.13)'; ctx.lineWidth = 2; ctx.setLineDash([14, 10]);
  ctx.beginPath(); ctx.ellipse(W / 2, TB.back - 60, 900, 262, 0, 0.12 * Math.PI, 0.88 * Math.PI); ctx.stroke();
  ctx.restore();
  // neon edges: the dealer's straight edge and the curved front edge
  ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 14;
  tablePath(); ctx.strokeStyle = 'rgba(143,232,248,0.55)'; ctx.lineWidth = 2.6; ctx.stroke();
  ctx.restore();
  const hg = ctx.createLinearGradient(TB.bx0, 0, TB.bx1, 0);
  hg.addColorStop(0, 'rgba(143,232,248,0.2)'); hg.addColorStop(0.5, 'rgba(143,232,248,0.85)'); hg.addColorStop(1, 'rgba(143,232,248,0.2)');
  ctx.fillStyle = hg; ctx.fillRect(TB.bx0, TB.back - 1.5, TB.bx1 - TB.bx0, 3);
}
// text printed on the felt
function feltText(s, x, y, o = {}) {
  const { size = 36, color = COL.cream, alpha = 1, align = 'center', weight = 900 } = o;
  txt(s, x, y, { size, weight, color, align, alpha: alpha * 0.92 });
}

// ---------- cards ----------
// a card lying on the felt: centre, width; solid 0..1 fills it with its colour (the highlighted card)
function flatCard(cx, cy, w, o = {}) {
  const { pal = BIG, solid = 0, alpha = 1, lit = 0, glyph = true } = o;
  const h = w * FLAT_K;
  if (alpha <= 0.003) return;
  withAlpha(alpha, () => {
    const x = cx - w / 2, y = cy - h / 2;
    rrect(x, y + CARD_T, w, h, 7, 'rgba(3,7,18,0.9)');
    ctx.save(); ctx.shadowColor = pal.c; ctx.shadowBlur = 6 + 20 * lit + 10 * solid;
    rrect(x, y, w, h, 7, solid > 0 ? lerpColor(CARD_FILL, pal.c, solid) : CARD_FILL, rgba(pal.hi, 0.6 + 0.4 * Math.max(lit, solid)), 2.2);
    ctx.restore();
    if (glyph) {
      const c = solid > 0.5 ? rgba(INK, 0.7) : rgba(pal.hi, 0.42 + 0.3 * lit);
      line(cx - w * 0.3, cy - h * 0.1, cx + w * 0.18, cy - h * 0.1, c, Math.max(2.4, h * 0.13));
      line(cx - w * 0.3, cy + h * 0.2, cx - w * 0.02, cy + h * 0.2, c, Math.max(2, h * 0.1));
    }
  });
}
// a stack of n cards on the felt: the side shows one line per card; returns the y of the top card
function deckStack(cx, baseY, n, o = {}) {
  const { w = 130, pal = BIG, alpha = 1, lit = 0, topSolid = 0 } = o;
  const N = Math.max(1, Math.round(n)), h = w * FLAT_K, topY = baseY - (N - 1) * CARD_T;
  if (alpha <= 0.003 || n < 0.5) return topY;
  withAlpha(alpha, () => {
    const x = cx - w / 2, y0 = topY + h / 2 - 2, y1 = baseY + h / 2 + CARD_T;
    ctx.save(); ctx.shadowColor = pal.c; ctx.shadowBlur = 4 + 18 * lit;
    rrect(x, y0, w, y1 - y0, 6, '#060c1e', rgba(pal.c, 0.45 + 0.4 * lit), 1.6);
    ctx.restore();
    for (let i = 1; i < N; i++) {
      const yy = y0 + i * CARD_T;
      line(x + 5, yy, x + w - 5, yy, rgba(pal.hi, 0.22 + 0.25 * lit), 1);
    }
    flatCard(cx, topY, w, { pal, lit, solid: topSolid });
  });
  return topY;
}
// an upright card (in a hand, flying, standing): o.flip 0..1 turns it over around its vertical axis (face swaps at 0.5);
// front / back are functions (w, h) that draw the face in card coordinates (origin = card centre)
function uprightCard(cx, cy, w, h, o = {}) {
  const { pal = BIG, alpha = 1, rot = 0, lit = 0, flip = 0, front = null, back = null, solid = 0, r = 14, lw = 3, fill = CARD_FILL } = o;
  if (alpha <= 0.003) return;
  const f = clamp(flip), sx = Math.abs(Math.cos(Math.PI * f));
  const face = f < 0.5 ? front : back;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(Math.max(0.03, sx), 1);
    ctx.save(); ctx.shadowColor = pal.c; ctx.shadowBlur = 8 + 30 * lit;
    rrect(-w / 2, -h / 2, w, h, r, solid > 0 ? lerpColor(fill, pal.c, solid) : fill, rgba(pal.hi, 0.75 + 0.25 * lit), lw);
    ctx.restore();
    if (face) face(w, h);
    ctx.restore();
  });
}
// the plain back of a card: a thin inner frame and two strokes
function plainFace(pal = BIG, k = 1) {
  return (w, h) => {
    ctx.save(); ctx.strokeStyle = rgba(pal.hi, 0.35 * k); ctx.lineWidth = 1.6;
    ctx.beginPath(); ctx.roundRect(-w / 2 + 6, -h / 2 + 6, w - 12, h - 12, 5); ctx.stroke(); ctx.restore();
    line(-w * 0.24, -h * 0.06, w * 0.2, -h * 0.06, rgba(pal.hi, 0.5 * k), Math.max(2, w * 0.07));
    line(-w * 0.24, h * 0.14, w * 0.02, h * 0.14, rgba(pal.hi, 0.4 * k), Math.max(1.8, w * 0.06));
  };
}
// a flash card's face with a word (front = the hard word, back = its meaning)
function wordFace(s, o = {}) {
  const { color = COL.cream, size = 44, fam = 'mono', weight = 800, sub = null, subColor = COL.grayHi } = o;
  return (w, h) => {
    txt(s, 0, sub ? -h * 0.1 : 2, { size, weight, fam, color, align: 'center' });
    if (sub) txt(sub, 0, h * 0.27, { size: 36, weight: 700, color: subColor, align: 'center' });
  };
}
// a deck held in a hand: a short stack seen from slightly above, tilted with the hand
function handDeck(hx, hy, n, o = {}) {
  const { pal = BIG, alpha = 1, w = 92, tilt = -0.08 } = o;
  if (n < 0.5 || alpha <= 0.003) return;
  withAlpha(alpha, () => {
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(tilt);
    deckStack(0, 6, Math.min(n, 20) * 0.6 + 1, { w, pal });
    ctx.restore();
  });
}

// ---------- the dealer's spring: cards stream in an arc from one hand to the other ----------
// p = progress 0..1 of one spring; the source deck shrinks while the target deck grows
function cardSpring(a, b, p, o = {}) {
  const { n = 11, pal = BIG, lift = 100, w = 38, h = 54, L = 0.46, alpha = 1 } = o;
  if (p <= 0 || p >= 1 || alpha <= 0.003) return;
  for (let i = 0; i < n; i++) {
    const s0 = (i * (1 - L)) / (n - 1), q = (p - s0) / L;
    if (q <= 0 || q >= 1) continue;
    const x = lerp(a[0], b[0], q), y = lerp(a[1], b[1], q) - Math.sin(Math.PI * q) * lift;
    uprightCard(x, y, w, h, { pal, rot: lerp(-0.7, 0.7, q), r: 5, lw: 2, alpha: alpha * 0.95, front: plainFace(pal, 0.8) });
  }
}

// ---------- big standing cards (the hook's estimate → test score) ----------
// tab = arrangement name on a coloured tab above the card; front / back: { head, value }
const PLAC = { w: 360, h: 210 };
function placard(cx, cy, o = {}) {
  const { pal = BIG, tab = '', front, back, flip = 0, lit = 0, alpha = 1, scale = 1, valueP = 1, dim = 0 } = o;
  if (alpha <= 0.003 || scale <= 0.003) return;
  const face = (f, side) => (w, h) => {
    const p = side === 'front' ? valueP : 1;
    txt(f.head, 0, -h / 2 + 46, { size: 36, weight: 900, color: COL.grayHi, align: 'center' });
    const v = Math.round(f.value * EASE.out(clamp(p)));
    const col = dim > 0.5 ? DIMC.hi : (lit > 0.3 ? pal.hi : COL.cream);
    txt(`${v}%`, 0, h * 0.14, { size: 104, weight: 800, fam: 'mono', color: col, align: 'center', glow: lit > 0.3 ? 22 * lit : 0, glowColor: pal.c });
  };
  const usePal = dim > 0.5 ? DIMC : pal;
  withAlpha(alpha, () => withScale(cx, cy, scale, () => {
    // the tab with the arrangement's name (does not flip)
    const tw = measure(tab, 38, 900) + 44;
    ctx.save(); ctx.shadowColor = usePal.c; ctx.shadowBlur = 6 + 14 * lit;
    rrect(cx - tw / 2, cy - PLAC.h / 2 - 50, tw, 58, 12, lerpColor(CARD_FILL, usePal.c, 0.18 + 0.5 * lit), rgba(usePal.hi, 0.8), 2.4);
    ctx.restore();
    txt(tab, cx, cy - PLAC.h / 2 - 22, { size: 38, weight: 900, color: lit > 0.3 ? INK : usePal.hi, align: 'center' });
    uprightCard(cx, cy, PLAC.w, PLAC.h, { pal: usePal, flip, lit, front: face(front, 'front'), back: face(back, 'back'), r: 18, lw: 3.4 });
  }));
}

// ---------- the overview tags ①②③ and the step headers: a card with a corner index ----------
function indexCard(cx, cy, num, o = {}) {
  const { w = 92, h = 124, pal = BIG, alpha = 1, flip = 0, lit = 0, rot = 0 } = o;
  uprightCard(cx, cy, w, h, { pal, alpha, flip, lit, rot, r: 12, front: (cw, ch) => {
    txt(String(num), -cw / 2 + 18, -ch / 2 + 24, { size: 34, weight: 800, fam: 'mono', color: pal.hi, align: 'center' });
    txt(String(num), 0, 6, { size: Math.round(ch * 0.52), weight: 800, fam: 'mono', color: pal.hi, align: 'center', glow: 14, glowColor: pal.c });
  }, back: plainFace(pal) });
}
function tagCard(cx, cy, num, s, o = {}) {
  const { alpha = 1, scale = 1, lit = 0, rot = 0 } = o;
  if (alpha <= 0.003 || scale <= 0.003) return;
  const w = measure(s, 44, 900) + 150, h = 118;
  withAlpha(alpha, () => withScale(cx, cy, scale, () => {
    uprightCard(cx, cy, w, h, { pal: BIG, lit, rot, r: 16, front: (cw, ch) => {
      txt(String(num), -cw / 2 + 24, -ch / 2 + 26, { size: 34, weight: 800, fam: 'mono', color: COL.yellowHi, align: 'center' });
      ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 16;
      circle(-cw / 2 + 74, 6, 30, COL.yellow); ctx.restore();
      txt(String(num), -cw / 2 + 74, 8, { size: 40, weight: 800, fam: 'mono', color: INK, align: 'center' });
      txt(s, -cw / 2 + 118, 6, { size: 44, weight: 900, color: COL.cream });
    } });
  }));
}
const tagCardW = (s) => measure(s, 44, 900) + 150;

// ---------- a day stand on the table: a small standing card that turns over to the next day ----------
function dayStand(cx, cy, labels, idx, o = {}) {
  const { alpha = 1, pal = SMALL, w = 250, h = 112, lit = 0 } = o;
  if (alpha <= 0.003) return;
  const i0 = Math.floor(idx), f = idx - i0, i1 = Math.min(labels.length - 1, i0 + 1);
  withAlpha(alpha, () => {
    // two little feet on the felt
    line(cx - w * 0.3, cy + h / 2, cx - w * 0.36, cy + h / 2 + 22, rgba(pal.hi, 0.6), 4);
    line(cx + w * 0.3, cy + h / 2, cx + w * 0.36, cy + h / 2 + 22, rgba(pal.hi, 0.6), 4);
    const face = (s) => (cw, ch) => txt(s, 0, 3, { size: s.length > 5 ? 46 : 52, weight: 900, color: COL.cream, align: 'center' });
    uprightCard(cx, cy, w, h, { pal, lit, flip: f, front: face(labels[i0]), back: face(labels[i1]), r: 14 });
  });
}

// ---------- speech bubble (he says the answer before he turns the card) ----------
function speechBubble(x, y, s, tail, o = {}) {
  const { alpha = 1, scale = 1, size = 50, color = COL.cream, fam = 'mono' } = o;
  if (alpha <= 0.003 || scale <= 0.003) return;
  const w = measure(s, size, 800, fam) + 64, h = size + 44;
  withAlpha(alpha, () => withScale(x, y, scale, () => {
    ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 16;
    ctx.beginPath(); ctx.roundRect(x - w / 2, y - h / 2, w, h, h / 2);
    ctx.fillStyle = 'rgba(12,26,58,0.94)'; ctx.fill();
    ctx.strokeStyle = rgba(COL.cyanHi, 0.9); ctx.lineWidth = 3; ctx.stroke();
    // tail toward the speaker
    const d = norm2([tail[0] - x, tail[1] - y]);
    const bx = x + d[0] * (w / 2 - 30), by = y + d[1] * (h / 2 - 6);
    ctx.beginPath(); ctx.moveTo(bx - 14, by - 6); ctx.lineTo(lerp(bx, tail[0], 0.55), lerp(by, tail[1], 0.55)); ctx.lineTo(bx + 14, by - 2);
    ctx.fillStyle = 'rgba(12,26,58,0.94)'; ctx.fill(); ctx.stroke();
    ctx.restore();
    txt(s, x, y + 2, { size, weight: 800, fam, color, align: 'center' });
  }));
}

// ---------- the discard tray (cards taken out of the deck) ----------
function discardTray(cx, cy, o = {}) {
  const { alpha = 1, w = 200, h = 64 } = o;
  if (alpha <= 0.003) return;
  withAlpha(alpha, () => {
    rrect(cx - w / 2, cy - h / 2, w, h, 12, 'rgba(6,10,26,0.92)', rgba(DIMC.hi, 0.7), 2.4);
    rrect(cx - w / 2 + 10, cy - h / 2 + 8, w - 20, h - 22, 8, 'rgba(255,255,255,0.03)');
  });
}

// ---------- a loop arrow around something (one pass through a deck); p 0..1 ----------
function loopArrow(cx, cy, rx, ry, p, color, o = {}) {
  const { lw = 5, alpha = 1 } = o;
  if (p <= 0.001 || alpha <= 0.003) return;
  const a0 = -Math.PI * 0.5, a1 = a0 + TAU * 0.86 * clamp(p);
  withAlpha(alpha, () => {
    ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.shadowColor = color; ctx.shadowBlur = 12;
    ctx.beginPath(); ctx.ellipse(cx, cy, rx, ry, 0, a0, a1); ctx.stroke();
    // arrow head, tangent to the ellipse at a1
    const ex = cx + rx * Math.cos(a1), ey = cy + ry * Math.sin(a1);
    const tx = -rx * Math.sin(a1), ty = ry * Math.cos(a1), d = norm2([tx, ty]), n = [-d[1], d[0]];
    ctx.fillStyle = color; ctx.beginPath();
    ctx.moveTo(ex + d[0] * 14, ey + d[1] * 14); ctx.lineTo(ex - d[0] * 6 + n[0] * 10, ey - d[1] * 6 + n[1] * 10);
    ctx.lineTo(ex - d[0] * 6 - n[0] * 10, ey - d[1] * 6 - n[1] * 10); ctx.closePath(); ctx.fill();
    ctx.restore();
  });
}
// an arc arrow over a row, from x0 to x1 (the same card coming back)
function hopArrow(x0, x1, y, hgt, p, color, o = {}) {
  const { lw = 4, alpha = 1, head = true } = o;
  if (p <= 0.001 || alpha <= 0.003) return;
  const N = 40, n = Math.max(1, Math.floor(N * clamp(p)));
  const P = (u) => [lerp(x0, x1, u), y - Math.sin(Math.PI * u) * hgt];
  withAlpha(alpha, () => {
    ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.shadowColor = color; ctx.shadowBlur = 10;
    ctx.beginPath();
    for (let i = 0; i <= n; i++) { const q = P(i / N); i ? ctx.lineTo(...q) : ctx.moveTo(...q); }
    ctx.stroke();
    if (head && p >= 1) {
      const e = P(1), b = P(0.96), d = norm2([e[0] - b[0], e[1] - b[1]]), nn = [-d[1], d[0]];
      ctx.fillStyle = color; ctx.beginPath();
      ctx.moveTo(e[0] + d[0] * 6, e[1] + d[1] * 6); ctx.lineTo(e[0] - d[0] * 14 + nn[0] * 9, e[1] - d[1] * 14 + nn[1] * 9);
      ctx.lineTo(e[0] - d[0] * 14 - nn[0] * 9, e[1] - d[1] * 14 - nn[1] * 9); ctx.closePath(); ctx.fill();
    }
    ctx.restore();
  });
}

// ---------- a strip of tiny cards = people (real counts), k of them lit ----------
function voteStrip(x, y, n, k, p, o = {}) {
  const { cols = 29, cw = 17, ch = 24, gap = 6, pal = SMALL, alpha = 1 } = o;
  withAlpha(alpha, () => {
    for (let i = 0; i < n; i++) {
      const r = Math.floor(i / cols), c = i % cols;
      const cx = x + c * (cw + gap) + cw / 2, cy = y + r * (ch + gap);
      const on = i < k && p * n > i;
      ctx.save();
      if (on) { ctx.shadowColor = pal.c; ctx.shadowBlur = 10; }
      rrect(cx - cw / 2, cy - ch / 2, cw, ch, 4, on ? pal.c : 'rgba(170,184,210,0.16)', on ? pal.hi : 'rgba(170,184,210,0.45)', 1.4);
      ctx.restore();
    }
  });
}

// ---------- small generic helpers ----------
function iconStar(x, y, r, fill) {
  ctx.save(); ctx.beginPath();
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + (i * Math.PI) / 5, rr = i % 2 === 0 ? r : r * 0.45;
    i === 0 ? ctx.moveTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr) : ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr);
  }
  ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); ctx.restore();
}
function iconCross(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.14; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.26, y - s * 0.26); ctx.lineTo(x + s * 0.26, y + s * 0.26);
  ctx.moveTo(x + s * 0.26, y - s * 0.26); ctx.lineTo(x - s * 0.26, y + s * 0.26); ctx.stroke(); ctx.restore();
}
function okMark(x, y, r, p = 1, color = COL.yellow) {
  ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 18; circle(x, y, r, color); ctx.restore();
  checkBadge(x, y, r, { color: INK, p, lw: 4 });
}
function noMark(x, y, r, color = DIMC.hi) {
  circle(x, y, r, color);
  iconCross(x, y, r * 1.1, INK);
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
function sourceNote(s, x, y, o = {}) {
  const { alpha = 1, align = 'left', size = 24 } = o;
  txt(s, x, y, { size, weight: 500, color: 'rgba(181,191,214,0.82)', align, alpha });
}
// a big number with a label under it (the result of a comparison), no panel
function scoreLine(cx, y, label, value, pal, o = {}) {
  const { alpha = 1, lit = 0, dim = 0, size = 96, p = 1 } = o;
  if (alpha <= 0.003) return;
  withAlpha(alpha, () => {
    const col = dim > 0.5 ? DIMC.hi : pal.hi;
    txt(`${Math.round(value * EASE.out(clamp(p)))}%`, cx, y, { size, weight: 800, fam: 'mono', color: col, align: 'center', glow: lit > 0 ? 20 * lit : 0, glowColor: pal.c });
    txt(label, cx, y + size * 0.72, { size: 38, weight: 900, color: dim > 0.5 ? DIMC.hi : pal.c, align: 'center' });
  });
}
