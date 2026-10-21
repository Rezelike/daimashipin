// 用法（在 money_happiness/ 目录下运行）：
//   视频：node src/render.mjs --fps 60 --out ../out/money_happiness_sample.mp4   （可选 --from / --to 秒，--crf 画质）
//   单帧：node src/render.mjs --still 6.5 --out build/still.png
//   拼图：node src/render.mjs --sheet 1,4,6.5,9 --out build/sheet.png
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { createCanvas } from '@napi-rs/canvas';
import ffmpegPath from 'ffmpeg-static';
import { W, H } from './engine/util.mjs';
import { FONT } from './engine/fonts.mjs';
import { drawFrame, DURATION } from './frame.mjs';

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) out[argv[i].slice(2)] = argv[i + 1];
  }
  return out;
}

const args = parseArgs(process.argv.slice(2));
if (!args.out) throw new Error('--out is required');
fs.mkdirSync(path.dirname(args.out), { recursive: true });

const canvas = createCanvas(W, H);
const ctx = canvas.getContext('2d');

async function renderStill(t) {
  drawFrame(ctx, t, Math.round(t * 60));
  fs.writeFileSync(args.out, await canvas.encode('png'));
  console.log(`wrote ${args.out} @ ${t}s`);
}

async function renderSheet(times) {
  const cols = 3;
  const tw = 640;
  const th = 360;
  const lab = 34;
  const rows = Math.ceil(times.length / cols);
  const sheet = createCanvas(cols * tw, rows * (th + lab));
  const s = sheet.getContext('2d');
  s.imageSmoothingEnabled = true;
  s.imageSmoothingQuality = 'high';
  s.fillStyle = '#000';
  s.fillRect(0, 0, sheet.width, sheet.height);
  times.forEach((t, i) => {
    drawFrame(ctx, t, Math.round(t * 60));
    const x = (i % cols) * tw;
    const y = Math.floor(i / cols) * (th + lab);
    s.drawImage(canvas, 0, 0, W, H, x, y + lab, tw, th);
    s.fillStyle = '#9fb3d1';
    s.font = FONT.mono(18);
    s.textBaseline = 'middle';
    s.fillText(`${t.toFixed(2)}s`, x + 10, y + lab / 2);
  });
  fs.writeFileSync(args.out, await sheet.encode('png'));
  console.log(`wrote ${args.out} (${times.length} frames)`);
}

async function renderVideo() {
  const fps = Number(args.fps ?? 60);
  const from = Number(args.from ?? 0);
  const to = Number(args.to ?? DURATION);
  const frames = Math.round((to - from) * fps);
  const ff = spawn(
    ffmpegPath,
    [
      '-y',
      '-f', 'rawvideo',
      '-pix_fmt', 'rgba',
      '-s', `${W}x${H}`,
      '-r', String(fps),
      '-i', '-',
      '-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p',
      '-c:v', 'libx264',
      '-preset', 'slow',
      '-crf', String(args.crf ?? 16),
      '-x264-params', 'aq-mode=3',
      '-colorspace', 'bt709',
      '-color_primaries', 'bt709',
      '-color_trc', 'bt709',
      '-color_range', 'tv',
      '-movflags', '+faststart',
      args.out,
    ],
    { stdio: ['pipe', 'ignore', 'pipe'] },
  );
  let log = '';
  ff.stderr.on('data', (d) => {
    log = (log + d).slice(-4000);
  });
  const done = new Promise((resolve, reject) => {
    ff.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}\n${log}`))));
  });

  const started = Date.now();
  for (let i = 0; i < frames; i++) {
    drawFrame(ctx, from + i / fps, i);
    const buf = Buffer.from(canvas.data());
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if (i % (fps * 5) === 0) {
      const sec = ((Date.now() - started) / 1000).toFixed(1);
      console.log(`frame ${i}/${frames} (${(from + i / fps).toFixed(1)}s) elapsed ${sec}s`);
    }
  }
  ff.stdin.end();
  await done;
  console.log(`wrote ${args.out}: ${frames} frames @ ${fps}fps in ${((Date.now() - started) / 1000).toFixed(1)}s`);
}

if (args.still !== undefined) await renderStill(Number(args.still));
else if (args.sheet) await renderSheet(args.sheet.split(',').map(Number));
else await renderVideo();
