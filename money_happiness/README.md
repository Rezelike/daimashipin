# 钱能买到快乐吗？ · Can Money Buy Happiness?

16:9 横屏数据解说视频（1920×1080 / 60fps）。深色数据风，无旁白，中英双语字幕，节奏紧凑。完整版 2 分 03 秒（片头 + 三项研究 + 结尾），暂无声音。

- 成片：[`../out/money_happiness_sample.mp4`](../out/money_happiness_sample.mp4)（2:03，41.2 MB）
- 预览拼图：[`../out/money_happiness_preview.png`](../out/money_happiness_preview.png)（24 个关键帧，覆盖全片）
- 新旧对比：[`../out/money_happiness_compare.png`](../out/money_happiness_compare.png)（研究 01 加小人前后，6 组镜头，左边是 v1）
- 旧版 v1：[`../out/money_happiness_sample_v1.mp4`](../out/money_happiness_sample_v1.mp4)（37.6 秒，14.8 MB，没有小人）

## 结构

主线是三篇 PNAS 论文：2010 年提出 → 2021 年被推翻 → 2023 年双方合作给出解释。

| 时间 | 段落 | 内容 |
|---|---|---|
| 0:00 | 片头 | 标题 → 卡尼曼和迪顿 → $75,000 → 曲线变平 → 数字裂开：「十年后，它被推翻了」→「到底谁对？」：卡尼曼（2010）和基林斯沃思（2021）站在裂开的两半数字下面对视 |
| 0:13 | 研究 01 · 快乐的天花板 | 45 万份问卷（450 个小人，每个代表 1,000 份）→ 两个问题：评委小人举 7 分牌，另一个小人回想「昨天」按下「是」→ 小人从左到右化成数据点：人生评分一直涨，「昨天开心吗」过了 $75K 就平了 → $25K / $75K / $150K 三个小人对比：买得到满意，买不到快乐 |
| 0:38 | 研究 02 · 没有天花板 | 基林斯沃思的 App 每天随机提醒几次 → 大手机上问「你现在感觉怎么样？」，从「非常差」到「非常好」拖滑杆；2010 年的「昨天」和「是 / 否」被划掉 → 一排排举着手机的小人，计数跑到 1,725,994 次打分、33,391 人 → 小人化成数据点，2021 年的线撞碎 2010 年的天花板 → $80K 两边各画一个「收入 ×2」三角形：一样陡 → 人生满意度也一起涨，研究 01 的三个小人再出场，$75K 到 $150K 之间快乐那一格的「=」翻成「↑」→ 2010 和 2021 两张小图之间裂开：结论正好相反 |
| 1:05 | 研究 03 · 握手言和 | 卡尼曼和基林斯沃思一起走来，梅勒斯当裁判，论文作者栏加上「· MELLERS」，盖章「对抗式合作」→ 50 个小人按快乐程度排成 5 行，化成 5 条百分位曲线：大多数人一直涨，最快乐的一组过了 $10 万更快，最不快乐的一组变平，5 条平均下来正好是一条直线 → 天花板效应：「昨天开心吗」只能答是或否，开心、很开心、非常开心都是「是」，天花板落下，把真实感受截平 → P15 那条线和 2010 年的曲线放在一起：同一个形状，先涨，后平 |
| 1:46 | 结尾 | 标题回来 → 7 个小人从 $15K 到 $200K，越往右越开心 → 右边一个有钱却不快乐的人：金币砸下来又弹走，快乐条不动 → 三篇论文、四位研究者 → 资料来源 |

## 生成

需要 Node.js 18+。不需要浏览器，也不用另装 ffmpeg（`ffmpeg-static` 自带）。

```bash
cd money_happiness
npm install
npm run render     # ../out/money_happiness_sample.mp4
npm run preview    # ../out/money_happiness_preview.png：24 帧拼成一张图，快速检查画面
node src/render.mjs --still 6.5 --out build/still.png           # 单帧 PNG
node src/render.mjs --from 12.6 --to 20 --out build/part.mp4    # 只渲染一段（--crf 可调画质，默认 16）
```

- 改字幕或节奏：只改 `src/cues.mjs`，所有画面动画都对齐里面的时间点。
- 加段落：在 `src/scenes/` 写场景，再到 `src/frame.mjs` 的 `SCENES` 里登记。总时长由 `src/scenes/end.mjs` 的 `END_T` 决定（最后一条字幕结束后 0.4 秒）。

## 小人

- 用法：数字和曲线出场时，小人让开；讲这些数字是什么意思时，小人再回来。片头只在「到底谁对？」这里加了两个人，免得抢走裂开的 $75,000 的注意力。
- `src/engine/people.mjs`：有名字的人物（卡尼曼、迪顿、基林斯沃思、梅勒斯）。`mood`（表情）、`look`（眼神）、`browTilt`（眉毛）都是可选参数，不传就和原来画得一样。梅勒斯是 `hairStyle: 'bob'`，头发盖住耳朵，所以不画耳朵。
- `src/engine/folk.mjs`：路人小人。`mood` 控制表情，从 -1（难过）到 1（大笑）；手臂角度用 `ARM_DOWN` / `ARM_OUT` / `ARM_UP`；可以举牌，牌上写字或显示满意度条；也可以拿手机（`prop: { kind: 'phone', side, lit }`），`phoneCenter()` 算出手机屏幕的位置，提醒的光点从这里飞出。
- 画人群时用 `drawFolkSprite`：每个小人只画一次，存成小位图，之后每帧直接贴图。位图按这个小人自己的 mood / look / lookY / armL / armR / prop 画，画好就不再变。450 个小人一帧大约 15 毫秒。

## 图表

都在 `src/engine/chart.mjs`，横轴是对数收入。

- 2010 年用 $10K–$160K 的 `AXIS_2010`；2021、2023 年要画到更高收入，用 $10K–$250K 的 `AXIS_WIDE`，刻度标到 $200K。
- 2021 年的线在 $75K 以下和 2010 年一样陡，所以两条线正好在 2010 年的平台处分开，天花板在交点处裂开。
- 2023 年的 5 条百分位曲线（P15 / P30 / P50 / P70 / P85）在 $10 万处转折：P15 变平，P85 斜率 ×2.2，其余 ×0.9–0.95。5 个倍数平均正好是 1，所以 5 条的平均仍是一条直线，对应论文说的 complementary nonlinearities。

## 数据来源

画面上的研究数据都出自下面的论文，出处标签会显示在画面上，片尾有完整引用和 DOI。

| 段落 | 出处 | 用到的数据 |
|---|---|---|
| 研究 01 | Kahneman & Deaton (2010). High income improves evaluation of life but not emotional well-being. *PNAS*. [doi:10.1073/pnas.1011492107](https://doi.org/10.1073/pnas.1011492107) | 超过 45 万份盖洛普问卷（美国，2008–09 年）；情绪幸福感在家庭年收入约 $75,000 处不再上升 |
| 研究 02 | Killingsworth (2021). Experienced well-being rises with income, even above $75,000 per year. *PNAS*. [doi:10.1073/pnas.2016976118](https://doi.org/10.1073/pnas.2016976118) | 33,391 名美国在职成年人的 1,725,994 次实时报告；题目是 How do you feel right now?，从 very bad 到 very good；$80,000 以上和以下涨得一样陡，没有平台 |
| 研究 03 | Killingsworth, Kahneman & Mellers (2023). Income and emotional well-being: A conflict resolved. *PNAS*. [doi:10.1073/pnas.2208661120](https://doi.org/10.1073/pnas.2208661120) | 梅勒斯当裁判的对抗式合作；只有最不快乐的约 20% 在 $10 万以后变平，最快乐的一组反而加速；2010 年的是 / 否题有天花板效应；用「不快乐」来描述，2010 年的结论可能就对了 |
| 结尾 | [Penn Today 新闻稿](https://penntoday.upenn.edu/news/does-more-money-correlate-greater-happiness-Penn-Princeton-research)（2023 年 3 月） | 基林斯沃思的总结：大多数人收入越高越快乐；有钱却不快乐的人，再多钱也帮不上忙 |

- 曲线是按论文结论画的示意图（画面上标了「示意图 · SCHEMATIC」），不是逐点还原原始数据。
- 研究 02 里一天的 4 个提醒时刻（09:12 等）是演示用的；论文只说每天随机提醒几次。
- 三项研究的样本都只来自美国；$75,000 是 2008–09 年的美元。
- 2024 年 PNAS 又刊出两封商榷信（[doi:10.1073/pnas.2313712121](https://doi.org/10.1073/pnas.2313712121)、[doi:10.1073/pnas.2314207121](https://doi.org/10.1073/pnas.2314207121)）和作者回复（[doi:10.1073/pnas.2322160121](https://doi.org/10.1073/pnas.2322160121)），片尾的说明里提到了这一点。
- 片头不说「两位诺奖得主」：迪顿 2015 年才获奖，2010 年发论文时只有卡尼曼得过。两人的获奖年份标在名字下面。

## 字体

都放在仓库根目录的 `fonts/`，均为 SIL Open Font License 1.1，可免费商用：

- [Noto Serif SC](https://github.com/notofonts/noto-cjk)（Regular / Medium / SemiBold）：中文和大数字
- [EB Garamond](https://github.com/octaviopardo/EBGaramond12)（Italic）：英文字幕
- [IBM Plex Mono](https://github.com/IBM/plex)（Regular / SemiBold）：标签和刻度

## 技术备注

- 渲染流程：`@napi-rs/canvas` 逐帧画出 RGBA 原始帧，经管道送进 `ffmpeg-static`，用 libx264 编码（crf 16，preset slow，yuv420p，BT.709）。
- 背景不要加逐帧变化的颗粒噪点。加了之后码率涨到约 70 Mbps（38 秒的样片就有 340 MB），x264 还会把噪点压成色块。现在用的是固定的 ±2 级抖动，防止渐变出现色带。
- 片头「裂开」的数字：左右两半各自预渲染、各自加光晕。不要在运行时裁切整张带光晕的图，否则裂缝处会出现一条暗线。
- 英文字幕用的 EB Garamond 里没有 ①② 这类带圈数字，所以英文字体后面加了 Noto Serif SC 作为备用字体，不然会显示成方框。
- 每一帧只由时间 t 决定：随机数都用固定种子（`mulberry32`），缓存的小人位图也和渲染顺序无关。所以可以用 `--from` / `--to` 分段并行渲染，再用 ffmpeg 的 concat 直接拼接、不重新编码。分段的起止点要落在整帧上（60fps 下取 0.2 秒的倍数最省事）。现在的成片分 8 段渲染（前 7 段各 15.4 秒，最后一段 15.6 秒），8 核机器上用了约 2 分钟。
