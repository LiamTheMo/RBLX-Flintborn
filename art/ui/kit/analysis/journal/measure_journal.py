"""Journal text/ink measurements. Run from the repo root:
python3 art/ui/kit/analysis/journal/measure_journal.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'forge'))
from mlib import Img, fmt
im = Img('art/reference/ui/lobby/07_quest_journal.png')
T = [
 ('title', (450, 170, 420, 65, 110)),
 ('compass icon', (360, 155, 95, 95, 110)),
 ('detail title', (975, 262, 290, 50, 110)),
 ('detail desc1', (978, 314, 345, 24, 110)),
 ('detail desc2', (978, 338, 345, 28, 110)),
 ('OBJECTIVES', (750, 402, 130, 26, 110)),
 ('REWARDS', (750, 632, 110, 26, 110)),
 ('CLAIM label', (1190, 685, 120, 40, 200, True)),
 ('QUEST PROGRESS', (490, 786, 160, 26, 110)),
 ('1/5 Completed', (1040, 786, 145, 26, 110)),
 ('illustration', (745, 255, 230, 130, 150)),
]
for i, y in enumerate([261, 361, 465, 568, 671]):
    T.append((f'q{i+1} title', (475, y+14, 205, 36, 110)))
    T.append((f'q{i+1} sub', (475, y+48, 205, 28, 120)))
    T.append((f'q{i+1} chevron', (685, y+25, 25, 45, 110)))
    T.append((f'q{i+1} icon', (368, y+4, 100, y and 86, 150)))
for i, y in enumerate([432, 497, 562]):
    T.append((f'obj{i+1} title', (830, y+4, 260, 30, 110)))
    T.append((f'obj{i+1} desc', (830, y+33, 300, 22, 140)))
    T.append((f'obj{i+1} count', (1200, y+12, 85, 34, 110)))
    T.append((f'obj{i+1} icon', (756, y+4, 70, 52, 150)))
for i, x in enumerate([751, 849, 946, 1045]):
    T.append((f'rew{i+1} icon', (x+4, 668, 92, 62, 150)))
    T.append((f'rew{i+1} amount', (x+40, 712, 60, 26, 110)))
    T.append((f'rew{i+1} label', (x+2, 737, 96, 24, 110)))
for n, args in T:
    light = len(args) > 5 and args[5] is True
    x, y, w, h, thr = args[:5]
    print(fmt(n, im.ink(x, y, w, h, thr, light)))
