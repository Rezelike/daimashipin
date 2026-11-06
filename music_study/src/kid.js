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
  // music_study: the right hand on the screen of the phone standing on his desk (drawDeskPhoneLocal at x = 166)
  phone: [[-92, -24], [-50, -8], [118, -48], [152, -62]],
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
  apply('phone', o.phone);
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

// a small word card held up in both hands (bedtime_words, after the opening); flip 0..1 turns it over
function drawHeldCard(cx, cy, flip, color) {
  const k = Math.abs(Math.cos(Math.PI * flip)), back = flip > 0.5 && flip < 1;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(Math.max(0.03, k), 1);
  rrect(-60, -38, 120, 76, 10, back ? '#fff1c9' : '#f7f4ec', 'rgba(120,130,160,0.5)', 2);
  if (color) rrect(-60, -38, 120, 12, [10, 10, 0, 0], color);
  line(-34, -4, 34, -4, 'rgba(60,70,100,0.55)', 6); line(-34, 14, 12, 14, 'rgba(60,70,100,0.4)', 6);
  ctx.restore();
}

// ---------- headphones (music_study) ----------
// cup colour = what is playing: lyrics pink, instrumental green, nothing gray
const PHONES = { band: '#2b3554', bandHi: '#55628c', cup: '#e9edf6' };
// on the head (head coords): band over the hair, cups over the ears; lift 0..1 = taken off (rises while it fades)
function drawHeadphonesOnHead(color, lift = 0) {
  ctx.save(); ctx.translate(0, -50 * lift);
  ctx.save(); ctx.lineCap = 'round';
  ctx.beginPath(); ctx.ellipse(0, -4, 70, 84, 0, Math.PI * 1.1, Math.PI * 1.9);
  ctx.strokeStyle = PHONES.band; ctx.lineWidth = 13; ctx.stroke();
  ctx.strokeStyle = PHONES.bandHi; ctx.lineWidth = 4; ctx.stroke();
  ctx.restore();
  for (const sx of [-1, 1]) {
    line(sx * 66, -30, sx * 64, -14, PHONES.band, 9);
    rrect(sx * 64 - 17, -18, 34, 56, 14, PHONES.cup, 'rgba(60,70,100,0.55)', 2);
    ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 10;
    rrect(sx * 64 - 9, -8, 18, 36, 8, color); ctx.restore();
  }
  ctx.restore();
}
// around the neck (body coords, sh = shoulder line); drop 0..1 = still sliding down into place
function drawHeadphonesOnNeck(sh, color, drop = 0) {
  ctx.save(); ctx.translate(0, -34 * drop);
  ctx.save(); ctx.lineCap = 'round';
  ctx.beginPath(); ctx.ellipse(0, sh + 2, 50, 30, 0, 0.12 * Math.PI, 0.88 * Math.PI);
  ctx.strokeStyle = PHONES.band; ctx.lineWidth = 12; ctx.stroke();
  ctx.strokeStyle = PHONES.bandHi; ctx.lineWidth = 4; ctx.stroke();
  ctx.restore();
  for (const sx of [-1, 1]) {
    ctx.save(); ctx.translate(sx * 50, sh + 8); ctx.rotate(sx * -0.5);
    rrect(-16, -24, 32, 48, 13, PHONES.cup, 'rgba(60,70,100,0.55)', 2);
    rrect(-9, -15, 18, 30, 8, color);
    ctx.restore();
  }
  ctx.restore();
}

function drawDesk(w) {
  const hw = w / 2;
  ctx.fillStyle = '#82563a'; ctx.fillRect(-hw + 14, 14, w - 28, 96);
  ctx.fillStyle = '#6c472f'; ctx.fillRect(-hw + 14, 14, w - 28, 7);
  rrect(-hw, -3, w, 19, 4, '#a9774f');
  ctx.fillStyle = '#c38d60'; ctx.fillRect(-hw + 3, -3, w - 6, 4);
}

// ---------- bed (bedtime_words): the kid "goes to bed" where he sits ----------
// bed = 0..1: a headboard replaces the chair back, a pillow appears behind the head and a blanket rises from below
// over the desk up to the chin (front view of a kid lying in bed). Kid-local coords, origin = desk top centre.
const BED = { blanket: '#3c6db5', blanketDark: '#2f5a99', sheet: '#e3ecf8', wood: '#7a5238', woodHi: '#9a6a48', pillow: '#eef2f8' };
function drawHeadboard(k) {
  withAlpha(k, () => {
    rrect(-170, -198, 340, 234, [34, 34, 6, 6], BED.wood);
    rrect(-152, -181, 304, 196, [24, 24, 4, 4], BED.woodHi);
    rrect(-152, -181, 304, 10, [24, 24, 0, 0], 'rgba(255,255,255,0.10)');
  });
}
function drawPillow(k, hx, hy) {
  withAlpha(k, () => {
    rrect(hx - 118, hy + 4, 236, 82, 34, BED.pillow, 'rgba(160,175,205,0.7)', 2);
    line(hx - 92, hy + 70, hx + 92, hy + 70, 'rgba(160,175,205,0.45)', 2);
  });
}
// k = how much of the bed is there (fades the frame in), sit = sitting up (blanket at the waist, over the desk),
// bed = lying down (blanket up to the chin). With sit = 0 this is exactly the old lie-down blanket.
function drawBlanket(k, sit, bed, t, breath) {
  if (k <= 0.001) return;
  const base = lerp(150, -6, EASE.out(sit));
  const top = lerp(base, -62, EASE.out(bed)) + breath * 0.9;
  ctx.save();
  ctx.beginPath(); ctx.rect(-300, -400, 600, 540); ctx.clip();
  // bed frame (bottom rail + legs) under the blanket
  withAlpha(clamp(k * 2), () => {
    rrect(-256, 104, 512, 26, 6, BED.wood);
    rrect(-252, 128, 22, 26, 4, BED.wood); rrect(230, 128, 22, 26, 4, BED.wood);
  });
  // blanket body with a soft wavy top
  ctx.beginPath();
  ctx.moveTo(-246, 124);
  ctx.lineTo(-246, top + 26);
  ctx.quadraticCurveTo(-246, top, -214, top);
  ctx.bezierCurveTo(-120, top - 6, -60, top + 8, 0, top + 2);
  ctx.bezierCurveTo(60, top - 4, 120, top + 8, 214, top);
  ctx.quadraticCurveTo(246, top, 246, top + 26);
  ctx.lineTo(246, 124); ctx.closePath();
  ctx.fillStyle = BED.blanket; ctx.fill();
  // folded sheet hem along the top
  ctx.save(); ctx.clip();
  ctx.fillStyle = BED.sheet; ctx.fillRect(-260, top - 12, 520, 30);
  ctx.fillStyle = 'rgba(120,140,180,0.35)'; ctx.fillRect(-260, top + 16, 520, 3);
  // little stars on the blanket
  ctx.fillStyle = 'rgba(255,214,120,0.55)';
  for (const [sx, sy] of [[-170, 46], [-80, 78], [20, 40], [120, 84], [190, 30], [-20, 104], [-200, 98]]) {
    if (sy > top + 30) iconStar(sx, sy, 7, 'rgba(255,214,120,0.55)');
  }
  // side fold shading
  ctx.fillStyle = BED.blanketDark; ctx.fillRect(-246, top + 20, 18, 140); ctx.fillRect(228, top + 20, 18, 140);
  ctx.restore();
  ctx.restore();
}

// o: { x, y, s, type, t, sleep, stretch, read, write, tap, point, thumb, worry, happy, blink, talk,
//      flip, alpha, deskW, deskProps(fn), bookColor, pencil, bob, bed }
function drawKid(o) {
  const st = KID_STYLE[o.type];
  const sleep = o.sleep || 0, stretch = o.stretch || 0, read = o.read || 0, write = o.write || 0;
  const bed = o.bed || 0;
  // sit: in bed but sitting up (reading before sleep). furn = how much bed furniture is shown.
  const sit = o.sit || 0, furn = Math.max(sit, bed);
  const t = o.t || 0;
  const breath = Math.sin(t * TAU / (BEAT * 4)) * (1.2 + Math.max(sleep, bed) * 1.6);
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
  const bedE = EASE.inOut(bed);
  hx = lerp(hx, -8, bedE); hy = lerp(hy, -116, bedE); hr = lerp(hr, -0.2, bedE);
  hy += breath * 0.6 + (o.bob || 0);
  hr += (o.headTilt || 0);
  const sh = lerp(-72, -54, sleep) + lerp(0, -6, stretch) + breath * 0.4;

  // chair back (or the headboard when in bed)
  if (furn < 0.999) withAlpha(1 - furn, () => {
    rrect(-86, -160, 172, 178, 20, '#44506a');
    rrect(-80, -158, 160, 8, 4, '#55627f');
  });
  if (furn > 0.001) { drawHeadboard(furn); drawPillow(furn, hx, hy); }

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
  // headphones resting around the neck
  const neck = o.neck || 0;
  if (neck > 0.01) withAlpha(clamp(neck * 1.4), () => drawHeadphonesOnNeck(sh, o.phonesColor || '#6b7795', 1 - EASE.out(neck)));

  // desk + desk props (the props go away while the blanket comes up)
  drawDesk(o.deskW || 440);
  if (o.deskProps && bed < 0.4) withAlpha(1 - bed / 0.4, o.deskProps);

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
  const eyeClose = Math.max(sleep, stretch, blink, o.eyesHappy || 0, bed);
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

  const inBed = furn > 0.001;
  const armsBehindHead = sleep > 0.5 || inBed;
  if (armsBehindHead) drawArms();
  if (inBed) drawBlanket(furn, sit, bed, t, breath);
  ctx.save(); ctx.translate(hx, hy); ctx.rotate(hr); drawHead(o, st, f);
  const ph = o.phones || 0;
  if (ph > 0.01) withAlpha(clamp(ph * 1.4), () => drawHeadphonesOnHead(o.phonesColor || '#6b7795', 1 - EASE.out(ph)));
  ctx.restore();
  if (read > 0.02 && bed < 0.5) {
    const by = lerp(-10, -38, EASE.out(read));
    ctx.save(); ctx.globalAlpha *= clamp(read * 3) * (1 - bed * 2);
    if (o.heldCard) drawHeldCard(0, by - 4, o.flip || 0, o.heldCardColor);
    else drawHeldBook(0, by, 134, 72, o.bookColor || '#7b5fd6', o.flip || 0, lerp(0.35, 1, clamp(read * 1.4)));
    ctx.restore();
  }
  // sitting up in bed: the hands hold the book in front of the blanket, fading out while he lies down
  const frontA = !armsBehindHead ? 1 : (sit > 0.001 ? clamp(1 - bed * 2) : 0);
  if (frontA > 0.001) withAlpha(frontA, drawArms);
  // layout lint: head (with the headphone band) and desk
  lintPanel('head:' + o.type, hx - 92, hy - 98, hx + 92, hy + 66);
  lintPanel('desk:' + o.type, -(o.deskW || 440) / 2, -6, (o.deskW || 440) / 2, 110);
  ctx.restore();
  // screen positions of the ear cups (where the music comes out)
  const cupAt = (sx) => [o.x + (hx + Math.cos(hr) * sx * 64 - Math.sin(hr) * 10) * o.s, o.y + (hy + Math.sin(hr) * sx * 64 + Math.cos(hr) * 10) * o.s];
  const cups = [cupAt(-1), cupAt(1)];

  // Zz (screen space, above head)
  const zzK = Math.max(sleep, bed);
  if (zzK > 0.6 && o.zz !== false) {
    const a = clamp((zzK - 0.6) / 0.4);
    const bx = o.x + (hx + 70) * o.s, by = o.y + (hy - 40) * o.s;
    for (let i = 0; i < 3; i++) {
      const ph = ((t / (BEAT * 4)) + i / 3) % 1;
      txt('Z', bx + ph * (o.zzW ?? 46) * o.s + i * 6, by - ph * (o.zzH ?? 90) * o.s, {
        size: (22 + ph * 26) * o.s, weight: 800, fam: 'mono', color: COL.cyanHi,
        alpha: a * Math.sin(Math.PI * ph) * (o.alpha ?? 1), glow: 10,
      });
    }
  }
  return { headX: o.x + hx * o.s, headY: o.y + hy * o.s, cups };
}
