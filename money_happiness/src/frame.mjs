import { CUES } from './cues.mjs';
import { drawBackground, drawDust, drawSubtitles, shakeAt } from './engine/draw.mjs';
import { drawHook, hookShakes } from './scenes/hook.mjs';
import { drawCh1 } from './scenes/ch1.mjs';
import { drawCh2 } from './scenes/ch2.mjs';
import { drawCh3, ch3Shakes } from './scenes/ch3.mjs';
import { drawEnd, END_T } from './scenes/end.mjs';

const SCENES = [
  { start: 0, end: 12.8, draw: drawHook },
  { start: 12.6, end: 38.4, draw: drawCh1 },
  { start: 38.2, end: 63.6, draw: drawCh2 },
  { start: 63.2, end: 106.2, draw: drawCh3 },
  { start: 106.0, end: END_T(), draw: drawEnd },
];

const SHAKES = [...hookShakes(), ...ch3Shakes()];

export const DURATION = END_T();

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
