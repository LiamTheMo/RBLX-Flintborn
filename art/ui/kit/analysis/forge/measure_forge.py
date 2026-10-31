"""Forge text/ink measurements. Run from the repo root:
python3 art/ui/kit/analysis/forge/measure_forge.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from mlib import Img, fmt
im = Img('art/reference/ui/lobby/06_forge.png')
T = [
 ('title', (460, 150, 430, 60, 110)),
 ('subtitle', (460, 205, 470, 30, 150)),
 ('RECIPES', (335, 258, 100, 30, 110)),
 ('YOUR MATERIALS', (1060, 260, 200, 30, 110)),
 ('IRON PICKAXE', (695, 260, 240, 40, 110)),
 ('desc line1', (700, 552, 300, 24, 140)),
 ('desc line2', (700, 577, 300, 26, 140)),
 ('REQUIRES', (680, 618, 100, 24, 110)),
 ('QUANTITY', (670, 752, 100, 24, 110)),
 ('qty 1', (835, 748, 45, 36, 110)),
 ('FORGE label', (1070, 748, 100, 34, 200, True)),
 ('req1 name', (760, 655, 70, 22, 110)),
 ('req1 count', (760, 678, 70, 26, 150)),
 ('req2 name', (935, 655, 70, 22, 110)),
 ('req2 count', (935, 678, 70, 26, 110)),
]
for i, y in enumerate([300, 375, 451, 527, 603, 680]):
    T.append((f'row{i+1} name', (432, y+4, 205, 34, 110)))
    T.append((f'row{i+1} desc', (432, y+36, 205, 26, 150)))
    T.append((f'row{i+1} icon', (343, y, 90, 68, 150)))
for i, y in enumerate([300, 366, 432, 499, 566, 634]):
    T.append((f'mat{i+1} name', (1140, y+12, 140, 34, 110)))
    T.append((f'mat{i+1} count', (1290, y+12, 45, 34, 110)))
    T.append((f'mat{i+1} icon', (1068, y+2, 72, 60, 150)))
for n, args in T:
    light = len(args) > 5 and args[5] is True
    x, y, w, h, thr = args[:5]
    print(fmt(n, im.ink(x, y, w, h, thr, light)))
