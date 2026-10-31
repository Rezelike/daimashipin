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
  [0.0, '先做题？', '第 0 帧：他托腮想，记分牌空着'],
  [1.2, '先做题？', '选项一个个亮：他在想'],
  [2.7, '先做题？', '揭晓 1：连错，31% vs 57%'],
  [3.4, '先做题？', '第三声「错」，他垂头'],
  [4.6, '先做题？', '揭晓 2：48 小时后 75% vs 53%'],
  [5.2, '先做题？', '打勾「反超」，他跳起来'],
  [6.4, '先做题？', '「57% → 53%」+ 来源'],
  [8.6, '先猜再读', '答案；题卡到他手里'],
  [10.6, '先猜再读', '走向大书页，弹出 ① ②'],
  [13.0, '先猜再读', '证据卡：问到的 g = 0.54'],
  [15.8, '① 挑哪些题', '第 1 关：题库'],
  [17.4, '① 挑哪些题', '抽出第 1 张'],
  [20.9, '① 挑哪些题', '5 张抽好，其余放回'],
  [22.8, '① 挑哪些题', '问到的：记得更牢'],
  [25.4, '① 挑哪些题', '没问到的：不会多记住'],
  [31.2, '② 怎么猜', '例题：番茄汁是什么颜色？'],
  [32.6, '② 怎么猜', '写下「红色？」→ 错'],
  [33.4, '② 怎么猜', '耸肩：猜错没关系'],
  [35.6, '② 怎么猜', '其余几道接着猜'],
  [40.8, '② 怎么猜', '一周后：55% vs 45%'],
  [46.8, '③ 怎么读', '拿荧光笔沿着书页读'],
  [49.2, '③ 怎么读', '转身，圈出「黑色」'],
  [50.9, '③ 怎么读', '划掉「红色？」写上「黑色」'],
  [54.0, '③ 怎么读', '找到答案的题 84% vs 54%'],
  [61.4, '照着做', '第 1 块翻开：挑 5 道'],
  [65.0, '照着做', '三块都翻开'],
  [67.2, '照着做', '粉色提醒 + 仅供参考'],
  [69.0, '照着做', '通关：大屏闪一下'],
  [71.0, '照着做', '指着大屏'],
  [73.6, '照着做', '跳起来（最后一屏）'],
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
    const cols = 5, tw = 640, th = 360, cap = 58, gap = 16;
    const rows = Math.ceil(LIST.length / cols);
    const W = cols * tw + (cols + 1) * gap, H = 92 + rows * (th + cap + gap) + gap;
    const tiles = LIST.map(([t, sec, what], i) => `
      <div class="tile" style="left:${gap + (i % cols) * (tw + gap)}px;top:${92 + Math.floor(i / cols) * (th + cap + gap)}px">
        <img src="${shots[i]}"><div class="cap"><b>图 ${i + 1}</b> · ${t.toFixed(1)} s · ${sec}<span>${what}</span></div></div>`).join('');
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
    </style></head><body><h1>先看书还是先做题？ · 分镜预览<small>128 BPM · 75 s · 图号 / 秒数 / 段落 / 这一帧在演什么</small></h1>${tiles}</body></html>`;
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
