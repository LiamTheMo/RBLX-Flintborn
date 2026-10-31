import sys
from PIL import Image, ImageDraw
src,out=sys.argv[1],sys.argv[2]
box=tuple(map(int,sys.argv[3].split(','))) if len(sys.argv)>3 else None
scale=float(sys.argv[4]) if len(sys.argv)>4 else 1
im=Image.open(src).convert('RGBA')
bg=Image.new('RGBA',im.size,(90,110,130,255)); bg.alpha_composite(im); im=bg.convert('RGB')
x0,y0=0,0
if box: x0,y0=box[0],box[1]; im=im.crop((box[0],box[1],box[0]+box[2],box[1]+box[3]))
im=im.resize((int(im.width*scale),int(im.height*scale)),Image.LANCZOS)
d=ImageDraw.Draw(im)
step=100 if not box or box[2]>500 else 50
import math
for gx in range((x0//step+1)*step, int(x0+im.width/scale), step):
    X=(gx-x0)*scale; d.line([(X,0),(X,im.height)],fill=(255,0,255),width=1); d.text((X+2,2),str(gx),fill=(255,255,0))
for gy in range((y0//step+1)*step, int(y0+im.height/scale), step):
    Y=(gy-y0)*scale; d.line([(0,Y),(im.width,Y)],fill=(0,255,255),width=1); d.text((2,Y+2),str(gy),fill=(255,255,0))
im.save(out)
