import numpy as np
from PIL import Image
L='art/reference/ui/lobby/'
h=np.asarray(Image.open(L+'01_hud.png').convert('RGB')).astype(float)
T=80
for name,win in [('02_inventory',(243,150,1190,655)),('03_settings',(287,145,1100,665))]:
    m=np.asarray(Image.open(L+name+'.png').convert('RGB')).astype(float)
    print(name,'k (x100) per 80px tile; c in brackets; -- = window/poor fit')
    ks=[]
    for ty in range(0,941-T+1,T):
        row=[]
        for tx in range(0,1672-T+1,T):
            x0,y0=tx,ty
            wx,wy,ww,wh=win
            if not (x0+T<wx or x0>wx+ww or y0+T<wy or y0>wy+wh):
                row.append('  --  ');continue
            a=h[y0:y0+T,x0:x0+T].ravel(); b=m[y0:y0+T,x0:x0+T].ravel()
            if a.std()<8: row.append('  ..  ');continue
            A=np.stack([a,np.ones(a.size)],1)
            sol,_,_,_=np.linalg.lstsq(A,b,rcond=None)
            r=np.sqrt(np.mean((A@sol-b)**2))
            if r>8: row.append('  ??  ');continue
            row.append(f'{sol[0]*100:3.0f}[{sol[1]:2.0f}]'); ks.append((tx,ty,sol[0],sol[1]))
        print(f'{ty:3d} '+' '.join(row))
    ks=np.array(ks); print('median k',np.median(ks[:,2]),'median c',np.median(ks[:,3]))
