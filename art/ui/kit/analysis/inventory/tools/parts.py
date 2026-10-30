# list connected components (alpha>200) bounding boxes in a kit sheet, area>=min
import sys, numpy as np
from PIL import Image
a=np.asarray(Image.open(sys.argv[1]).convert('RGBA'))[...,3]>200
mn=int(sys.argv[2]) if len(sys.argv)>2 else 300
H,W=a.shape
lab=np.zeros((H,W),np.int32); n=0; out=[]
# union-find row-run labeling
parent=[0]
def find(x):
    while parent[x]!=x:
        parent[x]=parent[parent[x]]; x=parent[x]
    return x
for y in range(H):
    row=a[y]; x=0
    while x<W:
        if row[x]:
            s=x
            while x<W and row[x]: x+=1
            n+=1; parent.append(n); lab[y,s:x]=n
            if y>0:
                above=np.unique(lab[y-1,max(0,s-1):min(W,x+1)]); 
                for l in above:
                    if l: 
                        ra,rb=find(l),find(n)
                        if ra!=rb: parent[max(ra,rb)]=min(ra,rb)
        else: x+=1
roots=np.array([find(i) for i in range(n+1)])
lab=roots[lab]
ids,counts=np.unique(lab[lab>0],return_counts=True)
res=[]
for i,c in zip(ids,counts):
    if c<mn: continue
    ys,xs=np.nonzero(lab==i)
    res.append((ys.min(),xs.min(),xs.max()-xs.min()+1,ys.max()-ys.min()+1,c))
for y,x,w,h,c in sorted(res):
    print(f'x={x} y={y} w={w} h={h} area={c}')
