"""Shared measuring helpers (imported by the per-screen measure scripts)."""
import numpy as np
from PIL import Image

class Img:
    def __init__(self, path):
        self.a = np.asarray(Image.open(path).convert('RGB')).astype(float)
        self.L = self.a @ [0.299, 0.587, 0.114]

    def ink(self, x, y, w, h, thr=110, light=False):
        """bbox of ink (luma < thr, or > thr if light) and its row profile."""
        L = self.L[y:y+h, x:x+w]
        m = L > thr if light else L < thr
        ys, xs = np.nonzero(m)
        if len(ys) == 0:
            return None
        rows = m.sum(1)
        col = self.a[y:y+h, x:x+w][m]
        core = col[(L[m] <= np.percentile(L[m], 30)) if not light else (L[m] >= np.percentile(L[m], 70))]
        return dict(x0=x+xs.min(), x1=x+xs.max(), y0=y+ys.min(), y1=y+ys.max(),
                    rows={y+i: int(c) for i, c in enumerate(rows) if c},
                    core=hexc(np.median(core, 0)))

    def box(self, x, y, w, h):
        return hexc(np.median(self.a[y:y+h, x:x+w].reshape(-1, 3), 0))

def hexc(c):
    c = np.clip(np.round(c), 0, 255).astype(int)
    return '#%02X%02X%02X' % tuple(c)

def heights(r, frac=0.35):
    """cap/x estimate from a row profile: first row, the row where density jumps (x-height top), last dense row (baseline)."""
    ys = sorted(r['rows']); vals = [r['rows'][k] for k in ys]
    mx = max(vals)
    dense = [k for k in ys if r['rows'][k] >= frac*mx]
    return dict(top=ys[0], xtop=dense[0], base=dense[-1], bottom=ys[-1])

def fmt(name, r):
    if r is None:
        return f'{name}: none'
    h = heights(r)
    return (f"{name}: ink x {r['x0']}..{r['x1']} y {r['y0']}..{r['y1']} | top {h['top']} xtop {h['xtop']} base {h['base']} "
            f"(cap~{h['base']-h['top']+1}, x~{h['base']-h['xtop']+1}) core {r['core']}")
