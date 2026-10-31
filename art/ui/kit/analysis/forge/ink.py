"""Ink bounding box inside a box: pixels darker than THR (luma) or matching --hex within TOL.
Prints bbox and a compact row profile (y:count) so cap height / baseline / descenders can be read.
usage: ink.py IMAGE x y w h [THR] [mode: dark|light]"""
import sys, numpy as np
from PIL import Image
img = sys.argv[1]; x, y, w, h = map(int, sys.argv[2:6])
thr = float(sys.argv[6]) if len(sys.argv) > 6 else 110
mode = sys.argv[7] if len(sys.argv) > 7 else 'dark'
a = np.asarray(Image.open(img).convert('RGB')).astype(float)[y:y+h, x:x+w]
l = a @ [0.299, 0.587, 0.114]
m = l < thr if mode == 'dark' else l > thr
ys, xs = np.nonzero(m)
if len(ys) == 0: print('no ink'); sys.exit()
print(f'bbox x {x+xs.min()}..{x+xs.max()} y {y+ys.min()}..{y+ys.max()}  (w {xs.max()-xs.min()+1}, h {ys.max()-ys.min()+1})')
rows = m.sum(1)
print('rows', ' '.join(f'{y+i}:{c}' for i, c in enumerate(rows) if c))
ink = a[m]; print('ink median #%02X%02X%02X' % tuple(np.median(ink, 0).astype(int)), 'darkest-quartile #%02X%02X%02X' % tuple(np.median(ink[l[m] <= np.percentile(l[m], 25)], 0).astype(int)))
