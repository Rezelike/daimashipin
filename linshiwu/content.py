"""Narration script. Each scene is a list of lines.

A line is either a plain string (used for both subtitle and TTS) or a tuple
(subtitle_text, tts_text) when the spoken form must differ from the on-screen form.
"""

TITLE = "临时物永久化理论"

SCENES = [
    dict(id="open", chapter="", pre=1.2, post=0.6, lines=[
        "这把椅子，已经三年没有人坐过了。",
        "但它，从来没有空过。",
    ]),
    dict(id="title", chapter="", pre=0.3, post=1.0, lines=[
        "今天，我们来观察一种特别的东西。",
    ]),
    dict(id="specimens", chapter="观察", pre=0.4, post=0.8, lines=[
        "它们广泛分布在人类的居所里。",
        "装满塑料袋的塑料袋。",
        "被胶带缠住的遥控器。",
        "垫在桌腿下的纸片。",
        "门口那个，过两天就拆的纸箱。",
        ("还有电脑里的，新建文件夹(3)。", "还有电脑里的，新建文件夹三。"),
        "它们有一个共同的出身。当初，都说是临时的。",
        "后来，都成了永久的。",
    ]),
    dict(id="core", chapter="命题", pre=0.4, post=1.4, lines=[
        "研究者把这种现象，称为临时物永久化。",
        "它的核心，只有一句话。",
        "没有什么，比临时方案更持久。",
    ]),
    dict(id="law1", chapter="第一定律", pre=1.0, post=0.8, lines=[
        "第一定律，够用即终点。",
        "人们改变现状的动力，来自不能用，而不是不完美。",
        "临时方案一出现，不能用，就变成了能用但不完美。改变的动力，随之消失。",
        "所以，胶带不是在修遥控器。胶带，是在消灭修遥控器这件事。",
    ]),
    dict(id="law2", chapter="第二定律", pre=1.0, post=1.0, lines=[
        "第二定律，习惯的吸引力。",
        "临时物存在得越久，周围的一切，就越会围绕它重新排列。",
        "那把椅子，早就不是椅子了。它是衣柜和洗衣篮之间，一个稳定的中转站。",
        "如果有一天你把它清空，你会发现，衣服无家可归了。",
    ]),
    dict(id="law3", chapter="第三定律", pre=1.0, post=1.0, lines=[
        "第三定律，标签豁免。",
        "正式的东西，会被挑剔。难看，不顺手，该换了。",
        "但临时的东西不会。因为，它本来就是临时的嘛。",
        "从没被认真看待过，所以，也从没被认真否定过。",
    ]),
    dict(id="breed", chapter="推论", pre=1.0, post=2.2, lines=[
        "由此还能推出一个现象，临时物会繁殖。",
        "装塑料袋的塑料袋，迟早会被塞满。",
        "然后，第二个装塑料袋的塑料袋，就诞生了。",
    ]),
    dict(id="turn", chapter="结论", pre=0.6, post=1.0, lines=[
        "不过，这并不是在嘲笑谁懒。",
        "临时物能留下来，是因为它真的解决了问题。只是，解决得不太好看。",
        "这张纸，比任何说明书，都更懂这张桌子。",
    ]),
    dict(id="end", chapter="", pre=0.6, post=3.0, lines=[
        "我们的生活，从来不是按计划搭起来的。",
        ("而是由一个又一个「先这样吧」，攒起来的。", "而是由一个又一个，先这样吧，攒起来的。"),
        ("你家里的「先这样吧」，是什么？", "你家里的先这样吧，是什么？"),
    ]),
]

LINE_GAP = 0.45   # silence between lines inside a scene (seconds)
VOICE_SID = 49    # kokoro zm_yunjian (deep male narrator)
VOICE_SPEED = 0.92
