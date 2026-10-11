# 代码视频：60 秒搞懂「防抖 Debounce」

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
