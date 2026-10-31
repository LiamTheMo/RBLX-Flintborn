"""Where the HUD parts sit in the modal mockups (04, 05) relative to 01: best luminance correlation offset."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'))
import numpy as np
from m import img, lum
A = lum(img('01_hud'))
for n in ('05_play', '04_party'):
    B = lum(img(n))
    for nm, (x, y, w, h) in {'hotbar': (550, 799, 572, 93), 'xpbar': (566, 766, 530, 20), 'tiles': (68, 312, 190, 272), 'card': (39, 60, 359, 81), 'currency': (1317, 70, 302, 46)}.items():
        best = None
        for dy in range(-5, 45):
            for dx in range(-6, 7):
                c = np.corrcoef(A[y:y + h, x:x + w].ravel(), B[y + dy:y + dy + h, x + dx:x + dx + w].ravel())[0, 1]
                if best is None or c > best[0]: best = (c, dx, dy)
        print(n, nm, 'corr %.3f dx %+d dy %+d' % best)
