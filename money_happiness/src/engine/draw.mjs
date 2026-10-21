import { createCanvas } from '@napi-rs/canvas';
import { W, H, clamp, ease, env, mulberry32 } from './util.mjs';
import { FONT } from './fonts.mjs';

export const C = {
  gold: '#F4C46A',
  goldGlow: 'rgba(255,182,72,0.85)',
  cyan: '#62D4FF',
  cyanGlow: 'rgba(70,195,255,0.85)',
  white: '#F3F1EC',
  dim: 'rgba(214,220,234,0.55)',
  faint: 'rgba(214,220,234,0.38)',
  line: 'rgba(232,206,150,0.5)',
  coral: '#FF8A7A',
  coralGlow: 'rgba(255,120,95,0.9)',
};

/* ---------- path helpers ---------- */

export function rr(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.arcTo(x + w, y, x + w, y + r, r);
  ctx.lineTo(x + w, y + h - r);
  ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
  ctx.lineTo(x + r, y + h);
  ctx.arcTo(x, y + h, x, y + h - r, r);
  ctx.lineTo(x, y + r);
  ctx.arcTo(x, y, x + r, y, r);
  ctx.closePath();
}

export function circle(ctx, x, y, r, fill) {
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fillStyle = fill;
  ctx.fill();
}

export function ellipse(ctx, x, y, rx, ry, fill) {
  ctx.beginPath();
  ctx.ellipse(x, y, Math.max(0.01, rx), Math.max(0.01, ry), 0, 0, Math.PI * 2);
  ctx.fillStyle = fill;
  ctx.fill();
}

/* ---------- background ---------- */

let bgCache = null;

function buildBackground() {
  const c = createCanvas(W, H);
  const g = c.getContext('2d');
  const base = g.createRadialGradient(960, 470, 60, 960, 540, 1250);
  base.addColorStop(0, '#111d33');
  base.addColorStop(0.55, '#0b1324');
  base.addColorStop(1, '#05080f');
  g.fillStyle = base;
  g.fillRect(0, 0, W, H);

  g.strokeStyle = 'rgba(150,175,220,0.05)';
  g.lineWidth = 1;
  for (let x = 0; x <= W; x += 120) {
    g.beginPath();
    g.moveTo(x + 0.5, 0);
    g.lineTo(x + 0.5, H);
    g.stroke();
  }
  for (let y = 60; y <= H; y += 120) {
    g.beginPath();
    g.moveTo(0, y + 0.5);
    g.lineTo(W, y + 0.5);
    g.stroke();
  }

  const vig = g.createRadialGradient(960, 540, 320, 960, 540, 1150);
  vig.addColorStop(0, 'rgba(0,0,0,0)');
  vig.addColorStop(1, 'rgba(0,0,0,0.62)');
  g.fillStyle = vig;
  g.fillRect(0, 0, W, H);

  // Static dither baked into the background: breaks up 8-bit banding in the dark gradient.
  // It never changes between frames, so the encoder gets it almost for free.
  const img = g.getImageData(0, 0, W, H);
  const d = img.data;
  const rnd = mulberry32(99);
  for (let i = 0; i < d.length; i += 4) {
    const n = (rnd() + rnd() - 1) * DITHER; // triangular noise
    d[i] = clamp(d[i] + n, 0, 255);
    d[i + 1] = clamp(d[i + 1] + n, 0, 255);
    d[i + 2] = clamp(d[i + 2] + n, 0, 255);
  }
  g.putImageData(img, 0, 0);
  return c;
}

// ±2 levels. Per-frame animated grain was tried and dropped: it pushed the encode to ~70 Mbps
// and, at sane CRF values, x264 smeared it into blocky artifacts.
const DITHER = 2;

const BOKEH = [
  { x: 210, y: 330, r: 80, a: 0.05 },
  { x: 300, y: 790, r: 48, a: 0.045 },
  { x: 1710, y: 250, r: 95, a: 0.035 },
  { x: 1620, y: 830, r: 60, a: 0.04 },
  { x: 1180, y: 120, r: 42, a: 0.025 },
];

export function drawBackground(ctx, t) {
  if (!bgCache) bgCache = buildBackground();
  ctx.drawImage(bgCache, 0, 0);
  BOKEH.forEach((b, i) => {
    const x = b.x + Math.sin(t * 0.15 + i) * 18;
    const y = b.y + Math.cos(t * 0.12 + i * 1.7) * 12;
    const g = ctx.createRadialGradient(x, y, 0, x, y, b.r);
    g.addColorStop(0, `rgba(180,200,235,${b.a})`);
    g.addColorStop(1, 'rgba(180,200,235,0)');
    ctx.fillStyle = g;
    ctx.fillRect(x - b.r, y - b.r, b.r * 2, b.r * 2);
  });
}

/* ---------- ambient dust ---------- */

const DUST = (() => {
  const r = mulberry32(7);
  return Array.from({ length: 70 }, () => ({
    x: r() * W,
    y: r() * H,
    s: 0.8 + r() * 1.6,
    a: 0.06 + r() * 0.16,
    v: 6 + r() * 14,
    ph: r() * Math.PI * 2,
  }));
})();

export function drawDust(ctx, t) {
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (const d of DUST) {
    const y = (((d.y - t * d.v) % H) + H) % H;
    const x = d.x + Math.sin(t * 0.3 + d.ph) * 12;
    const a = d.a * (0.6 + 0.4 * Math.sin(t * 1.3 + d.ph));
    ctx.fillStyle = `rgba(200,215,240,${a.toFixed(3)})`;
    ctx.beginPath();
    ctx.arc(x, y, d.s, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

/* ---------- text ---------- */

export function glowText(ctx, text, x, y, o = {}) {
  const {
    font,
    color = C.white,
    glow = null,
    blur = 24,
    passes = 1,
    alpha = 1,
    align = 'center',
    baseline = 'alphabetic',
    letterSpacing = 0,
  } = o;
  if (alpha <= 0 || !text) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.font = font;
  ctx.textAlign = align;
  ctx.textBaseline = baseline;
  ctx.letterSpacing = `${letterSpacing}px`;
  ctx.fillStyle = color;
  if (glow) {
    ctx.shadowColor = glow;
    ctx.shadowBlur = blur;
    for (let i = 0; i < passes; i++) ctx.fillText(text, x, y);
    ctx.shadowBlur = 0;
  }
  ctx.fillText(text, x, y);
  ctx.restore();
}

/**
 * Big numbers with fixed-width digit cells, so count-up animations don't jitter
 * even with the proportional serif figures.
 */
export function drawFixedDigits(ctx, str, cx, cy, o = {}) {
  const { font, alpha = 1, sepPad = 0.14 } = o;
  ctx.save();
  ctx.font = font;
  ctx.letterSpacing = '0px';
  const cell = ctx.measureText('0').width;
  // Separators get extra air on both sides; the serif comma is narrow and collides with "4" and "9".
  const widthOf = (ch) =>
    /\d/.test(ch) ? cell : ctx.measureText(ch).width + (/[,.]/.test(ch) ? cell * sepPad * 2 : 0);
  const chars = [...str];
  const total = chars.reduce((s, ch) => s + widthOf(ch), 0);
  ctx.restore();
  if (alpha <= 0) return total;
  let x = cx - total / 2;
  for (const ch of chars) {
    const w = widthOf(ch);
    glowText(ctx, ch, x + w / 2, cy, { ...o, align: 'center', baseline: 'middle' });
    x += w;
  }
  return total;
}

/** Bilingual subtitle block: Chinese serif + English italic underneath. */
export function drawSubtitles(ctx, t, cues) {
  for (const c of cues) {
    if (!c.zh) continue;
    const a = env(t, c.t0, c.t1, 0.2, 0.16);
    if (a <= 0) continue;
    const k = clamp((t - c.t0) / 0.32);
    const rise = (1 - ease.outCubic(k)) * 10;
    const blur = (1 - clamp((t - c.t0) / 0.2)) * 5;
    ctx.save();
    if (blur > 0.2) ctx.filter = `blur(${blur.toFixed(2)}px)`;
    glowText(ctx, c.zh, 960, 908 + rise, {
      font: FONT.zh(46),
      color: C.white,
      glow: 'rgba(255,255,255,0.18)',
      blur: 14,
      alpha: a,
    });
    glowText(ctx, c.en, 960, 952 + rise, {
      font: FONT.en(24),
      color: 'rgba(226,226,236,0.58)',
      alpha: a,
    });
    ctx.restore();
  }
}

/** Top-left chapter mark + two-line label (our own mark, not the reference channel's). */
export function drawChapterLabel(ctx, line1, line2, alpha) {
  if (alpha <= 0) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = 'rgba(205,212,228,0.38)';
  ctx.beginPath();
  ctx.arc(118, 120, 30, 0, Math.PI * 2);
  ctx.stroke();
  ctx.strokeStyle = 'rgba(244,196,106,0.6)';
  ctx.beginPath();
  ctx.arc(118, 120, 17, -Math.PI * 0.85, Math.PI * 0.35);
  ctx.stroke();
  ctx.shadowColor = C.goldGlow;
  ctx.shadowBlur = 10;
  circle(ctx, 118, 120, 4, C.gold);
  ctx.shadowBlur = 0;
  ctx.restore();
  glowText(ctx, line1, 170, 113, {
    font: FONT.mono(19),
    color: 'rgba(214,220,234,0.72)',
    align: 'left',
    letterSpacing: 2,
    alpha,
  });
  glowText(ctx, line2, 170, 142, {
    font: FONT.mono(14),
    color: 'rgba(214,220,234,0.42)',
    align: 'left',
    letterSpacing: 4,
    alpha,
  });
}

/** Rounded citation pill, e.g. "Kahneman & Deaton · 2010 · 45 万份问卷   PNAS". */
export function drawPill(ctx, text, tag, cx, cy, alpha) {
  if (alpha <= 0) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.font = FONT.zh(26);
  ctx.letterSpacing = '0px';
  const w1 = ctx.measureText(text).width;
  ctx.font = FONT.mono(13);
  ctx.letterSpacing = '3px';
  const w2 = ctx.measureText(tag).width;
  const pad = 30;
  const gap = 22;
  const h = 56;
  const w = pad + w1 + gap + w2 + pad;
  const x = cx - w / 2;
  const y = cy - h / 2;
  rr(ctx, x, y, w, h, h / 2);
  ctx.fillStyle = 'rgba(8,12,22,0.55)';
  ctx.fill();
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = 'rgba(235,215,170,0.42)';
  ctx.stroke();
  ctx.restore();
  glowText(ctx, text, x + pad, cy + 1, {
    font: FONT.zh(26),
    color: '#EDE7DA',
    align: 'left',
    baseline: 'middle',
    alpha,
  });
  glowText(ctx, tag, x + pad + w1 + gap, cy + 1, {
    font: FONT.mono(13),
    color: 'rgba(235,215,170,0.62)',
    align: 'left',
    baseline: 'middle',
    letterSpacing: 3,
    alpha,
  });
}

/** Teal glow band + warm floor line that characters stand on. */
export function drawStage(ctx, floorY, alpha) {
  if (alpha <= 0) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.save();
  ctx.translate(960, floorY - 60);
  ctx.scale(1, 0.2);
  const band = ctx.createRadialGradient(0, 0, 0, 0, 0, 720);
  band.addColorStop(0, 'rgba(70,160,160,0.30)');
  band.addColorStop(1, 'rgba(70,160,160,0)');
  ctx.fillStyle = band;
  ctx.fillRect(-720, -720, 1440, 1440);
  ctx.restore();
  const lg = ctx.createLinearGradient(420, 0, 1500, 0);
  lg.addColorStop(0, 'rgba(232,210,160,0)');
  lg.addColorStop(0.5, 'rgba(232,210,160,0.55)');
  lg.addColorStop(1, 'rgba(232,210,160,0)');
  ctx.fillStyle = lg;
  ctx.fillRect(420, floorY - 1, 1080, 2);
  ctx.restore();
}

/** Stroke a polyline up to `progress` (0..1) with glow; returns the head point. */
export function strokeGlowPath(ctx, pts, progress, o = {}) {
  if (progress <= 0 || pts.length < 2) return null;
  const { color = C.cyan, glow = C.cyanGlow, width = 3, blur = 18, core = true } = o;
  const n = pts.length - 1;
  const f = clamp(progress) * n;
  const k = Math.floor(f);
  const frac = f - k;
  ctx.save();
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i <= k; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  let head = pts[k];
  if (k < n) {
    head = [pts[k][0] + (pts[k + 1][0] - pts[k][0]) * frac, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * frac];
    ctx.lineTo(head[0], head[1]);
  }
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.shadowColor = glow;
  ctx.shadowBlur = blur;
  ctx.stroke();
  ctx.shadowBlur = 0;
  if (core) {
    ctx.lineWidth = width * 0.4;
    ctx.strokeStyle = 'rgba(255,255,255,0.6)';
    ctx.stroke();
  }
  ctx.restore();
  return head;
}

export function glowDot(ctx, x, y, r, color, glow, alpha = 1) {
  if (alpha <= 0) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.shadowColor = glow;
  ctx.shadowBlur = r * 3.5;
  circle(ctx, x, y, r, color);
  ctx.shadowBlur = 0;
  circle(ctx, x, y, r * 0.45, 'rgba(255,255,255,0.85)');
  ctx.restore();
}

/** Decaying camera shake: sum of impulses. */
export function shakeAt(t, shakes) {
  let x = 0;
  let y = 0;
  for (const s of shakes) {
    const d = t - s.t0;
    if (d < 0 || d > s.dur) continue;
    const k = 1 - d / s.dur;
    x += s.amp * k * Math.sin(d * 70);
    y += s.amp * k * Math.cos(d * 53);
  }
  return { x, y };
}
