import numpy as np
from m import img
A=img('01_hud').astype(float)
P={'coins paper':(1395,95,25,12),'gems paper':(1525,95,18,12),'plate paper':(300,92,40,6),'card XP track':(325,111,28,5),
'card XP fill':(205,112,60,4),'gear ink':(1585,85,6,6),'gem blue':(1472,92,6,6),'coin gold':(1338,96,8,6),'tile paper':(140,350,8,20),'portrait bg':(100,72,12,10),'pill outline':(1380,114,30,2)}
for n in ('05_play','04_party'):
    B=img(n).astype(float); xs=[];ys=[]
    for k,(x,y,w,h) in P.items():
        a=np.median(A[y:y+h,x:x+w].reshape(-1,3),0); b=np.median(B[y:y+h,x:x+w].reshape(-1,3),0); xs.append(a); ys.append(b)
    xs=np.array(xs); ys=np.array(ys)
    out=[]
    for c in range(3):
        k,b0=np.polyfit(xs[:,c],ys[:,c],1); res=ys[:,c]-(k*xs[:,c]+b0)
        out.append((k,b0,np.abs(res).max()))
    k=np.mean([o[0] for o in out]); alpha=1-k
    col=[o[1]/(1-o[0]) for o in out]
    print(n,'per-channel k',['%.3f'%o[0] for o in out],'offset',['%.1f'%o[1] for o in out],'max resid',['%.1f'%o[2] for o in out])
    print('   overlay alpha %.3f (BackgroundTransparency %.2f), overlay colour RGB %s'%(alpha,1-alpha,[round(c) for c in col]))
