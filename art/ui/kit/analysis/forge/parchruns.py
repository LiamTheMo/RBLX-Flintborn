"""Runs of 'parchment-like' pixels (light warm: luma>180, R>G>B) along a row or column -> tile/panel spans.
usage: parchruns.py IMAGE row|col INDEX START END [MINLEN]"""
import sys, numpy as np
from PIL import Image
img, axis, idx, s, e = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
mn = int(sys.argv[6]) if len(sys.argv) > 6 else 4
a = np.asarray(Image.open(img).convert('RGB')).astype(int)
line = a[idx, s:e+1] if axis == 'row' else a[s:e+1, idx]
L = line @ [0.299, 0.587, 0.114]
p = (L > 180) & (line[:, 0] >= line[:, 1]) & (line[:, 1] >= line[:, 2])
out = []; i = 0
while i < len(p):
    if p[i]:
        j = i
        while j+1 < len(p) and p[j+1]: j += 1
        if j-i+1 >= mn: out.append(f'{s+i}-{s+j}')
        i = j+1
    else: i += 1
print(' '.join(out))
