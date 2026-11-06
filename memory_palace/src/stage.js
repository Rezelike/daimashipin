// stage.js — this episode's own stage (plan: 「夜里剖开的一栋房子，每处一盏灯」): a one-storey house at night with its front
// wall cut away, seen face-on. Ten fixed spots along one route (门口 → 床), each under its own pendant lamp: the memory palace.
// World units: x to the right from the inside of the left wall, y up from the floor. The camera only moves on purpose
// (walks, the reveal-2 pull-back); nothing moves the whole frame on the beat.

// ---------- camera: world (x, y) -> screen. WX = world x drawn at the screen centre, Z = px per world unit ----------
const FLOOR_Y = 985;
const CAM = { WX: 0, Z: 1 };
function setCam(c) { Object.assign(CAM, c); }
const wx = (x) => 960 + (x - CAM.WX) * CAM.Z;
const wy = (y) => FLOOR_Y - y * CAM.Z;

// ---------- the house ----------
const HOUSE = { x0: 0, x1: 1900, ceil: 560, wall: 24, slab: 34, door: 300 };
// the ten spots of the route, in order, evenly spaced (one every two steps of his walk)
const SPOT_X = Array.from({ length: 10 }, (_, i) => 70 + 190 * i);
const SPOT_NAME = ['门口', '鞋柜', '衣架', '沙发', '电视', '餐桌', '冰箱', '灶台', '书架', '床'];
const LAMP_Y = 505;   // bottom of the lamp shade (world)
const BEAMS = [545, 925, 1495];   // room dividers: beams hanging from the ceiling, above head height (he walks under them)

// ---------- sky and yard ----------
const STARS = (() => {
  const r = mulberry32(20170308);
  return Array.from({ length: 140 }, () => ({ x: r() * W, y: r() * 640, s: 0.6 + r() * 1.7, a: 0.25 + r() * 0.6, ph: r() * TAU, tw: 0.5 + r() * 1.4 }));
})();
function drawSky(bt, t) {
  const g = ctx.createLinearGradient(0, 0, 0, FLOOR_Y);
  g.addColorStop(0, '#03061a'); g.addColorStop(0.55, '#0a1238'); g.addColorStop(0.9, '#18204e'); g.addColorStop(1, '#232a5a');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, FLOOR_Y + 2);
  // moonlight from the top right (static)
  const mg = ctx.createRadialGradient(1700, -80, 20, 1700, -80, 1100);
  mg.addColorStop(0, 'rgba(150,180,255,0.20)'); mg.addColorStop(1, 'rgba(150,180,255,0)');
  ctx.fillStyle = mg; ctx.fillRect(0, 0, W, H);
  const par = (CAM.WX * CAM.Z) * 0.03;
  for (const st of STARS) {
    const a = st.a * (0.6 + 0.4 * Math.sin(t * st.tw + st.ph)) * clamp(1 - st.y / 700);
    circle(((st.x - par) % W + W) % W, st.y, st.s, `rgba(220,230,255,${a})`);
  }
  // far hills behind the house (slow parallax)
  ctx.beginPath(); ctx.moveTo(0, FLOOR_Y);
  for (let x = 0; x <= W; x += 12) {
    const u = x + CAM.WX * CAM.Z * 0.12;
    ctx.lineTo(x, FLOOR_Y - 150 - 60 * (0.5 + 0.3 * Math.sin(u * 0.0023 + 1.1) + 0.2 * Math.sin(u * 0.0071 + 0.4)));
  }
  ctx.lineTo(W, FLOOR_Y); ctx.closePath(); ctx.fillStyle = '#0b1030'; ctx.fill();
  // the yard
  const yg = ctx.createLinearGradient(0, FLOOR_Y, 0, H);
  yg.addColorStop(0, '#0d1226'); yg.addColorStop(1, '#04060e');
  ctx.fillStyle = yg; ctx.fillRect(0, FLOOR_Y, W, H - FLOOR_Y);
  line(0, FLOOR_Y, W, FLOOR_Y, 'rgba(140,160,220,0.25)', 2);
}

// ---------- world-space drawing (y up): helpers ----------
function wRect(x0, y0, x1, y1, fill, stroke = null, lw = 2) {
  const X0 = wx(x0), X1 = wx(x1), Y0 = wy(y1), Y1 = wy(y0);
  ctx.beginPath(); ctx.rect(X0, Y0, X1 - X0, Y1 - Y0);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
}
function wPoly(pts, fill, stroke = null, lw = 2) {
  ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(wx(x), wy(y)) : ctx.moveTo(wx(x), wy(y)))); ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
}
function wLine(x0, y0, x1, y1, color, lw = 2) { line(wx(x0), wy(y0), wx(x1), wy(y1), color, lw * CAM.Z); }
const WARM = (a) => `rgba(255,206,140,${a})`;
// light reaching world x from the lamps (0..1): each lamp lights about its own spot
function lightAt(x, L) {
  let v = 0;
  for (let i = 0; i < 10; i++) if (L[i] > 0) v = Math.max(v, L[i] * Math.exp(-((x - SPOT_X[i]) ** 2) / (2 * 120 * 120)));
  return v;
}

// back wall, floor, walls, beams, roof. L = the ten lamp levels (0..1)
function drawHouse(bt, L) {
  const { x0, x1, ceil, wall, slab } = HOUSE;
  // interior back wall
  wRect(x0, 0, x1, ceil, '#0b1330');
  // warm pools of light on the back wall, one per lamp
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 10; i++) {
    if (L[i] <= 0.01) continue;
    const cx = wx(SPOT_X[i]), cy = wy(260), r = 260 * CAM.Z;
    const g = ctx.createRadialGradient(cx, cy, 10, cx, cy, r);
    g.addColorStop(0, `rgba(255,180,100,${0.30 * L[i]})`); g.addColorStop(1, 'rgba(255,180,100,0)');
    ctx.fillStyle = g; ctx.fillRect(cx - r, cy - r, 2 * r, 2 * r);
  }
  ctx.restore();
  // skirting and floor boards
  wRect(x0, 0, x1, 14, '#141c3c');
  wRect(x0 - wall, -slab, x1 + wall, 0, '#1a2248');
  for (let x = x0 + 90; x < x1; x += 120) wLine(x, -slab + 4, x, -4, 'rgba(10,14,32,0.8)', 3);
  ctx.save(); ctx.shadowColor = '#ffb27a'; ctx.shadowBlur = 10;
  wLine(x0, 0, x1, 0, WARM(0.25 + 0.5 * Math.max(...L)), 3); ctx.restore();
  // room dividers (beams from the ceiling)
  for (const b of BEAMS) wRect(b - 14, 430, b + 14, ceil, '#0e1636', 'rgba(140,160,220,0.25)', 2);
  // left wall with the doorway (the door leaf stands open toward the yard), right wall
  wRect(x0 - wall, HOUSE.door, x0, ceil, '#151d40');
  wPoly([[x0 - wall, 0], [x0 - wall - 70, 18], [x0 - wall - 70, HOUSE.door - 10], [x0 - wall, HOUSE.door]], '#101836', 'rgba(255,206,140,0.35)', 2);
  circle(wx(x0 - wall - 58), wy(140), 4 * CAM.Z, WARM(0.7));
  wRect(x1, 0, x1 + wall, ceil, '#151d40');
  // roof slab + parapet, lit edge from the moon
  wRect(x0 - wall - 16, ceil, x1 + wall + 16, ceil + slab, '#121a3c');
  wRect(x0 - wall - 16, ceil + slab, x0 - wall + 14, ceil + slab + 26, '#121a3c');
  wRect(x1 + wall - 14, ceil + slab, x1 + wall + 16, ceil + slab + 26, '#121a3c');
  wLine(x0 - wall - 16, ceil + slab, x1 + wall + 16, ceil + slab, 'rgba(170,190,255,0.45)', 2);
  // the cut edge of the house (where the front wall was taken away): a thin bright outline
  ctx.save(); ctx.strokeStyle = 'rgba(160,180,240,0.4)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(wx(x0 - wall), wy(0)); ctx.lineTo(wx(x0 - wall), wy(ceil)); ctx.lineTo(wx(x1 + wall), wy(ceil)); ctx.lineTo(wx(x1 + wall), wy(0)); ctx.stroke();
  ctx.restore();
}

// ---------- furniture: dark shapes whose top edges catch the lamp light ----------
const INK = '#070b1d', INK2 = '#0c1430';
function edge(L) { return WARM(0.12 + 0.75 * L); }
function drawFurniture(L) {
  const lt = (x) => lightAt(x, L);
  // 1 门口: door mat
  { const x = SPOT_X[0], l = lt(x); wRect(x - 60, 0, x + 60, 6, INK2, edge(l)); }
  // 2 鞋柜: low cabinet with two doors
  { const x = SPOT_X[1], l = lt(x); wRect(x - 80, 0, x + 80, 112, INK, edge(l), 2.5); wLine(x, 8, x, 104, edge(l * 0.6), 2);
    circle(wx(x - 12), wy(60), 3.5 * CAM.Z, edge(l)); circle(wx(x + 12), wy(60), 3.5 * CAM.Z, edge(l)); }
  // 3 衣架: coat stand with a coat
  { const x = SPOT_X[2], l = lt(x); wLine(x, 0, x, 300, edge(l * 0.8), 6); wLine(x - 40, 0, x + 40, 0, edge(l * 0.8), 6);
    wPoly([[x - 10, 285], [x - 46, 250], [x - 54, 120], [x - 10, 112]], INK, edge(l), 2); wLine(x - 26, 296, x + 26, 296, edge(l), 5); }
  // 4 沙发
  { const x = SPOT_X[3], l = lt(x); wRect(x - 135, 30, x + 135, 82, INK, edge(l), 2.5); wRect(x - 125, 82, x + 125, 160, INK, edge(l), 2.5);
    wRect(x - 155, 20, x - 120, 115, INK, edge(l), 2.5); wRect(x + 120, 20, x + 155, 115, INK, edge(l), 2.5);
    wLine(x - 120, 0, x - 120, 22, edge(l * 0.6), 5); wLine(x + 120, 0, x + 120, 22, edge(l * 0.6), 5); }
  // 5 电视: TV on a low stand
  { const x = SPOT_X[4], l = lt(x); wRect(x - 90, 0, x + 90, 60, INK, edge(l), 2.5); wRect(x - 80, 96, x + 80, 196, '#05080f', edge(l), 3);
    wLine(x, 60, x, 96, edge(l * 0.6), 5); }
  // 6 餐桌 with two chairs
  { const x = SPOT_X[5], l = lt(x); wRect(x - 95, 112, x + 95, 124, INK, edge(l), 2.5); wLine(x - 80, 0, x - 80, 112, edge(l * 0.7), 6); wLine(x + 80, 0, x + 80, 112, edge(l * 0.7), 6);
    for (const s of [-1, 1]) { const cx = x + s * 128; wLine(cx, 0, cx, 72, edge(l * 0.6), 5); wLine(cx - s * 24, 72, cx + s * 2, 72, edge(l * 0.6), 5); wLine(cx + s * 2, 72, cx + s * 2, 160, edge(l * 0.6), 5); } }
  // 7 冰箱 (tall, two doors)
  { const x = SPOT_X[6], l = lt(x); wRect(x - 62, 0, x + 62, 312, INK, edge(l), 3); wLine(x - 62, 200, x + 62, 200, edge(l * 0.7), 2);
    wLine(x + 44, 220, x + 44, 280, edge(l), 4); wLine(x + 44, 120, x + 44, 180, edge(l), 4); }
  // 8 灶台: counter with a hob, a hood above
  { const x = SPOT_X[7], l = lt(x); wRect(x - 92, 0, x + 92, 138, INK, edge(l), 2.5); wRect(x - 70, 138, x + 10, 146, edge(l * 0.8));
    wPoly([[x - 60, 360], [x + 60, 360], [x + 40, 400], [x - 40, 400]], INK, edge(l * 0.7), 2); wLine(x, 400, x, 440, edge(l * 0.5), 4); }
  // 9 书架
  { const x = SPOT_X[8], l = lt(x); wRect(x - 70, 0, x + 70, 310, INK, edge(l), 2.5);
    for (const y of [80, 160, 240]) wLine(x - 70, y, x + 70, y, edge(l * 0.8), 2);
    const r = mulberry32(9);
    for (const y0 of [0, 80, 160, 240]) { let bx = x - 62; while (bx < x + 52) { const bw = 10 + r() * 10, bh = 44 + r() * 26; wRect(bx, y0 + 2, bx + bw, y0 + 2 + bh, r() > 0.5 ? '#141d40' : '#101838', edge(l * 0.35), 1); bx += bw + 3; } } }
  // 10 床
  { const x = SPOT_X[9], l = lt(x); wRect(x - 120, 30, x + 105, 82, INK, edge(l), 2.5); wRect(x + 70, 0, x + 92, 170, INK, edge(l), 2.5);
    wRect(x + 20, 82, x + 68, 104, INK2, edge(l * 0.8), 2); wLine(x - 112, 0, x - 112, 30, edge(l * 0.6), 5); }
}

// ---------- the ten lamps: cord, shade, bulb, a soft cone of light down to the floor ----------
function drawLampCones(L) {
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 10; i++) {
    if (L[i] <= 0.01) continue;
    const x = wx(SPOT_X[i]), y0 = wy(LAMP_Y), y1 = wy(0), w0 = 34 * CAM.Z, w1 = 150 * CAM.Z;
    const g = ctx.createLinearGradient(0, y0, 0, y1);
    g.addColorStop(0, `rgba(255,214,150,${0.30 * L[i]})`); g.addColorStop(1, `rgba(255,214,150,${0.05 * L[i]})`);
    ctx.beginPath(); ctx.moveTo(x - w0, y0); ctx.lineTo(x + w0, y0); ctx.lineTo(x + w1, y1); ctx.lineTo(x - w1, y1); ctx.closePath();
    ctx.fillStyle = g; ctx.fill();
    const fg = ctx.createRadialGradient(x, y1, 4, x, y1, w1 * 1.2);
    fg.addColorStop(0, `rgba(255,200,130,${0.22 * L[i]})`); fg.addColorStop(1, 'rgba(255,200,130,0)');
    ctx.fillStyle = fg; ctx.fillRect(x - w1 * 1.2, y1 - 30 * CAM.Z, w1 * 2.4, 60 * CAM.Z);
  }
  ctx.restore();
}
function drawLamps(L) {
  for (let i = 0; i < 10; i++) {
    const x = SPOT_X[i], l = L[i];
    wLine(x, LAMP_Y + 26, x, HOUSE.ceil, 'rgba(150,165,210,0.55)', 2.5);
    wPoly([[x - 24, LAMP_Y], [x + 24, LAMP_Y], [x + 12, LAMP_Y + 28], [x - 12, LAMP_Y + 28]], lerpColor('#1a2248', '#e8a64e', l), WARM(0.25 + 0.6 * l), 2);
    if (l > 0.01) {
      ctx.save(); ctx.shadowColor = '#ffcf80'; ctx.shadowBlur = 26 * l;
      circle(wx(x), wy(LAMP_Y - 4), 9 * CAM.Z, `rgba(255,236,190,${0.35 + 0.65 * l})`); ctx.restore();
    } else circle(wx(x), wy(LAMP_Y - 4), 7 * CAM.Z, 'rgba(120,130,170,0.35)');
  }
}
// number badge and name of each spot (screen-size text, so it stays readable when the camera pulls back)
function drawSpotTags(bt, A) {
  for (let i = 0; i < 10; i++) {
    const a = A[i];
    if (a <= 0.001) continue;
    const x = wx(SPOT_X[i]), by = wy(470), ny = wy(410);
    const edgeA = clamp((x - 50) / 40) * clamp((1870 - x) / 40);   // spots leaving the frame (step ② follows him)
    if (edgeA <= 0) continue;
    withAlpha(a * edgeA, () => {
      withScale(x, by, 0.6 + 0.4 * clamp(a * 1.2), () => {
        ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 14; circle(x, by, 25, COL.yellow); ctx.restore();
        txt(String(i + 1), x, by + 1, { size: 34, weight: 800, fam: 'mono', color: '#14100a', align: 'center' });
      });
      txt(SPOT_NAME[i], x, ny, { size: 34, weight: 900, color: COL.cream, align: 'center' });
    });
  }
}

// soft vignette (static)
function drawVignette() {
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.5, W / 2, H / 2, H * 1.08);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,3,12,0.42)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
}
