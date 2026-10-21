import { CUES } from './cues.mjs';
import { drawBackground, drawDust, drawSubtitles, shakeAt } from './engine/draw.mjs';
import { drawHook, hookShakes } from './scenes/hook.mjs';
import { drawCh1 } from './scenes/ch1.mjs';

const SCENES = [
  { start: 0, end: 12.8, draw: drawHook },
  { start: 12.6, end: 38.4, draw: drawCh1 },
];

const SHAKES = [...hookShakes()];

export const DURATION = 38.4;

export function drawFrame(ctx, t, frameIndex) {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
  ctx.filter = 'none';
  ctx.shadowBlur = 0;
  ctx.setLineDash([]);
  ctx.letterSpacing = '0px';

  drawBackground(ctx, t);
  drawDust(ctx, t);

  ctx.save();
  const s = shakeAt(t, SHAKES);
  ctx.translate(s.x, s.y);
  for (const sc of SCENES) if (t >= sc.start && t < sc.end) sc.draw(ctx, t);
  ctx.restore();

  drawSubtitles(ctx, t, CUES);
}
