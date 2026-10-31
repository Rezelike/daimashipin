// cover.js — the code-drawn fallback cover (the real cover is made by the user with ChatGPT, see out/封面提示词.txt).
// Douyin keeps ONE cover picture and crops both the 3:4 竖封面 (profile grid) and the 4:3 横封面 from it, so this is one
// 1920x1440 picture: the dawn background across the full width (= 横封面), the whole design in the centre 1080 px (= the
// 竖封面 crop). Rules from the Douyin data: no people; the topic in plain words, what to do, the proof with its label;
// the bottom-left of the 3:4 crop stays empty (the play count sits there).
const COVER_W = 1920, COVER_H = 1440, CROP_W = 1080, CROP_X = (COVER_W - CROP_W) / 2;

// the road inside the crop: days 0..80 from x 480 to 1040 (crop coords), rising along Lally's curve
const CR = { x0: 480, x1: 1040, yBase: 1390, rise: 600, d1: 80 };
const crX = (d) => CR.x0 + (d / CR.d1) * (CR.x1 - CR.x0);
const crY = (d) => CR.yBase - ((habitE(d) - habitE(0)) / (habitE(CR.d1) - habitE(0))) * CR.rise;

function coverBackground() {
  const w = COVER_W, h = COVER_H, hz = 1180;
  const g = ctx.createLinearGradient(0, 0, 0, hz);
  g.addColorStop(0, '#05091c'); g.addColorStop(0.5, '#0d1438'); g.addColorStop(0.82, '#24204e'); g.addColorStop(0.95, '#5a3058'); g.addColorStop(1, '#b8603e');
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, hz + 2);
  ctx.fillStyle = '#1a1230'; ctx.fillRect(0, hz, w, h - hz);
  const rg = ctx.createRadialGradient(CROP_X + 1000, hz, 10, CROP_X + 1000, hz, 1100);
  rg.addColorStop(0, 'rgba(255,170,100,0.42)'); rg.addColorStop(0.4, 'rgba(240,120,110,0.14)'); rg.addColorStop(1, 'rgba(240,120,110,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, w, h);
  const r = mulberry32(20100716);
  for (let i = 0; i < 110; i++) {
    const x = r() * w, y = r() * 760, s = 0.7 + r() * 1.8;
    circle(x, y, s, `rgba(220,230,255,${(0.2 + r() * 0.5) * (1 - y / 900)})`);
  }
  for (const [base, amp, f, col] of [[hz, 90, 0.0023, '#1c1742'], [hz + 40, 70, 0.0031, '#140f30'], [hz + 90, 50, 0.0042, '#0d0b24']]) {
    ctx.beginPath(); ctx.moveTo(0, h);
    for (let x = 0; x <= w; x += 12) ctx.lineTo(x, base - amp * (0.6 + 0.3 * Math.sin(x * f + base) + 0.1 * Math.sin(x * f * 3.1)));
    ctx.lineTo(w, h); ctx.closePath(); ctx.fillStyle = col; ctx.fill();
  }
  // the hill and the road (background too: only text and props count as the design in the cover check)
  ctx.save(); ctx.translate(CROP_X, 0);
  ctx.beginPath(); ctx.moveTo(CR.x0 - 600, h + 10); ctx.lineTo(CR.x0 - 600, CR.yBase + 60);
  ctx.quadraticCurveTo(CR.x0 - 200, CR.yBase + 30, CR.x0, CR.yBase);
  for (let d = 0; d <= CR.d1; d += 0.5) ctx.lineTo(crX(d), crY(d));
  ctx.lineTo(COVER_W - CROP_X + 10, crY(CR.d1)); ctx.lineTo(COVER_W - CROP_X + 10, h + 10); ctx.closePath();
  const hg = ctx.createLinearGradient(0, 700, 0, h); hg.addColorStop(0, '#0b1024'); hg.addColorStop(1, '#04060e');
  ctx.fillStyle = hg; ctx.fill();
  ctx.save(); ctx.shadowColor = '#ffb27a'; ctx.shadowBlur = 16;
  ctx.beginPath(); ctx.moveTo(CR.x0, CR.yBase);
  for (let d = 0; d <= CR.d1; d += 0.5) ctx.lineTo(crX(d), crY(d));
  ctx.lineTo(COVER_W - CROP_X + 10, crY(CR.d1));
  ctx.strokeStyle = 'rgba(255,200,144,0.85)'; ctx.lineWidth = 4; ctx.stroke(); ctx.restore();
  ctx.restore();
}

function coverFlag(d, text, color, ink, h, size) {
  const x = crX(d), y = crY(d), top = y - h;
  line(x, y, x, top - 8, '#c9d2ea', 6);
  circle(x, top - 10, 8, COL.cream);
  const tw = measure(text, size, 900) + 48, fh = size + 34;
  ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 30;
  rrect(x - 2 - tw, top, tw, fh, 6, color); ctx.restore();
  txt(text, x - 2 - tw / 2, top + fh / 2 + 1, { size, weight: 900, color: ink, align: 'center' });
  return { x0: x - 2 - tw, top, bottom: top + fh, x };
}

function drawCover(bgOnly = false) {
  coverBackground();
  if (bgOnly) return;
  ctx.save();
  ctx.translate(CROP_X, 0);
  const w = CROP_W;
  txt('21 天养习惯？', w / 2, 168, { size: 140, weight: 900, color: COL.cream, align: 'center' });
  txt('一般要 66 天', w / 2, 340, { size: 140, weight: 900, color: COL.yellow, align: 'center', glow: 34 });
  rich([{ s: '按 ' }, { s: '2 个多月', color: COL.yellow }, { s: '准备，漏一天没关系' }], w / 2, 486, { size: 52, weight: 900, align: 'center' });
  // proof: the road with the two flags (Lally 2010: day 21 ~2/3 of the way, an estimate; the median top at 66 days)
  const f21 = coverFlag(21, '第 21 天', '#8fa3c8', '#0d1530', 330, 50);
  txt('还没到顶', f21.x0 + (f21.x - f21.x0) / 2, f21.bottom + 46, { size: 42, weight: 900, color: COL.grayHi, align: 'center' });
  const f66 = coverFlag(66, '第 66 天', COL.yellow, '#14100a', 330, 56);
  txt('到顶', f66.x0 - 24, f66.top + 46, { size: 52, weight: 900, color: COL.yellow, align: 'right', glow: 18 });
  txt('伦敦 82 人 · 每天做一件新的小事', 90, 640, { size: 34, weight: 700, color: COL.grayHi });
  ctx.restore();
}
