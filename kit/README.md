# kit：新小人和共用工具（「一口气做 6 条」那一批用）

用户 2026-10-31：「不要在开头放两个小人了，下次换成一个小人」「随便让他摆个什么姿势，就是不要再坐到凳子上写作业读书」「那个人我感觉特别幼稚」。

- `figure.js`：一个成年人比例的小人（约 7.5 个头高，s = 1 时 440 px），2D 骨架，正向运动学。姿势在 `POSES` 里（站、指、想、跳、躺、垂头、耸肩），走路用 `walkPose(phase)`，两个姿势之间用 `lerpPose(a, b, t)` 过渡。三种画法：`style: 'A'` 扁平插画（有小表情：`face: 'calm' | 'happy' | 'tired' | 'wow'`）、`'B'` 霓虹线条、`'C'` 剪影 + 轮廓光。`drawFigure()` 返回头和两只手在屏幕上的位置，方便把道具挂在手上。
- `lib.js`：从 `bedtime_words/src/lib.js` 复制来的文字、缓动、关键帧、背景和章节条。
- `design/figure_sheet.html` + `design/figure_sheet.js`：三种画法 × 五个姿势的对比图，输出 `design/小人方案.png`：
  ```bash
  node kit/tools/design.mjs kit/design/figure_sheet.html kit/design/小人方案.png
  ```
