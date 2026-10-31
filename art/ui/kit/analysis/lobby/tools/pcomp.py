import sys
from m import *
from comps import label
n=sys.argv[1]; minarea=int(sys.argv[2]) if len(sys.argv)>2 else 500
im=img(n); c=cls(im)
m=(c=='P')
bs=[b for b in label(m) if b[4]>=minarea]
bs.sort(key=lambda b:(b[1]//30,b[0]))
for b in bs: print("x=%d y=%d w=%d h=%d area=%d  -> x2=%d y2=%d"%(b+(b[0]+b[2]-1,b[1]+b[3]-1)))
