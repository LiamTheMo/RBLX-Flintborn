# edges.py img row|col idx start end [thr]  -> runs of dark (lum<thr) pixels: start-end(minlum)
import sys, numpy as np
from PIL import Image
img=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
L=img@[0.299,0.587,0.114]
mode,idx,s,e=sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
thr=float(sys.argv[6]) if len(sys.argv)>6 else 100
line=L[idx,s:e+1] if mode=='row' else L[s:e+1,idx]
runs=[];i=0
while i<len(line):
    if line[i]<thr:
        j=i
        while j<len(line) and line[j]<thr: j+=1
        runs.append(f'{s+i}-{s+j-1}({int(line[i:j].min())})'); i=j
    else: i+=1
print(f'{mode} {idx} [{s},{e}] dark<{thr}:',' '.join(runs))
