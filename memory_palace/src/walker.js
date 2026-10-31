// walker.js — puts the one figure (kit rig, look C: silhouette + rim light) on the house floor. Adapted from habit_days/src/
// walker.js for a flat floor and both directions: procedural walk with 2-bone leg IK, one step per beat, heel strikes ON
// the beats (the footstep sounds sit there), planted feet never slide, any upper-body pose on top, full-body poses blended in.
// All times in beats; positions in world units (stage.js), the figure's size in screen px (s = 1 -> 440 px tall).
const LEG_R = (FIG.thigh + FIG.shin) * 0.985;
const HIP_LOC = { B: [-4, -2], F: [4, 0] };

// 2-bone IK in figure-local units (x = forward, y = down), hip -> ankle target; the knee bends forward.
// Returns [thigh, shin] as absolute angles from vertical-down (the rig's convention, degrees).
function legIK(hx, hy, tx, ty) {
  let dx = tx - hx, dy = ty - hy, d = Math.hypot(dx, dy);
  const l1 = FIG.thigh, l2 = FIG.shin, maxD = (l1 + l2) * 0.9995, minD = Math.abs(l1 - l2) + 2;
  if (d > maxD) { dx *= maxD / d; dy *= maxD / d; d = maxD; }
  if (d < minD) { const k = minD / Math.max(d, 1e-6); dx *= k; dy *= k; d = minD; }
  const th = Math.atan2(dx, dy);
  const al = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1));
  const a1 = th + al;
  const kx = hx + Math.sin(a1) * l1, ky = hy + Math.cos(a1) * l1;
  return [a1 / D2R, Math.atan2(hx + dx - kx, hy + dy - ky) / D2R];
}

// spec: { posX(bt) -> pelvis world x, walk(bt) -> 0..1, s(bt) -> screen scale, dir(bt) -> 1 | -1, up(bt) -> upper-body pose,
//         armHold(bt) -> 0..1 (the upper-body pose keeps the near arm while walking), fk(bt) / fkPose(bt) -> full-body pose }
function walkerPose(bt, spec) {
  const s = spec.s(bt), w = spec.walk(bt), x = spec.posX(bt), dir = spec.dir(bt);
  const plant = (n) => spec.posX(n) + (spec.posX(n + 0.5) - spec.posX(n - 0.5)) / 2;
  const footAt = (parity) => {
    let n = Math.floor(bt);
    if (((n % 2) + 2) % 2 !== parity) n -= 1;
    // around a picture cut he is somewhere else: keep the feet under him (he never walks within 2.5 beats of a cut)
    if ((spec.cuts || CUTS).some((c) => c > n - 0.5 && c <= n + 2.5)) return { x, lift: 0 };
    const u = bt - n, p1 = plant(n);
    if (u < 1) return { x: p1, lift: 0 };
    const p2 = plant(n + 2), q = u - 1;
    const dist = Math.abs(p2 - p1) * CAM.Z;
    return { x: lerp(p1, p2, EASE.inOut(q)), lift: 20 * s * Math.sin(Math.PI * q) * clamp(dist / 40) };
  };
  const fF = footAt(0), fB = footAt(1);
  const footOff = { F: 7 * s * dir, B: -7 * s * dir };
  const ank = (f, side) => [wx(f.x) + footOff[side], FLOOR_Y - FIG.foot * s - f.lift, f.lift];
  const aF = ank(fF, 'F'), aB = ank(fB, 'B');
  const px = wx(x);
  let py = FLOOR_Y - s * (212 - 5 * w * Math.cos(TAU * bt));
  for (const [ax, ay, lift] of [aF, aB]) {
    if (lift > 3 * s) continue;
    const dx = (ax - px) / s;
    const reach = Math.sqrt(Math.max(0, LEG_R * LEG_R - dx * dx));
    py = Math.max(py, ay - s * reach);
  }
  const loc = (q) => [((q[0] - px) * dir) / s, (q[1] - py) / s];
  const [tFx, tFy] = loc(aF), [tBx, tBy] = loc(aB);
  const [thF, shF] = legIK(HIP_LOC.F[0], HIP_LOC.F[1], tFx, tFy);
  const [thB, shB] = legIK(HIP_LOC.B[0], HIP_LOC.B[1], tBx, tBy);
  const ftOf = (f) => 90 - (f.lift > 0 ? 12 * clamp(f.lift / (20 * s)) : 0);
  const up = { ...POSES.stand, ...spec.up(bt) };
  const hold = spec.armHold ? spec.armHold(bt) : 0;
  const c = Math.cos(Math.PI * bt), A = 24;
  const walkArms = { uaF: -A * c, faF: -A * c + 16, uaB: A * c, faB: A * c + 16 };
  const pose = { ...up };
  pose.uaB = lerp(up.uaB, walkArms.uaB, w * (1 - hold));
  pose.faB = lerp(up.faB, walkArms.faB, w * (1 - hold));
  pose.uaF = lerp(up.uaF, walkArms.uaF, w * (1 - hold));
  pose.faF = lerp(up.faF, walkArms.faF, w * (1 - hold));
  pose.lean = (up.lean || 0) + w * 5;
  Object.assign(pose, { thF, shF, thB, shB, ftF: ftOf(fF), ftB: ftOf(fB), lift: 0, rot: 0 });
  let pelvis = [px, py];
  const fk = spec.fk ? spec.fk(bt) : 0;
  if (fk > 0.001) {
    const fp = { ...POSES.stand, ...spec.fkPose(bt) };
    const fpy = FLOOR_Y - s * pelvisHeight(fp);
    for (const k of ['thF', 'shF', 'thB', 'shB']) pose[k] = lerp(pose[k], fp[k], fk);
    for (const k of ['lean', 'head', 'uaF', 'faF', 'uaB', 'faB']) pose[k] = lerp(pose[k], fp[k] ?? 0, fk);
    pose.ftF = lerp(pose.ftF, fp.ftF ?? fp.shF + 90, fk);
    pose.ftB = lerp(pose.ftB, fp.ftB ?? fp.shB + 90, fk);
    pose.lift = (fp.lift || 0) * fk;
    pelvis = [px, lerp(py, fpy, fk)];
  }
  return { pose, pelvis, s, dir };
}

// o: { rim, alpha, pointF, ghost } — ghost = the imagined walk in step ③ / the practice afterimages (cool rim, see-through)
function drawWalker(bt, spec, o = {}) {
  const { pose, pelvis, s, dir } = walkerPose(bt, spec);
  return drawFigure({ pelvis, x: pelvis[0], y: FLOOR_Y, s, dir, pose, style: 'C', rim: o.rim || '#ffd7a0', rimDx: -3.5, rimDy: -3.5,
    pointF: o.pointF, alpha: o.alpha ?? 1, shadow: o.shadow ?? true });
}
