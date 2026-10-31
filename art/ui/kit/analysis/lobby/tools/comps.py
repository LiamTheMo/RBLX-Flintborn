import sys, numpy as np
from PIL import Image
def label(mask):
    # run-length based connected components (8-connectivity)
    H,W=mask.shape
    parent=[]
    def find(a):
        while parent[a]!=a:
            parent[a]=parent[parent[a]]; a=parent[a]
        return a
    prev=[]; runs_all=[]
    for y in range(H):
        row=mask[y]
        d=np.diff(np.concatenate(([0],row.astype(np.int8),[0])))
        st=np.where(d==1)[0]; en=np.where(d==-1)[0]
        cur=[]
        j=0
        for s,e in zip(st,en):
            lab=len(parent); parent.append(lab)
            for (ps,pe,pl) in prev:
                if ps<=e and pe>=s-0:  # overlap with 8-conn (pe exclusive -> pe>=s means touching diag)
                    a,b=find(lab),find(pl)
                    if a!=b: parent[max(a,b)]=min(a,b)
            cur.append((s,e,lab)); runs_all.append((y,s,e,lab))
        prev=cur
    boxes={}
    for y,s,e,l in runs_all:
        r=find(l)
        b=boxes.get(r)
        if b is None: boxes[r]=[s,y,e-1,y,e-s]
        else:
            b[0]=min(b[0],s);b[1]=min(b[1],y);b[2]=max(b[2],e-1);b[3]=max(b[3],y);b[4]+=e-s
    return [(b[0],b[1],b[2]-b[0]+1,b[3]-b[1]+1,b[4]) for b in boxes.values()]
if __name__=='__main__':
    im=np.array(Image.open(sys.argv[1]).convert('RGBA'))
    thr=int(sys.argv[2]) if len(sys.argv)>2 else 128
    minarea=int(sys.argv[3]) if len(sys.argv)>3 else 400
    m=im[:,:,3]>=thr
    bs=[b for b in label(m) if b[4]>=minarea]
    bs.sort(key=lambda b:(b[1]//40,b[0]))
    for b in bs: print("x=%d y=%d w=%d h=%d area=%d"%b)
