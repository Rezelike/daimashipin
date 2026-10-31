// cover.js — the code-drawn fallback cover (the real cover is made by the user with ChatGPT, see out/封面提示词.txt).
// Douyin keeps ONE cover picture and crops the 3:4 竖封面 (profile grid) and the 4:3 横封面 from it, so this draws one
// 1920x1440 picture: background across the full width (= 横封面), the whole design in the centre 1080 px (= 竖封面).
// No people; the topic, what to do, the proof with its label; the bottom-left of the 3:4 crop stays empty (play count).
const COVER_W = 1920, COVER_H = 1440, CROP_W = 1080, CROP_X = (COVER_W - CROP_W) / 2;

function coverBackground(w, h) {
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, '#05070f'); g.addColorStop(0.6, '#0a1124'); g.addColorStop(1, '#05070f');
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  const rg = ctx.createRadialGradient(w / 2, h * 0.68, 40, w / 2, h * 0.68, 900);
  rg.addColorStop(0, 'rgba(255,190,90,0.10)'); rg.addColorStop(1, 'rgba(255,190,90,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, w, h);
  // a faint sound wave across the whole width
  ctx.save(); ctx.strokeStyle = 'rgba(70,190,240,0.18)'; ctx.lineWidth = 3; ctx.beginPath();
  for (let x = 0; x <= w; x += 6) {
    const d = (x - w / 2) / 360, y = h * 0.86 + Math.sin(x / 18) * 34 * Math.exp(-d * d);
    x ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  }
  ctx.stroke(); ctx.restore();
  const vg = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.45, w / 2, h / 2, Math.max(w, h) * 0.8);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.5)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, w, h);
}

// the proof: MacLeod et al. 2010 Exp 1, one word list, half read aloud: recognised 60 % (silent) vs 76 % (aloud)
function coverStacks(cx, bottom) {
  const bw = 230, bh = 46, gap = 8, H10 = 10 * bh + 9 * gap;
  [[cx - 170, 0.598, 'silent', '默读的'], [cx + 170, 0.760, 'aloud', '念出声的']].forEach(([x, lv, kind, label]) => {
    const n = Math.round(lv * 10 * 10) / 10;
    for (let i = 0; i < Math.ceil(n); i++) {
      const y = bottom - bh / 2 - i * (bh + gap), part = clamp(n - i);
      ctx.save();
      if (part < 1) { ctx.beginPath(); ctx.rect(x - bw, y + bh / 2 - bh * part, bw * 2, bh * part); ctx.clip(); }
      wordBlock(x, y, bw, bh, { solid: kind === 'aloud' ? 1 : 0, bright: 1, r: 12 });
      ctx.restore();
    }
    const top = bottom - lv * H10;
    txt(`${Math.round(lv * 100)}%`, x, top - 56, { size: 92, weight: 800, fam: 'mono', color: kind === 'aloud' ? COL.yellowHi : '#d5dbe8',
      align: 'center', glow: kind === 'aloud' ? 26 : 0 });
    txt(label, x, bottom + 54, { size: 50, weight: 900, color: kind === 'aloud' ? COL.yellow : COL.grayHi, align: 'center' });
  });
}

function drawCover(bgOnly = false) {
  coverBackground(COVER_W, COVER_H);
  if (bgOnly) return;
  ctx.save();
  ctx.translate(CROP_X, 0);
  const w = CROP_W;
  txt('背书要读出声？', w / 2, 168, { size: 132, weight: 900, color: COL.cream, align: 'center' });
  txt('挑着念', w / 2, 338, { size: 168, weight: 900, color: COL.yellow, align: 'center', glow: 36 });
  rich([{ s: '只把' }, { s: '要背的几句', color: COL.yellow }, { s: '读出声' }], w / 2, 492, { size: 60, weight: 900, align: 'center' });
  txt('同一张单词表，考完认得出：', w / 2, 590, { size: 46, weight: 900, color: COL.grayHi, align: 'center' });
  coverStacks(w / 2, 1170);
  ctx.restore();
}
