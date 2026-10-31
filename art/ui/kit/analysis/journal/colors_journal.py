"""Median colours of flat areas in the journal mockup (x, y, w, h boxes)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'forge'))
from mlib import Img
im = Img('art/reference/ui/lobby/07_quest_journal.png')
B = {
 'window parchment (header band)': (900, 160, 200, 10),
 'window parchment (under list)': (500, 780, 150, 6),
 'quest row fill (row2 right)': (650, 375, 30, 20),
 'quest row outline (row2 top 361-362)': (500, 361, 150, 2),
 'quest sel fill top-right': (640, 270, 60, 8),
 'quest sel fill mid-right': (650, 300, 30, 20),
 'quest sel fill bottom': (500, 340, 150, 6),
 'quest sel fill left': (372, 268, 10, 10),
 'quest sel border (261-264)': (450, 262, 200, 2),
 'quest sel border right (717-720)': (718, 280, 2, 50),
 'chevron ink': (695, 305, 4, 6),
 'active tab fill': (262, 268, 10, 50),
 'active tab border top (252-256)': (270, 253, 40, 2),
 'tab2 fill': (262, 360, 8, 50),
 'tab2 outline left (255-256)': (255, 360, 1, 50),
 'tab icon book leather': (284, 290, 8, 10),
 'tab icon trophy brown': (290, 378, 10, 8),
 'objective row fill': (1100, 440, 80, 8),
 'objective row outline top (431-433)': (900, 432, 200, 1),
 'objective desc ink': (840, 470, 200, 8),
 'circle ring': (1296, 458, 3, 6),
 'reward tile fill': (800, 668, 30, 8),
 'reward tile outline (662-663)': (770, 662, 60, 2),
 'claim leather top': (1190, 670, 120, 6),
 'claim leather mid': (1170, 700, 20, 15),
 'claim leather bottom': (1190, 735, 120, 6),
 'close leather': (1305, 180, 10, 8),
 'progress track': (850, 795, 150, 8),
 'progress fill': (680, 797, 70, 6),
 'progress fill top highlight (y794)': (680, 794, 70, 1),
 'progress outline (y790-791)': (850, 790, 150, 2),
 'header rule (242-243)': (500, 242, 300, 2),
 'detail rule (395-396)': (900, 395, 300, 2),
 'rewards rule (627-628)': (900, 627, 300, 2),
 'bottom rule (776-777)': (500, 776, 300, 2),
 'vline 735': (735, 300, 1, 400),
 'vline 351': (351, 300, 1, 400),
 'title ink core': (470, 195, 20, 20),
}
for k, b in B.items():
    print(f'{k:42s} {b} {im.box(*b)}')
