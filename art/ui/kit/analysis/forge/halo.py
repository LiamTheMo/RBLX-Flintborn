"""Halo/stroke check around text: mean colour of rings 1..4 px outside the ink mask vs the area's background.
usage: halo.py IMAGE x y w h THR [light]"""
import sys, numpy as np
from PIL import Image, ImageFilter
img = sys.argv[1]; x, y, w, h, thr = map(int, sys.argv[2:7]); light = len(sys.argv) > 7
a = np.asarray(Image.open(img).convert('RGB')).astype(float)[y:y+h, x:x+w]
L = a @ [0.299, 0.587, 0.114]
m = (L > thr) if light else (L < thr)
prev = m.copy()
mi = Image.fromarray((m*255).astype('uint8'))
for r in range(1, 6):
    d = np.asarray(mi.filter(ImageFilter.MaxFilter(2*r+1))) > 0
    ring = d & ~prev
    c = np.median(a[ring], 0); print(f'ring {r}: #%02X%02X%02X n={ring.sum()}' % tuple(c.astype(int)))
    prev = d
far = ~(np.asarray(mi.filter(ImageFilter.MaxFilter(13))) > 0)
print('background (>6px away): #%02X%02X%02X' % tuple(np.median(a[far], 0).astype(int)))
