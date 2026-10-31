import sys
from m import *
from tsize import solve, FB, FR
def run(n,items):
    for (x,y,w,h),text,mode in items:
        L=lum(img(n)[y:y+h,x:x+w])
        if mode=='dark': hi=np.percentile(L,90); lo=np.percentile(L,1)
        else: hi=np.percentile(L,99); lo=np.percentile(L,10)
        thr=(hi+lo)/2
        (bx,by,bw,bh),c=ink(n,x,y,w,h,thr,mode)
        sz,hh,ww=solve(text,bh)
        szr,_,wwr=solve(text,bh,FR)
        print('%-18s ink %4d,%3d,%3d,%2d  TextSize(Bold) %4.1f  predW %5.1f vs %3d (%+.0f%%) | Regular predW %5.1f  ink %s'%(text[:18],bx,by,bw,bh,sz,ww,bw,100*(bw-ww)/ww,wwr,c))
