# usage: px.py img row|col idx start end   -> prints "pos:hex(lum)" compact
import sys, numpy as np
from PIL import Image
img=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
mode,idx,s,e=sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
out=[]
for p in range(s,e+1):
    c=img[idx,p] if mode=='row' else img[p,idx]
    l=int(0.299*c[0]+0.587*c[1]+0.114*c[2])
    out.append(f'{p}:{c[0]:02X}{c[1]:02X}{c[2]:02X}({l})')
for i in range(0,len(out),8): print('  '.join(out[i:i+8]))
