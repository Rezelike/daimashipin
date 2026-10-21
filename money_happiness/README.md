# 钱能买到快乐吗？ · Can Money Buy Happiness?

16:9 横屏数据解说视频（1920×1080 / 60fps）。深色数据风，无旁白，中英双语字幕，节奏紧凑。目前是 38.4 秒样片（片头 + 研究 01，加小人版），暂无声音。

- 样片：[`../out/money_happiness_sample.mp4`](../out/money_happiness_sample.mp4)（16.9 MB）
- 预览拼图：[`../out/money_happiness_preview.png`](../out/money_happiness_preview.png)（15 个关键帧）
- 新旧对比：[`../out/money_happiness_compare.png`](../out/money_happiness_compare.png)（6 组镜头，左边是 v1，右边是加小人版）
- 旧版 v1：[`../out/money_happiness_sample_v1.mp4`](../out/money_happiness_sample_v1.mp4)（37.6 秒，14.8 MB，没有小人）

## 结构

主线是三篇 PNAS 论文：2010 年提出 → 2021 年被推翻 → 2023 年双方合作给出解释。

| 时间 | 段落 | 内容 | 状态 |
|---|---|---|---|
| 0:00 | 片头 | 标题 → 卡尼曼和迪顿 → $75,000 → 曲线变平 → 数字裂开：「十年后，它被推翻了」→「到底谁对？」：卡尼曼（2010）和基林斯沃思（2021）站在裂开的两半数字下面对视 | 已完成 |
| 0:13 | 研究 01 · 快乐的天花板 | 45 万份问卷（450 个小人，每个代表 1,000 份）→ 两个问题：评委小人举 7 分牌，另一个小人回想「昨天」按下「是」→ 小人从左到右化成数据点：人生评分一直涨，「昨天开心吗」过了 $75K 就平了 → $25K / $75K / $150K 三个小人对比：买得到满意，买不到快乐 | 已完成 |
| — | 研究 02 · 2021 | 170 多万次「你现在感觉怎么样？」的实时打分：过了 $75K 还在涨 | 待做 |
| — | 研究 03 · 2023 | 对抗式合作：只有最不快乐的约 20% 在 $10 万以后变平；2010 年的问题有天花板效应 | 待做 |
| — | 结尾 | | 待做 |

## 生成

需要 Node.js 18+。不需要浏览器，也不用另装 ffmpeg（`ffmpeg-static` 自带）。

```bash
cd money_happiness
npm install
npm run render     # ../out/money_happiness_sample.mp4
npm run preview    # ../out/money_happiness_preview.png：15 帧拼成一张图，快速检查画面
node src/render.mjs --still 6.5 --out build/still.png           # 单帧 PNG
node src/render.mjs --from 12.6 --to 20 --out build/part.mp4    # 只渲染一段（--crf 可调画质，默认 16）
```

- 改字幕或节奏：只改 `src/cues.mjs`，所有画面动画都对齐里面的时间点。
- 加段落：在 `src/scenes/` 写场景，再到 `src/frame.mjs` 的 `SCENES` 里登记，并更新 `DURATION`。

## 小人

- 用法：数字和曲线出场时，小人让开；讲这些数字是什么意思时，小人再回来。片头只在「到底谁对？」这里加了两个人，免得抢走裂开的 $75,000 的注意力。
- `src/engine/people.mjs`：有名字的人物（卡尼曼、迪顿、基林斯沃思）。`mood`（表情）、`look`（眼神）、`browTilt`（眉毛）都是可选参数，不传就和原来画得一样。
- `src/engine/folk.mjs`：路人小人。`mood` 控制表情，从 -1（难过）到 1（大笑）；手臂角度用 `ARM_DOWN` / `ARM_OUT` / `ARM_UP`；可以举牌，牌上写字或显示满意度条。画人群时用 `drawFolkSprite`：每个小人只画一次，存成小位图，之后每帧直接贴图。450 个小人一帧大约 15 毫秒。

## 数据来源

画面上的研究数据都出自下面的论文，出处标签会显示在画面上。

| 段落 | 论文 | 用到的数据 |
|---|---|---|
| 研究 01 | Kahneman & Deaton (2010). High income improves evaluation of life but not emotional well-being. *PNAS*. [doi:10.1073/pnas.1011492107](https://doi.org/10.1073/pnas.1011492107) | 超过 45 万份盖洛普问卷（美国，2008–09 年）；情绪幸福感在家庭年收入约 $75,000 处不再上升 |
| 研究 02 | Killingsworth (2021). Experienced well-being rises with income, even above $75,000 per year. *PNAS*. [doi:10.1073/pnas.2016976118](https://doi.org/10.1073/pnas.2016976118) | 33,391 名美国在职成年人的 1,725,994 次实时报告；幸福感随对数收入线性上升，没有平台 |
| 研究 03 | Killingsworth, Kahneman & Mellers (2023). Income and emotional well-being: A conflict resolved. *PNAS*. [doi:10.1073/pnas.2208661120](https://doi.org/10.1073/pnas.2208661120) | 只有最不快乐的约 20% 在 $10 万以后变平，最快乐的一组反而加速；2010 年的测量有天花板效应 |

- 曲线是按论文结论画的示意图（画面上标了「示意图 · SCHEMATIC」），不是逐点还原原始数据。
- 三项研究的样本都只来自美国；$75,000 是 2008–09 年的美元。

## 字体

都放在仓库根目录的 `fonts/`，均为 SIL Open Font License 1.1，可免费商用：

- [Noto Serif SC](https://github.com/notofonts/noto-cjk)（Regular / Medium / SemiBold）：中文和大数字
- [EB Garamond](https://github.com/octaviopardo/EBGaramond12)（Italic）：英文字幕
- [IBM Plex Mono](https://github.com/IBM/plex)（Regular / SemiBold）：标签和刻度

## 技术备注

- 渲染流程：`@napi-rs/canvas` 逐帧画出 RGBA 原始帧，经管道送进 `ffmpeg-static`，用 libx264 编码（crf 16，preset slow，yuv420p，BT.709）。
- 背景不要加逐帧变化的颗粒噪点。加了之后码率涨到约 70 Mbps（样片 340 MB），x264 还会把噪点压成色块。现在用的是固定的 ±2 级抖动，防止渐变出现色带，样片只有 14.8 MB。
- 片头「裂开」的数字：左右两半各自预渲染、各自加光晕。不要在运行时裁切整张带光晕的图，否则裂缝处会出现一条暗线。
- 英文字幕用的 EB Garamond 里没有 ①② 这类带圈数字，所以英文字体后面加了 Noto Serif SC 作为备用字体，不然会显示成方框。
- 随机数都用固定种子（`mulberry32`），所以可以用 `--from` / `--to` 分段并行渲染，再用 ffmpeg 的 concat 直接拼接、不重新编码，每一帧都和整段渲染的一样。现在的样片就是分 4 段渲染的，8 核机器上用了约 46 秒。
