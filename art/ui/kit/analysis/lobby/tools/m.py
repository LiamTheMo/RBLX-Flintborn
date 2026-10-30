import sys, numpy as np
from PIL import Image
import os
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','..','..','reference','ui','lobby')+os.sep
_c={}
def img(n):
    if n not in _c: _c[n]=np.array(Image.open(R+n+'.png').convert('RGB')).astype(int)
    return _c[n]
def lum(p): return (0.299*p[...,0]+0.587*p[...,1]+0.114*p[...,2])
def cls(p):
    r,g,b=p[...,0],p[...,1],p[...,2]; L=lum(p)
    c=np.full(L.shape,'.',dtype='<U1')
    c[(r>205)&(g>170)&(b>110)&(r-b>40)]='P'   # parchment
    c[L<95]='d'
    c[L<60]='D'
    return c
def runs(n,row=None,col=None,a=0,b=None,show=True):
    im=img(n)
    line=im[row,a:b] if row is not None else im[a:b,col]
    c=cls(line); out=[]; s=0
    for i in range(1,len(c)+1):
        if i==len(c) or c[i]!=c[s]:
            out.append((a+s,a+i-1,c[s],tuple(np.median(line[s:i],axis=0).astype(int))))
            s=i
    if show:
        print(('row %d'%row) if row is not None else ('col %d'%col), ' '.join('%d-%d%s'%(x0,x1,k) for x0,x1,k,_ in out))
    return out
def px(n,row=None,col=None,a=0,b=None):
    im=img(n)
    line=im[row,a:b] if row is not None else im[a:b,col]
    print(('row %d'%row) if row is not None else ('col %d'%col))
    print(' '.join('%d:%02x%02x%02x'%(a+i,*p) for i,p in enumerate(line)))
def med(n,x,y,w,h):
    im=img(n); p=np.median(im[y:y+h,x:x+w].reshape(-1,3),axis=0).astype(int)
    return '#%02X%02X%02X'%tuple(p)
def outer(n,x0,y0,x1,y1,maxw=7,thr=110,fr=(0.3,0.5,0.7)):
    """parchment bbox inclusive -> outward dark extents per side, sampled at fractions"""
    im=img(n); L=lum(im)
    res={}
    for side in 'LRTB':
        vals=[]
        for f in fr:
            if side in 'LR':
                y=int(y0+(y1-y0)*f); 
                if side=='L':
                    x=x0-1; k=0
                    while x>=0 and k<12 and L[y,x]>=thr: x-=1;k+=1   # light rim
                    e=x
                    while x>=0 and L[y,x]<thr and e-x<maxw: x-=1
                    vals.append(x+1)
                else:
                    x=x1+1;k=0
                    while k<12 and L[y,x]>=thr: x+=1;k+=1
                    e=x
                    while L[y,x]<thr and x-e<maxw: x+=1
                    vals.append(x-1)
            else:
                x=int(x0+(x1-x0)*f)
                if side=='T':
                    y=y0-1;k=0
                    while k<12 and L[y,x]>=thr: y-=1;k+=1
                    e=y
                    while L[y,x]<thr and e-y<maxw: y-=1
                    vals.append(y+1)
                else:
                    y=y1+1;k=0
                    while k<12 and L[y,x]>=thr: y+=1;k+=1
                    e=y
                    while y<L.shape[0] and L[y,x]<thr and y-e<maxw: y+=1
                    vals.append(y-1)
        res[side]=vals
    return res
def ink(n,x,y,w,h,thr=100,mode='dark',minpix=1):
    im=img(n)[y:y+h,x:x+w]; L=lum(im)
    m = (L<thr) if mode=='dark' else (L>thr)
    ys=np.where(m.sum(1)>=minpix)[0]; xs=np.where(m.sum(0)>=minpix)[0]
    if len(ys)==0: return None
    box=(x+xs[0],y+ys[0],xs[-1]-xs[0]+1,ys[-1]-ys[0]+1)
    col=np.median(im[m].reshape(-1,3),axis=0).astype(int) if m.sum() else None
    # darkest-quartile colour for ink core
    Lm=L[m]; core=im[m][Lm<=np.percentile(Lm,30)]
    cc=np.median(core,axis=0).astype(int)
    return box,'#%02X%02X%02X'%tuple(cc)
def rowprof(n,x,y,w,h,thr=100,mode='dark'):
    im=img(n)[y:y+h,x:x+w]; L=lum(im); m=(L<thr) if mode=='dark' else (L>thr)
    for i,r in enumerate(m.sum(1)): print(y+i, r)
def colgroups(n,x,y,w,h,thr=100,gap=3,mode='dark'):
    im=img(n)[y:y+h,x:x+w]; L=lum(im); m=(L<thr) if mode=='dark' else (L>thr)
    cs=m.sum(0)>0; out=[];s=None;last=None
    for i,v in enumerate(cs):
        if v:
            if s is None: s=i
            elif i-last>gap: out.append((x+s,x+last)); s=i
            last=i
    if s is not None: out.append((x+s,x+last))
    return out
def lprof(n,row=None,col=None,a=0,b=None):
    im=img(n); line=im[row,a:b] if row is not None else im[a:b,col]
    L=lum(line).astype(int)
    print(('row %d'%row) if row is not None else ('col %d'%col), ' '.join('%d:%d'%(a+i,v) for i,v in enumerate(L)))
def march(n,x,y,dx,dy,thr=75,maxs=40):
    L=lum(img(n)); k=0
    while k<maxs and L[y,x]>=thr: x+=dx;y+=dy;k+=1
    return x if dx else y
def box_from_inside(n,cx,cy,w2,h2,thr=75,fr=(0.3,0.5,0.7),inset=6):
    """cx,cy centre; w2,h2 approx half sizes; march outward from inset points near each edge"""
    out={}
    out['L']=[march(n,cx-w2+inset,int(cy-h2+2*h2*f),-1,0,thr) for f in fr]
    out['R']=[march(n,cx+w2-inset,int(cy-h2+2*h2*f),1,0,thr) for f in fr]
    out['T']=[march(n,int(cx-w2+2*w2*f),cy-h2+inset,0,-1,thr) for f in fr]
    out['B']=[march(n,int(cx-w2+2*w2*f),cy+h2-inset,0,1,thr) for f in fr]
    return out
def flood(n,sx,sy,tol=40,win=200,ref=None):
    from collections import deque
    im=img(n); H,W,_=im.shape
    x0=max(0,sx-win);x1=min(W,sx+win);y0=max(0,sy-win);y1=min(H,sy+win)
    sub=im[y0:y1,x0:x1].astype(float)
    c=np.median(im[sy-1:sy+2,sx-1:sx+2].reshape(-1,3),0) if ref is None else np.array(ref,float)
    ok=np.sqrt(((sub-c)**2).sum(2))<tol
    seen=np.zeros_like(ok); q=deque([(sy-y0,sx-x0)]); seen[sy-y0,sx-x0]=1
    while q:
        y,x=q.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            yy,xx=y+dy,x+dx
            if 0<=yy<ok.shape[0] and 0<=xx<ok.shape[1] and ok[yy,xx] and not seen[yy,xx]:
                seen[yy,xx]=1;q.append((yy,xx))
    ys,xs=np.where(seen)
    med=np.median(sub[seen.astype(bool)],0).astype(int)
    return (x0+xs.min(),y0+ys.min(),xs.max()-xs.min()+1,ys.max()-ys.min()+1), '#%02X%02X%02X'%tuple(med), int(seen.sum())
def text(n,x,y,w,h,thr=100,mode='dark',label='',cap_from_first=True,gap=1):
    r=ink(n,x,y,w,h,thr,mode)
    if r is None: print(label,'NO INK'); return
    (bx,by,bw,bh),c=r
    gs=colgroups(n,bx,by,bw,bh,thr,gap=gap,mode=mode)
    g0=gs[0]
    fb=ink(n,g0[0],by,g0[1]-g0[0]+1,bh,thr,mode)[0]
    cap=fb[3]
    print('%-22s ink x=%d y=%d w=%d h=%d | first glyph y=%d..%d cap=%d -> TextSize %.1f | ink %s'%(label,bx,by,bw,bh,fb[1],fb[1]+fb[3]-1,cap,cap/0.743,c))
    return (bx,by,bw,bh),cap,c
def T(n,x,y,w,h,label='',mode='dark',gap=1):
    L=lum(img(n)[y:y+h,x:x+w])
    if mode=='dark': hi=np.percentile(L,90); lo=np.percentile(L,1)
    else: hi=np.percentile(L,99); lo=np.percentile(L,10)
    thr=(hi+lo)/2
    r=ink(n,x,y,w,h,thr,mode)
    (bx,by,bw,bh),c=r
    gs=colgroups(n,bx,by,bw,bh,thr,gap=gap,mode=mode)
    g0=gs[0]
    fb=ink(n,g0[0],by,g0[1]-g0[0]+1,bh,thr,mode)[0]
    cap=fb[3]
    s='%-20s ink %d,%d,%d,%d  cap(first glyph) %d..%d=%dpx -> TextSize %d  ink %s  (thr %d)'%(label,bx,by,bw,bh,fb[1],fb[1]+fb[3]-1,cap,round(cap/0.743),c,thr)
    print(s); return (bx,by,bw,bh),cap,c
def leather_box(n,x,y,w,h):
    im=img(n)[y:y+h,x:x+w]; r,g,b=im[...,0],im[...,1],im[...,2]
    m=(r>110)&(r<235)&(g>40)&(g<130)&(b<90)&(r-g>55)   # orange/brown leather
    from comps import label
    bs=sorted(label(m),key=lambda t:-t[4])
    if not bs: return None
    bx,by,bw,bh,a=bs[0]
    return (x+bx,y+by,bw,bh,a)
