// sections.js — 怎么听 ①②③ (32–128) and 照着做 (128–160), music-player look (Skill 2.3: own props and layouts):
// a "now playing" header per step, a recited poem, album covers, a rating slider, tempo × volume pads, a volume bar,
// an arithmetic worksheet + LCD, task tiles and a 3-channel mixer for the summary.
// Not used: the earlier episodes' bars, wall clock, timer ring, alarm, calendar, HUD panel, list table, word cards, window.
const cr = (s) => ({ s, color: COL.cream });
const hl = (s, color) => ({ s, color });

// ---------- header: "now playing" card (album square with the number, title, line 2, typed subtitle, progress) ----------
function nowPlaying(h, bt, o = {}) {
  const { alpha = 1, dx = 0 } = o;
  withAlpha(alpha, () => {
    const x = 140 + dx, y = 58, w = 980, hh = 198;
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 8;
    rrect(x, y, w, hh, 24, 'rgba(12,24,54,0.95)', rgba(h.color, 0.6), 2.5); ctx.restore();
    lintPanel('header', x, y, x + w, y + hh);
    const a = 150, ax = x + 22, ay = y + 24;
    const g = ctx.createLinearGradient(ax, ay, ax + a, ay + a);
    g.addColorStop(0, h.color); g.addColorStop(1, lerpColor(h.color, '#0b1736', 0.45));
    ctx.save(); ctx.shadowColor = h.color; ctx.shadowBlur = 18; rrect(ax, ay, a, a, 18, g); ctx.restore();
    if (h.num) txt(h.num, ax + a / 2, ay + a / 2 + 4, { size: 104, weight: 800, fam: 'mono', color: '#0b1736', align: 'center' });
    else drawFaderIcon(ax + a / 2, ay + a / 2, 90, '#0b1736');
    const tx = ax + a + 30;
    txt(h.title, tx, y + 54, { size: 54, weight: 900, color: COL.cream });
    rich(h.line2(bt), tx, y + 114, { size: 44, weight: 900 });
    typeText(h.sub, seg(bt, h.from + 0.5, h.from + 2.9), tx + 2, y + 156, { size: 22, weight: 500, fam: 'mono', color: '#8d99b5' }, bt);
    const lx0 = tx, lx1 = x + w - 34, ly = y + 180, prog = seg(bt, h.from, h.to);
    line(lx0, ly, lx1, ly, 'rgba(200,212,236,0.2)', 4);
    if (prog > 0) { line(lx0, ly, lerp(lx0, lx1, prog), ly, h.color, 4); circle(lerp(lx0, lx1, prog), ly, 6, COL.cream); }
  });
}
function drawFaderIcon(x, y, s, color) {
  for (const [dx, k] of [[-0.28, 0.65], [0, 0.3], [0.28, 0.5]]) {
    line(x + dx * s, y - s * 0.36, x + dx * s, y + s * 0.36, color, s * 0.06);
    rrect(x + dx * s - s * 0.1, y - s * 0.36 + k * s * 0.72 - s * 0.06, s * 0.2, s * 0.12, s * 0.03, color);
  }
}
const HEADERS = [
  { from: 32, to: 64, num: '1', color: LYR, title: '别听带词的歌', sub: 'Memorizing or reading: lyrics off, favourites too',
    line2: () => [cr('背书、读书时，'), hl('喜欢的歌也一样', LYR)] },
  { from: 64, to: 96, num: '2', color: INST, title: '想听就换纯音乐', sub: 'Want music? Instrumental, slow and soft',
    line2: () => [hl('慢一点、小声一点', COL.greenHi)] },
  { from: 96, to: 126.8, num: '3', color: COL.yellow, title: '算题影响不明显', sub: 'Arithmetic: barely affected',
    line2: () => [cr('背和读的时候，'), hl('再关掉', COL.yellow)] },
  { from: 126.9, to: 161, num: null, color: COL.cyan, title: '照着做', sub: 'While studying, set it like this',
    line2: () => [cr('背书时，'), hl('这样调', COL.cyanHi)] },
];
function drawHeaders(bt) {
  for (const h of HEADERS) {
    const inP = EASE.out(seg(bt, h.from - 0.5, h.from + 0.4)), outP = EASE.in(seg(bt, h.to - 0.5, h.to));
    const a = inP * (1 - outP);
    if (a <= 0) continue;
    nowPlaying(h, bt, { alpha: a, dx: (1 - inP) * -40 - outP * 40 });
  }
}
// right-hand stage for the visuals (the boy sits on the left from beat 32)
const STAGE = { x: 1290 };
function caption(spans, y, a, size = 40) { if (a > 0) rich(spans, STAGE.x, y, { size, weight: 900, align: 'center', alpha: a }); }

// ---------- ① 别听带词的歌 ----------
// 15.5 s: he recites 床前明月光 while a song with lyrics plays; the lyrics get into the second line (示意).
const POEM = { x: 1290, y: 470, w: 860, h: 250 };
function drawPoem(bt, boy) {
  if (bt < 33.5 || bt > 44) return;
  const a = popA(bt, 33.5, 0.5) * (1 - seg(bt, 43, 43.5));
  if (a <= 0) return;
  const { x, y, w, h } = POEM;
  withAlpha(a, () => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 24; ctx.fillStyle = PAPER;
    ctx.beginPath(); ctx.moveTo(x - w / 2 + 10, y + 30); ctx.lineTo(boy.headX + 120, boy.headY + 34); ctx.lineTo(x - w / 2 + 10, y + 96); ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.roundRect(x - w / 2, y - h / 2, w, h, 40); ctx.fill(); ctx.restore();
    lintPanel('poem', x - w / 2, y - h / 2, x + w / 2, y + h / 2);
    txt('示意', x + w / 2 - 32, y - h / 2 + 34, { size: 30, weight: 700, color: '#7a85a3', align: 'right' });
    const L1 = '床前明月光，', L2 = '疑是地上', lx = x - w / 2 + 64;
    const n1 = bt < 34 ? 0 : Math.min(6, Math.floor((bt - 34) / 0.5) + 1), n2 = bt < 37 ? 0 : Math.min(4, Math.floor((bt - 37) / 0.5) + 1);
    txt(L1.slice(0, n1), lx, y - 52, { size: 80, weight: 900, color: PAPER_INK });
    const w2 = rich([{ s: L2.slice(0, n2), color: PAPER_INK }], lx, y + 56, { size: 80, weight: 900 });
    if (bt >= 39.5) {
      const ea = popA(bt, 39.5, 0.3);
      rich([{ s: '……啦啦？', color: '#d6336c' }], lx + w2, y + 56, { size: 80, weight: 900, alpha: ea });
      const cs = popS(bt, 39.5, 0.5);
      if (cs > 0) withScale(x + w / 2 - 62, y + 56, cs, () => crossMark(x + w / 2 - 62, y + 56, 30, LYR));
    }
  });
  // the lyric bubble that gets into the poem (38 -> 39.5), from his right ear cup
  if (bt >= 38 && bt < 39.5) {
    const e = EASE.inOut(seg(bt, 38, 39.5)), [sx, sy] = boy.cups[1], cx = 820, cy = 560, ex = x + 210, ey = y + 56;
    drawLyricBubble((1 - e) * (1 - e) * sx + 2 * (1 - e) * e * cx + e * e * ex, (1 - e) * (1 - e) * sy + 2 * (1 - e) * e * cy + e * e * ey, { scale: 0.85 * popS(bt, 38, 0.4) });
  }
  if (bt >= 39.5 && bt < 40) popRing(x + 210, y + 56, seg(bt, 39.5, 40), LYR);
  caption([cr('听得懂的'), hl('歌词', LYR), cr('，脑子会忍不住去听')], 664, popA(bt, 40, 0.4) * (1 - seg(bt, 43, 43.5)));
}
// 20.6 s: quiet vs a favourite song vs a disliked one (Perham & Vizard 2011: serial recall; Perham & Currie 2014: reading)
const ALBUMS = [
  { x: 1000, label: '安静', kind: 'quiet', color: QUIET, at: 44 },
  { x: 1310, label: '最爱的歌', kind: 'fave', color: LYR, at: 45 },
  { x: 1620, label: '讨厌的重金属', kind: 'metal', color: '#9aa6c2', at: 46 },
];
function albumCover(x, y, kind, color) {
  const a = 204;
  const g = ctx.createLinearGradient(x - a / 2, y - a / 2, x + a / 2, y + a / 2);
  g.addColorStop(0, lerpColor(color, '#0b1736', 0.25)); g.addColorStop(1, lerpColor(color, '#0b1736', 0.75));
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 20; ctx.shadowOffsetY = 6;
  rrect(x - a / 2, y - a / 2, a, a, 22, g, rgba(color, 0.8), 2.5); ctx.restore();
  lintPanel('album:' + kind, x - a / 2, y - a / 2, x + a / 2, y + a / 2);
  if (kind === 'quiet') iconQuiet(x, y, 112, COL.cream);
  else {
    iconHeadphones(x, y - 8, 122, COL.cream);
    if (kind === 'fave') iconHeart(x, y + 14, 58, COL.pinkHi);
    else iconBolt(x, y + 14, 60, '#ffd57e');
  }
}
function drawFavourites(bt) {
  if (bt < 43.8 || bt > 56.2) return;
  const out = 1 - seg(bt, 55.5, 56);
  withAlpha(out, () => {
    for (const al of ALBUMS) {
      const sc = popS(bt, al.at, 0.6);
      if (sc <= 0) continue;
      withScale(al.x, 448, sc, () => albumCover(al.x, 448, al.kind, al.color));
      txt(al.label, al.x, 600, { size: 40, weight: 900, color: COL.cream, align: 'center', alpha: popA(bt, al.at, 0.3) });
    }
    const ok = popS(bt, 48, 0.6);
    if (ok > 0) withScale(1084, 364, ok, () => okMark(1084, 364, 30, seg(bt, 48, 48.7), QUIET));
    txt('记得多', 1000, 656, { size: 38, weight: 900, color: COL.cyanHi, align: 'center', alpha: popA(bt, 48, 0.3) });
    const eq = popS(bt, 48.5, 0.5);
    if (eq > 0) withScale(1465, 448, eq, () => txt('=', 1465, 444, { size: 96, weight: 900, color: LYR, align: 'center', glow: 16 }));
    txt('一样，都比安静差', 1465, 656, { size: 38, weight: 900, color: LYR, align: 'center', alpha: popA(bt, 49, 0.3) });
  });
  caption([cr('自己挑的'), hl('最爱的歌', LYR), cr('，和讨厌的重金属一样拖后腿')], 742, popA(bt, 49.5, 0.4) * out, 38);
  sourceNote('两个小实验 · Perham & Vizard 2011（记一串字母）· Perham & Currie 2014（读文章）', 760, 948, { alpha: popA(bt, 50.5, 0.5) * out });
}
// 26.3 s: Sun et al. 2024 as one example (only 15 students per group): lyrics in the language of the text hurt most
function closedBook(x, y, label, spine) {
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 16; ctx.shadowOffsetY = 6;
  rrect(x - 82, y - 104, 164, 208, 14, PAPER); ctx.restore();
  rrect(x - 82, y - 104, 28, 208, [14, 0, 0, 14], spine);
  txt(label, x + 14, y, { size: 56, weight: 900, color: PAPER_INK, align: 'center' });
  lintPanel('book:' + label, x - 82, y - 104, x + 82, y + 104);
}
function drawLanguages(bt) {
  if (bt < 56 || bt > 60.4) return;
  const a = popA(bt, 56, 0.4) * (1 - seg(bt, 59.5, 60));
  withAlpha(a, () => {
    [[1050, '中文', '中文歌'], [1530, '英文', '英文歌']].forEach(([x, book, song], k) => {
      const sc = popS(bt, 56 + k * 0.5, 0.6);
      if (sc <= 0) return;
      withScale(x, 470, sc, () => {
        closedBook(x - 60, 492, book, k ? COL.cyan : COL.yellow);
        drawLyricBubble(x + 92, 360, { scale: 1.2, text: song });
      });
      const m = popS(bt, 57.5 + k * 0.5, 0.5);
      if (m > 0) withScale(x + 104, 520, m, () => crossMark(x + 104, 520, 34, LYR));
    });
    caption([cr('国内一个小实验：读中文听中文歌、读英文听英文歌，'), hl('最伤', LYR)], 670, popA(bt, 57, 0.4), 36);
    sourceNote('Sun 等 2024 · 《Frontiers in Psychology》 · 每组只有 15 人，只当个例子', 760, 948, { alpha: popA(bt, 57.5, 0.5) });
  });
}
// 28.1 s: the headphones come off
function drawLyricsOff(bt) {
  if (bt < 59.8 || bt > 63.6) return;
  const a = popA(bt, 60, 0.4) * (1 - seg(bt, 62.5, 63.3));
  withAlpha(a, () => {
    rich([cr('背书、读书：'), hl('关掉带词的歌', LYR)], STAGE.x, 450, { size: 56, weight: 900, align: 'center' });
    if (bt < 60.5) drawLyricBubble(STAGE.x, 580, { scale: popS(bt, 60, 0.4) });
    else popRing(STAGE.x, 580, seg(bt, 60.5, 61), LYR);
    const q = popS(bt, 61, 0.5);
    if (q > 0) withScale(STAGE.x, 580, q, () => iconQuiet(STAGE.x, 580, 80, COL.cyanHi));
  });
}
function drawStep1(bt, boy) {
  if (bt < 33 || bt > 64) return;
  drawPoem(bt, boy);
  drawFavourites(bt);
  drawLanguages(bt);
  drawLyricsOff(bt);
}

// ---------- ② 想听就换纯音乐 ----------
// 30.5 s: the opening's numbers again (20 words, same students): quiet 8.4, instrumental 7.9, lyrics 7.4
function chip(x, y, icon, label, num, color, a) {
  withAlpha(a, () => {
    rrect(x - 140, y - 59, 280, 118, 22, 'rgba(12,26,58,0.92)', rgba(color, 0.75), 2.5);
    lintPanel('chip:' + label, x - 140, y - 59, x + 140, y + 59);
    circle(x - 84, y, 38, rgba(color, 0.2), color, 2.5);
    ICONS[icon](x - 84, y, icon === 'note' ? 44 : 50, color);
    txt(label, x - 32, y - 24, { size: 34, weight: 900, color: COL.cream });
    txt(num, x - 32, y + 26, { size: 52, weight: 800, fam: 'mono', color });
  });
}
function drawRecap(bt) {
  if (bt < 65 || bt > 70) return;
  const out = 1 - seg(bt, 69.5, 70);
  caption([hl('纯音乐', COL.greenHi), cr('：和安静差得不明显')], 372, popA(bt, 65.5, 0.4) * out, 50);
  [[980, 'quiet', '安静', '8.4', QUIET], [1290, 'note', '纯音乐', '7.9', INST], [1600, 'lyric', '带词的歌', '7.4', LYR]]
    .forEach(([x, ic, l, n, c], k) => chip(x, 496, ic, l, n, c, popA(bt, 66 + k * 0.5, 0.4) * out));
  txt('开头那个实验：背 20 个词，平均记住几个', STAGE.x, 618, { size: 34, weight: 700, color: COL.grayHi, align: 'center', alpha: popA(bt, 68, 0.4) * out });
}
// 32.8 s: how did they think the music affected them? (post-task ratings after the reading task, −10..+10)
const SLIDER = { x0: 970, x1: 1610, y: 492 };
const sliderX = (v) => lerp(SLIDER.x0, SLIDER.x1, (v + 10) / 20);
function drawRating(bt) {
  if (bt < 69.8 || bt > 76.8) return;
  const out = 1 - seg(bt, 76, 76.6);
  withAlpha(out, () => {
    caption([cr('读完问大家：'), hl('纯音乐', COL.greenHi), cr('有帮助吗？')], 372, popA(bt, 70, 0.4), 42);
    const ta = popA(bt, 70, 0.4);
    if (ta > 0) withAlpha(ta, () => {
      line(SLIDER.x0, SLIDER.y, SLIDER.x1, SLIDER.y, 'rgba(200,212,236,0.3)', 10);
      for (const v of [-10, -5, 0, 5, 10]) line(sliderX(v), SLIDER.y - (v ? 14 : 22), sliderX(v), SLIDER.y + (v ? 14 : 22), 'rgba(200,212,236,0.5)', 3);
      txt('拖后腿', SLIDER.x0, SLIDER.y + 58, { size: 34, weight: 900, color: COL.grayHi, align: 'center' });
      txt('有帮助', SLIDER.x1, SLIDER.y + 58, { size: 34, weight: 900, color: COL.grayHi, align: 'center' });
      lintPanel('slider', SLIDER.x0 - 50, SLIDER.y - 30, SLIDER.x1 + 50, SLIDER.y + 30);
    });
    // means: instrumental +2.3, lyrics −1.4 (Souza & Barbosa 2023, reading task)
    const kp = EASE.out(seg(bt, 70.5, 71.3)), kg = EASE.out(seg(bt, 71, 71.8));
    if (ta > 0) {
      const xp = sliderX(-1.36 * kp), xg = sliderX(2.32 * kg);
      ctx.save(); ctx.shadowColor = LYR; ctx.shadowBlur = 14; circle(xp, SLIDER.y, 20, LYR, '#0d1838', 3); ctx.restore();
      ctx.save(); ctx.shadowColor = INST; ctx.shadowBlur = 14; circle(xg, SLIDER.y, 20, INST, '#0d1838', 3); ctx.restore();
      txt('带词的歌', xp, SLIDER.y + 58, { size: 34, weight: 900, color: LYR, align: 'center', alpha: popA(bt, 71.5, 0.3) });
      txt('纯音乐', xg, SLIDER.y - 54, { size: 34, weight: 900, color: COL.greenHi, align: 'center', alpha: popA(bt, 72, 0.3) });
    }
    caption([cr('大家觉得：纯音乐'), hl('有一点帮助', COL.greenHi)], 612, popA(bt, 72, 0.4), 36);
    // the stamp: accuracy was about the same
    const st = seg(bt, 73, 73.35);
    if (st > 0) {
      const sc = lerp(1.6, 1, EASE.out(st)), sa = clamp(st * 3);
      withAlpha(sa, () => {
        ctx.save(); ctx.translate(STAGE.x, 716); ctx.rotate(-0.06); ctx.scale(sc, sc);
        ctx.shadowColor = COL.yellow; ctx.shadowBlur = 18;
        rrect(-250, -50, 500, 100, 18, 'rgba(247,185,62,0.12)', COL.yellow, 5);
        ctx.shadowBlur = 0;
        txt('正确率其实差不多', 0, 2, { size: 50, weight: 900, color: COL.yellow, align: 'center' });
        lintPanel('stamp', -250, -50, 250, 50);
        ctx.restore();
      });
    }
  });
  sourceNote('Souza & Barbosa 2023 · 读句子任务后的自评（−10 到 +10）· 正确率：纯音乐 94.7%，安静 93.9%', 760, 948, { alpha: popA(bt, 73.5, 0.5) * out });
}
// 36 s: instrumental music, slow / fast × soft / loud (Thompson et al. 2012, Mozart piano, reading comprehension)
const PADS = [
  { x: 1100, y: 474, label: '慢 · 小声', at: 80, ok: true },
  { x: 1480, y: 474, label: '慢 · 大声', at: 81, ok: true },
  { x: 1100, y: 616, label: '快 · 小声', at: 82, ok: true },
  { x: 1480, y: 616, label: '快 · 大声', at: 86, ok: false },
];
function drawPads(bt) {
  if (bt < 76.8 || bt > 88.4) return;
  const out = 1 - seg(bt, 87.5, 88);
  withAlpha(out, () => {
    caption([cr('纯音乐也要挑')], 360, popA(bt, 77, 0.4), 44);
    PADS.forEach((p, k) => {
      const a = popA(bt, 77.5 + k * 0.5, 0.4);
      if (a <= 0) return;
      const lit = bt >= p.at, c = p.ok ? INST : LYR;
      const pre = !p.ok && bt < p.at ? seg(bt, 84.5, 86) : 0;
      withAlpha(a, () => {
        ctx.save(); if (lit || pre > 0) { ctx.shadowColor = lit ? c : COL.cream; ctx.shadowBlur = lit ? 22 : 14 * pre; }
        rrect(p.x - 170, p.y - 58, 340, 116, 24, lit ? rgba(c, 0.22) : 'rgba(255,255,255,0.05)', lit ? c : `rgba(200,212,236,${0.35 + 0.4 * pre})`, 3);
        ctx.restore();
        lintPanel('pad' + k, p.x - 170, p.y - 58, p.x + 170, p.y + 58);
        txt(p.label, p.x - 34, p.y + 1, { size: 44, weight: 900, color: lit ? COL.cream : COL.grayHi, align: 'center' });
        if (lit) {
          const m = popS(bt, p.at, 0.5);
          withScale(p.x + 118, p.y, m, () => (p.ok ? okMark(p.x + 118, p.y, 27, seg(bt, p.at, p.at + 0.6), INST) : crossMark(p.x + 118, p.y, 27, LYR)));
        }
      });
    });
    caption([hl('又快又响', LYR), cr('，读文章答对的少了')], 742, popA(bt, 86.5, 0.4), 40);
  });
  sourceNote('Thompson 等 2012 · 25 名大学生 · 莫扎特钢琴曲 · 快 150 / 慢 110 拍每分钟 · 大声 72 / 小声 60 分贝', 760, 948, { alpha: popA(bt, 87, 0.5) * out });
}
// 41.25 s: he turns it down
function drawVolume(bt) {
  if (bt < 87.8 || bt > 96) return;
  const a = popA(bt, 88, 0.4) * (1 - seg(bt, 95, 95.6));
  withAlpha(a, () => {
    const x0 = 1080, x1 = 1600, y = 440, v = lerp(0.85, 0.35, EASE.inOut(seg(bt, 88.5, 89.5)));
    // speaker without the cross + three arcs that disappear as it gets quieter
    ctx.save(); ctx.fillStyle = COL.cream; ctx.beginPath();
    ctx.moveTo(990, y - 12); ctx.lineTo(1006, y - 12); ctx.lineTo(1026, y - 30); ctx.lineTo(1026, y + 30); ctx.lineTo(1006, y + 12); ctx.lineTo(990, y + 12); ctx.closePath(); ctx.fill(); ctx.restore();
    for (let k = 0; k < 3; k++) {
      const on = clamp((v - k * 0.3) / 0.3);
      if (on <= 0) continue;
      ctx.save(); ctx.globalAlpha *= on; ctx.strokeStyle = COL.cream; ctx.lineWidth = 4; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.arc(1030, y, 14 + k * 11, -0.7, 0.7); ctx.stroke(); ctx.restore();
    }
    rrect(x0, y - 11, x1 - x0, 22, 11, 'rgba(255,255,255,0.1)');
    ctx.save(); ctx.shadowColor = INST; ctx.shadowBlur = 14; rrect(x0, y - 11, (x1 - x0) * v, 22, 11, INST); ctx.restore();
    circle(x0 + (x1 - x0) * v, y, 22, COL.cream, '#0d1838', 3);
    lintPanel('volume', 980, y - 34, x1 + 24, y + 34);
    rich([cr('想听：'), hl('纯音乐', COL.greenHi), cr('，别又快又响')], STAGE.x, 568, { size: 52, weight: 900, align: 'center' });
    txt('纯音乐不会让你背得更好', STAGE.x, 642, { size: 34, weight: 700, color: COL.grayHi, align: 'center', alpha: popA(bt, 90, 0.4) });
  });
}
function drawStep2(bt) {
  if (bt < 64 || bt > 97) return;
  drawRecap(bt);
  drawRating(bt);
  drawPads(bt);
  drawVolume(bt);
}

// ---------- ③ 算题影响不明显 ----------
// 45.5 s: the paper's arithmetic problems (a × b + c, a × b − c, a + b × c; 8 s each, five options); accuracy
// silence 69.1 %, instrumental 68.4 %, lyrics 67.5 % (d = −0.11, evidence for no effect)
const PROBLEMS = [['4 × 9 + 8 = ', '44', 98], ['7 × 5 − 3 = ', '32', 100], ['9 + 3 × 8 = ', '33', 102]];
function drawArithmetic(bt) {
  if (bt < 96.8 || bt > 109.2) return;
  const out = 1 - seg(bt, 108.5, 109);
  withAlpha(out * popA(bt, 97, 0.5), () => {
    const x = 970, y = 296, w = 640, h = 262;
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 22; ctx.shadowOffsetY = 6;
    rrect(x, y, w, h, 20, PAPER); ctx.restore();
    lintPanel('worksheet', x, y, x + w, y + h);
    txt('论文里的题型', x + 30, y + 38, { size: 32, weight: 900, color: '#6b7690' });
    PROBLEMS.forEach(([q, ans, at], k) => {
      const qa = popA(bt, at, 0.3);
      if (qa <= 0) return;
      const ly = y + 100 + k * 66, qx = x + 40;
      txt(q, qx, ly, { size: 54, weight: 800, fam: 'mono', color: PAPER_INK, alpha: qa });
      const qw = measure(q, 54, 800, 'mono'), wa = seg(bt, at + 0.5, at + 0.8);
      if (wa > 0) {
        ctx.save(); ctx.beginPath(); ctx.rect(qx + qw - 4, ly - 40, 80 * wa + 4, 80); ctx.clip();
        txt(ans, qx + qw, ly, { size: 54, weight: 800, fam: 'mono', color: '#2f6fd1' }); ctx.restore();
      }
      const cs = popS(bt, at + 1, 0.5);
      if (cs > 0) withScale(x + w - 60, ly, cs, () => okMark(x + w - 60, ly, 20, seg(bt, at + 1, at + 1.6), INST));
    });
  });
  // the LCD with the three accuracies
  const la = popA(bt, 104, 0.4) * out;
  if (la > 0) withAlpha(la, () => {
    const x = 960, y = 588, w = 660, h = 206;
    rrect(x, y, w, h, 18, '#0f2a2a', 'rgba(140,240,200,0.45)', 2.5);
    lintPanel('lcd', x, y, x + w, y + h);
    txt('答对率', x + 26, y + 32, { size: 32, weight: 900, color: '#8fdcc0' });
    [['quiet', '安静', '69%', QUIET, 104.5], ['note', '纯音乐', '68%', INST, 105], ['lyric', '带词的歌', '67%', LYR, 105.5]].forEach(([ic, l, n, c, at], k) => {
      const cx = x + 120 + k * 210, a = popA(bt, at, 0.3);
      if (a <= 0) return;
      withAlpha(a, () => {
        ICONS[ic](cx, y + 72, ic === 'note' ? 36 : 42, c);
        txt(n, cx, y + 128, { size: 56, weight: 800, fam: 'mono', color: '#c9ffe9', align: 'center', glow: 10, glowColor: '#5fe0b0' });
        txt(l, cx, y + 178, { size: 32, weight: 900, color: c, align: 'center' });
      });
    });
  });
  const m = popS(bt, 106.5, 0.5) * out;
  if (m > 0) withScale(1722, 660, m, () => aboutMark(1722, 660, 34, INST));
  txt('差得不明显', 1722, 728, { size: 36, weight: 900, color: COL.greenHi, align: 'center', alpha: popA(bt, 106.5, 0.4) * out });
  sourceNote('Souza & Barbosa 2023 · 算术题：每题 8 秒，五选一 · 平均正确率', 760, 948, { alpha: popA(bt, 105, 0.5) * out });
}
// 51 s: what the lyrics did to each task (vs silence; reading: worse than with instrumental music)
const TASKS = [
  { x: 1010, icon: 'paper', label: '背词', res: 'bad', note: '变差', at: 110 },
  { x: 1250, icon: 'image', label: '记图', res: 'bad', note: '变差', at: 111 },
  { x: 1490, icon: 'lines', label: '读句子', res: 'bad', note: '比纯音乐差', at: 112 },
  { x: 1730, icon: 'calc', label: '算题', res: 'same', note: '不明显', at: 113 },
];
function drawTasks(bt) {
  if (bt < 109 || bt > 120.2) return;
  const out = 1 - seg(bt, 119.5, 120);
  withAlpha(out, () => {
    caption([cr('放'), hl('带词的歌', LYR), cr('的时候：')], 340, popA(bt, 109, 0.4), 42);
    TASKS.forEach((tk, k) => {
      const a = popA(bt, 109.5, 0.4);
      if (a <= 0) return;
      const done = bt >= tk.at, c = tk.res === 'bad' ? LYR : INST, y = 498;
      withAlpha(a, () => {
        ctx.save(); if (done) { ctx.shadowColor = c; ctx.shadowBlur = 20; }
        rrect(tk.x - 100, y - 104, 200, 208, 22, done ? rgba(c, 0.16) : 'rgba(12,26,58,0.9)', done ? c : 'rgba(200,212,236,0.4)', 3);
        ctx.restore();
        lintPanel('task' + k, tk.x - 100, y - 104, tk.x + 100, y + 104);
        const iconA = 1 - seg(bt, tk.at, tk.at + 0.2), m = popS(bt, tk.at, 0.5);
        if (iconA > 0) withAlpha(iconA, () => ICONS[tk.icon](tk.x, y - 30, 78, COL.cream));
        if (m > 0) withScale(tk.x, y - 30, m, () => (tk.res === 'bad' ? crossMark(tk.x, y - 30, 38, LYR) : aboutMark(tk.x, y - 30, 38, INST)));
        txt(tk.label, tk.x, y + 62, { size: 38, weight: 900, color: COL.cream, align: 'center' });
        txt(tk.note, tk.x, y + 146, { size: tk.note.length > 3 ? 32 : 36, weight: 900, color: tk.res === 'bad' ? COL.pinkHi : COL.greenHi, align: 'center', alpha: popA(bt, tk.at, 0.3) });
      });
    });
    caption([cr('受影响的是'), hl('背和读', LYR), cr('，算题差得不明显')], 734, popA(bt, 114, 0.4), 40);
  });
  sourceNote('Souza & Barbosa 2023 · 读句子：带词的歌比纯音乐差，和安静差得不明显', 760, 948, { alpha: popA(bt, 114.5, 0.5) * out });
}
function drawPhonesOff(bt) {
  if (bt < 119.8 || bt > 127) return;
  const a = popA(bt, 120, 0.4) * (1 - seg(bt, 126, 126.8));
  withAlpha(a, () => {
    rich([cr('要背、要读了：'), hl('摘下耳机', COL.yellow)], STAGE.x, 450, { size: 56, weight: 900, align: 'center' });
    const q = popA(bt, 121, 0.5);
    if (q > 0) withAlpha(q, () => { iconHeadphones(STAGE.x, 578 + 20 * EASE.out(q), 110, COL.grayHi); });
  });
}
function drawStep3(bt) {
  if (bt < 96 || bt > 128) return;
  drawArithmetic(bt);
  drawTasks(bt);
  drawPhonesOff(bt);
}

// ---------- 照着做: a three-channel mixer, set while he acts each row ----------
const CH = [
  { x: 917, label: '背书、读书', main: '关掉带词的歌', sub: '喜欢的歌也一样', at: 130, pos: 1.0, icon: 'lyric', color: LYR, off: true },
  { x: 1270, label: '想听的话', main: '换纯音乐', sub: '慢一点、小声一点', at: 134, pos: 0.72, icon: 'note', color: INST },
  { x: 1623, label: '只做计算题', main: '影响不明显', sub: '背和读的时候再关', at: 138, pos: 0.3, icon: 'calc', color: COL.yellow },
];
const MIX = { x0: 740, x1: 1800, y0: 286, y1: 692, ft: 392, fb: 560 };
function drawSummary(bt) {
  const inP = EASE.out(seg(bt, 126.5, 128));
  if (inP <= 0) return;
  withAlpha(inP, () => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 10;
    rrect(MIX.x0, MIX.y0, MIX.x1 - MIX.x0, MIX.y1 - MIX.y0, 26, '#111b38', 'rgba(200,212,236,0.35)', 2.5); ctx.restore();
    lintPanel('mixer', MIX.x0, MIX.y0, MIX.x1, MIX.y1);
    CH.forEach((c, k) => {
      const done = bt >= c.at;
      rrect(c.x - 160, MIX.y0 + 16, 320, 58, 14, 'rgba(255,255,255,0.06)');
      txt(c.label, c.x, MIX.y0 + 45, { size: 36, weight: 900, color: COL.cream, align: 'center' });
      // fader: slot + cap; it moves to its setting on the row's beat
      const fx = c.x - 74, pos = lerp(0.5, c.pos, EASE.inOut(seg(bt, c.at, c.at + 0.8)));
      rrect(fx - 7, MIX.ft, 14, MIX.fb - MIX.ft, 7, '#060b1c', 'rgba(200,212,236,0.25)', 1.5);
      for (let i = 0; i <= 4; i++) line(fx - 30, lerp(MIX.ft, MIX.fb, i / 4), fx - 18, lerp(MIX.ft, MIX.fb, i / 4), 'rgba(200,212,236,0.35)', 2);
      const ky = lerp(MIX.ft + 14, MIX.fb - 14, pos);
      ctx.save(); if (done) { ctx.shadowColor = c.color; ctx.shadowBlur = 16; }
      rrect(fx - 34, ky - 16, 68, 32, 8, done ? c.color : '#8d99b5'); ctx.restore();
      line(fx - 24, ky, fx + 24, ky, '#0b1736', 3);
      // channel icon + LED
      const ix = c.x + 62, iy = MIX.ft + 52, m = popS(bt, c.at, 0.6);
      circle(ix, iy, 46, '#0d1838', done ? c.color : 'rgba(200,212,236,0.3)', 3);
      withAlpha(done ? 1 : 0.35, () => {
        ICONS[c.icon](ix, iy, c.icon === 'note' ? 46 : 54, done ? c.color : COL.gray);
        if (c.off && done) withAlpha(m, () => line(ix - 34, iy + 34, ix + 34, iy - 34, COL.cream, 6));
      });
      const ledOn = done && !c.off;
      ctx.save(); if (ledOn) { ctx.shadowColor = INST; ctx.shadowBlur = 16; }
      circle(ix, iy + 92, 10, ledOn ? INST : done ? LYR : '#2a3352'); ctx.restore();
      // the setting, written under the channel
      const ta = popA(bt, c.at, 0.35);
      if (ta > 0) {
        txt(c.main, c.x, MIX.fb + 50, { size: 40, weight: 900, color: k === 0 ? COL.pinkHi : k === 1 ? COL.greenHi : COL.yellowHi, align: 'center', alpha: ta });
        txt(c.sub, c.x, MIX.fb + 98, { size: 32, weight: 700, color: 'rgba(200,212,236,0.9)', align: 'center', alpha: ta });
      }
    });
    // reminder, footnote
    const wa = popA(bt, 142, 0.35);
    if (wa > 0) withAlpha(wa, () => withScale(1270, 752, 0.9 + 0.1 * popS(bt, 142, 0.6), () => {
      rrect(MIX.x0, 712, MIX.x1 - MIX.x0, 80, 16, 'rgba(255,111,158,0.12)', 'rgba(255,111,158,0.75)', 2.5);
      lintPanel('reminder', MIX.x0, 712, MIX.x1, 792);
      rich([hl('纯音乐', COL.greenHi), cr('只是不太拖后腿，'), hl('不会帮你多记', LYR)], 1270, 752, { size: 42, weight: 900, align: 'center' });
    }));
    const fa = popA(bt, 144, 0.6);
    if (fa > 0) {
      txt('仅供参考 · 影响都不大：20 个词平均少记约 1 个 · 因人而异', MIX.x0, 830, { size: 30, weight: 700, color: COL.gray, alpha: fa });
      txt('Souza & Barbosa 2023 · Vasilev 2018 · Perham 2011 / 2014 · Thompson 2012 · Sun 2024', MIX.x0, 870, { size: 22, weight: 500, fam: 'mono', color: COL.grayDim, alpha: fa });
    }
    const fl = win(bt, 146, 147.4, 0.04, 1.2);
    if (fl > 0) rrect(MIX.x0 - 24, MIX.y0 - 22, MIX.x1 - MIX.x0 + 48, 800 - MIX.y0 + 44, 26, `rgba(255,255,255,${0.08 * fl})`, `rgba(255,250,235,${0.9 * fl})`, 5);
  });
}

// ---------- wiring ----------
function decorateBoy(bp, bt, t) {
  // the book's pages turn every 2 beats while he reads
  if (bp.read > 0.9) { const cyc = ((bt - 0.5) % 2 + 2) % 2; bp.flip = cyc < 0.9 ? cyc / 0.9 : 0; }
  // head shake "no" for 「不会帮你多记」
  if (bt > 142 && bt < 144.5) bp.headTilt = Math.sin((bt - 142) * Math.PI * 2.2) * 0.12 * (1 - seg(bt, 143.6, 144.5));
}
function drawSections(bt, t, boy, bp) {
  if (bt < 31) return;
  drawHeaders(bt);
  drawStep1(bt, boy);
  drawStep2(bt);
  drawStep3(bt);
  if (bt >= 126.2) drawSummary(bt);
}
