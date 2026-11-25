# -*- coding: utf-8 -*-
"""60 秒样片的小人：侧面 / 正面两种视角，关节角度或 IK 摆姿势，表情、道具、手持物。

坐标单位是"身高 h"：骨盆在 (0, 0)，y 向下为正。
姿势 pose = dict(
    view='side' | 'front',
    lean=躯干前倾角度, head=头部前倾角度, rot=整个人绕骨盆转的角度（顺时针为正）,
    arms=(后/左手臂, 前/右手臂), legs=(后/左腿, 前/右腿),
    bust=True 时不画腿,
)
手臂/腿可以写成角度 (a, b)：a 是从"朝下"往前（正面视角是往外）转的角度，b 是肘/膝的弯曲；
也可以写成 IK：{'ik': (x, y), 'rel': 'P'|'N'|'Hc', 'bend': ±1}，让手或脚到指定位置。
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import render_hero_select as hero

F = hero.F

FIGS = {
    'dacong': dict(color=(175, 182, 200), sw=0.23, hw=0.17, limb=1.0, props=('messy', 'phones_neck', 'plaid')),
    'afei': dict(color=(255, 70, 85), sw=0.29, hw=0.18, limb=1.3, props=('bib',)),
    'xiaok': dict(color=(255, 186, 30), sw=0.23, hw=0.17, limb=1.0, props=('helmet', 'skates')),
    'laozhou': dict(color=(64, 150, 255), sw=0.22, hw=0.17, limb=0.95, props=('glasses', 'backpack')),
    'xingxing': dict(color=(172, 112, 255), sw=0.23, hw=0.2, limb=1.0, props=('longhair', 'scarf')),
    'suguan': dict(color=(196, 72, 64), sw=0.25, hw=0.22, limb=1.05, props=('curly', 'keys')),
    'roomA': dict(color=(70, 190, 200), sw=0.23, hw=0.17, limb=1.0, props=('glasses', 'phones_head')),
    'roomB': dict(color=(225, 215, 200), sw=0.23, hw=0.17, limb=1.0, props=('bedhair',)),
    'roomC': dict(color=(110, 200, 120), sw=0.23, hw=0.17, limb=1.0, props=('buzz', 'towel', 'toothbrush')),
    'guard': dict(color=(80, 100, 150), sw=0.24, hw=0.19, limb=1.0, props=('cap',)),
    'girl': dict(color=(240, 140, 180), sw=0.2, hw=0.18, limb=0.9, props=('longhair',)),
    'boy': dict(color=(130, 140, 165), sw=0.23, hw=0.17, limb=1.0, props=()),
}
CROWD_COLORS = [(150, 170, 210), (210, 160, 120), (140, 200, 170), (200, 150, 190), (220, 200, 120), (160, 160, 175)]

BL = dict(neck=0.035, torso=0.29, upper=0.155, fore=0.145, thigh=0.235, shin=0.225, foot=0.065)
HRX, HRY = 0.056, 0.066
DARK = (24, 24, 30, 255)


def rad(d):
    return d * math.pi / 180


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def ik2(S, T, L1, L2, bend):
    dx, dy = T[0] - S[0], T[1] - S[1]
    d = max(abs(L1 - L2) + 1e-6, min(math.hypot(dx, dy), L1 + L2 - 1e-6))
    a = math.atan2(dy, dx)
    b = math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    ang = a + bend * b
    E = (S[0] + L1 * math.cos(ang), S[1] + L1 * math.sin(ang))
    Wr = (S[0] + d * math.cos(a), S[1] + d * math.sin(a))
    return E, Wr


def joints(spec, pose, facing):
    view = pose.get('view', 'side')
    lean, head = rad(pose.get('lean', 0)), rad(pose.get('head', 0))
    lim = spec.get('limb', 1.0)
    f = facing if view == 'side' else 1

    def up(L, a):
        return (f * L * math.sin(a), -L * math.cos(a))

    def down(L, a):
        return (f * L * math.sin(a), L * math.cos(a))

    P = (0.0, 0.0)
    N = add(P, up(BL['torso'], lean))
    Hc = add(N, up(BL['neck'] + HRY * 0.95, lean + head))
    J = dict(P=P, N=N, Hc=Hc)
    legscale = pose.get('legscale', (1.0, 1.0))
    for i in range(2):
        side = (-1, 1)[i]
        if view == 'side':
            S = add(N, down(0.03, lean))
        else:
            S = add(N, (side * spec['sw'] / 2, 0.035))
        arm = pose.get('arms', ((5, 5), (5, 5)))[i]
        if isinstance(arm, dict):
            base = J[arm.get('rel', 'P')]
            tx, ty = arm['ik']
            T = add(base, ((f * tx) if view == 'side' else tx, ty))
            E, Wr = ik2(S, T, BL['upper'], BL['fore'], arm.get('bend', 1) * (f if view == 'side' else 1))
        else:
            sa, ea = rad(arm[0]), rad(arm[1])
            if view == 'side':
                E = add(S, down(BL['upper'], lean + sa))
                Wr = add(E, down(BL['fore'], lean + sa + ea))
            else:
                E = add(S, (side * BL['upper'] * math.sin(sa), BL['upper'] * math.cos(sa)))
                Wr = add(E, (side * BL['fore'] * math.sin(sa + ea), BL['fore'] * math.cos(sa + ea)))
        J[f'S{i}'], J[f'E{i}'], J[f'W{i}'] = S, E, Wr
        leg = pose.get('legs', ((0, 0), (0, 0)))[i]
        th, sh = BL['thigh'] * legscale[0], BL['shin'] * legscale[1]
        Hp = P if view == 'side' else add(P, (side * spec['hw'] * 0.3, 0))
        if isinstance(leg, dict):
            base = J[leg.get('rel', 'P')]
            tx, ty = leg['ik']
            T = add(base, ((f * tx) if view == 'side' else tx, ty))
            K, A = ik2(Hp, T, th, sh, leg.get('bend', -1) * (f if view == 'side' else 1))
        else:
            ta, ka = rad(leg[0]), rad(leg[1])
            if view == 'side':
                K = add(Hp, down(th, ta))
                A = add(K, down(sh, ta - ka))
            else:
                K = add(Hp, (side * th * math.sin(ta), th * math.cos(ta)))
                A = add(K, (side * sh * math.sin(ta - ka), sh * math.cos(ta - ka)))
        Ft = add(A, (f * BL['foot'], 0.005)) if view == 'side' else add(A, (side * 0.03, 0.01))
        J[f'H{i}'], J[f'K{i}'], J[f'A{i}'], J[f'F{i}'] = Hp, K, A, Ft
    rot = rad(pose.get('rot', 0))
    if rot:
        c, s = math.cos(rot), math.sin(rot)
        J = {k: (x * c - y * s, x * s + y * c) for k, (x, y) in J.items()}
    J['_rot'] = rot
    return J


# ---------------------------------------------------------------- 画小人
def _limb(d, pts, w):
    d.line(pts, fill=255, width=max(1, int(w)), joint='curve')
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=255)


def fig_layer(key, pose, h, facing=1, expr='neutral', talk=0.0, hold=None, glow=True, wind=0.0,
              glint=False, sweat=False, color=None):
    """画一个小人，返回 (RGBA 图, 骨盆在图里的坐标)。"""
    spec = dict(FIGS[key])
    if color is not None:
        spec['color'] = color
    view = pose.get('view', 'side')
    J = joints(spec, pose, facing)
    rot = J.pop('_rot')
    bust = pose.get('bust', False)
    keys = [k for k in J if not (bust and k[0] in 'KAF')]
    xs = [J[k][0] for k in keys]
    ys = [J[k][1] for k in keys]
    pad = 0.2
    x0, x1 = min(xs) - pad, max(xs) + pad
    y0, y1 = min(ys) - pad, max(ys) + pad
    if bust:
        y1 = min(y1, 0.08)
    ss = 2 if h <= 420 else 1
    u = h * ss
    Wc, Hc_ = max(4, int((x1 - x0) * u)), max(4, int((y1 - y0) * u))
    ox, oy = -x0 * u, -y0 * u

    def px(k):
        x, y = J[k]
        return (ox + x * u, oy + y * u)

    lim = spec['limb']
    w_up, w_fo, w_th, w_sh = 0.055 * u * lim, 0.047 * u * lim, 0.078 * u * lim ** 0.6, 0.062 * u * lim ** 0.5
    back = Image.new('L', (Wc, Hc_), 0)
    front = Image.new('L', (Wc, Hc_), 0)
    db, dfm = ImageDraw.Draw(back), ImageDraw.Draw(front)

    # 腿
    if not bust:
        for i in range(2):
            dd = db if (view == 'side' and i == 0) else dfm
            _limb(dd, [px(f'H{i}'), px(f'K{i}')], w_th)
            _limb(dd, [px(f'K{i}'), px(f'A{i}')], w_sh)
            _limb(dd, [px(f'A{i}'), px(f'F{i}')], 0.04 * u)
    # 躯干
    N, P = px('N'), px('P')
    ax, ay = P[0] - N[0], P[1] - N[1]
    L = math.hypot(ax, ay) or 1
    pxv, pyv = -ay / L, ax / L
    if view == 'side':
        top, bot = 0.065 * u * (1.15 if key == 'afei' else 1), 0.052 * u
        poly = [(N[0] + pxv * top, N[1] + pyv * top), (N[0] - pxv * top, N[1] - pyv * top),
                (P[0] - pxv * bot, P[1] - pyv * bot), (P[0] + pxv * bot, P[1] + pyv * bot)]
        dfm.polygon(poly, fill=255)
        dfm.ellipse((N[0] - top, N[1] - top, N[0] + top, N[1] + top), fill=255)
        dfm.ellipse((P[0] - bot, P[1] - bot, P[0] + bot, P[1] + bot), fill=255)
    else:
        S0, S1 = px('S0'), px('S1')
        hw = spec['hw'] / 2 * u
        c, s = math.cos(rot), math.sin(rot)
        H0 = (P[0] - hw * c, P[1] - hw * s)
        H1 = (P[0] + hw * c, P[1] + hw * s)
        dfm.polygon([S0, S1, H1, H0], fill=255)
        r = 0.055 * u * (1.2 if key == 'afei' else 1)
        for q in (S0, S1):
            dfm.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=255)
        dfm.ellipse((P[0] - hw, P[1] - 0.05 * u, P[0] + hw, P[1] + 0.05 * u), fill=255)
    # 脖子和头
    Hc = px('Hc')
    _limb(dfm, [N, Hc], 0.042 * u)
    rx, ry = HRX * u, HRY * u
    if view == 'side':
        rx *= 1.04
    dfm.ellipse((Hc[0] - rx, Hc[1] - ry, Hc[0] + rx, Hc[1] + ry), fill=255)
    # 手臂
    for i in range(2):
        dd = db if (view == 'side' and i == 0) else dfm
        _limb(dd, [px(f'S{i}'), px(f'E{i}')], w_up)
        _limb(dd, [px(f'E{i}'), px(f'W{i}')], w_fo)
        Wx, Wy = px(f'W{i}')
        hr = 0.032 * u * lim ** 0.5
        dd.ellipse((Wx - hr, Wy - hr, Wx + hr, Wy + hr), fill=255)
    if bust:
        cut = int(oy + 0.06 * u)
        for m in (back, front):
            ImageDraw.Draw(m).rectangle((0, cut, Wc, Hc_), fill=0)

    col = np.array(spec['color'], np.float32)
    tt = np.linspace(0, 1, Hc_)[:, None, None]
    top_c = np.clip(col * 0.6 + 255 * 0.22, 0, 255)
    grad = np.repeat(top_c * (1 - tt) + col * 0.32 * tt, Wc, axis=1)
    face_c = tuple(int(v) for v in grad[int(max(0, min(Hc_ - 1, Hc[1]))), 0])
    body = Image.fromarray(grad.astype(np.uint8), 'RGB').convert('RGBA')
    union = Image.fromarray(np.maximum(np.array(back), np.array(front)), 'L')
    out = Image.new('RGBA', (Wc, Hc_), (0, 0, 0, 0))
    if glow:
        g = Image.new('RGBA', (Wc, Hc_), tuple(spec['color']) + (0,))
        g.putalpha(union.filter(ImageFilter.GaussianBlur(min(24, 0.045 * u))).point(lambda v: int(v * 0.7)))
        out = Image.alpha_composite(out, g)
    bk = Image.fromarray((grad * 0.62).astype(np.uint8), 'RGB').convert('RGBA')
    bk.putalpha(back)
    out = Image.alpha_composite(out, bk)
    fr = body.copy()
    fr.putalpha(front)
    out = Image.alpha_composite(out, fr)
    if 'plaid' in spec['props']:
        pl = Image.new('RGBA', (Wc, Hc_), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pl)
        step = max(6, int(0.035 * u))
        for x in range(0, Wc, step):
            pd.line((x, 0, x, Hc_), fill=(255, 255, 255, 70), width=max(1, int(0.008 * u)))
        for y in range(0, Hc_, step):
            pd.line((0, y, Wc, y), fill=(255, 255, 255, 70), width=max(1, int(0.008 * u)))
        m = np.array(front, np.float32) / 255
        m[: int(Hc[1] + ry * 1.2)] = 0
        pl.putalpha(Image.fromarray((np.array(pl.getchannel('A'), np.float32) * m).astype(np.uint8), 'L'))
        out = Image.alpha_composite(out, pl)
    edge = union.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    rim = Image.new('RGBA', (Wc, Hc_), (255, 255, 255, 0))
    rim.putalpha(edge.point(lambda v: int(min(255, v * 1.3) * 0.5)))
    out = Image.alpha_composite(out, rim)

    pr = Image.new('RGBA', (Wc, Hc_), (0, 0, 0, 0))
    d = ImageDraw.Draw(pr)
    ctx = dict(J=J, px=px, u=u, view=view, facing=facing, rx=rx, ry=ry, Hc=Hc, N=N, P=P, face=face_c,
               rot=rot, wind=wind, glint=glint, key=key, spec=spec)
    for p in spec['props']:
        PROPS.get(p, lambda *a: None)(d, ctx)
    draw_face(d, ctx, expr, talk)
    if sweat:
        sx, sy = Hc[0] + (rx * 1.25 if view == 'front' else -facing * rx * 0.9), Hc[1] - ry * 0.6
        s = 0.018 * u
        d.polygon([(sx, sy - 2 * s), (sx - s, sy), (sx + s, sy)], fill=(120, 200, 255, 255))
        d.ellipse((sx - s, sy - s * 0.6, sx + s, sy + s * 1.2), fill=(120, 200, 255, 255))
    if hold:
        for item, where in (hold.items() if isinstance(hold, dict) else [(hold, 'W1')]):
            HOLD[item](d, px(where), u, ctx)
    out = Image.alpha_composite(out, pr)
    if ss == 2:
        out = out.resize((Wc // 2, Hc_ // 2), Image.LANCZOS)
        return out, (ox / 2, oy / 2)
    return out, (ox, oy)


def put(frame, key, pose, x, y, h, **kw):
    """把小人画到 frame 上，骨盆落在 (x, y)。"""
    img, (px_, py_) = fig_layer(key, pose, h, **kw)
    frame.paste(img, (int(round(x - px_)), int(round(y - py_))), img)
    return img


# ---------------------------------------------------------------- 表情
def draw_face(d, c, expr, talk):
    hx, hy = c['Hc']
    rx, ry, u = c['rx'], c['ry'], c['u']
    view, f = c['view'], c['facing']
    eye = (22, 22, 28, 255)
    lw = max(2, int(0.008 * u))
    if view == 'front':
        eyes = [(hx - rx * 0.4, hy - ry * 0.05), (hx + rx * 0.4, hy - ry * 0.05)]
        mouth = (hx, hy + ry * 0.48)
    else:
        eyes = [(hx + f * rx * 0.48, hy - ry * 0.08)]
        mouth = (hx + f * rx * 0.62, hy + ry * 0.46)
    er = rx * 0.11
    for ex, ey in eyes:
        if expr in ('shock',):
            d.ellipse((ex - rx * 0.24, ey - rx * 0.24, ex + rx * 0.24, ey + rx * 0.24), fill=(250, 250, 250, 255))
            d.ellipse((ex - rx * 0.1, ey - rx * 0.1, ex + rx * 0.1, ey + rx * 0.1), fill=eye)
        elif expr in ('deadpan', 'squint'):
            w = rx * (0.22 if expr == 'deadpan' else 0.26)
            d.line((ex - w, ey, ex + w, ey), fill=eye, width=lw)
            if expr == 'squint':
                d.line((ex - w, ey - rx * 0.22, ex + w, ey - rx * 0.12 if ex > hx else ey - rx * 0.22), fill=eye, width=lw)
        elif expr == 'happy':
            d.arc((ex - rx * 0.18, ey - rx * 0.12, ex + rx * 0.18, ey + rx * 0.2), 200, 340, fill=eye, width=lw)
        elif expr == 'yell':
            d.line((ex - rx * 0.18, ey - rx * 0.12, ex + rx * 0.1, ey), fill=eye, width=lw)
            d.line((ex - rx * 0.18, ey + rx * 0.12, ex + rx * 0.1, ey), fill=eye, width=lw)
        else:
            d.ellipse((ex - er, ey - er * 1.2, ex + er, ey + er * 1.2), fill=eye)
        if expr in ('determined', 'question', 'sad'):
            dy = {'determined': (-0.28, -0.2), 'question': (-0.38, -0.3), 'sad': (-0.2, -0.3)}[expr]
            d.line((ex - rx * 0.2, ey + rx * dy[0], ex + rx * 0.2, ey + rx * dy[1]), fill=eye, width=lw)
    mx, my = mouth
    if expr in ('shock', 'yell') or talk > 0.05:
        a = 0.32 if expr in ('shock', 'yell') else 0.1 + 0.25 * talk
        w = rx * (0.18 if view == 'front' else 0.12)
        d.ellipse((mx - w, my - ry * a * 0.5, mx + w, my + ry * a * 0.5), fill=(70, 20, 30, 255))
    elif expr == 'happy':
        w = rx * 0.26
        d.chord((mx - w, my - ry * 0.16, mx + w, my + ry * 0.2), 0, 180, fill=(70, 20, 30, 255))
    elif expr == 'sad':
        d.arc((mx - rx * 0.2, my, mx + rx * 0.2, my + ry * 0.25), 200, 340, fill=eye, width=lw)
    else:
        w = rx * (0.16 if view == 'front' else 0.1)
        d.line((mx - w, my, mx + w, my), fill=eye, width=lw)


# ---------------------------------------------------------------- 道具
def _head_box(c, sx=1.0, sy=1.0, dx=0.0, dy=0.0):
    hx, hy = c['Hc']
    return (hx + dx - c['rx'] * sx, hy + dy - c['ry'] * sy, hx + dx + c['rx'] * sx, hy + dy + c['ry'] * sy)


def p_messy(d, c):
    hx, hy = c['Hc']
    rx, ry = c['rx'], c['ry']
    pts = []
    tilt = 0 if c['view'] == 'front' else -c['facing'] * 0.15
    for k in range(13):
        a = math.pi * (1.05 + 0.9 * k / 12) + tilt
        r = (1.0 if k % 2 == 0 else 1.5) * (1 + 0.05 * math.sin(k * 3))
        pts.append((hx + math.cos(a) * rx * r, hy + math.sin(a) * ry * r * 0.95 - ry * 0.05))
    d.polygon(pts + [(hx + rx * 0.9, hy - ry * 0.25), (hx - rx * 0.9, hy - ry * 0.25)], fill=(44, 44, 52, 255))


def p_bedhair(d, c):
    hx, hy = c['Hc']
    rx, ry = c['rx'], c['ry']
    d.chord(_head_box(c, 1.04, 1.04, 0, -ry * 0.04), 180, 360, fill=(70, 62, 56, 255))
    for k, a in enumerate((-0.5, -0.1, 0.35)):
        x = hx + a * rx
        d.polygon([(x - rx * 0.15, hy - ry * 0.85), (x + rx * (0.25 if k % 2 else -0.25), hy - ry * 1.4), (x + rx * 0.15, hy - ry * 0.85)],
                  fill=(70, 62, 56, 255))


def p_buzz(d, c):
    d.chord(_head_box(c, 1.02, 1.0, 0, -c['ry'] * 0.03), 190, 350, fill=(40, 46, 44, 255))


def p_curly(d, c):
    hx, hy = c['Hc']
    rx, ry = c['rx'], c['ry']
    for k in range(9):
        a = math.pi * (1.0 + k / 8)
        x, y = hx + math.cos(a) * rx * 0.92, hy + math.sin(a) * ry * 0.85 - ry * 0.1
        r = rx * 0.32
        d.ellipse((x - r, y - r, x + r, y + r), fill=(56, 40, 40, 255))


def p_longhair(d, c):
    hx, hy = c['Hc']
    rx, ry, u = c['rx'], c['ry'], c['u']
    hair = (46, 30, 72, 255) if c['key'] == 'xingxing' else (70, 40, 50, 255)
    N = c['N']
    w = c['wind']
    if c['view'] == 'front':
        d.ellipse(_head_box(c, 1.12, 1.1, 0, -ry * 0.05), fill=hair)
        x0, x1 = hx - rx * 1.12, hx + rx * 1.12
        sway = w * rx * 3.2
        d.polygon([(x0, hy), (x1, hy), (x1 + sway, N[1] + 0.07 * u - w * 0.08 * u), (x0 + sway * 1.2, N[1] + 0.08 * u - w * 0.1 * u)], fill=hair)
        d.ellipse(_head_box(c, 0.8, 0.86, 0, ry * 0.12), fill=c['face'] + (255,))
        d.chord(_head_box(c, 0.98, 0.92, 0, -ry * 0.12), 180, 360, fill=hair)
    else:
        f = c['facing']
        d.ellipse(_head_box(c, 1.1, 1.08, -f * rx * 0.12, -ry * 0.04), fill=hair)
        bx = hx - f * rx * 0.9
        d.polygon([(bx - rx * 0.5, hy), (bx + rx * 0.5, hy), (bx + rx * 0.3 - f * w * rx * 2, N[1] + 0.09 * u),
                   (bx - rx * 0.6 - f * w * rx * 3, N[1] + 0.08 * u)], fill=hair)
        d.ellipse(_head_box(c, 0.72, 0.8, f * rx * 0.3, ry * 0.14), fill=c['face'] + (255,))


def p_scarf(d, c):
    N, u = c['N'], c['u']
    hx = c['Hc'][0]
    y = N[1] - 0.005 * u
    w = 0.07 * u
    red = (222, 48, 60, 255)
    d.rounded_rectangle((N[0] - w, y - 0.02 * u, N[0] + w, y + 0.022 * u), radius=0.02 * u, fill=red)
    if c['view'] == 'front':
        d.polygon([(N[0] + w * 0.3, y), (N[0] + w * 0.8, y), (N[0] + w * 0.9, y + 0.11 * u), (N[0] + w * 0.45, y + 0.11 * u)],
                  fill=(198, 38, 50, 255))
    else:
        f = c['facing']
        d.polygon([(N[0] - f * w * 0.6, y), (N[0] - f * w * 1.0, y), (N[0] - f * w * 1.9, y + 0.07 * u), (N[0] - f * w * 1.5, y + 0.09 * u)],
                  fill=(198, 38, 50, 255))


def p_phones_neck(d, c):
    N, u = c['N'], c['u']
    rx = c['rx']
    y = N[1] - 0.004 * u
    cup = (30, 30, 36, 255)
    if c['view'] == 'front':
        d.arc((N[0] - rx * 1.0, y - 0.03 * u, N[0] + rx * 1.0, y + 0.05 * u), 0, 180, fill=cup, width=max(2, int(0.012 * u)))
        for sx in (-1, 1):
            x = N[0] + sx * rx * 0.95
            r = rx * 0.34
            d.ellipse((x - r, y - r * 0.7, x + r, y + r * 1.1), fill=cup, outline=(255, 150, 60, 255), width=max(1, int(0.006 * u)))
    else:
        x = N[0] + c['facing'] * rx * 0.25
        r = rx * 0.36
        d.ellipse((x - r, y - r * 0.6, x + r, y + r * 1.2), fill=cup, outline=(255, 150, 60, 255), width=max(1, int(0.006 * u)))


def p_phones_head(d, c):
    hx, hy = c['Hc']
    rx, ry, u = c['rx'], c['ry'], c['u']
    cup = (30, 30, 36, 255)
    if c['view'] == 'front':
        d.arc(_head_box(c, 1.15, 1.18, 0, -ry * 0.05), 180, 360, fill=cup, width=max(2, int(0.014 * u)))
        for sx in (-1, 1):
            x = hx + sx * rx * 1.05
            d.rounded_rectangle((x - rx * 0.2, hy - ry * 0.3, x + rx * 0.2, hy + ry * 0.35), radius=rx * 0.1, fill=cup)
    else:
        d.arc(_head_box(c, 1.1, 1.16, 0, -ry * 0.05), 200, 340, fill=cup, width=max(2, int(0.014 * u)))
        x = hx - c['facing'] * rx * 0.1
        d.ellipse((x - rx * 0.38, hy - ry * 0.35, x + rx * 0.38, hy + ry * 0.4), fill=cup)


def p_glasses(d, c):
    hx, hy = c['Hc']
    rx, ry, u = c['rx'], c['ry'], c['u']
    k = (12, 12, 12, 255)
    lw = max(2, int(0.008 * u))
    y = hy - ry * 0.05
    if c['view'] == 'front':
        for sx in (-1, 1):
            x = hx + sx * rx * 0.42
            d.rounded_rectangle((x - rx * 0.3, y - ry * 0.2, x + rx * 0.3, y + ry * 0.2), radius=rx * 0.08, outline=k, width=lw)
            if c['glint']:
                d.line((x - rx * 0.2, y - ry * 0.1, x - rx * 0.02, y - ry * 0.1), fill=(255, 255, 255, 255), width=lw)
        d.line((hx - rx * 0.12, y, hx + rx * 0.12, y), fill=k, width=lw)
    else:
        f = c['facing']
        x = hx + f * rx * 0.5
        d.rounded_rectangle((x - rx * 0.24, y - ry * 0.2, x + rx * 0.24, y + ry * 0.2), radius=rx * 0.08, outline=k, width=lw)
        d.line((x - f * rx * 0.24, y, hx - f * rx * 0.55, y - ry * 0.05), fill=k, width=lw)


def p_helmet(d, c):
    hx, hy = c['Hc']
    rx, ry, u = c['rx'], c['ry'], c['u']
    hel = (34, 34, 42, 255)
    d.pieslice(_head_box(c, 1.18, 1.18, 0, -ry * 0.02), 180, 360, fill=hel)
    d.rectangle((hx - rx * 1.18, hy - ry * 0.12, hx + rx * 1.18, hy + ry * 0.02), fill=hel)
    d.line((hx - rx * 1.1, hy - ry * 0.06, hx + rx * 1.1, hy - ry * 0.06), fill=(255, 200, 60, 255), width=max(2, int(0.01 * u)))
    if c['view'] == 'side':
        f = c['facing']
        d.polygon([(hx + f * rx * 0.9, hy - ry * 0.1), (hx + f * rx * 1.5, hy - ry * 0.02), (hx + f * rx * 0.9, hy + ry * 0.05)], fill=hel)


def p_cap(d, c):
    hx, hy = c['Hc']
    rx, ry, u = c['rx'], c['ry'], c['u']
    cap = (36, 46, 80, 255)
    d.rectangle((hx - rx * 1.02, hy - ry * 1.12, hx + rx * 1.02, hy - ry * 0.42), fill=cap)
    d.ellipse((hx - rx * 0.25, hy - ry * 0.95, hx + rx * 0.25, hy - ry * 0.62), fill=(230, 200, 90, 255))
    if c['view'] == 'front':
        d.rectangle((hx - rx * 1.1, hy - ry * 0.5, hx + rx * 1.1, hy - ry * 0.36), fill=(20, 24, 40, 255))
    else:
        f = c['facing']
        d.polygon([(hx, hy - ry * 0.5), (hx + f * rx * 1.6, hy - ry * 0.42), (hx + f * rx * 1.6, hy - ry * 0.32), (hx, hy - ry * 0.36)],
                  fill=(20, 24, 40, 255))


def p_bib(d, c):
    N, P, u = c['N'], c['P'], c['u']
    cx = N[0] + (P[0] - N[0]) * 0.4
    cy = N[1] + (P[1] - N[1]) * 0.4
    if c['view'] == 'front':
        w, h = 0.075 * u, 0.06 * u
        d.rounded_rectangle((cx - w, cy - h, cx + w, cy + h), radius=0.01 * u, fill=(246, 246, 246, 255), outline=(30, 30, 30, 255),
                            width=max(1, int(0.004 * u)))
        d.text((cx, cy + 0.004 * u), '50', font=F('Black', max(8, int(0.085 * u))), fill=(20, 20, 20, 255), anchor='mm')
    else:
        f = c['facing']
        x = cx + f * 0.05 * u
        d.rectangle((x - 0.012 * u, cy - 0.05 * u, x + 0.012 * u, cy + 0.05 * u), fill=(246, 246, 246, 255))


def p_backpack(d, c):
    N, P, u = c['N'], c['P'], c['u']
    if c['view'] == 'side':
        f = c['facing']
        x = (N[0] + P[0]) / 2 - f * 0.085 * u
        y = (N[1] + P[1]) / 2 - 0.02 * u
        d.rounded_rectangle((x - 0.05 * u, y - 0.09 * u, x + 0.05 * u, y + 0.09 * u), radius=0.02 * u, fill=(26, 26, 32, 255))
    else:
        for sx in (-1, 1):
            x = N[0] + sx * 0.06 * u
            d.line((x, N[1] + 0.03 * u, x + sx * 0.01 * u, P[1] - 0.02 * u), fill=(26, 26, 32, 255), width=max(2, int(0.022 * u)))


def p_towel(d, c):
    N, u = c['N'], c['u']
    if c['view'] == 'front':
        d.polygon([(N[0] - 0.02 * u, N[1] + 0.01 * u), (N[0] + 0.04 * u, N[1] - 0.005 * u), (N[0] + 0.13 * u, N[1] + 0.03 * u),
                   (N[0] + 0.1 * u, N[1] + 0.16 * u), (N[0] + 0.05 * u, N[1] + 0.16 * u), (N[0] + 0.06 * u, N[1] + 0.04 * u)],
                  fill=(240, 240, 236, 255))
    else:
        d.rectangle((N[0] - 0.03 * u, N[1], N[0] + 0.03 * u, N[1] + 0.12 * u), fill=(240, 240, 236, 255))


def p_toothbrush(d, c):
    hx, hy = c['Hc']
    rx, ry, u = c['rx'], c['ry'], c['u']
    lw = max(2, int(0.012 * u))
    if c['view'] == 'front':
        x0, y0 = hx + rx * 0.05, hy + ry * 0.48
        d.line((x0, y0, x0 + rx * 0.9, y0 + ry * 0.2), fill=(90, 160, 255, 255), width=lw)
        d.line((x0, y0, x0 + rx * 0.18, y0 + ry * 0.04), fill=(250, 250, 250, 255), width=lw)
    else:
        f = c['facing']
        x0, y0 = hx + f * rx * 0.62, hy + ry * 0.46
        d.line((x0, y0, x0 + f * rx * 0.9, y0 + ry * 0.08), fill=(90, 160, 255, 255), width=lw)


def p_keys(d, c):
    P, u = c['P'], c['u']
    x = P[0] + (0.09 * u if c['view'] == 'front' else -c['facing'] * 0.03 * u)
    y = P[1] - 0.01 * u
    r = 0.02 * u
    d.ellipse((x - r, y - r, x + r, y + r), outline=(210, 210, 220, 255), width=max(1, int(0.006 * u)))
    for k in (-1, 0, 1):
        d.line((x + k * r * 0.6, y + r, x + k * r * 0.9, y + r * 2.4), fill=(210, 210, 220, 255), width=max(1, int(0.008 * u)))


def p_skates(d, c):
    J, px, u = c['J'], c['px'], c['u']
    for i in range(2):
        if f'A{i}' not in J:
            continue
        A, Fp = px(f'A{i}'), px(f'F{i}')
        d.line((A, Fp), fill=(30, 30, 34, 255), width=max(2, int(0.05 * u)))
        for k in (0.0, 0.5, 1.0):
            x = A[0] + (Fp[0] - A[0]) * k
            y = A[1] + (Fp[1] - A[1]) * k + 0.035 * u
            r = 0.016 * u
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 200, 60, 255))


PROPS = dict(messy=p_messy, bedhair=p_bedhair, buzz=p_buzz, curly=p_curly, longhair=p_longhair, scarf=p_scarf,
             phones_neck=p_phones_neck, phones_head=p_phones_head, glasses=p_glasses, helmet=p_helmet, cap=p_cap,
             bib=p_bib, backpack=p_backpack, towel=p_towel, toothbrush=p_toothbrush, keys=p_keys, skates=p_skates)


# ---------------------------------------------------------------- 手里拿的东西
def draw_bag(d, x, y, s, alpha=255):
    """红色外卖保温袋，(x, y) 是袋子中心，s 是袋子宽度（像素）。"""
    w, h = s / 2, s * 0.42
    d.rounded_rectangle((x - w, y - h, x + w, y + h), radius=s * 0.12, fill=(220, 40, 52, alpha), outline=(120, 16, 24, alpha),
                        width=max(1, int(s * 0.04)))
    d.rounded_rectangle((x - w * 0.62, y - h - s * 0.14, x + w * 0.62, y - h + s * 0.05), radius=s * 0.05, fill=(248, 248, 244, alpha))
    d.line((x - w * 0.8, y - h * 0.35, x + w * 0.8, y - h * 0.35), fill=(150, 20, 30, alpha), width=max(1, int(s * 0.03)))
    d.arc((x - w * 0.5, y - h - s * 0.36, x + w * 0.5, y - h + s * 0.1), 200, 340, fill=(120, 16, 24, alpha), width=max(1, int(s * 0.05)))


def h_bag(d, p, u, c):
    draw_bag(d, p[0], p[1] + 0.05 * u, 0.13 * u)


def h_remote(d, p, u, c):
    x, y = p
    d.rounded_rectangle((x - 0.04 * u, y - 0.02 * u, x + 0.04 * u, y + 0.025 * u), radius=0.008 * u, fill=(40, 40, 48, 255),
                        outline=(205, 205, 215, 255), width=max(1, int(0.003 * u)))
    for sx in (-1, 1):
        d.line((x + sx * 0.03 * u, y - 0.02 * u, x + sx * 0.038 * u, y - 0.06 * u), fill=(205, 205, 215, 255), width=max(1, int(0.004 * u)))


def h_thermos(d, p, u, c):
    x, y = p
    d.rounded_rectangle((x - 0.022 * u, y - 0.07 * u, x + 0.022 * u, y + 0.03 * u), radius=0.008 * u, fill=(200, 205, 215, 255))
    d.rectangle((x - 0.024 * u, y - 0.08 * u, x + 0.024 * u, y - 0.065 * u), fill=(90, 90, 100, 255))


def h_phone(d, p, u, c):
    x, y = p
    d.rounded_rectangle((x - 0.018 * u, y - 0.04 * u, x + 0.018 * u, y + 0.03 * u), radius=0.006 * u, fill=(20, 20, 26, 255),
                        outline=(120, 170, 255, 255), width=max(1, int(0.003 * u)))


def h_cup(d, p, u, c):
    x, y = p
    d.polygon([(x - 0.025 * u, y - 0.05 * u), (x + 0.025 * u, y - 0.05 * u), (x + 0.02 * u, y + 0.03 * u), (x - 0.02 * u, y + 0.03 * u)],
              fill=(235, 220, 200, 255))
    if not c.get('lid_off'):
        d.rectangle((x - 0.028 * u, y - 0.058 * u, x + 0.028 * u, y - 0.048 * u), fill=(250, 250, 250, 255))
        d.line((x + 0.005 * u, y - 0.058 * u, x + 0.012 * u, y - 0.1 * u), fill=(255, 120, 150, 255), width=max(1, int(0.006 * u)))


def h_wing(d, p, u, c):
    x, y = p
    d.ellipse((x - 0.03 * u, y - 0.018 * u, x + 0.03 * u, y + 0.018 * u), fill=(196, 120, 50, 255))
    d.ellipse((x + 0.015 * u, y - 0.01 * u, x + 0.045 * u, y + 0.012 * u), fill=(176, 100, 40, 255))


HOLD = dict(bag=h_bag, remote=h_remote, thermos=h_thermos, phone=h_phone, cup=h_cup, wing=h_wing)


# ---------------------------------------------------------------- 常用姿势
def stand(view='front'):
    if view == 'front':
        return dict(view='front', arms=((8, 4), (8, 4)), legs=((3, 0), (3, 0)))
    return dict(view='side', arms=((-6, 10), (6, 12)), legs=((-3, 3), (4, 3)))


def run(ph, lean=16, amp=1.0, arms=None):
    legs, arm = [], []
    for i in range(2):
        q = ph + i * math.pi
        legs.append((amp * 40 * math.sin(q) + 6, 20 + 70 * (0.5 + 0.5 * math.sin(q - math.pi / 2))))
        arm.append((-amp * 48 * math.sin(q), 85))
    return dict(view='side', lean=lean, head=-lean * 0.6, arms=tuple(arms) if arms else tuple(arm), legs=tuple(legs))


def run_bob(ph, h, amp=1.0):
    return -0.025 * h * abs(math.cos(ph)) * amp
