# col.py img name:x,y,w,h[:ink|light|flat] ... flat = median of box; ink = median of darkest 12%; light = median of lightest 12%
import sys, numpy as np
from PIL import Image
img=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
def hx(c): return '#%02X%02X%02X'%tuple(int(round(v)) for v in c)
for spec in sys.argv[2:]:
    parts=spec.split(':'); name=parts[0]; x,y,w,h=map(int,parts[1].split(',')); mode=parts[2] if len(parts)>2 else 'flat'
    r=img[y:y+h,x:x+w].reshape(-1,3); L=r@[0.299,0.587,0.114]
    if mode=='ink': sel=r[L<=np.percentile(L,12)]
    elif mode=='light': sel=r[L>=np.percentile(L,88)]
    else: sel=r
    print(f'{name:24s} {mode:5s} {hx(np.median(sel,0))}  std={sel.std(0).mean():.1f}')
