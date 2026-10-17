"""Minimal 'newc' cpio extractor (the sandbox has rpm2cpio but no cpio binary).

    rpm2cpio pkg.rpm | python3 cpio_extract.py OUT_DIR
"""
import os
import stat
import sys

data = sys.stdin.buffer.read()
out = sys.argv[1]
i = 0
while i < len(data):
    h = data[i:i + 110]
    assert h[:6] in (b"070701", b"070702"), f"not a newc cpio archive: {h[:6]!r}"
    f = [int(h[6 + 8 * k:14 + 8 * k], 16) for k in range(13)]
    mode, fsize, nsize = f[1], f[6], f[11]
    name = data[i + 110:i + 110 + nsize - 1].decode()
    i = (i + 110 + nsize + 3) & ~3
    body = data[i:i + fsize]
    i = (i + fsize + 3) & ~3
    if name == "TRAILER!!!":
        break
    p = os.path.join(out, name.lstrip("./"))
    if stat.S_ISDIR(mode):
        os.makedirs(p, exist_ok=True)
    elif stat.S_ISLNK(mode):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if not os.path.lexists(p):
            os.symlink(body.decode(), p)
    elif stat.S_ISREG(mode):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(body)
