# 代码视频

| 作品 | 成片 | 说明 |
|---|---|---|
| 开场动画样片（0:30，4 种开场动画：对比反转 / 消散 / 分叉 / 计时） | [`out/openers_demo.mp4`](out/openers_demo.mp4) | [`engine/openers.py`](engine/openers.py) |
| 主动回忆（1:15，无配乐，按 128 BPM 卡点，画面不抖，直接结束） | [`out/active_recall.mp4`](out/active_recall.mp4) · [封面](out/active_recall_cover.png) · [发布文案](out/active_recall_publish.txt) | [`episodes/active_recall/`](episodes/active_recall/episode.py) |
| 艾宾浩斯遗忘曲线（1:16，无配乐，按 128 BPM 的节拍剪辑） | [`out/forgetting_curve.mp4`](out/forgetting_curve.mp4) · [封面](out/forgetting_curve_cover.png) · [发布文案](out/forgetting_curve_publish.txt) | [`episodes/forgetting_curve/`](episodes/forgetting_curve/episode.py) |
| 费曼学习法 · 短版（1:12，新结构） | [`out/feynman_short.mp4`](out/feynman_short.mp4) · [无配乐版](out/feynman_short_nomusic.mp4) · [封面](out/feynman_short_cover.png) · [发布文案](out/feynman_short_publish.txt) | [`episodes/feynman_short/`](episodes/feynman_short/episode.py) |
| 费曼学习法（3:51，横屏，中英双语，钢琴 + 小提琴原创配乐） | [`out/feynman.mp4`](out/feynman.mp4) · [封面](out/feynman_cover.png) | [`feynman/`](feynman/README.md) |
| 60 秒搞懂「防抖 Debounce」 | [`out/debounce.mp4`](out/debounce.mp4) | 见下文 |

## 做新一期（引擎 + Skill）

- Skill：[`.kiro/skills/vibe-knowledge-video/`](.kiro/skills/vibe-knowledge-video/SKILL.md)。在新的 Kiro 对话里直接说「做下一期视频」，Kiro 会按它的流程执行：选题 → 分镜 → 渲染 → 验证 → 提 PR。它会先读 [`references/lessons.md`](.kiro/skills/vibe-knowledge-video/references/lessons.md) 里往期的抖音数据。
- 引擎：[`engine/`](engine/)。一期视频对应一个 `episodes/<名字>/episode.py`，结构固定为：痛点 → 10 秒内给答案 → 分步讲（每步带例子）→ 一图总结 → 互动。原创钢琴和小提琴配乐会根据每个场景的角色自动编配，自动检查会提示过小的字、缺失的字形和超出卡片的文字。

```bash
bash .kiro/skills/vibe-knowledge-video/scripts/setup_env.sh    # 环境准备（约 40 秒）
V=/projects/sandbox/.videoenv/vpy
$V -m engine.assets                                            # 下载 CC0 采样和图标
$V episodes/feynman_short/episode.py --preview                 # 生成一张拼图预览，并做文字检查
$V episodes/feynman_short/episode.py                           # 输出成片、无配乐版、发布文案，并自动验证
```

---

## 60 秒搞懂「防抖 Debounce」

用一个 Python 脚本自动生成 1 分钟代码讲解视频（1080p / 30fps / 带音效和字幕）。

![预览](out/debounce_preview.gif)

- 成片：[`out/debounce.mp4`](out/debounce.mp4)（点开后右上角下载按钮可下载）
- 字幕：[`out/debounce.srt`](out/debounce.srt)
- 关键帧：[`out/preview/`](out/preview)

## 自己生成

```bash
pip install -r requirements.txt
python make_video.py            # 输出 out/debounce.mp4 + out/debounce.srt
python make_video.py --preview  # 只导出关键帧 PNG，快速检查画面
```

不需要单独安装 ffmpeg（`imageio-ffmpeg` 自带）。

## 做下一期

在 `make_video.py` 里改：
- `CODE`：要讲的代码
- `SEGMENTS`：每段代码对应的讲解字幕和停顿时长
- 各个 `Scene` 类：片头、问题演示、可视化、总结

## 字体

`fonts/` 内为 [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) 与 [Noto Sans SC](https://github.com/notofonts/noto-cjk)，均为 SIL Open Font License。
