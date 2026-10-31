// props.js — this episode's own props (Skill 2.3: no bars / clocks / calendars / HUD panels / word-card grids / windows
// from the earlier episodes). The stage is sound: a word said aloud becomes a glowing solid block, a word read silently
// stays a dashed outline. Everything here draws in screen coordinates.
const INK = '#0b1736';
const LOUD = { c: COL.yellow, hi: COL.yellowHi };      // said aloud
const QUIET = { c: '#8d99b5', hi: '#c9d1e3' };         // read silently

// ---------- a word block ----------
// solid 0 = dashed outline (read silently) ... 1 = filled glowing block (said aloud); bright scales the fill and glow
// (whisper / mouthing are dimmer); lit = recognised in the test (brighter), dim = not recognised (fades).
function wordBlock(cx, cy, w, h, o = {}) {
  const { solid = 1, bright = 1, word = null, size = 40, fam = 'mono', lit = 0, dim = 0, alpha = 1, r = 10,
    color = LOUD.c, colorHi = LOUD.hi, quiet = QUIET, glyph = true, weight = 800 } = o;
  const a = alpha * (1 - 0.78 * dim);
  if (a <= 0.003 || w < 1 || h < 1) return;
  withAlpha(a, () => {
    const x = cx - w / 2, y = cy - h / 2;
    // dashed outline (always there under a block that is filling up)
    if (solid < 1) {
      ctx.save();
      ctx.setLineDash([9, 7]); ctx.lineDashOffset = 0;
      ctx.strokeStyle = lerpColor(quiet.c, quiet.hi, lit); ctx.lineWidth = 2.6;
      ctx.globalAlpha *= 1 - solid;
      ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.stroke();
      if (lit > 0) { ctx.fillStyle = rgba('#8fa3c9', 0.22 * lit); ctx.fill(); }
      ctx.restore();
    }
    if (solid > 0) {
      withAlpha(solid, () => {
        const g = ctx.createLinearGradient(0, y, 0, y + h);
        g.addColorStop(0, colorHi); g.addColorStop(1, color);
        ctx.save();
        ctx.globalAlpha *= 0.35 + 0.65 * bright;
        ctx.shadowColor = color; ctx.shadowBlur = (6 + 16 * bright + 14 * lit);
        rrect(x, y, w, h, r, g);
        ctx.restore();
      });
    }
    const inkC = solid > 0.5 ? rgba(INK, 0.75) : rgba(quiet.hi, 0.75);
    if (word) {
      txt(word, cx, cy + 1, { size, weight, fam, color: solid > 0.5 ? INK : lerpColor(quiet.c, quiet.hi, 0.6), align: 'center' });
    } else if (glyph) {
      // two "text" strokes instead of a word too small to read
      const lw = Math.max(3, h * 0.13), l1 = w * 0.56, l2 = w * 0.34;
      line(cx - l1 / 2, cy - h * 0.13, cx + l1 / 2, cy - h * 0.13, inkC, lw);
      line(cx - l1 / 2, cy + h * 0.17, cx - l1 / 2 + l2, cy + h * 0.17, inkC, lw);
    }
  });
}

// ---------- sound rings in front of the mouth (p 0..1 over one burst, k = loudness) ----------
function soundRings(x, y, dir, p, k = 1, color = COL.yellow) {
  if (p <= 0 || p >= 1 || k <= 0) return;
  ctx.save();
  ctx.lineCap = 'round';
  for (let i = 0; i < 3; i++) {
    const q = clamp(p * 1.4 - i * 0.18);
    if (q <= 0 || q >= 1) continue;
    const rr = 18 + q * 70 * (0.6 + 0.4 * k);
    ctx.globalAlpha = (1 - q) * 0.9 * k;
    ctx.strokeStyle = color; ctx.lineWidth = 4.5;
    ctx.shadowColor = color; ctx.shadowBlur = 12;
    ctx.beginPath();
    const a0 = dir > 0 ? -0.62 : Math.PI - 0.62, a1 = dir > 0 ? 0.62 : Math.PI + 0.62;
    ctx.arc(x, y, rr, a0, a1);
    ctx.stroke();
  }
  ctx.restore();
}

// ---------- a column of 10 word blocks that is also a recognition meter ----------
// n = blocks present (float: the top one fades in), level = share recognised (null before the test), scan = 0..1 test
// sweep. The level line + number sit on top of the recognised part.
const COLM = { w: 150, h: 34, gap: 5, n: 10 };
COLM.H = COLM.n * COLM.h + (COLM.n - 1) * COLM.gap;
function colBlockY(bottom, i) { return bottom - COLM.h / 2 - i * (COLM.h + COLM.gap); }
function levelY(bottom, level) { return bottom - level * COLM.H; }
function recogColumn(cx, bottom, kind, o = {}) {
  const { n = 10, level = null, scan = 1, alpha = 1, numAlpha = 1, flash = 0 } = o;
  if (alpha <= 0.003) return;
  const loud = kind === 'aloud';
  withAlpha(alpha, () => {
    // empty slots
    for (let i = Math.ceil(n); i < COLM.n; i++) {
      const y = colBlockY(bottom, i);
      rrect(cx - COLM.w / 2, y - COLM.h / 2, COLM.w, COLM.h, 9, 'rgba(255,255,255,0.025)', 'rgba(200,212,236,0.10)', 1.5);
    }
    const lv = level === null ? null : level * EASE.out(clamp(scan));
    for (let i = 0; i < Math.ceil(n); i++) {
      const y = colBlockY(bottom, i), fadeIn = clamp(n - i);
      let lit = 0, dim = 0;
      if (lv !== null) {
        const top = (i + 1) / COLM.n, bot = i / COLM.n;
        // block fully under the level line: recognised; above it: not recognised; dim waits for the sweep to pass
        lit = clamp((lv - bot) / (top - bot));
        // a block cut by the level line stays (it is partly recognised); blocks wholly above it fade as the sweep ends
        dim = lit > 0.05 ? 0 : EASE.out(clamp((scan - 0.6) / 0.4));
      }
      // not recognised = gone: the block turns into a faint empty slot, so the lit part reads as a height
      if (dim > 0) withAlpha(dim, () => rrect(cx - COLM.w / 2, y - COLM.h / 2, COLM.w, COLM.h, 9, 'rgba(255,255,255,0.02)', 'rgba(200,212,236,0.16)', 1.5));
      wordBlock(cx, y, COLM.w, COLM.h, { solid: loud ? 1 : 0, alpha: fadeIn * (1 - 0.94 * dim), lit: lit * (1 + flash * 0.6),
        bright: loud ? 0.75 + 0.25 * lit : 1 });
    }
    if (lv !== null && lv > 0.002) {
      const y = levelY(bottom, lv), c = loud ? COL.yellow : QUIET.hi;
      ctx.save(); ctx.shadowColor = c; ctx.shadowBlur = 16;
      line(cx - COLM.w / 2 - 12, y, cx + COLM.w / 2 + 12, y, c, 4); ctx.restore();
      const v = Math.round(level * 100 * EASE.out(clamp(scan)));
      txt(`${v}%`, cx, y - 36, { size: 58, weight: 800, fam: 'mono', color: loud ? COL.yellowHi : '#d5dbe8', align: 'center',
        alpha: numAlpha, glow: loud ? 16 : 0 });
    }
  });
}

// ---------- labels ----------
function kindLabel(cx, cy, s, kind, o = {}) {
  const { alpha = 1, size = 34 } = o;
  withAlpha(alpha, () => {
    const loud = kind === 'aloud', w = measure(s, size, 900);
    txt(s, cx, cy, { size, weight: 900, color: loud ? COL.yellow : COL.grayHi, align: 'center', glow: loud ? 10 : 0 });
    if (loud) iconSpeak(cx - w / 2 - 26, cy, 30, COL.yellow);
    else iconEye(cx - w / 2 - 26, cy, 30, COL.grayHi);
  });
}
// a pill with a caption; idx flips between items (float), like a slot machine line
function capPill(cx, cy, items, idx, o = {}) {
  const { alpha = 1, flash = 0, size = 36, color = COL.cream, border = 'rgba(243,238,227,0.5)' } = o;
  if (alpha <= 0.003) return;
  const i0 = Math.floor(idx), i1 = Math.min(items.length - 1, i0 + 1), p = idx - i0;
  const wOf = (s) => measure(s, size, 900) + 64;
  const w = lerp(wOf(items[i0]), wOf(items[i1]), EASE.inOut(p)), h = size + 30;
  withAlpha(alpha, () => {
    ctx.save();
    if (flash > 0) { ctx.shadowColor = COL.cream; ctx.shadowBlur = 30 * flash; }
    rrect(cx - w / 2, cy - h / 2, w, h, h / 2, `rgba(12,24,54,${0.82})`, border, 2.5);
    ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.roundRect(cx - w / 2, cy - h / 2, w, h, h / 2); ctx.clip();
    const one = (s, dy, a) => txt(s, cx, cy + dy + 1, { size, weight: 900, color, align: 'center', alpha: a });
    if (p <= 0.001) one(items[i0], 0, 1);
    else { const e = EASE.inOut(p); one(items[i0], -e * h, 1 - e); one(items[i1], (1 - e) * h, e); }
    ctx.restore();
  });
}

// ---------- icons (line style, centred) ----------
function iconSpeak(x, y, s, color) {  // a mouth with sound waves
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.11; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(x - s * 0.2, y, s * 0.16, 0, TAU); ctx.stroke();
  for (let i = 0; i < 2; i++) { ctx.beginPath(); ctx.arc(x - s * 0.2, y, s * (0.34 + i * 0.18), -0.7, 0.7); ctx.stroke(); }
  ctx.restore();
}
function iconEye(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.1; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.46, y); ctx.quadraticCurveTo(x, y - s * 0.42, x + s * 0.46, y);
  ctx.quadraticCurveTo(x, y + s * 0.42, x - s * 0.46, y); ctx.closePath(); ctx.stroke();
  circle(x, y, s * 0.13, color); ctx.restore();
}
function iconEar(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.1; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.18, y + s * 0.34);
  ctx.bezierCurveTo(x - s * 0.02, y + s * 0.42, x + s * 0.06, y + s * 0.2, x + s * 0.12, y + s * 0.08);
  ctx.bezierCurveTo(x + s * 0.34, y - s * 0.14, x + s * 0.26, y - s * 0.46, x - s * 0.02, y - s * 0.44);
  ctx.bezierCurveTo(x - s * 0.3, y - s * 0.42, x - s * 0.34, y - s * 0.14, x - s * 0.26, y - s * 0.04);
  ctx.stroke();
  ctx.beginPath(); ctx.arc(x, y - s * 0.16, s * 0.1, Math.PI, TAU * 0.95); ctx.stroke();
  ctx.restore();
}
function iconTape(x, y, s, color) {  // a recording: a play triangle in a rounded box
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.1; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.roundRect(x - s * 0.46, y - s * 0.32, s * 0.92, s * 0.64, s * 0.12); ctx.stroke();
  ctx.fillStyle = color; ctx.beginPath(); ctx.moveTo(x - s * 0.1, y - s * 0.16); ctx.lineTo(x + s * 0.18, y); ctx.lineTo(x - s * 0.1, y + s * 0.16);
  ctx.closePath(); ctx.fill(); ctx.restore();
}
function iconCheck(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.14; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.3, y + s * 0.02); ctx.lineTo(x - s * 0.08, y + s * 0.24); ctx.lineTo(x + s * 0.32, y - s * 0.22);
  ctx.stroke(); ctx.restore();
}
function iconCross(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.14; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x - s * 0.26, y - s * 0.26); ctx.lineTo(x + s * 0.26, y + s * 0.26);
  ctx.moveTo(x + s * 0.26, y - s * 0.26); ctx.lineTo(x - s * 0.26, y + s * 0.26); ctx.stroke(); ctx.restore();
}
function iconPen(x, y, s, color) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(-0.78);
  ctx.strokeStyle = color; ctx.lineWidth = s * 0.1; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.roundRect(-s * 0.1, -s * 0.42, s * 0.2, s * 0.62, s * 0.05); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-s * 0.1, s * 0.2); ctx.lineTo(0, s * 0.42); ctx.lineTo(s * 0.1, s * 0.2); ctx.stroke();
  ctx.restore();
}
function iconBrain(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.09; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath();
  ctx.arc(x - s * 0.16, y - s * 0.12, s * 0.2, Math.PI * 0.8, Math.PI * 1.9);
  ctx.arc(x + s * 0.16, y - s * 0.12, s * 0.2, Math.PI * 1.1, Math.PI * 0.2);
  ctx.arc(x + s * 0.14, y + s * 0.14, s * 0.2, Math.PI * 1.7, Math.PI * 0.6);
  ctx.arc(x - s * 0.14, y + s * 0.14, s * 0.2, Math.PI * 0.4, Math.PI * 1.3);
  ctx.closePath(); ctx.moveTo(x, y - s * 0.3); ctx.lineTo(x, y + s * 0.32); ctx.stroke(); ctx.restore();
}
function iconBulb(x, y, s, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = s * 0.1; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(x, y - s * 0.1, s * 0.28, Math.PI * 0.8, Math.PI * 2.2); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x - s * 0.14, y + s * 0.2); ctx.lineTo(x + s * 0.14, y + s * 0.2);
  ctx.moveTo(x - s * 0.1, y + s * 0.34); ctx.lineTo(x + s * 0.1, y + s * 0.34); ctx.stroke(); ctx.restore();
}
function iconStar(x, y, r, fill) {
  ctx.save(); ctx.beginPath();
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + (i * Math.PI) / 5, rr = i % 2 === 0 ? r : r * 0.45;
    i === 0 ? ctx.moveTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr) : ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr);
  }
  ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); ctx.restore();
}
const ICONS = { speak: iconSpeak, eye: iconEye, ear: iconEar, tape: iconTape, check: iconCheck, cross: iconCross, pen: iconPen,
  brain: iconBrain, bulb: iconBulb };

// ---------- verdict marks ----------
function okMark(x, y, r, p = 1) {
  ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 18; circle(x, y, r, COL.yellow); ctx.restore();
  checkBadge(x, y, r, { color: INK, p, lw: 4 });
}
function noMark(x, y, r, color = COL.grayHi) {
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
  txt(s, x, y, { size, weight: 500, color: 'rgba(181,191,214,0.8)', align, alpha });
}

// ---------- the light pen: a glowing stick in his hand, a thin beam to where it draws ----------
function lightPen(hx, hy, tx, ty, beam = 0) {
  const an = Math.atan2(ty - hy, tx - hx);
  ctx.save(); ctx.translate(hx, hy); ctx.rotate(an);
  ctx.shadowColor = COL.cyan; ctx.shadowBlur = 14;
  rrect(-10, -6, 52, 12, 6, '#dff8ff');
  circle(44, 0, 6.5, COL.cyanHi);
  ctx.restore();
  if (beam > 0.01) {
    const bx = hx + Math.cos(an) * 46, by = hy + Math.sin(an) * 46;
    ctx.save(); ctx.globalAlpha *= 0.55 * beam; ctx.strokeStyle = COL.cyanHi; ctx.lineWidth = 2.5;
    ctx.shadowColor = COL.cyan; ctx.shadowBlur = 10; ctx.setLineDash([3, 9]);
    ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(tx, ty); ctx.stroke(); ctx.restore();
    ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 20; circle(tx, ty, 7 * beam, COL.cyanHi); ctx.restore();
  }
}
// a hand-drawn glowing loop around a box (p = drawing progress)
function penLoop(cx, cy, rx, ry, p, color = COL.cyan, seed = 1) {
  if (p <= 0) return;
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = 5; ctx.lineCap = 'round';
  ctx.shadowColor = color; ctx.shadowBlur = 16;
  ctx.beginPath();
  const N = 64, end = Math.floor(N * 1.08 * clamp(p));
  for (let i = 0; i <= end; i++) {
    const a = -Math.PI * 0.62 + (i / N) * TAU, wob = 1 + 0.035 * Math.sin(i * 0.45 + seed * 2.1);
    const x = cx + Math.cos(a) * rx * wob, y = cy + Math.sin(a) * ry * wob + (i / N) * 6;
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  }
  ctx.stroke(); ctx.restore();
}
function penLoopEnd(cx, cy, rx, ry, p, seed = 1) {
  const N = 64, i = Math.floor(N * 1.08 * clamp(p));
  const a = -Math.PI * 0.62 + (i / N) * TAU, wob = 1 + 0.035 * Math.sin(i * 0.45 + seed * 2.1);
  return [cx + Math.cos(a) * rx * wob, cy + Math.sin(a) * ry * wob + (i / N) * 6];
}

// ---------- a numbered tag block (the ① ② ③ overview, also the step headers' number) ----------
function numBlock(cx, cy, num, o = {}) {
  const { size = 84, alpha = 1, scale = 1, color = COL.yellow, colorHi = COL.yellowHi } = o;
  if (alpha <= 0.003 || scale <= 0.003) return;
  withAlpha(alpha, () => withScale(cx, cy, scale, () => {
    const g = ctx.createLinearGradient(0, cy - size / 2, 0, cy + size / 2);
    g.addColorStop(0, colorHi); g.addColorStop(1, color);
    ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 22; rrect(cx - size / 2, cy - size / 2, size, size, size * 0.2, g); ctx.restore();
    txt(String(num), cx, cy + 2, { size: size * 0.66, weight: 800, fam: 'mono', color: INK, align: 'center' });
  }));
}
function tagChip(cx, cy, num, s, o = {}) {
  const { alpha = 1, scale = 1, hi = 0 } = o;
  if (alpha <= 0.003 || scale <= 0.003) return;
  withAlpha(alpha, () => withScale(cx, cy, scale, () => {
    const tw = measure(s, 42, 900), w = tw + 122, h = 84;
    ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 10 + hi * 26;
    rrect(cx - w / 2, cy - h / 2, w, h, 18, 'rgba(12,26,58,0.92)', rgba(COL.yellow, 0.85), 3); ctx.restore();
    numBlock(cx - w / 2 + 46, cy, num, { size: 54 });
    txt(s, cx - w / 2 + 88, cy + 1, { size: 42, weight: 900, color: COL.cream });
  }));
}
const tagWidth = (s) => measure(s, 42, 900) + 122;

// ---------- karaoke line: outlined text that fills solid from the left (= reading it aloud) ----------
// spans [{s, color}], p 0..1 fill progress
function karaoke(spans, x, y, p, o = {}) {
  const { size = 64, alpha = 1, outline = 'rgba(200,212,236,0.55)' } = o;
  if (alpha <= 0.003) return;
  const total = richWidth(spans, size, 900);
  withAlpha(alpha, () => {
    // outline (unread part)
    let cx = x;
    ctx.save();
    for (const sp of spans) {
      setFont(size, 900); ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      ctx.strokeStyle = outline; ctx.lineWidth = 1.6; ctx.setLineDash([6, 5]); ctx.strokeText(sp.s, cx, y);
      cx += measure(sp.s, size, 900);
    }
    ctx.restore();
    // filled part
    if (p > 0) {
      ctx.save(); ctx.beginPath(); ctx.rect(x - 4, y - size, total * clamp(p) + 4, size * 2); ctx.clip();
      rich(spans.map((sp) => ({ ...sp, glow: sp.color && sp.color !== COL.cream ? 14 : 0 })), x, y, { size, weight: 900 });
      ctx.restore();
    }
  });
  return total;
}
