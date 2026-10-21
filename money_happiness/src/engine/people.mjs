// 扁平小人：纯代码绘制，形象是通用卡通人物，不追求还原真人长相。
import { rr, circle, ellipse } from './draw.mjs';

export const PEOPLE = {
  kahneman: {
    zh: '卡尼曼',
    tag: 'NOBEL · 2002',
    skin: '#F2CDAA',
    skinShade: '#DFAF8A',
    hair: '#C9CBD1',
    brow: '#8E9099',
    hairStyle: 'receding',
    glasses: true,
    beard: false,
    top: '#3F6FA6',
    topShade: '#335C8C',
    topStyle: 'blazer',
    shirt: '#ECE6DA',
    pants: '#26324C',
    shoe: '#141A29',
    phase: 0.3,
    blink: 1.7,
  },
  deaton: {
    zh: '迪顿',
    tag: 'NOBEL · 2015',
    skin: '#F4D0AE',
    skinShade: '#E1B48E',
    hair: '#EEEBE4',
    brow: '#D3CEC4',
    hairStyle: 'full',
    glasses: false,
    beard: true,
    top: '#E09A46',
    topShade: '#C5833A',
    topStyle: 'sweater',
    shirt: '#F3EFE6',
    pants: '#2A3550',
    shoe: '#141A29',
    phase: 1.9,
    blink: 2.9,
  },
  killingsworth: {
    zh: '基林斯沃思',
    tag: '2021',
    skin: '#F1CBA6',
    skinShade: '#DDAD86',
    hair: '#4A3426',
    brow: '#3E2C22',
    hairStyle: 'short',
    glasses: false,
    beard: false,
    top: '#3E9C93',
    topShade: '#33827A',
    topStyle: 'tee',
    shirt: '#EAF4F1',
    pants: '#2A3550',
    shoe: '#141A29',
    phase: 1.1,
    blink: 0.9,
  },
};

function rrFill(ctx, x, y, w, h, r, fill) {
  rr(ctx, x, y, w, h, r);
  ctx.fillStyle = fill;
  ctx.fill();
}

function tri(ctx, ax, ay, bx, by, cx, cy, fill) {
  ctx.beginPath();
  ctx.moveTo(ax, ay);
  ctx.lineTo(bx, by);
  ctx.lineTo(cx, cy);
  ctx.closePath();
  ctx.fillStyle = fill;
  ctx.fill();
}

function drawHair(ctx, p) {
  ctx.fillStyle = p.hair;
  if (p.hairStyle === 'receding') {
    ellipse(ctx, -41, -306, 10, 18, p.hair);
    ellipse(ctx, 41, -306, 10, 18, p.hair);
    ctx.beginPath();
    ctx.arc(0, -296, 47, Math.PI * 1.08, Math.PI * 1.92);
    ctx.arc(0, -301, 41, Math.PI * 1.9, Math.PI * 1.1, true);
    ctx.closePath();
    ctx.fillStyle = p.hair;
    ctx.fill();
  } else if (p.hairStyle === 'full') {
    ctx.beginPath();
    ctx.arc(0, -296, 48, Math.PI, Math.PI * 2);
    ctx.quadraticCurveTo(44, -318, 22, -320);
    ctx.quadraticCurveTo(4, -312, -8, -322);
    ctx.quadraticCurveTo(-34, -324, -48, -296);
    ctx.closePath();
    ctx.fillStyle = p.hair;
    ctx.fill();
    rrFill(ctx, -48, -306, 9, 22, 4, p.hair);
    rrFill(ctx, 39, -306, 9, 22, 4, p.hair);
  } else if (p.hairStyle === 'short') {
    ctx.beginPath();
    ctx.moveTo(-47, -289);
    ctx.bezierCurveTo(-51.5, -334, -22.4, -348.6, 2.2, -347.5);
    ctx.bezierCurveTo(31.4, -346.4, 51.5, -329.6, 47, -288.5);
    ctx.quadraticCurveTo(42.6, -311, 26.9, -315.5);
    ctx.quadraticCurveTo(4.5, -306.6, -13.4, -317.8);
    ctx.quadraticCurveTo(-33.6, -313.3, -47, -289);
    ctx.closePath();
    ctx.fillStyle = p.hair;
    ctx.fill();
  }
}

function drawBeard(ctx, p) {
  ctx.beginPath();
  ctx.moveTo(-45, -292);
  ctx.quadraticCurveTo(-46, -246, 0, -238);
  ctx.quadraticCurveTo(46, -246, 45, -292);
  ctx.lineTo(34, -288);
  ctx.quadraticCurveTo(28, -266, 12, -266);
  ctx.quadraticCurveTo(0, -262, -12, -266);
  ctx.quadraticCurveTo(-28, -266, -34, -288);
  ctx.closePath();
  ctx.fillStyle = p.hair;
  ctx.fill();
  ellipse(ctx, 0, -281, 13, 4.5, p.hair);
}

/**
 * Draw a flat character. Feet at (p.x, p.y), ~345px tall at scale 1.
 */
export function drawPerson(ctx, p, t, alpha = 1) {
  if (alpha <= 0) return;
  const s = p.s ?? 1;
  const bob = Math.sin(t * 1.7 + p.phase) * 1.6;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(p.x, p.y);
  ctx.scale(s, s);

  ellipse(ctx, 0, 0, 66, 9, 'rgba(0,0,0,0.35)');

  // legs + shoes
  rrFill(ctx, -29, -126, 25, 118, 9, p.pants);
  rrFill(ctx, 4, -126, 25, 118, 9, p.pants);
  ellipse(ctx, -18, -7, 21, 9.5, p.shoe);
  ellipse(ctx, 18, -7, 21, 9.5, p.shoe);

  ctx.translate(0, bob);

  // arms behind torso
  rrFill(ctx, -77, -226, 25, 108, 12, p.topShade);
  rrFill(ctx, 52, -226, 25, 108, 12, p.topShade);
  circle(ctx, -64.5, -116, 11.5, p.skin);
  circle(ctx, 64.5, -116, 11.5, p.skin);

  // torso
  rrFill(ctx, -58, -238, 116, 126, 26, p.top);
  ctx.save();
  rr(ctx, -58, -238, 116, 126, 26);
  ctx.clip();
  ctx.fillStyle = 'rgba(0,0,0,0.10)';
  ctx.fillRect(16, -238, 50, 130);
  if (p.topStyle === 'sweater') {
    ctx.fillStyle = 'rgba(0,0,0,0.13)';
    ctx.fillRect(-58, -128, 116, 16);
  }
  ctx.restore();

  if (p.topStyle === 'blazer') {
    tri(ctx, -21, -238, 21, -238, 0, -186, p.shirt);
    ctx.strokeStyle = 'rgba(0,0,0,0.22)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(-26, -236);
    ctx.lineTo(0, -184);
    ctx.lineTo(26, -236);
    ctx.stroke();
    circle(ctx, 0, -168, 3, 'rgba(0,0,0,0.28)');
    circle(ctx, 0, -146, 3, 'rgba(0,0,0,0.28)');
  } else if (p.topStyle === 'sweater') {
    tri(ctx, -19, -240, -2, -240, -10, -222, p.shirt);
    tri(ctx, 2, -240, 19, -240, 10, -222, p.shirt);
  } else if (p.topStyle === 'tee') {
    ctx.beginPath();
    ctx.arc(0, -238, 15, 0, Math.PI);
    ctx.fillStyle = p.skinShade;
    ctx.fill();
    ctx.strokeStyle = p.topShade;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(0, -238, 16, 0.05 * Math.PI, 0.95 * Math.PI);
    ctx.stroke();
  }

  // neck, ears, head
  rrFill(ctx, -11, -256, 22, 22, 6, p.skinShade);
  circle(ctx, -46, -292, 10, p.skin);
  circle(ctx, 46, -292, 10, p.skin);
  circle(ctx, -46, -292, 5, p.skinShade);
  circle(ctx, 46, -292, 5, p.skinShade);
  circle(ctx, 0, -296, 46, p.skin);

  drawHair(ctx, p);
  if (p.beard) drawBeard(ctx, p);

  // face
  const blinking = (t + p.blink) % 4.2 < 0.12;
  const eyeRy = blinking ? 0.8 : 5.4;
  // look: -1..1 shifts the pupils sideways (characters facing each other).
  const ex = (p.look ?? 0) * 3.5;
  ellipse(ctx, -16 + ex, -290, 4.4, eyeRy, '#272A36');
  ellipse(ctx, 16 + ex, -290, 4.4, eyeRy, '#272A36');
  // browTilt > 0 lowers the inner ends (determined); 0 keeps the original brows.
  const bt = p.browTilt ?? 0;
  ctx.strokeStyle = p.brow;
  ctx.lineWidth = 3;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(-23, -306 - bt);
  ctx.lineTo(-10, -308 + bt * 4);
  ctx.moveTo(10, -308 + bt * 4);
  ctx.lineTo(23, -306 - bt);
  ctx.stroke();
  circle(ctx, -27, -275, 7, 'rgba(235,120,110,0.22)');
  circle(ctx, 27, -275, 7, 'rgba(235,120,110,0.22)');
  ctx.strokeStyle = '#9A5A4A';
  ctx.lineWidth = 2.6;
  ctx.beginPath();
  if (p.mood === undefined) {
    ctx.arc(0, -277, 7, 0.2 * Math.PI, 0.8 * Math.PI);
  } else {
    // mood: -1 frown … 0 flat … 1 wide smile
    const m = p.mood;
    const w = 6 + 2 * Math.max(0, m);
    ctx.moveTo(-w, -272.5 - 2.6 * m);
    ctx.quadraticCurveTo(0, -272.5 + 7 * m, w, -272.5 - 2.6 * m);
  }
  ctx.stroke();

  if (p.glasses) {
    ctx.strokeStyle = '#2C2F3A';
    ctx.lineWidth = 2.6;
    ctx.beginPath();
    ctx.arc(-16, -290, 12.5, 0, Math.PI * 2);
    ctx.moveTo(28.5, -290);
    ctx.arc(16, -290, 12.5, 0, Math.PI * 2);
    ctx.moveTo(-3.5, -291);
    ctx.lineTo(3.5, -291);
    ctx.stroke();
  }
  ctx.restore();
}
