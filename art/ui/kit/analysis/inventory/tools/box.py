# box.py img thr name:x,y ...  -> scan from seed outward to first pixel with lum<thr (outline), report outer edges by continuing through dark run
import sys, numpy as np
from PIL import Image
img=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
L=img@[0.299,0.587,0.114]
thr=float(sys.argv[2])
H,W=L.shape
for spec in sys.argv[3:]:
    name,xy=spec.split(':'); x,y=map(int,xy.split(','))
    res={}
    for d,(dx,dy) in {'L':(-1,0),'R':(1,0),'U':(0,-1),'D':(0,1)}.items():
        cx,cy=x,y
        while 0<cx<W-1 and 0<cy<H-1 and L[cy,cx]>=thr: cx+=dx; cy+=dy
        inner=(cx,cy)
        n=0
        while 0<cx<W-1 and 0<cy<H-1 and L[cy,cx]<thr+40 and n<12: cx+=dx;cy+=dy;n+=1
        res[d]=(inner,(cx-dx,cy-dy))
    l=res['L'][1][0]; r=res['R'][1][0]; u=res['U'][1][1]; dn=res['D'][1][1]
    il=res['L'][0][0]; ir=res['R'][0][0]; iu=res['U'][0][1]; idn=res['D'][0][1]
    print(f'{name}: outer x={l} y={u} w={r-l+1} h={dn-u+1} | first-dark L{il} R{ir} U{iu} D{idn} | outline px L{il-l+1} R{r-ir+1} U{iu-u+1} D{dn-idn+1}')
