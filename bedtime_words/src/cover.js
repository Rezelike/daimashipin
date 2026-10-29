// cover.js — the code-drawn fallback cover (the real cover is made by the user with ChatGPT, see out/封面提示词.txt).
// Douyin's publish page keeps ONE cover picture and crops both the 3:4 竖封面 (profile grid) and the 4:3 横封面 from it,
// so this draws one 1920x1440 picture directly: the background across the full width (= 横封面), the whole design in the
// centre 1080 px (= the 竖封面 crop). Rules from the Douyin data: no people; say the topic, what to do, and the proof with
// its label; keep the bottom-left of the 3:4 crop empty (the play count sits there).
const COVER_W = 1920, COVER_H = 1440, CROP_W = 1080, CROP_X = (COVER_W - CROP_W) / 2;

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
  const rng = mulberry32(20161016);
  for (let i = 0; i < 70; i++) {
    const x = rng() * w, y = rng() * horizon, r = 0.8 + rng() * 1.8, a = 0.12 + rng() * 0.4;
    ctx.fillStyle = `rgba(170,215,255,${a})`;
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
  }
  const vg = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.45, w / 2, h / 2, Math.max(w, h) * 0.8);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,4,15,0.5)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, w, h);
}

// 「一周后还记得（16 个里）」 (Mazza et al. 2016, means): learned in the morning + relearned in the evening 11.25,
// learned before bed + relearned in the morning 15.2. Both groups relearned to criterion; only the schedule differed.
const PLATES = [['早上背', COL.cyan], ['睡前背', COL.yellow]];
function coverChart(x, y, w, h) {
  hudPanel(x, y, w, h, 1, 1);
  txt('一周后还记得（16 个里）', x + w / 2, y + 58, { size: 46, weight: 900, color: COL.cream, align: 'center' });
  const xa = x + w * 0.3, xb = x + w * 0.7, bw = 124;
  const meterTop = y + 160, bottom = y + h - 112, hMax = bottom - meterTop;
  const la = 11.25 / 16, lb = 15.2 / 16;
  drawMeter(xa, bottom, bw, hMax, la, { color: '#66728f', colorHi: '#8994ad', label: '', glow: 0 });
  drawMeter(xb, bottom, bw, hMax, lb, { color: COL.yellow, colorHi: COL.yellowHi, label: '' });
  const topA = bottom - la * hMax, topB = bottom - lb * hMax;
  txt('11 个', xa, topA - 40, { size: 50, weight: 900, color: COL.grayHi, align: 'center' });
  ctx.save(); ctx.shadowColor = COL.yellow; ctx.shadowBlur = 22; circle(xb, topB, 30, COL.yellow); ctx.restore();
  checkBadge(xb, topB, 30, { color: '#0d1838', p: 1, lw: 4.5 });
  txt('15 个', xb + bw / 2 + 24, topB + 4, { size: 50, weight: 900, color: COL.yellow, glow: 14 });
  PLATES.forEach(([s, c], i) => namePlate(i ? xb : xa, bottom + 58, s, c, { size: 40 }));
}

function drawCover(bgOnly = false) {
  coverBackground(COVER_W, COVER_H, 1115);
  if (bgOnly) return;
  ctx.save();
  ctx.translate(CROP_X, 0);
  const w = CROP_W;
  txt('单词总忘？', w / 2, 170, { size: 150, weight: 900, color: COL.cream, align: 'center' });
  txt('睡前背', w / 2, 352, { size: 150, weight: 900, color: COL.yellow, align: 'center', glow: 34 });
  rich([{ s: '睡一觉，早上' }, { s: '默到全对', color: COL.yellow }], w / 2, 506, { size: 56, weight: 900, align: 'center' });
  coverChart(90, 584, 900, 540);
  ctx.restore();
}
