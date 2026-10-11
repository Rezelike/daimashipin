"""Download (once) and load real instrument samples.

Piano  : Salamander Grand Piano V2 (Yamaha C5), Alexander Holm, CC BY 3.0
         via https://github.com/Tonejs/audio/tree/master/salamander
Strings: FluidR3 GM soundfont (Frank Wen), CC BY 3.0
         via https://github.com/gleitz/midi-js-soundfonts

Files are cached in assets/ (git-ignored) and decoded to float32 with ffmpeg.
"""
import os
import subprocess
import urllib.request

import imageio_ffmpeg
import numpy as np

SR = 44100
ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, 'assets')
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

PIANO_URL = 'https://raw.githubusercontent.com/Tonejs/audio/master/salamander/{}.mp3'
GM_URL = 'https://raw.githubusercontent.com/gleitz/midi-js-soundfonts/gh-pages/FluidR3_GM/{}-mp3/{}.mp3'

SHARP = ['C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs', 'A', 'As', 'B']
FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
PIANO_NOTES = [n for n in range(21, 109) if n % 12 in (9, 0, 3, 6)]   # A, C, D#, F# (minor thirds)


def note_name(m, table):
    return f'{table[m % 12]}{m // 12 - 1}'


def _fetch(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + '.part'
        urllib.request.urlretrieve(url, tmp)
        os.replace(tmp, path)
    return path


def _decode(path):
    out = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    x = np.frombuffer(out, dtype=np.float32).astype(np.float64)
    # trim leading silence so notes start on time
    k = int(np.argmax(np.abs(x) > 0.003 * np.max(np.abs(x))))
    return x[max(0, k - 40):]


class Instrument:
    def __init__(self, notes):
        self.notes = notes            # midi -> np.array

    def nearest(self, m):
        k = min(self.notes, key=lambda n: (abs(n - m), n))
        return k, self.notes[k]


_cache = {}


def piano():
    if 'piano' not in _cache:
        notes = {}
        for m in PIANO_NOTES:
            name = note_name(m, SHARP).replace('s', 's')
            p = _fetch(PIANO_URL.format(name), os.path.join(ASSETS, 'piano', f'{name}.mp3'))
            notes[m] = _decode(p)
        _cache['piano'] = Instrument(notes)
    return _cache['piano']


def gm(instrument, lo, hi):
    key = (instrument, lo, hi)
    if key not in _cache:
        notes = {}
        for m in range(lo, hi + 1):
            name = note_name(m, FLAT)
            p = _fetch(GM_URL.format(instrument, name), os.path.join(ASSETS, instrument, f'{name}.mp3'))
            notes[m] = _decode(p)
        _cache[key] = Instrument(notes)
    return _cache[key]


def strings():
    return gm('string_ensemble_1', 36, 84)


def cello():
    return gm('cello', 36, 67)


if __name__ == '__main__':
    for name, inst in (('piano', piano()), ('strings', strings()), ('cello', cello())):
        lens = [len(v) / SR for v in inst.notes.values()]
        print(name, len(inst.notes), 'samples, length', round(min(lens), 2), '-', round(max(lens), 2), 's')
