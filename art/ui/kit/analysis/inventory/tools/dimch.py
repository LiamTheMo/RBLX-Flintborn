import numpy as np
from PIL import Image
L='art/reference/ui/lobby/'
h=np.asarray(Image.open(L+'01_hud.png').convert('RGB')).astype(float)
# background-only regions outside windows and HUD in both
regs=[(0,160,240,140),(0,560,240,200),(1460,560,200,200),(0,0,600,60),(700,0,600,60)]
for name in ['02_inventory','03_settings']:
    m=np.asarray(Image.open(L+name+'.png').convert('RGB')).astype(float)
    for ch in range(3):
        a=np.concatenate([h[y:y+hh,x:x+w,ch].ravel() for x,y,w,hh in regs]); b=np.concatenate([m[y:y+hh,x:x+w,ch].ravel() for x,y,w,hh in regs])
        A=np.stack([a,np.ones(a.size)],1); (k,c),_,_,_=np.linalg.lstsq(A,b,rcond=None)
        print(name,'RGB'[ch],f'k={k:.3f} c={c:.1f} alpha={1-k:.3f} overlay={c/(1-k):.0f}')
