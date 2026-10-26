// kid.js — flat cartoon kid sitting behind a desk. Local origin = desk top centre.
const SKIN = '#f8d4b3', SKIN_SH = '#e9b892', INK = '#2b1e17', BLUSH = 'rgba(245,135,135,0.5)';
const KID_STYLE = {
  boy: { hair: '#3a2a20', hairHi: '#4e3a2d', shirt: '#4174bd', shirtDark: '#2f5c9e', collar: '#dbe8f8' },
  girl: { hair: '#5c3a27', hairHi: '#714a33', shirt: '#ad4553', shirtDark: '#8b3441', collar: '#f5ebe6' },
};

// arm keypoints per pose: [elbowL, handL, elbowR, handR]
const ARM_POSES = {
  rest: [[-92, -24], [-50, -8], [92, -24], [50, -8]],
  read: [[-90, -26], [-60, -16], [90, -26], [60, -16]],
  write: [[-92, -24], [-46, -8], [84, -26], [26, -10]],
  sleep: [[-98, -16], [16, -17], [98, -16], [-16, -17]],
  stretch: [[-100, -150], [-50, -226], [100, -150], [50, -226]],
  tap: [[-92, -24], [-50, -8], [126, -44], [168, -22]],
  // point: arm reaches right toward the table at ~30° (a raised arm with one finger up read as a middle finger)
  point: [[-92, -24], [-50, -8], [112, -60], [180, -98]],
  thumb: [[-92, -24], [-50, -8], [104, -52], [100, -116]],
};

function blendArms(o) {
  let pts = ARM_POSES.rest.map((p) => p.slice());
  const apply = (name, w) => {
    if (!w) return;
    const q = ARM_POSES[name];
    pts = pts.map((p, i) => [lerp(p[0], q[i][0], w), lerp(p[1], q[i][1], w)]);
  };
  apply('read', o.read); apply('write', o.write); apply('sleep', o.sleep);
  apply('stretch', o.stretch); apply('tap', o.tap); apply('point', o.point); apply('thumb', o.thumb);
  if (o.write) { // scribble wiggle
    const ph = (o.t || 0) * 9;
    pts[3][0] += Math.sin(ph) * 7 * o.write; pts[3][1] += Math.cos(ph * 1.3) * 2.5 * o.write;
  }
  return pts;
}

// through: 0 = elbow acts as Bezier control point (soft bend), 1 = curve passes through the elbow
function drawArm(st, sx, sy, e, h, kind, through = 0) {
  ctx.save();
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const cx = lerp(e[0], 2 * e[0] - (sx + h[0]) / 2, through), cy = lerp(e[1], 2 * e[1] - (sy + h[1]) / 2, through);
  ctx.beginPath(); ctx.moveTo(sx, sy); ctx.quadraticCurveTo(cx, cy, h[0], h[1]);
  ctx.strokeStyle = st.shirtDark; ctx.lineWidth = 27; ctx.stroke();
  ctx.strokeStyle = st.shirt; ctx.lineWidth = 21; ctx.stroke();
  const [hx, hy] = h;
  if (kind === 'thumb') {
    // 👍: a square fist with curled-finger creases, the thumb rising from its top-left corner (never centred:
    // a single centred digit on a round fist reads as a middle finger)
    ctx.save(); ctx.translate(hx, hy);
    ctx.save(); ctx.translate(-8, -12); ctx.rotate(-0.12); rrect(-6, -26, 12, 28, 6, SKIN, SKIN_SH, 1.5); ctx.restore();
    rrect(-15, -14, 31, 29, 9, SKIN, SKIN_SH, 1.5);
    for (const y of [-5, 2, 9]) line(3, y, 13, y, SKIN_SH, 2.2);
    ctx.restore();
    ctx.restore();
    return;
  }
  if (kind === 'point') {
    // 👉: index finger straight along the forearm, thumb tucked on top of the fist, curled fingers below
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(Math.atan2(h[1] - e[1], h[0] - e[0]));
    rrect(4, -5, 28, 10, 5, SKIN, SKIN_SH, 1.5);
    circle(0, 0, 14, SKIN, SKIN_SH, 1.5);
    ctx.save(); ctx.rotate(-0.5); rrect(1, -15.5, 15, 8, 4, SKIN, SKIN_SH, 1.5); ctx.restore();
    for (const y of [5, 10]) line(-2, y, 9, y - 1, SKIN_SH, 2);
    ctx.restore();
    ctx.restore();
    return;
  }
  circle(hx, hy, 13, SKIN, SKIN_SH, 1.5);
  if (kind === 'pencil') {
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(-0.7);
    rrect(-3, -40, 7, 36, 2, '#f6c445'); rrect(-3, -46, 7, 8, 2, '#f08a9a');
    ctx.beginPath(); ctx.moveTo(-3, -4); ctx.lineTo(4, -4); ctx.lineTo(0.5, 6); ctx.closePath(); ctx.fillStyle = '#e9cfa6'; ctx.fill();
    ctx.restore();
  }
  ctx.restore();
}

function drawEyes(f, type) {
  for (const sx of [-1, 1]) {
    const ex = sx * 22, ey = 8;
    if (f.eyeClose < 0.62) {
      const k = 1 - (f.eyeClose / 0.62) * 0.85;
      ellipse(ex + f.pdx, ey + f.pdy, 6.6, 8.6 * k, INK);
      if (k > 0.55) circle(ex + f.pdx + 2.2, ey + f.pdy - 3, 2.2, '#ffffff');
    } else {
      ctx.save(); ctx.strokeStyle = INK; ctx.lineWidth = 3.6; ctx.lineCap = 'round';
      ctx.beginPath();
      if (f.eyeStyle === 'happy') ctx.arc(ex, ey + 5, 8, Math.PI * 1.15, Math.PI * 1.85);
      else ctx.arc(ex, ey - 3, 8, Math.PI * 0.15, Math.PI * 0.85);
      ctx.stroke();
      ctx.restore();
    }
  }
}

// cleaner brow drawing (worried = inner ends raised)
function drawBrows(f) {
  for (const sx of [-1, 1]) {
    const ex = sx * 22, by = -14 - f.browUp * 3;
    const inner = by - f.worry * 6, outer = by + f.worry * 2;
    line(ex - sx * 7, inner, ex + sx * 7, outer, 'rgba(43,30,23,0.85)', 3.2);
  }
}

function drawMouth(f) {
  const y = 31;
  if (f.mouthOpen > 0.08) {
    const rw = 7 + f.mouthOpen * 6, rh = 3 + f.mouthOpen * 9;
    ellipse(0, y + 2, rw, rh, '#7c2f33');
    ellipse(0, y + 2 + rh * 0.45, rw * 0.6, rh * 0.42, '#e8798a');
  } else {
    ctx.save(); ctx.strokeStyle = '#7c3a33'; ctx.lineWidth = 3.4; ctx.lineCap = 'round';
    ctx.beginPath();
    const s = f.smile;
    if (s >= 0) ctx.arc(0, y - 6 - s * 2, 9 + s * 3, Math.PI * (0.5 - 0.28 - s * 0.08), Math.PI * (0.5 + 0.28 + s * 0.08));
    else ctx.arc(0, y + 10, 8, Math.PI * 1.25, Math.PI * 1.75);
    ctx.stroke(); ctx.restore();
  }
}

function drawHairFront(st, type) {
  ctx.fillStyle = st.hair;
  ctx.beginPath();
  if (type === 'boy') {
    ctx.moveTo(-65, 6);
    ctx.bezierCurveTo(-72, -52, -36, -76, 0, -76);
    ctx.bezierCurveTo(38, -76, 72, -52, 65, 6);
    ctx.quadraticCurveTo(60, -10, 52, -14);
    ctx.quadraticCurveTo(44, -26, 30, -21);
    ctx.quadraticCurveTo(18, -36, 2, -25);
    ctx.quadraticCurveTo(-12, -37, -26, -24);
    ctx.quadraticCurveTo(-42, -32, -50, -16);
    ctx.quadraticCurveTo(-60, -10, -65, 6);
  } else {
    ctx.moveTo(-67, 34);
    ctx.bezierCurveTo(-76, -50, -36, -78, 2, -78);
    ctx.bezierCurveTo(42, -78, 76, -50, 67, 34);
    ctx.quadraticCurveTo(60, 36, 55, 30);
    ctx.quadraticCurveTo(57, -6, 42, -20);
    ctx.quadraticCurveTo(12, -12, -14, -36);
    ctx.quadraticCurveTo(-40, -22, -50, -6);
    ctx.quadraticCurveTo(-56, 14, -55, 30);
    ctx.quadraticCurveTo(-60, 36, -67, 34);
  }
  ctx.closePath(); ctx.fill();
  // shine
  ctx.save(); ctx.strokeStyle = st.hairHi; ctx.lineWidth = 5; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(0, -10, 56, Math.PI * 1.22, Math.PI * 1.42); ctx.stroke(); ctx.restore();
}

function drawHairBack(st) {
  ctx.fillStyle = st.hair;
  ctx.beginPath();
  ctx.moveTo(-72, -6);
  ctx.bezierCurveTo(-80, -92, 80, -92, 72, -6);
  ctx.lineTo(80, 104);
  ctx.quadraticCurveTo(0, 124, -80, 104);
  ctx.closePath(); ctx.fill();
}

function drawHead(o, st, f) {
  // ears
  circle(-60, 9, 11, SKIN, SKIN_SH, 1.5); circle(60, 9, 11, SKIN, SKIN_SH, 1.5);
  ellipse(0, 0, 63, 61, SKIN);
  // cheeks
  ellipse(-36, 27, 11.5, 6.5, BLUSH); ellipse(36, 27, 11.5, 6.5, BLUSH);
  drawEyes(f, o.type);
  drawBrows(f);
  drawMouth(f);
  drawHairFront(st, o.type);
  // sweat drop
  if (f.sweat > 0.01) {
    ctx.save(); ctx.globalAlpha *= f.sweat;
    const sx = 58, sy = -18 + (1 - f.sweat) * -8;
    ctx.beginPath(); ctx.moveTo(sx, sy - 16);
    ctx.quadraticCurveTo(sx + 11, sy + 2, sx, sy + 6); ctx.quadraticCurveTo(sx - 11, sy + 2, sx, sy - 16);
    ctx.fillStyle = '#9fe2f7'; ctx.fill(); ctx.strokeStyle = '#5cc3e6'; ctx.lineWidth = 2; ctx.stroke();
    ctx.restore();
  }
  // sleep bubble
  if (f.bubble > 0.01) {
    const r = f.bubble;
    ctx.save();
    circle(14, 22 + r * 0.2, r, 'rgba(190,230,255,0.28)', 'rgba(215,240,255,0.75)', 2);
    circle(14 - r * 0.35, 22 - r * 0.25, r * 0.22, 'rgba(255,255,255,0.8)');
    ctx.restore();
  }
}

// held, open book facing viewer. flip: 0..1 progress of a page turning (right -> left)
function drawHeldBook(cx, cy, w, h, color, flip, openK = 1) {
  const hw = (w / 2) * openK;
  rrect(cx - hw - 7, cy - h / 2 - 5, hw * 2 + 14, h + 11, 6, color);
  ctx.fillStyle = '#f7f4ec';
  // left page
  ctx.beginPath();
  ctx.moveTo(cx, cy - h / 2 + 5); ctx.quadraticCurveTo(cx - hw * 0.5, cy - h / 2 - 3, cx - hw, cy - h / 2);
  ctx.lineTo(cx - hw, cy + h / 2); ctx.quadraticCurveTo(cx - hw * 0.5, cy + h / 2 - 4, cx, cy + h / 2 + 3); ctx.closePath(); ctx.fill();
  // right page
  ctx.beginPath();
  ctx.moveTo(cx, cy - h / 2 + 5); ctx.quadraticCurveTo(cx + hw * 0.5, cy - h / 2 - 3, cx + hw, cy - h / 2);
  ctx.lineTo(cx + hw, cy + h / 2); ctx.quadraticCurveTo(cx + hw * 0.5, cy + h / 2 - 4, cx, cy + h / 2 + 3); ctx.closePath(); ctx.fill();
  // text lines
  if (openK > 0.5) {
    ctx.save(); ctx.strokeStyle = 'rgba(120,130,160,0.55)'; ctx.lineWidth = 3; ctx.lineCap = 'round';
    for (let i = 0; i < 4; i++) {
      const y = cy - h / 2 + 16 + i * 14;
      ctx.beginPath(); ctx.moveTo(cx - hw + 12, y); ctx.lineTo(cx - 10 - (i % 2) * 10, y); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx + 10, y); ctx.lineTo(cx + hw - 12 - (i % 3) * 8, y); ctx.stroke();
    }
    ctx.restore();
  }
  line(cx, cy - h / 2 + 5, cx, cy + h / 2 + 3, 'rgba(140,130,120,0.6)', 2);
  if (flip > 0 && flip < 1) {
    const c = Math.cos(Math.PI * flip);
    const pw = hw * c;
    ctx.beginPath();
    ctx.moveTo(cx, cy - h / 2 + 5); ctx.lineTo(cx + pw, cy - h / 2 - 6 * Math.sin(Math.PI * flip));
    ctx.lineTo(cx + pw, cy + h / 2 - 6 * Math.sin(Math.PI * flip)); ctx.lineTo(cx, cy + h / 2 + 3); ctx.closePath();
    ctx.fillStyle = c > 0 ? '#e9e4d8' : '#fbf9f3'; ctx.fill();
    ctx.strokeStyle = 'rgba(140,130,120,0.5)'; ctx.lineWidth = 1.5; ctx.stroke();
  }
}

function drawDesk(w) {
  const hw = w / 2;
  ctx.fillStyle = '#82563a'; ctx.fillRect(-hw + 14, 14, w - 28, 96);
  ctx.fillStyle = '#6c472f'; ctx.fillRect(-hw + 14, 14, w - 28, 7);
  rrect(-hw, -3, w, 19, 4, '#a9774f');
  ctx.fillStyle = '#c38d60'; ctx.fillRect(-hw + 3, -3, w - 6, 4);
}

// o: { x, y, s, type, t, sleep, stretch, read, write, tap, point, thumb, worry, happy, blink, talk,
//      flip, alpha, deskW, deskProps(fn), bookColor, pencil, bob }
function drawKid(o) {
  const st = KID_STYLE[o.type];
  const sleep = o.sleep || 0, stretch = o.stretch || 0, read = o.read || 0, write = o.write || 0;
  const t = o.t || 0;
  const breath = Math.sin(t * TAU / (BEAT * 4)) * (1.2 + sleep * 1.6);
  ctx.save();
  ctx.translate(o.x, o.y);
  ctx.scale(o.s, o.s);
  ctx.globalAlpha *= o.alpha ?? 1;

  // head transform
  let hx = 0, hy = -130, hr = 0;
  hy = lerp(hy, -134, read);
  hx = lerp(hx, 4, write); hy = lerp(hy, -122, write); hr = lerp(hr, 0.07, write);
  hy = lerp(hy, -136, stretch); hr = lerp(hr, -0.05, stretch);
  hx = lerp(hx, 10, sleep); hy = lerp(hy, -64, sleep); hr = lerp(hr, 0.32, sleep);
  hy += breath * 0.6;
  hr += (o.headTilt || 0);
  const sh = lerp(-72, -54, sleep) + lerp(0, -6, stretch) + breath * 0.4;

  // chair back
  rrect(-86, -160, 172, 178, 20, '#44506a');
  rrect(-80, -158, 160, 8, 4, '#55627f');

  // back hair (girl)
  if (o.type === 'girl') {
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(hr); drawHairBack(st); ctx.restore();
  }

  // torso
  ctx.fillStyle = st.shirt;
  ctx.beginPath();
  ctx.moveTo(-76, 16); ctx.lineTo(-72, sh + 30);
  ctx.quadraticCurveTo(-70, sh, -38, sh); ctx.lineTo(38, sh);
  ctx.quadraticCurveTo(70, sh, 72, sh + 30); ctx.lineTo(76, 16); ctx.closePath(); ctx.fill();
  // neck + collar
  if (sleep < 0.7) {
    rrect(-13, sh - 18, 26, 26, 6, SKIN_SH);
    ctx.fillStyle = st.collar;
    ctx.beginPath(); ctx.moveTo(-26, sh); ctx.quadraticCurveTo(0, sh + 26, 26, sh); ctx.lineTo(16, sh); ctx.quadraticCurveTo(0, sh + 13, -16, sh); ctx.closePath(); ctx.fill();
  }

  // desk + desk props
  drawDesk(o.deskW || 440);
  if (o.deskProps) o.deskProps();

  const arms = blendArms(o);
  const shoulderL = [-56, sh + 16], shoulderR = [56, sh + 16];
  const handR = o.thumb > 0.5 ? 'thumb' : o.point > 0.5 ? 'point' : (o.pencil && write > 0.5) ? 'pencil' : null;
  const thr = clamp(sleep * 1.2) * 0.85;
  const drawArms = () => {
    drawArm(st, shoulderL[0], shoulderL[1], arms[0], arms[1], null, thr);
    drawArm(st, shoulderR[0], shoulderR[1], arms[2], arms[3], handR, thr);
  };

  // face params
  const blink = o.blink || 0;
  const eyeClose = Math.max(sleep, stretch, blink, o.eyesHappy || 0);
  const f = {
    eyeClose,
    eyeStyle: stretch > sleep || (o.eyesHappy || 0) > 0.5 ? 'happy' : 'sleep',
    pdx: write * 2, pdy: read * 3 + write * 3,
    smile: lerp(lerp(0.45, -1, o.worry || 0), 1, o.happy || 0),
    mouthOpen: Math.max(stretch * 0.9, (o.talk || 0)),
    worry: o.worry || 0,
    browUp: stretch * 0.6 + (o.worry || 0) * 0.3,
    sweat: o.worry || 0,
    bubble: o.bubble || 0,
  };

  const armsBehindHead = sleep > 0.5;
  if (armsBehindHead) drawArms();
  ctx.save(); ctx.translate(hx, hy); ctx.rotate(hr); drawHead(o, st, f); ctx.restore();
  if (read > 0.02) {
    const by = lerp(-10, -38, EASE.out(read));
    ctx.save(); ctx.globalAlpha *= clamp(read * 3);
    drawHeldBook(0, by, 134, 72, o.bookColor || '#7b5fd6', o.flip || 0, lerp(0.35, 1, clamp(read * 1.4)));
    ctx.restore();
  }
  if (!armsBehindHead) drawArms();
  ctx.restore();

  // Zz (screen space, above head)
  if (sleep > 0.6 && o.zz !== false) {
    const a = clamp((sleep - 0.6) / 0.4);
    const bx = o.x + (hx + 70) * o.s, by = o.y + (hy - 40) * o.s;
    for (let i = 0; i < 3; i++) {
      const ph = ((t / (BEAT * 4)) + i / 3) % 1;
      txt('Z', bx + ph * 46 * o.s + i * 6, by - ph * 90 * o.s, {
        size: (22 + ph * 26) * o.s, weight: 800, fam: 'mono', color: COL.cyanHi,
        alpha: a * Math.sin(Math.PI * ph) * (o.alpha ?? 1), glow: 10,
      });
    }
  }
  return { headX: o.x + hx * o.s, headY: o.y + hy * o.s };
}
