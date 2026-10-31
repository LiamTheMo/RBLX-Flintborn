"""Kit sheet on a grey backdrop with a labelled grid every STEP px (for locating parts).
usage: kitgrid.py SHEET STEP OUT [x y w h scale]"""
import sys
from PIL import Image, ImageDraw
src, step, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
im = Image.open(src).convert('RGBA')
bg = Image.new('RGBA', im.size, (90, 90, 90, 255)); bg.alpha_composite(im); im = bg.convert('RGB')
x, y, w, h, sc = (map(int, sys.argv[4:9]) if len(sys.argv) > 8 else (0, 0, im.width, im.height, 1))
im = im.crop((x, y, x+w, y+h)).resize((w*sc, h*sc), Image.NEAREST)
d = ImageDraw.Draw(im)
for gx in range(((x+step-1)//step)*step, x+w, step):
    px = (gx-x)*sc; d.line([(px, 0), (px, h*sc)], fill=(255, 0, 255)); d.text((px+2, 2), str(gx), fill=(255, 255, 0))
for gy in range(((y+step-1)//step)*step, y+h, step):
    py = (gy-y)*sc; d.line([(0, py), (w*sc, py)], fill=(0, 220, 255)); d.text((2, py+2), str(gy), fill=(255, 255, 0))
im.save(out)
