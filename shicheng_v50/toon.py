# -*- coding: utf-8 -*-
"""卡通角色：描边、表情、发型、衣服、手里的东西。

坐标单位是身高 h：骨盆在 (0, 0)，y 向下为正，脚底约在 +0.44，头顶约在 -0.56。
姿势 pose = dict(
    view='front' | 'side', lean=躯干倾斜, head=头部倾斜, rot=整个人绕骨盆转（顺时针为正，单位度）,
    arms=(左/后手臂, 右/前手臂), legs=(左/后腿, 右/前腿), hands=('fist'|'open'|'point'|'thumb', ...),
    bust=True 时不画腿,
)
手臂/腿可以写成角度 (a, b)：a 从朝下往外（侧面是往前）转，b 是肘/膝再弯的角度；
也可以写成 IK：{'ik': (x, y), 'rel': 'P'|'N'|'Hc', 'bend': ±1}。
表情 expr 可以是预设名（见 EXPR），也可以是 dict(eyes=, brows=, mouth=, blush=, fx=[...])。
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import render_hero_select as hero

F = hero.F
INK = (36, 28, 44)
WHITE = (255, 255, 255)
B = dict(torso=0.31, neck=0.025, upper=0.17, fore=0.16, thigh=0.215, shin=0.205, foot=0.085)
HEAD_RX, HEAD_RY, HEAD_UP = 0.11, 0.12, 0.10


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def dk(c, k=0.78):
    return tuple(int(v * k) for v in c[:3])


def lt(c, k=0.3):
    return tuple(int(v + (255 - v) * k) for v in c[:3])


SKIN = dict(light=rgb('F6D8BE'), mid=rgb('EFC6A2'), tan=rgb('D9A276'), old=rgb('E9C3A0'))

CH = {
    'dacong': dict(skin=SKIN['light'], hair='messy', hair_c=rgb('2A2A3A'), top='pajama', top_c=rgb('8DB6F2'), pat_c=WHITE,
                   sleeve=2, bottom='pants', bottom_c=rgb('8DB6F2'), shoes='flipflop', shoe_c=rgb('3C9BE0'), eye_c=rgb('5B3A29'),
                   face=(1.08, 1.0), sw=0.25, hw=0.2, arm=1.0, leg=1.0, acc=('phones_neck',)),
    'afei': dict(skin=SKIN['tan'], hair='spiky', hair_c=rgb('3A2418'), top='tank', top_c=rgb('E8394A'), pat_c=WHITE, sleeve=0,
                 bottom='shorts', bottom_c=rgb('25252E'), shoes='sneaker', shoe_c=rgb('B8F23C'), eye_c=rgb('3B2416'),
                 face=(1.02, 1.0), sw=0.31, hw=0.21, arm=1.45, leg=1.2, acc=('headband', 'bib'), brow=1.5),
    'xiaok': dict(skin=SKIN['light'], hair='none', hair_c=rgb('222222'), top='hoodie', top_c=rgb('8B8F99'), pat_c=rgb('6B6F78'),
                  sleeve=2, bottom='pants', bottom_c=rgb('2B2D35'), shoes='skate', shoe_c=rgb('202024'), eye_c=rgb('2F2A40'),
                  face=(1.0, 1.0), sw=0.25, hw=0.2, arm=1.0, leg=1.0, acc=('helmet', 'bandaid', 'kneepads')),
    'laozhou': dict(skin=SKIN['light'], hair='sidepart', hair_c=rgb('231E1C'), top='shirt', top_c=rgb('4E86D6'), pat_c=rgb('2E5FA8'),
                    sleeve=2, bottom='pants', bottom_c=rgb('C9B48A'), shoes='shoe', shoe_c=rgb('6A4A34'), eye_c=rgb('2A2A30'),
                    face=(0.96, 1.04), sw=0.24, hw=0.2, arm=0.95, leg=1.0, acc=('glasses', 'backpack')),
    'xingxing': dict(skin=SKIN['light'], hair='long', hair_c=rgb('241B33'), top='puffer', top_c=rgb('F4F4F8'), pat_c=rgb('C9CBD6'),
                     sleeve=2, bottom='pants', bottom_c=rgb('3A3550'), shoes='sneaker', shoe_c=WHITE, eye_c=rgb('6B4BA8'),
                     face=(0.98, 1.0), sw=0.24, hw=0.21, arm=0.95, leg=0.95, acc=('scarf', 'starclip'), lash=True),
    'suguan': dict(skin=SKIN['old'], hair='curly', hair_c=rgb('4A4248'), top='cardigan', top_c=rgb('C8323C'), pat_c=rgb('F6F0E6'),
                   sleeve=2, bottom='pants', bottom_c=rgb('2E2B33'), shoes='shoe', shoe_c=rgb('1E1E22'), eye_c=rgb('3A2A20'),
                   face=(1.06, 0.98), sw=0.27, hw=0.25, arm=1.05, leg=1.0, acc=('halfglasses', 'keys'), lash=True, old=True),
    'roomA': dict(skin=SKIN['light'], hair='neat', hair_c=rgb('1F1B1A'), top='tee', top_c=rgb('9AA3B0'), pat_c=WHITE, sleeve=0.6,
                  bottom='pants', bottom_c=rgb('34405C'), shoes='sneaker', shoe_c=WHITE, eye_c=rgb('2A2A30'),
                  face=(0.98, 1.02), sw=0.24, hw=0.2, arm=1.0, leg=1.0, acc=('roundglasses', 'phones_head')),
    'roomB': dict(skin=SKIN['light'], hair='bedhead', hair_c=rgb('5A4636'), top='tank', top_c=rgb('F2F2EE'), pat_c=rgb('D8D8D0'),
                  sleeve=0, bottom='shorts', bottom_c=rgb('5C79B8'), shoes='flipflop', shoe_c=rgb('F2A33C'), eye_c=rgb('4A3828'),
                  face=(1.0, 1.0), sw=0.24, hw=0.2, arm=1.0, leg=1.0, acc=()),
    'roomC': dict(skin=SKIN['mid'], hair='buzz', hair_c=rgb('2A2A2A'), top='tee', top_c=rgb('2B2B33'), pat_c=WHITE, sleeve=0.6,
                  bottom='pants', bottom_c=rgb('8A8E98'), shoes='flipflop', shoe_c=rgb('3CC27A'), eye_c=rgb('2A2A30'),
                  face=(1.02, 1.0), sw=0.25, hw=0.2, arm=1.0, leg=1.0, acc=('towel', 'toothbrush')),
    'guard': dict(skin=SKIN['old'], hair='buzz', hair_c=rgb('B8B8B8'), top='uniform', top_c=rgb('2F4777'), pat_c=rgb('F2C84B'),
                  sleeve=2, bottom='pants', bottom_c=rgb('243656'), shoes='shoe', shoe_c=rgb('1E1E22'), eye_c=rgb('2A2A30'),
                  face=(1.05, 1.0), sw=0.26, hw=0.23, arm=1.0, leg=1.0, acc=('guardcap', 'mustache'), old=True),
    'girl': dict(skin=SKIN['light'], hair='ponytail', hair_c=rgb('4A2C24'), top='hoodie', top_c=rgb('F29BB8'), pat_c=rgb('E07A9E'),
                 sleeve=2, bottom='pants', bottom_c=rgb('7EA6D8'), shoes='sneaker', shoe_c=WHITE, eye_c=rgb('5B3A29'),
                 face=(0.98, 1.0), sw=0.22, hw=0.2, arm=0.9, leg=0.92, acc=(), lash=True),
    'rider': dict(skin=SKIN['tan'], hair='none', hair_c=rgb('222222'), top='jacket', top_c=rgb('F5C431'), pat_c=rgb('D9A514'),
                  sleeve=2, bottom='pants', bottom_c=rgb('2B2D35'), shoes='sneaker', shoe_c=rgb('333333'), eye_c=rgb('2A2A30'),
                  face=(1.04, 1.0), sw=0.26, hw=0.21, arm=1.05, leg=1.0, acc=('helmet',), helmet_c=rgb('F5C431'), helmet_s=WHITE),
    'boy': dict(skin=SKIN['mid'], hair='short', hair_c=rgb('2A2220'), top='jacket', top_c=rgb('5DAE7A'), pat_c=rgb('3F8A5A'),
                sleeve=2, bottom='pants', bottom_c=rgb('2E3448'), shoes='sneaker', shoe_c=rgb('E8E8E8'), eye_c=rgb('2A2A30'),
                face=(1.0, 1.0), sw=0.25, hw=0.2, arm=1.0, leg=1.0, acc=()),
}

CROWD_LOOKS = [
    dict(hair='short', hair_c=rgb('2A2220'), top='tee', top_c=rgb('F2B84B'), bottom_c=rgb('2E3448')),
    dict(hair='bob', hair_c=rgb('3B2A22'), top='hoodie', top_c=rgb('7FC8E8'), bottom_c=rgb('3A3550'), lash=True),
    dict(hair='bun', hair_c=rgb('1E1A1A'), top='tee', top_c=rgb('B98BE0'), bottom_c=rgb('2B2D35'), lash=True),
    dict(hair='spiky', hair_c=rgb('5A3A22'), top='jacket', top_c=rgb('E8704A'), bottom_c=rgb('34405C')),
    dict(hair='neat', hair_c=rgb('222222'), top='tee', top_c=rgb('6CCB8E'), bottom_c=rgb('5C5C66')),
    dict(hair='ponytail', hair_c=rgb('6B4430'), top='hoodie', top_c=rgb('F2E2B8'), bottom_c=rgb('5C79B8'), lash=True),
]


def crowd_char(i):
    base = dict(CH['boy'])
    base.update(sleeve=0.6 if CROWD_LOOKS[i % 6]['top'] == 'tee' else 2, acc=(), lash=False)
    base.update(CROWD_LOOKS[i % len(CROWD_LOOKS)])
    base['skin'] = [SKIN['light'], SKIN['mid'], SKIN['tan']][i % 3]
    return base


# ---------------------------------------------------------------- 表情预设
EXPR = {
    'neutral': dict(eyes='open', brows='flat', mouth='smile_small'),
    'smile': dict(eyes='open', brows='up', mouth='smile', blush=0.35),
    'happy': dict(eyes='happy', brows='up', mouth='grin', blush=0.6),
    'laugh': dict(eyes='happy', brows='up', mouth='laugh', blush=0.7, fx=('joy_tears',)),
    'excited': dict(eyes='star', brows='up', mouth='laugh', blush=0.6, fx=('sparkle',)),
    'love': dict(eyes='heart', brows='up', mouth='grin', blush=0.9, fx=('hearts',)),
    'shock': dict(eyes='shock', brows='high', mouth='O', fx=('shock', 'sweat')),
    'scream': dict(eyes='x', brows='high', mouth='scream', fx=('shock', 'sweats')),
    'panic': dict(eyes='shock', brows='worried', mouth='wavy', fx=('sweats', 'gloom')),
    'cry': dict(eyes='cry', brows='sad', mouth='wail', blush=0.4, fx=('tears',)),
    'moved': dict(eyes='teary', brows='sad', mouth='wobble', blush=0.7, fx=('sparkle',)),
    'angry': dict(eyes='angry', brows='angry', mouth='grit', fx=('anger',)),
    'determined': dict(eyes='determined', brows='determined', mouth='grit'),
    'fired': dict(eyes='fire', brows='angry', mouth='grin', fx=('sparkle',)),
    'smug': dict(eyes='half', brows='sly', mouth='smirk', blush=0.2),
    'cool': dict(eyes='half', brows='determined', mouth='smirk'),
    'deadpan': dict(eyes='half', brows='flat', mouth='flat'),
    'dead': dict(eyes='dot', brows='flat', mouth='flat', fx=('gloom',)),
    'judge': dict(eyes='half', brows='sly', mouth='flat'),
    'nervous': dict(eyes='open', brows='worried', mouth='wavy', look=(0.8, 0.0), fx=('sweat',)),
    'sad': dict(eyes='teary', brows='sad', mouth='frown'),
    'dizzy': dict(eyes='spiral', brows='worried', mouth='wavy'),
    'sleepy': dict(eyes='line', brows='flat', mouth='o', fx=('zzz',)),
    'stern': dict(eyes='half', brows='angry', mouth='flat'),
    'sly': dict(eyes='sly', brows='up', mouth='cat', blush=0.3),
    'confused': dict(eyes='open', brows='sly', mouth='wavy', fx=('question',)),
    'drool': dict(eyes='star', brows='up', mouth='drool', blush=0.5),
    'soul': dict(eyes='dot', brows='flat', mouth='O', fx=('soul', 'gloom')),
    'wink': dict(eyes=('open', 'happy'), brows='up', mouth='grin', blush=0.4),
    'focus': dict(eyes='open', brows='determined', mouth='flat', look=(0.6, -0.2)),
}

BROWS = dict(flat=(0.0, 0.0), up=(-0.08, -0.05), high=(-0.22, -0.14), angry=(0.12, -0.08), sad=(-0.12, 0.07),
             determined=(0.09, -0.04), worried=(-0.15, 0.03))


def resolve_expr(expr):
    e = dict(EXPR.get(expr, EXPR['neutral'])) if isinstance(expr, str) else dict(expr)
    e.setdefault('eyes', 'open')
    e.setdefault('brows', 'flat')
    e.setdefault('mouth', 'smile_small')
    e.setdefault('blush', 0.0)
    e.setdefault('fx', ())
    e.setdefault('look', (0.0, 0.0))
    return e


# ---------------------------------------------------------------- 骨架
def rad(d):
    return d * math.pi / 180


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def rot2(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def ik2(S, T, L1, L2, bend):
    dx, dy = T[0] - S[0], T[1] - S[1]
    d = max(abs(L1 - L2) + 1e-6, min(math.hypot(dx, dy), L1 + L2 - 1e-6))
    a = math.atan2(dy, dx)
    b = math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    ang = a + bend * b
    E = (S[0] + L1 * math.cos(ang), S[1] + L1 * math.sin(ang))
    Wr = (S[0] + d * math.cos(a), S[1] + d * math.sin(a))
    return E, Wr


def joints(c, pose, facing=1):
    view = pose.get('view', 'front')
    lean, head = rad(pose.get('lean', 0)), rad(pose.get('head', 0))
    f = facing if view == 'side' else 1

    def up(L, a):
        return (f * L * math.sin(a), -L * math.cos(a))

    def down(L, a):
        return (f * L * math.sin(a), L * math.cos(a))

    P = (0.0, 0.0)
    N = add(P, up(B['torso'], lean))
    Hc = add(N, up(B['neck'] + HEAD_UP, lean + head))
    J = dict(P=P, N=N, Hc=Hc)
    U, Fo = B['upper'], B['fore']
    for i in range(2):
        side = (-1, 1)[i]
        S = add(N, down(0.045, lean)) if view == 'side' else add(N, rot2((side * c['sw'] * 0.4, 0.04), lean))
        arm = pose.get('arms', ((6, 6), (6, 6)))[i]
        if isinstance(arm, dict):
            T = add(J[arm.get('rel', 'P')], ((f * arm['ik'][0]) if view == 'side' else arm['ik'][0], arm['ik'][1]))
            E, Wr = ik2(S, T, U, Fo, arm.get('bend', 1) * (f if view == 'side' else 1))
        else:
            sa, ea = rad(arm[0]), rad(arm[1])
            if view == 'side':
                E = add(S, down(U, lean + sa))
                Wr = add(E, down(Fo, lean + sa + ea))
            else:
                E = add(S, (side * U * math.sin(sa), U * math.cos(sa)))
                Wr = add(E, (side * Fo * math.sin(sa + ea), Fo * math.cos(sa + ea)))
        J[f'S{i}'], J[f'E{i}'], J[f'W{i}'] = S, E, Wr
        Th, Sh = B['thigh'] * pose.get('thigh_k', 1.0), B['shin']
        Hp = add(P, (0.0, 0.0)) if view == 'side' else add(P, rot2((side * c['hw'] * 0.27, 0.0), lean * 0.3))
        leg = pose.get('legs', ((2, 0), (2, 0)))[i]
        if isinstance(leg, dict):
            T = add(J[leg.get('rel', 'P')], ((f * leg['ik'][0]) if view == 'side' else leg['ik'][0], leg['ik'][1]))
            K, A = ik2(Hp, T, Th, Sh, leg.get('bend', -1) * (f if view == 'side' else 1))
        else:
            ta, ka = rad(leg[0]), rad(leg[1])
            if view == 'side':
                K = add(Hp, down(Th, ta))
                A = add(K, down(Sh, ta - ka))
            else:
                K = add(Hp, (side * Th * math.sin(ta), Th * math.cos(ta)))
                A = add(K, (side * Sh * math.sin(ta - ka), Sh * math.cos(ta - ka)))
        J[f'H{i}'], J[f'K{i}'], J[f'A{i}'] = Hp, K, A
        J[f'F{i}'] = add(A, (f * B['foot'], 0.012)) if view == 'side' else add(A, (side * 0.012, 0.012))
    r = rad(pose.get('rot', 0))
    if r:
        J = {k: rot2(v, r) for k, v in J.items()}
    J['_head_ang'] = r + (f * (lean + head) if view == 'side' else lean + head)
    return J


def foot_y(key, pose, facing=1):
    c = CH[key] if isinstance(key, str) else key
    J = joints(c, pose, facing)
    return max(J['A0'][1], J['A1'][1]) + 0.04


# ---------------------------------------------------------------- 描边画法
def ocircle(d, p, r, fill, ow, ink=INK):
    d.ellipse((p[0] - r - ow, p[1] - r - ow, p[0] + r + ow, p[1] + r + ow), fill=ink)
    d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)


def opoly_outline(d, pts, ow, ink=INK):
    d.polygon(pts, fill=ink)
    d.line(list(pts) + [pts[0]], fill=ink, width=max(1, int(round(2 * ow))))
    for p in pts:
        d.ellipse((p[0] - ow, p[1] - ow, p[0] + ow, p[1] + ow), fill=ink)


def opoly(d, pts, fill, ow, ink=INK):
    opoly_outline(d, pts, ow, ink)
    d.polygon(pts, fill=fill)


def seg_line(d, a, b, w, col):
    d.line((a, b), fill=col, width=max(1, int(round(w))))
    r = w / 2
    for p in (a, b):
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=col)


def lerp2(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def split_chain(chain, cover):
    """chain=[(p0, p1, w)]，cover=[(到哪儿为止(0..1), 颜色)] -> [(a, b, w, 颜色)]。"""
    lens = [math.dist(a, b) for a, b, _ in chain]
    total = sum(lens) or 1.0
    out, acc = [], 0.0
    for (a, b, w), L in zip(chain, lens):
        t0, t1 = acc / total, (acc + L) / total
        cuts = [t0] + [c for c, _ in cover if t0 < c < t1] + [t1]
        for u0, u1 in zip(cuts, cuts[1:]):
            mid = (u0 + u1) / 2
            col = next(cc for c, cc in cover if mid <= c + 1e-9)
            out.append((lerp2(a, b, (u0 - t0) / (t1 - t0)), lerp2(a, b, (u1 - t0) / (t1 - t0)), w, col))
        acc += L
    return out


def draw_limb(d, chain, cover, ow, skin, pattern=None):
    segs = split_chain(chain, cover)
    for a, b, w, _ in segs:
        seg_line(d, a, b, w + 2 * ow, INK)
    for a, b, w, col in sorted(segs, key=lambda s: 0 if s[3] == skin else 1):
        seg_line(d, a, b, w, col)
    for (a, b, w, col), (a2, b2, w2, col2) in zip(segs, segs[1:]):
        if col != col2:
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            ww = max(w, w2) / 2
            d.line(((b[0] - nx * ww, b[1] - ny * ww), (b[0] + nx * ww, b[1] + ny * ww)), fill=INK, width=max(1, int(ow)))
    if pattern:
        col, step, kinds = pattern
        for a, b, w, c in segs:
            if c == skin:
                continue
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            if L < 1:
                continue
            nx, ny = -dy / L, dx / L
            n = int(L // step)
            for k in range(1, n + 1):
                p = lerp2(a, b, k * step / L)
                d.line(((p[0] - nx * w * 0.42, p[1] - ny * w * 0.42), (p[0] + nx * w * 0.42, p[1] + ny * w * 0.42)),
                       fill=col, width=max(1, int(ow * 0.6)))
            if 'center' in kinds:
                d.line((a, b), fill=col, width=max(1, int(ow * 0.6)))


# ---------------------------------------------------------------- 脸
def draw_eye(d, ex, ey, rw, rh, kind, side, look, iris_c, ow, skin, lash=False, t=0.0):
    ew = max(1, int(ow * 0.7))
    inner = -side
    if kind in ('open', 'half', 'sly', 'angry', 'determined', 'teary', 'wide', 'fire'):
        sw, sh = (1.12, 1.1) if kind == 'wide' else (1.0, 1.0)
        box = (ex - rw * sw, ey - rh * sh, ex + rw * sw, ey + rh * sh)
        d.ellipse(box, fill=WHITE, outline=INK, width=ew)
        ir = rw * (0.5 if kind == 'wide' else (0.86 if kind in ('determined', 'fire', 'teary') else 0.76))
        ix = ex + max(-1, min(1, look[0])) * (rw - ir) * 0.9
        iy = ey + rh * 0.1 + max(-1, min(1, look[1])) * (rh - ir) * 0.5
        ic = (255, 120, 30) if kind == 'fire' else iris_c
        d.ellipse((ix - ir, iy - ir, ix + ir, iy + ir), fill=ic)
        pr = ir * (0.62 if kind == 'teary' else 0.5)
        if kind == 'fire':
            d.polygon([(ix - pr, iy + pr * 0.8), (ix, iy - pr * 1.4), (ix + pr, iy + pr * 0.8)], fill=(255, 232, 120))
        else:
            d.ellipse((ix - pr, iy - pr, ix + pr, iy + pr), fill=dk(ic, 0.35))
        hr = ir * (0.42 if kind == 'teary' else 0.32)
        d.ellipse((ix - ir * 0.38 - hr, iy - ir * 0.42 - hr, ix - ir * 0.38 + hr, iy - ir * 0.42 + hr), fill=WHITE)
        hr2 = ir * 0.14
        d.ellipse((ix + ir * 0.32 - hr2, iy + ir * 0.34 - hr2, ix + ir * 0.32 + hr2, iy + ir * 0.34 + hr2), fill=WHITE)
        if kind == 'teary':
            d.chord((ex - rw * 0.9, ey + rh * 0.2, ex + rw * 0.9, ey + rh * 1.0), 0, 180, fill=(150, 210, 255))
        d.arc(box, 195, 345, fill=INK, width=max(2, int(ow * 1.5)))
        if lash:
            ox = ex + side * rw * 0.92
            for k, a in enumerate((0.0, 0.5)):
                d.line(((ox, ey - rh * (0.55 - a * 0.4)), (ox + side * rw * 0.35, ey - rh * (0.85 - a * 0.5))), fill=INK,
                       width=max(1, int(ow * 0.9)))
        if kind in ('half', 'sly'):
            cut = ey - rh * (0.1 if kind == 'half' else 0.25)
            d.rectangle((ex - rw * 1.15, ey - rh * 1.3, ex + rw * 1.15, cut), fill=skin)
            d.line(((ex - rw * 1.02, cut), (ex + rw * 1.02, cut)), fill=INK, width=max(2, int(ow * 1.5)))
            if kind == 'sly':
                d.chord((ex - rw * 1.2, ey + rh * 0.35, ex + rw * 1.2, ey + rh * 1.6), 180, 360, fill=skin)
                d.arc((ex - rw * 1.2, ey + rh * 0.35, ex + rw * 1.2, ey + rh * 1.6), 200, 340, fill=INK, width=ew)
        elif kind == 'angry':
            x_in, x_out = ex + inner * rw * 1.05, ex - inner * rw * 1.05
            pts = [(x_in, ey - rh * 0.05), (x_out, ey - rh * 0.7), (x_out, ey - rh * 1.3), (x_in, ey - rh * 1.3)]
            d.polygon(pts, fill=skin)
            d.line((pts[0], pts[1]), fill=INK, width=max(2, int(ow * 1.6)))
    elif kind == 'shock':
        box = (ex - rw * 1.15, ey - rh * 1.2, ex + rw * 1.15, ey + rh * 1.2)
        d.ellipse(box, fill=WHITE, outline=INK, width=ew)
        pr = rw * 0.2
        d.ellipse((ex - pr, ey - pr, ex + pr, ey + pr), fill=INK)
    elif kind == 'dot':
        d.ellipse((ex - rw * 0.32, ey - rh * 0.36, ex + rw * 0.32, ey + rh * 0.36), fill=INK)
    elif kind == 'happy':
        d.arc((ex - rw, ey - rh * 0.5, ex + rw, ey + rh * 1.1), 195, 345, fill=INK, width=max(2, int(ow * 1.8)))
    elif kind == 'closed':
        d.arc((ex - rw, ey - rh * 1.0, ex + rw, ey + rh * 0.4), 15, 165, fill=INK, width=max(2, int(ow * 1.8)))
    elif kind == 'line':
        d.line(((ex - rw, ey + rh * 0.2), (ex + rw, ey + rh * 0.2)), fill=INK, width=max(2, int(ow * 1.8)))
    elif kind in ('x', 'cry'):
        k = side
        d.line(((ex - k * rw, ey - rh * 0.6), (ex + k * rw * 0.8, ey + rh * 0.05), (ex - k * rw, ey + rh * 0.6)), fill=INK,
               width=max(2, int(ow * 1.8)), joint='curve')
    elif kind == 'spiral':
        pts = []
        for i in range(40):
            a = i * 0.45 + t * 8 * side
            r = rw * 1.0 * i / 40
            pts.append((ex + math.cos(a) * r, ey + math.sin(a) * r * rh / rw))
        d.line(pts, fill=INK, width=max(1, int(ow)))
    elif kind == 'star':
        d.ellipse((ex - rw, ey - rh, ex + rw, ey + rh), fill=WHITE, outline=INK, width=ew)
        star(d, ex, ey + rh * 0.08, rw * 0.85, (255, 200, 40), rot=t * 2)
        d.ellipse((ex - rw * 0.55, ey - rh * 0.55, ex - rw * 0.2, ey - rh * 0.2), fill=WHITE)
    elif kind == 'heart':
        heart(d, ex, ey, rw * 1.25, (240, 50, 90), ow)


def star(d, x, y, r, col, rot=0.0, ink=None, ow=0):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5 + rot
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    if ink:
        opoly(d, pts, col, ow, ink)
    else:
        d.polygon(pts, fill=col)


def sparkle(d, x, y, r, col=(255, 250, 220), a=255):
    pts = [(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22), (x, y + r),
           (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)]
    d.polygon(pts, fill=tuple(col) + (int(a),))


def heart(d, x, y, r, col, ow=0):
    pts = []
    for k in range(40):
        a = k / 40 * 2 * math.pi
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + hx * r / 17, y + hy * r / 17))
    if ow:
        opoly(d, pts, col, ow * 0.7)
    else:
        d.polygon(pts, fill=col)


def drop(d, x, y, r, col=(140, 205, 255), ow=0):
    pts = [(x, y - r * 1.8)]
    for k in range(13):
        a = math.pi * (1.15 - 1.3 * k / 12)
        pts.append((x + math.cos(a) * r, y - math.sin(a) * r))
    if ow:
        opoly(d, pts, col, ow * 0.6)
    else:
        d.polygon(pts, fill=col)
    d.ellipse((x - r * 0.45, y - r * 0.6, x - r * 0.1, y - r * 0.15), fill=WHITE)


def draw_mouth(d, kind, cx, my, rx, ry, talk, ow, side_view=False, f=1, t=0.0):
    dark, tongue = (96, 26, 40), (236, 112, 124)
    lw = max(2, int(ow * 1.3))
    k = 0.65 if side_view else 1.0
    if talk > 0.05 and kind in ('smile', 'smile_small', 'flat', 'smirk', 'cat', 'pout', 'frown', 'wavy', 'wobble'):
        kind, talk_h = 'talk', talk
    else:
        talk_h = talk
    if side_view:
        cx += f * rx * 0.05
    if kind == 'talk':
        w, h = rx * 0.2 * k, ry * (0.06 + 0.2 * talk_h)
        d.ellipse((cx - w, my - h, cx + w, my + h), fill=dark, outline=INK, width=lw)
        d.ellipse((cx - w * 0.6, my + h * 0.1, cx + w * 0.6, my + h * 0.9), fill=tongue)
    elif kind in ('smile', 'smile_small'):
        w = rx * (0.3 if kind == 'smile' else 0.17) * k
        d.arc((cx - w, my - ry * 0.14, cx + w, my + ry * 0.12), 20, 160, fill=INK, width=lw)
    elif kind in ('grin', 'laugh', 'drool'):
        w, h = (rx * 0.42, ry * 0.36) if kind == 'laugh' else (rx * 0.3, ry * 0.24)
        w *= k
        h *= (1 + 0.15 * talk_h)
        box = (cx - w, my - h, cx + w, my + h)
        d.chord(box, 0, 180, fill=dark)
        d.chord((cx - w * 0.95, my - h * 0.32, cx + w * 0.95, my + h * 0.32), 0, 180, fill=WHITE)
        d.ellipse((cx - w * 0.42, my + h * 0.45, cx + w * 0.42, my + h * 0.98), fill=tongue)
        d.arc(box, 0, 180, fill=INK, width=lw)
        d.line(((cx - w, my), (cx + w, my)), fill=INK, width=lw)
        if kind == 'drool':
            drop(d, cx + w * 0.8, my + h * 1.5, rx * 0.06)
    elif kind in ('O', 'o'):
        w, h = (rx * 0.16, ry * 0.2) if kind == 'O' else (rx * 0.08, ry * 0.09)
        w *= k
        d.ellipse((cx - w, my - h, cx + w, my + h), fill=dark, outline=INK, width=lw)
        if kind == 'O':
            d.ellipse((cx - w * 0.6, my + h * 0.15, cx + w * 0.6, my + h * 0.85), fill=tongue)
    elif kind in ('scream', 'wail'):
        w, h = (rx * 0.27, ry * 0.36) if kind == 'scream' else (rx * 0.3, ry * 0.26)
        w *= k
        wob = 0.08 * math.sin(t * 30) if kind == 'wail' else 0
        box = (cx - w, my - h * (0.55 + wob), cx + w, my + h)
        d.rounded_rectangle(box, radius=w * 0.7, fill=dark, outline=INK, width=lw)
        d.rectangle((cx - w * 0.75, box[1] + lw, cx + w * 0.75, box[1] + lw + h * 0.22), fill=WHITE)
        d.ellipse((cx - w * 0.55, my + h * 0.3, cx + w * 0.55, my + h * 0.92), fill=tongue)
    elif kind == 'wavy' or kind == 'wobble':
        w = rx * 0.3 * k
        pts = [(cx - w + i * w / 5, my + (ry * 0.045 if i % 2 else -ry * 0.045) + (ry * 0.03 if kind == 'wobble' else 0)) for i in range(11)]
        d.line(pts, fill=INK, width=lw, joint='curve')
    elif kind == 'flat':
        w = rx * 0.2 * k
        d.line(((cx - w, my), (cx + w, my)), fill=INK, width=lw)
    elif kind == 'frown':
        w = rx * 0.22 * k
        d.arc((cx - w, my - ry * 0.02, cx + w, my + ry * 0.2), 200, 340, fill=INK, width=lw)
    elif kind == 'smirk':
        w = rx * 0.26 * k
        s = f if side_view else 1
        d.line(((cx - s * w, my + ry * 0.02), (cx + s * w * 0.3, my + ry * 0.05), (cx + s * w, my - ry * 0.07)), fill=INK,
               width=lw, joint='curve')
    elif kind == 'cat':
        w = rx * 0.14 * k
        d.arc((cx - 2 * w, my - w, cx, my + w * 0.9), 0, 180, fill=INK, width=lw)
        d.arc((cx, my - w, cx + 2 * w, my + w * 0.9), 0, 180, fill=INK, width=lw)
    elif kind == 'grit':
        w, h = rx * 0.27 * k, ry * 0.12
        d.rounded_rectangle((cx - w, my - h, cx + w, my + h), radius=h * 0.6, fill=WHITE, outline=INK, width=lw)
        d.line(((cx - w, my), (cx + w, my)), fill=INK, width=max(1, int(ow * 0.7)))
        for i in range(1, 4):
            x = cx - w + i * w / 2
            d.line(((x, my - h), (x, my + h)), fill=INK, width=max(1, int(ow * 0.7)))


def head_canvas(c, e, view, f, u, ow, talk, t, blink, glint):
    """画一个不旋转的头，返回 (图, 头中心在图里的位置)。"""
    sx, sy = c.get('face', (1.0, 1.0))
    rx, ry = HEAD_RX * u * sx, HEAD_RY * u * sy
    W_, H_ = int(rx * 4.2), int(ry * 4.6)
    cx, cy = W_ / 2, H_ / 2
    img = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, 'RGBA')
    skin, hc = c['skin'], c['hair_c']
    style = c['hair']
    acc = c.get('acc', ())
    side = view == 'side'
    # 耳朵、脸、鼻子：先画所有描边，再填色，连成一个整体
    parts = []
    if side:
        parts.append(('c', (cx - f * rx * 0.12, cy + ry * 0.08), rx * 0.2))
        parts.append(('e', (cx - rx, cy - ry, cx + rx, cy + ry)))
        parts.append(('c', (cx + f * rx * 0.97, cy + ry * 0.16), rx * 0.12))
    else:
        for s in (-1, 1):
            parts.append(('c', (cx + s * rx * 0.98, cy + ry * 0.1), rx * 0.2))
        parts.append(('e', (cx - rx, cy - ry, cx + rx, cy + ry)))
    for p in parts:
        if p[0] == 'c':
            ocircle(d, p[1], p[2], INK, ow)
        else:
            b = p[1]
            d.ellipse((b[0] - ow, b[1] - ow, b[2] + ow, b[3] + ow), fill=INK)
    for p in parts:
        if p[0] == 'c':
            d.ellipse((p[1][0] - p[2], p[1][1] - p[2], p[1][0] + p[2], p[1][1] + p[2]), fill=skin)
        else:
            d.ellipse(p[1], fill=skin)
    if not side:
        for s in (-1, 1):
            ex = cx + s * rx * 0.98
            d.arc((ex - rx * 0.1, cy, ex + rx * 0.1, cy + ry * 0.2), 90 - s * 70, 270 - s * 70, fill=dk(skin, 0.75),
                  width=max(1, int(ow * 0.6)))
    if c.get('old'):
        for s in ((-1, 1) if not side else (f,)):
            x = cx + s * rx * (0.55 if not side else 0.35)
            d.arc((x - rx * 0.18, cy + ry * 0.3, x + rx * 0.18, cy + ry * 0.6), 200, 300, fill=dk(skin, 0.8), width=max(1, int(ow * 0.6)))
    # 眼睛
    eyes = e['eyes'] if isinstance(e['eyes'], tuple) else (e['eyes'], e['eyes'])
    rw, rh = rx * 0.19, ry * 0.24
    ey = cy + ry * 0.12
    if blink:
        eyes = tuple('line' if k in ('open', 'half', 'determined', 'wide', 'sly', 'angry', 'teary') else k for k in eyes)
    look = e['look']
    if side:
        ex = cx + f * rx * 0.5
        draw_eye(d, ex, ey, rw * 0.8, rh, eyes[1], f, (f * 0.6 + look[0] * 0.3, look[1]), c['eye_c'], ow, skin, c.get('lash'), t)
        eye_xs = [(ex, f)]
    else:
        eye_xs = []
        for i, s in enumerate((-1, 1)):
            ex = cx + s * rx * 0.42
            draw_eye(d, ex, ey, rw, rh, eyes[i], s, look, c['eye_c'], ow, skin, c.get('lash'), t)
            eye_xs.append((ex, s))
    # 腮红
    if e['blush'] > 0:
        a = int(150 * e['blush'])
        for ex, s in eye_xs:
            bx = ex + (s * rw * 0.2 if not side else f * rw * 0.1)
            d.ellipse((bx - rw * 1.0, ey + rh * 1.15, bx + rw * 1.0, ey + rh * 1.65), fill=(255, 120, 140, a))
    # 鼻子（正面）
    if not side:
        d.arc((cx - rx * 0.06, cy + ry * 0.3, cx + rx * 0.06, cy + ry * 0.42), 20, 160, fill=dk(skin, 0.7), width=max(1, int(ow * 0.8)))
    # 嘴
    mx = cx + (f * rx * 0.58 if side else 0)
    my = cy + ry * 0.6
    draw_mouth(d, e['mouth'], mx, my, rx, ry, talk, ow, side, f, t)
    if 'toothbrush' in acc:
        bx = mx + (f * rx * 0.1 if side else rx * 0.12)
        d.line(((bx, my), (bx + (f if side else 1) * rx * 0.75, my + ry * 0.12)), fill=INK, width=int(ow * 2.6))
        d.line(((bx, my), (bx + (f if side else 1) * rx * 0.75, my + ry * 0.12)), fill=(90, 170, 255), width=int(ow * 1.4))
        tx = bx + (f if side else 1) * rx * 0.75
        d.rectangle((tx - rx * 0.06, my + ry * 0.03, tx + rx * 0.06, my + ry * 0.12), fill=WHITE, outline=INK)
    if 'mustache' in acc:
        mw = rx * (0.18 if side else 0.3)
        d.chord((mx - mw, my - ry * 0.2, mx + mw, my + ry * 0.08), 180, 360, fill=lt(hc, 0.2), outline=INK, width=max(1, int(ow * 0.7)))
    # 脸上的效果
    fx = e['fx']
    if 'gloom' in fx:
        d.chord((cx - rx, cy - ry, cx + rx, cy + ry * 0.3), 180, 360, fill=(80, 60, 140, 90))
        for i in range(5):
            x = cx - rx * 0.5 + i * rx * 0.25
            d.line(((x, cy - ry * 0.75), (x, cy - ry * 0.25)), fill=(90, 70, 150, 220), width=max(1, int(ow * 0.8)))
    if 'tears' in fx:
        for ex, s in eye_xs:
            x0 = ex + s * rw * 0.3
            pts_l, pts_r = [], []
            for i in range(9):
                yy = ey + rh * 0.5 + i * ry * 0.16
                wv = math.sin(t * 18 + i * 1.3) * rx * 0.03
                pts_l.append((x0 - rx * 0.07 + wv, yy))
                pts_r.append((x0 + rx * 0.07 + wv, yy))
            d.polygon(pts_l + pts_r[::-1], fill=(120, 190, 255, 220))
    if 'joy_tears' in fx:
        for ex, s in eye_xs:
            drop(d, ex + s * rw * 1.25, ey + rh * 0.2, rx * 0.06)
    if 'sweat' in fx:
        sx_ = cx + (rx * 1.0 if not side else -f * rx * 0.7)
        drop(d, sx_, cy - ry * 0.25, rx * 0.13, ow=ow)
    # 头发（前面）和帽子
    draw_hair_front(d, style, cx, cy, rx, ry, hc, ow, view, f, t)
    if 'headband' in acc:
        y = cy - ry * 0.52
        if side:
            opoly(d, [(cx - rx * 1.0, y - ry * 0.1), (cx + rx * 0.98, y - ry * 0.12), (cx + rx * 0.98, y + ry * 0.06),
                      (cx - rx * 1.0, y + ry * 0.08)], (232, 50, 64), ow * 0.8)
            opoly(d, [(cx - f * rx * 1.0, y), (cx - f * rx * 1.5, y + ry * 0.25 + 0.05 * ry * math.sin(t * 20)),
                      (cx - f * rx * 1.35, y + ry * 0.38)], (232, 50, 64), ow * 0.6)
        else:
            opoly(d, [(cx - rx * 1.0, y - ry * 0.1), (cx + rx * 1.0, y - ry * 0.1), (cx + rx * 0.98, y + ry * 0.08),
                      (cx - rx * 0.98, y + ry * 0.08)], (232, 50, 64), ow * 0.8)
    if 'helmet' in acc:
        box = (cx - rx * 1.16, cy - ry * 1.22, cx + rx * 1.16, cy + ry * 0.12)
        hcol = c.get('helmet_c', (30, 30, 38))
        stripe = c.get('helmet_s', (255, 200, 50))
        d.chord((box[0] - ow, box[1] - ow, box[2] + ow, box[3] + ow), 180, 360, fill=INK)
        d.chord(box, 180, 360, fill=hcol)
        d.arc((box[0] + rx * 0.1, box[1] + ry * 0.12, box[2] - rx * 0.1, box[3]), 200, 340, fill=stripe, width=int(ow * 2))
        for k in (-0.3, 0.0, 0.3):
            d.line(((cx + k * rx, cy - ry * 1.05), (cx + k * rx * 1.2, cy - ry * 0.8)), fill=(70, 70, 84), width=max(1, int(ow)))
        yb = (box[1] + box[3]) / 2
        if side:
            opoly(d, [(cx + f * rx * 0.6, yb - ry * 0.02), (cx + f * rx * 1.5, yb + ry * 0.05), (cx + f * rx * 0.6, yb + ry * 0.12)],
                  hcol, ow * 0.7)
        d.line(((cx - rx * 0.95, yb), (cx - rx * 0.55, cy + ry * 0.95)), fill=INK, width=max(1, int(ow * 0.9)))
        d.line(((cx + rx * 0.95, yb), (cx + rx * 0.55, cy + ry * 0.95)), fill=INK, width=max(1, int(ow * 0.9)))
    if 'guardcap' in acc:
        top = cy - ry * 1.3
        opoly(d, [(cx - rx * 0.98, cy - ry * 0.55), (cx - rx * 1.08, top + ry * 0.1), (cx + rx * 1.08, top + ry * 0.1),
                  (cx + rx * 0.98, cy - ry * 0.55)], (36, 54, 96), ow)
        d.rectangle((cx - rx * 0.98, cy - ry * 0.72, cx + rx * 0.98, cy - ry * 0.55), fill=(20, 26, 46))
        star(d, cx + (f * rx * 0.3 if side else 0), cy - ry * 0.95, rx * 0.17, (245, 200, 70), ink=INK, ow=ow * 0.5)
        if side:
            opoly(d, [(cx + f * rx * 0.3, cy - ry * 0.6), (cx + f * rx * 1.45, cy - ry * 0.5), (cx + f * rx * 1.3, cy - ry * 0.4),
                      (cx + f * rx * 0.3, cy - ry * 0.45)], (20, 22, 30), ow * 0.7)
        else:
            d.chord((cx - rx * 1.05, cy - ry * 0.7, cx + rx * 1.05, cy - ry * 0.3), 0, 180, fill=(20, 22, 30), outline=INK, width=int(ow))
    # 眉毛（画在头发上面，方便看清）
    brows = e['brows']
    th = ry * 0.07 * c.get('brow', 1.0)
    for ex, s in eye_xs:
        if brows == 'sly':
            di, do = BROWS['up'] if s < 0 else BROWS['angry']
        else:
            di, do = BROWS.get(brows, (0, 0))
        by = ey - rh - ry * 0.12
        if side:
            xi, xo = ex - f * rw * 0.7, ex + f * rw * 0.9
        else:
            xi, xo = ex - s * rw * 0.85, ex + s * rw * 1.05
        seg_line(d, (xi, by + di * ry), (xo, by + do * ry), th, dk(hc, 0.9) if hc[0] > 120 else INK)
    # 眼镜
    if 'glasses' in acc or 'roundglasses' in acc or 'halfglasses' in acc:
        kind = 'round' if 'roundglasses' in acc else ('half' if 'halfglasses' in acc else 'rect')
        lw = max(2, int(ow * 1.1))
        for ex, s in eye_xs:
            gw, gh = (rw * 1.45, rh * 1.12) if not side else (rw * 1.2, rh * 1.12)
            gy = ey + (rh * 0.55 if kind == 'half' else 0)
            box = (ex - gw, gy - gh * (0.55 if kind == 'half' else 1), ex + gw, gy + gh)
            fill = (255, 255, 255, 235) if glint else (200, 230, 255, 50)
            if kind == 'round':
                d.ellipse(box, fill=fill, outline=INK, width=lw)
            else:
                d.rounded_rectangle(box, radius=gh * 0.35, fill=fill, outline=INK, width=lw)
            if glint:
                d.line(((box[0] + gw * 0.3, box[3] - gh * 0.3), (box[2] - gw * 0.3, box[1] + gh * 0.3)), fill=(150, 200, 255),
                       width=max(2, int(ow * 1.4)))
                sparkle(d, box[2], box[1], rx * 0.25, (255, 255, 255))
        if side:
            ex = eye_xs[0][0]
            d.line(((ex - f * rw * 1.2, ey), (cx - f * rx * 0.15, ey - ry * 0.05)), fill=INK, width=lw)
        else:
            d.line(((eye_xs[0][0] + rw * 1.45, ey), (eye_xs[1][0] - rw * 1.45, ey)), fill=INK, width=lw)
    if 'bandaid' in acc:
        bx, by = (cx + rx * 0.45, cy + ry * 0.42) if not side else (cx + f * rx * 0.3, cy + ry * 0.4)
        d.rounded_rectangle((bx - rx * 0.16, by - ry * 0.05, bx + rx * 0.16, by + ry * 0.05), radius=ry * 0.04,
                            fill=(245, 205, 160), outline=INK, width=max(1, int(ow * 0.6)))
    if 'starclip' in acc:
        star(d, cx + (rx * 0.62 if not side else -f * rx * 0.1), cy - ry * 0.62, rx * 0.17, (255, 214, 60), ink=INK, ow=ow * 0.5)
    return img, (cx, cy), (rx, ry)


def draw_hair_front(d, style, cx, cy, rx, ry, hc, ow, view, f, t):
    side = view == 'side'
    hl = lt(hc, 0.25)
    if style in ('none',):
        return

    def cap(hairline=0.35, ext=1.06, top=1.1, back=0.0):
        box = (cx - rx * ext, cy - ry * top, cx + rx * ext, cy + ry * (2 * (-hairline) + top))
        d.chord((box[0] - ow, box[1] - ow, box[2] + ow, box[3] + ow), 180, 360, fill=INK)
        d.chord(box, 180, 360, fill=hc)
        return box

    if side:
        # 侧面：盖住头顶和后脑勺
        hair_pts = []
        for k in range(18):
            a = -math.pi * 0.15 - k / 17 * math.pi * 1.15
            hair_pts.append((cx + f * math.cos(a) * rx * 1.08, cy + math.sin(a) * ry * 1.08))
        hair_pts = [(cx + f * rx * 0.75, cy - ry * 0.5)] + hair_pts + [(cx - f * rx * 0.55, cy + ry * 0.45), (cx - f * rx * 0.15, cy - ry * 0.25)]
        if style == 'buzz':
            hair_pts = [(x * 0.97 + cx * 0.03, y * 0.97 + cy * 0.03) for x, y in hair_pts]
        opoly(d, hair_pts, hc, ow)
        if style in ('messy', 'spiky', 'bedhead'):
            n = 6 if style != 'bedhead' else 3
            for k in range(n):
                a = -math.pi * (0.35 + 0.75 * k / max(1, n - 1))
                bx, by = cx + f * math.cos(a) * rx * 0.95, cy + math.sin(a) * ry * 0.95
                tip = (cx + f * math.cos(a) * rx * (1.45 if style != 'spiky' else 1.3), cy + math.sin(a) * ry * (1.45 if style != 'spiky' else 1.3))
                w = rx * 0.18
                opoly(d, [(bx - w * math.sin(a), by + w * math.cos(a) * 0.3), tip, (bx + w * math.sin(a), by - w * math.cos(a) * 0.3)], hc, ow * 0.8)
        if style == 'curly':
            for k in range(8):
                a = -math.pi * (0.2 + 0.95 * k / 7)
                ocircle(d, (cx + f * math.cos(a) * rx * 1.0, cy + math.sin(a) * ry * 1.0), rx * 0.24, hc, ow * 0.7)
        if style in ('long', 'bob'):
            opoly(d, [(cx + f * rx * 0.7, cy - ry * 0.55), (cx + f * rx * 0.95, cy - ry * 0.1), (cx + f * rx * 0.55, cy - ry * 0.25)], hc, ow * 0.6)
        if style == 'bun':
            ocircle(d, (cx - f * rx * 0.4, cy - ry * 1.15), rx * 0.32, hc, ow)
        d.arc((cx - rx * 0.8, cy - ry * 1.0, cx + rx * 0.8, cy - ry * 0.2), 220 if f > 0 else 250, 290 if f > 0 else 320, fill=hl,
              width=max(1, int(ow * 1.2)))
        return
    if style == 'messy':
        cap(0.38)
        pts = []
        for k in range(15):
            a = math.pi * (1.02 + 0.96 * k / 14)
            rr = 1.05 if k % 2 == 0 else 1.42 + 0.05 * math.sin(k * 7)
            pts.append((cx + math.cos(a) * rx * rr, cy - ry * 0.1 + math.sin(a) * ry * rr))
        opoly(d, pts + [(cx + rx * 0.95, cy - ry * 0.3), (cx - rx * 0.95, cy - ry * 0.3)], hc, ow)
        for x0, w in ((-0.55, 0.3), (-0.12, 0.34), (0.35, 0.3)):
            opoly(d, [(cx + rx * (x0 - w / 2), cy - ry * 0.5), (cx + rx * (x0 + w / 2), cy - ry * 0.5), (cx + rx * (x0 + 0.05), cy - ry * 0.16)],
                  hc, ow * 0.8)
    elif style == 'spiky':
        cap(0.42)
        pts = []
        for k in range(13):
            a = math.pi * (1.05 + 0.9 * k / 12)
            rr = 1.02 if k % 2 == 0 else 1.28
            pts.append((cx + math.cos(a) * rx * rr, cy - ry * 0.12 + math.sin(a) * ry * rr))
        opoly(d, pts, hc, ow)
    elif style == 'sidepart':
        cap(0.4)
        opoly(d, [(cx - rx * 1.02, cy - ry * 0.25), (cx - rx * 0.6, cy - ry * 0.75), (cx + rx * 0.3, cy - ry * 0.68),
                  (cx + rx * 1.06, cy - ry * 0.2), (cx + rx * 1.0, cy - ry * 0.62), (cx + rx * 0.2, cy - ry * 1.05),
                  (cx - rx * 0.8, cy - ry * 0.85)], hc, ow)
        d.line(((cx - rx * 0.35, cy - ry * 1.0), (cx - rx * 0.45, cy - ry * 0.65)), fill=hl, width=max(1, int(ow)))
    elif style == 'long':
        cap(0.3)
        pts = [(cx - rx * 1.06, cy - ry * 0.25)]
        for i in range(9):
            x = cx - rx * 0.95 + i * rx * 1.9 / 8
            pts.append((x, cy - ry * (0.2 if i % 2 == 0 else 0.3)))
        pts += [(cx + rx * 1.06, cy - ry * 0.25), (cx + rx * 1.0, cy - ry * 0.85), (cx - rx * 1.0, cy - ry * 0.85)]
        opoly(d, pts, hc, ow)
        for s in (-1, 1):
            x = cx + s * rx * 1.0
            opoly(d, [(x - s * rx * 0.08, cy - ry * 0.45), (x + s * rx * 0.2, cy - ry * 0.4), (x + s * rx * 0.24, cy + ry * 0.95),
                      (x - s * rx * 0.02, cy + ry * 1.05)], hc, ow * 0.8)
    elif style == 'bob':
        cap(0.32)
        opoly(d, [(cx - rx * 1.05, cy - ry * 0.3), (cx + rx * 1.05, cy - ry * 0.3), (cx + rx * 0.9, cy - ry * 0.85), (cx - rx * 0.9, cy - ry * 0.85)], hc, ow)
        for s in (-1, 1):
            opoly(d, [(cx + s * rx * 0.92, cy - ry * 0.4), (cx + s * rx * 1.18, cy - ry * 0.3), (cx + s * rx * 1.1, cy + ry * 0.55),
                      (cx + s * rx * 0.85, cy + ry * 0.5)], hc, ow * 0.8)
    elif style == 'curly':
        cap(0.45, 1.05)
        for k in range(13):
            a = math.pi * (0.92 + 1.16 * k / 12)
            ocircle(d, (cx + math.cos(a) * rx * 1.0, cy - ry * 0.05 + math.sin(a) * ry * 1.02), rx * 0.25, hc, ow * 0.7)
        for k in range(6):
            a = math.pi * (1.15 + 0.7 * k / 5)
            d.arc((cx + math.cos(a) * rx * 0.95 - rx * 0.12, cy + math.sin(a) * ry * 0.98 - rx * 0.12,
                   cx + math.cos(a) * rx * 0.95 + rx * 0.12, cy + math.sin(a) * ry * 0.98 + rx * 0.12), 180, 300, fill=hl,
                  width=max(1, int(ow * 0.7)))
    elif style == 'bedhead':
        cap(0.38)
        opoly(d, [(cx - rx * 1.04, cy - ry * 0.3), (cx - rx * 0.7, cy - ry * 0.55), (cx - rx * 0.3, cy - ry * 0.4),
                  (cx + rx * 0.2, cy - ry * 0.6), (cx + rx * 0.7, cy - ry * 0.4), (cx + rx * 1.04, cy - ry * 0.3),
                  (cx + rx * 0.9, cy - ry * 0.9), (cx - rx * 0.9, cy - ry * 0.9)], hc, ow)
        for x0, a, ln in ((-0.25, -0.5, 0.55), (0.15, 0.4, 0.6), (0.45, 1.0, 0.45)):
            bx, by = cx + rx * x0, cy - ry * 1.0
            tip = (bx + math.sin(a) * rx * ln, by - math.cos(a) * ry * ln)
            opoly(d, [(bx - rx * 0.12, by + ry * 0.05), (tip[0], tip[1]), (bx + rx * 0.12, by + ry * 0.05)], hc, ow * 0.8)
    elif style == 'buzz':
        cap(0.5, 1.02, 1.04)
        for k in range(18):
            a = math.pi * (1.15 + 0.7 * (k % 6) / 5)
            r2 = 0.6 + 0.12 * (k // 6)
            x, y = cx + math.cos(a) * rx * r2, cy - ry * 0.1 + math.sin(a) * ry * r2
            d.ellipse((x - ow * 0.4, y - ow * 0.4, x + ow * 0.4, y + ow * 0.4), fill=lt(hc, 0.3))
    elif style in ('neat', 'short', 'ponytail', 'bun'):
        cap(0.4 if style != 'ponytail' else 0.34)
        y1 = cy - ry * (0.32 if style == 'neat' else 0.42)
        opoly(d, [(cx - rx * 1.03, cy - ry * 0.35), (cx - rx * 0.5, y1), (cx + rx * 0.2, y1 + ry * 0.03), (cx + rx * 1.03, cy - ry * 0.35),
                  (cx + rx * 0.95, cy - ry * 0.85), (cx - rx * 0.95, cy - ry * 0.85)], hc, ow)
        if style == 'bun':
            ocircle(d, (cx, cy - ry * 1.18), rx * 0.33, hc, ow)
    d.arc((cx - rx * 0.75, cy - ry * 1.0, cx + rx * 0.35, cy - ry * 0.25), 200, 260, fill=hl, width=max(1, int(ow * 1.3)))


def hair_back(d, c, Hc, rx, ry, ang, ow, view, f, wind, t):
    style = c['hair']
    hc = c['hair_c']

    def tr(pts):
        return [(Hc[0] + p[0] * math.cos(ang) - p[1] * math.sin(ang), Hc[1] + p[0] * math.sin(ang) + p[1] * math.cos(ang)) for p in pts]

    sway = math.sin(t * 3) * 0.04 + wind
    if style == 'long':
        if view == 'side':
            pts = [(-f * rx * 0.2, -ry * 0.9), (-f * rx * 1.1, -ry * 0.4), (-f * rx * (1.2 + 1.2 * wind), ry * (2.1 - 1.2 * wind)),
                   (-f * rx * (0.2 + 1.4 * wind), ry * (2.25 - 1.0 * wind)), (0, ry * 0.2)]
        else:
            pts = [(-rx * 1.12, -ry * 0.2), (rx * 1.12, -ry * 0.2), (rx * (1.18 + sway * 3), ry * 2.2), (rx * (0.3 + sway * 3), ry * 2.35),
                   (-rx * (0.3 - sway * 3), ry * 2.35), (-rx * (1.18 - sway * 3), ry * 2.2)]
        opoly(d, tr(pts), hc, ow)
    elif style == 'ponytail':
        base = (-f * rx * 0.75, -ry * 0.55) if view == 'side' else (rx * 0.0, -ry * 0.95)
        dirx = (-f if view == 'side' else 1) * (0.6 + 2.5 * wind)
        tip = (base[0] + dirx * rx * 1.2, base[1] + ry * (1.6 - 1.4 * wind) + math.sin(t * 5) * ry * 0.05)
        pts = [(base[0] - rx * 0.22, base[1]), (base[0] + rx * 0.22, base[1]), (tip[0] + rx * 0.1, tip[1]), (tip[0] - rx * 0.12, tip[1] - ry * 0.1)]
        opoly(d, tr(pts), hc, ow)
    elif style == 'bob':
        pts = [(-rx * 1.15, -ry * 0.3), (rx * 1.15, -ry * 0.3), (rx * 1.15, ry * 0.75), (-rx * 1.15, ry * 0.75)]
        opoly(d, tr(pts), hc, ow)


# ---------------------------------------------------------------- 手里的东西
def draw_bag(d, x, y, s, ow=2, ang=0.0):
    w, h = s / 2, s * 0.4
    body = [(x - w, y - h), (x + w, y - h), (x + w * 0.96, y + h), (x - w * 0.96, y + h)]
    d.arc((x - w * 0.55, y - h - s * 0.42, x + w * 0.55, y - h + s * 0.12), 190, 350, fill=INK, width=max(2, int(s * 0.09)))
    d.arc((x - w * 0.55, y - h - s * 0.42, x + w * 0.55, y - h + s * 0.12), 190, 350, fill=(170, 24, 36), width=max(1, int(s * 0.05)))
    d.rounded_rectangle((x - w * 0.66 - ow, y - h - s * 0.17 - ow, x + w * 0.66 + ow, y - h + s * 0.05 + ow), radius=s * 0.05, fill=INK)
    d.rounded_rectangle((x - w * 0.66, y - h - s * 0.17, x + w * 0.66, y - h + s * 0.05), radius=s * 0.05, fill=(250, 248, 240))
    for k in range(3):
        bx = x - w * 0.4 + k * w * 0.4
        d.ellipse((bx - s * 0.09, y - h - s * 0.26, bx + s * 0.09, y - h - s * 0.08), fill=(206, 130, 54), outline=INK, width=max(1, int(ow * 0.6)))
    opoly(d, body, (226, 44, 56), ow)
    d.rectangle((x - w * 0.96, y - h * 0.1, x + w * 0.96, y + h * 0.12), fill=(250, 220, 90))
    d.line(((x - w * 0.9, y - h * 0.62), (x + w * 0.9, y - h * 0.62)), fill=(150, 20, 30), width=max(1, int(ow * 0.7)))


def draw_bucket(d, x, y, s, ow=2):
    for k in range(5):
        a = -0.9 + k * 0.45
        ocircle(d, (x + a * 50 * s, y - 52 * s - 16 * s * (1 - abs(a))), 22 * s, (214, 136, 58), ow * 0.8)
    opoly(d, [(x - 70 * s, y - 50 * s), (x + 70 * s, y - 50 * s), (x + 52 * s, y + 60 * s), (x - 52 * s, y + 60 * s)], (252, 250, 244), ow)
    for k in range(3):
        xx = -40 + k * 40
        d.polygon([(x + xx * s - 10 * s, y - 50 * s), (x + xx * s + 10 * s, y - 50 * s), (x + xx * 0.75 * s + 8 * s, y + 60 * s),
                   (x + xx * 0.75 * s - 8 * s, y + 60 * s)], fill=(230, 60, 66))
    d.rectangle((x - 66 * s, y - 50 * s, x + 66 * s, y - 36 * s), fill=(240, 238, 230), outline=INK, width=max(1, int(ow * 0.6)))


def hold_item(d, item, p, u, ow, ctx):
    x, y = p
    if item == 'bag':
        draw_bag(d, x, y + 0.07 * u, 0.15 * u, ow)
    elif item == 'phone':
        d.rounded_rectangle((x - 0.022 * u - ow, y - 0.05 * u - ow, x + 0.022 * u + ow, y + 0.035 * u + ow), radius=0.008 * u, fill=INK)
        d.rounded_rectangle((x - 0.022 * u, y - 0.05 * u, x + 0.022 * u, y + 0.035 * u), radius=0.008 * u, fill=(120, 190, 255))
    elif item == 'remote':
        d.rounded_rectangle((x - 0.05 * u, y - 0.025 * u, x + 0.05 * u, y + 0.03 * u), radius=0.01 * u, fill=(40, 42, 50), outline=INK,
                            width=max(1, int(ow * 0.8)))
        for s in (-1, 1):
            d.line(((x + s * 0.035 * u, y - 0.025 * u), (x + s * 0.045 * u, y - 0.075 * u)), fill=INK, width=max(1, int(ow * 0.8)))
            ocircle(d, (x + s * 0.025 * u, y), 0.01 * u, (110, 110, 120), ow * 0.3)
    elif item == 'thermos':
        opoly(d, [(x - 0.026 * u, y - 0.08 * u), (x + 0.026 * u, y - 0.08 * u), (x + 0.026 * u, y + 0.04 * u), (x - 0.026 * u, y + 0.04 * u)],
              (196, 204, 216), ow * 0.8)
        d.rectangle((x - 0.028 * u, y - 0.095 * u, x + 0.028 * u, y - 0.075 * u), fill=(90, 90, 100), outline=INK)
        if ctx.get('steam', True):
            t = ctx.get('t', 0.0)
            for k in range(2):
                yy = y - 0.12 * u - k * 0.04 * u - (t * 0.05 * u) % (0.04 * u)
                d.arc((x - 0.02 * u + k * 0.01 * u, yy - 0.02 * u, x + 0.01 * u + k * 0.01 * u, yy + 0.02 * u), 90, 270,
                      fill=(255, 255, 255, 140), width=max(1, int(ow * 0.6)))
    elif item == 'cup':
        opoly(d, [(x - 0.03 * u, y - 0.06 * u), (x + 0.03 * u, y - 0.06 * u), (x + 0.024 * u, y + 0.04 * u), (x - 0.024 * u, y + 0.04 * u)],
              (238, 214, 186), ow * 0.8)
        for k in range(3):
            d.ellipse((x - 0.012 * u + k * 0.01 * u, y + 0.01 * u, x - 0.004 * u + k * 0.01 * u, y + 0.018 * u), fill=(60, 40, 30))
        if not ctx.get('lid_off'):
            d.rectangle((x - 0.034 * u, y - 0.07 * u, x + 0.034 * u, y - 0.058 * u), fill=WHITE, outline=INK, width=max(1, int(ow * 0.6)))
            d.line(((x + 0.006 * u, y - 0.07 * u), (x + 0.016 * u, y - 0.12 * u)), fill=(255, 110, 150), width=max(2, int(ow * 1.2)))
    elif item == 'wing':
        ocircle(d, (x, y), 0.028 * u, (214, 136, 58), ow * 0.7)
        ocircle(d, (x + 0.03 * u, y + 0.008 * u), 0.016 * u, (196, 116, 44), ow * 0.6)
    elif item == 'bucket':
        draw_bucket(d, x, y - 0.02 * u, 0.0012 * u, ow)


# ---------------------------------------------------------------- 画整个人
def render(key, pose, h, facing=1, expr='neutral', talk=0.0, t=0.0, hold=None, wind=0.0, glint=False, blink=None,
           stone=0.0, scale_head=1.0, look=None, hold_ctx=None):
    c = CH[key] if isinstance(key, str) else key
    if scale_head != 1.0:
        c = dict(c)
        c['face'] = (c.get('face', (1, 1))[0] * scale_head, c.get('face', (1, 1))[1] * scale_head)
    e = resolve_expr(expr)
    if look is not None:
        e['look'] = look
    view = pose.get('view', 'front')
    J = joints(c, pose, facing)
    head_ang = J.pop('_head_ang')
    bust = pose.get('bust', False)
    ss = 2 if h <= 520 else 1
    u = h * ss
    ow = max(2.0, 0.0078 * u)
    keys = [k for k in J if not (bust and k in ('K0', 'K1', 'A0', 'A1', 'F0', 'F1', 'H0', 'H1'))]
    xs = [J[k][0] for k in keys]
    ys = [J[k][1] for k in keys]
    x0, x1 = min(xs) - 0.36, max(xs) + 0.36
    y0, y1 = min(ys) - 0.5, max(ys) + 0.2
    if bust:
        y1 = min(y1, 0.14)
    Wc, Hc_ = int((x1 - x0) * u), int((y1 - y0) * u)
    ox, oy = -x0 * u, -y0 * u
    P = {k: (ox + v[0] * u, oy + v[1] * u) for k, v in J.items()}
    img = Image.new('RGBA', (Wc, Hc_), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, 'RGBA')
    f = facing if view == 'side' else 1
    skin = c['skin']
    top_c, bot_c = c['top_c'], c['bottom_c']
    arm_k, leg_k = c.get('arm', 1.0), c.get('leg', 1.0)
    w_up, w_fo = 0.06 * u * arm_k, 0.052 * u * arm_k
    w_th, w_sh = 0.082 * u * leg_k ** 0.7, 0.068 * u * leg_k ** 0.6
    sleeve = c.get('sleeve', 2)
    if sleeve >= 2:
        arm_cover = [(1.0, top_c)]
    elif sleeve <= 0:
        arm_cover = [(1.0, skin)]
    else:
        arm_cover = [(sleeve * 0.5, top_c), (1.0, skin)]
    leg_cover = [(1.0, bot_c)] if c.get('bottom') == 'pants' else [(0.42, bot_c), (1.0, skin)]
    pat = None
    if c['top'] in ('pajama', 'shirt'):
        pat = (tuple(c['pat_c']) + (170,), 0.04 * u, ('center',))
    elif c['top'] == 'puffer':
        pat = (tuple(c['pat_c']) + (255,), 0.05 * u, ())
    rxh, ryh = HEAD_RX * u * c.get('face', (1, 1))[0], HEAD_RY * u * c.get('face', (1, 1))[1]
    # 1. 后面的头发
    hair_back(d, c, P['Hc'], rxh, ryh, head_ang, ow, view, f, wind, t)
    if 'backpack' in c.get('acc', ()) and view == 'side':
        mid = lerp2(P['N'], P['P'], 0.45)
        bx = mid[0] - f * 0.085 * u
        d.rounded_rectangle((bx - 0.055 * u - ow, mid[1] - 0.1 * u - ow, bx + 0.055 * u + ow, mid[1] + 0.1 * u + ow), radius=0.03 * u, fill=INK)
        d.rounded_rectangle((bx - 0.055 * u, mid[1] - 0.1 * u, bx + 0.055 * u, mid[1] + 0.1 * u), radius=0.03 * u, fill=(40, 44, 56))

    def arm(i, darker=False):
        sk = dk(skin, 0.8) if darker else skin
        cov = [(a, sk if col == skin else (dk(col, 0.8) if darker else col)) for a, col in arm_cover]
        chain = [(P[f'S{i}'], P[f'E{i}'], w_up), (P[f'E{i}'], P[f'W{i}'], w_fo)]
        draw_limb(d, chain, cov, ow, sk, None if darker else pat)
        Wp, Ep = P[f'W{i}'], P[f'E{i}']
        dx, dy = Wp[0] - Ep[0], Wp[1] - Ep[1]
        L = math.hypot(dx, dy) or 1
        hp = (Wp[0] + dx / L * 0.012 * u, Wp[1] + dy / L * 0.012 * u)
        hand = pose.get('hands', ('fist', 'fist'))[i]
        hr = 0.034 * u * arm_k ** 0.5
        if hand == 'point':
            tip = (hp[0] + dx / L * 0.07 * u, hp[1] + dy / L * 0.07 * u)
            seg_line(d, hp, tip, 0.024 * u + 2 * ow, INK)
            seg_line(d, hp, tip, 0.024 * u, sk)
        elif hand == 'thumb':
            tip = (hp[0], hp[1] - 0.06 * u)
            seg_line(d, hp, tip, 0.024 * u + 2 * ow, INK)
            seg_line(d, hp, tip, 0.024 * u, sk)
        ocircle(d, hp, hr * (1.15 if hand == 'open' else 1.0), sk, ow)
        if hand == 'open':
            for k in (-1, 0, 1):
                a = math.atan2(dy, dx) + k * 0.45
                q = (hp[0] + math.cos(a) * hr * 1.25, hp[1] + math.sin(a) * hr * 1.25)
                ocircle(d, q, hr * 0.38, sk, ow * 0.7)
        return hp

    def leg(i, darker=False):
        col = dk(bot_c, 0.8) if darker else bot_c
        sk = dk(skin, 0.8) if darker else skin
        cov = [(a, col if cc == bot_c else sk) for a, cc in leg_cover]
        chain = [(P[f'H{i}'], P[f'K{i}'], w_th), (P[f'K{i}'], P[f'A{i}'], w_sh)]
        draw_limb(d, chain, cov, ow, sk)
        if 'kneepads' in c.get('acc', ()):
            ocircle(d, P[f'K{i}'], w_th * 0.55, (30, 30, 36), ow * 0.8)
        A, Fp = P[f'A{i}'], P[f'F{i}']
        shoe = c.get('shoes', 'sneaker')
        sc = dk(c['shoe_c'], 0.8) if darker else c['shoe_c']
        if view == 'side':
            if shoe == 'flipflop':
                seg_line(d, (A[0], A[1] + 0.01 * u), (Fp[0], Fp[1]), 0.032 * u + 2 * ow, INK)
                seg_line(d, (A[0], A[1] + 0.01 * u), (Fp[0], Fp[1]), 0.032 * u, sk)
                d.line(((A[0] - f * 0.01 * u, Fp[1] + 0.022 * u), (Fp[0] + f * 0.015 * u, Fp[1] + 0.022 * u)), fill=sc, width=int(0.016 * u))
            elif shoe == 'skate':
                opoly(d, [(A[0] - f * 0.035 * u, A[1] - 0.06 * u), (A[0] + f * 0.03 * u, A[1] - 0.06 * u), (Fp[0] + f * 0.025 * u, Fp[1] - 0.01 * u),
                          (Fp[0] + f * 0.025 * u, Fp[1] + 0.02 * u), (A[0] - f * 0.04 * u, Fp[1] + 0.02 * u)], sc, ow)
                d.line(((A[0] - f * 0.04 * u, Fp[1] + 0.035 * u), (Fp[0] + f * 0.025 * u, Fp[1] + 0.035 * u)), fill=(200, 200, 210), width=int(0.012 * u))
                for k in range(3):
                    wx = A[0] - f * 0.035 * u + f * k * (Fp[0] - A[0] + f * 0.06 * u) / 2 * f
                    ocircle(d, (wx, Fp[1] + 0.05 * u), 0.016 * u, (255, 200, 40), ow * 0.6)
            else:
                seg_line(d, (A[0] - f * 0.01 * u, A[1] + 0.012 * u), Fp, 0.046 * u + 2 * ow, INK)
                seg_line(d, (A[0] - f * 0.01 * u, A[1] + 0.012 * u), Fp, 0.046 * u, sc)
                if shoe == 'sneaker':
                    d.line(((A[0] - f * 0.03 * u, Fp[1] + 0.016 * u), (Fp[0] + f * 0.02 * u, Fp[1] + 0.016 * u)), fill=WHITE, width=max(1, int(0.01 * u)))
        else:
            if shoe == 'flipflop':
                ocircle(d, (A[0], A[1] + 0.02 * u), 0.03 * u, sk, ow)
                d.line(((A[0] - 0.035 * u, A[1] + 0.045 * u), (A[0] + 0.035 * u, A[1] + 0.045 * u)), fill=sc, width=int(0.016 * u))
            elif shoe == 'skate':
                d.rounded_rectangle((A[0] - 0.036 * u - ow, A[1] - 0.04 * u - ow, A[0] + 0.036 * u + ow, A[1] + 0.04 * u + ow), radius=0.015 * u, fill=INK)
                d.rounded_rectangle((A[0] - 0.036 * u, A[1] - 0.04 * u, A[0] + 0.036 * u, A[1] + 0.04 * u), radius=0.015 * u, fill=sc)
                ocircle(d, (A[0], A[1] + 0.065 * u), 0.018 * u, (255, 200, 40), ow * 0.6)
            else:
                d.ellipse((A[0] - 0.042 * u - ow, A[1] - 0.006 * u - ow, A[0] + 0.042 * u + ow, A[1] + 0.044 * u + ow), fill=INK)
                d.ellipse((A[0] - 0.042 * u, A[1] - 0.006 * u, A[0] + 0.042 * u, A[1] + 0.044 * u), fill=sc)

    # 2. 侧面的后手和后腿
    if view == 'side':
        if not bust:
            leg(0, True)
        arm(0, True)
    # 3. 腿
    if not bust:
        for i in ((1,) if view == 'side' else (0, 1)):
            leg(i)
    # 4. 脖子
    neck_top = lerp2(P['N'], P['Hc'], 0.55)
    seg_line(d, P['N'], neck_top, 0.05 * u + 2 * ow, INK)
    seg_line(d, P['N'], neck_top, 0.05 * u, skin)
    # 5. 躯干
    N, Pp = P['N'], P['P']
    ax, ay = N[0] - Pp[0], N[1] - Pp[1]
    L = math.hypot(ax, ay) or 1
    ax, ay = ax / L, ay / L
    px, py = -ay, ax
    if view == 'side':
        top_w, bot_w = 0.15 * u * (1.15 if c.get('arm', 1) > 1.2 else 1), 0.135 * u
    else:
        top_w, bot_w = c['sw'] * 0.86 * u, c['hw'] * u
    Tc = (N[0] - ax * 0.005 * u, N[1] - ay * 0.005 * u)
    Bc = (Pp[0] - ax * 0.035 * u, Pp[1] - ay * 0.035 * u)
    quad = [(Tc[0] - px * top_w / 2, Tc[1] - py * top_w / 2), (Tc[0] + px * top_w / 2, Tc[1] + py * top_w / 2),
            (Bc[0] + px * bot_w / 2, Bc[1] + py * bot_w / 2), (Bc[0] - px * bot_w / 2, Bc[1] - py * bot_w / 2)]
    caps = []
    if view == 'front':
        for i in range(2):
            caps.append((P[f'S{i}'], 0.052 * u * arm_k ** 0.8))
    else:
        caps.append((lerp2(Tc, Bc, 0.12), top_w / 2))
    opoly_outline(d, quad, ow)
    for p, r in caps:
        d.ellipse((p[0] - r - ow, p[1] - r - ow, p[0] + r + ow, p[1] + r + ow), fill=INK)
    d.polygon(quad, fill=top_c)
    cap_col = skin if (c.get('sleeve', 2) <= 0) else top_c
    for p, r in caps:
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=cap_col if view == 'front' else top_c)
    # 衣服细节
    TL, TR, BR, BL = quad
    shade_pts = [lerp2(TL, TR, 0.72), TR, BR, lerp2(BL, BR, 0.72)]
    d.polygon(shade_pts, fill=dk(top_c, 0.86) + (255,))
    style = c['top']
    if style in ('pajama', 'shirt'):
        pc = tuple(c['pat_c']) + (150,)
        for k in range(1, 6):
            fr = k / 6
            d.line((lerp2(TL, TR, fr), lerp2(BL, BR, fr)), fill=pc, width=max(1, int(ow * 0.6)))
        for k in range(1, 6):
            fr = k / 6
            d.line((lerp2(TL, BL, fr), lerp2(TR, BR, fr)), fill=pc, width=max(1, int(ow * 0.6)))
    if style == 'puffer':
        for k in range(1, 4):
            fr = k / 4
            d.line((lerp2(TL, BL, fr), lerp2(TR, BR, fr)), fill=c['pat_c'], width=max(1, int(ow * 0.9)))
    if style == 'tank':
        mid = lerp2(TL, TR, 0.5)
        r = top_w * 0.26
        d.chord((mid[0] - r, mid[1] - r * 1.1, mid[0] + r, mid[1] + r * 0.9), 0, 180, fill=skin)
        d.arc((mid[0] - r, mid[1] - r * 1.1, mid[0] + r, mid[1] + r * 0.9), 0, 180, fill=INK, width=max(1, int(ow * 0.8)))
        for fr in (0.12, 0.88):
            d.line((lerp2(TL, TR, fr), lerp2(BL, BR, fr)), fill=tuple(c['pat_c']) + (230,), width=max(1, int(ow * 1.2)))
    if style in ('tee', 'hoodie', 'jacket', 'uniform', 'shirt', 'pajama', 'puffer', 'cardigan') and view == 'front':
        mid = lerp2(TL, TR, 0.5)
        r = top_w * 0.17
        if style in ('cardigan', 'pajama', 'shirt', 'uniform', 'jacket'):
            inner_c = {'cardigan': c['pat_c'], 'pajama': (250, 250, 250), 'shirt': (240, 244, 250), 'uniform': (210, 222, 240),
                       'jacket': (240, 240, 236)}[style]
            depth = 0.4 if style == 'cardigan' else 0.22
            v = [lerp2(TL, TR, 0.36), lerp2(TL, TR, 0.64), lerp2(lerp2(TL, BL, depth), lerp2(TR, BR, depth), 0.5)]
            opoly(d, v, inner_c, ow * 0.6)
            line_top = v[2]
            d.line((line_top, lerp2(BL, BR, 0.5)), fill=INK, width=max(1, int(ow * 0.7)))
            for k in range(3):
                q = lerp2(line_top, lerp2(BL, BR, 0.5), 0.2 + k * 0.3)
                ocircle(d, (q[0] + px * 0.012 * u, q[1] + py * 0.012 * u), 0.008 * u, lt(top_c, 0.5), ow * 0.3)
        else:
            d.chord((mid[0] - r, mid[1] - r, mid[0] + r, mid[1] + r), 0, 180, fill=skin)
            d.arc((mid[0] - r, mid[1] - r, mid[0] + r, mid[1] + r), 0, 180, fill=INK, width=max(1, int(ow * 0.8)))
        if style == 'hoodie':
            pk = [lerp2(lerp2(TL, BL, 0.62), lerp2(TR, BR, 0.62), 0.25), lerp2(lerp2(TL, BL, 0.62), lerp2(TR, BR, 0.62), 0.75),
                  lerp2(BL, BR, 0.82), lerp2(BL, BR, 0.18)]
            opoly(d, pk, dk(top_c, 0.9), ow * 0.6)
            for s in (0.42, 0.58):
                q = lerp2(TL, TR, s)
                d.line((q, (q[0], q[1] + 0.07 * u)), fill=WHITE, width=max(1, int(ow * 0.8)))
        if style == 'uniform':
            q = lerp2(lerp2(TL, BL, 0.3), lerp2(TR, BR, 0.3), 0.75)
            star(d, q[0], q[1], 0.022 * u, c['pat_c'], ink=INK, ow=ow * 0.4)
    if 'bib' in c.get('acc', ()) and view == 'front':
        cen = lerp2(lerp2(TL, BL, 0.48), lerp2(TR, BR, 0.48), 0.5)
        bw, bh = 0.075 * u, 0.06 * u
        d.rounded_rectangle((cen[0] - bw - ow, cen[1] - bh - ow, cen[0] + bw + ow, cen[1] + bh + ow), radius=0.01 * u, fill=INK)
        d.rounded_rectangle((cen[0] - bw, cen[1] - bh, cen[0] + bw, cen[1] + bh), radius=0.01 * u, fill=(250, 250, 250))
        d.text(cen, '50', font=F('Black', max(8, int(0.085 * u))), fill=INK, anchor='mm')
    if 'backpack' in c.get('acc', ()) and view == 'front':
        for fr in (0.2, 0.8):
            d.line((lerp2(TL, TR, fr), lerp2(BL, BR, fr * 0.9 + 0.05)), fill=(40, 44, 56), width=max(2, int(0.022 * u)))
    if 'towel' in c.get('acc', ()):
        s0 = lerp2(TL, TR, 0.75)
        opoly(d, [(s0[0] - 0.03 * u, s0[1] - 0.01 * u), (s0[0] + 0.07 * u, s0[1] - 0.012 * u), (s0[0] + 0.06 * u, s0[1] + 0.16 * u),
                  (s0[0] + 0.0, s0[1] + 0.16 * u)], (246, 246, 240), ow * 0.8)
        d.line(((s0[0] - 0.0, s0[1] + 0.13 * u), (s0[0] + 0.06 * u, s0[1] + 0.13 * u)), fill=(120, 170, 230), width=max(1, int(ow)))
    if 'keys' in c.get('acc', ()):
        q = lerp2(BL, BR, 0.78 if view == 'front' else 0.3)
        d.ellipse((q[0] - 0.018 * u, q[1] - 0.018 * u, q[0] + 0.018 * u, q[1] + 0.018 * u), outline=(220, 220, 228), width=max(2, int(ow)))
        for k in (-1, 0, 1):
            d.line(((q[0] + k * 0.01 * u, q[1] + 0.016 * u), (q[0] + k * 0.016 * u, q[1] + 0.06 * u)), fill=(235, 210, 90), width=max(2, int(ow * 1.1)))
    if 'scarf' in c.get('acc', ()):
        y = N[1] + 0.01 * u
        sw_ = 0.085 * u
        opoly(d, [(N[0] - sw_, y - 0.03 * u), (N[0] + sw_, y - 0.03 * u), (N[0] + sw_ * 0.9, y + 0.03 * u), (N[0] - sw_ * 0.9, y + 0.03 * u)],
              (222, 48, 60), ow * 0.8)
        tail_x = N[0] + (sw_ * 0.45 if view == 'front' else -f * sw_ * 0.8)
        sway = wind * 0.12 * u * (-f if view == 'side' else 1)
        opoly(d, [(tail_x - 0.025 * u, y), (tail_x + 0.025 * u, y), (tail_x + 0.03 * u + sway, y + 0.13 * u), (tail_x - 0.02 * u + sway, y + 0.13 * u)],
              (198, 38, 50), ow * 0.7)
    if 'phones_neck' in c.get('acc', ()):
        y = N[1] - 0.01 * u
        d.arc((N[0] - 0.075 * u, y - 0.04 * u, N[0] + 0.075 * u, y + 0.06 * u), 0, 180, fill=INK, width=max(2, int(0.02 * u)))
        for s in ((-1, 1) if view == 'front' else (f,)):
            ocircle(d, (N[0] + s * 0.068 * u, y + 0.01 * u), 0.03 * u, (40, 40, 48), ow * 0.8)
            d.ellipse((N[0] + s * 0.068 * u - 0.014 * u, y - 0.004 * u, N[0] + s * 0.068 * u + 0.014 * u, y + 0.024 * u), fill=(255, 150, 50))
    # 6. 头
    ph = (sum(map(ord, key)) % 11) * 0.29 if isinstance(key, str) else 0.0
    hc_img, (hcx, hcy), (rx, ry) = head_canvas(c, e, view, f, u, ow, talk, t,
                                                bool(blink) if blink is not None else ((t + ph) % 3.3) < 0.1, glint)
    if 'phones_head' in c.get('acc', ()):
        hd = ImageDraw.Draw(hc_img, 'RGBA')
        hd.arc((hcx - rx * 1.15, hcy - ry * 1.3, hcx + rx * 1.15, hcy + ry * 0.6), 190, 350, fill=INK, width=max(2, int(0.022 * u)))
        for s in ((-1, 1) if view == 'front' else (-f * 0.1,)):
            x = hcx + s * rx * 1.05
            hd.rounded_rectangle((x - rx * 0.2 - ow, hcy - ry * 0.32 - ow, x + rx * 0.2 + ow, hcy + ry * 0.38 + ow), radius=rx * 0.12, fill=INK)
            hd.rounded_rectangle((x - rx * 0.2, hcy - ry * 0.32, x + rx * 0.2, hcy + ry * 0.38), radius=rx * 0.12, fill=(230, 70, 90))
    if abs(head_ang) > 1e-3:
        hc_img = hc_img.rotate(-head_ang * 180 / math.pi, resample=Image.BICUBIC, expand=True)
    hx0, hy0 = int(round(P['Hc'][0] - hc_img.width / 2)), int(round(P['Hc'][1] - hc_img.height / 2))
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    layer.paste(hc_img, (hx0, hy0))
    img.alpha_composite(layer)
    # 7. 前面的手臂和手里的东西
    hands = {}
    for i in ((1,) if view == 'side' else (0, 1)):
        hands[f'W{i}'] = arm(i)
    if view == 'side':
        hands['W0'] = P['W0']
    if hold:
        items = hold.items() if isinstance(hold, dict) else [(hold, 'W1')]
        for item, where in items:
            hold_item(d, item, hands.get(where, P.get(where)), u, ow, dict(t=t, **(hold_ctx or {})))
    # 8. 头顶的符号
    head_fx(d, e['fx'], P['Hc'], rx, ry, u, ow, t, f)
    if stone > 0:
        img = petrify(img, stone, u, P)
    if ss == 2:
        img = img.resize((Wc // 2, Hc_ // 2), Image.LANCZOS)
        return img, (ox / 2, oy / 2), {k: (v[0] / 2, v[1] / 2) for k, v in P.items()}
    return img, (ox, oy), P


def head_fx(d, fx, H, rx, ry, u, ow, t, f):
    x, y = H
    if 'shock' in fx:
        for k, a in enumerate((-0.6, 0.0, 0.6)):
            r0, r1 = ry * 1.25, ry * 1.65
            d.line(((x + math.sin(a) * r0, y - math.cos(a) * r0), (x + math.sin(a) * r1, y - math.cos(a) * r1)), fill=INK, width=max(2, int(ow * 1.4)))
    if 'sweats' in fx:
        for k in range(3):
            ph = (t * 2.2 + k / 3) % 1
            a = -0.9 + k * 0.5
            r = ry * (1.2 + 0.6 * ph)
            drop(d, x + math.sin(a) * r * 1.3, y - math.cos(a) * r, rx * 0.1 * (1 - 0.4 * ph), ow=ow)
    if 'anger' in fx:
        ax, ay = x + rx * 0.75, y - ry * 0.85
        s = rx * 0.22 * (1 + 0.1 * math.sin(t * 20))
        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            ccx, ccy = ax + dx * s, ay + dy * s
            toward = math.degrees(math.atan2(-dy, -dx))
            d.arc((ccx - s * 0.85, ccy - s * 0.85, ccx + s * 0.85, ccy + s * 0.85), toward - 50, toward + 50, fill=(230, 40, 50),
                  width=max(2, int(ow * 1.6)))
    if 'question' in fx:
        d.text((x + rx * 1.0, y - ry * 1.3), '？', font=F('Black', int(ry * 0.9)), fill=WHITE, anchor='mm', stroke_width=int(ow * 1.2), stroke_fill=INK)
    if 'exclaim' in fx:
        d.text((x + rx * 1.0, y - ry * 1.3), '！', font=F('Black', int(ry * 0.9)), fill=(255, 220, 60), anchor='mm', stroke_width=int(ow * 1.2), stroke_fill=INK)
    if 'sparkle' in fx:
        for k, (dx, dy) in enumerate(((-1.3, -0.9), (1.35, -0.6), (1.1, 0.9))):
            s = 0.6 + 0.4 * math.sin(t * 8 + k * 2)
            sparkle(d, x + dx * rx, y + dy * ry, rx * 0.28 * s, (255, 245, 180))
    if 'hearts' in fx:
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1
            heart(d, x + (-1.1 + k * 1.1) * rx + math.sin(t * 4 + k) * rx * 0.1, y - ry * (1.2 + 1.2 * ph), rx * 0.18 * (1 - 0.3 * ph),
                  (250, 70, 110), ow * 0.6)
    if 'zzz' in fx:
        for k in range(3):
            ph = (t * 0.6 + k / 3) % 1
            d.text((x + rx * (0.9 + ph * 0.6), y - ry * (0.9 + ph * 1.2)), 'Z', font=F('Black', int(ry * (0.35 + 0.2 * k))),
                   fill=(220, 230, 255, int(255 * (1 - ph))), anchor='mm', stroke_width=max(1, int(ow * 0.6)), stroke_fill=INK)
    if 'soul' in fx:
        ph = (t * 0.7) % 1
        sx_, sy_ = x + f * rx * 0.1 + math.sin(t * 3) * rx * 0.2, y - ry * (0.6 + ph * 1.6)
        a = int(200 * (1 - ph * 0.5))
        d.ellipse((sx_ - rx * 0.4, sy_ - ry * 0.4, sx_ + rx * 0.4, sy_ + ry * 0.35), fill=(240, 244, 255, a))
        d.polygon([(sx_ - rx * 0.35, sy_), (sx_ + rx * 0.35, sy_), (sx_ + rx * 0.05, sy_ + ry * 0.75)], fill=(240, 244, 255, a))
        d.ellipse((sx_ - rx * 0.16, sy_ - ry * 0.1, sx_ - rx * 0.06, sy_), fill=(60, 60, 80, a))
        d.ellipse((sx_ + rx * 0.06, sy_ - ry * 0.1, sx_ + rx * 0.16, sy_), fill=(60, 60, 80, a))


def petrify(img, k, u, P):
    arr = np.array(img).astype(np.float32)
    rgbv = arr[..., :3]
    g = rgbv.mean(axis=2, keepdims=True)
    stone = np.concatenate([g * 0.75 + 70, g * 0.75 + 72, g * 0.75 + 80], axis=2)
    arr[..., :3] = rgbv * (1 - k) + stone * k
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    if k > 0.6:
        d = ImageDraw.Draw(out, 'RGBA')
        rng = np.random.default_rng(3)
        for start in (P['Hc'], P['N'], P['P']):
            x, y = start
            pts = [(x, y)]
            for _ in range(5):
                x += rng.uniform(-0.04, 0.04) * u
                y += rng.uniform(0.02, 0.05) * u
                pts.append((x, y))
            d.line(pts, fill=(60, 60, 70, int(255 * (k - 0.6) / 0.4)), width=max(2, int(0.006 * u)))
    return out


def put(frame, key, pose, x, y, h, shadow=False, **kw):
    """把人画到 frame 上，骨盆落在 (x, y)。返回关节在画面里的位置。"""
    img, (px_, py_), P = render(key, pose, h, **kw)
    ox, oy = int(round(x - px_)), int(round(y - py_))
    if shadow and not pose.get('bust'):
        fy = max(P['A0'][1], P['A1'][1]) + oy + 0.03 * h
        sd = ImageDraw.Draw(frame, 'RGBA')
        sd.ellipse((x - 0.16 * h, fy - 0.025 * h, x + 0.16 * h, fy + 0.025 * h), fill=(0, 0, 0, 70))
    if frame.mode == 'RGBA':
        layer = Image.new('RGBA', frame.size, (0, 0, 0, 0))
        layer.paste(img, (ox, oy))
        frame.alpha_composite(layer)
    else:
        frame.paste(img, (ox, oy), img)
    return {k: (v[0] + ox, v[1] + oy) for k, v in P.items()}


def put_on(frame, key, pose, x, ground, h, facing=1, **kw):
    """脚踩在 ground 上。"""
    c = CH[key] if isinstance(key, str) else key
    J = joints(c, pose, facing)
    fy = max(J['A0'][1], J['A1'][1]) + 0.045
    return put(frame, key, pose, x, ground - fy * h, h, facing=facing, **kw)


# ---------------------------------------------------------------- 常用姿势
def stand(view='front'):
    if view == 'front':
        return dict(view='front', arms=((8, 6), (8, 6)), legs=((3, 0), (3, 0)))
    return dict(view='side', arms=((-8, 10), (8, 14)), legs=((-4, 3), (5, 3)))


def run(ph, lean=18, amp=1.0):
    legs, arms = [], []
    for i in range(2):
        q = ph + i * math.pi
        legs.append((amp * 42 * math.sin(q) + 8, 25 + 75 * (0.5 + 0.5 * math.sin(q - math.pi / 2))))
        arms.append((-amp * 55 * math.sin(q), 90))
    return dict(view='side', lean=lean, head=-lean * 0.6, arms=tuple(arms), legs=tuple(legs))


def bob(ph, h, amp=1.0):
    return -0.03 * h * abs(math.cos(ph)) * amp


def head_icon(key, size, expr='neutral', talk=0.0, t=0.0, bg=None, glint=False, blink=False):
    """圆形头像：只画头，放在一个底色圆里。"""
    c = CH[key] if isinstance(key, str) else key
    u = size / (HEAD_RY * 2.0) * 0.62 * 2
    ow = max(1.5, 0.0078 * u)
    e = resolve_expr(expr)
    img, (cx, cy), (rx, ry) = head_canvas(c, e, 'front', 1, u, ow, talk, t, blink, glint)
    out = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0))
    m = Image.new('L', (size * 2, size * 2), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * 2 - 1, size * 2 - 1), fill=255)
    base = Image.new('RGBA', (size * 2, size * 2), tuple(bg or lt(c['top_c'], 0.2)) + (255,))
    base.alpha_composite(img, (int(size - cx), int(size * 1.12 - cy)))
    out.paste(base, (0, 0), m)
    return out.resize((size, size), Image.LANCZOS)
