// scene.js — timeline. All times in beats (bt). 128 BPM -> 1 beat = 0.46875 s; 160 beats = 75 s.
// Same beat grid as sleep_or_cram / bedtime_words (lessons 13): reveal 1 at beat 4.5 (2.11 s), reveal 2 four beats later
// at 8.5 (3.98 s), the check at 10.5 (4.92 s), the answer section from beat 17 (8.0 s), steps at 32 / 64 / 96, summary 128.
// Data (Souza & Barbosa 2023, verbal recall, 20 words, same 113 students in every condition; music only while studying):
// silence 8.39, lo-fi instrumental 7.94, popular songs with lyrics 7.37 words (d lyrics vs silence = -0.32).
const TOTAL_BEATS = 160;
const RECALL = { quiet: 8.4, lyrics: 7.4, inst: 7.9 };

// ---------- the boy (on screen in every frame) ----------
const BOY = {
  x: KB([[0, 1360], [16, 1360], [17.5, 960], [30.5, 960], [32.5, 470], [126.5, 470], [128.5, 400]]),
  y: KB([[0, 860], [16, 860], [17.5, 872], [30.5, 872], [32.5, 842], [126.5, 842], [128.5, 852]]),
  s: KB([[0, 1], [16, 1], [17.5, 1.12], [30.5, 1.12], [32.5, 0.9], [126.5, 0.9], [128.5, 0.92]]),
  // headphones on the head / around the neck: off for 关掉带词的歌 (beat 60), on again for 纯音乐 (65), off for 摘下耳机 (120),
  // on for row 2 of the summary (134)
  phones: KB([[0, 1], [60, 1], [60.8, 0, 'out'], [65, 0], [65.8, 1, 'out'], [120, 1], [120.8, 0, 'out'], [134, 0], [134.8, 1, 'out']]),
  neck: KB([[0, 0], [60.5, 0], [61.2, 1, 'out'], [65, 1], [65.5, 0, 'in'], [120.5, 0], [121.2, 1, 'out'], [134, 1], [134.5, 0, 'in']]),
  read: KB([[0, 1], [4.5, 1], [5.0, 0], [19.5, 0], [20.3, 1, 'out'], [30, 1], [30.8, 0], [33, 0], [33.8, 1, 'out'], [43, 1], [43.5, 0],
    [49, 0], [49.6, 1, 'out'], [59, 1], [59.8, 0], [66, 0], [66.8, 1, 'out'], [76, 1], [76.8, 0], [89.5, 0], [90.3, 1, 'out'], [95.5, 1], [96.2, 0],
    [120, 0], [120.8, 1, 'out'], [126, 1], [126.8, 0], [129.5, 0], [130.2, 1, 'out'], [137.5, 1], [138, 0]]),
  write: KB([[4.5, 0], [5.0, 1, 'out'], [6.0, 1], [6.5, 0], [8.5, 0], [9.0, 1, 'out'], [10.0, 1], [10.5, 0, 'out'], [96.5, 0], [97.3, 1, 'out'], [103.5, 1], [104, 0],
    [137.5, 0], [138.2, 1, 'out'], [141.5, 1], [142, 0]]),
  // the right hand on the phone: switch to 纯音乐 (8.5), turn it down (18), the favourite song (44), tempo / volume (80–86), 88
  phone: KB([[8.0, 0], [8.5, 1, 'out'], [8.8, 1], [9.0, 0], [17.5, 0], [18.0, 1, 'out'], [19, 1], [19.5, 0], [43.5, 0], [44, 1, 'out'],
    [44.6, 1], [45, 0], [79.5, 0], [80, 1, 'out'], [82.5, 1], [83, 0], [85.5, 0], [86, 1, 'out'], [86.5, 1], [87, 0],
    [87.5, 0], [88, 1, 'out'], [89, 1], [89.5, 0]]),
  point: KB([[149.5, 0], [150.3, 1, 'out'], [152, 1], [152.6, 0]]),
  thumb: KB([[153, 0], [153.8, 1, 'back']]),
  happy: KB([[10.5, 0], [11, 1], [16, 1], [17, 0.4], [152, 0.4], [152.6, 1]]),
  worry: KB([[5.5, 0], [6.3, 0.8], [8.5, 0.8], [9.0, 0], [39.5, 0], [39.9, 0.7], [42, 0.7], [42.6, 0], [142, 0], [142.4, 0.6], [144.2, 0.6], [144.6, 0]]),
};
// what plays in his headphones (cup colour, desk phone, what comes out of the cups)
function musicMode(bt) {
  if (bt < 4.5) return 'lyrics';
  if (bt < 8.5) return 'off';       // dictation: in the experiment the music played only while learning
  if (bt < 32) return 'inst';
  if (bt >= 44 && bt < 56) return 'fave';
  if (bt < 60) return 'lyrics';
  if (bt < 65) return 'off';
  if (bt < 96) return 'inst';
  if (bt < 120) return 'lyrics';    // ③: arithmetic with the lyrics on
  if (bt < 134) return 'off';
  return 'inst';
}
// volume (he turns it down at 18 and at 88)
const VOL = KB([[0, 1], [18.5, 1], [19, 0.55], [32, 0.55], [32.5, 1], [65, 1], [88.5, 1], [89.5, 0.4], [96, 0.4], [96.5, 1], [134, 1], [134.5, 0.55]]);
const BLINKS = [1.2, 3.6, 11.6, 19.6, 25.6, 29.3, 46.1, 52.9, 66.4, 71.6, 83.3, 92.6, 101.4, 109.6, 113.3, 124.2, 131.2, 144.6, 156.2];
function blinkAt(bt, list = BLINKS) {
  let v = 0;
  for (const b of list) { const d = Math.abs(bt - b); if (d < 0.35) v = Math.max(v, 1 - d / 0.35); }
  return v;
}
function talkAt(bt) {
  if (bt < 4.5) return Math.max(0, Math.sin((bt + 0.3) * Math.PI * 2.2)) * 0.4;           // memorising aloud
  if (bt > 34 && bt < 39.4) return Math.max(0, Math.sin(bt * Math.PI * 2)) * 0.45;        // 床前明月光…
  return 0;
}

// ---------- floating music from his ear cups ----------
// one bubble (lyrics) or note (instrumental) every beat on the half beat, alternating cups. In the opening the lyric
// bubbles fly into his head and one knocks a word away (beat 2.5); at reveal 1 (4.5) the music stops and they pop.
const SPAWNS = Array.from({ length: 166 }, (_, i) => i - 3 + 0.5);
const KNOCK = { at: 2.5, spawn: 1.5 };   // this bubble flies at his third word and knocks it away
const OPEN_LIFE = 1.8;
// opening path: from an ear cup up and round into his head (the knocking bubble ends on the word instead)
function openingBubble(i, ts, bt, boy, s) {
  const knock = ts === KNOCK.spawn, side = knock ? 1 : -1;
  const L = knock ? KNOCK.at - KNOCK.spawn : OPEN_LIFE;
  const p = clamp((bt - ts) / L), e = EASE.inOut(p), cup = boy.cups[side > 0 ? 1 : 0];
  const [ex, ey] = knock ? wordPos('boy', 2, KNOCK.at) : [boy.headX + side * 24 * s, boy.headY - 30 * s];
  const cx = cup[0] + side * 80 * s, cy = cup[1] - 110 * s;
  return { p, knock, L, x: (1 - e) * (1 - e) * cup[0] + 2 * (1 - e) * e * cx + e * e * ex, y: (1 - e) * (1 - e) * cup[1] + 2 * (1 - e) * e * cy + e * e * ey };
}
function drawParticles(bt, boy, bp) {
  const vol = VOL(bt), s = bp.s;
  for (let i = 0; i < SPAWNS.length; i++) {
    const ts = SPAWNS[i];
    if (ts > bt) break;
    const mode = musicMode(ts);
    if (BOY.phones(ts) < 0.9 || mode === 'off') continue;
    if (ts < 4.5) {
      // reveal 1 (4.5): the music stops and the bubbles still in the air pop
      const q0 = openingBubble(i, ts, bt, boy, s);
      const popT = q0.knock ? KNOCK.at : ts + q0.L > 4.5 ? 4.5 : null;
      if (popT !== null && bt >= popT) {
        if (bt < popT + 0.45) { const q = openingBubble(i, ts, popT, boy, s); popRing(q.x, q.y, (bt - popT) / 0.45, LYR); }
        continue;
      }
      if (q0.p >= 1) continue;
      const sc = (q0.knock ? 0.85 : 0.8 * (1 - 0.5 * seg(q0.p, 0.75, 1))) * s;
      drawLyricBubble(q0.x, q0.y, { scale: sc * popS(bt, ts, 0.5), alpha: 1 - 0.6 * seg(q0.p, 0.85, 1), text: i % 3 ? '啦啦' : '啦啦啦' });
      continue;
    }
    const L = mode === 'inst' ? 2.4 : 2.0, p = (bt - ts) / L;
    if (p >= 1) continue;
    const side = i % 2 ? 1 : -1, cup = boy.cups[side > 0 ? 1 : 0];
    // in the opening the notes drift sideways (the sheets and their numbers are above his head)
    const early = ts < 17;
    const dx = side * (26 + (early ? 110 : 80) * p) * s, dy = -(early ? 20 + 70 * p : 30 + 170 * p) * s, wob = Math.sin(p * 5 + i) * 10 * s;
    const a = Math.pow(Math.sin(Math.PI * p), 0.7) * (0.45 + 0.55 * vol);
    if (mode === 'inst') drawFloatNote(cup[0] + dx + wob, cup[1] + dy, (30 + 10 * (i % 2)) * s * (0.7 + 0.3 * vol), { alpha: a, rot: Math.sin(p * 4 + i) * 0.25, beamed: i % 3 === 0 });
    else drawLyricBubble(cup[0] + dx + wob, cup[1] + dy, { scale: 0.62 * s, alpha: a * 0.9, heart: mode === 'fave', text: '' });
  }
}

// ---------- opening (0–17): words go from the book into the head; 20-line dictation sheets ----------
const OPEN = {
  outA: KB([[0, 1], [15.5, 1], [16.6, 0, 'out']]),
  girlX: KB([[0, 560], [15.5, 560], [17, 300, 'in']]),
  idx: KB([[0, 0], [4.5, 0], [5.0, 1, 'out'], [8.5, 1], [9.0, 2, 'out']]),
};
const WORD_FLIGHT = 1.0;
// 示意 words (the experiment used Portuguese word lists); hers land on the half beats, his on the beats
const WORDS = {
  girl: [['苹果', -0.5], ['河流', 0.5], ['勇气', 1.5], ['钥匙', 2.5], ['雨伞', 3.5]],
  boy: [['自由', 0], ['海豚', 1], ['蜡烛', 2], ['规则', 3]],
};
function wordPos(who, t0, bt) {
  const kx = who === 'girl' ? OPEN.girlX(bt) : 1360, side = who === 'girl' ? -1 : 1;
  const e = EASE.inOut(seg(bt, t0, t0 + WORD_FLIGHT));
  const x0 = kx + side * 40, y0 = 806, cx = kx + side * 200, cy = 700, x1 = kx + side * 34, y1 = 650;
  return [(1 - e) * (1 - e) * x0 + 2 * (1 - e) * e * cx + e * e * x1, (1 - e) * (1 - e) * y0 + 2 * (1 - e) * e * cy + e * e * y1];
}
function drawWords(bt) {
  for (const who of ['girl', 'boy']) {
    for (const [w, t0] of WORDS[who]) {
      if (bt < t0 || bt > t0 + WORD_FLIGHT + 1.2) continue;
      const knocked = who === 'boy' && t0 === 2 && bt >= KNOCK.at;
      if (knocked) {
        const q = seg(bt, KNOCK.at, KNOCK.at + 1.1), [kx, ky] = wordPos('boy', t0, KNOCK.at);
        drawWordChip(kx + 150 * EASE.out(q), ky - 30 * q + 220 * q * q, w, { alpha: 1 - EASE.in(q), rot: 1.6 * q, scale: 1 });
        continue;
      }
      const p = seg(bt, t0, t0 + WORD_FLIGHT);
      if (p >= 1) continue;
      const [x, y] = wordPos(who, t0, bt);
      drawWordChip(x, y, w, { scale: popS(bt, t0, 0.4) * (1 - 0.6 * seg(p, 0.75, 1)), alpha: 1 - seg(p, 0.85, 1) });
    }
  }
  // a small ring on the head where a word goes in
  for (const who of ['girl', 'boy']) for (const [, t0] of WORDS[who]) {
    if (who === 'boy' && t0 === 2) continue;
    const t1 = t0 + WORD_FLIGHT;
    if (bt > t1 && bt < t1 + 0.45) { const [x, y] = wordPos(who, t0, t1); popRing(x, y, seg(bt, t1, t1 + 0.45), who === 'girl' ? QUIET : COL.yellow); }
  }
}
// the dictation: hers fills to 8.4, his to 7.4 (lyrics); at reveal 2 his sheet turns over and fills to 7.9 (instrumental)
const SHEETS = { girl: [560, 528], boy: [1360, 528] };
const fillGirl = (bt) => clamp(RECALL.quiet * (bt - 5.0) / (5.5 - 5.0), 0, RECALL.quiet);      // done on beat 5.5
const fillBoyLyr = (bt) => clamp(RECALL.lyrics * (bt - 5.0) / (6.0 - 5.0), 0, RECALL.lyrics);  // done on beat 6
const fillBoyInst = (bt) => clamp(RECALL.inst * (bt - 9.0) / (10.0 - 9.0), 0, RECALL.inst);     // done on beat 10
const countText = (n, full) => (n >= full - 1e-6 ? full.toFixed(1) : String(Math.floor(n)));
function drawSheets(bt) {
  if (bt < 4.5) return;
  const A = OPEN.outA(bt), drop = EASE.out(seg(bt, 4.5, 5.1));
  withAlpha(A * drop, () => {
    const [gx, gy] = SHEETS.girl, [bx, by] = SHEETS.boy, dy = -40 * (1 - drop);
    drawSheet(gx, gy + dy, fillGirl(bt), { accent: QUIET, name: 'sheet:girl' });
    const f = flipFace(bt, 8.5, 0.4, 'lyr', 'inst');
    if (f.face === 'lyr') drawSheet(bx, by + dy, fillBoyLyr(bt), { accent: LYR, sx: f.sx, name: 'sheet:boy' });
    else drawSheet(bx, by + dy, fillBoyInst(bt), { accent: INST, sx: f.sx, glow: win(bt, 10.5, 11.6, 0.1, 0.8), name: 'sheet:boy' });
    // counts on the inner side of each sheet
    const na = popA(bt, 5.0, 0.3), gNum = gx + SHEET.w / 2 + 24, bNum = bx - SHEET.w / 2 - 24;
    if (na > 0) {
      rich([{ s: countText(fillGirl(bt), RECALL.quiet), size: 62, fam: 'mono', weight: 800, color: COL.cyanHi, glow: 10 }, { s: ' 个', size: 40, color: COL.cream }],
        gNum, 520, { size: 62, weight: 800, alpha: na });
      const inst = bt >= 8.75, v = inst ? fillBoyInst(bt) : fillBoyLyr(bt), full = inst ? RECALL.inst : RECALL.lyrics;
      const c = inst ? COL.greenHi : COL.pinkHi;
      rich([{ s: countText(v, full), size: 62, fam: 'mono', weight: 800, color: c, glow: 10 }, { s: ' 个', size: 40, color: COL.cream }],
        bNum, 520, { size: 62, weight: 800, align: 'right', alpha: na * (inst ? popA(bt, 9.5, 0.25) : 1 - seg(bt, 8.5, 8.75)) });
    }
    // reveal 1: 少记 1 个 under his number (moves into the gray tag at reveal 2)
    const la = popA(bt, 6.5, 0.4) * (1 - seg(bt, 8.5, 8.8));
    if (la > 0) txt('少记 1 个', bNum - (1 - la) * 20, 586, { size: 38, weight: 900, color: LYR, align: 'right', alpha: la, glow: 12 });
    // reveal 2: his lyrics result stays as a gray tag on the outside; the check lands between the two sheets
    // (5.39 s) the tag gets its third line: 带词的歌 / 7.4 个 / 少记 1 个
    const ta = popA(bt, 8.5, 0.5);
    if (ta > 0) withAlpha(ta, () => {
      const tx = 1650, ty = 528, w = 236, h = 196, sl = (1 - EASE.out(seg(bt, 8.5, 9.2))) * -150;
      rrect(tx - w / 2 + sl, ty - h / 2, w, h, 18, 'rgba(12,24,54,0.9)', rgba(LYR, 0.25 + 0.5 * popA(bt, 11.5, 0.4)), 2);
      lintPanel('lyricsTag', tx - w / 2 + sl, ty - h / 2, tx + w / 2 + sl, ty + h / 2);
      txt('带词的歌', tx + sl, ty - 56, { size: 34, weight: 900, color: COL.grayHi, align: 'center' });
      rich([{ s: '7.4', size: 56, fam: 'mono', weight: 800, color: COL.grayHi }, { s: ' 个', size: 36, color: COL.grayHi }], tx + sl, ty + 4, { size: 56, weight: 800, align: 'center' });
      const ra = popA(bt, 11.5, 0.4);
      if (ra > 0) txt('少记 1 个', tx + sl, ty + 62, { size: 36, weight: 900, color: LYR, align: 'center', alpha: ra, glow: 12 });
    });
    const cs = popS(bt, 10.5, 0.6);
    if (cs > 0) withScale(960, 548, cs, () => okMark(960, 548, 30, seg(bt, 10.5, 11.2), INST));
    const ca = popA(bt, 10.5, 0.4);
    if (ca > 0) txt('差得不明显', 960, 616, { size: 42, weight: 900, color: COL.greenHi, align: 'center', alpha: ca, glow: 14 });
  });
  if (bt >= 10.5 && bt < 12.5) dingBurst(960, 548, seg(bt, 10.5, 12.5), { s: '', size: 40, color: INST });
}

const PLAYER_ITEMS = [
  { icon: 'play', spans: [{ s: '背 ' }, { s: '20 个词', color: COL.yellow }] },
  { icon: 'pencil', spans: [{ s: '默写：' }, { s: '记住几个', color: COL.yellow }] },
  { icon: 'note', spans: [{ s: '换' }, { s: '纯音乐', color: COL.greenHi }, { s: '，再背一组' }] },
];
function drawOpening(bt, t) {
  const A = OPEN.outA(bt);
  if (A <= 0 && bt > 17) return;
  const idx = OPEN.idx(bt);
  const prog = bt < 4.5 ? seg(bt, 0, 4.5) : bt < 8.5 ? seg(bt, 5.0, 6.0) : seg(bt, 9.0, 10.0);
  const flash = win(bt, 4.5, 5.4, 0.08, 0.8) + win(bt, 8.5, 9.4, 0.08, 0.8);   // starts on the reveal's beat
  drawPlayerBar(960, 458, PLAYER_ITEMS, idx, prog, { alpha: A, flash: clamp(flash) });
  drawSheets(bt);
  sourceNote('Souza & Barbosa 2023 · 《Journal of Cognition》 · 葡萄牙 113 名大学生，同一批人在安静、纯音乐、带词的歌下各背 20 个词 · 平均数', 110, 988, { alpha: A * popA(bt, 13, 0.8) });
}

function drawTitleBlock(bt, t) {
  const outA = 1 - EASE.out(seg(bt, 30.5, 31.4));
  const dyOut = -40 * EASE.in(seg(bt, 30.5, 31.4));
  if (outA <= 0) return;
  withAlpha(outA, () => {
    // both lines roll from the question to the answer at beat 17
    const roll = (y, a, b, p0) => {
      const e = EASE.inOut(seg(bt, p0, p0 + 0.8));
      ctx.save(); ctx.beginPath(); ctx.rect(0, y - 92, W, 184); ctx.clip();
      if (e < 1) rich(a, 960, y - e * 170, { size: 136, weight: 900, align: 'center', alpha: 1 - e });
      if (e > 0) rich(b, 960, y + (1 - e) * 170, { size: 136, weight: 900, align: 'center', alpha: e });
      ctx.restore();
    };
    roll(140 + dyOut, [{ s: '边' }, { s: '听歌', color: LYR, glow: 26 }],
      [{ s: '背书、读书', color: COL.yellow, glow: 22 }, { s: '时' }], 16.5);
    roll(282 + dyOut, [{ s: '边' }, { s: '背书', color: COL.yellow, glow: 26 }, { s: '？' }],
      [{ s: '别听' }, { s: '带词的歌', color: LYR, glow: 26 }], 16.5);
    const en1 = 'Studying with music on?', en2 = 'Memorizing or reading? Skip the lyrics.';
    const useSecond = bt >= 17, s = useSecond ? en2 : en1;
    const fw = measure(s, 34, 500, 'mono');
    const p1 = useSecond ? seg(bt, 17, 19.8) : lerp(7 / en1.length, 1, seg(bt, 0, 2.6));
    typeText(s, p1, 960 - fw / 2, 376 + dyOut, { size: 34, weight: 500, fam: 'mono', color: COL.cyan, keepCursor: true }, bt);
  });
}

function drawGirl(bt, t) {
  const A = OPEN.outA(bt);
  if (A <= 0) return;
  const cyc = ((bt - 0.5) % 2 + 2) % 2;
  const flip = bt < 4.5 && bt > 0.5 ? clamp(cyc / 0.9) : 0;
  const x = OPEN.girlX(bt);
  const read = KB([[0, 1], [4.6, 1], [5.1, 0]])(bt);
  const write = KB([[4.6, 0], [5.0, 1], [5.5, 1], [6.0, 0]])(bt);
  drawKid({
    type: 'girl', x, y: 860, s: 1, t, alpha: A,
    read, write, pencil: true, flip: flip >= 1 ? 0 : flip,
    talk: bt < 4.5 ? Math.max(0, Math.sin(bt * Math.PI * 2.2)) * 0.4 : 0,
    happy: win(bt, 6.2, 15, 0.5, 0.5) * 0.5, blink: blinkAt(bt, [1.6, 5.2, 7.4, 12.4, 14.6]), bookColor: '#3d9bd6',
    deskProps: () => { drawMugLocal(-160); if (bt > 4.8 && bt < 7.2) drawNotebookLocal(20, -3); },
  });
  namePlate(x, 922, '安静背', QUIET, { alpha: A });
}

// ---------- answer section 「关掉歌词」 (17–32): the three steps as a playlist, the evidence card ----------
const STEPS = [
  { n: 1, s: '别听带词的歌', color: LYR, at: 19.0 },
  { n: 2, s: '换纯音乐', color: INST, at: 21.5 },
  { n: 3, s: '算题影响不明显', color: COL.yellow, at: 25.0 },
];
const LIST = { x: 1250, y0: 470, dy: 116 };
function drawS1(bt, t, boy, bp) {
  if (bt < 18 || bt > 33) return;
  STEPS.forEach((st, i) => {
    if (bt < st.at) return;
    const fly = EASE.out(seg(bt, st.at, st.at + 0.8));
    const ox = i === 1 ? boy.cups[1][0] : boy.headX, oy = i === 1 ? boy.cups[1][1] : boy.headY;
    let x = lerp(ox - TRACK.w / 2, LIST.x, fly), y = lerp(oy, LIST.y0 + i * LIST.dy, fly);
    let sc = popS(bt, st.at, 0.8), a = popA(bt, st.at, 0.25);
    const hi = i === 0 ? win(bt, 29, 31, 0.4, 0.4) : 0;
    if (bt > 30.5) {
      const q = EASE.inOut(seg(bt, 30.5, 32.2));
      if (i === 0) { x = lerp(LIST.x, 150, q); y = lerp(LIST.y0, 156, q); a = 1 - seg(bt, 31.6, 32.3); }
      else { sc = 1 - q * 0.3; a = 1 - seg(bt, 30.5, 31.3); }
    }
    drawTrackRow(x, y, st.n, st.s, st.color, { alpha: a, scale: sc, hi, prog: i === 0 ? seg(bt, 19.6, 30) * 0.3 : 0 });
  });
  // evidence (12.4 s): Vasilev et al. 2018, 65 studies on reading — noise, instrumental music, speech, lyrics all make
  // reading a little worse; intelligible speech and lyrical music the most
  const ea = popA(bt, 26.5, 0.5) * (1 - seg(bt, 30.5, 31.2));
  if (ea > 0) withAlpha(ea, () => {
    const x = 100, y = 600, w = 600, h = 318;
    rrect(x, y, w, h, 20, 'rgba(12,26,58,0.9)', 'rgba(243,238,227,0.32)', 2);
    lintPanel('evidence', x, y, x + w, y + h);
    txt('不止一个实验：65 项研究', x + 28, y + 44, { size: 36, weight: 900, color: COL.cream });
    const items = [['noise', '噪音', COL.grayHi], ['note', '纯音乐', INST], ['speech', '说话声', LYR], ['lyric', '带词的歌', LYR]];
    items.forEach(([ic, label, c], k) => {
      const cx = x + 84 + k * 146, cy = y + 128, at = 26.5 + k * 0.5;
      const sc = popS(bt, at, 0.5);
      if (sc <= 0) return;
      const worst = k >= 2, glow = worst ? seg(bt, 28.5, 29) : 0;
      withScale(cx, cy, sc, () => {
        ctx.save(); if (glow > 0) { ctx.shadowColor = LYR; ctx.shadowBlur = 22 * glow; }
        circle(cx, cy, 44, '#0d1838', worst && glow > 0 ? LYR : 'rgba(200,212,236,0.45)', 3); ctx.restore();
        ICONS[ic](cx, cy, ic === 'note' ? 46 : 52, c);
      });
      txt(label, cx, cy + 76, { size: 34, weight: 900, color: c, align: 'center', alpha: popA(bt, at, 0.3) });
    });
    const wa = popA(bt, 28.5, 0.4);
    if (wa > 0) {
      rrect(x + 336, y + 232, 222, 50, 25, rgba(LYR, 0.18 * wa), rgba(LYR, 0.8 * wa), 2);
      txt('这两种最伤', x + 447, y + 257, { size: 34, weight: 900, color: LYR, align: 'center', alpha: wa });
    }
    txt('都只让阅读差一点', x + 28, y + 257, { size: 34, weight: 700, color: COL.grayHi, alpha: popA(bt, 28, 0.4) });
    sourceNote('Vasilev 等 2018 · 元分析 · 阅读理解', x + 28, y + 298, { alpha: popA(bt, 28.5, 0.5) });
  });
}

// ---------- main ----------
function boyParams(bt, t) {
  const mode = musicMode(bt), ph = BOY.phones(bt);
  const groove = ph > 0.5 && mode !== 'off' ? (mode === 'inst' ? 0.5 : 1) : 0;
  return {
    type: 'boy', x: BOY.x(bt), y: BOY.y(bt), s: BOY.s(bt), t,
    read: BOY.read(bt), write: BOY.write(bt), phone: BOY.phone(bt), pencil: true,
    point: BOY.point(bt), thumb: BOY.thumb(bt), worry: BOY.worry(bt),
    happy: BOY.happy(bt), blink: blinkAt(bt), talk: talkAt(bt),
    phones: ph, neck: BOY.neck(bt), phonesColor: MODE_COL[mode === 'fave' ? 'lyrics' : mode],
    // swaying to the music: a slow tilt every 2 beats and a small dip on each beat (the head only, never the frame)
    headTilt: groove * 0.04 * Math.sin(Math.PI * bt), bob: groove * 2.4 * Math.abs(Math.sin(Math.PI * bt)),
    bookColor: '#7b5fd6', flip: 0,
    deskProps: () => {
      drawDeskPhoneLocal(166, mode, { glow: Math.max(win(bt, 8.4, 9.4, 0.1, 0.6), win(bt, 18, 19.4, 0.1, 0.6)), vol: VOL(bt) });
      if (BOY.write(bt) > 0.02 || (bt > 4.8 && bt < 10.6)) drawNotebookLocal(20, -3);
    },
  };
}

function renderFrame(t) {
  const bt = t / BEAT;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  drawBackground(t);
  const info = { t, bt, kid: false };

  if (bt < 18) drawOpening(bt, t);
  drawTitleBlock(bt, t);
  if (bt < 17) drawGirl(bt, t);

  if (typeof drawPanelLayer === 'function') drawPanelLayer(bt, t);

  const bp = boyParams(bt, t);
  if (typeof decorateBoy === 'function') decorateBoy(bp, bt, t);
  const boy = drawKid(bp);
  info.kid = (bp.alpha ?? 1) > 0.5;
  if (bt < 17) {
    const f = flipFace(bt, 8.5, 0.4, 'a', 'b');
    withAlpha(OPEN.outA(bt), () => withScale(bp.x, 922, 1, () => {
      ctx.save(); ctx.translate(bp.x, 922); ctx.scale(f.sx, 1); ctx.translate(-bp.x, -922);
      namePlate(bp.x, 922, f.face === 'a' ? '听歌背' : '听纯音乐', f.face === 'a' ? LYR : INST);
      ctx.restore();
    }));
  }
  drawParticles(bt, boy, bp);
  if (bt < 9) drawWords(bt);

  drawS1(bt, t, boy, bp);
  if (typeof drawSections === 'function') drawSections(bt, t, boy, bp);

  drawChapterBar(bt);
  window.__frameInfo = info;
}
