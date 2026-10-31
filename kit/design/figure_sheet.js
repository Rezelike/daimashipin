// figure_sheet.js — one picture with the three candidate looks of the new figure, each in five poses.
const SHEET_W = 2560, SHEET_H = 1830, LABEL_W = 360, TILE_W = 428, TILE_H = 500, GAP = 12, TOP = 214;
const STYLES = [
  ['A', '扁平插画', ['成年人比例', '小脸、点眼睛', '没有腮红'], true],
  ['B', '霓虹线条', ['发光的线条', '没有五官', '科技感最强'], false],
  ['C', '剪影 + 轮廓光', ['深色身体', '边上一圈光', '没有五官'], false],
];
const COLS = [
  ['指着说', { pose: POSES.point, face: 'calm', pointF: true }],
  ['走路', { pose: walkPose(0.5), face: 'calm' }],
  ['托腮想', { pose: POSES.think, face: 'calm' }],
  ['跳起来', { pose: POSES.cheer, face: 'happy' }],
  ['躺下睡', { pose: POSES.lie, face: 'tired' }],
];
function tileBg(x, y, w, h) {
  const g = ctx.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, '#0a1330'); g.addColorStop(0.7, '#0f1c42'); g.addColorStop(1, '#0a1231');
  rrect(x, y, w, h, 16, g);
  const fy = y + h - 64;
  ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, 16); ctx.clip();
  const hg = ctx.createLinearGradient(x, 0, x + w, 0);
  hg.addColorStop(0, 'rgba(70,190,240,0)'); hg.addColorStop(0.5, 'rgba(70,190,240,0.4)'); hg.addColorStop(1, 'rgba(70,190,240,0)');
  ctx.fillStyle = hg; ctx.fillRect(x, fy - 1, w, 2);
  ctx.fillStyle = 'rgba(20,40,85,0.45)'; ctx.fillRect(x, fy, w, h - 64);
  ctx.restore();
  return fy;
}
function drawSheet() {
  ctx.fillStyle = '#05070d'; ctx.fillRect(0, 0, SHEET_W, SHEET_H);
  txt('新小人：三种画法，选一种', 40, 62, { size: 56, weight: 900, color: COL.cream });
  txt('一个人 · 成年人比例 · 姿势随便摆，不再坐在桌前写作业 · 同一副骨架，每期换动作和道具', 40, 128, { size: 32, weight: 700, color: COL.grayHi });
  COLS.forEach(([name], c) => txt(name, LABEL_W + c * (TILE_W + GAP) + TILE_W / 2, TOP - 16, { size: 34, weight: 900, color: COL.cream, align: 'center' }));
  STYLES.forEach(([key, name, lines, rec], r) => {
    const y = TOP + 10 + r * (TILE_H + GAP);
    txt(key, 40, y + 70, { size: 96, weight: 800, fam: 'mono', color: COL.yellow });
    if (rec) { rrect(118, y + 44, 104, 50, 25, COL.yellow); txt('推荐', 170, y + 70, { size: 30, weight: 900, color: '#0b1736', align: 'center' }); }
    txt(name, 40, y + 160, { size: 40, weight: 900, color: COL.cream });
    lines.forEach((l, i) => txt(l, 40, y + 214 + i * 40, { size: 28, weight: 700, color: COL.grayHi }));
    COLS.forEach(([, opt], c) => {
      const x = LABEL_W + c * (TILE_W + GAP), fy = tileBg(x, y, TILE_W, TILE_H);
      const lying = opt.pose === POSES.lie, pointing = opt.pose === POSES.point;
      if (pointing) txt('66 天', x + TILE_W - 40, y + 150, { size: 64, weight: 900, color: COL.yellow, align: 'right', glow: 18 });
      drawFigure({ x: x + (pointing ? 130 : lying ? TILE_W / 2 - 10 : TILE_W / 2), y: fy, s: 0.78, style: key, ...opt });
    });
  });
}
