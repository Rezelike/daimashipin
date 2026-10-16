# 费曼学习法 · The Feynman Technique

3 分 51 秒横屏讲解视频（1920×1080 / 30fps）。深色科技风，中英双语，无配音。原创配乐以钢琴和小提琴为主，136 BPM。

- 成片：[`../out/feynman.mp4`](../out/feynman.mp4)
- 封面：[`../out/feynman_cover.png`](../out/feynman_cover.png)

## 结构

| 时间 | 段落 | 内容 |
|---|---|---|
| 0:00 | 开场 Hook | 「为什么你学了就忘？」→ 3 个痛点 → 不是你笨，是方法错了 |
| 0:14 | 标题 | 费曼学习法 · 4 步，学什么都更快 · 建议先收藏 |
| 0:21 | 费曼是谁 | 费曼图动画、1965 诺贝尔物理学奖、《我不知道的事》笔记本 |
| 0:42 | 核心 | 听懂了 ≠ 真懂了 · 费曼「大一新生」原话 |
| 0:56 | 4 步法 | 选概念 → 讲给 12 岁孩子 → 找卡壳点 → 简化 + 比喻 |
| 2:21 | 实战 | 用 4 步学「复利」（单利与复利 30 年曲线、滚雪球比喻） |
| 2:56 | 误区 | 3 个常见错误及改法 |
| 3:18 | 总结 + 互动 | 一图总结（可截图），评论区提问，点赞 / 收藏 / 关注 |

所有镜头切换都落在音乐小节线上：`timeline.py` 定义了共享的小节网格，背景地面网格每拍滚动一格。

## 生成

```bash
pip install -r feynman/requirements.txt
cd feynman
python fetch_assets.py      # 下载 CC0 乐器采样与 Lucide 图标（只用 GitHub，不入库）
python make_music.py        # build/music.wav
python make_video.py        # ../out/feynman.mp4（多进程渲染，约 3 分钟）
python make_video.py --preview        # build/contact_sheet.png：24 帧拼成一张图，快速检查
python make_video.py --frame 63.5     # 单帧 PNG
python make_video.py --cover          # ../out/feynman_cover.png
```

在无图形界面的 Linux 上，`skia-python` 需要系统里有 `libEGL.so.1` / `libGL.so.1`（例如 `mesa-libEGL`、`mesa-libGL`）。

## 素材与授权

- 配乐：原创曲，由脚本作曲并渲染，使用 [VSCO 2 Community Edition](https://github.com/sgossner/VSCO-2-CE) 真实乐器采样（CC0-1.0）。立式钢琴由 Simon Dalzell（Ivy Audio）采样。商用免费，不需要署名，平台版权识别也不会误判。
- 图标：[Lucide](https://github.com/lucide-icons/lucide)（ISC）
- 字体：Noto Sans SC、JetBrains Mono（SIL OFL）
- 引言出处：费曼「讲不到大一新生的水平，说明我们还没真正理解」一句，出自 David Goodstein 的回忆（*Feynman's Lost Lecture*）。笔记本标题出自 James Gleick 的 *Genius*。
