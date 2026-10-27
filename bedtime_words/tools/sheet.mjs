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
  [0.0, '开场', '第 0 帧：两人都在背'],
  [1.6, '开场', '早上背 / 睡前背'],
  [2.6, '开场', '揭晓 1：都背到全对'],
  [3.4, '开场', '男孩背完就上床'],
  [4.5, '开场', '揭晓 2：12 小时后再考'],
  [5.7, '开场', '打勾：记得多 / 忘了一半'],
  [8.9, '睡前背', '早上醒来，被子滑下'],
  [10.4, '睡前背', '伸懒腰，弹出 ① ②'],
  [12.7, '睡前背', '卡片：3 轮 vs 6 轮'],
  [16.2, '① 睡前背什么', '标题 + 主句'],
  [19.0, '① 睡前背什么', '边背边默，进度涨'],
  [21.4, '① 睡前背什么', '例子 nyanya → 番茄'],
  [22.9, '① 睡前背什么', '16 个全对，叮'],
  [24.6, '① 睡前背什么', '合上书，上床'],
  [31.2, '② 背完多久睡', '挂钟变计时环'],
  [33.4, '② 背完多久睡', '几小时内：忘得少'],
  [37.2, '② 背完多久睡', '熬通宵：补不回来'],
  [41.7, '② 背完多久睡', '14 小时 + 填空'],
  [46.2, '③ 醒来干嘛', '床头闹钟响'],
  [47.6, '③ 醒来干嘛', '掀被子醒来'],
  [49.0, '③ 醒来干嘛', '第 1 轮 10/16'],
  [50.6, '③ 醒来干嘛', '第 3 轮 全对'],
  [52.6, '③ 醒来干嘛', '日历翻 7 天'],
  [56.2, '③ 醒来干嘛', '一周后 15 个，还领先'],
  [61.6, '照着做', '第 1 行，男孩翻书背'],
  [63.6, '照着做', '第 2 行，男孩上床'],
  [65.6, '照着做', '第 3 行，醒来默写'],
  [67.0, '照着做', '粉色提醒，男孩摇头'],
  [70.9, '照着做', '指着表'],
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
    const shots = [];
    for (const [t] of FRAMES) {
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
    const rows = Math.ceil(FRAMES.length / cols);
    const W = cols * tw + (cols + 1) * gap, H = 92 + rows * (th + cap + gap) + gap;
    const tiles = FRAMES.map(([t, sec, what], i) => `
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
    fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });
    const out = path.join(ROOT, 'out', '分镜预览.png');
    await p2.screenshot({ path: out, fullPage: true });
    console.log(`wrote ${out} ${W}x${H}, ${FRAMES.length} tiles`);
  } finally {
    await browser.close();
  }
}
