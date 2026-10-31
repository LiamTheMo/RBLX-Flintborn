# obj.py img thr name:x,y,w,h ... -> bbox of pixels whose RGB distance from region's median > thr
import sys, numpy as np
from PIL import Image
img=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
thr=float(sys.argv[2])
for spec in sys.argv[3:]:
    name,b=spec.split(':'); x,y,w,h=map(int,b.split(','))
    r=img[y:y+h,x:x+w]; med=np.median(r.reshape(-1,3),0)
    d=np.sqrt(((r-med)**2).sum(2)); m=d>thr
    ys,xs=np.nonzero(m)
    if len(xs)==0: print(name,'none'); continue
    # robust: ignore rows/cols with <2 px
    cs=m.sum(0); rs=m.sum(1)
    xs2=np.nonzero(cs>=2)[0]; ys2=np.nonzero(rs>=2)[0]
    print(f'{name}: x={x+xs2.min()} y={y+ys2.min()} w={xs2.max()-xs2.min()+1} h={ys2.max()-ys2.min()+1}  (bg median #{int(med[0]):02X}{int(med[1]):02X}{int(med[2]):02X})')
