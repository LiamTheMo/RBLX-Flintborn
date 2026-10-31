# sbs.py img out scale  then triples: x,y,w,h|text|size ...
import sys
from PIL import Image, ImageFont, ImageDraw
img=Image.open(sys.argv[1]).convert('RGB'); out=sys.argv[2]; sc=int(sys.argv[3])
fonts=[('MW Bold','art/ui/fonts/Merriweather-Bold.woff'),('MW Regular','art/ui/fonts/Merriweather-Regular.woff')]
tiles=[]
for spec in sys.argv[4:]:
    box,text,size=spec.split('|'); x,y,w,h=map(int,box.split(',')); size=float(size)
    c=img.crop((x,y,x+w,y+h))
    tiles.append(c.resize((w*sc,h*sc),Image.LANCZOS))
    for n,p in fonts:
        f=ImageFont.truetype(p,size*sc)
        t=Image.new('RGB',(w*sc,h*sc),(253,216,168)); d=ImageDraw.Draw(t); d.text((4,4),text,font=f,fill=(43,22,10)); d.text((w*sc-110,2),n,fill=(200,0,0))
        tiles.append(t)
W=max(t.width for t in tiles); H=sum(t.height+6 for t in tiles)
o=Image.new('RGB',(W,H),'white'); yy=0
for t in tiles: o.paste(t,(0,yy)); yy+=t.height+6
o.save(out)
