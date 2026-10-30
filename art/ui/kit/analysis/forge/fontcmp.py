"""Render candidate fonts under a reference crop at a matched cap (or x-) height.
usage: fontcmp.py REF x y w h TEXT METRIC(cap|x) PX OUT FONT[:label] ...
Small caps: put the text in the form 'A|NCESTRAL F|ORGE' (| toggles small-cap scale 0.86)."""
import sys
from PIL import Image, ImageDraw, ImageFont
ref, x, y, w, h, text, metric, px, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6], sys.argv[7], int(sys.argv[8]), sys.argv[9]
fonts = sys.argv[10:]
S = 3
crop = Image.open(ref).convert('RGB').crop((x, y, x+w, y+h))
rows = [('reference', crop.resize((w*S, h*S), Image.LANCZOS))]
def size_for(path, target):
    for s in range(6, 200):
        f = ImageFont.truetype(path, s)
        bb = f.getbbox('H' if metric == 'cap' else 'x')
        if bb[3]-bb[1] >= target:
            return s
    return 200
for spec in fonts:
    path, _, label = spec.partition(':')
    s = size_for(path, px*S)
    img = Image.new('RGB', (w*S, h*S), (253, 224, 182)); d = ImageDraw.Draw(img)
    if '|' in text:
        sm = ImageFont.truetype(path, int(round(s*0.86)))
        big = ImageFont.truetype(path, s)
        cx = 4; base = int(h*S*0.8); big_mode = True
        for part in text.split('|'):
            for ch in part:
                f = big if big_mode else sm
                d.text((cx, base), ch, font=f, fill=(35, 4, 0), anchor='ls'); cx += f.getlength(ch)
            big_mode = not big_mode
        width = cx
    else:
        f = ImageFont.truetype(path, s)
        d.text((4, int(h*S*0.8)), text, font=f, fill=(35, 4, 0), anchor='ls'); width = f.getlength(text)
    rows.append((f'{label or path.split("/")[-1]} size {s/S:.1f}px width {width/S:.0f}px', img))
W = w*S; H = sum(r[1].height+18 for r in rows)
c = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(c); yy = 0
for lab, im in rows:
    d.text((2, yy+2), lab, fill='black'); yy += 16; c.paste(im, (0, yy)); yy += im.height+2
c.save(out)
