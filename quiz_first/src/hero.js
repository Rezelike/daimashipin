// hero.js — the one adult figure (kit/figure.js, look A), on screen in every frame. He always faces right (dir = 1).
// heroState(bt) gives { x, y (ground), s, pose, face, prop } per section; poses are keyframed with PT() and hands are
// placed with a 2-link IK (armTo) so he really touches the buzzer, the cards and the page.
const full = (p) => ({ ...POSES.stand, ...p });

// pose track: keys [[beat, pose | (bt) => pose, ease?], ...]
function PT(keys) {
  return (bt) => {
    const val = (k) => full(typeof k[1] === 'function' ? k[1](bt) : k[1]);
    if (bt <= keys[0][0]) return val(keys[0]);
    for (let i = 1; i < keys.length; i++) {
      if (bt <= keys[i][0]) {
        const span = keys[i][0] - keys[i - 1][0];
        const p = span > 0 ? (bt - keys[i - 1][0]) / span : 1;
        return lerpPose(val(keys[i - 1]), val(keys[i]), EASE[keys[i][2] || 'inOut'](clamp(p)));
      }
    }
    return val(keys[keys.length - 1]);
  };
}
// face track: [[beat, face], ...] -> the last face whose beat has passed
function FT(keys) { return (bt) => { let f = keys[0][1]; for (const [b, v] of keys) if (bt >= b) f = v; return f; }; }

// 2-link IK in figure-local coordinates (pelvis = origin, +x forward, +y down); angles from vertical-down, degrees
function ikArm(sh, tx, ty) {
  const L1 = FIG.ua, L2 = FIG.fa;
  let dx = tx - sh[0], dy = ty - sh[1];
  let d = Math.hypot(dx, dy);
  const dmax = L1 + L2 - 0.5, dmin = Math.abs(L1 - L2) + 20;
  if (d > dmax) { dx *= dmax / d; dy *= dmax / d; d = dmax; }
  if (d < dmin) { dx *= dmin / Math.max(d, 1e-3); dy *= dmin / Math.max(d, 1e-3); d = dmin; }
  const th = Math.atan2(dx, dy);
  const a = Math.acos(clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1));
  const ua = th - a;  // elbow below the line from shoulder to hand
  const ex = sh[0] + Math.sin(ua) * L1, ey = sh[1] + Math.cos(ua) * L1;
  const fa = Math.atan2(sh[0] + dx - ex, sh[1] + dy - ey);
  return [ua / D2R, fa / D2R];
}
// a pose with the front (or back) hand at screen point (X, Y), for a figure at st = { x, y, s }
function armTo(pose, X, Y, st, side = 'F') {
  const p = full(pose), py = pelvisHeight(p);
  const lx = (X - st.x) / ((st.dir ?? 1) * st.s), ly = (Y - st.y) / st.s + py;
  const J = rigJoints(p), sh = side === 'F' ? J.armF[0] : J.armB[0];
  const [ua, fa] = ikArm(sh, lx, ly);
  return side === 'F' ? { ...p, uaF: ua, faF: fa, faFL: 1 } : { ...p, uaB: ua, faB: fa, faBL: 1 };
}
// walking on top of a pose: one step per beat, start on a half beat so the footsteps land on the beats
function walkOver(pose, bt, b0, b1, k = 0.7) {
  if (bt <= b0 || bt >= b1) return pose;
  const ramp = Math.min(seg(bt, b0, b0 + 0.3), 1 - seg(bt, b1 - 0.3, b1));
  const w = walkPose(bt - b0, k);
  const o = { ...pose };
  for (const key of ['lean', 'thF', 'shF', 'thB', 'shB']) o[key] = lerp(pose[key] ?? 0, w[key], ramp);
  // arms swing only if they are hanging down (not while holding something up)
  if (Math.abs(pose.uaB ?? 0) < 20) { o.uaB = lerp(pose.uaB ?? 0, w.uaB, ramp); o.faB = lerp(pose.faB ?? 0, w.faB, ramp); }
  if (Math.abs(pose.uaF ?? 0) < 20) { o.uaF = lerp(pose.uaF ?? 0, w.uaF, ramp); o.faF = lerp(pose.faF ?? 0, w.faF, ramp); }
  return o;
}
const walkX = (bt, b0, b1, x0, x1) => lerp(x0, x1, EASE.inOut(seg(bt, b0, b1)));
const hop = (bt, b0, d, hgt = 70) => (bt > b0 && bt < b0 + d ? hgt * Math.sin(Math.PI * (bt - b0) / d) : 0);
// small chin-tapping / head-tilting motion of the thinking pose (he is moving on frame 0)
const thinkPose = (bt) => ({ ...POSES.think, head: 15 + 5 * Math.sin(bt * Math.PI * 0.5 + 0.6), faF: 196 + 8 * Math.max(0, Math.sin(bt * Math.PI * 2)), lean: -2 + 1.5 * Math.sin(bt * Math.PI * 0.5) });
const STANDP = { ...POSES.stand };

// ---------- opening + answer section (0–32) ----------
const BUZ = { x: 885, top: 668 };
const OP_X = 760, WALK1 = [19.5, 23.5], ANS_X = 1170;
const OP_FACE = FT([[0, 'calm'], [4.5, 'wow'], [7.0, 'tired'], [8.0, 'calm'], [8.5, 'happy'], [16.5, 'calm'], [24.5, 'happy']]);
function heroOpening(bt) {
  const st = { x: bt < WALK1[0] ? OP_X : walkX(bt, WALK1[0], WALK1[1], OP_X, ANS_X), y: STAGE_Y, s: 1, prop: null };
  const at = (X, Y, base = {}) => () => armTo({ ...STANDP, ...base }, X, Y, st);
  const raise = at(BUZ.x - 30, BUZ.top - 178, { lean: 2, head: -4 });
  const slap = at(BUZ.x - 2, BUZ.top - 26, { lean: 9, head: 12 });
  const lift = at(BUZ.x - 14, BUZ.top - 112, { lean: 6, head: 8 });
  const hold = at(OP_X + 128, 610, { head: 10 });
  const T = PT([
    [0, thinkPose], [3.0, thinkPose], [4.0, raise], [4.5, slap, 'in'], [5.0, slap], [5.25, lift, 'out'], [5.5, slap, 'in'], [6.0, slap],
    [6.25, lift, 'out'], [6.5, slap, 'in'], [7.0, slap], [7.5, POSES.slump], [8.0, raise], [8.5, slap, 'in'], [9.0, slap], [9.25, lift, 'out'],
    [9.5, slap, 'in'], [10.0, slap], [10.5, POSES.cheer, 'out'], [11.5, POSES.cheer], [12.0, POSES.point], [14.5, POSES.point], [15.0, STANDP],
    [16.5, STANDP], [17.0, hold], [18.0, hold], [19.0, { uaF: 5, faF: -12, head: 6 }], [19.5, STANDP], [24.0, STANDP],
    [24.5, { ...POSES.point, head: 2 }], [28.0, { ...POSES.point, head: 2 }], [28.5, STANDP],
  ]);
  st.pose = walkOver(T(bt), bt, WALK1[0], WALK1[1]);
  st.pose.lift = hop(bt, 10.5, 1.0, 60);
  st.face = OP_FACE(bt);
  st.pointF = (bt > 11.8 && bt < 14.8) || (bt > 24.3 && bt < 28.2);
  // the question card in his hand (17.0 -> into the pocket at 18.5–19.0)
  if (bt >= 17.0 && bt < 19.0) st.prop = { type: 'qcard', s: bt < 18.5 ? 0.34 : 0.34 * (1 - seg(bt, 18.5, 19.0)) };
  return st;
}
