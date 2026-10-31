// cover.js — the code-drawn fallback cover (the real cover is made by the user with ChatGPT, see out/封面提示词.txt).
// Douyin keeps ONE cover picture and crops the 3:4 竖封面 (profile grid) and the 4:3 横封面 from it, so this draws one
// 1920x1440 picture: background across the full width (= 横封面), the whole design in the centre 1080 px (= 竖封面).
// No people; the topic, what to do, the proof with its label; the bottom-left of the 3:4 crop stays empty (play count).
const COVER_W = 1920, COVER_H = 1440, CROP_W = 1080, CROP_X = (COVER_W - CROP_W) / 2;

function coverBackground(w, h) {
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, '#05070f'); g.addColorStop(0.6, '#0a1124'); g.addColorStop(1, '#05070f');
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  const rg = ctx.createRadialGradient(w / 2, h * 0.7, 40, w / 2, h * 0.7, 900);
  rg.addColorStop(0, 'rgba(255,190,90,0.10)'); rg.addColorStop(1, 'rgba(255,190,90,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, w, h);
  // the card table's curved neon edge, faint, across the whole width
  ctx.save(); ctx.strokeStyle = 'rgba(143,232,248,0.16)'; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.ellipse(w / 2, h * 0.62, w * 0.62, h * 0.3, 0, 0.08 * Math.PI, 0.92 * Math.PI); ctx.stroke(); ctx.restore();
  const vg = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.45, w / 2, h / 2, Math.max(w, h) * 0.8);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.5)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, w, h);
}

// the proof: Kornell 2009 Exp 3, test on day 6: four small stacks 34 %, one big deck 65 %
function coverProof(w) {
  const lx = 270, rx = 810;
  // four small stacks of 5 (2 x 2), dim cyan
  [[-74, 1000], [74, 1000], [-74, 1088], [74, 1088]].forEach(([dx, by]) => {
    ctx.save(); ctx.translate(lx + dx, by); ctx.scale(1.25, 1.25);
    deckStack(0, 0, 5, { w: 104, pal: SMALL, lit: 0.15 });
    ctx.restore();
  });
  // one big deck of 20, glowing yellow
  ctx.save(); ctx.translate(rx, 1090); ctx.scale(1.9, 1.9);
  deckStack(0, 0, 20, { w: 130, pal: BIG, lit: 1 });
  ctx.restore();
  txt('34%', lx, 820, { size: 104, weight: 800, fam: 'mono', color: '#bfe9f3', align: 'center' });
  txt('65%', rx, 820, { size: 120, weight: 800, fam: 'mono', color: COL.yellowHi, align: 'center', glow: 30, glowColor: COL.yellow });
  txt('四小叠', lx, 1196, { size: 54, weight: 900, color: COL.cyan, align: 'center' });
  txt('一大叠', rx, 1196, { size: 54, weight: 900, color: COL.yellow, align: 'center', glow: 12 });
}

function drawCover(bgOnly = false) {
  coverBackground(COVER_W, COVER_H);
  if (bgOnly) return;
  ctx.save();
  ctx.translate(CROP_X, 0);
  const w = CROP_W;
  txt('单词卡分小叠？', w / 2, 176, { size: 128, weight: 900, color: COL.cream, align: 'center' });
  txt('洗成一大叠', w / 2, 344, { size: 168, weight: 900, color: COL.yellow, align: 'center', glow: 36 });
  rich([{ s: '同一叠' }, { s: '分几天', color: COL.yellow }, { s: '过，每天一两遍' }], w / 2, 496, { size: 56, weight: 900, align: 'center' });
  txt('第 6 天考试，答对：', w / 2, 618, { size: 46, weight: 900, color: COL.grayHi, align: 'center' });
  coverProof(w);
  ctx.restore();
}
