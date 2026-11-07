"""Vibe知识大赏：画出来，更好记？

Independent Pillow renderer. No inherited episode code or visual assets.
Run: python render.py --all [--ffmpeg PATH]
Output: out/画出来更好记_75s_1080p.mp4, cover.png, storyboard.png.
"""
from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
W, H = 960, 540
FPS = 30
BPM = 128
BEAT = 60 / BPM
FRAMES = 2250
BG = (8, 13, 26)
WHITE = (239, 246, 252)
MUTED = (154, 183, 204)
CYAN = (67, 225, 224)
GOLD = (255, 195, 94)
PINK = (247, 123, 151)
FONT_CANDIDATES = [
    Path(__file__).parent / "assets" / "NotoSansSC-VF.ttf",
    Path("C:/Windows/Fonts/NotoSansSC-VF.ttf"),
    Path("C:/Windows/Fonts/msyhbd.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"),
]
FONT_PATH = next((p for p in FONT_CANDIDATES if p.exists()), None)
if not FONT_PATH:
    raise RuntimeError("Noto Sans CJK font missing; install fonts-noto-cjk")
FONT = {s: ImageFont.truetype(str(FONT_PATH), s) for s in (16, 18, 20, 22, 24, 26, 28, 30, 34, 38, 42, 48, 52, 58)}


def txt(d, xy, value, size, fill=WHITE, anchor="la", max_width=None):
    """Draw visible text and fail before shipping if it would be clipped."""
    font = FONT.setdefault(size, ImageFont.truetype(str(FONT_PATH), size))
    x, y = xy
    box = d.textbbox((x, y), value, font=font, anchor=anchor)
    if box[0] < 0 or box[1] < 0 or box[2] > d.im.size[0] or box[3] > d.im.size[1]:
        raise ValueError(f"Text out of frame: {value!r}: {box}")
    if max_width and box[2] - box[0] > max_width:
        raise ValueError(f"Text too wide: {value!r}: {box[2]-box[0]} > {max_width}")
    d.text(xy, value, font=font, fill=fill, anchor=anchor, stroke_width=0)


def rr(d, box, radius, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius, fill=fill, outline=outline, width=width)


def glow_line(im, points, color=CYAN, width=5, glow=13):
    layer = Image.new("RGBA", im.size)
    q = ImageDraw.Draw(layer)
    q.line(points, fill=(*color, 210), width=width, joint="curve")
    soft = layer.filter(ImageFilter.GaussianBlur(glow))
    im.alpha_composite(soft)
    im.alpha_composite(layer)


def base(stage):
    im = Image.new("RGBA", (W, H), (*BG, 255))
    d = ImageDraw.Draw(im)
    # Architectural atelier, with depth and an anchored floor; never beat-shaken.
    for x in range(0, W, 80):
        d.line((x, 0, x, 540), fill=(15, 32, 49, 255), width=1)
    for y in range(56, 540, 80):
        d.line((0, y, W, y), fill=(15, 32, 49, 255), width=1)
    d.polygon([(0, 485), (960, 485), (960, 540), (0, 540)], fill=(12, 22, 35, 255))
    d.line((0, 485, 960, 485), fill=(61, 115, 126, 255), width=2)
    d.line((0, 55, 960, 55), fill=(39, 67, 82, 255), width=1)
    txt(d, (42, 28), "VIBE / KNOWLEDGE", 18, MUTED, "lm")
    txt(d, (918, 28), f"{stage}  ·  128 BPM", 18, MUTED, "rm")
    return im


def easel(im, x=550, y=305, size=1):
    d = ImageDraw.Draw(im)
    ww, hh = int(310 * size), int(315 * size)
    x0, y0 = int(x - ww / 2), int(y - hh / 2)
    # Glass slab and easel stand, not a desk.
    d.polygon([(x0+30,y0+hh), (x0+ww-30,y0+hh), (x0+ww-54,y0+hh+38), (x0+54,y0+hh+38)], fill=(22,47,58,255))
    rr(d, (x0,y0,x0+ww,y0+hh), 20, (22, 40, 59, 255), (64, 151, 168, 255), 3)
    rr(d, (x0+18,y0+18,x0+ww-18,y0+hh-18), 13, (12, 24, 39, 255), (41, 82, 98,255), 2)
    d.ellipse((x0+27,y0+28,x0+37,y0+38), fill=(*CYAN,255))
    d.ellipse((x0+45,y0+28,x0+55,y0+38), fill=(*GOLD,255))
    return (x0+18,y0+18,x0+ww-18,y0+hh-18)


def apple(im, x, y, scale=1.0, progress=1.0, color=GOLD):
    """Hand-drawn apple appears stroke by stroke; simple enough for four seconds."""
    p = max(0, min(1, progress))
    pts=[]
    for i in range(65):
        a = math.pi*2*i/64
        # A sketch-like heart silhouette, not a perfect icon.
        r = 1 - 0.18*math.cos(2*a)
        pts.append((int(x+64*scale*r*math.sin(a)), int(y+65*scale*r*math.cos(a))))
    n=max(2,int(len(pts)*min(p/0.76,1)))
    glow_line(im,pts[:n],color,int(5*scale),int(10*scale))
    if p > .74:
        glow_line(im, [(int(x),int(y-59*scale)),(int(x+8*scale),int(y-91*scale)),(int(x+37*scale),int(y-99*scale))],color,int(4*scale),7)
    if p > .88:
        d=ImageDraw.Draw(im)
        d.ellipse((x+13*scale,y-101*scale,x+52*scale,y-82*scale),fill=(*color,190))


def figure(im, t, hand="pen", x=178, y=453, scale=1.0):
    """One adult-proportion figure, standing or walking through every frame."""
    d=ImageDraw.Draw(im)
    bob=math.sin(t*3.7)*2.0
    x,y=int(x),int(y+bob)
    s=scale
    head=(x, int(y-172*s))
    # 7.5-head standing silhouette with teal edge and a long coat.
    d.ellipse((x-17*s,head[1]-18*s,x+17*s,head[1]+18*s),fill=(30,56,67,255),outline=(*CYAN,255),width=max(2,int(3*s)))
    d.polygon([(x-25*s,y-148*s),(x+25*s,y-148*s),(x+34*s,y-74*s),(x-34*s,y-74*s)],fill=(28,54,64,255))
    glow_line(im,[(int(x-25*s),int(y-148*s)),(int(x-34*s),int(y-76*s))],CYAN,max(2,int(3*s)),5)
    glow_line(im,[(int(x+25*s),int(y-148*s)),(int(x+34*s),int(y-76*s))],CYAN,max(2,int(3*s)),5)
    stride=math.sin(t*2.4)*7 if t<8 else math.sin(t*1.4)*3
    d.line((x-14*s,y-76*s,x-17*s+stride,y-4*s),fill=(128,211,211,255),width=max(4,int(9*s)))
    d.line((x+14*s,y-76*s,x+18*s-stride,y-4*s),fill=(128,211,211,255),width=max(4,int(9*s)))
    d.line((x-27*s+stride,y-4*s,x-8*s+stride,y-4*s),fill=(*WHITE,255),width=max(3,int(6*s)))
    d.line((x+14*s-stride,y-4*s,x+34*s-stride,y-4*s),fill=(*WHITE,255),width=max(3,int(6*s)))
    # Arm reaches to an upright easel; no chair, book, or homework pose.
    d.line((x+22*s,y-132*s,x+67*s,y-111*s,x+94*s,y-131*s),fill=(133,205,209,255),width=max(4,int(8*s)),joint="curve")
    d.ellipse((x+88*s,y-138*s,x+101*s,y-125*s),fill=(*WHITE,255))
    d.line((x-22*s,y-131*s,x-48*s,y-75*s),fill=(110,172,181,255),width=max(4,int(8*s)))
    if hand=="pen":
        d.line((x+94*s,y-129*s,x+112*s,y-156*s),fill=(*GOLD,255),width=max(2,int(5*s)))
        d.ellipse((x+107*s,y-162*s,x+115*s,y-154*s),fill=(*WHITE,255))
    elif hand=="point":
        d.line((x+94*s,y-130*s,x+114*s,y-142*s),fill=(*WHITE,255),width=max(2,int(4*s)))
    d.ellipse((x-48*s,y-3*s,x+48*s,y+4*s),fill=(12,40,49,255))


def header(d, cn, en, accent=CYAN, y=78):
    txt(d,(46,y),cn,52,WHITE,"la",870)
    d.line((46,y+67,144,y+67),fill=(*accent,255),width=4)
    txt(d,(46,y+82),en,24,MUTED,"la",855)


def scene_frame(t):
    beat=t/BEAT
    if beat < 16:
        im=base("01 / 先画还是先写")
        d=ImageDraw.Draw(im)
        header(d,"画一笔，更好记？","Draw it, or write it?",GOLD)
        easel(im,580,316,.90)
        # From frame 0 the adult is already drawing, and the first stroke is visible.
        apple(im,580,314,1.03,max(.06,min(1,t/1.8)),GOLD)
        figure(im,t,"pen",157,469,1.05)
        if 4.5 <= beat < 8.5:
            rr(d,(366,411,855,474),16,(22,46,60,255),(69,135,151,255),2)
            txt(d,(610,440),"每个词，只给 4 秒",30,WHITE,"mm")
            txt(d,(610,468),"4 seconds per word",18,MUTED,"mm")
        if beat >= 8.5:
            # Both measured values are Experiment 7, pure-list groups; no false doubling.
            rr(d,(326,210,852,407),22,(15,31,47,255),(88,162,173,255),2)
            txt(d,(452,251),"自己画",28,CYAN,"mm")
            txt(d,(716,251),"反复写",28,PINK,"mm")
            txt(d,(452,323),"23%",58,CYAN,"mm")
            txt(d,(716,323),"14%",58,PINK,"mm")
            txt(d,(589,388),"66 个易画词 · 短时自由回忆",20,WHITE,"mm")
        if beat >= 10.5:
            txt(d,(589,194),"画的词，回忆更多",30,GOLD,"mm")
        if beat >= 13:
            txt(d,(805,510),"Wammes et al., 2016 · Exp. 7",18,MUTED,"rm")
        return im
    if beat < 32:
        im=base("02 / 方法")
        d=ImageDraw.Draw(im)
        header(d,"先自己画，再试着想","Draw it yourself, then recall it.",CYAN)
        figure(im,t,"point",188,469,1.05)
        for idx,(lab,en) in enumerate([("挑词","choose"),("简画","sketch"),("回想","recall")]):
            if beat >= 17 + idx*3:
                x=330+idx*173
                rr(d,(x,243,x+151,331),18,(22,41,59,255),(70,140,155,255),2)
                txt(d,(x+75,272),lab,30,WHITE,"mm")
                txt(d,(x+75,310),en,20,MUTED,"mm")
        if beat>=26.5:
            txt(d,(239,411),"论文测的是易画的单词",24,GOLD,"mm")
            txt(d,(239,444),"The study tested drawable words.",18,MUTED,"mm")
        return im
    if beat < 64:
        im=base("03 / 挑词")
        d=ImageDraw.Draw(im)
        header(d,"① 挑能画的词","Start with words you can picture.",GOLD)
        figure(im,t,"point",186,469,1.04)
        # Gallery plinths replace cards and previous episodes' list layouts.
        for idx,(cn,en,kind) in enumerate([("苹果","apple",0),("钥匙","key",1),("雨伞","umbrella",2)]):
            x=370+idx*180
            if beat >= 34+idx*6:
                rr(d,(x-67,226,x+67,392),19,(21,40,56,255),(66,124,137,255),2)
                if kind==0: apple(im,x,282,.35,1,GOLD)
                elif kind==1:
                    d.ellipse((x-31,248,x+2,281),outline=(*GOLD,255),width=4)
                    d.line((x,271,x+37,309,x+43,299),fill=(*GOLD,255),width=5)
                else:
                    d.arc((x-46,245,x+46,320),180,360,fill=(*GOLD,255),width=5)
                    d.line((x,285,x,330,x+21,330),fill=(*GOLD,255),width=5)
                txt(d,(x,347),cn,30,WHITE,"mm")
                txt(d,(x,379),en,20,MUTED,"mm")
        txt(d,(487,455),"例：苹果、钥匙、雨伞",26,CYAN,"mm")
        return im
    if beat < 96:
        im=base("04 / 简画")
        d=ImageDraw.Draw(im)
        header(d,"② 画出最明显的特征","Sketch the identifying features.",CYAN)
        easel(im,598,310,1.02)
        progress=min(1,max(.05,(beat-66)/16))
        apple(im,597,307,1.14,progress,CYAN)
        figure(im,t,"pen",160,469,1.05)
        if beat>=82:
            rr(d,(354,420,839,473),15,(22,44,57,255),(67,123,138,255),2)
            txt(d,(595,447),"苹果 = 圆 + 叶，画得像就够",25,WHITE,"mm")
        if beat>=89:
            txt(d,(696,510),"研究中每词仅 4 秒（实验 6、7）",18,MUTED,"rm")
        return im
    if beat < 128:
        im=base("05 / 回想")
        d=ImageDraw.Draw(im)
        header(d,"③ 遮住图，自己回想","Hide the sketch. Recall the word.",PINK)
        easel(im,592,312,1.02)
        apple(im,592,306,.95,1,GOLD)
        if beat>=103:
            # A sliding opaque gallery curtain; the person stays active.
            curtain=min(1,(beat-103)/11)
            x0=int(747-292*curtain)
            rr(d,(x0,153,747,449),13,(35,47,66,255),(109,130,155,255),2)
            d.line((x0+24,160,x0+24,442),fill=(87,103,130,255),width=2)
        figure(im,t,"point",165,469,1.05)
        if beat>=113:
            rr(d,(352,385,819,456),18,(22,46,58,255),(70,141,151,255),2)
            txt(d,(585,421),"答案：苹果  /  APPLE",32,GOLD,"mm")
        if beat>=120:
            txt(d,(781,508),"回想练习是实用延伸；本研究测的是回忆成绩",18,MUTED,"rm")
        return im
    im=base("06 / 照着做")
    d=ImageDraw.Draw(im)
    header(d,"挑词 → 简画 → 遮住回想","Choose → sketch → recall",GOLD)
    figure(im,t,"point",154,470,1.02)
    # Final art wall is a stable, readable composition, held for the last 7 s.
    for i,(cn,en) in enumerate([("苹果","APPLE"),("钥匙","KEY"),("雨伞","UMBRELLA")]):
        if beat>=130+i*5:
            x=365+i*182
            rr(d,(x-76,221,x+76,340),20,(22,42,58,255),(80,138,150,255),2)
            txt(d,(x,260),cn,34,WHITE,"mm")
            txt(d,(x,311),en,20,MUTED,"mm")
    if beat>=144:
        rr(d,(295,365,898,432),18,(30,51,64,255),(111,177,177,255),2)
        txt(d,(596,390),"4 秒/词：画 23%  ·  写 14%",29,CYAN,"mm")
        txt(d,(596,418),"Wammes et al., 2016 · 实验 7",18,MUTED,"mm")
    if beat>=150:
        txt(d,(596,468),"证据范围：易画单词 · 短时自由回忆",20,WHITE,"mm")
    return im


def find_ffmpeg(cli):
    if cli:
        return cli
    import shutil
    p=shutil.which("ffmpeg")
    if p:return p
    candidates=list(Path.home().glob("Documents/ChatGPT/工作台/下一期_单词卡/.qa_tools/imageio_ffmpeg/binaries/ffmpeg*.exe"))
    if candidates:return str(candidates[0])
    raise RuntimeError("ffmpeg not found; supply --ffmpeg")


def audio_file():
    """Short deterministic per-event effects; no score, melody, or ambience."""
    sr=48000
    seconds=75
    a=np.zeros(sr*seconds,dtype=np.float64)
    # All cue times are beat positions; each transient starts with its visual event.
    cues=[(0,"hit"),(4.5,"tick"),(8.5,"chime"),(10.5,"pop"),(13,"pop"),
          (16,"whoosh"),(17,"pop"),(20,"pop"),(23,"pop"),(26.5,"chime"),
          (32,"whoosh"),(34,"pop"),(40,"pop"),(46,"pop"),
          (64,"whoosh"),(66,"draw"),(74,"draw"),(82,"pop"),(89,"tick"),
          (96,"whoosh"),(103,"slide"),(113,"chime"),(120,"pop"),
          (128,"whoosh"),(130,"pop"),(135,"pop"),(140,"pop"),(144,"chime"),(150,"pop")]
    rng=np.random.default_rng(20261107)
    for beat,kind in cues:
        start=int(round(beat*BEAT*sr))
        dur={"hit":.30,"whoosh":.22,"chime":.34,"tick":.09,"pop":.14,"draw":.18,"slide":.24}[kind]
        n=int(dur*sr); tt=np.arange(n)/sr
        env=np.exp(-tt*({"hit":13,"chime":9,"whoosh":15,"tick":28,"pop":23,"draw":22,"slide":16}[kind]))
        if kind=="hit": sig=np.sin(2*np.pi*(80*tt+150*tt*tt))*env + .30*rng.normal(size=n)*env
        elif kind=="whoosh": sig=rng.normal(size=n)*env*.22
        elif kind=="chime": sig=(np.sin(2*np.pi*880*tt)+.45*np.sin(2*np.pi*1320*tt))*env*.25
        elif kind=="tick": sig=rng.normal(size=n)*env*.16
        elif kind=="pop": sig=np.sin(2*np.pi*(420+beat*2)*tt)*env*.21
        elif kind=="draw": sig=rng.normal(size=n)*env*.09
        else: sig=rng.normal(size=n)*env*.13
        a[start:start+n]+=sig
    # Conservative peak, then ffmpeg loudnorm measures final integrated loudness.
    a=np.clip(a*.55,-.84,.84)
    path=OUT/"effects.wav"
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes((a*32767).astype("<i2").tobytes())
    return path,cues


def render(ffmpeg):
    wav,cues=audio_file()
    raw=OUT/"picture_noaudio.mp4"
    cmd=[ffmpeg,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s","960x540","-r",str(FPS),"-i","-",
         "-vf","scale=1920:1080:flags=lanczos,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","20","-movflags","+faststart","-an",str(raw)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n in range(FRAMES):
            im=scene_frame(n/FPS).convert("RGB")
            p.stdin.write(im.tobytes())
            if n%300==0:print(f"frame {n}/{FRAMES}",flush=True)
        p.stdin.close()
        if p.wait():raise RuntimeError("picture encode failed")
    except Exception:
        p.kill();raise
    final=OUT/"画出来更好记_75s_1080p.mp4"
    # Speech-free effects only. Measured output is checked by verify.py.
    cmd=[ffmpeg,"-y","-loglevel","error","-i",str(raw),"-i",str(wav),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-af","loudnorm=I=-18:TP=-1.5:LRA=11","-t","75","-movflags","+faststart",str(final)]
    subprocess.run(cmd,check=True)
    raw.unlink()
    print(final)
    return final


def preview():
    times=[0,2.2,4.2,8.2,15.2,25,30.2,40,45.2,55,60.2,70]
    sheet=Image.new("RGB",(1440,4*315),(5,12,24))
    d=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        frame=scene_frame(t).convert("RGB").resize((460,259),Image.Resampling.LANCZOS)
        x=10+(i%3)*480;y=8+(i//3)*315
        sheet.paste(frame,(x,y+31))
        d.text((x,y),f"{i+1:02d}  {t:05.1f} s",font=FONT[20],fill=WHITE)
    path=OUT/"分镜预览.png";sheet.save(path)
    return path


def cover():
    """Single 4:3 upload image; every essential item fits the central 3:4 crop."""
    cw,ch=1920,1440
    im=Image.new("RGB",(cw,ch),(5,10,22))
    d=ImageDraw.Draw(im)
    # Subtle cinematic spotlights and continuous dark side wings.
    for r in range(700,40,-8):
        alpha=(700-r)/700
        col=(int(5+17*alpha),int(10+26*alpha),int(22+35*alpha))
        d.ellipse((960-r,760-r,960+r,760+r),outline=col,width=8)
    d.rectangle((0,0,1920,1440),outline=(23,41,52),width=4)
    # Central safe strip = x 420..1500, but contents inset another 90 px.
    title=ImageFont.truetype(str(FONT_PATH),108)
    sub=ImageFont.truetype(str(FONT_PATH),51)
    small=ImageFont.truetype(str(FONT_PATH),35)
    d.text((960,139),"想记牢？",font=title,fill=WHITE,anchor="ma")
    d.text((960,278),"自己画一笔",font=title,fill=(255,202,110),anchor="ma")
    # Raised translucent specimen plates: brush drawing against repeated writing.
    d.rounded_rectangle((575,490,945,960),38,fill=(22,45,63),outline=(67,190,192),width=6)
    d.rounded_rectangle((975,490,1345,960),38,fill=(25,38,55),outline=(113,113,140),width=5)
    d.ellipse((658,615,862,833),outline=(255,205,110),width=14)
    d.line((760,621,773,576,825,568),fill=(255,205,110),width=12,joint="curve")
    d.ellipse((792,548,860,586),fill=(255,205,110))
    for j in range(5):
        d.text((1160,610+j*42),"苹果",font=sub,fill=(120-j*12,134-j*10,149-j*8),anchor="mm")
    d.text((760,913),"画 23%",font=sub,fill=(95,235,224),anchor="mm")
    d.text((1160,913),"写 14%",font=sub,fill=(229,137,158),anchor="mm")
    d.text((960,1050),"4 秒/词 · 短时自由回忆",font=sub,fill=WHITE,anchor="mm")
    d.text((960,1132),"Wammes 等，2016 · 实验 7",font=small,fill=(160,190,207),anchor="mm")
    d.text((960,1215),"挑词  →  简画  →  遮住回想",font=small,fill=(211,230,233),anchor="mm")
    # Bottom-left of the central crop (x 420..~870, y 1275..1400) is entirely empty.
    path=OUT/"封面_横竖通用.png";im.save(path,optimize=True)
    crop=im.crop((420,0,1500,1440));crop.save(OUT/"竖裁预览.png")
    # Mechanical crop/text audit for upload readiness.
    for box in [d.textbbox((960,139),"想记牢？",font=title,anchor="ma"), d.textbbox((960,278),"自己画一笔",font=title,anchor="ma")]:
        assert box[0]>=500 and box[2]<=1420,box
    return path


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--all",action="store_true")
    ap.add_argument("--preview",action="store_true")
    ap.add_argument("--cover",action="store_true")
    ap.add_argument("--render",action="store_true")
    ap.add_argument("--ffmpeg")
    a=ap.parse_args()
    if a.all or a.preview:print(preview())
    if a.all or a.cover:print(cover())
    if a.all or a.render:render(find_ffmpeg(a.ffmpeg))


if __name__=="__main__":main()

