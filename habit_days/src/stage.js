// stage.js — this episode's own stage (plan: 「日出前的一条上坡路」): a road up a hill before sunrise, seen from the side.
// The road IS Lally et al. 2010's habit curve: height = automaticity, slope = how much it grows per day (steep at first,
// flatter and flatter, p.1007). Median parameters from Table 2: a = 35, b = 30, c = 0.042 (y = a - b e^(-c day)), so
// day 21 sits at 65 % of the top (≈ 2/3, an ESTIMATE, labelled on screen) and day 66 at 95 % (the paper's "到顶").
// Nothing here moves the whole frame on the beat; the camera only moves on purpose (walks, the reveal-2 pull-back).
const HABIT = { a: 35, b: 30, c: 0.042 };
const E0 = (HABIT.a - HABIT.b) / HABIT.a, E0S = (HABIT.b * HABIT.c) / HABIT.a; // e(0) = 0.143, e'(0) = 0.036 per day
// automaticity as a share of his own top (0..1); before day 0 the ground eases in flat (no kink at the start of the road)
function habitE(d) {
  if (d >= 0) return (HABIT.a - HABIT.b * Math.exp(-HABIT.c * d)) / HABIT.a;
  if (d > -4) return E0 - 2 * E0S + (E0S * (d + 4) * (d + 4)) / 8;
  return E0 - 2 * E0S;
}

// ---------- camera: world (day, e) -> screen. The anchor day D is drawn at (X, Y); K px per day, V px per unit of e ----------
const CAM = { D: 21, X: 1300, Y: 700, K: 64, V: 1000 };
function setCam(c) { Object.assign(CAM, c); }
const sx = (d) => CAM.X + (d - CAM.D) * CAM.K;
const sy = (d) => CAM.Y - (habitE(d) - habitE(CAM.D)) * CAM.V;
const dayAt = (x) => CAM.D + (x - CAM.X) / CAM.K;
// road incline at day d on screen, radians (positive = uphill to the right)
function slopeAt(d) { const h = 0.05; return Math.atan2(sy(d - h) - sy(d + h), 2 * h * CAM.K); }
// zoom relative to the close shot (K = 64): props on the road scale with it
const zoomK = () => CAM.K / 64;

// ---------- sky ----------
const SKY_STARS = (() => {
  const r = mulberry32(20101009);
  return Array.from({ length: 120 }, () => ({ x: r() * W, y: r() * 560, s: 0.6 + r() * 1.8, a: 0.25 + r() * 0.6, ph: r() * TAU, tw: 0.5 + r() * 1.5 }));
})();
const HZ = 770; // screen height of the far horizon (fixed: it is far away)
// dawn: 0 = just before dawn (frame 0), 1 = the sun is up (the summary)
const DAWN = KB([[0, 0.12], [8.5, 0.18], [17, 0.3], [26, 0.48, 'inOut'], [128, 0.8, 'inOut'], [146, 1, 'inOut']]);
const SUN_X = 1580;
const SUN_Y = KB([[0, HZ + 150], [17, HZ + 60], [26, HZ + 8, 'out'], [128, HZ - 40, 'inOut'], [146, HZ - 92, 'out'], [160, HZ - 100]]);

function drawSky(bt, t, parallax) {
  const dn = DAWN(bt);
  const g = ctx.createLinearGradient(0, 0, 0, HZ);
  g.addColorStop(0, lerpColor('#04081a', '#0b1536', dn));
  g.addColorStop(0.45, lerpColor('#0b1234', '#1a2456', dn));
  g.addColorStop(0.78, lerpColor('#1c1a48', '#3d2c62', dn));
  g.addColorStop(0.93, lerpColor('#3a2250', '#8a4a62', dn));
  g.addColorStop(1, lerpColor('#6a3248', '#e08a5a', dn));
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, HZ + 2);
  ctx.fillStyle = lerpColor('#120d26', '#3a2340', dn); ctx.fillRect(0, HZ, W, H - HZ);
  // the glow where the sun comes up (ahead of him: he walks toward it)
  const sxp = SUN_X - parallax * 0.04, syp = SUN_Y(bt);
  const rg = ctx.createRadialGradient(sxp, HZ, 10, sxp, HZ, 1100);
  rg.addColorStop(0, `rgba(255,170,100,${0.18 + 0.32 * dn})`);
  rg.addColorStop(0.35, `rgba(240,120,110,${0.08 + 0.14 * dn})`);
  rg.addColorStop(1, 'rgba(240,120,110,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
  // stars fade as it gets light
  for (const st of SKY_STARS) {
    const a = st.a * (1 - dn * 0.85) * (0.6 + 0.4 * Math.sin(t * st.tw + st.ph)) * clamp(1 - st.y / 620);
    if (a < 0.02) continue;
    circle((st.x - parallax * 0.02 + W * 4) % W, st.y, st.s, `rgba(220,230,255,${a})`);
  }
  // the sun (clipped by the far mountains drawn after it)
  if (syp < HZ + 120) {
    ctx.save(); ctx.shadowColor = '#ffb562'; ctx.shadowBlur = 60 + 40 * dn;
    circle(sxp, syp, 96, lerpColor('#ff9a52', '#ffd27a', dn)); ctx.restore();
    circle(sxp, syp, 96, rgba('#fff1c8', 0.25 + 0.35 * dn));
  }
}

// far mountain ranges: smooth ridges from a few sines, fixed seed; parallax = how much they follow the camera
const RANGES = [
  { base: HZ, amp: 70, f: [0.0021, 0.0047, 0.011], ph: [0.3, 1.7, 4.1], col0: '#1b1640', col1: '#4a3256', par: 0.05 },
  { base: HZ + 30, amp: 58, f: [0.0029, 0.0061, 0.013], ph: [2.2, 0.4, 5.2], col0: '#141233', col1: '#33223f', par: 0.1 },
  { base: HZ + 70, amp: 44, f: [0.0034, 0.0082, 0.017], ph: [4.0, 2.9, 1.1], col0: '#0e0d28', col1: '#241830', par: 0.18 },
];
function drawRanges(bt, parallax) {
  const dn = DAWN(bt);
  for (const r of RANGES) {
    ctx.beginPath(); ctx.moveTo(0, H);
    for (let x = 0; x <= W; x += 12) {
      const u = x + parallax * r.par;
      const y = r.base - r.amp * (0.55 + 0.25 * Math.sin(u * r.f[0] + r.ph[0]) + 0.13 * Math.sin(u * r.f[1] + r.ph[1]) + 0.07 * Math.sin(u * r.f[2] + r.ph[2]));
      ctx.lineTo(x, y);
    }
    ctx.lineTo(W, H); ctx.closePath();
    ctx.fillStyle = lerpColor(r.col0, r.col1, dn * 0.8); ctx.fill();
  }
  // low mist over the valley, lit from the sun side
  const mg = ctx.createLinearGradient(0, HZ - 10, 0, HZ + 160);
  mg.addColorStop(0, 'rgba(255,170,140,0)'); mg.addColorStop(0.5, `rgba(255,170,140,${0.05 + 0.05 * dn})`); mg.addColorStop(1, 'rgba(255,170,140,0)');
  ctx.fillStyle = mg; ctx.fillRect(0, HZ - 10, W, 170);
}

// ---------- the road and the hill under it ----------
const ROAD = { band: 24, dash: 30, gap: 26 };
function roadPath(x0, x1, step = 6) {
  const pts = [];
  for (let x = x0; x <= x1 + step; x += step) pts.push([x, sy(dayAt(x))]);
  return pts;
}
// o.gapDay: a missing slab (step ③): the road has a hole of o.gapW days there
function drawRoad(bt, o = {}) {
  const z = zoomK(), band = ROAD.band * clamp(Math.sqrt(z), 0.55, 1.4), dn = DAWN(bt);
  const pts = roadPath(-10, W + 10);
  // hill mass
  ctx.beginPath(); ctx.moveTo(-10, H + 10);
  for (const [x, y] of pts) ctx.lineTo(x, y);
  ctx.lineTo(W + 10, H + 10); ctx.closePath();
  const hg = ctx.createLinearGradient(0, 300, 0, H);
  hg.addColorStop(0, '#0b1024'); hg.addColorStop(1, '#05070f');
  ctx.fillStyle = hg; ctx.fill();
  // road band (the side of the road surface), slightly lighter than the hill
  ctx.save();
  ctx.beginPath();
  for (const [x, y] of pts) ctx.lineTo(x, y);
  for (let i = pts.length - 1; i >= 0; i--) ctx.lineTo(pts[i][0], pts[i][1] + band);
  ctx.closePath();
  ctx.fillStyle = '#18203f'; ctx.fill();
  ctx.restore();
  // lit edge: the road surface catches the dawn light
  ctx.save();
  ctx.shadowColor = '#ffb27a'; ctx.shadowBlur = 14;
  ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
  ctx.strokeStyle = rgba('#ffc890', 0.55 + 0.3 * dn); ctx.lineWidth = 3; ctx.stroke();
  ctx.restore();
  // centre dashes along the band (world-anchored, so they move with the road, never on their own)
  ctx.save();
  ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y + band * 0.5) : ctx.moveTo(x, y + band * 0.5)));
  const per = (ROAD.dash + ROAD.gap) * z;
  ctx.setLineDash([ROAD.dash * z, ROAD.gap * z]);
  ctx.lineDashOffset = ((sx(0) % per) + per) % per;
  ctx.strokeStyle = 'rgba(243,238,227,0.22)'; ctx.lineWidth = 3; ctx.stroke();
  ctx.restore();
  if (o.gapDay != null && o.gapA > 0) drawRoadGap(o.gapDay, o.gapW, band, o.gapA);
}
// a missing slab: a hole cut through the lit road surface and the band, fading into the hill below; only its two
// broken edges catch the light (a dark outlined box read as an object sitting on the road)
function drawRoadGap(d, wDays, band, a) {
  const d0 = d - wDays / 2, d1 = d + wDays / 2;
  const x0 = sx(d0), x1 = sx(d1), y0 = sy(d0), y1 = sy(d1), depth = band + 50;
  withAlpha(a, () => {
    const g = ctx.createLinearGradient(0, Math.min(y0, y1) - 4, 0, Math.max(y0, y1) + depth);
    g.addColorStop(0, '#010207'); g.addColorStop(0.65, '#03050c'); g.addColorStop(1, 'rgba(5,8,18,0)');
    ctx.beginPath(); ctx.moveTo(x0, y0 - 4); ctx.lineTo(x1, y1 - 4);
    ctx.lineTo(x1 - 7, y1 + depth); ctx.lineTo(x0 + 7, y0 + depth); ctx.closePath();
    ctx.fillStyle = g; ctx.fill();
    line(x0, y0 - 1, x0 + 5, y0 + band + 8, 'rgba(255,200,144,0.75)', 3);
    line(x1, y1 - 1, x1 - 5, y1 + band + 8, 'rgba(255,200,144,0.75)', 3);
  });
}

// darkness over the road ahead in the hook (you can't see far before dawn); it lifts at reveal 2
function drawFog(a, fromX) {
  if (a <= 0.001) return;
  const g = ctx.createLinearGradient(fromX, 0, fromX + 420, 0);
  g.addColorStop(0, 'rgba(4,7,18,0)'); g.addColorStop(1, `rgba(4,7,18,${0.92 * a})`);
  ctx.fillStyle = g; ctx.fillRect(fromX, 0, W - fromX, H);
}

// soft vignette (static)
function drawVignette() {
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.5, W / 2, H / 2, H * 1.08);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,3,12,0.42)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
}
