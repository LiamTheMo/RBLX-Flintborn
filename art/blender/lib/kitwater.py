"""Kit water texture: the tileable stylised cartoon water shared by the Roblox
export and the Blender preview, so kit renders show what Roblox shows.

- scripts/export_kit_roblox.py writes it as water/<key>.png for every water key.
- flintkit.material() samples it for kit water keys (KIT_PALETTE and sheet-
  prefixed module keys), cached as assets/kit/water_preview/<key>.png.

The texture is the key's colour, gently mottled, with a bold warped caustic net
of lighter lines, a finer fainter net and a few soft foam specks, painted with
numpy on the unit torus so opposite edges match. It is deterministic for a
(hex, key) pair: the seed is the sum of the key's character codes. One tile
covers TILE_STUDS x TILE_STUDS studs (the exporter's planar / box UVs).
"""

import math
import os

import numpy as np

SIZE = 512          # texture size in pixels
TILE_STUDS = 16.0   # studs per texture tile
VERSION = 1         # bump when the painter changes, so cached previews are repainted


def seed_of(key):
    """The painter's seed for a water key."""
    return sum(map(ord, key))


def _wrap(d):
    return (d + 0.5) % 1.0 - 0.5


def pixels(hexcol, key=None, seed=None, size=SIZE):
    """Tileable stylised water for `hexcol` (sRGB floats, size x size x 3, top row
    first), seeded by `seed` or else by the key (seed_of(key))."""
    if seed is None:
        seed = seed_of(key)
    rng = np.random.default_rng(seed)
    base = np.array([int(hexcol.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)])
    light = base + (1.0 - base) * 0.5
    y, x = np.mgrid[0:size, 0:size].astype(np.float64)
    x, y = (x + 0.5) / size, (y + 0.5) / size
    tau = 2 * math.pi
    mott = np.zeros((size, size))
    for _ in range(4):
        kx, ky = rng.integers(-3, 4, 2)
        if kx == 0 and ky == 0:
            kx = 1
        mott += math.sqrt(0.25) * np.sin(tau * (kx * x + ky * y) + rng.uniform(0, tau))
    img = base[None, None, :] * (1.0 + 0.05 * np.clip(mott, -1.5, 1.5))[..., None]

    def caustics(count, width, warp, strength):
        nonlocal img
        wx = x + warp * np.sin(tau * (2 * y + rng.uniform(0, 1)))
        wy = y + warp * np.sin(tau * (2 * x + rng.uniform(0, 1)))
        g = int(math.ceil(math.sqrt(count)))  # jittered grid: even cells, no clumps
        pts = [((i + rng.uniform(0.15, 0.85)) / g, (j + rng.uniform(0.15, 0.85)) / g)
               for i in range(g) for j in range(g)]
        d = np.stack([np.hypot(_wrap(wx - px), _wrap(wy - py)) for px, py in pts])
        f = np.partition(d, 1, axis=0)
        edge = f[1] - f[0]  # ~2x the distance to the nearest cell border
        line = np.clip((width - edge) * size / 1.5, 0.0, 1.0)  # crisp ~1.5 px edge
        img = img + (light[None, None, :] - img) * (line * strength)[..., None]

    caustics(16, 0.016, 0.02, 0.85)
    caustics(49, 0.007, 0.012, 0.35)
    for _ in range(int(rng.integers(6, 10))):  # foam specks
        cx, cy, rad = rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0.006, 0.014)
        dd = np.hypot(_wrap(x - cx), _wrap(y - cy)) / rad
        speck = np.clip((1.0 - dd) * rad * size / 2.0, 0.0, 1.0) * 0.85
        img = img + (1.0 - img) * speck[..., None]
    return np.clip(img, 0.0, 1.0)


def write_png(path, hexcol, key, size=SIZE):
    """Paint the key's texture and save it as an RGB PNG at `path` (written to a
    temporary file first and renamed, so a reader never sees half a file)."""
    import bpy

    px = pixels(hexcol, key, size=size)
    rgba = np.ones((size, size, 4), dtype=np.float32)
    rgba[..., :3] = px[::-1]  # Blender images start at the bottom row
    tmp = f"{path}.{os.getpid()}.tmp.png"
    image = bpy.data.images.new("KitWater", size, size, alpha=False)
    try:
        image.colorspace_settings.name = "Non-Color"  # values above are already sRGB
        image.pixels.foreach_set(rgba.ravel())
        image.filepath_raw = tmp
        image.file_format = "PNG"
        image.save()
    finally:
        bpy.data.images.remove(image)
    try:
        os.replace(tmp, path)
    except OSError:  # Windows: another build has the file open; its copy is the same bytes
        if not os.path.exists(path):
            raise
        os.remove(tmp)
    return path


def cached_png(path, hexcol, key, size=SIZE):
    """`path`, painting it first when it is missing or was painted from another
    colour, size or painter VERSION (recorded next to it in <path>.src)."""
    stamp = path + ".src"
    want = f"{hexcol.lstrip('#').upper()} {key} {size} v{VERSION}"
    try:
        with open(stamp, encoding="utf-8") as fh:
            fresh = fh.read().strip() == want and os.path.isfile(path)
    except OSError:
        fresh = False
    if not fresh:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        write_png(path, hexcol, key, size)
        tmp = f"{stamp}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(want + "\n")
        try:
            os.replace(tmp, stamp)
        except OSError:  # another build is reading it; it will repaint next time at worst
            os.remove(tmp)
    return path
