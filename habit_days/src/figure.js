// figure.js — copied from kit/figure.js (branch six-videos, 2026-10-31; the plan says copy it, never import kit/), with three
// additions for this episode: the rim light can sit on either side (rimDx / rimDy), feet can be given an absolute angle so they
// lie flat on a slope (pose keys ftB / ftF), and the pelvis can be placed directly (o.pelvis) for the leg IK in walker.js.
// ONE adult figure that can take any pose (user, 2026-10-31: 「那个人我感觉特别幼稚」「下次换成一个小人」
// 「随便让他摆个什么姿势，就是不要再坐到凳子上写作业读书」). Forward kinematics on a 2D skeleton, adult proportions
// (about 7.5 heads, ~440 px tall at s = 1). Origin = the ground under the pelvis; +x = the way he faces.
// Angles in degrees, all absolute. lean / head: from vertical-up (+ = toward +x). Limbs: from vertical-down
// (+ = swing toward +x). B = far side (drawn behind the body), F = near side (drawn in front).
const FIG = { thigh: 108, shin: 102, torso: 146, neck: 12, headR: 26, ua: 84, fa: 78, foot: 10 };
const D2R = Math.PI / 180;
const fDown = (a) => [Math.sin(a * D2R), Math.cos(a * D2R)];
const fUp = (a) => [Math.sin(a * D2R), -Math.cos(a * D2R)];
const vAdd = (p, d, k = 1) => [p[0] + d[0] * k, p[1] + d[1] * k];

// lift = pelvis above its standing height (jumps); rot = whole body (-90: lying, head on the left); ground = pelvis
// height when lying
const POSES = {
  stand: { lean: 0, head: 0, uaB: -5, faB: -2, uaF: 6, faF: 4, thB: -2, shB: -2, thF: 3, shF: 3 },
  point: { lean: 0, head: 4, uaB: -16, faB: 30, uaF: 104, faF: 112, thB: -5, shB: -5, thF: 8, shF: 8 },
  // faBL / faFL: forearm drawn shorter = foreshortened (an arm crossing the body points at the camera)
  think: { lean: -2, head: 16, uaB: 10, faB: 84, faBL: 0.42, uaF: 28, faF: 196, faFL: 0.92, thB: -3, shB: -3, thF: 9, shF: 9 },
  cheer: { lean: -3, head: -12, uaB: -34, faB: 56, uaF: 152, faF: 166, thB: -8, shB: -62, thF: 40, shF: -16, lift: 24 },
  // lying on his back, head on the left: + angles point away from the floor, so the arms rest along the body
  lie: { lean: 0, head: 6, uaB: 3, faB: 2, uaF: 9, faF: 4, thB: 2, shB: 2, thF: 22, shF: -12, rot: -90 },
  slump: { lean: 16, head: 28, uaB: 4, faB: 2, uaF: 8, faF: 4, thB: -2, shB: -2, thF: 4, shF: 4 },
  shrug: { lean: 0, head: -6, uaB: -24, faB: 70, uaF: 26, faF: 112, thB: -4, shB: -4, thF: 6, shF: 6 },
};
const POSE_KEYS = ['lean', 'head', 'uaB', 'faB', 'uaF', 'faF', 'thB', 'shB', 'thF', 'shF', 'lift', 'rot', 'ground', 'faBL', 'faFL'];
const POSE_DEF = { ground: 24, faBL: 1, faFL: 1 };
function lerpPose(a, b, t) {
  const o = {};
  for (const k of POSE_KEYS) o[k] = lerp(a[k] ?? POSE_DEF[k] ?? 0, b[k] ?? POSE_DEF[k] ?? 0, t);
  return o;
}
// walk cycle: phase in steps (one step per beat looks right at 128 BPM)
function walkPose(phase, k = 1) {
  const s = Math.sin(phase * Math.PI), c = Math.cos(phase * Math.PI);
  return {
    lean: 5 * k, head: 3, thF: 26 * s * k, shF: 26 * s * k - 34 * Math.max(0, -c) * k, thB: -26 * s * k, shB: -26 * s * k - 34 * Math.max(0, c) * k,
    uaF: -26 * s * k, faF: -26 * s * k + 18 * k, uaB: 26 * s * k, faB: 26 * s * k + 18 * k,
  };
}

// joint positions relative to the pelvis, before the body rotation
function rigJoints(p) {
  const nb = vAdd([0, 0], fUp(p.lean), FIG.torso);
  const neckTop = vAdd(nb, fUp(p.lean + p.head * 0.4), FIG.neck);
  const head = vAdd(neckTop, fUp(p.lean + p.head), FIG.headR * 0.9);
  const shB = vAdd(nb, [-5, 3]), shF = vAdd(nb, [5, 1]);
  const hipB = [-4, -2], hipF = [4, 0];
  const limb = (o, a1, l1, a2, l2) => { const m = vAdd(o, fDown(a1), l1); return [o, m, vAdd(m, fDown(a2), l2)]; };
  return {
    nb, neckTop, head, headAng: p.lean + p.head,
    armB: limb(shB, p.uaB, FIG.ua, p.faB, FIG.fa * (p.faBL ?? 1)), armF: limb(shF, p.uaF, FIG.ua, p.faF, FIG.fa * (p.faFL ?? 1)),
    legB: limb(hipB, p.thB, FIG.thigh, p.shB, FIG.shin), legF: limb(hipF, p.thF, FIG.thigh, p.shF, FIG.shin),
  };
}
// pelvis height: the lower ankle touches the ground when upright; `ground` when lying
function pelvisHeight(p) {
  const ext = (th, sh) => FIG.thigh * Math.cos(th * D2R) + FIG.shin * Math.cos(sh * D2R);
  const up = Math.max(ext(p.thB, p.shB), ext(p.thF, p.shF)) + FIG.foot + (p.lift || 0);
  return lerp(up, p.ground ?? 24, clamp(Math.abs(p.rot || 0) / 90));
}

// ---------- style A: flat adult (cream sweater, slate trousers, white sneakers; small head, dot eye, no blush) ----------
const PAL_A = { skin: '#e8b48e', skinSh: '#cf9873', hair: '#2b2220', top: '#ece4d4', topSh: '#c4baa6', pants: '#5a6684',
  pantsSh: '#454f6b', shoe: '#f3f2ee', sole: '#8f99ad', eye: '#2b2220', mouth: '#8a4b3c' };
function polyline(pts, w, color) {
  ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = color; ctx.lineWidth = w;
  ctx.beginPath(); ctx.moveTo(...pts[0]); for (let i = 1; i < pts.length; i++) ctx.lineTo(...pts[i]); ctx.stroke(); ctx.restore();
}
function drawLegFlat(L, footAng, pal, far) {
  const [hip, knee, ankle] = L;
  polyline([hip, knee], 33, far ? pal.pantsSh : pal.pants);
  polyline([knee, ankle], 27, far ? pal.pantsSh : pal.pants);
  const fd = fDown(footAng);  // footAng: absolute foot direction (90 = flat, pointing forward)
  const toe = vAdd(ankle, fd, 26), heel = vAdd(ankle, fd, -7);
  polyline([heel, toe], 17, far ? pal.sole : pal.shoe);
  const n = [fd[1] * -1, fd[0]];  // perpendicular (toward the sole when standing)
  polyline([vAdd(heel, n, -6), vAdd(toe, n, -6)], 4, pal.sole);
}
function drawArmFlat(A, pal, far, point) {
  const [sh, el, hand] = A;
  polyline([sh, el], 23, far ? pal.topSh : pal.top);
  polyline([el, hand], 20, far ? pal.topSh : pal.top);
  if (point) {  // index finger straight along the forearm (a raised single digit reads as a middle finger: lessons 9)
    const d = [hand[0] - el[0], hand[1] - el[1]], k = 1 / Math.hypot(...d);
    polyline([hand, vAdd(hand, d, 15 * k)], 6, pal.skin);
  }
  circle(hand[0], hand[1], 8.5, far ? pal.skinSh : pal.skin);
}
function drawTorsoFlat(J, lean, pal) {
  const u = fUp(lean), f = [Math.cos(lean * D2R), Math.sin(lean * D2R)], nb = J.nb;
  const P = (o, a, b) => vAdd(vAdd(o, f, a), u, b);
  const pts = [P([0, 0], 23, -18), P(nb, 25, -16), P(nb, 12, 4), P(nb, -16, 4), P(nb, -23, -14), P([0, 0], -24, -18)];
  ctx.save(); ctx.lineJoin = 'round'; ctx.fillStyle = pal.top; ctx.strokeStyle = pal.top; ctx.lineWidth = 14;
  ctx.beginPath(); ctx.moveTo(...pts[0]); for (const q of pts.slice(1)) ctx.lineTo(...q); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.restore();
  // collar
  polyline([P(nb, 9, 2), P(nb, -7, 3)], 5, pal.topSh);
}
// face: 'calm' | 'happy' | 'tired' | 'wow' | 'none'
function drawHeadFlat(J, pal, face) {
  polyline([J.nb, J.neckTop], 14, pal.skinSh);
  ctx.save(); ctx.translate(...J.head); ctx.rotate(J.headAng * D2R);
  ellipse(0, 0, 23, 27, pal.skin);
  ctx.beginPath(); ctx.moveTo(21, -3); ctx.lineTo(28, 5); ctx.lineTo(21, 8); ctx.closePath(); ctx.fillStyle = pal.skin; ctx.fill();
  ellipse(-5, 3, 5, 7, pal.skinSh);
  // short hair: over the top and the back, a small fringe at the front
  ctx.beginPath(); ctx.ellipse(-1, -3, 25, 28, 0, Math.PI * 0.8, Math.PI * 1.86);
  ctx.quadraticCurveTo(10, -16, -4, -15); ctx.quadraticCurveTo(-14, -10, -17, 8); ctx.closePath();
  ctx.fillStyle = pal.hair; ctx.fill();
  if (face !== 'none') {
    const ink = pal.eye;
    if (face === 'happy') { ctx.save(); ctx.strokeStyle = ink; ctx.lineWidth = 2.6; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(12, 0, 4, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); ctx.restore(); }
    else if (face === 'tired') line(8, 0, 16, 1, ink, 2.6);
    else circle(12, -1, face === 'wow' ? 3.4 : 2.7, ink);
    line(7, face === 'wow' ? -14 : -10, 17, face === 'wow' ? -15 : face === 'tired' ? -8 : -11, pal.hair, 2.6);
    if (face === 'happy') { ctx.save(); ctx.strokeStyle = pal.mouth; ctx.lineWidth = 2.4; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(15, 10, 5, Math.PI * 0.15, Math.PI * 0.75); ctx.stroke(); ctx.restore(); }
    else if (face === 'wow') ellipse(16, 15, 2.6, 3.4, pal.mouth);
    else line(13, 15, 19, face === 'tired' ? 16 : 14, pal.mouth, 2.2);
  }
  ctx.restore();
}
function drawFlat(J, p, pal, o) {
  drawArmFlat(J.armB, pal, true, false);
  drawLegFlat(J.legB, p.ftB ?? p.shB + 90, pal, true);
  drawLegFlat(J.legF, p.ftF ?? p.shF + 90, pal, false);
  drawTorsoFlat(J, p.lean, pal);
  drawHeadFlat(J, pal, o.face ?? 'calm');
  drawArmFlat(J.armF, pal, false, o.pointF);
}

// ---------- style B: neon line figure (no face) ----------
function drawNeon(J, p, o) {
  const c = o.color || COL.cream, g = o.glowColor || COL.cyan;
  const stroke = (pts, w, a) => withAlpha(a, () => { ctx.save(); ctx.shadowColor = g; ctx.shadowBlur = 16; polyline(pts, w, c); ctx.restore(); });
  stroke(J.armB, 9, 0.45); stroke(J.legB, 10, 0.45);
  stroke(J.legF, 10, 1); stroke([[0, 0], J.nb, J.neckTop], 12, 1);
  const foot = (L, fa, a) => stroke([L[2], vAdd(L[2], fDown(fa), 20)], 9, a);
  foot(J.legB, p.ftB ?? p.shB + 90, 0.45); foot(J.legF, p.ftF ?? p.shF + 90, 1);
  ctx.save(); ctx.shadowColor = g; ctx.shadowBlur = 22; circle(J.head[0], J.head[1], 22, c); ctx.restore();
  stroke(J.armF, 9, 1);
}

// ---------- style C: silhouette with a rim light (no face) ----------
const PAL_DARK = { skin: '#0b1226', skinSh: '#0b1226', hair: '#0b1226', top: '#0b1226', topSh: '#0b1226', pants: '#0b1226',
  pantsSh: '#0b1226', shoe: '#0b1226', sole: '#0b1226', eye: '#0b1226', mouth: '#0b1226' };
function drawSilhouette(J, p, o) {
  const rim = o.rim || COL.yellowHi;
  const palRim = Object.fromEntries(Object.keys(PAL_DARK).map((k) => [k, rim]));
  // rim on the side the light comes from: (-3.5, -3) = behind him (kit default), (+3.5, -3) = in front of him
  ctx.save(); ctx.translate(o.rimDx ?? -3.5, o.rimDy ?? -3); ctx.shadowColor = rim; ctx.shadowBlur = 10; drawFlat(J, p, palRim, { face: 'none', pointF: o.pointF }); ctx.restore();
  drawFlat(J, p, PAL_DARK, { face: 'none', pointF: o.pointF });
}

// ---------- main ----------
// o: { x, y (= the ground), s, dir (1 faces right, -1 left), pose (partial pose, merged over stand), style 'A' | 'B' | 'C',
//      face, pointF, alpha, color / glowColor (B), rim (C) }. Returns screen positions of the head and both hands.
function drawFigure(o) {
  const p = { ...POSES.stand, ...o.pose };
  const J = rigJoints(p), s = o.s ?? 1, dir = o.dir ?? 1, rot = (p.rot || 0) * D2R;
  const k = clamp(Math.abs(p.rot || 0) / 90);
  // o.pelvis = [x, y] on screen (walker.js places the pelvis itself); otherwise stand on the ground at (o.x, o.y)
  const px = o.pelvis ? o.pelvis[0] : o.x, py0 = o.pelvis ? o.pelvis[1] : o.y - s * pelvisHeight(p);
  const toScreen = (q) => {
    const rx = q[0] * Math.cos(rot) - q[1] * Math.sin(rot), ry = q[0] * Math.sin(rot) + q[1] * Math.cos(rot);
    return [px + dir * s * rx, py0 + s * ry];
  };
  withAlpha(o.alpha ?? 1, () => {
    if (o.shadow !== false) ellipse(o.x + dir * 12 * s * k, o.y + 3, lerp(64, 220, k) * s, 11 * s, 'rgba(0,0,0,0.32)');
    ctx.save(); ctx.translate(px, py0); ctx.scale(dir * s, s); ctx.rotate(rot);
    if (o.style === 'B') drawNeon(J, p, o);
    else if (o.style === 'C') drawSilhouette(J, p, o);
    else drawFlat(J, p, o.pal || PAL_A, o);
    ctx.restore();
  });
  return { head: toScreen(J.head), handF: toScreen(J.armF[2]), handB: toScreen(J.armB[2]), elbowF: toScreen(J.armF[1]),
    neck: toScreen(J.nb), pelvis: [px, py0], ankleB: toScreen(J.legB[2]), ankleF: toScreen(J.legF[2]) };
}
