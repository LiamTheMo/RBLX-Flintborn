# ink.py img x,y,w,h thr [mode]  -> clusters of rows containing pixels with lum<thr (or >thr if mode=light), and x extents per cluster
import sys, numpy as np
from PIL import Image
img=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
x,y,w,h=map(int,sys.argv[2].split(','))
thr=float(sys.argv[3]); light=len(sys.argv)>4 and sys.argv[4]=='light'
L=img[y:y+h,x:x+w]@[0.299,0.587,0.114]
m=(L>thr) if light else (L<thr)
rows=m.sum(1)>0
i=0
while i<h:
    if rows[i]:
        j=i
        while j<h and rows[j]: j+=1
        sub=m[i:j]; cols=np.nonzero(sub.sum(0))[0]
        # split cols into words by gaps >= 8
        segs=[];s=cols[0];p=cols[0]
        for c in cols[1:]:
            if c-p>8: segs.append((s,p)); s=c
            p=c
        segs.append((s,p))
        print(f'rows {y+i}-{y+j-1} (h={j-i}) x {x+cols[0]}-{x+cols[-1]} (w={cols[-1]-cols[0]+1}) segs:',' '.join(f'{x+a}-{x+b}' for a,b in segs))
        i=j
    else: i+=1
