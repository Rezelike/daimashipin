# Storyboard for 《临时物永久化理论》
# Each scene: (shot, duration_s, subtitle, chapter_label)
# [..] marks the highlighted (gold) keyword in the subtitle.

# Shot presets: 3D camera zoom k + world target point (x, y, z), plus options.
SHOTS = {
    "wide":       dict(k=1.00, target=None),
    "wide2":      dict(k=1.25, target=(0.0, 0.35, 4.2)),
    "chair":      dict(k=2.80, target=(1.50, 0.62, 3.25)),
    "chair_wide": dict(k=1.60, target=(1.05, 0.55, 3.6)),
    "bag":        dict(k=5.20, target=(-2.00, 0.80, 5.05), bags=1),
    "bags2":      dict(k=3.60, target=(-1.70, 0.85, 5.15), bags=2),
    "remote":     dict(k=6.50, target=(-0.28, 0.53, 2.75)),
    "remote_tape": dict(k=8.5, target=(-0.18, 0.535, 2.75)),
    "table":      dict(k=3.00, target=(-0.10, 0.58, 2.85)),
    "leg":        dict(k=6.00, target=(0.555, 1.22, 2.66)),
    "leg_close":  dict(k=9.50, target=(0.555, 1.25, 2.66)),
    "phone":      dict(k=10.5, target=(0.1425, 0.42, 3.05)),
    "box":        dict(k=2.40, target=(1.25, 0.98, 4.70)),
    "box_wide":   dict(k=1.50, target=(0.8, 0.8, 4.7)),
    "tag":        dict(k=2.60, target=(-0.12, -0.06, 4.0), tag=True),
    "tag_close":  dict(k=4.20, target=(-0.12, -0.08, 4.0), tag=True),
    "tag_wide":   dict(k=1.50, target=(-0.1, 0.05, 4.4), tag=True),
    "sticky":     dict(k=6.50, target=(0.21, -0.01, 6.0)),
    "notice":     dict(k=4.20, target=(2.00, -0.20, 6.0)),
    "flower":     dict(k=3.40, target=(0.38, 0.40, 2.95), flower=True),
    "leg_flower": dict(k=3.60, target=(0.50, 0.95, 2.70), flower=True),
    "box_end":    dict(k=1.70, target=(1.0, 0.85, 4.7), flower=True),
    "chair_end":  dict(k=2.50, target=(1.50, 0.60, 3.25), flower=True),
    "ending":     dict(k=1.00, target=None, flower=True, tag=True),
}

SCENES = [
    ("title",       8.0, "临时物[永久]化理论", ""),
    ("wide2",       6.0, "在家里看一圈，大概能找到这些东西。", "一 · 现象"),
    ("chair",       7.0, "卧室角落的椅子，坐的人很少，[衣服]堆得很多。", "一 · 现象"),
    ("bag",         7.0, "抽屉里有个塑料袋，专门用来[装别的塑料袋]。", "一 · 现象"),
    ("remote",      7.0, "遥控器后盖坏了，用胶带粘着，一粘就是[三年]。", "一 · 现象"),
    ("leg",         7.0, "桌腿下垫着一张纸，那张桌子[再没晃过]。", "一 · 现象"),
    ("phone",       7.0, "“新建文件夹(3)”里，放着[最重要的东西]。", "一 · 现象"),
    ("box",         6.5, "门口的纸箱：“先放着，[过两天拆]”。", "一 · 现象"),
    ("wide",        7.0, "当初都说是[临时]的，后来都成了[永久]的。", "一 · 现象"),
    ("tag",         8.0, "没有什么，比临时方案[更持久]。", "二 · 核心命题"),
    ("table",       8.0, "人想改变现状，靠的是“[不能用]”，而不是“不完美”。", "第一定律 · 够用即终点"),
    ("remote_tape", 8.0, "胶带不是在修遥控器，是在[消灭“修”这件事]。", "第一定律 · 够用即终点"),
    ("chair_wide",  8.0, "临时物存在越久，周围的东西就越[围着它安排]。", "第二定律 · 习惯的引力"),
    ("leg_close",   7.5, "它已经不是凑合，而是[承重的一部分]。", "第二定律 · 习惯的引力"),
    ("tag_close",   7.5, "“临时”两个字，像一张[免检证]。", "第三定律 · 标签豁免"),
    ("tag_wide",    7.5, "从没被认真看待，所以也[从没被认真否定]。", "第三定律 · 标签豁免"),
    ("leg",         6.5, "越潦草的方案，[活得越久]。", "三 · 推论"),
    ("sticky",      6.5, "“等有空再弄”，等于“[永远不弄]”。", "三 · 推论"),
    ("chair",       6.5, "本来是正式的椅子，现在成了[衣架]。", "三 · 推论"),
    ("bags2",       7.0, "装塑料袋的塑料袋，迟早会有[第二个]。", "三 · 推论"),
    ("notice",      7.5, "那张“临时通知”，会比很多[正式制度]活得久。", "四 · 可验证的预测"),
    ("flower",      7.5, "临时物能永久存在，是因为它[真的解决了问题]。", "五 · 这个理论想说什么"),
    ("leg_flower",  7.5, "那张垫桌腿的纸，比说明书[更懂那张桌子]。", "五 · 这个理论想说什么"),
    ("box_end",     7.0, "想改变什么，就[别给它“临时”的机会]。", "五 · 这个理论想说什么"),
    ("chair_end",   7.0, "那把椅子不用愧疚，它就是[衣服的家]。", "五 · 这个理论想说什么"),
    ("ending",     11.0, "生活，是一个个“[先这样吧]”攒起来的。", ""),
]

SPEED = 0.80   # global duration scale -> ~2:33 total
FPS = 30
XFADE = 1.0    # cross-fade seconds between scenes


def shot_of(name):
    if name == "title":
        d = dict(SHOTS["wide"])
        d["title"] = True
        return d
    return dict(SHOTS[name])


def timeline():
    starts, durs, t = [], [], 0.0
    for s in SCENES:
        d = round(s[1] * SPEED * FPS) / FPS
        starts.append(t)
        durs.append(d)
        t += d
    return starts, durs, t


if __name__ == "__main__":
    st, du, total = timeline()
    for s, a, d in zip(SCENES, st, du):
        print(f"{a:7.2f} {d:5.2f}  {s[0]:12s} {s[2]}")
    print("total", total)
