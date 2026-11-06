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
  const rng = mulberry32(20230505);
  for (let i = 0; i < 70; i++) {
    const x = rng() * w, y = rng() * horizon, r = 0.8 + rng() * 1.8, a = 0.12 + rng() * 0.4;
    ctx.fillStyle = `rgba(170,215,255,${a})`;
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
  }
  const vg = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.45, w / 2, h / 2, Math.max(w, h) * 0.8);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,4,15,0.5)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, w, h);
}

// the proof objects: big headphones resting on an open textbook, a lyric bubble crossed out next to them
function coverObjects(cx, cy) {
  // open book
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14;
  ctx.fillStyle = '#e9e2d3';
  ctx.beginPath(); ctx.moveTo(cx - 330, cy + 40); ctx.quadraticCurveTo(cx - 160, cy + 4, cx, cy + 40);
  ctx.quadraticCurveTo(cx + 160, cy + 4, cx + 330, cy + 40); ctx.lineTo(cx + 350, cy + 150);
  ctx.quadraticCurveTo(cx + 170, cy + 118, cx, cy + 156); ctx.quadraticCurveTo(cx - 170, cy + 118, cx - 350, cy + 150); ctx.closePath(); ctx.fill();
  ctx.restore();
  ctx.save(); ctx.strokeStyle = 'rgba(110,122,156,0.5)'; ctx.lineWidth = 4; ctx.lineCap = 'round';
  for (let i = 0; i < 4; i++) {
    const y = cy + 62 + i * 20;
    ctx.beginPath(); ctx.moveTo(cx - 290 + i * 4, y); ctx.lineTo(cx - 40, y + 4); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx + 40, y + 4); ctx.lineTo(cx + 290 - i * 4, y); ctx.stroke();
  }
  ctx.restore();
  line(cx, cy + 40, cx, cy + 156, 'rgba(120,110,95,0.6)', 3);
  // headphones on the book
  ctx.save(); ctx.lineCap = 'round';
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 30;
  ctx.beginPath(); ctx.ellipse(cx, cy + 10, 205, 250, 0, Math.PI * 1.08, Math.PI * 1.92);
  ctx.strokeStyle = '#2b3554'; ctx.lineWidth = 36; ctx.stroke();
  ctx.shadowBlur = 0; ctx.strokeStyle = '#55628c'; ctx.lineWidth = 10; ctx.stroke();
  ctx.restore();
  for (const sx of [-1, 1]) {
    const x = cx + sx * 196;
    line(x, cy - 66, x, cy - 30, '#2b3554', 22);
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 24;
    rrect(x - 56, cy - 40, 112, 168, 46, '#e9edf6'); ctx.restore();
    ctx.save(); ctx.shadowColor = COL.green; ctx.shadowBlur = 26;
    rrect(x - 30, cy - 12, 60, 112, 28, COL.green); ctx.restore();
  }
  // the lyric bubble that is switched off
  ctx.save(); ctx.translate(cx + 300, cy - 210); ctx.rotate(0.08);
  ctx.save(); ctx.shadowColor = LYR; ctx.shadowBlur = 30;
  ctx.beginPath(); ctx.roundRect(-110, -58, 220, 116, 56); ctx.moveTo(-70, 50); ctx.lineTo(-92, 92); ctx.lineTo(-30, 54);
  ctx.fillStyle = LYR; ctx.fill(); ctx.restore();
  iconNote(-48, -2, 70, '#5a0f2c');
  txt('啦啦', 30, 2, { size: 52, weight: 900, color: '#5a0f2c', align: 'center' });
  ctx.restore();
  line(cx + 190, cy - 120, cx + 410, cy - 300, COL.cream, 14);
  line(cx + 190, cy - 120, cx + 410, cy - 300, LYR, 6);
}
function proofChip(x, y, label, value, color) {
  ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 20;
  rrect(x - 210, y - 58, 420, 116, 26, 'rgba(12,26,58,0.92)', color, 3); ctx.restore();
  txt(label, x - 184, y + 2, { size: 40, weight: 900, color: COL.cream });
  txt(value, x + 186, y + 2, { size: 52, weight: 800, fam: 'mono', color, align: 'right', glow: 12 });
}

function drawCover(bgOnly = false) {
  coverBackground(COVER_W, COVER_H, 1115);
  if (bgOnly) return;
  ctx.save();
  ctx.translate(CROP_X, 0);
  const w = CROP_W;
  txt('听歌背书？', w / 2, 196, { size: 168, weight: 900, color: COL.cream, align: 'center' });
  txt('关掉歌词', w / 2, 386, { size: 168, weight: 900, color: COL.yellow, align: 'center', glow: 34 });
  rich([{ s: '背书、读书时，别听' }, { s: '带词的歌', color: LYR }], w / 2, 540, { size: 54, weight: 900, align: 'center' });
  coverObjects(w / 2, 840);
  // Souza & Barbosa 2023: 20 words, the same students, means
  txt('20 个词里平均记住', w / 2, 1066, { size: 46, weight: 900, color: COL.cream, align: 'center' });
  proofChip(w / 2 - 222, 1160, '安静', '8.4 个', COL.cyan);
  proofChip(w / 2 + 222, 1160, '带词的歌', '7.4 个', LYR);
  ctx.restore();
}
