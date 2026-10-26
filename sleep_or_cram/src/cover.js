// cover.js — cover layout references for ChatGPT (and fallback covers): 3:4 1080x1440 (profile grid) and 4:3 1440x1080.
// Rules from the Douyin data: no people; say the topic, what to do, and the proof with its label; keep the bottom-left
// empty (the play count sits there). The chart uses the video's own wording (opening, 3.98–4.45 s): both bars are
// compared with the 「只休息」 line, never with each other.
const COVER_SIZES = { '3x4': [1080, 1440], '4x3': [1440, 1080] };

// first line = the accepted ChatGPT cover's 「学累了？」 (2026-10-26; the old 「学累了，睡还是背？」 wording was dropped)
const Q_SPANS = () => [{ s: '学累了？' }];
const SUB_SPANS = () => [{ s: '睡 ' }, { s: '30–60 分钟', color: COL.yellow }, { s: '，醒来接着学' }];

function coverBackground(w, h, horizon) {
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, '#0a1330'); g.addColorStop(0.6, '#0f1c42'); g.addColorStop(1, '#0a1231');
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  const rg = ctx.createRadialGradient(w / 2, h * 0.45, 40, w / 2, h * 0.45, Math.max(w, h) * 0.75);
  rg.addColorStop(0, 'rgba(52,98,178,0.22)'); rg.addColorStop(1, 'rgba(52,98,178,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, w, h);

  ctx.save();
  ctx.strokeStyle = 'rgba(95,155,225,0.065)'; ctx.lineWidth = 1;
  ctx.beginPath();
  for (let x = (w / 2) % 64; x <= w; x += 64) { ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, horizon); }
  for (let y = horizon; y >= 0; y -= 64) { ctx.moveTo(0, y + 0.5); ctx.lineTo(w, y + 0.5); }
  ctx.stroke();
  ctx.beginPath(); ctx.rect(0, horizon, w, h - horizon); ctx.clip();
  const fg = ctx.createLinearGradient(0, horizon, 0, h);
  fg.addColorStop(0, 'rgba(20,40,85,0.55)'); fg.addColorStop(1, 'rgba(8,16,40,0.2)');
  ctx.fillStyle = fg; ctx.fillRect(0, horizon, w, h - horizon);
  ctx.lineWidth = 1.2;
  for (let i = -16; i <= 16; i++) {
    ctx.strokeStyle = `rgba(80,180,235,${Math.max(0.04, 0.16 - Math.abs(i) * 0.004)})`;
    ctx.beginPath(); ctx.moveTo(w / 2 + i * 14, horizon); ctx.lineTo(w / 2 + i * 150, h); ctx.stroke();
  }
  for (let k = 1; k <= 7; k++) {
    const u = k / 7, y = horizon + (h - horizon) * u * u;
    ctx.strokeStyle = `rgba(80,180,235,${0.03 + 0.16 * u})`;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }
  ctx.restore();

  const hg = ctx.createLinearGradient(0, 0, w, 0);
  hg.addColorStop(0, 'rgba(70,190,240,0)'); hg.addColorStop(0.5, 'rgba(70,190,240,0.38)'); hg.addColorStop(1, 'rgba(70,190,240,0)');
  ctx.fillStyle = hg; ctx.fillRect(0, horizon - 1, w, 2);
  const rng = mulberry32(20191029);
  for (let i = 0; i < 70; i++) {
    const x = rng() * w, y = rng() * horizon, r = 0.8 + rng() * 1.8, a = 0.12 + rng() * 0.4;
    ctx.fillStyle = `rgba(170,215,255,${a})`;
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
  }
  const vg = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.45, w / 2, h / 2, Math.max(w, h) * 0.8);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,4,15,0.5)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, w, h);
}

function coverRestLine(x1, x2, y, labelX, size) {
  const gap = measure('只休息', size, 700) + 40;
  ctx.save(); ctx.setLineDash([14, 10]); ctx.strokeStyle = 'rgba(181,191,214,0.85)'; ctx.lineWidth = 3.5;
  ctx.beginPath();
  ctx.moveTo(x1, y); ctx.lineTo(labelX - gap / 2, y);
  ctx.moveTo(labelX + gap / 2, y); ctx.lineTo(x2, y);
  ctx.stroke(); ctx.restore();
  txt('只休息', labelX, y, { size, weight: 700, color: COL.grayHi, align: 'center' });
}

// 「一周后还记得的」 (Cousins et al. 2019, day-8 test), same levels as the video's opening: the cram bar back at the
// rest line (0.44 vs 0.42), the nap bar above it. Slots: title / status labels / bars / name plates.
const PLATES = ['接着背 1 小时', '午睡 1 小时'];
function coverChart(x, y, w, h, o) {
  const { bw, title, fa, fb } = o;
  hudPanel(x, y, w, h, 1, 1);
  txt('一周后还记得的', x + w / 2, y + 58, { size: title, weight: 900, color: COL.cream, align: 'center' });
  const xa = x + w * fa, xb = x + w * fb;
  const meterTop = y + 160, bottom = y + h - 112, hMax = bottom - meterTop;
  const restY = bottom - 0.42 * hMax, nap = 0.82;
  drawMeter(xa, bottom, bw, hMax, 0.44, { color: '#66728f', colorHi: '#8994ad', label: '', glow: 0 });
  drawMeter(xb, bottom, bw, hMax, nap, { color: COL.yellow, colorHi: COL.yellowHi, label: '' });
  coverRestLine(x + 36, x + w - 36, restY, (xa + xb) / 2, 36);
  const top = bottom - nap * hMax;
  ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 22; circle(xb, top, 30, COL.yellow); ctx.restore();
  checkBadge(xb, top, 30, { color: '#0d1838', p: 1, lw: 4.5 });
  txt('优势没了', xa, y + 126, { size: 38, weight: 700, color: COL.grayHi, align: 'center' });
  txt('还领先', xb, y + 126, { size: 44, weight: 900, color: COL.yellow, align: 'center', glow: 14 });
  // name plates: largest size that keeps both inside the panel with a gap between them
  let size = o.plate;
  const pw = (s, z) => measure(s, z, 900) + 48;
  while (size > 26 && (xa + pw(PLATES[0], size) / 2 + 28 > xb - pw(PLATES[1], size) / 2
    || xa - pw(PLATES[0], size) / 2 < x + 18 || xb + pw(PLATES[1], size) / 2 > x + w - 18)) size -= 1;
  namePlate(xa, bottom + 58, PLATES[0], COL.cyan, { size });
  namePlate(xb, bottom + 58, PLATES[1], COL.yellow, { size });
}

function coverPill(x, cy, size, align) {
  const s = '1 分钟学会怎么午睡';
  const tw = measure(s, size, 900), padX = size * 1.1, ph = size * 1.9, pw = tw + padX * 2;
  const x0 = align === 'center' ? x - pw / 2 : x;
  ctx.save(); ctx.shadowColor = 'rgba(247,185,62,0.45)'; ctx.shadowBlur = 18;
  rrect(x0, cy - ph / 2, pw, ph, ph / 2, 'rgba(70,54,22,0.88)', COL.yellow, 3);
  ctx.restore();
  txt(s, x0 + pw / 2, cy + 1, { size, weight: 900, color: COL.cream, align: 'center' });
}

function drawCover(kind, bgOnly = false) {
  if (kind === '3x4') {
    const w = 1080;
    coverBackground(w, 1440, 1115);
    if (bgOnly) return;
    rich(Q_SPANS(), w / 2, 172, { size: 92, weight: 900, align: 'center' });
    txt('先睡一觉', w / 2, 362, { size: 200, weight: 900, color: COL.yellow, align: 'center', glow: 34 });
    rich(SUB_SPANS(), w / 2, 528, { size: 56, weight: 900, align: 'center' });
    coverChart(90, 596, 900, 500, { bw: 124, plate: 38, title: 46, fa: 0.3, fb: 0.7 });
    coverPill(w / 2, 1190, 52, 'center');
  } else {
    coverBackground(1440, 1080, 905);
    if (bgOnly) return;
    const L = 96;
    rich(Q_SPANS(), L, 236, { size: 66, weight: 900 });
    txt('先睡一觉', L - 6, 400, { size: 150, weight: 900, color: COL.yellow, glow: 30 });
    rich(SUB_SPANS(), L, 552, { size: 44, weight: 900 });
    coverPill(L, 684, 44, 'left');
    coverChart(750, 170, 610, 660, { bw: 104, plate: 36, title: 44, fa: 0.26, fb: 0.74 });
  }
}
