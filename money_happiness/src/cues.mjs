// 节拍表：字幕文本与时间（秒）。画面动画都对齐这里的时间点，改节奏只改这里。
// 没有旁白，字幕就是叙事本身；每条 2–3 秒，保持紧凑。
export const CUES = [
  // ---------- 片头 ----------
  { id: 'h1', t0: 0.0, t1: 2.6 }, // 大标题，无字幕
  // 不说"两位诺奖得主"：迪顿 2015 年才获奖，2010 年发论文时只有卡尼曼是。获奖年份画面上有标签。
  { id: 'h2', t0: 2.6, t1: 5.4, zh: '2010 年，卡尼曼和迪顿给出了答案：', en: 'In 2010, Kahneman and Deaton gave an answer:' },
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
  // 结论段多给 0.8 秒：先在图上画出差距，再让三个小人把它演一遍。
  { id: 'c1h', t0: 31.6, t1: 35.4, zh: '结论：高收入买得到满意，买不到快乐。', en: 'Verdict: high income buys satisfaction, not happiness.' },
  { id: 'c1i', t0: 35.4, t1: 38.0, zh: '这个数字，一火就是十年。', en: 'That number reigned for a decade.' },

  // ---------- 研究 02 · Killingsworth 2021 ----------
  // Penn 新闻稿：他自己做的 App「Track Your Happiness」，每天随机提醒几次；
  // 题目 "How do you feel right now?"，从 "very bad" 到 "very good"。
  { id: 'c2a', t0: 38.4, t1: 41.2, zh: '2021 年，沃顿商学院的基林斯沃思换了个问法。', en: 'In 2021, Matthew Killingsworth at Wharton asked differently.' },
  { id: 'c2b', t0: 41.2, t1: 43.6, zh: '他做了个 App，每天在随机时刻提醒几次：', en: 'His app pinged people at random moments, a few times a day:' },
  { id: 'c2c', t0: 43.6, t1: 46.2, zh: '“你现在感觉怎么样？”', en: '“How do you feel right now?”' },
  { id: 'c2d', t0: 46.2, t1: 48.6, zh: '不用回想昨天，只问此时此刻；', en: 'Not recalling yesterday, just this moment;' },
  { id: 'c2e', t0: 48.6, t1: 51.4, zh: '也不是二选一，而是从「非常差」到「非常好」。', en: 'not yes/no, but anywhere from “very bad” to “very good.”' },
  // 原文："1,725,994 experience-sampling reports from 33,391 employed US adults"
  { id: 'c2f', t0: 51.4, t1: 54.4, zh: '33,391 名美国上班族，一共打了 1,725,994 次分。', en: '33,391 employed Americans gave 1,725,994 ratings.' },
  { id: 'c2g', t0: 54.4, t1: 57.2, zh: '结果：过了 7.5 万美元，快乐还在涨。', en: 'Result: past $75,000, happiness kept rising.' },
  // 原文："with an equally steep slope above $80,000 as below it"
  { id: 'c2h', t0: 57.2, t1: 59.8, zh: '过了 8 万美元，涨得和之前一样快。', en: 'Above $80,000, it rose just as steeply as below.' },
  // 原文：没有哪个收入点让"此刻感受"和"人生满意度"分道扬镳。
  { id: 'c2i', t0: 59.8, t1: 63.2, zh: '满意和快乐，一起往上涨——没有天花板。', en: 'Satisfaction and happiness rose together. No ceiling.' },
  { id: 'c2j', t0: 63.2, t1: 65.6, zh: '两项研究，结论正好相反。', en: 'Two studies, opposite conclusions.' },

  // ---------- 研究 03 · Killingsworth, Kahneman & Mellers 2023 ----------
  // Penn 新闻稿："an adversarial collaboration … with Barbara Mellers as arbiter"
  { id: 'c3a', t0: 65.6, t1: 68.4, zh: '2023 年，两位作者决定一起查个明白，', en: 'In 2023, the two authors teamed up to settle it,' },
  { id: 'c3b', t0: 68.4, t1: 71.2, zh: '还请来第三位学者梅勒斯当裁判。', en: 'with a third scholar, Barbara Mellers, as arbiter.' },
  { id: 'c3c', t0: 71.2, t1: 73.6, zh: '这叫「对抗式合作」。', en: 'It’s called an adversarial collaboration.' },
  // 论文按"快乐程度"的百分位（15/30/50/70/85）分别看收入的影响。
  { id: 'c3d', t0: 73.6, t1: 76.6, zh: '他们把 2021 年的数据，按快乐程度从低到高分开看：', en: 'They re-split the 2021 data, from least to most happy:' },
  { id: 'c3e', t0: 76.6, t1: 79.4, zh: '大多数人：收入越高，越快乐。', en: 'For most people: more income, more happiness.' },
  // 原文："even accelerates in the happiest group"
  { id: 'c3f', t0: 79.4, t1: 82.2, zh: '最快乐的人：过了 10 万美元，涨得更快。', en: 'The happiest: rising even faster past $100,000.' },
  // 原文："the flattening pattern exists but is restricted to the least happy 20% of the population"
  { id: 'c3g', t0: 82.2, t1: 85.4, zh: '只有最不快乐的约 20%：过了 10 万美元，就平了。', en: 'Only the least happy ~20% level off past $100,000.' },
  // 原文："complementary nonlinearities contribute to the overall linear-log relationship"
  { id: 'c3h', t0: 85.4, t1: 88.6, zh: '一个变平，一个加速——平均下来，正好是一条直线。', en: 'One flattens, one speeds up: the average is a straight line.' },
  { id: 'c3i', t0: 88.6, t1: 91.0, zh: '那 2010 年为什么会看到「天花板」？', en: 'So why did 2010 find a ceiling?' },
  // 原文："Using dichotomous questions about the preceding day"
  { id: 'c3j', t0: 91.0, t1: 93.8, zh: '因为当年的问题，只能答「是」或「否」。', en: 'Because its questions allowed only yes or no.' },
  { id: 'c3k', t0: 93.8, t1: 96.8, zh: '开心、很开心、非常开心——都只能答「是」。', en: 'Happy, happier, happiest: all just “yes.”' },
  // 原文："their measures could not discriminate among degrees of happiness because of a ceiling effect"
  { id: 'c3l', t0: 96.8, t1: 99.6, zh: '量表顶到了头，这叫「天花板效应」。', en: 'The measure maxed out: a ceiling effect.' },
  { id: 'c3m', t0: 99.6, t1: 102.6, zh: '它分得清「不开心」，却分不清有多开心。', en: 'It caught unhappiness, but not degrees of happiness.' },
  // 原文："might have reached the correct conclusion if they had described their results in terms of unhappiness"
  { id: 'c3n', t0: 102.6, t1: 105.8, zh: '用「不快乐」来描述，2010 年的结论可能就对了。', en: 'Framed as unhappiness, 2010 might have been right.' },

  // ---------- 结尾 ----------
  // Killingsworth（Penn 新闻稿）："for most people larger incomes are associated with greater happiness …
  // if you’re rich and miserable, more money won’t help."
  { id: 'e1', t0: 106.2, t1: 108.8, zh: '所以，钱能买到快乐吗？', en: 'So, can money buy happiness?' },
  { id: 'e2', t0: 108.8, t1: 111.8, zh: '对大多数人来说：收入越高，往往越快乐。', en: 'For most people, higher income tends to mean more happiness.' },
  { id: 'e3', t0: 111.8, t1: 115.0, zh: '但如果你有钱却不快乐，再多的钱也帮不上忙。', en: 'But if you’re rich and miserable, more money won’t help.' },
  { id: 'e4', t0: 115.0, t1: 118.0, zh: '13 年，3 篇论文，一个更完整的答案。', en: '13 years, 3 papers, one fuller answer.' },
  { id: 'e5', t0: 118.0, t1: 123.0 }, // 资料来源，无字幕
];

export function cue(id) {
  const c = CUES.find((x) => x.id === id);
  if (!c) throw new Error(`Unknown cue: ${id}`);
  return c;
}
