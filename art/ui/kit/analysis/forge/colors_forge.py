"""Median colours of flat areas in the forge mockup (x, y, w, h boxes)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from mlib import Img
im = Img('art/reference/ui/lobby/06_forge.png')
B = {
 'window parchment (top band)': (600, 236, 200, 8),
 'window parchment (right col)': (1100, 236, 150, 8),
 'recipes col bg': (325, 300, 8, 400),
 'recipe row fill (row2, right part)': (590, 380, 40, 20),
 'recipe row fill (row4 right)': (600, 535, 30, 40),
 'recipe row outline (row2 top edge y373-374)': (450, 373, 150, 2),
 'recipe sel fill (x430-450 top)': (580, 302, 40, 6),
 'recipe sel fill centre right': (600, 325, 30, 20),
 'recipe sel fill bottom right': (600, 352, 30, 6),
 'recipe sel fill left (x350-360)': (348, 330, 6, 20),
 'recipe sel outline gold (y294-295)': (450, 294, 150, 2),
 'recipe sel outline dark (y296)': (450, 296, 150, 1),
 'recipe sel inner gold (y298-299)': (450, 298, 150, 2),
 'mat row fill (Wood right)': (1230, 340, 60, 12),
 'mat row outline top (y299-300)': (1200, 299, 80, 2),
 'mat sel fill top': (1210, 440, 80, 6),
 'mat sel fill mid': (1240, 458, 50, 10),
 'mat sel fill bottom': (1240, 478, 50, 6),
 'mat sel outline (y431-433)': (1200, 432, 80, 2),
 'req card fill': (800, 700, 40, 6),
 'req card outline top (645-646)': (720, 645, 100, 2),
 'divider 608': (750, 608, 200, 2),
 'divider 722': (750, 722, 200, 2),
 'top rule 248': (450, 248, 200, 2),
 'vrule 657': (657, 300, 1, 400),
 'vrule 1046': (1046, 300, 1, 400),
 'vrule 320': (320, 300, 1, 400),
 'art brush stroke behind pickaxe': (880, 480, 25, 25),
 'qty field fill': (838, 760, 8, 18),
 'qty field outline (y741)': (840, 741, 40, 1),
 'minus leather': (785, 748, 10, 8),
 'minus leather low': (785, 772, 10, 6),
 'plus leather': (900, 748, 10, 8),
 'forge leather top': (990, 738, 180, 6),
 'forge leather mid': (1170, 760, 30, 10),
 'forge leather bottom': (1000, 785, 160, 5),
 'close leather': (1298, 176, 8, 8),
 'close leather low': (1298, 205, 30, 6),
 'outline window left (285-288)': (285, 400, 3, 100),
 'window inner stitch (295)': (295, 400, 1, 100),
}
for k, b in B.items():
    print(f'{k:42s} {b} {im.box(*b)}')
