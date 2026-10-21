export const W = 1920;
export const H = 1080;

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;

export const ease = {
  linear: (t) => t,
  inQuad: (t) => t * t,
  outQuad: (t) => 1 - (1 - t) * (1 - t),
  inCubic: (t) => t * t * t,
  outCubic: (t) => 1 - Math.pow(1 - t, 3),
  inOutCubic: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  outQuart: (t) => 1 - Math.pow(1 - t, 4),
  outExpo: (t) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  inOutSine: (t) => -(Math.cos(Math.PI * t) - 1) / 2,
  outBack: (t, s = 1.70158) => 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2),
};

/** Eased 0→1 progress of t inside [t0, t0 + dur]. */
export const prog = (t, t0, dur, e = ease.outCubic) => e(clamp((t - t0) / dur));

/** Envelope: fades in over `fi` after a, holds, fades out over `fo` before b. */
export function env(t, a, b, fi = 0.25, fo = 0.25) {
  if (t < a || t > b) return 0;
  const i = fi > 0 ? clamp((t - a) / fi) : 1;
  const o = fo > 0 ? clamp((b - t) / fo) : 1;
  return ease.inOutSine(Math.min(i, o));
}

/** Deterministic PRNG so every render is identical. */
export function mulberry32(seed) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function gauss(rng) {
  let u = 0;
  let v = 0;
  while (u === 0) u = rng();
  while (v === 0) v = rng();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

/** Smooth minimum, used for curves that bend into a plateau. */
export const smin = (a, b, k) => (a + b - Math.sqrt((a - b) * (a - b) + k * k)) / 2;

export const fmtInt = (n) =>
  Math.round(n)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ',');
