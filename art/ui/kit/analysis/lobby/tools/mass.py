import sys, numpy as np
from PIL import Image, ImageFont, ImageDraw
from m import img, lum
def refmass(n,x,y,w,h):
    L=lum(img(n)[y:y+h,x:x+w]); paper=np.percentile(L,95); inkL=np.percentile(L,2)
    d=np.clip((paper-L)/(paper-inkL),0,1); m=L<(paper+inkL)/2
    ys=np.where(m.any(1))[0]; xs=np.where(m.any(0))[0]
    return d.sum(), ys[-1]-ys[0]+1, xs[-1]-xs[0]+1
def rmass(f,text,inkh):
    for sz in np.arange(6,140,0.25):
        F=ImageFont.truetype(f,sz)
        im=Image.new('L',(2000,300),0); ImageDraw.Draw(im).text((10,10),text,font=F,fill=255)
        a=np.array(im)/255.; m=a>0.5; ys=np.where(m.any(1))[0]; xs=np.where(m.any(0))[0]
        if len(ys) and ys[-1]-ys[0]+1>=inkh: return sz,a.sum(),xs[-1]-xs[0]+1
n,x,y,w,h,text=sys.argv[1],*map(int,sys.argv[2:6]),sys.argv[6]
M,hh,ww=refmass(n,x,y,w,h); print('ref mass %.0f h %d w %d'%(M,hh,ww))
for f in sys.argv[7:]:
    sz,mm,rw=rmass(f,text,hh); print('  %-28s size %.2f mass %.0f (ratio %.2f) w %d'%(f.split('/')[-1],sz,mm,M/mm,rw))
