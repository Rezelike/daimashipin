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
  [0.0, '分小叠？', '第 0 帧：洗牌 + 两种摆法'],
  [1.2, '分小叠？', '牌在两手之间飞'],
  [2.4, '分小叠？', '揭晓 1：估计 66% > 51%'],
  [3.4, '分小叠？', '他把手伸向小叠'],
  [4.3, '分小叠？', '揭晓 2：考试 65% vs 34%'],
  [5.9, '分小叠？', '✓ 赢了 · 70 人里 63 人'],
  [7.0, '分小叠？', '来源：Kornell 2009 实验 3'],
  [8.4, '一大叠', '答案；四小叠滑过来'],
  [9.2, '一大叠', '四小叠合成一叠'],
  [10.0, '一大叠', '变成一大叠，洗一遍'],
  [12.2, '一大叠', '发出 ① ② ③'],
  [13.6, '一大叠', '小卡：72% 觉得小叠好'],
  [16.4, '① 怎么叠', '发第一张（黄 = 同一张）'],
  [19.0, '① 怎么叠', '一张张发满一排'],
  [22.0, '① 怎么叠', '同一张隔 19 张才回来'],
  [23.6, '① 怎么叠', '四小叠：隔 4 张就回来'],
  [25.8, '① 怎么叠', '49% vs 36%，遍数时间一样'],
  [31.4, '② 怎么排', '第 1 天：大叠 1 遍，小叠 ×8'],
  [35.2, '② 怎么排', '第 3 天：换小叠 3'],
  [40.0, '② 怎么排', '第 5 天考：54% vs 21%'],
  [41.6, '② 怎么排', '考前一天背的那叠 34%'],
  [46.4, '③ 怎么翻', '抽一张：effulgent'],
  [47.2, '③ 怎么翻', '先说出答案：brilliant!'],
  [48.0, '③ 怎么翻', '翻过来，对了 ✓'],
  [49.2, '③ 怎么翻', '答对了也放回叠底'],
  [55.4, '③ 怎么翻', '抽走 21% vs 放回 44%'],
  [61.4, '照着做', '一大叠（把牌码齐）'],
  [63.2, '照着做', '分几天（洗一遍）'],
  [65.8, '照着做', '说出答案再翻（✓）'],
  [67.8, '照着做', '粉色提醒 + 仅供参考'],
  [71.2, '照着做', '摊成扇形，举起来指着'],
  [74.6, '照着做', '最后一屏，75 s 直接结束'],
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
    </style></head><body><h1>单词卡分小叠背更好？ · 分镜预览<small>128 BPM · 75 s · 图号 / 秒数 / 段落 / 这一帧在演什么</small></h1>${tiles}</body></html>`;
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
