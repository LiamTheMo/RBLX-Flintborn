#!/usr/bin/env python3
"""Paint the play-world island as a parchment map (Journal and world Map screens).

Samples the island with the game's own terrain functions (island_dump.luau run
through the capture harness: BiomeCatalog zones, IslandLayout heights, water,
rivers and pools), then paints it in the style of the Journal reference
(07_journal): turquoise shallows fading to deep water and into the paper at the
edges, a foam line and an inked coast, sand beaches, zone colours shaded by the
hills, tree stamps in the forests and rock stamps on the heights.

    python3 art/ui/map/render_island.py            # -> art/ui/map/island.png

The image covers MAP_SPAN studs centred on the island, north (-Z) up; the
Journal and Map screens place pins with the same span (src/client/Hud/IslandMap
.luau). Rerun it when the island layout changes. Needs `luau` on PATH, numpy and
Pillow. Deterministic.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "art" / "ui" / "capture"))
sys.path.insert(0, str(ROOT / "art" / "ui"))
import capture  # noqa: E402
from slice_parchment import box_blur  # noqa: E402

CELLS = 400
MAP_SPAN = 4400
SIZE = 1000
OUT = HERE / "island.png"

PAPER = np.array([238, 214, 170]) / 255
DEEP = np.array([46, 128, 178]) / 255
SHALLOW = np.array([98, 198, 204]) / 255
LAKE = np.array([80, 178, 200]) / 255
FOAM = np.array([236, 246, 238]) / 255
SAND = np.array([232, 212, 160]) / 255
INK = np.array([70, 44, 26]) / 255
ROCK = np.array([128, 122, 116]) / 255

# Zone colours nudged toward the reference's warm painted greens.
ZONE_TINT = {
    "Rimlands": (156, 182, 92),
    "PinewoodWilds": (86, 136, 66),
    "MosswickForest": (100, 150, 70),
    "EmberhollowCaves": (150, 112, 86),
    "FrostpeakRidge": (214, 220, 226),
    "FallenTemple": (92, 140, 72),
    "Timberwatch": (118, 146, 76),
    "Riverlands": (140, 184, 92),
    "CraterLake": (128, 124, 116),
    "ShatteredKeep": (140, 132, 136),
}
FORESTS = {"PinewoodWilds": 0.55, "MosswickForest": 0.6, "FallenTemple": 0.5, "Timberwatch": 0.45,
           "Riverlands": 0.18, "Rimlands": 0.08, "EmberhollowCaves": 0.12}
ROCKY = {"FrostpeakRidge": 0.08, "EmberhollowCaves": 0.06, "CraterLake": 0.05, "ShatteredKeep": 0.04}


def sample():
    luau = shutil.which("luau")
    if luau is None:
        sys.exit("luau CLI not found on PATH (cargo install luau-cli)")
    source = capture.bundle(HERE / "island_dump.luau", {})
    source = "__mapCells = %d\n__mapSpan = %d\n" % (CELLS, MAP_SPAN) + source
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "island.luau"
        path.write_text(source, encoding="utf-8")
        result = subprocess.run([luau, str(path)], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(result.stderr)
    data = json.loads(result.stdout.split("@@MAP@@")[1].split("@@END@@")[0])
    n = int(data["n"])
    grid = lambda key: np.array(data[key], np.float32).reshape(n, n)  # noqa: E731
    return data, grid("zones").astype(int), grid("dry") > 0.5, grid("heights"), grid("water")


def up(field, order=Image.BILINEAR):
    return np.asarray(Image.fromarray(field.astype(np.float32)).resize((SIZE, SIZE), order))


def blur(x, r):
    """About a Gaussian of radius r: three box blurs."""
    x = x.astype(np.float32)
    k = max(1, int(round(r * 0.8)))
    for _ in range(3):
        x = box_blur(x, k)
    return x


def distance(mask, steps):
    """Approximate distance (px) from `mask`, out to `steps` px."""
    dist = np.full(mask.shape, float(steps), np.float32)
    grown = mask.copy()
    dist[grown] = 0
    for i in range(1, steps + 1):
        g = grown.copy()
        g[1:] |= grown[:-1]
        g[:-1] |= grown[1:]
        g[:, 1:] |= grown[:, :-1]
        g[:, :-1] |= grown[:, 1:]
        dist[g & ~grown] = i
        grown = g
    return dist


def stamp(img, alpha_img, cx, cy, r, body, shadow=True):
    """A small painted tree or rock: shadow, body disc, lighter top-left."""
    y0, y1 = int(max(0, cy - r - 3)), int(min(SIZE, cy + r + 4))
    x0, x1 = int(max(0, cx - r - 3)), int(min(SIZE, cx + r + 4))
    ys, xs = np.mgrid[y0:y1, x0:x1]
    if shadow:
        d = np.sqrt((xs - cx - r * 0.35) ** 2 + (ys - cy - r * 0.45) ** 2)
        a = np.clip(r - d + 0.5, 0, 1) * 0.35
        img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - a[..., None]) + INK * a[..., None]
    d = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    a = np.clip(r - d + 0.5, 0, 1)
    light = np.clip(1 - np.sqrt((xs - cx + r * 0.35) ** 2 + (ys - cy + r * 0.35) ** 2) / (r * 1.1), 0, 1)
    color = body[None, None, :] * (0.85 + 0.35 * light[..., None])
    edge = np.clip(d - (r - 1.2), 0, 1)[..., None] * 0.6
    color = color * (1 - edge) + INK * edge
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - a[..., None]) + color * a[..., None]


def main():
    data, zones, dry, heights, water = sample()
    ids = [c[0] for c in data["colors"]]
    tint = np.zeros((len(ids) + 1, 3), np.float32)
    for i, zone in enumerate(ids):
        tint[i + 1] = np.array(ZONE_TINT.get(zone, data["colors"][i][1:])) / 255

    land = up(dry.astype(np.float32)) > 0.5
    sea_mask = up((zones == 0).astype(np.float32)) > 0.5
    inland_water = ~land & ~sea_mask
    h = up(heights)

    # Zone colours, blended softly across borders (land only).
    zc = tint[zones]
    zc_big = np.stack([up(zc[..., i]) for i in range(3)], -1)
    soft = blur(zc_big * land[..., None], 6) / np.maximum(blur(land.astype(np.float32), 6), 1e-3)[..., None]
    color = soft.copy()

    # Heights: rock toward the tops, hill shading from the north-west.
    rockiness = np.clip((h - 160) / 260, 0, 1)[..., None]
    color = color * (1 - rockiness * 0.7) + ROCK * rockiness * 0.7
    gy, gx = np.gradient(blur(h, 2))
    shade = np.clip(1 + (-gx - gy) * 0.035, 0.72, 1.22)
    color = np.clip(color * shade[..., None], 0, 1)
    # Painted ground: broad light and dark patches plus fine speckle.
    rng = np.random.default_rng(7)
    patches = blur(rng.random((SIZE, SIZE)).astype(np.float32), 30)
    patches = (patches - patches.mean()) / (patches.std() + 1e-6)
    speckle = blur(rng.random((SIZE, SIZE)).astype(np.float32), 1.5) - 0.5
    color = np.clip(color * (1 + patches[..., None] * 0.06 + speckle[..., None] * 0.1), 0, 1)

    # Beaches: sand on low land next to the sea.
    to_sea = distance(sea_mask, 14)
    sand = np.clip((14 - to_sea) / 8, 0, 1) * np.clip((40 - h) / 30, 0, 1)
    color = color * (1 - sand[..., None]) + SAND * sand[..., None]

    # Sea: shallow near the coast, deep offshore, paper at the edges.
    to_land = distance(land | inland_water, 70)
    depth = np.clip(to_land / 70, 0, 1)[..., None]
    sea = SHALLOW * (1 - depth) + DEEP * depth
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    edge = np.minimum(np.minimum(xx, SIZE - 1 - xx), np.minimum(yy, SIZE - 1 - yy)) / 34.0
    wobble = blur(rng.random((SIZE, SIZE)).astype(np.float32), 18)
    wobble = (wobble - wobble.mean()) / (wobble.std() + 1e-6)
    fade = np.clip(edge - 0.3 + wobble * 0.14, 0, 1)[..., None]
    sea = sea * fade + PAPER * (1 - fade)
    foam = np.clip(1 - np.abs(to_land - 3) / 2.2, 0, 1)[..., None] * 0.8
    sea = sea * (1 - foam) + FOAM * foam
    color = np.where(sea_mask[..., None], sea, color)

    # Lake, river and pools.
    lake_edge = np.clip(1 - distance(land, 4) / 4, 0, 1)[..., None] * 0.35
    lake = LAKE * (1 - lake_edge) + np.array([60, 140, 160]) / 255 * lake_edge
    color = np.where(inland_water[..., None], lake, color)

    # Trees in clumps (a low-frequency density field) and rocks on the heights,
    # scattered with a fixed seed.
    zone_big = np.asarray(Image.fromarray(zones.astype(np.uint8)).resize((SIZE, SIZE), Image.NEAREST))
    near_water = distance(~land, 4) < 4
    clumps = blur(rng.random((SIZE, SIZE)).astype(np.float32), 22)
    clumps = np.clip((clumps - clumps.mean()) / (clumps.std() + 1e-6) * 0.5 + 0.5, 0, 1)
    greens = [np.array(c) / 255 for c in ((46, 96, 46), (58, 112, 50), (70, 124, 54), (40, 84, 44))]
    spots = []
    for _ in range(60000):
        x, y = rng.random() * SIZE, rng.random() * SIZE
        ix, iy = int(x), int(y)
        if not land[iy, ix] or near_water[iy, ix] or sand[iy, ix] > 0.2 or zone_big[iy, ix] == 0:
            continue
        zone = ids[zone_big[iy, ix] - 1]
        rock = rockiness[iy, ix, 0]
        forest = FORESTS.get(zone, 0) * (1 - rock) * clumps[iy, ix] ** 1.5
        roll = rng.random()
        if roll < forest * 0.5:
            spots.append((y, x, "tree"))
        elif roll > 1 - ROCKY.get(zone, 0.004) * (0.3 + rock) * 0.25:
            spots.append((y, x, "rock"))
    # Drawn top to bottom so nearer (lower) canopies overlap the ones behind.
    for y, x, kind in sorted(spots):
        if kind == "tree":
            r = 4.2 + rng.random() * 2.0
            body = greens[int(rng.random() * len(greens))]
            stamp(color, None, x, y, r, body)
            stamp(color, None, x - r * 0.45, y - r * 0.55, r * 0.55, np.clip(body * 1.18, 0, 1), shadow=False)
        else:
            stamp(color, None, x, y, 3 + rng.random() * 2.6, ROCK * (0.85 + rng.random() * 0.25))

    # Inked coast and shorelines.
    coast = (distance(land, 2) > 0.5) & (distance(land, 2) <= 1.5)
    ink_a = blur(coast.astype(np.float32), 0.7)[..., None] * 0.75
    color = color * (1 - ink_a) + INK * ink_a

    # Paper grain over everything.
    grain = blur(rng.random((SIZE, SIZE)).astype(np.float32), 1.2) - 0.5
    color = np.clip(color * (1 + grain[..., None] * 0.12), 0, 1)

    Image.fromarray((color * 255 + 0.5).astype(np.uint8), "RGB").save(OUT)
    print("wrote", OUT.relative_to(ROOT), f"({SIZE}x{SIZE}, {MAP_SPAN} studs)")


if __name__ == "__main__":
    main()
