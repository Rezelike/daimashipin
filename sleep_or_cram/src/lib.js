// lib.js — shared helpers (easing, keyframes, text, shapes, background, chapter bar)
const W = 1920, H = 1080;
const BPM = 128, BEAT = 60 / BPM; // 0.46875 s
const TAU = Math.PI * 2;
const HORIZON = 722;

const COL = {
  cream: '#f3eee3',
  yellow: '#f7b93e',
  yellowHi: '#ffd57e',
  cyan: '#3fcbe8',
  cyanHi: '#8fe8f8',
  pink: '#ff6f9e',
  red: '#f06464',
  gray: '#8d99b5',
  grayHi: '#b5bfd6',
  grayDim: '#5c6887',
  green: '#59d68f',
};
const FAM = { cjk: 'NotoSansSC', mono: 'JetBrainsMono' };

let ctx = null;
function setCtx(c) { ctx = c; }

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));

const EASE = {
  lin: (x) => x,
  in: (x) => x * x * x,
  out: (x) => 1 - Math.pow(1 - x, 3),
  inOut: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  back: (x) => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
  elastic: (x) => (x <= 0 ? 0 : x >= 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * (TAU / 3)) + 1),
  bounce: (x) => {
    const n1 = 7.5625, d1 = 2.75;
    if (x < 1 / d1) return n1 * x * x;
    if (x < 2 / d1) return n1 * (x -= 1.5 / d1) * x + 0.75;
    if (x < 2.5 / d1) return n1 * (x -= 2.25 / d1) * x + 0.9375;
    return n1 * (x -= 2.625 / d1) * x + 0.984375;
  },
  step: (x) => (x < 1 ? 0 : 1),
};

// Keyframe track. keys: [[beat, value, easeName?], ...] (ease applies to the segment ending at that key)
function KB(keys) {
  return (bt) => {
    if (bt <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const [b1, v1, e] = keys[i];
      if (bt <= b1) {
        const [b0, v0] = keys[i - 1];
        const p = b1 === b0 ? 1 : (bt - b0) / (b1 - b0);
        return v0 + (v1 - v0) * EASE[e || 'inOut'](p);
      }
    }
    return keys[keys.length - 1][1];
  };
}

// alpha window: fade in over [a, a+fi], fade out over [b-fo, b]
function win(bt, a, b, fi = 0.5, fo = 0.5) {
  if (bt < a || bt > b) return 0;
  const i = fi > 0 ? clamp((bt - a) / fi) : 1;
  const o = fo > 0 ? clamp((b - bt) / fo) : 1;
  return Math.min(EASE.out(i), EASE.out(o));
}
// pop-in scale (back easing) starting at beat a, duration d beats
const popS = (bt, a, d = 0.7) => (bt < a ? 0 : EASE.back(clamp((bt - a) / d)));
const popA = (bt, a, d = 0.3) => (bt < a ? 0 : EASE.out(clamp((bt - a) / d)));

function hexToRgb(h) {
  const n = parseInt(h.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
function lerpColor(a, b, t) {
  const A = hexToRgb(a), B = hexToRgb(b);
  return `rgb(${Math.round(lerp(A[0], B[0], t))},${Math.round(lerp(A[1], B[1], t))},${Math.round(lerp(A[2], B[2], t))})`;
}
function rgba(hex, a) { const [r, g, b] = hexToRgb(hex); return `rgba(${r},${g},${b},${a})`; }

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------- text ----------
function setFont(size, weight = 700, fam = 'cjk') {
  // mono falls back to the CJK face for Chinese glyphs
  const f = fam === 'mono' ? `${FAM.mono}, ${FAM.cjk}` : (FAM[fam] || fam);
  ctx.font = `${weight} ${size}px ${f}`;
}
function measure(s, size, weight = 700, fam = 'cjk') {
  setFont(size, weight, fam);
  return ctx.measureText(s).width;
}
function txt(s, x, y, o = {}) {
  const { size = 40, weight = 700, fam = 'cjk', color = COL.cream, align = 'left', base = 'middle',
    alpha = 1, glow = 0, glowColor = null, stroke = null, lw = 2 } = o;
  if (alpha <= 0.001 || !s) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  setFont(size, weight, fam);
  ctx.textAlign = align;
  ctx.textBaseline = base;
  if (stroke) {
    ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.lineJoin = 'round';
    if (glow) { ctx.shadowColor = glowColor || stroke; ctx.shadowBlur = glow; }
    ctx.strokeText(s, x, y);
  } else {
    ctx.fillStyle = color;
    if (glow) {
      ctx.shadowColor = glowColor || color; ctx.shadowBlur = glow;
      ctx.fillText(s, x, y);
      ctx.shadowBlur = 0;
    }
    ctx.fillText(s, x, y);
  }
  ctx.restore();
}
// spans: [{s, color, glow, weight, size, fam, alpha, strike}] on one line
function rich(spans, x, y, o = {}) {
  const { size = 40, weight = 700, align = 'left', alpha = 1, fam = 'cjk' } = o;
  const ws = spans.map((sp) => measure(sp.s, sp.size || size, sp.weight || weight, sp.fam || fam));
  const total = ws.reduce((a, b) => a + b, 0);
  let cx = align === 'center' ? x - total / 2 : align === 'right' ? x - total : x;
  spans.forEach((sp, i) => {
    txt(sp.s, cx, y, {
      size: sp.size || size, weight: sp.weight || weight, fam: sp.fam || fam, color: sp.color || COL.cream,
      glow: sp.glow || 0, glowColor: sp.glowColor, alpha: alpha * (sp.alpha ?? 1),
    });
    cx += ws[i];
  });
  return total;
}
function richWidth(spans, size = 40, weight = 700, fam = 'cjk') {
  return spans.reduce((a, sp) => a + measure(sp.s, sp.size || size, sp.weight || weight, sp.fam || fam), 0);
}
// typewriter: p in 0..1 ; cursor blinks
function typeText(s, p, x, y, o = {}, bt = 0) {
  const n = Math.floor(clamp(p) * s.length + 0.0001);
  const shown = s.slice(0, n);
  const cursorOn = p < 1 ? true : Math.floor(bt * 2) % 2 === 0;
  const showCursor = o.cursor !== false && (p < 1 || (o.keepCursor && cursorOn));
  txt(shown + (showCursor ? '_' : ''), x, y, o);
}

// ---------- shapes ----------
function rrect(x, y, w, h, r, fill, stroke, lw = 2) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
}
function circle(x, y, r, fill, stroke, lw = 2) {
  ctx.beginPath();
  ctx.arc(x, y, Math.max(0.01, r), 0, TAU);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
}
function ellipse(x, y, rx, ry, fill, rot = 0) {
  ctx.beginPath();
  ctx.ellipse(x, y, Math.max(0.01, rx), Math.max(0.01, ry), rot, 0, TAU);
  ctx.fillStyle = fill; ctx.fill();
}
function line(x1, y1, x2, y2, color, lw = 2, dash = null) {
  ctx.save();
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);
  ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round';
  if (dash) ctx.setLineDash(dash);
  ctx.stroke();
  ctx.restore();
}
// scale around a point
function withScale(x, y, s, fn) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.translate(-x, -y); fn(); ctx.restore();
}
function withAlpha(a, fn) {
  if (a <= 0.001) return;
  ctx.save(); ctx.globalAlpha *= a; fn(); ctx.restore();
}

// circle with check (p: draw progress 0..1)
function checkBadge(x, y, r, o = {}) {
  const { color = COL.cyan, fill = null, p = 1, lw = 3.5, glow = 0, checkColor = null } = o;
  ctx.save();
  if (glow) { ctx.shadowColor = color; ctx.shadowBlur = glow; }
  const pr = clamp(p / 0.55);
  ctx.beginPath();
  ctx.arc(x, y, r, -Math.PI / 2, -Math.PI / 2 + TAU * pr);
  if (fill && pr >= 1) { ctx.fillStyle = fill; ctx.fill(); }
  ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.stroke();
  const pc = clamp((p - 0.45) / 0.55);
  if (pc > 0) {
    const pts = [[x - r * 0.42, y + r * 0.02], [x - r * 0.1, y + r * 0.32], [x + r * 0.45, y - r * 0.3]];
    const l1 = Math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]);
    const l2 = Math.hypot(pts[2][0] - pts[1][0], pts[2][1] - pts[1][1]);
    const L = (l1 + l2) * pc;
    ctx.beginPath(); ctx.moveTo(...pts[0]);
    if (L <= l1) ctx.lineTo(lerp(pts[0][0], pts[1][0], L / l1), lerp(pts[0][1], pts[1][1], L / l1));
    else { ctx.lineTo(...pts[1]); const q = (L - l1) / l2; ctx.lineTo(lerp(pts[1][0], pts[2][0], q), lerp(pts[1][1], pts[2][1], q)); }
    ctx.strokeStyle = checkColor || color; ctx.lineWidth = lw * 1.25; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.stroke();
  }
  ctx.restore();
}

// ---------- background ----------
const BG_RNG = mulberry32(20190607);
const PARTICLES = Array.from({ length: 90 }, () => ({
  x: BG_RNG() * W, y: BG_RNG() * H, r: 0.7 + BG_RNG() * 1.9, a: 0.12 + BG_RNG() * 0.45,
  sp: 3 + BG_RNG() * 9, ph: BG_RNG() * TAU, tw: 0.6 + BG_RNG() * 1.6,
}));

function drawBackground(t) {
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#0a1330');
  g.addColorStop(0.6, '#0f1c42');
  g.addColorStop(1, '#0a1231');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

  const rg = ctx.createRadialGradient(W / 2, 620, 40, W / 2, 620, 980);
  rg.addColorStop(0, 'rgba(52,98,178,0.20)'); rg.addColorStop(1, 'rgba(52,98,178,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);

  // wall grid
  ctx.save();
  ctx.strokeStyle = 'rgba(95,155,225,0.065)'; ctx.lineWidth = 1;
  ctx.beginPath();
  for (let x = 0; x <= W; x += 64) { ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, HORIZON); }
  for (let y = HORIZON; y >= 0; y -= 64) { ctx.moveTo(0, y + 0.5); ctx.lineTo(W, y + 0.5); }
  ctx.stroke();

  // perspective floor
  ctx.beginPath(); ctx.rect(0, HORIZON, W, H - HORIZON); ctx.clip();
  const fg = ctx.createLinearGradient(0, HORIZON, 0, H);
  fg.addColorStop(0, 'rgba(20,40,85,0.55)'); fg.addColorStop(1, 'rgba(8,16,40,0.2)');
  ctx.fillStyle = fg; ctx.fillRect(0, HORIZON, W, H - HORIZON);
  ctx.lineWidth = 1.2;
  for (let i = -16; i <= 16; i++) {
    const xb = W / 2 + i * 210;
    const a = 0.16 - Math.abs(i) * 0.004;
    ctx.strokeStyle = `rgba(80,180,235,${Math.max(0.04, a)})`;
    ctx.beginPath(); ctx.moveTo(W / 2 + i * 14, HORIZON); ctx.lineTo(xb, H); ctx.stroke();
  }
  const N = 9, phase = (t / (BEAT * 8)) % 1;
  for (let k = 0; k < N + 1; k++) {
    const u = (k + phase) / N;
    const y = HORIZON + (H - HORIZON) * u * u;
    ctx.strokeStyle = `rgba(80,180,235,${0.03 + 0.16 * u})`;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
  }
  ctx.restore();

  // horizon glow line
  const hg = ctx.createLinearGradient(0, 0, W, 0);
  hg.addColorStop(0, 'rgba(70,190,240,0)'); hg.addColorStop(0.5, 'rgba(70,190,240,0.38)'); hg.addColorStop(1, 'rgba(70,190,240,0)');
  ctx.fillStyle = hg; ctx.fillRect(0, HORIZON - 1, W, 2);

  // particles
  for (const p of PARTICLES) {
    const y = (((p.y - t * p.sp) % H) + H) % H;
    const a = p.a * (0.55 + 0.45 * Math.sin(t * p.tw + p.ph));
    ctx.fillStyle = `rgba(170,215,255,${a})`;
    ctx.beginPath(); ctx.arc(p.x, y, p.r, 0, TAU); ctx.fill();
  }

  // vignette
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.05);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,4,15,0.45)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
}

// ---------- chapter bar ----------
const CHAPTERS = [['睡还是背', 0, 15], ['先睡一觉', 15, 32], ['怎么睡', 32, 128], ['照着做', 128, 160]];
function drawChapterBar(bt) {
  const x0 = 120, x1 = 1800, gap = 14, total = 160;
  const avail = x1 - x0 - gap * (CHAPTERS.length - 1);
  let x = x0;
  for (const [name, a, b] of CHAPTERS) {
    const w = (avail * (b - a)) / total;
    const p = clamp((bt - a) / (b - a));
    const active = bt >= a && bt < b;
    const past = bt >= b;
    txt(name, x + 2, 1019, { size: 24, weight: active ? 900 : 700, color: active ? COL.cream : past ? '#a7b2cb' : '#5d6988' });
    rrect(x, 1043, w, 5, 2.5, 'rgba(120,140,185,0.22)');
    if (p > 0) rrect(x, 1043, Math.max(5, w * p), 5, 2.5, COL.cyan);
    if (active) {
      ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 14;
      circle(x + w * p, 1045.5, 5.5, COL.cyanHi);
      ctx.restore();
    }
    x += w + gap;
  }
}
