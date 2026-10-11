# 60 秒看懂「蝴蝶效应」

用 Python 代码生成的科普视频：66 秒，1080p，带中文配音、字幕和音效。

![预览](out/butterfly_preview.gif)

- 成片：[`out/butterfly.mp4`](out/butterfly.mp4)
- 字幕：[`out/butterfly.srt`](out/butterfly.srt)
- 关键帧：[`out/preview/`](out/preview)

## 画面中的数据都是算出来的

视频里的轨迹、距离、倍数和对数曲线，都是脚本用 RK4 数值方法求解洛伦兹方程（σ=10, ρ=28, β=8/3）得到的真实结果，不是手绘动画：

- 两个起点只差 0.00001，大约 t≈12.5 时彻底分开
- 实测误差增长率 λ≈0.81，相当于误差每 0.86 个时间单位翻一倍
- 1000 个相差不到 0.001 的起点，最后会散布到整个吸引子上
- 两条轨迹被分别转换成左、右声道的旋律：开始时两个声道是同一段旋律，分开后变成两段不同的旋律

## 自己生成

```bash
pip install pillow numpy imageio-ffmpeg gtts
python make_video.py --preview   # 先导出关键帧检查画面
python make_video.py             # 渲染完整视频，约 2 分钟
```

配音使用 gTTS（Google 中文语音），需要能访问 translate.google.com。字幕和画面的时间会根据配音长度自动对齐。
