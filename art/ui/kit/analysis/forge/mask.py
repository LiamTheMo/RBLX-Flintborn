"""Bounding box of pixels matching a colour class inside a box, plus their median colour.
classes: leather (orange-brown metal), dark (luma<THR), gold, red, white, notparch (differs from parchment)
usage: mask.py IMAGE CLASS x y w h"""
import sys, numpy as np
from PIL import Image
img, cls = sys.argv[1], sys.argv[2]; x, y, w, h = map(int, sys.argv[3:7])
a = np.asarray(Image.open(img).convert('RGB')).astype(int)[y:y+h, x:x+w]
R, G, B = a[..., 0], a[..., 1], a[..., 2]
lum = 0.299*R+0.587*G+0.114*B
m = {'leather': (R > 120) & (R-G > 60) & (G-B > 10) & (B < 90),
     'dark': lum < 70,
     'gold': (R > 220) & (G > 150) & (G < 215) & (B < 120),
     'red': (R > 140) & (G < 80) & (B < 60),
     'white': lum > 235,
     'notparch': (np.abs(a-[253, 223, 180]).sum(-1) > 90)}[cls]
ys, xs = np.nonzero(m)
if len(ys) == 0: print('none'); sys.exit()
print(f'{cls}: x {x+xs.min()}..{x+xs.max()} y {y+ys.min()}..{y+ys.max()} (w {xs.max()-xs.min()+1} h {ys.max()-ys.min()+1}) n={len(ys)} median #%02X%02X%02X' % tuple(np.median(a[m], 0).astype(int)))
