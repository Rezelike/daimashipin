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
  [0.0, '开场', '第 0 帧：各 16 张空白单词卡'],
  [1.6, '开场', '边背边一排排翻亮'],
  [2.3, '开场', '揭晓 1：16 张全亮＝都背到全对'],
  [3.4, '开场', '男孩关灯躺下'],
  [4.6, '开场', '揭晓 2：卡翻回「？」7.5 vs 10'],
  [5.9, '开场', '打勾：记得多 / 忘了一半'],
  [8.9, '睡前背', '早上醒来，坐在床上'],
  [10.4, '睡前背', '伸懒腰，弹出 ① ②'],
  [13.4, '睡前背', '两排圆点：3 轮 vs 6 轮'],
  [16.6, '① 睡前背什么', '晚上 9 点，台灯亮着'],
  [18.2, '① 睡前背什么', '大卡片：nyanya'],
  [19.2, '① 睡前背什么', '默错「西瓜？」，放回去'],
  [20.9, '① 睡前背什么', '番茄 ✓，放进「全对」'],
  [23.2, '① 睡前背什么', '16/16 全对，叮'],
  [25.0, '① 睡前背什么', '关灯躺下'],
  [31.2, '② 背完多久睡', '标题填空 + 三条时间条'],
  [33.4, '② 背完多久睡', '几小时内：忘得少 ✓'],
  [37.2, '② 背完多久睡', '熬通宵：补不回来 ✗'],
  [41.7, '② 背完多久睡', '14 小时 ✗ + 填空'],
  [45.8, '③ 醒来干嘛', '天亮，窗外鸟叫'],
  [48.7, '③ 醒来干嘛', '第 1 轮：10/16'],
  [50.7, '③ 醒来干嘛', '第 3 轮：全对'],
  [52.6, '③ 醒来干嘛', '窗外日夜转 7 次'],
  [56.7, '③ 醒来干嘛', '一周后：15 个 vs 11 个'],
  [61.6, '照着做', '晚上：男孩翻卡背'],
  [63.6, '照着做', '夜里：男孩躺下'],
  [65.7, '照着做', '早上：醒来默'],
  [67.4, '照着做', '粉色提醒，男孩摇头'],
  [70.9, '照着做', '指着时间表'],
  [73.5, '照着做', '竖大拇指（最后一屏）'],
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
    </style></head><body><h1>背单词：早上还是睡前？ · 分镜预览<small>128 BPM · 75 s · 图号 / 秒数 / 段落 / 这一帧在演什么</small></h1>${tiles}</body></html>`;
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
