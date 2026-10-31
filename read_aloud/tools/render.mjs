// Render frames of src/scene.html with headless Chromium.
//   node tools/render.mjs --stills 0,2.2,3.2      -> build/stills/t_<sec>.png
//   node tools/render.mjs --all [--workers 7]      -> build/frames/f_00000.png ... (30 fps, 75 s)
//   node tools/render.mjs --covers                 -> out/封面参考_横竖通用.png (fallback cover, 1920x1440)
// playwright-core and Chromium are found automatically (local node_modules, global npm, Kiro sandbox).
// Override with PW_CORE=<playwright-core dir> and CHROME_EXE=<chrome or chrome-headless-shell>.
import { createRequire } from 'module';
import { execSync } from 'child_process';
import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);

function loadPlaywright() {
  const candidates = [process.env.PW_CORE, 'playwright-core', 'playwright'];
  try {
    const g = execSync('npm root -g', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    candidates.push(path.join(g, 'playwright-core'), path.join(g, 'playwright'),
      path.join(g, '@playwright/mcp/node_modules/playwright-core'));
  } catch {}
  let lastErr;
  for (const c of candidates.filter(Boolean)) {
    try { return require(c); } catch (e) { lastErr = e; }
  }
  throw new Error(`playwright-core not found (run \`npm i playwright-core\` here, or set PW_CORE): ${lastErr?.message}`);
}

function findChrome() {
  if (process.env.CHROME_EXE) return process.env.CHROME_EXE;
  const roots = [process.env.PLAYWRIGHT_BROWSERS_PATH, '/inner_container/opt/playwright',
    path.join(os.homedir(), '.cache/ms-playwright')].filter(Boolean);
  for (const r of roots) {
    let dirs;
    try { dirs = fs.readdirSync(r); } catch { continue; }
    for (const d of dirs.filter((x) => x.startsWith('chromium_headless_shell-')).sort().reverse()) {
      const exe = path.join(r, d, 'chrome-headless-shell-linux64', 'chrome-headless-shell');
      if (fs.existsSync(exe)) return exe;
    }
  }
  return undefined; // let Playwright use its own installed browser
}

const { chromium } = loadPlaywright();
const EXE = findChrome();

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SCENE = 'file://' + path.join(ROOT, 'src/scene.html');
const FPS = 30, DURATION = 75;

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
  page.on('console', (m) => { if (m.type() === 'error') console.error('console:', m.text()); });
  await page.goto(SCENE);
  const n = await page.evaluate(() => window.fontsReady);
  if (n < 4) throw new Error('fonts not loaded: ' + n);
  return page;
}
async function grab(page, t) {
  const url = await page.evaluate((tt) => window.grab(tt), t);
  return Buffer.from(url.split(',')[1], 'base64');
}

const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox', '--disable-gpu', '--font-render-hinting=none'] });
try {
  if (args.includes('--stills')) {
    const times = opt('--stills', '0').split(',').map(Number);
    const out = path.join(ROOT, 'build/stills');
    fs.mkdirSync(out, { recursive: true });
    const page = await openPage(browser);
    for (const t of times) {
      const buf = await grab(page, t);
      const f = path.join(out, `t_${t.toFixed(2).padStart(6, '0')}.png`);
      fs.writeFileSync(f, buf);
      console.log('wrote', f);
    }
  } else if (args.includes('--covers')) {
    // code-drawn fallback cover, ONE picture for both crops (Douyin keeps a single cover image) -> out/封面参考_横竖通用.png
    const page = await browser.newPage({ viewport: { width: 1920, height: 1440 }, deviceScaleFactor: 1 });
    page.on('pageerror', (e) => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
    await page.goto('file://' + path.join(ROOT, 'src/cover.html'));
    const n = await page.evaluate(() => window.fontsReady);
    if (n < 4) throw new Error('fonts not loaded: ' + n);
    fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });
    const chk = await page.evaluate(() => window.coverCheck());
    const url = await page.evaluate(() => window.cover());
    const f = path.join(ROOT, 'out', '封面参考_横竖通用.png');
    fs.writeFileSync(f, Buffer.from(url.split(',')[1], 'base64'));
    const ok = chk.bottomLeftPixels === 0 && Math.min(...chk.margins34) >= 40;
    console.log(`wrote ${f} ${chk.size.join('x')}  竖封面 crop margins L/T/R/B ${chk.margins34.join('/')}  bottom-left pixels ${chk.bottomLeftPixels}  ${ok ? 'OK' : 'CHECK'}`);
    if (!ok) process.exitCode = 1;
  } else if (args.includes('--lint')) {
    // text lint, every 0.25 s: text outside the frame, two texts on top of each other, text below 34 px (info)
    const page = await openPage(browser);
    const off = new Map(), overlap = new Map(), small = new Map();
    const step = Number(opt('--step', '0.25'));
    const [r0, r1] = opt('--range', `0,${DURATION}`).split(',').map(Number);
    for (let t = r0; t < r1; t += step) {
      const boxes = (await page.evaluate((tt) => window.lintFrame(tt), t)).filter((b) => b.s.trim() && b.s !== '_');
      for (const b of boxes) {
        if (b.x0 < 12 || b.x1 > 1908 || b.y0 < 4 || b.y1 > 1076) if (!off.has(b.s)) off.set(b.s, `${t.toFixed(2)} s  x ${b.x0.toFixed(0)}–${b.x1.toFixed(0)} y ${b.y0.toFixed(0)}–${b.y1.toFixed(0)}`);
        if (b.px < 33.5 && b.a > 0.5) { const k = `${Math.round(b.px)} px  ${b.s}`; if (!small.has(k)) small.set(k, t.toFixed(2)); }
      }
      const vis = boxes.filter((b) => b.a > 0.6);
      for (let i = 0; i < vis.length; i++) for (let j = i + 1; j < vis.length; j++) {
        const a = vis[i], b = vis[j];
        const iw = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0), ih = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
        const hmin = Math.min(a.y1 - a.y0, b.y1 - b.y0);
        if (iw > 8 && ih > 0.5 * hmin && !(a.s === b.s && Math.abs(a.x0 - b.x0) < 2 && Math.abs(a.y0 - b.y0) < 2)) {
          const k = `${a.s}  <->  ${b.s}`;
          if (!overlap.has(k)) overlap.set(k, t.toFixed(2));
        }
      }
    }
    console.log(`lint: ${Math.ceil((r1 - r0) / step)} frames (${r0}-${r1} s)`);
    console.log(`off-screen: ${off.size}`); for (const [s, w] of off) console.log(`  ${w}  ${s}`);
    console.log(`overlapping: ${overlap.size}`); for (const [k, t] of overlap) console.log(`  ${t} s  ${k}`);
    console.log(`below 34 px (info): ${small.size}`); for (const [k, t] of small) console.log(`  ${t} s  ${k}`);
    if (off.size || overlap.size) process.exitCode = 1;
  } else if (args.includes('--all')) {
    const workers = Number(opt('--workers', '7'));
    const start = Number(opt('--from', '0')), end = Number(opt('--to', String(DURATION * FPS)));
    const out = path.join(ROOT, 'build/frames');
    fs.mkdirSync(out, { recursive: true });
    const noKid = [];
    let next = start, done = 0;
    const t0 = Date.now();
    const work = async () => {
      const page = await openPage(browser);
      while (true) {
        const i = next++;
        if (i >= end) break;
        const t = i / FPS;
        const url = await page.evaluate((tt) => { const d = window.grab(tt); return [d, window.__frameInfo]; }, t);
        fs.writeFileSync(path.join(out, `f_${String(i).padStart(5, '0')}.png`), Buffer.from(url[0].split(',')[1], 'base64'));
        if (!url[1].hero) noKid.push(i);
        done++;
        if (done % 150 === 0) console.log(`${done}/${end - start} frames, ${((Date.now() - t0) / 1000).toFixed(1)} s`);
      }
      await page.close();
    };
    await Promise.all(Array.from({ length: workers }, work));
    fs.writeFileSync(path.join(ROOT, 'build/frame_check.json'), JSON.stringify({ framesWithoutHero: noKid }, null, 1));
    console.log(`done ${done} frames in ${((Date.now() - t0) / 1000).toFixed(1)} s; frames without the figure: ${noKid.length}`);
  }
} finally {
  await browser.close();
}
