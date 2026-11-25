"""Original, native 1080p motion-graphics renderer for the drawing effect.

Art direction: an ink-and-light atelier with tactile paper, sculpted objects,
an adult painter, and editorial typography. All frames and sounds are coded.
Run `python render.py --all --ffmpeg ffmpeg` after replacing the earlier draft.
"""
from __future__ import annotations

import argparse
import math
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
W, H, FPS = 1920, 1080, 30
BPM = 128
BEAT = 60 / BPM
FRAMES = 2250
INK = (9, 18, 29)
PAPER = (234, 223, 198)
WHITE = (251, 247, 232)
SAND = (185, 181, 158)
GOLD = (249, 188, 87)
TEAL = (96, 212, 197)
RED = (204, 83, 73)

FONT_CANDIDATES = [
    ROOT / "assets" / "NotoSansSC-VF.ttf",
    Path("C:/Windows/Fonts/NotoSansSC-VF.ttf"),
    Path("C:/Windows/Fonts/msyhbd.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"),
]
FONT_PATH = next((p for p in FONT_CANDIDATES if p.exists()), None)
if not FONT_PATH:
    raise RuntimeError("Install Noto Sans CJK or provide a font in assets/")


@lru_cache(maxsize=60)
def font(size):
    return ImageFont.truetype(str(FONT_PATH), size)


def text(d, x, y, s, size, color=WHITE, anchor="la", width=None):
    f=font(size)
    bb=d.textbbox((x,y),s,font=f,anchor=anchor)
    if bb[0]<0 or bb[1]<0 or bb[2]>d.im.size[0] or bb[3]>d.im.size[1]:
        raise ValueError(f"Text clipped: {s!r} at {bb}")
    if width and bb[2]-bb[0]>width:
        raise ValueError(f"Text too wide: {s!r} at {bb}")
    d.text((x,y),s,font=f,fill=color,anchor=anchor)


def round_rect(d,box,r,fill,outline=None,w=1):
    d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=w)


def path_points(cx,cy,rx,ry,n=160):
    # A hand-drawn apple rather than a generic stock icon.
    pts=[]
    for i in range(n+1):
        a=2*math.pi*i/n
        r=1-.15*math.cos(2*a)
        pts.append((int(cx+rx*math.sin(a)*r),int(cy+ry*math.cos(a)*r)))
    return pts


def apple_sketch(im,cx,cy,scale=1,progress=1,color=(59,109,109),stroke=9):
    d=ImageDraw.Draw(im)
    pts=path_points(cx,cy,int(100*scale),int(102*scale))
    p=max(.025,min(1,progress))
    n=max(3,int(len(pts)*min(p/.78,1)))
    d.line(pts[:n],fill=color,width=int(stroke*scale),joint="curve")
    if p>.80:
        d.line([(cx,cy-int(95*scale)),(cx+int(15*scale),cy-int(151*scale)),(cx+int(56*scale),cy-int(157*scale))],fill=color,width=int(stroke*.7*scale),joint="curve")
    if p>.92:
        d.ellipse((cx+int(30*scale),cy-int(166*scale),cx+int(99*scale),cy-int(135*scale)),fill=color)


def apple_object(im,cx,cy,scale=1):
    paste_object(im,0,cx,cy,int(250*scale))


def key_object(im,cx,cy,scale=1):
    paste_object(im,1,cx,cy,int(300*scale))


def umbrella_object(im,cx,cy,scale=1):
    paste_object(im,2,cx,cy,int(330*scale))


@lru_cache(maxsize=12)
def object_asset(index,height):
    src=Image.open(ROOT/"assets"/"objects_clean.png").convert("RGBA")
    cw=src.width//3
    src=src.crop((index*cw,0,(index+1)*cw,src.height))
    mask=src.getchannel("A").point(lambda a:255 if a>25 else 0)
    bb=mask.getbbox()
    if not bb:raise RuntimeError(f"Object {index} has no alpha")
    src=src.crop(bb)
    width=round(src.width*height/src.height)
    return src.resize((width,height),Image.Resampling.LANCZOS)


def paste_object(im,index,cx,cy,height):
    asset=object_asset(index,height)
    im.alpha_composite(asset,(round(cx-asset.width/2),round(cy-asset.height/2)))


def shadow(im,box,blur=30,alpha=85):
    layer=Image.new("RGBA",im.size)
    d=ImageDraw.Draw(layer)
    d.ellipse(box,fill=(0,0,0,alpha))
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


@lru_cache(maxsize=1)
def backdrop():
    im=Image.open(ROOT/"assets"/"atelier_background.png").convert("RGBA")
    im=im.resize((W,H),Image.Resampling.LANCZOS)
    # Keep generated material detail, while reserving contrast for the type.
    veil=Image.new("RGBA",(W,H),(3,11,18,64))
    im=Image.alpha_composite(im,veil)
    d=ImageDraw.Draw(im)
    text(d,112,65,"VIBE 知识大赏",34,GOLD)
    d.line((112,107,371,107),fill=GOLD,width=3)
    return im


def title(d,cn,en,section=None):
    if section:
        text(d,115,161,section,34,GOLD)
        d.line((115,208,235,208),fill=GOLD,width=4)
    text(d,112,238,cn,106,WHITE,width=1540)
    text(d,116,375,en,43,SAND,width=1590)


def paper_board(im,box,accent=GOLD):
    x0,y0,x1,y1=box
    shadow(im,(x0+40,y1-5,x1+40,y1+77),27,95)
    d=ImageDraw.Draw(im)
    round_rect(d,(x0-12,y0-12,x1+14,y1+19),35,(68,66,58),(137,115,77),4)
    round_rect(d,(x0,y0,x1,y1),29,PAPER,(248,229,188),6)
    d.line((x0+35,y0+35,x1-45,y0+35),fill=(199,185,153),width=2)
    d.line((x0+40,y1-38,x1-40,y1-38),fill=(199,185,153),width=2)
    for x in (x0+52,x1-52):
        d.ellipse((x-12,y0-15,x+12,y0+9),fill=(116,89,59),outline=(240,205,129),width=3)
    d.polygon([(x1-65,y0),(x1,y0),(x1,y0+65)],fill=(207,193,166))
    return box


@lru_cache(maxsize=8)
def artist_asset(pose,height):
    name="adult_artist.png" if pose=="paint" else "adult_artist_point.png"
    src=Image.open(ROOT/"assets"/name).convert("RGBA")
    mask=src.getchannel("A").point(lambda a:255 if a>10 else 0)
    bb=mask.getbbox()
    if not bb:raise RuntimeError(f"Character {name} has no alpha")
    src=src.crop(bb)
    width=round(src.width*height/src.height)
    return src.resize((width,height),Image.Resampling.LANCZOS)


def paste_artist(im,t,x,foot=916,pose="paint",scale=1):
    height=round(550*scale)
    asset=artist_asset(pose,height)
    px=round(x-asset.width/2+math.sin(t*1.2)*2)
    py=round(foot+80-height)
    d=ImageDraw.Draw(im)
    d.ellipse((x-90,foot+71,x+90,foot+96),fill=(5,11,16))
    im.alpha_composite(asset,(px,py))


def result_type(d,draw_pct=True):
    text(d,125,620,"画",48,TEAL)
    text(d,125,667,"23%",125,TEAL)
    text(d,433,620,"写",48,SAND)
    text(d,433,667,"14%",125,SAND)
    d.line((124,823,740,823),fill=(108,111,100),width=3)
    text(d,125,844,"66 个易画词 · 短时自由回忆",37,WHITE)


@lru_cache(maxsize=36)
def still(section,state):
    im=backdrop().copy()
    d=ImageDraw.Draw(im)
    if section==0:
        # Question and physical workspace dominate. Results live on dark floor, not UI cards.
        text(d,114,211,"画一笔，",115,WHITE)
        text(d,114,342,"真的更好记？",115,GOLD)
        text(d,118,500,"Draw it, or write it?",45,SAND)
        paper_board(im,(1060,245,1780,902))
        if state>=1:
            round_rect(d,(139,595,720,715),18,(48,57,57),(182,149,94),3)
            text(d,171,607,"每个词，只有 4 秒",57,WHITE)
            text(d,174,675,"4 seconds per word",35,SAND)
        if state>=2:
            # The two percentages belong to Experiment 7's two pure-list groups.
            d.rectangle((108,570,811,895),fill=(15,24,33))
            result_type(d)
        if state>=3:
            text(d,125,920,"画过的词，回忆更多",44,GOLD)
        if state>=4:
            text(d,125,1000,"Wammes et al., 2016 · Exp. 7",36,SAND)
    elif section==1:
        title(d,"先自己画，再试着想","Draw it yourself, then recall it.","方法 / THE METHOD")
        paper_board(im,(910,470,1680,872))
        apple_object(im,1160,692,1.05)
        if state>=1: text(d,170,602,"挑词",65,WHITE)
        if state>=2: text(d,170,695,"简画",65,GOLD)
        if state>=3: text(d,170,788,"回想",65,TEAL)
        if state>=4: text(d,1100,955,"论文测试的是易画的单词",39,SAND,anchor="ma")
    elif section==2:
        title(d,"先挑能画的词","Start with words you can picture.","01 / CHOOSE")
        # Each life-size object sits on a sculpted plinth; no rectangular flashcards.
        labs=[("苹果","APPLE",830),("钥匙","KEY",1235),("雨伞","UMBRELLA",1630)]
        for i,(cn,en,cx) in enumerate(labs):
            if state<i+1:continue
            d.ellipse((cx-155,840,cx+155,891),fill=(9,16,23))
            d.polygon([(cx-135,834),(cx+135,834),(cx+100,905),(cx-100,905)],fill=(73,69,62),outline=(154,126,82))
            d.line((cx-121,842,cx+121,842),fill=(218,176,102),width=5)
            if i==0:apple_object(im,cx,680,1.22)
            if i==1:key_object(im,cx-20,690,1.15)
            if i==2:umbrella_object(im,cx,692,1.11)
            text(d,cx,943,cn,54,WHITE,anchor="mm")
            text(d,cx,999,en,34,SAND,anchor="mm")
        if state>=4:
            d.arc((677,494,985,848),200,502,fill=GOLD,width=9)
            text(d,827,553,"选它",43,GOLD,anchor="mm")
            text(d,827,1001,"例：苹果、钥匙、雨伞",38,TEAL,anchor="mm")
    elif section==3:
        title(d,"只画关键特征","Sketch the identifying features.","02 / SKETCH")
        paper_board(im,(770,440,1780,900))
        apple_object(im,1050,679,1.15)
        d.line((1218,677,1346,677),fill=(161,141,109),width=7)
        d.polygon([(1336,655),(1367,677),(1336,699)],fill=(161,141,109))
        if state>=1:
            text(d,1285,804,"圆 + 叶 = 苹果",52,(50,86,85))
        if state>=2:
            text(d,1713,973,"实验 6、7：每词 4 秒",35,SAND,anchor="ra")
    elif section==4:
        title(d,"遮住图，自己想","Hide the sketch. Recall the word.","03 / RECALL")
        paper_board(im,(780,440,1780,905))
        apple_sketch(im,1270,677,1.15,1,(50,95,94),8)
        if state>=2:
            round_rect(d,(899,682,1675,803),23,(29,57,59),(131,190,163),4)
            text(d,1287,709,"答案：苹果 / APPLE",68,WHITE,anchor="ma")
        if state>=3:
            text(d,1784,982,"回想练习是实用延伸；论文测的是回忆成绩",35,SAND,anchor="ra")
    else:
        title(d,"画一笔，再回想","Draw a word. Then recall it.","照着做 / IN PRACTICE")
        paper_board(im,(712,440,1790,930))
        labels=[("挑词","CHOOSE",890),("简画","SKETCH",1250),("回想","RECALL",1610)]
        for i,(cn,en,cx) in enumerate(labels):
            if state<i+1:continue
            if i==0:apple_object(im,cx,628,.69)
            elif i==1:apple_sketch(im,cx,640,.72,1,(52,100,100),9)
            else:
                d.ellipse((cx-70,565,cx+70,707),outline=(51,99,101),width=8)
                text(d,cx,620,"?",80,(52,100,100),anchor="mm")
            text(d,cx,776,cn,56,(45,76,77),anchor="mm")
            text(d,cx,840,en,35,(94,106,101),anchor="mm")
        if state>=4:
            d.line((800,885,1695,885),fill=(145,135,113),width=3)
            text(d,1247,957,"实验 7：画 23%   /   写 14%",52,TEAL,anchor="ma")
        if state>=5:
            text(d,1247,1020,"证据范围：易画单词 · 短时自由回忆",36,SAND,anchor="ma")
    return im


def scene_frame(t):
    b=t/BEAT
    if b<16:
        state=sum(b>=v for v in (4.5,8.5,10.5,13))
        im=still(0,state).copy()
        apple_sketch(im,1418,591,1.35,max(.08,min(1,t/1.92)),(62,105,99),9)
        paste_artist(im,t,835,917,"paint",1.0)
    elif b<32:
        state=sum(b>=v for v in (17,20,23,26.5))
        im=still(1,state).copy()
        paste_artist(im,t,610,918,"point",1.02)
    elif b<64:
        state=sum(b>=v for v in (32,38,44,54))
        im=still(2,state).copy()
        x=260+min(1,(t-15)/12)*265
        paste_artist(im,t,x,916,"point",1.0)
    elif b<96:
        state=sum(b>=v for v in (82,89))
        im=still(3,state).copy()
        apple_sketch(im,1540,669,.93,max(.04,min(1,(b-65)/17)),(51,101,101),9)
        paste_artist(im,t,565,918,"paint",1.02)
    elif b<128:
        state=0 if b<113 else 1 if b<120 else 3
        # Text on the curtain is drawn after it slides over the page.
        im=still(4,0).copy()
        if b>=103:
            d=ImageDraw.Draw(im)
            v=min(1,(b-103)/10)
            x0=int(1770-902*v)
            round_rect(d,(x0,462,1780,878),20,(32,47,56),(155,141,108),5)
            for x in range(x0+48,1740,90):
                d.line((x,472,x,870),fill=(43,60,67),width=3)
        if state>=1:
            d=ImageDraw.Draw(im)
            round_rect(d,(899,682,1675,803),23,(29,57,59),(131,190,163),4)
            text(d,1287,709,"答案：苹果 / APPLE",68,WHITE,anchor="ma")
        if state>=3:
            d=ImageDraw.Draw(im)
            text(d,1784,982,"回想练习是实用延伸；论文测的是回忆成绩",35,SAND,anchor="ra")
        paste_artist(im,t,548,918,"point",1.02)
    else:
        state=sum(b>=v for v in (130,135,140,144,150))
        im=still(5,state).copy()
        paste_artist(im,t,497,919,"point",1.0)
    return im


def audio_file():
    """Deterministic non-musical effects, each aligned to a visual beat."""
    sr=48000
    a=np.zeros(sr*75,dtype=np.float64)
    cues=[(0,"hit"),(4.5,"tick"),(8.5,"chime"),(10.5,"pop"),(13,"pop"),
          (16,"whoosh"),(17,"pop"),(20,"pop"),(23,"pop"),(26.5,"chime"),
          (32,"whoosh"),(38,"pop"),(44,"pop"),(54,"chime"),
          (64,"whoosh"),(66,"draw"),(74,"draw"),(82,"pop"),(89,"tick"),
          (96,"whoosh"),(103,"slide"),(113,"chime"),(120,"pop"),
          (128,"whoosh"),(130,"pop"),(135,"pop"),(140,"pop"),(144,"chime"),(150,"pop")]
    rng=np.random.default_rng(20261109)
    for beat,kind in cues:
        start=int(round(beat*BEAT*sr))
        dur={"hit":.30,"whoosh":.22,"chime":.34,"tick":.09,"pop":.14,"draw":.18,"slide":.24}[kind]
        n=int(dur*sr);tt=np.arange(n)/sr
        env=np.exp(-tt*({"hit":13,"chime":9,"whoosh":15,"tick":28,"pop":23,"draw":22,"slide":16}[kind]))
        if kind=="hit":sig=np.sin(2*np.pi*(80*tt+150*tt*tt))*env+.30*rng.normal(size=n)*env
        elif kind=="whoosh":sig=rng.normal(size=n)*env*.22
        elif kind=="chime":sig=(np.sin(2*np.pi*880*tt)+.45*np.sin(2*np.pi*1320*tt))*env*.25
        elif kind=="tick":sig=rng.normal(size=n)*env*.16
        elif kind=="pop":sig=np.sin(2*np.pi*(420+beat*2)*tt)*env*.21
        elif kind=="draw":sig=rng.normal(size=n)*env*.09
        else:sig=rng.normal(size=n)*env*.13
        a[start:start+n]+=sig
    a=np.clip(a*.55,-.84,.84)
    path=OUT/"effects.wav"
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((a*32767).astype("<i2").tobytes())
    return path,cues


def find_ffmpeg(cli):
    if cli:return cli
    import shutil
    p=shutil.which("ffmpeg")
    if p:return p
    candidates=list(Path.home().glob("Documents/ChatGPT/工作台/下一期_单词卡/.qa_tools/imageio_ffmpeg/binaries/ffmpeg*.exe"))
    if candidates:return str(candidates[0])
    raise RuntimeError("ffmpeg not found; supply --ffmpeg")


def preview():
    times=[0,2.2,4.2,8.2,12.8,15.2,25.5,30.2,40,45.2,55,70.5]
    sheet=Image.new("RGB",(1440,4*307),(11,18,28));d=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        frame=scene_frame(t).convert("RGB").resize((460,259),Image.Resampling.LANCZOS)
        x=10+i%3*480;y=7+i//3*307
        sheet.paste(frame,(x,y+35))
        d.text((x,y),f"{i+1:02d}  {t:05.1f} s",font=font(22),fill=WHITE)
    p=OUT/"分镜预览.png";sheet.save(p)
    return p


def cover():
    # One 4:3 image; all content lives inside x=420..1500 (central 3:4 crop).
    cw,ch=1920,1440
    yy,xx=np.mgrid[0:ch,0:cw]
    r=np.sqrt(((xx-960)/1150)**2+((yy-670)/830)**2)
    light=np.clip(1-r,0,1)**2
    a=np.zeros((ch,cw,3),dtype=np.uint8)
    for k,b,v in ((0,8,31),(1,16,27),(2,25,17)):
        a[:,:,k]=np.clip(b+light*v,0,255)
    im=Image.fromarray(a,"RGB").convert("RGBA")
    d=ImageDraw.Draw(im)
    text(d,960,93,"想记牢？",105,WHITE,anchor="ma")
    text(d,960,238,"自己画一笔",108,GOLD,anchor="ma")
    # Physical paper boards and sculpted apple; no mobile UI or flat chart.
    paper_board(im,(553,459,943,938))
    paper_board(im,(975,459,1368,938))
    apple_object(im,748,683,1.34)
    for j in range(3):
        text(d,1170,580+j*92,"苹果",72,(113+j*16,102+j*15,91+j*14),anchor="ma")
    text(d,747,1001,"画 23%",66,TEAL,anchor="ma")
    text(d,1170,1001,"写 14%",66,SAND,anchor="ma")
    d.line((570,1080,1355,1080),fill=(141,132,105),width=4)
    text(d,960,1104,"4 秒/词 · 短时自由回忆",47,WHITE,anchor="ma")
    text(d,960,1193,"Wammes 等，2016 · 实验 7",37,SAND,anchor="ma")
    text(d,960,1268,"挑词 → 简画 → 遮住回想",41,GOLD,anchor="ma")
    p=OUT/"封面_横竖通用.png";im.convert("RGB").save(p,optimize=True)
    im.crop((420,0,1500,1440)).convert("RGB").save(OUT/"竖裁预览.png")
    return p


def render(ffmpeg):
    # Exercise every beat state before opening the encoder so layout errors fail fast.
    for half_beat in range(320):
        scene_frame(half_beat*BEAT/2)
    wav,_=audio_file()
    picture=OUT/"picture_noaudio.mp4"
    cmd=[ffmpeg,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s","1920x1080","-r","30","-i","-",
         "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-movflags","+faststart","-an",str(picture)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n in range(FRAMES):
            proc.stdin.write(scene_frame(n/FPS).convert("RGB").tobytes())
            if n%300==0:print(f"frame {n}/{FRAMES}",flush=True)
        proc.stdin.close()
        if proc.wait():raise RuntimeError("FFmpeg picture encode failed")
    except Exception:
        proc.kill();raise
    out=OUT/"画出来更好记_75s_1080p.mp4"
    cmd=[ffmpeg,"-y","-loglevel","error","-i",str(picture),"-i",str(wav),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-af","acompressor=threshold=-23dB:ratio=5:attack=1:release=70,loudnorm=I=-18.4:TP=-2.0:LRA=11","-t","75","-movflags","+faststart",str(out)]
    subprocess.run(cmd,check=True)
    picture.unlink()
    print(out)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--all",action="store_true")
    ap.add_argument("--preview",action="store_true")
    ap.add_argument("--cover",action="store_true")
    ap.add_argument("--render",action="store_true")
    ap.add_argument("--ffmpeg")
    args=ap.parse_args()
    if args.all or args.preview:print(preview())
    if args.all or args.cover:print(cover())
    if args.all or args.render:render(find_ffmpeg(args.ffmpeg))


if __name__=="__main__":main()

