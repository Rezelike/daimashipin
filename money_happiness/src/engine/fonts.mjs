// 字体放在仓库根目录的 fonts/，全部为 SIL OFL 开源授权，可免费商用：
// 思源宋体 Noto Serif SC、EB Garamond、IBM Plex Mono。
import { GlobalFonts } from '@napi-rs/canvas';

const dir = new URL('../../../fonts/', import.meta.url).pathname;

const FILES = [
  ['NotoSerifSC-Regular.otf', 'SerifSC'],
  ['NotoSerifSC-Medium.otf', 'SerifSC Medium'],
  ['NotoSerifSC-SemiBold.otf', 'SerifSC SemiBold'],
  ['EBGaramond-Italic.ttf', 'Garamond Italic'],
  ['IBMPlexMono-Regular.ttf', 'Plex Mono'],
  ['IBMPlexMono-SemiBold.ttf', 'Plex Mono SemiBold'],
];

for (const [file, name] of FILES) {
  if (!GlobalFonts.registerFromPath(dir + file, name)) {
    throw new Error(`Font failed to load: ${dir + file}`);
  }
}

const withWeight = (family, weight) => (weight ? `${family} ${weight}` : family);

export const FONT = {
  /** Chinese serif (subtitles, titles). weight: '', 'Medium', 'SemiBold' */
  zh: (px, weight = '') => `${px}px "${withWeight('SerifSC', weight)}"`,
  /** English italic serif (subtitle translation line). */
  en: (px) => `${px}px "Garamond Italic"`,
  /** Monospace labels and numbers; Chinese falls back to the serif. weight: '', 'SemiBold' */
  mono: (px, weight = '') => `${px}px "${withWeight('Plex Mono', weight)}", "SerifSC"`,
};
