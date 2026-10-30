"""Crop a region, upscale, and draw labelled rulers (ticks every 10 px, labels every 50).
usage: ruler.py IMAGE x y w h scale OUT"""
import sys
from PIL import Image, ImageDraw
img, x, y, w, h, sc, out = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
src = Image.open(img).convert('RGB').crop((x, y, x+w, y+h)).resize((w*sc, h*sc), Image.NEAREST)
M = 40
can = Image.new('RGB', (w*sc+M, h*sc+M), 'white'); can.paste(src, (M, M))
d = ImageDraw.Draw(can)
for gx in range((x//10)*10, x+w+1, 10):
    if gx < x: continue
    px = M+(gx-x)*sc; major = gx % 50 == 0
    d.line([(px, M-(12 if major else 5)), (px, M)], fill='black')
    if major:
        d.text((px+2, 2), str(gx), fill='red')
        d.line([(px, M), (px, M+h*sc)], fill=(255, 0, 255))
for gy in range((y//10)*10, y+h+1, 10):
    if gy < y: continue
    py = M+(gy-y)*sc; major = gy % 50 == 0
    d.line([(M-(12 if major else 5), py), (M, py)], fill='black')
    if major:
        d.text((1, py+2), str(gy), fill='red')
        d.line([(M, py), (M+w*sc, py)], fill=(0, 200, 255))
can.save(out)
