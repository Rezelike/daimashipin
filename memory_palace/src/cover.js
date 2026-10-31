// cover.js — the code-drawn fallback cover (the real cover is made by the user with ChatGPT, see out/封面提示词.txt).
// Douyin keeps ONE cover picture and crops both the 3:4 竖封面 (profile grid) and the 4:3 横封面 from it, so this is one
// 1920x1440 picture: the night background across the full width (= 横封面), the whole design in the centre 1080 px (= the
// 竖封面 crop). No people; the topic in plain words, what to do, the proof with its label; the bottom-left of the 3:4 crop
// stays empty (the play count sits there).
const COVER_W = 1920, COVER_H = 1440, CROP_W = 1080, CROP_X = (COVER_W - CROP_W) / 2;

function coverBackground() {
  const w = COVER_W, h = COVER_H;
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, '#03061a'); g.addColorStop(0.6, '#0a1236'); g.addColorStop(1, '#141b44');
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  const r = mulberry32(20170308);
  for (let i = 0; i < 120; i++) { const x = r() * w, y = r() * 900; circle(x, y, 0.7 + r() * 1.6, `rgba(220,230,255,${(0.2 + r() * 0.5) * (1 - y / 1000)})`); }
  const rg = ctx.createRadialGradient(w / 2 + 160, 1180, 20, w / 2 + 160, 1180, 760);
  rg.addColorStop(0, 'rgba(255,180,100,0.28)'); rg.addColorStop(1, 'rgba(255,180,100,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, w, h);
}
// a sagging string of n bulbs, `on` of them lit, from x0 to x1 (crop coordinates)
function coverString(x0, x1, y, n, on, sag) {
  ctx.save(); ctx.strokeStyle = 'rgba(150,165,210,0.6)'; ctx.lineWidth = 3; ctx.beginPath();
  for (let u = 0; u <= 1.0001; u += 0.02) { const xx = lerp(x0, x1, u), yy = y + sag * Math.sin(Math.PI * u); u ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); }
  ctx.stroke(); ctx.restore();
  for (let k = 0; k < n; k++) {
    const u = (k + 0.5) / n, x = lerp(x0, x1, u), yy = y + sag * Math.sin(Math.PI * u) + 16;
    if (k < on) { ctx.save(); ctx.shadowColor = '#ffc861'; ctx.shadowBlur = 22; ellipse(x, yy, 11, 15, '#ffd57e'); ctx.restore(); }
    else ellipse(x, yy, 11, 15, '#1e2650');
  }
}
function drawCover(bgOnly = false) {
  coverBackground();
  if (bgOnly) return;
  ctx.save(); ctx.translate(CROP_X, 0);
  const w = CROP_W;
  txt('记忆宫殿有用吗？', w / 2, 180, { size: 120, weight: 900, color: COL.cream, align: 'center' });
  txt('有用，但要练', w / 2, 340, { size: 120, weight: 900, color: COL.yellow, align: 'center', glow: 34 });
  rich([{ s: '背清单：每天 30 分钟，练 ' }, { s: '40 天', color: COL.yellow }], w / 2, 480, { size: 50, weight: 900, align: 'center' });
  txt('72 个词，记住几个', w / 2, 620, { size: 40, weight: 700, color: COL.grayHi, align: 'center' });
  // proof (Dresler 2017, 20 min recall of 72 words, group means): 26.5 before, 62.5 after 40 days
  txt('练之前', 120, 760, { size: 48, weight: 900, color: COL.grayHi });
  coverString(320, 980, 735, 18, 7, 22);
  txt('26.5 个', 980, 840, { size: 52, weight: 900, color: COL.grayHi, align: 'right' });
  txt('练 40 天', 120, 1000, { size: 48, weight: 900, color: COL.cream });
  coverString(320, 980, 975, 18, 16, 22);
  txt('62.5 个', 980, 1090, { size: 64, weight: 900, color: COL.yellow, align: 'right', glow: 20 });
  ctx.restore();
}
