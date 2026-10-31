# fontcmp.py img x,y,w,h thr text capH out.png [light]
import sys, numpy as np
from PIL import Image, ImageFont, ImageDraw
img=Image.open(sys.argv[1]).convert('RGB')
x,y,w,h=map(int,sys.argv[2].split(',')); thr=float(sys.argv[3]); text=sys.argv[4]; out=sys.argv[6]
light=len(sys.argv)>7 and sys.argv[7]=='light'
crop=np.asarray(img.crop((x,y,x+w,y+h))).astype(float)@[0.299,0.587,0.114]
m=(crop>thr) if light else (crop<thr)
ys,xs=np.nonzero(m); m=m[ys.min():ys.max()+1, xs.min():xs.max()+1]
fonts={'MerriweatherBold':'art/ui/fonts/Merriweather-Bold.woff','MerriweatherRegular':'art/ui/fonts/Merriweather-Regular.woff',
'DejaVuSerifBold':'/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf','LiberationSerifBold':'/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
'CrimsonProBold':'/mnt/skills/examples/canvas-design/canvas-fonts/CrimsonPro-Bold.ttf','IBMPlexSerifBold':'/mnt/skills/examples/canvas-design/canvas-fonts/IBMPlexSerif-Bold.ttf'}
rows=[]
H,W=m.shape
import os
for name,path in fonts.items():
    if not os.path.exists(path): continue
    best=None
    for size in np.arange(10,120,0.5):
        f=ImageFont.truetype(path,size); bb=f.getbbox(text)
        if bb[3]-bb[1]>=H: break
    # render at size where bbox height == H
    f=ImageFont.truetype(path,size); bb=f.getbbox(text)
    im=Image.new('L',(bb[2]+4,bb[3]+4),0); ImageDraw.Draw(im).text((0,0),text,font=f,fill=255)
    r=np.asarray(im)>110; ys2,xs2=np.nonzero(r); r=r[ys2.min():ys2.max()+1,xs2.min():xs2.max()+1]
    rw=r.shape[1]
    # resize render to mock size for IoU
    rr=np.asarray(Image.fromarray((r*255).astype(np.uint8)).resize((W,H),Image.BILINEAR))>127
    iou=(rr&m).sum()/max(1,(rr|m).sum())
    ink_mock=m.mean(); ink_r=rr.mean()
    rows.append((name,size,rw,W,iou,ink_mock,ink_r))
    print(f'{name:22s} size@H={size:5.1f} natural width {rw} vs mock {W} ({rw/W:.3f}) IoU={iou:.3f} ink {ink_r:.3f} vs mock {ink_mock:.3f}')
    if name=='MerriweatherBold' or name=='MerriweatherRegular':
        vis=np.zeros((H,W,3),np.uint8); vis[m]=[255,0,0]; vis[rr]=vis[rr]+np.array([0,255,0],np.uint8)
        Image.fromarray(vis).resize((W*3,H*3),Image.NEAREST).save(out.replace('.png',f'_{name}.png'))
