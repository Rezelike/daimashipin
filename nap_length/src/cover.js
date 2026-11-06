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
  ctx.restore();
  // still water under the horizon instead of the grid floor (this episode's stage)
  const wg = ctx.createLinearGradient(0, horizon, 0, h);
  wg.addColorStop(0, '#1a527c'); wg.addColorStop(0.4, '#123b63'); wg.addColorStop(1, '#0a1b3d');
  ctx.fillStyle = wg; ctx.fillRect(0, horizon, w, h - horizon);
  ctx.save(); ctx.shadowColor = COL.cyan; ctx.shadowBlur = 10;
  line(0, horizon, w, horizon, 'rgba(165,236,255,0.85)', 3); ctx.restore();
  const rng = mulberry32(20010315);
  for (let i = 0; i < 70; i++) {
    const x = rng() * w, y = rng() * horizon, r = 0.8 + rng() * 1.8, a = 0.12 + rng() * 0.4;
    ctx.fillStyle = `rgba(170,215,255,${a})`;
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
  }
  const vg = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.45, w / 2, h / 2, Math.max(w, h) * 0.8);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,4,15,0.5)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, w, h);
}

// Tietzel & Lack 2001, table 3: symbol -> digit substitutions in 90 s, 5 min after waking (12 students, short night before):
// no nap 55.0, 10-min nap 65.3, 30-min nap 50.6
const COVER_BOARDS = [['没睡', 55, COL.grayHi], ['睡 10 分钟', 65, COL.yellow], ['睡 30 分钟', 51, COL.pink]];
function drawCover(bgOnly = false) {
  coverBackground(COVER_W, COVER_H, 1180);
  if (bgOnly) return;
  ctx.save();
  ctx.translate(CROP_X, 0);
  const w = CROP_W;
  txt('午睡更懵？', w / 2, 190, { size: 140, weight: 900, color: COL.cream, align: 'center' });
  txt('只睡 10 分钟', w / 2, 370, { size: 140, weight: 900, color: COL.yellow, align: 'center', glow: 34 });
  txt('马上要用脑的话', w / 2, 516, { size: 52, weight: 900, color: COL.cream, align: 'center' });
  txt('醒来 5 分钟，做同一种题（换对几个）', w / 2, 640, { size: 40, weight: 900, color: COL.grayHi, align: 'center' });
  COVER_BOARDS.forEach(([label, v, tone], i) => {
    const cx = 250 + i * 290, best = i === 1, worst = i === 2;
    drawScoreBoard(cx, 700, label, v, {
      w: 260, h: 230, tone, hi: 1, post: false, labelSize: 40, numSize: 120,
      numColor: best ? COL.yellowHi : worst ? COL.pink : COL.cream, glow: best ? 24 : 0,
    });
  });
  okMark(540 + 118, 704, 36);
  txt('一醒就好', 540, 990, { size: 46, weight: 900, color: COL.yellow, align: 'center', glow: 14 });
  txt('比没睡还差', 830, 990, { size: 42, weight: 900, color: COL.pink, align: 'center' });
  txt('Tietzel & Lack 2001 · 前一晚只睡约 5 小时', w / 2, 1080, { size: 30, weight: 700, color: COL.grayHi, align: 'center' });
  ctx.restore();
}
