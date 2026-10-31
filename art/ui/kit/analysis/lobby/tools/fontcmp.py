import sys, numpy as np
from PIL import Image, ImageFont, ImageDraw
from m import img, lum
# args: screen x y w h text out [fonts...]
n,x,y,w,h,text,out=sys.argv[1],*map(int,sys.argv[2:6]),sys.argv[6],sys.argv[7]
fonts=sys.argv[8:]
ref=img(n)[y:y+h,x:x+w]; L=lum(ref); m=L<100
ys=np.where(m.any(1))[0]; xs=np.where(m.any(0))[0]
inkh=ys[-1]-ys[0]+1; inkw=xs[-1]-xs[0]+1
S=4
rows=[Image.fromarray(ref.astype('uint8')).resize((w*S,h*S),Image.NEAREST)]
for f in fonts:
    # find size where ink height matches
    best=None
    for sz in np.arange(8,140,0.5):
        F=ImageFont.truetype(f,int(round(sz*S)))
        im=Image.new('L',(w*S*3,h*S*3),0); d=ImageDraw.Draw(im); d.text((10,10),text,font=F,fill=255)
        a=np.array(im)>128; yy=np.where(a.any(1))[0]; xx=np.where(a.any(0))[0]
        hh=(yy[-1]-yy[0]+1)/S
        if hh>=inkh: best=(sz,a[yy[0]:yy[-1]+1,xx[0]:xx[-1]+1]); break
    sz,a=best
    print(f.split('/')[-1],'size',sz,'ink w',a.shape[1]/S,'ref w',inkw,'ink h',a.shape[0]/S,'ref h',inkh)
    can=Image.new('RGB',(w*S,h*S),(245,215,170)); g=Image.fromarray(((1-a)*200+30).astype('uint8')).convert('RGB')
    can.paste(g,(xs[0]*S,ys[0]*S)); rows.append(can)
W=w*S; H=sum(r.size[1] for r in rows)
o=Image.new('RGB',(W,H)); yy=0
for r in rows: o.paste(r,(0,yy)); yy+=r.size[1]
o.save(out)
