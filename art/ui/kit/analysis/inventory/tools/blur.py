# blur.py -> is the background behind the 02/03 windows blurred? Fits 02/03 = k*blur(01, sigma) + c on
# background-only regions for several Gaussian sigmas; the lowest RMS marks the blur. Run from repo root.
import numpy as np
from PIL import Image, ImageFilter
L = 'art/reference/ui/lobby/'
H = Image.open(L + '01_hud.png').convert('RGB')
regs = {'right_bg': (1440, 520, 220, 120), 'bottom_left': (20, 620, 200, 120),
        'bottom_right': (1180, 850, 480, 85), 'top_mid': (700, 20, 500, 110)}
blurred = {s: np.asarray(H.filter(ImageFilter.GaussianBlur(s)) if s else H).astype(float)
           for s in [0, 1, 2, 3, 4, 6, 8, 10, 12, 16]}
for name in ['02_inventory', '03_settings']:
    m = np.asarray(Image.open(L + name + '.png').convert('RGB')).astype(float)
    for rn, (x, y, w, hh) in regs.items():
        b = m[y:y + hh, x:x + w].ravel()
        res = []
        for s, img in blurred.items():
            a = img[y:y + hh, x:x + w].ravel()
            A = np.stack([a, np.ones(a.size)], 1)
            sol, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
            res.append((np.sqrt(np.mean((A @ sol - b) ** 2)), s, sol[0], sol[1]))
        r, s, k, c = min(res)
        print(name, rn, f'best sigma={s} rms={r:.1f} k={k:.3f} c={c:.1f}',
              ' | '.join(f'{q[1]}:{q[0]:.1f}' for q in res))
