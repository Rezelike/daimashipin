# 《事成V你50》11～19 秒选英雄卡预览

TT语音「你与搭子的群像故事」参赛短片《事成V你50》（60 秒）里的 11～19 秒。四个陌生人在 TT 语音房间里组队，像无畏契约选英雄一样一张张"锁定"。最后一张是大聪明，锁定失败，一只乌鸦飞过。

- 成片：[`hero_select_11-19s.mp4`](hero_select_11-19s.mp4)（8 秒，1280×720，30 fps，有声音）
- 无声 GIF：[`hero_select_11-19s_silent.gif`](hero_select_11-19s_silent.gif)
- 关键帧：[`hero_select_11-19s_keyframes.png`](hero_select_11-19s_keyframes.png)
- 代码：[`render_hero_select.py`](render_hero_select.py)

这是预览版：人物是代码画的占位剪影，正式版换成 AI 定妆图；台词用的是 edge-tts 在线 AI 配音；叮、嗖、锁定、乌鸦叫和背景节奏都是代码合成的。

## 时间分配

| 卡 | 成片时间 | 台词 |
|---|---|---|
| 阿飞（田径队） | 11.0～12.8 秒 | V我50，真的假的？ |
| 小K（轮滑社） | 12.8～14.6 秒 | 下坡？我的主场。 |
| 老周（航模社） | 14.6～16.0 秒 | 50块，够买俩桨。 |
| 星星（天文社） | 16.0～17.8 秒 | 钱不要，鸡翅留一个。 |
| 大聪明（501寝室） | 17.8～19.0 秒 | （乌鸦叫） |

## 自己生成

```bash
pip install numpy pillow imageio-ffmpeg edge-tts
python shicheng_v50/render_hero_select.py
```

在仓库根目录运行。配音需要联网，生成后缓存在 `shicheng_v50/.assets/`，已被 `.gitignore` 忽略。字体用仓库 `fonts/` 里的 Noto Sans SC 和 JetBrains Mono。
