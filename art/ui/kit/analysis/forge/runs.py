"""Compact colour runs along a row/column (same idea as ref_tools.py scan, one line per run).
usage: runs.py IMAGE row|col INDEX START END [TOL] [MINLEN]"""
import sys, numpy as np
from PIL import Image
img, axis, idx, s, e = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
tol = float(sys.argv[6]) if len(sys.argv) > 6 else 30
minlen = int(sys.argv[7]) if len(sys.argv) > 7 else 1
a = np.asarray(Image.open(img).convert('RGB')).astype(int)
line = a[idx, s:e+1] if axis == 'row' else a[s:e+1, idx]
runs = []; start = 0
for i in range(1, len(line)+1):
    if i == len(line) or np.abs(line[i]-line[start]).sum() > tol:
        seg = line[start:i]; med = np.median(seg, 0).astype(int)
        runs.append((s+start, s+i-1, '#%02X%02X%02X' % tuple(med)))
        start = i
print(' '.join(f'{a}-{b}:{c}' for a, b, c in runs if b-a+1 >= minlen))
