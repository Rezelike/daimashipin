// Storyboard preview: key frames with their section and time written under each tile -> out/分镜预览.png
//   node tools/sheet.mjs
// Every tile is numbered, so feedback can point at "图 7" instead of searching the video.
import { createRequire } from 'module';
import { execSync } from 'child_process';
import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
function loadPlaywright() {
  const c = [process.env.PW_CORE, 'playwright-core', 'playwright'];
  try {
    const g = execSync('npm root -g', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    c.push(path.join(g, 'playwright-core'), path.join(g, 'playwright'), path.join(g, '@playwright/mcp/node_modules/playwright-core'));
  } catch {}
  for (const x of c.filter(Boolean)) { try { return require(x); } catch {} }
  throw new Error('playwright-core not found (npm i playwright-core, or set PW_CORE)');
}
function findChrome() {
  if (process.env.CHROME_EXE) return process.env.CHROME_EXE;
  for (const r of [process.env.PLAYWRIGHT_BROWSERS_PATH, '/inner_container/opt/playwright', path.join(os.homedir(), '.cache/ms-playwright')].filter(Boolean)) {
    let dirs; try { dirs = fs.readdirSync(r); } catch { continue; }
    for (const d of dirs.filter((x) => x.startsWith('chromium_headless_shell-')).sort().reverse()) {
      const exe = path.join(r, d, 'chrome-headless-shell-linux64', 'chrome-headless-shell');
      if (fs.existsSync(exe)) return exe;
    }
  }
  return undefined;
}

// [seconds, section, what happens]
export const FRAMES = [
  [0.0, '要念吗？', '第 0 帧：边走边念，念出声的词变成实心块'],
  [1.2, '要念吗？', '念出声 → 实心块；默读 → 虚线框'],
  [2.4, '要念吗？', '揭晓 1：认得出 默读 60%，念出声 76%'],
  [3.4, '要念吗？', '转身，下一张表几乎全念出声'],
  [4.4, '要念吗？', '揭晓 2：63% vs 65%，差别没了'],
  [6.4, '要念吗？', '✓ 挑着念 · 全念：差不多 · 来源'],
  [8.4, '挑着念', '第二行翻成答案，他举起一页纸'],
  [11.0, '挑着念', '① ② ③ 从纸上弹出来'],
  [13.4, '挑着念', '小卡：自己念 77% … 默读 65%'],
  [15.6, '① 念哪些', '复习笔记，他托着下巴默读'],
  [17.4, '① 念哪些', '虚线框一行行往下：默读一遍'],
  [20.6, '① 念哪些', '光笔圈出「定义」'],
  [22.6, '① 念哪些', '圈出「公式」'],
  [25.0, '① 念哪些', '圈出「单词」，其余几行变暗'],
  [26.4, '① 念哪些', '挑重点念是作者的建议，没单独测过'],
  [31.6, '② 怎么念', '一字一字念出声：块最亮'],
  [34.6, '② 怎么念', '小声念：块暗一些'],
  [37.4, '② 怎么念', '只动嘴：更暗'],
  [40.2, '② 怎么念', '默读：只有虚线框'],
  [42.2, '② 怎么念', '66% > 57% > 43%，正常出声最好'],
  [47.6, '③ 念了有什么用', '念出的块堆进「记住原话」'],
  [49.6, '③ 念了有什么用', '块从「读懂意思」上弹开'],
  [51.4, '③ 念了有什么用', '记忆题 81% vs 74% ✓，理解题差不多'],
  [54.6, '③ 念了有什么用', '要读懂：另想办法'],
  [61.4, '照着做', '默读一遍（他演）'],
  [63.4, '照着做', '圈出要背的（光笔）'],
  [65.4, '照着做', '念出声（实心块）'],
  [67.6, '照着做', '粉色提醒 + 仅供参考'],
  [70.6, '照着做', '指着这一屏'],
  [72.2, '照着做', '跳起来（最后一屏，75 s 直接结束）'],
];

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const FONTS = path.resolve(ROOT, '../sleep_or_cram/assets/fonts');
if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ executablePath: findChrome(), args: ['--no-sandbox', '--disable-gpu', '--font-render-hinting=none'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    page.on('pageerror', (e) => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
    await page.goto('file://' + path.join(ROOT, 'src/scene.html'));
    await page.evaluate(() => window.fontsReady);
    // --mp4 <file>: take the tiles from the encoded video (what viewers see) instead of the live page
    const mi = process.argv.indexOf('--mp4');
    const mp4 = mi > 0 ? path.resolve(process.argv[mi + 1]) : null;
    const ffmpeg = process.env.FFMPEG || (() => {
      try { return execSync(`${path.join(ROOT, '.venv/bin/python')} -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`, { encoding: 'utf8' }).trim(); } catch { return 'ffmpeg'; }
    })();
    // --times a,b,c [--out file]: a quick sheet of just these moments (default output build/quick.png)
    const ti = process.argv.indexOf('--times');
    const LIST = ti > 0 ? process.argv[ti + 1].split(',').map((x) => [Number(x), '', '']) : FRAMES;
    const xi = process.argv.indexOf('--extra');
    const extra = xi > 0 ? { file: path.resolve(process.argv[xi + 1]), label: process.argv[xi + 2] || '' } : null;
    const oi = process.argv.indexOf('--out');
    const OUT = oi > 0 ? path.resolve(process.argv[oi + 1]) : ti > 0 ? path.join(ROOT, 'build', 'quick.png') : path.join(ROOT, 'out', '分镜预览.png');
    const shots = [];
    for (const [t] of LIST) {
      if (mp4) {
        const jpg = execSync(`"${ffmpeg}" -v error -ss ${t.toFixed(3)} -i "${mp4}" -frames:v 1 -vf scale=640:360 -q:v 3 -f image2pipe -vcodec mjpeg -`);
        shots.push('data:image/jpeg;base64,' + jpg.toString('base64'));
        continue;
      }
      shots.push(await page.evaluate((tt) => {
        window.draw(tt);
        const c = document.createElement('canvas'); c.width = 640; c.height = 360;
        c.getContext('2d').drawImage(document.getElementById('c'), 0, 0, 640, 360);
        return c.toDataURL('image/jpeg', 0.9);
      }, t));
    }
    if (extra) {
      const b64 = fs.readFileSync(extra.file).toString('base64');
      shots.push(await page.evaluate(async (src) => {
        const im = new Image(); im.src = src; await im.decode();
        const c = document.createElement('canvas'); c.width = 640; c.height = 360;
        const g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, 640, 360);
        const k = Math.min(640 / im.width, 360 / im.height), w = im.width * k, h = im.height * k;
        g.drawImage(im, (640 - w) / 2, (360 - h) / 2, w, h);
        g.strokeStyle = 'rgba(247,185,62,0.9)'; g.lineWidth = 2; const cw = h * 0.75; g.strokeRect((640 - cw) / 2, 0, cw, h);
        return c.toDataURL('image/jpeg', 0.9);
      }, 'data:image/png;base64,' + b64));
      LIST.push([0, '附加', extra.label]);
    }
    const cols = 5, tw = 640, th = 360, cap = 58, gap = 16;
    const rows = Math.ceil(LIST.length / cols);
    const W = cols * tw + (cols + 1) * gap, H = 92 + rows * (th + cap + gap) + gap;
    const tiles = LIST.map(([t, sec, what], i) => `
      <div class="tile" style="left:${gap + (i % cols) * (tw + gap)}px;top:${92 + Math.floor(i / cols) * (th + cap + gap)}px">
        <img src="${shots[i]}"><div class="cap"><b>图 ${i + 1}</b> · ${sec === '附加' ? '' : t.toFixed(1) + ' s · '}${sec}<span>${what}</span></div></div>`).join('');
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>
      @font-face { font-family: S; src: url('file://${FONTS}/NotoSansCJKsc-Bold.otf'); font-weight: 700; }
      @font-face { font-family: S; src: url('file://${FONTS}/NotoSansCJKsc-Black.otf'); font-weight: 900; }
      body { margin: 0; width: ${W}px; height: ${H}px; background: #05070d; font-family: S; color: #f3eee3; position: relative; }
      h1 { position: absolute; left: ${gap}px; top: 18px; margin: 0; font-size: 40px; font-weight: 900; }
      h1 small { font-size: 26px; color: #8d99b5; font-weight: 700; margin-left: 18px; }
      .tile { position: absolute; width: ${tw}px; }
      .tile img { display: block; width: ${tw}px; height: ${th}px; }
      .cap { height: ${cap}px; font-size: 25px; font-weight: 700; line-height: ${cap}px; white-space: nowrap; overflow: hidden; color: #b5bfd6; }
      .cap b { color: #f7b93e; font-weight: 900; }
      .cap span { color: #f3eee3; margin-left: 12px; }
    </style></head><body><h1>背书要读出声吗？ · 分镜预览<small>128 BPM · 75 s · 图号 / 秒数 / 段落 / 这一帧在演什么</small></h1>${tiles}</body></html>`;
    const sheetPath = path.join(ROOT, 'build/sheet.html');
    fs.mkdirSync(path.dirname(sheetPath), { recursive: true });
    fs.writeFileSync(sheetPath, html);
    const p2 = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
    await p2.goto('file://' + sheetPath);
    await p2.evaluate(() => document.fonts.ready);
    fs.mkdirSync(path.dirname(OUT), { recursive: true });
    await p2.screenshot({ path: OUT, fullPage: true });
    console.log(`wrote ${OUT} ${W}x${H}, ${LIST.length} tiles`);
  } finally {
    await browser.close();
  }
}
