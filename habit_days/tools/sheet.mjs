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
  [0.0, '21 天？', '第 0 帧：天快亮，他上坡，前面是第 21 天的旗'],
  [1.2, '21 天？', '边走边涨：头顶「不用想就会做」'],
  [2.4, '21 天？', '揭晓 1：第 21 天，还没到顶（约 2/3）'],
  [3.1, '21 天？', '他抬头看，耸耸肩'],
  [4.4, '21 天？', '揭晓 2：镜头拉远，一般要 66 天'],
  [5.6, '21 天？', '最快 18 天 / 最慢 ≈254 天（推算）'],
  [6.6, '21 天？', '来源：Lally 2010，伦敦 82 人'],
  [8.5, '66 天', '答案：不按 21 天，按 2 个多月准备'],
  [10.9, '66 天', '路牌 ① 做什么 ② 怎么坚持，他指着'],
  [13.0, '66 天', '小卡：「21 天」出自 1960 年的整形医生'],
  [16.0, '① 挑一件小事', '走向「早饭」路牌'],
  [17.1, '① 挑一件小事', '拿出小卡「背 10 个单词」'],
  [18.6, '① 挑一件小事', '挂到「早饭」下面'],
  [21.4, '① 挑一件小事', '研究里的例子：午饭、晚饭前'],
  [24.6, '① 挑一件小事', '换成定钟点 7:30 也行'],
  [31.0, '② 天天做', '一步一天，踩过的路一块块亮'],
  [35.4, '② 天天做', '曲线清楚的 39 人：88% 的天做到了'],
  [37.6, '② 天天做', '曲线不清楚的人：60–63%'],
  [40.4, '② 天天做', '相关，不是因果；坡越来越平'],
  [46.4, '③ 漏一天', '前面路上缺了一块'],
  [47.0, '③ 漏一天', '踩空'],
  [48.0, '③ 漏一天', '跪倒；漏一次只掉 0.29 分'],
  [49.6, '③ 漏一天', '站起来；满分 42 里只少一小截'],
  [50.6, '③ 漏一天', '接着走'],
  [53.4, '③ 漏一天', '第二天接着做，照样往上涨'],
  [61.3, '照着做', '坡顶：① 小事 + 固定时机，到顶'],
  [63.4, '照着做', '② 天天做'],
  [65.4, '照着做', '③ 漏了就接上'],
  [68.7, '照着做', '日出照亮路牌'],
  [72.6, '照着做', '迎着日出举手（最后一屏）'],
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
    </style></head><body><h1>21 天能养成习惯吗？ · 分镜预览<small>128 BPM · 75 s · 图号 / 秒数 / 段落 / 这一帧在演什么</small></h1>${tiles}</body></html>`;
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
