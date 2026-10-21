// 路人小人：比 people.mjs 里的主角简单，用来做人群、举牌、按按钮这类动作。
// mood 控制表情：-1 难过 → 0 平淡 → 0.6 微笑 → 1 大笑。纯代码绘制，不对应任何真实人物。
// 坐标以脚底中心为原点，scale 1 时约 100px 高。
import { createCanvas } from '@napi-rs/canvas';
import { clamp } from './util.mjs';
import { rr, circle, ellipse } from './draw.mjs';
import { FONT } from './fonts.mjs';

const SKINS = ['#F6D9BC', '#F1CBA4', '#E4B286', '#CF9568', '#AC7149', '#7F5136'];
const HAIRS = ['#2B2422', '#3F2C22', '#6B4A30', '#B98C55', '#A9A6A1'];
const TOPS = ['#3F6FA6', '#E09A46', '#4A9A8E', '#B65D72', '#7B6BB5', '#C9A04B', '#5E8F57', '#D27A57', '#6B7E9E', '#E4DCCB'];
const PANTS = ['#26324C', '#2F2B3F', '#3A4258', '#22303F', '#4A3F37'];
const STYLES = ['short', 'short', 'long', 'bun', 'curly', 'bald'];

/** Arm angles: 0 = straight down, π = straight up (measured outward from the body). */
export const ARM_DOWN = 0.32;
export const ARM_OUT = 1.45;
export const ARM_UP = 2.45;

const SH_X = 12.5;
const SH_Y = -52;
const ARM_LEN = 25;

export function shade(hex, k) {
  const n = parseInt(hex.slice(1), 16);
  const r = Math.round(((n >> 16) & 255) * k);
  const g = Math.round(((n >> 8) & 255) * k);
  const b = Math.round((n & 255) * k);
  return `rgb(${r},${g},${b})`;
}

function luma(hex) {
  const n = parseInt(hex.slice(1), 16);
  return (0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255;
}

/** Random look. `over` pins any field (e.g. { top: '#3F6FA6' }). */
export function makeFolk(rng, over = {}) {
  const pick = (a) => a[Math.floor(rng() * a.length)];
  const hairStyle = over.hairStyle ?? pick(STYLES);
  const hair = hairStyle === 'bald' ? pick(['#A9A6A1', '#D9D5CD', '#3F2C22']) : pick(HAIRS);
  return {
    skin: pick(SKINS),
    hair,
    hairStyle,
    top: pick(TOPS),
    pants: pick(PANTS),
    shoe: '#141924',
    phase: rng() * Math.PI * 2,
    blinkAt: rng() * 4,
    ...over,
  };
}

export function handPos(side, theta) {
  return { x: side * (SH_X + ARM_LEN * Math.sin(theta)), y: SH_Y + ARM_LEN * Math.cos(theta) };
}

function rrFill(ctx, x, y, w, h, r, fill) {
  rr(ctx, x, y, w, h, r);
  ctx.fillStyle = fill;
  ctx.fill();
}

function strokeArm(ctx, side, hand, color) {
  ctx.save();
  ctx.lineCap = 'round';
  ctx.strokeStyle = color;
  ctx.lineWidth = 8;
  ctx.beginPath();
  ctx.moveTo(side * SH_X, SH_Y);
  ctx.lineTo(hand.x, hand.y);
  ctx.stroke();
  ctx.restore();
}

function drawHairBack(ctx, f) {
  if (f.hairStyle === 'long') rrFill(ctx, -22.5, -97, 45, 46, 15, f.hair);
  if (f.hairStyle === 'bun') circle(ctx, 0, -102, 8.5, f.hair);
}

function drawHairFront(ctx, f) {
  const st = f.hairStyle;
  ctx.fillStyle = f.hair;
  if (st === 'short' || st === 'bun') {
    ctx.beginPath();
    ctx.moveTo(-21, -76);
    ctx.bezierCurveTo(-23, -96, -10, -102.5, 1, -102);
    ctx.bezierCurveTo(14, -101.5, 23, -94, 21, -76);
    if (st === 'short') {
      ctx.quadraticCurveTo(19, -86, 12, -88);
      ctx.quadraticCurveTo(2, -84, -6, -89);
      ctx.quadraticCurveTo(-15, -87, -21, -76);
    } else {
      ctx.quadraticCurveTo(17, -90, 0, -91);
      ctx.quadraticCurveTo(-17, -90, -21, -76);
    }
    ctx.closePath();
    ctx.fill();
  } else if (st === 'long') {
    ctx.beginPath();
    ctx.moveTo(-22, -66);
    ctx.bezierCurveTo(-25, -98, -8, -103.5, 2, -102.5);
    ctx.bezierCurveTo(16, -101.5, 25, -92, 22, -66);
    ctx.quadraticCurveTo(19, -84, 7, -90);
    ctx.quadraticCurveTo(-8, -86, -15, -87);
    ctx.quadraticCurveTo(-20, -80, -22, -66);
    ctx.closePath();
    ctx.fill();
  } else if (st === 'curly') {
    ctx.beginPath();
    ctx.ellipse(0, -89, 20.5, 13, 0, Math.PI, Math.PI * 2);
    ctx.fill();
    for (let i = 0; i <= 7; i++) {
      const a = Math.PI * (1 + i / 7);
      circle(ctx, Math.cos(a) * 19, -87 + Math.sin(a) * 14, 6.4, f.hair);
    }
  } else if (st === 'bald') {
    ellipse(ctx, -18.6, -84, 3.6, 7, f.hair);
    ellipse(ctx, 18.6, -84, 3.6, 7, f.hair);
  }
}

function drawFace(ctx, f, mood, look, lookY, blink) {
  const m = clamp(mood, -1, 1);
  const happy = Math.max(0, m);
  const sad = Math.max(0, -m);
  const ex = look * 2;
  const ey = lookY * 1.5;
  const ink = '#262833';
  const dark = luma(f.skin) < 0.5;

  if (m > 0.74) {
    // closed, smiling eyes "^ ^"
    ctx.save();
    ctx.strokeStyle = ink;
    ctx.lineWidth = 1.9;
    ctx.lineCap = 'round';
    for (const sx of [-7, 7]) {
      ctx.beginPath();
      ctx.arc(sx + ex, -76.4 + ey, 3.1, Math.PI * 1.12, Math.PI * 1.88);
      ctx.stroke();
    }
    ctx.restore();
  } else {
    const ry = blink ? 0.45 : 2.9;
    ellipse(ctx, -7 + ex, -78 + ey, 2.3, ry, ink);
    ellipse(ctx, 7 + ex, -78 + ey, 2.3, ry, ink);
  }

  // brows: sad lifts the inner ends, happy lifts both a little
  const bx = ex * 0.5;
  const lift = happy * 0.9;
  ctx.save();
  ctx.strokeStyle = shade(f.hairStyle === 'bald' ? '#6E6A66' : f.hair, 0.85);
  ctx.lineWidth = 1.7;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(-11 + bx, -85.6 + sad * 0.9 - lift);
  ctx.lineTo(-4 + bx, -86.6 - sad * 2 - lift);
  ctx.moveTo(4 + bx, -86.6 - sad * 2 - lift);
  ctx.lineTo(11 + bx, -85.6 + sad * 0.9 - lift);
  ctx.stroke();
  ctx.restore();

  const blush = 0.12 + 0.26 * happy;
  circle(ctx, -12.5, -71.5, 3.4, `rgba(235,120,110,${blush.toFixed(3)})`);
  circle(ctx, 12.5, -71.5, 3.4, `rgba(235,120,110,${blush.toFixed(3)})`);

  const my = -69.5;
  const w = 4 + 1.8 * happy;
  if (m > 0.62) {
    const open = 3.2 + (3 * (m - 0.62)) / 0.38;
    ctx.beginPath();
    ctx.moveTo(-w - 0.5, my - 1.2);
    ctx.quadraticCurveTo(0, my, w + 0.5, my - 1.2);
    ctx.quadraticCurveTo(0, my + open * 1.9, -w - 0.5, my - 1.2);
    ctx.closePath();
    ctx.fillStyle = dark ? '#4A1E1C' : '#7A2F2C';
    ctx.fill();
  } else {
    ctx.save();
    ctx.strokeStyle = dark ? '#4E2622' : '#8A463B';
    ctx.lineWidth = 1.8;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(-w, my - 2 * m);
    ctx.quadraticCurveTo(0, my + 5 * m, w, my - 2 * m);
    ctx.stroke();
    ctx.restore();
  }
}

/** Score paddle held up by one hand. `meter` (0..1) draws a level bar, `text` a big number. */
function drawPaddle(ctx, hand, p) {
  const side = p.side ?? 1;
  const w = p.w ?? 50;
  const h = p.h ?? 40;
  const k = p.k ?? 1;
  const cx = hand.x + (p.dx ?? 11) * side;
  const cy = hand.y - (p.lift ?? 46);
  ctx.save();
  ctx.lineCap = 'round';
  ctx.strokeStyle = '#7E6040';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(hand.x, hand.y + 3);
  ctx.lineTo(cx, cy + (h / 2) * k - 1);
  ctx.stroke();
  ctx.translate(cx, cy);
  ctx.scale(k, k);
  ctx.shadowColor = p.glow ?? 'rgba(255,182,72,0.55)';
  ctx.shadowBlur = 12;
  rr(ctx, -w / 2, -h / 2, w, h, 7);
  ctx.fillStyle = '#F5EFE1';
  ctx.fill();
  ctx.shadowBlur = 0;
  ctx.lineWidth = 1.6;
  ctx.strokeStyle = '#D9A84E';
  ctx.stroke();
  ctx.letterSpacing = '0px';
  if (p.text !== undefined) {
    ctx.fillStyle = '#2A2B36';
    ctx.font = FONT.mono(p.fs ?? 28, 'SemiBold');
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(p.text), p.sub ? -6 : 0, 1.5);
    if (p.sub) {
      ctx.font = FONT.mono(8);
      ctx.fillStyle = 'rgba(42,43,54,0.6)';
      ctx.textAlign = 'right';
      ctx.fillText(p.sub, w / 2 - 5, h / 2 - 7);
    }
  }
  if (p.meter !== undefined) {
    const bw = w - 14;
    const bh = 9;
    rr(ctx, -bw / 2, -bh / 2, bw, bh, bh / 2);
    ctx.fillStyle = 'rgba(42,43,54,0.14)';
    ctx.fill();
    const fw = bw * clamp(p.meter);
    if (fw > 0.5) {
      rr(ctx, -bw / 2, -bh / 2, Math.max(bh, fw), bh, bh / 2);
      ctx.fillStyle = '#E8A93C';
      ctx.fill();
    }
  }
  ctx.restore();
}

/** Phone held upright just above the hand. `lit` (0..1) lights the screen. */
const PHONE_W = 10;
const PHONE_H = 17;
const PHONE_LIFT = 8;

/** Centre of a held phone's screen, in figure units (multiply by scale, add feet position). */
export function phoneCenter(side, theta) {
  const h = handPos(side, theta);
  return { x: h.x, y: h.y - PHONE_LIFT };
}

function drawPhoneProp(ctx, hand, lit) {
  ctx.save();
  ctx.translate(hand.x, hand.y - PHONE_LIFT);
  rr(ctx, -PHONE_W / 2, -PHONE_H / 2, PHONE_W, PHONE_H, 2.6);
  ctx.fillStyle = '#1A2133';
  ctx.fill();
  ctx.lineWidth = 0.9;
  ctx.strokeStyle = 'rgba(220,228,245,0.35)';
  ctx.stroke();
  rr(ctx, -PHONE_W / 2 + 1.4, -PHONE_H / 2 + 1.7, PHONE_W - 2.8, PHONE_H - 3.8, 1.4);
  if (lit > 0) {
    ctx.shadowColor = 'rgba(110,235,200,0.95)';
    ctx.shadowBlur = 10 * lit;
  }
  ctx.fillStyle = lit > 0 ? `rgba(150,240,210,${(0.35 + 0.65 * lit).toFixed(3)})` : '#33405E';
  ctx.fill();
  ctx.restore();
}

/**
 * Draw one folk figure.
 * o: { x, y, s, alpha, mood, look, lookY, armL, armR, t, blink, bob, prop }
 * prop: { kind: 'paddle', side: ±1, text?, sub?, meter?, k?, dx?, lift?, w?, h?, fs? }
 *     | { kind: 'phone', side: ±1, lit?: 0..1 }
 */
export function drawFolk(ctx, f, o = {}) {
  const { x = 0, y = 0, s = 1, alpha = 1, mood = 0.3, look = 0, lookY = 0, bob = 0, prop = null } = o;
  const armL = o.armL ?? ARM_DOWN;
  const armR = o.armR ?? ARM_DOWN;
  if (alpha <= 0 || s <= 0) return;
  const blink = o.blink ?? (o.t !== undefined && (o.t + f.blinkAt) % 4.2 < 0.12);
  const skinShade = shade(f.skin, 0.86);
  const topShade = shade(f.top, 0.8);

  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(x, y);
  ctx.scale(s, s);

  ellipse(ctx, 0, 0, 19, 3.6, 'rgba(0,0,0,0.32)');
  rrFill(ctx, -10, -25, 8.5, 24, 4, f.pants);
  rrFill(ctx, 1.5, -25, 8.5, 24, 4, f.pants);
  ellipse(ctx, -6, -2.4, 6.8, 3.2, f.shoe);
  ellipse(ctx, 6, -2.4, 6.8, 3.2, f.shoe);

  ctx.translate(0, bob);

  const hl = handPos(-1, armL);
  const hr = handPos(1, armR);
  strokeArm(ctx, -1, hl, topShade);
  strokeArm(ctx, 1, hr, topShade);
  const propSide = prop ? (prop.side ?? 1) : 0;
  if (propSide !== -1) circle(ctx, hl.x, hl.y, 4.3, f.skin);
  if (propSide !== 1) circle(ctx, hr.x, hr.y, 4.3, f.skin);

  rrFill(ctx, -16, -58, 32, 37, 11, f.top);
  ctx.save();
  rr(ctx, -16, -58, 32, 37, 11);
  ctx.clip();
  ctx.fillStyle = 'rgba(0,0,0,0.12)';
  ctx.fillRect(7, -60, 12, 42);
  ctx.restore();
  ctx.beginPath();
  ctx.arc(0, -58, 5.5, 0, Math.PI);
  ctx.fillStyle = skinShade;
  ctx.fill();
  rrFill(ctx, -4.5, -64, 9, 8, 3, skinShade);

  drawHairBack(ctx, f);
  if (f.hairStyle !== 'long') {
    circle(ctx, -19.5, -78, 4, f.skin);
    circle(ctx, 19.5, -78, 4, f.skin);
    circle(ctx, -19.5, -78, 2, skinShade);
    circle(ctx, 19.5, -78, 2, skinShade);
  }
  circle(ctx, 0, -79, 20.5, f.skin);
  drawHairFront(ctx, f);
  drawFace(ctx, f, mood, look, lookY, blink);

  if (prop && prop.kind === 'paddle') {
    const hand = propSide === -1 ? hl : hr;
    drawPaddle(ctx, hand, { ...prop, side: propSide });
    circle(ctx, hand.x, hand.y, 4.3, f.skin);
  }
  if (prop && prop.kind === 'phone') {
    const hand = propSide === -1 ? hl : hr;
    drawPhoneProp(ctx, hand, prop.lit ?? 0);
    circle(ctx, hand.x, hand.y, 4.3, f.skin);
  }
  ctx.restore();
}

/* ---------- sprites for crowds: one cached bitmap per figure (fixed pose and mood) ---------- */

const SPR_W = 80;
const SPR_H = 132;
const SPR_OX = 40;
const SPR_OY = 124;

/** Sprites bake one fixed pose: f.mood, f.look, f.lookY, f.armL, f.armR and f.prop (e.g. an unlit phone). */
export function drawFolkSprite(ctx, f, x, y, s, alpha = 1) {
  if (alpha <= 0 || s <= 0) return;
  if (!f.sprite) {
    const c = createCanvas(SPR_W, SPR_H);
    drawFolk(c.getContext('2d'), f, {
      x: SPR_OX,
      y: SPR_OY,
      s: 1,
      mood: f.mood ?? 0.3,
      look: f.look ?? 0,
      lookY: f.lookY ?? 0,
      armL: f.armL,
      armR: f.armR,
      prop: f.prop ?? null,
      blink: false,
    });
    f.sprite = c;
  }
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(f.sprite, x - SPR_OX * s, y - SPR_OY * s, SPR_W * s, SPR_H * s);
  ctx.restore();
}
