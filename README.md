# 代码视频

| 作品 | 成片 | 说明 |
|---|---|---|
| 钱能买到快乐吗？· 完整版（2:03，横屏 60fps，片头 + 三项研究 + 结尾，无旁白，中英双语字幕） | [`out/money_happiness_sample.mp4`](out/money_happiness_sample.mp4) · [预览拼图](out/money_happiness_preview.png) · [新旧对比](out/money_happiness_compare.png) · [旧版 v1](out/money_happiness_sample_v1.mp4) | [`money_happiness/`](money_happiness/README.md) |
| 60 秒搞懂「防抖 Debounce」 | [`out/debounce.mp4`](out/debounce.mp4) | 见下文 |

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

`fonts/` 内为 [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)、[Noto Sans SC / Noto Serif SC](https://github.com/notofonts/noto-cjk)、[EB Garamond](https://github.com/octaviopardo/EBGaramond12) 与 [IBM Plex Mono](https://github.com/IBM/plex)，均为 SIL Open Font License。
