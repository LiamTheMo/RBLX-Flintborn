"""Reproduces the numbers in docs/ui/LobbyScreen.md. Run: python3 measure_lobby.py > measure_log.txt"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'))
from m import *
from tsize_run import run
n = '01_hud'
print('# Parchment-class components (pcomp.py 01_hud 300) are listed in parchment_components.txt')
print('\n## Edges (first/last outline pixels; outer() marches out from the parchment box, box_from_inside() marches in->out to the first L<75 px)')
for nm, b in [('coins', (1319, 72, 1430, 112)), ('gems', (1452, 72, 1548, 112)), ('gear', (1569, 72, 1616, 112))]:
    print(nm, outer(n, *b))
for x in range(6):
    xx = [552, 649, 745, 842, 939, 1035][x]
    print('hotbar', x + 1, outer(n, xx, 802, xx + 83, 887))
for nm, (x0, y0, x1, y1) in [('tile r1c1', (71, 314, 153, 392)), ('tile r1c2', (173, 314, 254, 392)), ('tile r2c1', (71, 407, 153, 487)),
                             ('tile r2c2', (173, 408, 254, 487)), ('tile r3c1', (71, 502, 153, 582)), ('tile r3c2', (173, 502, 254, 582))]:
    print(nm, box_from_inside(n, (x0 + x1) // 2, (y0 + y1) // 2, (x1 - x0) // 2, (y1 - y0) // 2, inset=3, fr=(0.35, 0.5, 0.65)))
print('party panel', box_from_inside(n, 1471, 379, 141, 116, inset=3, fr=(0.4, 0.5, 0.6)))
print('\n## Luminance profiles used for outer edges')
lprof(n, row=100, a=32, b=46); lprof(n, row=100, a=118, b=136); lprof(n, col=80, a=52, b=66); lprof(n, col=80, a=130, b=148)
runs(n, col=300, a=55, b=145); runs(n, row=95, a=370, b=405)
lprof(n, row=380, a=1315, b=1336); lprof(n, row=380, a=1604, b=1626); lprof(n, col=1450, a=248, b=268); lprof(n, col=1450, a=488, b=512)
lprof(n, row=338, a=1540, b=1600); lprof(n, col=1570, a=318, b=360); lprof(n, row=338, a=1350, b=1400); lprof(n, col=1375, a=318, b=362)
lprof(n, col=1591, a=360, b=480); lprof(n, row=410, a=1580, b=1600)
runs(n, row=114, a=190, b=370); runs(n, col=250, a=100, b=128)
lprof(n, row=776, a=625, b=640); lprof(n, row=776, a=980, b=995); lprof(n, col=700, a=764, b=790); runs(n, row=776, a=625, b=995)
lprof(n, row=92, a=1324, b=1362); lprof(n, col=1342, a=72, b=114); lprof(n, row=92, a=1458, b=1492); lprof(n, col=1474, a=72, b=114)
print('\n## Small parts')
print('photo window', 'row100', end=' '); lprof(n, row=100, a=44, b=54)
print('leaf emblem ink', ink(n, 358, 72, 30, 58, thr=90), colgroups(n, 350, 72, 40, 58, thr=90))
print('gear glyph', ink(n, 1576, 78, 33, 31, thr=110))
print('crown (fill)', flood(n, 1525, 340, tol=60, win=30))
for y in (383, 418, 453): print('party dot', flood(n, 1364, y, tol=25, win=20))
for i, x in enumerate([556, 652, 749, 845, 942, 1038]): print('hotbar badge', i + 1, flood(n, x + 2, 806, tol=45, win=40))
for (x, y, w, h) in [(554, 803, 20, 21), (649, 804, 23, 20), (746, 804, 22, 20)]: print('badge numeral', ink(n, x + 3, y + 2, w - 6, h - 4, thr=150, mode='light'))
print('\n## Text (Merriweather Bold size whose rendered ink height matches the measured ink height)')
run(n, [((143, 76, 125, 26), 'LiamTheMo', 'dark'), ((143, 104, 52, 20), 'LV. 12', 'dark'), ((1362, 80, 62, 26), '2,450', 'dark'), ((1495, 80, 50, 26), '125', 'dark'),
        ((1348, 284, 80, 22), 'PARTY', 'dark'), ((1438, 280, 52, 26), '1/10', 'dark'), ((1402, 328, 95, 22), 'LiamTheMo', 'dark'),
        ((566, 766, 60, 22), 'LV. 12', 'dark'), ((992, 766, 105, 22), '450/750 XP', 'dark')])
print('\n## Colours (median of box)')
for lab, b in [('plate parchment', (300, 92, 40, 6)), ('photo backdrop', (100, 72, 12, 10)), ('card XP fill', (205, 112, 90, 4)), ('card XP track', (325, 111, 28, 5)),
               ('coins parchment', (1415, 84, 12, 20)), ('pill outline', (1380, 114, 30, 2)), ('tile parchment', (140, 350, 8, 20)), ('party parchment', (1450, 440, 80, 20)),
               ('party title rule', (1400, 311, 80, 2)), ('party row rule', (1400, 364, 80, 1)), ('party dot', (1360, 380, 8, 8)), ('scroll thumb', (1589, 380, 6, 40)),
               ('scroll track', (1589, 440, 6, 30)), ('add-friend fill', (1556, 326, 8, 8)), ('bottom XP fill', (700, 773, 150, 6)), ('bottom XP track', (900, 773, 80, 6)),
               ('bottom XP outline', (700, 768, 150, 1)), ('hotbar parchment', (870, 850, 30, 30)), ('hotbar badge', (556, 806, 4, 4))]:
    print('%-20s %s' % (lab, med(n, *b)))
