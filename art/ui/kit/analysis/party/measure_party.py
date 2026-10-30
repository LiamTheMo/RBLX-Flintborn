"""Reproduces the numbers in docs/ui/PartyScreen.md. Run: python3 measure_party.py > measure_log.txt"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lobby', 'tools'))
from m import *
from tsize_run import run
n = '04_party'
L = lum(img(n))
print('## Window frame edges')
for y in (300, 450, 600): lprof(n, row=y, a=266, b=290); lprof(n, row=y, a=1382, b=1404)
for x in (500, 800, 1100): lprof(n, col=x, a=136, b=160); lprof(n, col=x, a=762, b=786)
print('\n## Close (X) button and CLOSE button'); lprof(n, row=195, a=1318, b=1390); lprof(n, col=1352, a=160, b=230)
lprof(n, row=731, a=700, b=720); lprof(n, row=731, a=950, b=972); lprof(n, col=835, a=694, b=708); lprof(n, col=835, a=754, b=772)
print('\n## Sub-panel borders (dips >12 below line median)')
def dips(row=None, col=None, a=0, b=0, thr=12):
    line = L[row, a:b] if row is not None else L[a:b, col]; base = np.median(line)
    out = [(a + i, int(v)) for i, v in enumerate(line) if v < base - thr]; g = []
    for p in out:
        if g and p[0] - g[-1][-1][0] <= 1: g[-1].append(p)
        else: g.append([p])
    print(('row %d' % row) if row is not None else ('col %d' % col), 'base', int(base), ' '.join('%d-%d(min %d)' % (q[0][0], q[-1][0], min(v for _, v in q)) for q in g))
dips(row=680, a=285, b=1390); dips(col=480, a=230, b=710); dips(col=860, a=230, b=710); dips(col=1200, a=230, b=710)
print('corner radius scan (first border px per row, YourParty TL):')
for y in range(244, 256): print(' ', y, [300 + i for i, v in enumerate(L[y, 300:330]) if v < 212][:3])
print('\n## Rules (rows darker than +-3 px rows)')
def hextent(y, a, b, delta=6):
    line = L[y, a:b]; ref = (L[y - 3, a:b] + L[y + 3, a:b]) / 2; d = np.where(ref - line > delta)[0]
    if len(d) < 20: return
    print('y', y, 'x %d..%d' % (a + d[0], a + d[-1]), med(n, a + d[len(d) // 2], y, 8, 1))
for y in (297, 298): hextent(y, 306, 661, 10); hextent(y, 672, 1038, 10); hextent(y, 1049, 1366, 10)
for y in (376, 428, 481, 533, 586, 638): hextent(y, 306, 661)
for y in (367, 433, 500): hextent(y, 672, 1038)
for y in (341, 377, 413, 448, 485): hextent(y, 1049, 1366)
hextent(629, 1049, 1366)
for y in range(226, 234):
    d = np.where(L[y, 282:1390] < 150)[0]; print('ground line y', y, (282 + d[0], 282 + d[-1]) if len(d) else None)
print('\n## Headshots')
for args in [dict(row=340, a=314, b=326), dict(row=340, a=372, b=384), dict(col=348, a=308, b=320), dict(col=348, a=362, b=374),
             dict(row=400, a=684, b=694), dict(row=400, a=736, b=746), dict(col=715, a=370, b=382), dict(col=715, a=422, b=432),
             dict(col=715, a=436, b=448), dict(col=715, a=488, b=498), dict(row=597, a=1058, b=1068), dict(row=597, a=1108, b=1118),
             dict(col=1087, a=568, b=580), dict(col=1087, a=618, b=630)]:
    lprof(n, **args)
print('\n## Pills, dots, search, icons')
print('crown fill', flood(n, 549, 342, tol=70, win=30))
lprof(n, row=339, a=568, b=580); lprof(n, row=339, a=642, b=654); lprof(n, col=610, a=318, b=330); lprof(n, col=610, a=350, b=362)
for y in (402, 455, 508, 560, 612, 665): print('empty dot', flood(n, 349, y, tol=25, win=30))
lprof(n, row=335, a=680, b=692); lprof(n, row=335, a=1018, b=1030); lprof(n, col=850, a=308, b=320); lprof(n, col=850, a=350, b=362)
print('search glyph', ink(n, 694, 320, 30, 30, thr=110), 'people glyph', ink(n, 320, 260, 45, 32, thr=110), 'magnifier glyph', ink(n, 688, 258, 36, 36, thr=110))
print('info disc', ink(n, 1060, 258, 40, 40, thr=110), 'check disc', ink(n, 1060, 520, 40, 40, thr=110))
lprof(n, row=400, a=906, b=920); lprof(n, row=400, a=1015, b=1030); lprof(n, col=967, a=372, b=384); lprof(n, col=967, a=416, b=430)
lprof(n, row=597, a=1262, b=1272); lprof(n, row=597, a=1346, b=1358); lprof(n, col=1310, a=575, b=586); lprof(n, col=1310, a=608, b=620)
print('green dot', flood(n, 1284, 597, tol=60, win=20))
print('tent', ink(n, 690, 170, 55, 55, thr=110), 'trees L', ink(n, 630, 165, 60, 62, thr=170), 'trees R', ink(n, 935, 160, 90, 68, thr=170))
print('\n## Text')
run(n, [((760, 170, 170, 55), 'PARTY', 'dark'), ((365, 262, 145, 30), 'YOUR PARTY', 'dark'), ((530, 262, 60, 30), '1/10', 'dark'),
        ((390, 318, 115, 22), 'LiamTheMo', 'dark'), ((390, 343, 50, 20), 'LV. 12', 'dark'), ((585, 328, 50, 22), 'Leader', 'dark'),
        ((390, 392, 90, 22), 'Empty Slot', 'dark'), ((735, 262, 170, 30), 'INVITE PLAYERS', 'dark'), ((725, 324, 125, 22), 'Search players...', 'dark'),
        ((752, 380, 115, 22), 'ForestRanger', 'dark'), ((752, 403, 45, 20), 'LV. 15', 'dark'), ((752, 446, 95, 24), 'SunnyVale', 'dark'), ((752, 470, 35, 20), 'LV. 8', 'dark'),
        ((935, 390, 65, 22), 'Invite', 'light'), ((1105, 262, 170, 30), 'PARTY DETAILS', 'dark'), ((1070, 313, 110, 22), 'Party Leader', 'dark'),
        ((1275, 313, 75, 22), 'LiamTheMo', 'dark'), ((1070, 348, 80, 22), 'Members', 'dark'), ((1300, 348, 50, 22), '1 / 10', 'dark'),
        ((1070, 384, 90, 22), 'Join Type', 'dark'), ((1265, 384, 85, 22), 'Invite Only', 'dark'), ((1070, 420, 80, 22), 'Play Style', 'dark'),
        ((1295, 420, 55, 22), 'Casual', 'dark'), ((1070, 456, 65, 22), 'Created', 'dark'), ((1280, 456, 70, 22), 'Just now', 'dark'),
        ((1105, 525, 170, 30), 'READIED STATUS', 'dark'), ((1122, 587, 100, 22), 'LiamTheMo', 'dark'), ((1295, 587, 50, 22), 'Ready', 'dark'), ((790, 715, 95, 32), 'CLOSE', 'light')])
print('\n## Colours')
for lab, b in [('window parchment', (350, 720, 100, 15)), ('sub-panel fill', (850, 560, 80, 80)), ('sub-panel border', (450, 245, 60, 2)), ('header rule', (450, 297, 100, 1)),
               ('row rule', (450, 481, 100, 1)), ('leader pill fill', (590, 326, 40, 4)), ('leader pill outline', (600, 323, 30, 1)), ('empty dot', (345, 398, 8, 8)),
               ('search fill', (900, 320, 80, 8)), ('search outline', (900, 314, 80, 1)), ('invite leather', (925, 400, 15, 6)), ('ready fill', (1320, 584, 25, 6)),
               ('ready outline', (1300, 581, 30, 1)), ('green dot', (1282, 595, 4, 4)), ('CLOSE leather', (730, 730, 40, 10)), ('X btn leather', (1330, 175, 8, 8)),
               ('info/check disc', (1068, 265, 4, 4)), ('ground line', (800, 230, 40, 2)), ('tree ink', (960, 200, 4, 8))]:
    print('%-20s %s' % (lab, med(n, *b)))
