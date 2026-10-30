# ink2.py img name:x,y,w,h[:light] -> glyph core colour: pixels beyond 70% of the way from bg median to extreme
import sys, numpy as np
from PIL import Image
img=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
def hx(c): return '#%02X%02X%02X'%tuple(int(round(v)) for v in c)
for spec in sys.argv[2:]:
    p=spec.split(':'); name=p[0]; x,y,w,h=map(int,p[1].split(',')); light=len(p)>2 and p[2]=='light'
    r=img[y:y+h,x:x+w].reshape(-1,3); L=r@[0.299,0.587,0.114]
    bg=np.median(L); ext=L.max() if light else L.min()
    cut=bg+0.7*(ext-bg)
    sel=r[L>=cut] if light else r[L<=cut]
    print(f'{name:16s} core {hx(np.median(sel,0))} n={len(sel)} bg {hx(np.median(r,0))}')
