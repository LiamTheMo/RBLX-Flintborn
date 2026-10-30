"""Edge clusters along a row/column: pixels whose colour differs from the line's
background (its median, or --bg hex) by more than TOL (sum of |dRGB|), grouped.
usage: edges.py IMAGE row|col INDEX START END [TOL] [BGHEX]"""
import sys, numpy as np
from PIL import Image
img, axis, idx, s, e = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
tol = float(sys.argv[6]) if len(sys.argv) > 6 else 60
a = np.asarray(Image.open(img).convert('RGB')).astype(int)
line = a[idx, s:e+1] if axis == 'row' else a[s:e+1, idx]
bg = np.array([int(sys.argv[7][i:i+2], 16) for i in (1, 3, 5)]) if len(sys.argv) > 7 else np.median(line, 0)
off = np.abs(line-bg).sum(1) > tol
out = []; i = 0
while i < len(line):
    if off[i]:
        j = i
        while j+1 < len(line) and off[j+1]: j += 1
        seg = line[i:j+1]; dark = seg[np.argmin(seg.sum(1))]
        out.append(f'{s+i}-{s+j}(#{dark[0]:02X}{dark[1]:02X}{dark[2]:02X})')
        i = j+1
    else: i += 1
print('bg #%02X%02X%02X:' % tuple(bg.astype(int)), ' '.join(out))
