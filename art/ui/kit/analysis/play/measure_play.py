"""Reproduces the numbers in docs/ui/PlayScreen.md. Run: python3 measure_play.py > measure_log.txt"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lobby', 'tools'))
from m import *
from tsize_run import run
n = '05_play'
print('## Window frame edges (luminance; outer outline = first dark run outside the rim)')
for y in (300, 450, 600): lprof(n, row=y, a=300, b=322); lprof(n, row=y, a=1350, b=1372)
for x in (500, 800, 1100): lprof(n, col=x, a=118, b=140); lprof(n, col=x, a=778, b=800)
print('\n## Close button'); lprof(n, row=162, a=1285, b=1365); lprof(n, col=1320, a=125, b=200)
print('leather comps (no outline): close', leather_box(n, 1285, 128, 70, 68), 'PLAY btn', leather_box(n, 880, 685, 460, 95))
print('\n## Title plaque / region plaque'); lprof(n, row=200, a=348, b=362); lprof(n, row=200, a=624, b=640); lprof(n, col=490, a=150, b=162); lprof(n, col=490, a=234, b=250)
lprof(n, row=260, a=885, b=900); lprof(n, row=260, a=1310, b=1325); lprof(n, col=1100, a=215, b=230); lprof(n, col=1100, a=288, b=302)
print('\n## Map sheet'); lprof(n, row=500, a=340, b=362); lprof(n, row=500, a=855, b=880)
for x in (680, 750, 820): lprof(n, col=x, a=210, b=232)
for x in (420, 600): lprof(n, col=x, a=748, b=768)
print('rune', ink(n, 375, 270, 60, 90, thr=110), 'x mark', flood(n, 659, 423, tol=80, win=25))
print('\n## Detail icons')
for (x, y, w, h), nm in [((900, 300, 45, 40), 'region/volcano'), ((900, 338, 45, 40), 'biome/palm'), ((900, 377, 45, 40), 'difficulty/tools'), ((900, 416, 45, 40), 'recommended/chest')]:
    print(nm, ink(n, x, y, w, h, thr=120))
print('\n## Dividers (rows darker than the rows 3 px above/below)')
L = lum(img(n))
for y in (338, 377, 417, 466):
    line = L[y, 890:1330]; ref = (L[y - 3, 890:1330] + L[y + 3, 890:1330]) / 2; d = np.where(ref - line > 8)[0]
    print('y', y, 'x %d..%d' % (890 + d[0], 890 + d[-1]), med(n, 1000, y, 150, 1))
print('\n## Party row box / headshot / crown'); lprof(n, row=540, a=890, b=902); lprof(n, row=540, a=1310, b=1322); lprof(n, col=1150, a=500, b=512); lprof(n, col=1150, a=556, b=568)
lprof(n, row=532, a=944, b=956); lprof(n, row=532, a=994, b=1004); lprof(n, col=973, a=506, b=516); lprof(n, col=973, a=552, b=562)
print('crown fill', flood(n, 925, 535, tol=70, win=25))
print('\n## Equipment slots')
for i, x in enumerate([889, 965, 1039, 1114, 1187, 1261]): print('slot', i + 1, outer(n, x, 608, x + 64, 679, fr=(0.4, 0.6, 0.8)))
for i, x in enumerate([887, 962, 1037, 1112, 1185, 1259]): print('badge', i + 1, flood(n, x + 5, 612, tol=50, win=25, ref=(0x65, 0x28, 0x08)))
print('\n## PLAY button'); lprof(n, row=732, a=880, b=905); lprof(n, row=732, a=1305, b=1330); lprof(n, col=1100, a=688, b=702); lprof(n, col=1100, a=760, b=775); lprof(n, row=715, a=880, b=905)
print('triangle', ink(n, 1020, 708, 45, 48, thr=200, mode='light'))
print('\n## Text')
run(n, [((395, 170, 195, 60), 'PLAY', 'dark'), ((915, 232, 375, 50), 'Shattered Crater', 'dark'),
        ((960, 308, 70, 24), 'Region', 'dark'), ((1135, 308, 135, 24), 'Shattered Crater', 'dark'), ((960, 346, 60, 24), 'Biome', 'dark'), ((1135, 346, 135, 24), 'Tropical Islands', 'dark'),
        ((960, 385, 85, 26), 'Difficulty', 'dark'), ((1135, 385, 90, 24), 'Moderate', 'dark'), ((960, 424, 130, 24), 'Recommended', 'dark'), ((1135, 424, 85, 24), 'Level 10+', 'dark'),
        ((895, 476, 150, 26), 'YOUR PARTY', 'dark'), ((1010, 523, 110, 24), 'LiamTheMo', 'dark'), ((1250, 523, 55, 22), 'LV. 12', 'dark'),
        ((895, 572, 200, 26), 'YOUR EQUIPMENT', 'dark'), ((1075, 710, 145, 45), 'PLAY', 'light')])
print('\n## Colours')
for lab, b in [('window parchment', (650, 770, 100, 10)), ('window parchment R', (1320, 450, 20, 40)), ('frame rim', (800, 129, 200, 2)), ('title plaque', (380, 165, 15, 10)),
               ('region plaque', (905, 230, 10, 8)), ('detail rule', (1000, 338, 150, 1)), ('section rule', (1000, 466, 200, 1)), ('party row fill', (1150, 515, 40, 10)),
               ('party row border', (1100, 507, 40, 1)), ('slot parchment', (1140, 650, 30, 20)), ('badge', (892, 612, 4, 4)), ('PLAY leather top', (1000, 705, 60, 8)),
               ('PLAY leather mid', (960, 730, 40, 10)), ('PLAY leather bottom', (1000, 752, 60, 8)), ('close leather', (1300, 145, 8, 8)), ('detail icon ink', (920, 320, 4, 4))]:
    print('%-20s %s' % (lab, med(n, *b)))
