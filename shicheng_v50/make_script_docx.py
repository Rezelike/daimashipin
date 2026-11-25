#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把《事成V你50》剧本整理成 Word 文档（以 60 秒样片 v2 为准）。

在仓库根目录运行：
    pip install python-docx numpy pillow imageio-ffmpeg edge-tts
    python shicheng_v50/make_script_docx.py
输出 shicheng_v50/事成V你50_剧本.docx。这是给用户自己用 AI 生成视频的剧本：不放样片截图，只写到“九、前后呼应”
（用户 2026-11-25：“不要把你已经生成的镜头给我，第十点以及之后的全删”）。
镜头时间会和 render_sample_60s_v2.py 的 SHOTS 对一遍，对不上就报错；台词时间来自 sample_audio.py 的配音长度
（第一次运行要联网生成配音）。
"""
import datetime
import os
import re
import sys

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_hero_select as hero  # noqa: E402
import render_sample_60s_v2 as R2  # noqa: E402
import sample_audio as SA  # noqa: E402

OUT = os.path.join(HERE, '事成V你50_剧本.docx')

FONT_LATIN, FONT_CN = 'Microsoft YaHei', '微软雅黑'
RED = RGBColor(0xC0, 0x39, 0x2B)
DARK = RGBColor(0x26, 0x26, 0x26)
GRAY = RGBColor(0x80, 0x80, 0x80)
HEAD_FILL, ZEBRA_FILL, BORDER = 'F4D9D3', 'FAF6F5', 'BFBFBF'
CENTER, RIGHT = WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT

# ================================================================ 内容
INFO = [
    ('片名', '《事成V你50》（备选：《今晚吃鸡》）'),
    ('时长', '60秒'),
    ('画幅', '16:9横屏。要发竖屏的话改成9:16，人物放在画面中间'),
    ('风格', '放飞：短剧式推镜、纪录片旁白、游戏界面全贴到现实里，一本正经地干一件很小的事'),
    ('场景', '校园：8号楼501寝室、9号楼阳台、南门外卖架、校园路、大坡、保安岗亭、人工湖、8号楼门口和大厅'),
    ('群像', '宿舍：8号楼501的四个人。社团：田径队、轮滑社、航模社、天文社各一个人，分别住在别的楼，和501互不认识，'
           '是通过TT语音找搭子凑到一起的。再加一个8号楼的宿管阿姨'),
    ('游戏元素', '无畏契约（选英雄、锁定、爆能器滴滴声）、三角洲行动（大红）、和平精英（四排、空投、吃鸡）'),
    ('TT语音功能', '找搭子（“事成V你50”的帖子）、组队（四个陌生人锁定进房）、开麦（全程语音接力）、实时沟通（报点、交接、临时改路线）'),
    ('一句话梗概', '周四晚上10点52分，大聪明把炸鸡外卖填到了南门，可他住北区，离门禁只剩8分钟。他在TT语音发帖找搭子：“事成V你50”。'
              '四个社团的陌生人锁定进房，跑的跑，滑的滑，飞的飞，把一桶炸鸡接力运过了大半个校园。'),
    ('结尾字幕', '一个人很难吃鸡，一群人就行。在TT语音，永远有人并肩相伴。'),
]

SUMMARY = [
    '周四晚上10点52分，外卖小哥打来电话：炸鸡放南门了。可大聪明住北区8号楼，离23点门禁只剩8分钟。三个室友齐刷刷回头看他：“这把，拉完了。”',
    '大聪明在TT语音发了一条找搭子的帖子：“急！南门炸鸡运回北区8号楼，事成V你50。”田径队的阿飞、轮滑社的小K、航模社的老周、'
    '天文社的星星像选英雄一样，一个接一个锁定进房。',
    '星星在9号楼阳台用望远镜报点，阿飞从南门一路狂奔到坡顶，小K接过炸鸡顺着大坡滑到湖边，老周用无人机把炸鸡空投过湖。'
    '门禁前最后一秒，大聪明飞扑接住炸鸡，四个人同时扑进各自的宿舍楼。',
    '结账时，大聪明发现零钱只有3块5。大家反过来一人V他50；房间里一直灰着的“神秘人”也亮了，是8号楼的宿管阿姨。'
    '收款合计正好250，三个室友齐声喊：“二百五！”',
]

STRUCTURE = [
    ('起：出事', '0～11秒', 'S01–S07', '炸鸡放错南门，室友三连回头，大聪明发帖找搭子，全校的窗户亮了'),
    ('承：组队', '11～19秒', 'S08–S12', '四个社团的陌生人像选英雄一样锁定进房，大聪明锁定失败'),
    ('转：接力', '19～45秒', 'S13–S31', '报点、狂奔、交接、漂移、急刹、空投，门禁前一秒四栋楼同时飞扑，大吉大利，今晚吃鸡'),
    ('合：反转', '45～60秒', 'S32–S38', '宿管凝视，余额只有3块5，大家反过来V他50，神秘人是宿管阿姨，收款合计250，全员合影'),
]

HIGHLIGHTS = [
    '**小事当大片拍。**任务只是把一桶炸鸡运回宿舍，却按特种行动来拍：选英雄、望远镜报点、交接棒慢镜头、无人机空投、门禁前一秒飞扑。拍得越认真越好笑。',
    '**游戏界面贴满现实。**炸鸡被标成“大红”，路人头顶挂着“中立”“无害”的标签，右上角刷运送播报，门禁倒计时配爆能器的滴滴声，'
    '接住炸鸡弹出“大吉大利，今晚吃鸡”。',
    '**V我50从头贯穿到尾。**帖子写“事成V你50”，人是靠它招来的。结账时发现大聪明只有3块5，反转成大家V他50，最后收款合计正好250。',
    '**连“boss”都是搭子。**准点锁门的宿管阿姨，其实早就在房间里听了全程。',
    '**情绪拉满。**每个人都有招牌表情：大聪明瞳孔地震、哭着狂奔、当场石化；阿飞眼里冒火；老周眼镜反光；星星扶额；室友B灵魂出窍。'
    '反应镜头宁可夸张一点。',
]

CAST = [
    ('大聪明', '8号楼（男生楼）501寝室，大二。外号是室友起的，因为他总干这种事', '圆脸，鸡窝头，蓝白格子睡衣，人字拖，耳机挂在脖子上',
     '普通话，一急就破音', '填错地址、发帖、最后接住炸鸡的人。瞳孔地震、哭着狂奔、星星眼、当场石化'),
    ('阿飞', '田径队，住3号楼，被教练罚夜跑', '小麦色皮肤，一身腱子肉，红头带，红色田径背心，黑短裤，胸前50号号码布，荧光绿跑鞋',
     '长得猛，说话嗲', '第一棒：南门跑到坡顶。眼里冒火，跑起来带残影'),
    ('小K', '轮滑社社长，住6号楼', '黑头盔，灰卫衣的帽子扣在头盔外面，脸上一块创可贴，护膝，轮滑鞋', '话少，酷',
     '第二棒：顺着大坡滑到湖边。一脸酷，急刹时双手乱挥'),
    ('老周', '航模社，理工男，住7号楼', '侧分头，黑框眼镜，蓝格子衬衫，卡其裤，背着设备箱，手拿无人机遥控器', '平，像在念说明书',
     '第三棒：无人机空投过湖。推眼镜，镜片反光'),
    ('星星', '天文社，住9号楼（女生楼），在宿舍阳台上等流星', '黑长发，星星发卡，白色长款羽绒服，红围巾，天文望远镜', '冷静，像指挥官',
     '全程报点；唯一说“钱不要”的人。扶额，脸上一排黑线'),
    ('宿管阿姨', '8号楼宿管，守门二十年', '灰色短卷发，半框眼镜，红色针织开衫，腰上挂一串钥匙，手里端着保温杯',
     '慢，一个眼神能硬控整栋楼', '23:00准时锁门；房间里的“神秘人”。凝视、眼镜反光、最后眨眼'),
    ('室友A', '501，大聪明的室友', '短发，圆框眼镜，红色头戴耳机，灰T恤', '慢悠悠', '三连回头第一个。推眼镜，一脸审视'),
    ('室友B', '501，整天躺在上铺', '睡乱的头发，白背心，蓝短裤', '有气无力', '从“这把，拉完了”到“这把，夯爆了！”。灵魂出窍，流口水'),
    ('室友C', '501', '寸头，黑T恤，肩上搭毛巾，嘴里叼牙刷', '（没有单独台词）', '回头时牙刷吓掉；偷鸡翅被拍手，当场哭'),
    ('保安大爷', '南门保安', '保安帽，八字胡，深蓝制服，保温杯', '（没有台词）', '望远镜里“中立｜别惹”；岗亭里眼珠跟着转'),
    ('外卖小哥', '只在开头出现', '黄头盔，黄外套，电动车', '电话音，大大咧咧', '开场打电话，在南门比大拇指'),
    ('情侣', '长椅上的路人', '女生扎马尾、粉卫衣；男生绿外套，手里一杯奶茶', '（没有台词）', '被阿飞带起的风吹懵：从爱心眼到“？！”'),
]

# 镜号, 开始, 结束, 画面, 台词, 音效
SHOT_ROWS = [
    ('S01', 0.0, 1.4,
     '黑屏，白字“周四 22:52”。手机来电，屏幕上是外卖小哥的头像，两边弹出“嗡”。0.6秒接通，变成“通话中”。',
     '**外卖小哥**（电话音，大大咧咧）：“兄弟，炸鸡放南门了啊！”', '手机震动'),
    ('S02', 1.4, 4.0,
     '501寝室。室友A在左边电脑前打游戏，室友B盖着被子躺在上铺刷手机，室友C叼着牙刷站在右边。大聪明穿着格子睡衣站在中间接电话，一脸轻松。'
     '左上角滑进一个小窗：外卖小哥在南门外卖架旁边比大拇指。\n2.05秒，大聪明反应过来：瞳孔地震，张大嘴尖叫，整个人蹦起来；集中线炸开，'
     '画面一闪白，镜头猛推近，三个室友同时吓一跳。',
     '**大聪明**（破音）：“南门？？我住北区啊！”', '小窗滑入“嗖”；2.05秒“咚”'),
    ('S03', 4.0, 4.9,
     '三连回头，每人0.3秒，短剧式猛推镜：室友A转过来，眼镜一闪反光，一脸审视；室友B躺着扭过头，豆豆眼，眼神死；室友C猛回头，嘴里的牙刷吓掉了。'
     '\n字幕“距离门禁：8分钟｜距离南门：3公里”，门禁倒计时从这里挂上屏幕顶部。',
     '—', '三声“咚”；眼镜反光“叮”'),
    ('S04', 4.9, 6.6, '室友A特写：推了推眼镜，镜片反光，半眯着眼，头上冒出问号。',
     '**室友A**（慢悠悠）：“大聪明，你填的南门？”', '眼镜反光“叮”'),
    ('S05', 6.6, 7.45, '室友B躺在枕头上，豆豆眼，脸上一排黑线，灵魂从头顶飘出来。旁边弹出一个大大的紫色“拉”字。',
     '**室友B**（有气无力）：“这把，拉完了。”', '—'),
    ('S06', 7.45, 10.35,
     '大聪明拿起手机发帖。表情三连变：先冒冷汗、手抖着打字，再皱眉下定决心，最后眼里冒火，背后橙色集中线。\n手机上是TT语音的找搭子页：'
     '标题“急！南门炸鸡运回北区8号楼”，标签“#门禁前”“#事成V你50”“#找搭子”一个个弹出来。一根手指慢动作按下“发布”，镜头推到按钮上，弹出“发布成功”。',
     '**旁白**（低沉的纪录片腔）：“此时的他还不知道，这条帖子，将惊动全校。”', '打字声；10.2秒按发布“咚”'),
    ('S07', 10.35, 11.0,
     '画面一闪，切到夜晚的校园全景，3、5、6、8、7、9号楼一字排开。以8号楼为中心荡开一圈光波，光波扫过的窗户一扇扇亮起来，有的窗口还亮起手机屏。'
     '字幕“全校：？？？”。',
     '（旁白在这里说完）', '窗户亮起一串“啵啵啵”'),
    ('S08', 11.0, 12.8,
     '【无畏契约选英雄界面】第一张卡：阿飞。田径队｜决斗｜技能：百米11秒｜位置：南门操场。他双臂秀肌肉，眼里冒火。卡片最后盖上“已锁定”，'
     '右上角TT悬浮条亮起他的头像。',
     '**阿飞**（长得猛，声音嗲）：“V我50，真的假的？”', '进房“叮”、“嗖”、锁定音效（S08–S11每张卡都一样）'),
    ('S09', 12.8, 14.6, '小K。轮滑社｜先锋｜技能：下坡不踩刹车｜位置：大坡顶。抬手一指，一脸酷。',
     '**小K**（话少，酷）：“下坡？我的主场。”', '同上'),
    ('S10', 14.6, 16.0, '老周。航模社｜控场｜技能：呼叫空投｜位置：人工湖。一手推眼镜，镜片反光，一手拿着遥控器。',
     '**老周**（平，像念说明书）：“50块，够买俩桨。”', '同上'),
    ('S11', 16.0, 17.8, '星星。天文社｜哨卫｜技能：全图视野｜位置：9号楼阳台。笑着指向镜头。',
     '**星星**（冷静）：“钱不要，鸡翅留一个。”', '同上'),
    ('S12', 17.8, 19.0,
     '大聪明。501寝室｜定位：？？？｜技能：填错地址｜位置：8号楼501。挠头傻笑，冒冷汗。背景节奏突然停掉，一只乌鸦“嘎！嘎！”飞过，'
     '锁定按钮变灰，整张卡抖一下，他的脸当场变成豆豆眼。字幕“（一只乌鸦飞过）”。',
     '—', '节奏戛然而止；乌鸦叫'),
    ('S13', 19.0, 20.6, '9号楼阳台，夜空里一颗流星划过。星星戴着红围巾，弯腰把眼睛贴上天文望远镜，头发被风吹起来。',
     '**星星**（冷静，利落）：“报点：外卖架三层，红袋子。”', '流星“叮”；行动配乐进来（128 BPM）'),
    ('S14', 20.6, 23.0,
     '望远镜视角，圆形视野加十字线。南门外卖架上摆满外卖袋，路人头顶都挂着游戏标签：“保安大爷｜中立｜别惹”“情侣｜无害｜别打扰”'
     '“流浪猫｜中立｜可撸”“外卖小哥｜已撤离”。镜头推近，红色瞄准框锁定一个红袋子，标签“大红·炸鸡桶”。\n21.6秒，阿飞从左边冲进视野，'
     '头顶标签“阿飞｜决斗”。',
     '**阿飞**（画外，中气十足）：“看见了！”', '推镜“嗡”；锁定“嘀嘀”'),
    ('S15', 23.0, 24.5,
     '校园路。阿飞拎着炸鸡蹲成起跑姿势，眼里冒火，字幕“预备——”。下一秒像子弹一样冲出去，身后拖着两道残影和一路尘土，速度线越来越密，'
     '外卖架被甩在身后。',
     '**阿飞**（边跑边喊）：“小K！坡顶！接！”', '起跑“砰”和风声；脚步声'),
    ('S16', 24.5, 26.3,
     '长椅上一对情侣，两人都是爱心眼。阿飞带着三道残影从他们面前一闪而过：女生的马尾被吹飞，男生奶茶的盖子被掀上天，落叶乱飞。'
     '两人瞬间瞪大眼睛，头顶“？！”，然后一脸懵地对视。\n右上角弹出击杀播报样式的字幕：“阿飞 运送了 炸鸡桶 800米”。',
     '（阿飞的喊声持续到这里）', '呼啸而过；播报“叮”；奶茶盖“啵”'),
    ('S17', 26.3, 27.0, '坡顶的路灯下，小K张开手等着；阿飞抱着炸鸡从左边冲过来。', '—', '脚步声'),
    ('S18', 27.0, 28.2,
     '交接棒慢镜头：路灯的光从头顶打下来，金色光点飘在空中。阿飞把袋子递出去，小K稳稳接住，两人对视一眼：阿飞从冒火变成咧嘴笑，小K从酷变成坚定。',
     '—', '史诗合唱“啊——”'),
    ('S19', 28.2, 29.3, '小K抱着炸鸡顺着大坡滑下去，身后拖着残影。过弯时压低身体漂移，轮子擦出一串火花，字幕“小K 漂移 +1”。',
     '—', '轮滑声；漂移“吱——”'),
    ('S20', 29.3, 30.0, '保安岗亭里，保安大爷正端着保温杯喝水。窗外一道黄光嗖地闪过，他的眼珠从左转到右，头顶冒出问号。',
     '—', '呼啸声；问号“啵”'),
    ('S21', 30.0, 31.5,
     '人工湖边。小K高速滑过来，发现前面是一整片湖，急刹：身体后仰，双手乱挥，满脸惊恐，脚下火花四溅。刹住以后站在岸边摇摇晃晃，头顶“……”。',
     '**星星**（画外，急）：“绕湖来不及了！”', '急刹“吱——”'),
    ('S22', 31.5, 33.0, '老周特写：推了推眼镜，镜片“唰”地反光，背后蓝色集中线。他拿出遥控器，无人机吊着红袋子缓缓升空，镜头跟着往上摇。',
     '**老周**（淡定）：“交给我。”', '眼镜反光“叮”；螺旋桨嗡嗡声'),
    ('S23', 33.0, 35.4,
     '全片最大的镜头：月光下的湖面，无人机吊着炸鸡飞过去，身后拖着一道长长的红色烟雾，像和平精英的空投。湖面有倒影，远处石拱桥上几个同学指着天。'
     '右上角弹出“老周 呼叫了 空投”。',
     '—', '螺旋桨声；播报“叮”'),
    ('S24', 35.4, 36.5, '湖边夜跑、散步的同学一起抬头，头顶冒出“！”，然后条件反射一样追着空投跑，眼睛变成星星和爱心。',
     '**路人**（几个人同时喊）：“空投！”', '一群人的脚步声'),
    ('S25', 36.5, 38.0, '阳台上，天上还挂着那道红烟。星星抬手扶额，半眯着眼，脸上一排黑线。',
     '**星星**（无奈）：“全校最大的显眼包。”', '—'),
    ('S26', 38.0, 39.0, '8号楼门口。宿管阿姨面无表情地把玻璃门往里推，眼镜一闪一闪地反光。倒计时变大变红，屏幕四周一下下闪红光，一直闪到门禁归零。',
     '—', '无畏契约爆能器的“滴……滴……滴滴滴”，越来越快；心跳声'),
    ('S27', 39.0, 40.0, '大聪明哭着冲下楼梯，面条泪往后飞，一只人字拖从脚上飞了出去。', '—', '呼啸声'),
    ('S28', 40.0, 41.0, '夜空里，红袋子拖着烟、发着光，从天上笔直掉下来。大聪明仰着头举起双手，眼睛变成星星。', '—', '渐强的风声'),
    ('S29', 41.0, 42.0, '宿舍楼门口，背后金色放射光。大聪明纵身飞扑，慢动作，在半空中接住炸鸡，炸出一个冲击星。花字“接住泼天的富贵”。',
     '—', '接住“砰”'),
    ('S30', 42.0, 43.6,
     '四宫格，字幕“同一秒，四栋楼”：8号楼的大聪明抱着炸鸡、3号楼的阿飞、6号楼的小K、7号楼的老周（手里还捏着遥控器），'
     '同时从快关上的门缝里横着飞扑进去。门关上，每格弹出“咔哒”，倒计时归零“00:00”。',
     '—', '四声“咔哒”'),
    ('S31', 43.6, 45.0, '金色放射背景，炸鸡桶弹出来，五个人的头像在四周蹦出来哈哈大笑，彩纸落下。花字“大吉大利，今晚吃鸡”。',
     '**室友B**（画外，一反常态地激动）：“这把，夯爆了！”', '胜利音效'),
    ('S32', 45.0, 46.8,
     '8号楼大厅，画面一下暗成紫色。大聪明趴在地上死死抱着炸鸡，冒冷汗。宿管阿姨低头看着他，慢悠悠喝了一口保温杯，镜片反光。'
     '顶部弹出：“宿管阿姨 使用了【凝视】，全场被硬控2秒”。说完那句话，她的嘴角慢慢翘了起来。',
     '**宿管阿姨**（先停顿，慢）：“……几个人吃啊？”', '低沉的嗡鸣；喝水“吸溜”'),
    ('S33', 46.8, 48.2,
     '501寝室，炸鸡开吃。室友A举手欢呼，室友B流口水。大聪明先挑一个鸡翅放进小纸盒，盒子上贴着“星星的”。室友C伸手想拿，'
     '被大聪明一巴掌拍开，“啪！”，室友C当场哭出来。',
     '—', '欢快的马林巴；“啪”'),
    ('S34', 48.2, 50.6,
     '大聪明拿着手机转账：转给TT语音组队的4位搭子，每人¥50，共¥200。按下“确认转账”，弹出“余额不足｜零钱 ¥3.50”。'
     '\n画面瞬间褪色，字幕“空气突然安静”，一只乌鸦“嘎！”飞过，大聪明当场石化，身上裂开几道缝。',
     '**大聪明**（越说越小声）：“说好的V你们50……”', '弹窗“咚”；乌鸦叫；石头裂开声'),
    ('S35', 50.6, 53.1,
     'TT语音房间“南门炸鸡运输队”，6个麦位：大聪明、阿飞、小K、老周、星星，还有一个一直灰着的“神秘人”。大聪明的头像是石化的豆豆眼，'
     '头顶“余额 ¥3.50”。阿飞的麦位亮起来说话，喊“包的！”时所有人的麦位一起亮。',
     '**阿飞**（先愣一下，然后豪爽）：“……那我们V你50，下周四再来！”\n**全员**（齐声）：“包的！”', '欢快的配乐'),
    ('S36', 53.1, 55.6,
     '四张“收款 +50”一张接一张飞向大聪明，余额涨到¥203.50，他的头像先是一愣，然后变成感动的泪眼。一直灰着的“神秘人”翻了个面亮起来：'
     '8号楼·宿管阿姨，冲镜头眨眼。最后一张“收款 +50”从她那里飞过来。',
     '**宿管阿姨**（慢悠悠，带笑）：“阿姨也V你50，鸡腿留一个。”', '四声“叮！收款”；头像翻面“嗖”'),
    ('S37', 55.6, 57.4, '金光一闪，大字“收款合计：250元”。切回寝室：三个室友齐刷刷扭头冲大聪明大喊，大聪明一边感动一边哭，头顶弹出红色的“250”。',
     '**三个室友**（齐声，憋不住笑）：“二百五！”', '“咚”'),
    ('S38', 57.4, 60.0,
     '片尾合影：8号楼前放起烟花，所有人站成一排。大聪明把炸鸡桶举过头顶大笑，阿飞秀肌肉，小K比大拇指，老周推眼镜，星星啃鸡翅，'
     '宿管阿姨拿着鸡腿眨眼，三个室友、保安大爷和那对情侣也在，彩纸飘落。\n字幕：一个人很难吃鸡，一群人就行。在TT语音，永远有人并肩相伴。'
     '右上角放TT语音Logo。',
     '所有人的笑声', '烟花“啵啵”；温暖的收尾和弦'),
]

DIRECTION = {
    'rider': '电话音，大大咧咧', 'dacong1': '一急就破音', 'roomA1': '推着眼镜，慢悠悠', 'roomB1': '有气无力', 'narr': '低沉的纪录片腔',
    'xing1': '冷静，利落', 'afei1': '画外，中气十足', 'afei2': '边跑边喊', 'xing2': '画外，急', 'zhou1': '淡定', 'crowd': '几个人同时喊',
    'xing3': '扶额，无奈', 'roomB2': '画外，一反常态地激动', 'suguan1': '先停顿，慢', 'dacong2': '越说越小声',
    'afei3': '先愣一下，然后豪爽', 'all1': '齐声', 'suguan2': '慢悠悠，带笑', 'room3': '齐声，憋不住笑', 'laugh': '所有人一起大笑',
    'afei': '长得猛，声音嗲，反差越大越好笑', 'xiaok': '话少，酷', 'laozhou': '平，像在念说明书', 'xingxing': '冷静',
}

GAME = [
    ('选英雄界面、“锁定”', '无畏契约', 'S08–S12：四个陌生人进房间，每人一张英雄卡'),
    ('英雄定位：决斗、先锋、控场、哨卫', '无畏契约', '英雄卡上。决斗负责冲，先锋负责开路，控场负责控地形，哨卫负责守和盯'),
    ('爆能器倒计时的滴滴声', '无畏契约', 'S26–S30：宿管关门到门禁归零'),
    ('大红', '三角洲行动', 'S14：炸鸡桶的标签。大红是最值钱的那类物资'),
    ('四排', '和平精英', 'S02：501四个人等着炸鸡开四排，白板上写着“每晚十点·四排”'),
    ('空投', '和平精英', 'S23–S24：无人机吊着炸鸡、拖着红烟飞过湖面，路人条件反射追着跑'),
    ('吃鸡', '和平精英', 'S31：“大吉大利，今晚吃鸡”，这次是真的吃上了鸡'),
    ('报点、击杀播报、头顶标签', '射击游戏通用', 'S13–S14：星星报点，路人头顶的标签；S16、S23：右上角的运送播报'),
]

MEMES = [
    ('V我50', '“转我50块”。来自“疯狂星期四”段子：先编一个很长的故事，最后一句要50块', '帖子“事成V你50”、阿飞入队、结账反转、收款合计250'),
    ('此时的他还不知道', '纪录片和短剧最常见的旁白腔', 'S06：发帖那一刻'),
    ('拉完了／夯爆了', '2026年流行的评价：“拉”是很差，“夯”是顶级', 'S05“这把，拉完了”；S31“这把，夯爆了！”'),
    ('显眼包', '特别爱出风头、走到哪都惹眼的人', 'S25：星星吐槽拖着红烟飞过湖面的老周'),
    ('接住泼天的富贵', '好运从天而降，稳稳接住', 'S29：大聪明接住从天上掉下来的炸鸡'),
    ('硬控', '被定住动不了', 'S32：宿管阿姨“使用了【凝视】”'),
    ('包的', '“包在我身上”', 'S35：全员答应下周四再来'),
    ('大聪明', '反话，说一个人干了件蠢事', '主角外号'),
    ('空气突然安静', '场面一下子尴尬', 'S34：余额3.50那一刻'),
    ('裂开', '心态崩了。画面上直接画成石化、裂缝', 'S34：大聪明当场石化裂开'),
    ('二百五', '说人傻的老话', 'S37：收款合计正好250'),
]
MEME_SOURCE = ('中国社会科学网《从“夯爆了”到“文字失语症”》（2026-10-30）', 'https://m.163.com/dy/article/LAGFR9OI051495OJ.html')

CALLBACKS = [
    ('帖子“事成V你50”（S06）', '余额3.50 → 大家反过来V他50 → 收款合计250 → “二百五！”（S34–S37）', 'V我50贯穿全片，最后变成最大的笑点'),
    ('英雄卡“技能：填错地址”（S12）', '开头把炸鸡填到了南门（S01–S02）', '主角自己就是事故源头'),
    ('“这把，拉完了”（S05）', '“这把，夯爆了！”（S31）', '从拉到夯'),
    ('旁白“将惊动全校”（S06）', '全校的窗户一扇扇亮起（S07）；路人追着空投跑（S24）', '旁白说到做到'),
    ('星星“钱不要，鸡翅留一个”（S11）', '第一个鸡翅装进贴着“星星的”的盒子（S33）；片尾她啃着鸡翅（S38）', '唯一不要钱的人，第一个鸡翅归她'),
    ('老周“50块，够买俩桨”（S10）', '无人机吊着炸鸡空投过湖（S22–S23）', '理工男的高光时刻'),
    ('悬浮条里一直灰着的“神秘人”（S08起）', 'S36亮起：“8号楼·宿管阿姨”', '埋了大半部片的彩蛋'),
    ('宿管阿姨准点锁门（S26）、【凝视】（S32）', '“阿姨也V你50，鸡腿留一个”（S36）；片尾拿着鸡腿眨眼（S38）', '最后的“boss”也成了搭子'),
    ('和平精英的“吃鸡”（S31）', '真的吃上了炸鸡（S33）；结尾“一个人很难吃鸡，一群人就行”', '双关'),
    ('阿飞号码布上的“50”', '不解释', '给细心观众的彩蛋'),
]

# ================================================================ Word 工具
def set_rfonts(rpr):
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.insert(0, rfonts)
    for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        if rfonts.get(qn(a)) is not None:
            del rfonts.attrib[qn(a)]
    for a in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rfonts.set(qn(a), FONT_LATIN)
    rfonts.set(qn('w:eastAsia'), FONT_CN)


PPR_AFTER_PBDR = ('w:shd', 'w:tabs', 'w:suppressAutoHyphens', 'w:kinsoku', 'w:wordWrap', 'w:overflowPunct', 'w:topLinePunct',
                  'w:autoSpaceDE', 'w:autoSpaceDN', 'w:bidi', 'w:adjustRightInd', 'w:snapToGrid', 'w:spacing', 'w:ind',
                  'w:contextualSpacing', 'w:mirrorIndents', 'w:suppressOverlap', 'w:jc', 'w:textDirection', 'w:textAlignment',
                  'w:textboxTightWrap', 'w:outlineLvl', 'w:divId', 'w:cnfStyle', 'w:rPr', 'w:sectPr', 'w:pPrChange')


def setup_styles(doc):
    st = doc.styles['Normal']
    st.font.size = Pt(10.5)
    st.font.color.rgb = DARK
    rpr = st.element.get_or_add_rPr()
    set_rfonts(rpr)
    lang = rpr.find(qn('w:lang'))
    if lang is None:
        lang = OxmlElement('w:lang')
        rpr.append(lang)
    lang.set(qn('w:val'), 'en-US')
    lang.set(qn('w:eastAsia'), 'zh-CN')
    pf = st.paragraph_format
    pf.space_after = Pt(4)
    pf.line_spacing = 1.3
    for name, size, color, before, after in (('Heading 1', 15, DARK, 16, 8), ('Heading 2', 12, RED, 10, 4)):
        s = doc.styles[name]
        s.font.size = Pt(size)
        s.font.bold = True
        s.font.italic = False
        s.font.color.rgb = color
        set_rfonts(s.element.get_or_add_rPr())
        s.paragraph_format.space_before = Pt(before)
        s.paragraph_format.space_after = Pt(after)
        s.paragraph_format.keep_with_next = True
        s.paragraph_format.line_spacing = 1.2
        if name == 'Heading 1':
            ppr = s.element.get_or_add_pPr()
            pbdr = OxmlElement('w:pBdr')
            bottom = OxmlElement('w:bottom')
            for k, v in (('w:val', 'single'), ('w:sz', '8'), ('w:space', '4'), ('w:color', 'C0392B')):
                bottom.set(qn(k), v)
            pbdr.append(bottom)
            ppr.insert_element_before(pbdr, *PPR_AFTER_PBDR)


def add_rich(par, text, size=None, color=None, bold=False):
    """**粗体**，换行用 \\n。"""
    for part in re.split(r'(\*\*.+?\*\*)', text):
        if not part:
            continue
        b = bold
        if part.startswith('**') and part.endswith('**'):
            part, b = part[2:-2], True
        for i, line in enumerate(part.split('\n')):
            if i:
                par.add_run().add_break()
            if line:
                r = par.add_run(line)
                r.bold = b
                if size:
                    r.font.size = Pt(size)
                if color is not None:
                    r.font.color.rgb = color


def para(doc, text, size=None, color=None, bold=False, align=None, before=0, after=4, hang=None):
    p = doc.add_paragraph()
    add_rich(p, text, size, color, bold)
    pf = p.paragraph_format
    pf.space_before, pf.space_after = Pt(before), Pt(after)
    if align is not None:
        p.alignment = align
    if hang:
        pf.left_indent, pf.first_line_indent = Cm(hang), Cm(-hang)
    return p


def numbered(doc, items, start=1):
    for i, t in enumerate(items, start):
        para(doc, f'{i}. {t}', hang=0.6, after=3)


def add_field(par, instr, size=8, color=GRAY):
    r = par.add_run()
    r.font.size = Pt(size)
    r.font.color.rgb = color
    els = []
    for kind in ('begin', None, 'separate', 'text', 'end'):
        if kind in ('begin', 'separate', 'end'):
            e = OxmlElement('w:fldChar')
            e.set(qn('w:fldCharType'), kind)
        elif kind is None:
            e = OxmlElement('w:instrText')
            e.set(qn('xml:space'), 'preserve')
            e.text = f' {instr} '
        else:
            e = OxmlElement('w:t')
            e.text = '1'
        els.append(e)
    for e in els:
        r._r.append(e)


def add_link(par, url, text, size=None):
    r_id = par.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement('w:hyperlink')
    h.set(qn('r:id'), r_id)
    r = OxmlElement('w:r')
    rpr = OxmlElement('w:rPr')
    c = OxmlElement('w:color')
    c.set(qn('w:val'), '1F5FBF')
    rpr.append(c)
    if size:
        for tag in ('w:sz', 'w:szCs'):
            sz = OxmlElement(tag)
            sz.set(qn('w:val'), str(int(size * 2)))
            rpr.append(sz)
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rpr.append(u)
    r.append(rpr)
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)
    h.append(r)
    par._p.append(h)


def shade(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    old = tcpr.find(qn('w:shd'))
    if old is not None:
        tcpr.remove(old)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    tcpr.insert_element_before(shd, 'w:noWrap', 'w:tcMar', 'w:textDirection', 'w:tcFitText', 'w:vAlign', 'w:hideMark',
                               'w:headers', 'w:cellIns', 'w:cellDel', 'w:cellMerge', 'w:tcPrChange')


def row_flags(row, header=False):
    trpr = row._tr.get_or_add_trPr()
    cs = OxmlElement('w:cantSplit')
    trpr.append(cs)
    if header:
        th = OxmlElement('w:tblHeader')
        trpr.append(th)


def table_look(t):
    tblpr = t._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{side}')
        for k, v in (('w:val', 'single'), ('w:sz', '4'), ('w:space', '0'), ('w:color', BORDER)):
            e.set(qn(k), v)
        borders.append(e)
    tblpr.insert_element_before(borders, 'w:shd', 'w:tblLayout', 'w:tblCellMar', 'w:tblLook', 'w:tblCaption', 'w:tblDescription')
    mar = OxmlElement('w:tblCellMar')
    for side, v in (('top', 50), ('left', 85), ('bottom', 50), ('right', 85)):
        e = OxmlElement(f'w:{side}')
        e.set(qn('w:w'), str(v))
        e.set(qn('w:type'), 'dxa')
        mar.append(e)
    tblpr.insert_element_before(mar, 'w:tblLook', 'w:tblCaption', 'w:tblDescription')


def table(doc, headers, rows, widths, size=9.5, zebra=False, center_cols=()):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    table_look(t)
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(w)
    hdr = t.rows[0]
    row_flags(hdr, header=True)
    for i, h in enumerate(headers):
        c = hdr.cells[i]
        c.width = Cm(widths[i])
        shade(c, HEAD_FILL)
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.alignment = CENTER
        add_rich(p, h, size, bold=True)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        row_flags(t.rows[-1])
        for i, val in enumerate(row):
            c = cells[i]
            c.width = Cm(widths[i])
            if zebra and ri % 2 == 1:
                shade(c, ZEBRA_FILL)
            p = c.paragraphs[0]
            pf = p.paragraph_format
            pf.space_after = Pt(0)
            pf.line_spacing = 1.2
            add_rich(p, val, size)
            if i in center_cols:
                p.alignment = CENTER
                c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    return t


def page_setup(sec, landscape=False):
    if landscape:
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
        sec.left_margin = sec.right_margin = Cm(1.5)
        sec.top_margin, sec.bottom_margin = Cm(1.7), Cm(1.5)
    else:
        sec.orientation = WD_ORIENT.PORTRAIT
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
        sec.left_margin = sec.right_margin = Cm(2.0)
        sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(1.8)
    sec.header_distance = sec.footer_distance = Cm(0.8)


# ================================================================ 数据检查
def check_shots():
    bounds = set()
    for a, b, *_ in R2.SHOTS:
        bounds |= {round(a, 3), round(min(b, 60.0), 3)}
    bounds |= {round(11.0 + s, 3) for s in hero.STARTS}
    prev = 0.0
    for code, t0, t1, *_ in SHOT_ROWS:
        assert abs(t0 - prev) < 1e-6, f'{code} 没接上前一镜：{t0} != {prev}'
        assert round(t0, 3) in bounds and round(t1, 3) in bounds, f'{code} 的时间 {t0}～{t1} 和样片对不上'
        prev = t1
    assert abs(prev - 60.0) < 1e-6, f'镜头加起来是 {prev} 秒'


def shot_of(t):
    for code, t0, t1, *_ in SHOT_ROWS:
        if t0 <= t < t1:
            return code
    return 'S38'


def dialogue_rows():
    voices = SA.build_voices()
    rows = []
    for s, e, ln in SA.line_windows(voices):
        who = ln['who'] or '全员'
        text = ln.get('show', ln['text'])
        rows.append((s, e, who, text, DIRECTION[ln['key']]))
    for k, c in enumerate(hero.CARDS[:4]):
        x, _ = hero.tts_fit(c, c['dur'] - hero.VOICE_LEAD - 0.02)
        s = 11.0 + hero.STARTS[k] + hero.VOICE_LEAD
        rows.append((s, s + len(x) / hero.SR, c['name'], c['line'], DIRECTION[c['key']]))
    rows.sort(key=lambda r: r[0])
    return [(shot_of(s), f'{s:.1f}～{e:.1f}', who, text, how) for s, e, who, text, how in rows]


# ================================================================ 拼文档
def sec_fmt(x):
    s = f'{x:.2f}'.rstrip('0')
    return s + '0' if s.endswith('.') else s


def build():
    check_shots()
    dlg = dialogue_rows()

    doc = Document()
    setup_styles(doc)
    cp = doc.core_properties
    now = datetime.datetime.now()
    cp.title, cp.subject = '《事成V你50》剧本', 'TT语音「你与搭子的群像故事」参赛短片'
    cp.author = cp.last_modified_by = ''
    cp.keywords, cp.comments = 'TT语音, 事成V你50, 剧本, 分镜', ''
    cp.created = cp.modified = now
    cp.revision = 1

    sec = doc.sections[0]
    page_setup(sec)
    hp = sec.header.paragraphs[0]
    hp.alignment = RIGHT
    add_rich(hp, '《事成V你50》剧本｜TT语音「你与搭子的群像故事」参赛短片', 8, GRAY)
    fp = sec.footer.paragraphs[0]
    fp.alignment = CENTER
    add_rich(fp, '第 ', 8, GRAY)
    add_field(fp, 'PAGE')
    add_rich(fp, ' 页 / 共 ', 8, GRAY)
    add_field(fp, 'NUMPAGES')
    add_rich(fp, ' 页', 8, GRAY)

    para(doc, '《事成V你50》', 26, RED, True, CENTER, before=4, after=2)
    para(doc, 'TT语音「你与搭子的群像故事」参赛短片剧本', 13, DARK, False, CENTER, after=2)
    para(doc, '60秒 · 16:9横屏 · 校园放飞版', 9.5, GRAY, False, CENTER, after=10)

    doc.add_heading('一、项目信息', 1)
    table(doc, ['项目', '内容'], INFO, [2.6, 14.4])

    doc.add_heading('二、故事梗概', 1)
    for s in SUMMARY:
        para(doc, s, after=5)
    doc.add_heading('节奏结构', 2)
    table(doc, ['段落', '时间', '镜号', '内容'], STRUCTURE, [2.2, 2.0, 2.0, 10.8], center_cols=(0, 1, 2))

    doc.add_heading('三、这一版的看点', 1)
    numbered(doc, HIGHLIGHTS)

    doc.add_heading('四、人物', 1)
    para(doc, '只有大聪明和三个室友住501。阿飞、小K、老周、星星来自四个社团，住在别的楼，和大聪明互不认识，是看到TT语音的找搭子帖子才进的房间。', after=6)
    table(doc, ['人物', '是谁', '造型', '声音', '片中作用和招牌表情'], CAST, [1.6, 3.4, 4.6, 2.7, 4.7], size=9)

    # ---- 横版：分镜脚本
    sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
    page_setup(sec2, landscape=True)
    doc.add_heading('五、分镜脚本（38个镜头）', 1)
    para(doc, '时间单位是秒。帖子、倒计时、标签、播报、余额、字幕这些字都在剪辑时加。', 9, GRAY, after=6)
    rows = []
    for code, t0, t1, pic, line, sfx in SHOT_ROWS:
        rows.append((f'**{code}**', f'{sec_fmt(t0)}～{sec_fmt(t1)}', pic, line, sfx))
    table(doc, ['镜号', '时间', '画面', '台词', '音效'], rows, [1.2, 1.8, 12.6, 6.6, 4.5], size=9, zebra=True, center_cols=(0, 1))

    # ---- 竖版：其余部分
    sec3 = doc.add_section(WD_SECTION.NEW_PAGE)
    page_setup(sec3)
    doc.add_heading('六、台词表', 1)
    para(doc, '时间单位是秒。配音后按台词实际长度微调，总长保持60秒。', 9, GRAY, after=6)
    table(doc, ['镜号', '时间', '角色', '台词', '怎么说'], dlg, [1.3, 2.5, 2.1, 6.6, 4.5], size=9.5, zebra=True, center_cols=(0, 1))

    doc.add_heading('七、游戏元素', 1)
    table(doc, ['元素', '来自', '出现在'], GAME, [4.6, 2.4, 10.0])

    doc.add_heading('八、热梗', 1)
    table(doc, ['梗', '意思', '出现在'], MEMES, [2.8, 7.2, 7.0])
    p = para(doc, '“夯／拉”的来源：', 9, GRAY, before=4)
    add_link(p, MEME_SOURCE[1], MEME_SOURCE[0], size=9)

    doc.add_heading('九、前后呼应', 1)
    table(doc, ['前面', '后面', '作用'], CALLBACKS, [5.0, 7.4, 4.6])

    doc.save(OUT)
    print('完成：', OUT)


if __name__ == '__main__':
    build()
