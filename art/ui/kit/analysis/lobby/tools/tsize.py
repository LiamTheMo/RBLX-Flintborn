import numpy as np
from PIL import Image, ImageFont, ImageDraw
import os
_F=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','..','fonts')
FB=os.path.join(_F,'Merriweather-Bold.woff')
FR=os.path.join(_F,'Merriweather-Regular.woff')
_cache={}
def inkhw(f,text,sz):
    k=(f,text,sz)
    if k in _cache: return _cache[k]
    F=ImageFont.truetype(f,sz*4)
    im=Image.new('L',(int(sz*4*len(text)*1.2)+50,int(sz*4*2)+50),0); ImageDraw.Draw(im).text((10,10),text,font=F,fill=255)
    a=np.array(im)>127; ys=np.where(a.any(1))[0]; xs=np.where(a.any(0))[0]
    r=((ys[-1]-ys[0]+1)/4,(xs[-1]-xs[0]+1)/4); _cache[k]=r; return r
def solve(text,h,f=FB):
    best=None
    for sz in np.arange(6,100,0.5):
        hh,ww=inkhw(f,text,sz)
        if best is None or abs(hh-h)<abs(best[1]-h): best=(sz,hh,ww)
    return best
