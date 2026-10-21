// 节拍表：字幕文本与时间（秒）。画面动画都对齐这里的时间点，改节奏只改这里。
// 没有旁白，字幕就是叙事本身；每条 2–3 秒，保持紧凑。
export const CUES = [
  // ---------- 片头 ----------
  { id: 'h1', t0: 0.0, t1: 2.6 }, // 大标题，无字幕
  { id: 'h2', t0: 2.6, t1: 5.4, zh: '2010 年，两位诺奖得主给出了答案：', en: 'In 2010, two Nobel laureates gave an answer:' },
  { id: 'h3', t0: 5.4, t1: 8.4, zh: '家庭年收入过了这条线，快乐就不再增加。', en: 'Beyond this income, happiness stopped rising.' },
  // 2010-09 → 2021-01，相隔 10 年 4 个月，所以说"十年"，不说"11 年"。
  { id: 'h4', t0: 8.4, t1: 10.6, zh: '十年后，它被推翻了。', en: 'A decade later, it was overturned.' },
  { id: 'h5', t0: 10.6, t1: 12.4, zh: '到底谁对？', en: 'So who was right?' },

  // ---------- 研究 01 · Kahneman & Deaton 2010 ----------
  // 原文："more than 450,000 responses to the Gallup-Healthways Well-Being Index"
  { id: 'c1a', t0: 12.8, t1: 15.8, zh: '他们分析了超过 45 万份美国人的问卷。', en: 'They analyzed over 450,000 survey responses from Americans.' },
  { id: 'c1b', t0: 15.8, t1: 18.0, zh: '问卷里有两个问题：', en: 'Two questions mattered:' },
  { id: 'c1c', t0: 18.0, t1: 20.6, zh: '① 给你的人生打个分（0–10）', en: '① Rate your life, from 0 to 10.' },
  // 盖洛普原题："Did you experience the following feelings during a lot of the day yesterday?"（是/否）
  { id: 'c1d', t0: 20.6, t1: 23.4, zh: '② 昨天很多时候，你开心吗？', en: '② Were you happy during a lot of the day yesterday?' },
  { id: 'c1e', t0: 23.4, t1: 26.2, zh: '收入越高，给人生打的分越高。', en: 'The higher the income, the higher the life rating.' },
  { id: 'c1f', t0: 26.2, t1: 28.8, zh: '“昨天开心吗”也跟着涨——', en: '“Happy yesterday?” rose too—' },
  { id: 'c1g', t0: 28.8, t1: 31.6, zh: '但过了 7.5 万美元，就平了。', en: 'but past $75,000, it flattened.' },
  // 原文结论："high income buys life satisfaction but not happiness"
  { id: 'c1h', t0: 31.6, t1: 34.6, zh: '结论：高收入买得到满意，买不到快乐。', en: 'Verdict: high income buys satisfaction, not happiness.' },
  { id: 'c1i', t0: 34.6, t1: 37.2, zh: '这个数字，一火就是十年。', en: 'That number reigned for a decade.' },
];

export function cue(id) {
  const c = CUES.find((x) => x.id === id);
  if (!c) throw new Error(`Unknown cue: ${id}`);
  return c;
}
