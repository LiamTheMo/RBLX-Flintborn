#!/usr/bin/env python3
"""Paint the play-world island as a parchment map (Journal and world Map screens).

Samples the island with the game's own terrain functions (island_dump.luau run
through the capture harness: BiomeCatalog zones, IslandLayout heights, water,
rivers and pools), then paints it in the style of the Journal reference
(07_journal): turquoise shallows fading to deep water and into the paper at the
edges, a foam line and an inked coast, sand beaches, zone colours shaded by the
hills, tree stamps in the forests and rock stamps on the heights.

    python3 art/ui/map/render_island.py   # -> art/ui/map/island.png, island_hi.png
    python3 art/ui/pack_atlas.py

The image covers MAP_SPAN studs centred on the island, north (-Z) up; the
Journal and Map screens place pins with the same span (src/client/Hud/IslandMap
.luau). Rerun it when the island layout changes. Needs `luau` on PATH, numpy and
Pillow. Deterministic.

It paints the same map at two sizes: island.png (1000 px, the pm_map_island
sprite) and island_hi.png (HI_SIZE px, for the world map, which draws it up to
2600 design px wide). Every length below is in 1000-px units and scaled with the
size, and every random draw is made on the 1000-px grid (fields upsampled), so
the large map is the same painting with more detail, not a different one. The
large painting goes into art/ui/sprites as pm_map_island__hi: 2 x 2 tiles of at
most 1024 px (Roblox's largest image) overlapping by 2 px each side of the cut,
with "hi" / "scale" / "of" in manifest.json (UiAssets.Placement).
pm_map_island.png itself (the 1000 px painting as it was cut for the parchment
UI, uploaded in atlas_island) is left as it is.
"""
import json
import re
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
import capture  # noqa: E402

CELLS = 400
MAP_SPAN = 4400
BASE = 1000
# 2 x 2 tiles of at most 1024 px that overlap by 2 px each side of the cut, so
# 2040 rather than 2048.
HI_SIZE = 2040
OUT = HERE / "island.png"
OUT_HI = HERE / "island_hi.png"
SPRITES = ROOT / "art" / "ui" / "sprites"
MANIFEST = SPRITES / "manifest.json"
SPRITE = "pm_map_island"
HI_SPRITE = SPRITE + "__hi"
TILES = 2
TILE_OVERLAP = 2
SIZE = BASE  # the size being painted (main sets it)
K = 1.0      # SIZE / BASE

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


def noise(rng, rec):
    """A random field drawn on the 1000-px grid, upsampled to SIZE. The first
    (1000-px) paint draws them and records them in `rec`; the large paint takes
    the recorded fields, so both paints use the same draws."""
    if rng is not None:
        field = rng.random((BASE, BASE)).astype(np.float32)
        rec["noise"].append(field)
    else:
        field = rec["noise"][len(rec["used"])]
        rec["used"].append(field)
    return field if SIZE == BASE else up(field)


def box_blur(x, r):
    """Separable box blur with edge clamping; x is HxW or HxWxC."""
    k = 2 * r + 1
    for axis in (0, 1):
        pad = [(0, 0)] * x.ndim
        pad[axis] = (r + 1, r)
        c = np.cumsum(np.pad(x, pad, mode="edge"), axis=axis)
        hi = np.take(c, range(k, c.shape[axis]), axis=axis)
        lo = np.take(c, range(0, c.shape[axis] - k), axis=axis)
        x = (hi - lo) / k
    return x


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
    y0, y1 = int(max(0, cy - r - 3 * K)), int(min(SIZE, cy + r + 4 * K))
    x0, x1 = int(max(0, cx - r - 3 * K)), int(min(SIZE, cx + r + 4 * K))
    ys, xs = np.mgrid[y0:y1, x0:x1]
    if shadow:
        d = np.sqrt((xs - cx - r * 0.35) ** 2 + (ys - cy - r * 0.45) ** 2)
        a = np.clip(r - d + 0.5, 0, 1) * 0.35
        img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - a[..., None]) + INK * a[..., None]
    d = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    a = np.clip(r - d + 0.5, 0, 1)
    light = np.clip(1 - np.sqrt((xs - cx + r * 0.35) ** 2 + (ys - cy + r * 0.35) ** 2) / (r * 1.1), 0, 1)
    color = body[None, None, :] * (0.85 + 0.35 * light[..., None])
    edge = np.clip(d - (r - 1.2 * K), 0, 1)[..., None] * 0.6
    color = color * (1 - edge) + INK * edge
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - a[..., None]) + color * a[..., None]


def check_span():
    """The map screens place pins with the same span (IslandMap.MAP_SPAN)."""
    source = (ROOT / "src" / "client" / "Hud" / "IslandMap.luau").read_text(encoding="utf-8")
    found = re.search(r"IslandMap\.MAP_SPAN = (\d+)", source)
    if not found or int(found.group(1)) != MAP_SPAN:
        sys.exit(f"IslandMap.MAP_SPAN must equal MAP_SPAN ({MAP_SPAN}) here")


def main():
    check_span()
    sampled = sample()
    rec = paint(sampled, BASE, OUT)
    paint(sampled, HI_SIZE, OUT_HI, rec)
    write_sprites()


def write_sprites():
    """island_hi.png as the tiles of sprite pm_map_island__hi, and the manifest
    entries that make it pm_map_island's high-resolution copy."""
    image = Image.open(OUT_HI).convert("RGBA")
    w, h = image.size
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tiles = []
    for row in range(TILES):
        for col in range(TILES):
            x0, y0 = max(0, col * w // TILES - TILE_OVERLAP), max(0, row * h // TILES - TILE_OVERLAP)
            x1, y1 = min(w, (col + 1) * w // TILES + TILE_OVERLAP), min(h, (row + 1) * h // TILES + TILE_OVERLAP)
            if max(x1 - x0, y1 - y0) > 1024:
                sys.exit(f"{HI_SPRITE} tiles must be at most 1024 px")
            tile = f"{HI_SPRITE}__{row + 1}_{col + 1}"
            image.crop((x0, y0, x1, y1)).save(SPRITES / f"{tile}.png", optimize=True)
            entry = {"file": f"{tile}.png", "w": x1 - x0, "h": y1 - y0, "slice": None}
            prev = manifest.get(tile, {})
            if prev.get("atlas") and (prev.get("w"), prev.get("h")) == (entry["w"], entry["h"]):
                entry["atlas"], entry["rect"] = prev["atlas"], prev["rect"]
            manifest[tile] = entry
            tiles.append([tile, x0, y0, x1 - x0, y1 - y0])
    base = manifest[SPRITE]
    manifest[HI_SPRITE] = {"file": None, "w": w, "h": h, "slice": None, "tiles": tiles,
                           "scale": round(w / base["w"], 4), "of": SPRITE}
    base["hi"] = HI_SPRITE
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {HI_SPRITE}: {len(tiles)} tiles (run art/ui/pack_atlas.py)")


def paint(sampled, size, out, rec=None):
    """Paints the map at `size` px. Without `rec` it makes the random draws (at
    1000 px) and returns them; with it, it repeats those draws at `size`."""
    global SIZE, K
    SIZE, K = size, size / BASE
    rng = np.random.default_rng(7) if rec is None else None
    rec = rec or {"noise": [], "stamps": []}
    rec["used"] = []
    data, zones, dry, heights, water = sampled
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
    soft = blur(zc_big * land[..., None], 6 * K) / np.maximum(blur(land.astype(np.float32), 6 * K), 1e-3)[..., None]
    color = soft.copy()

    # Heights: rock toward the tops, hill shading from the north-west.
    rockiness = np.clip((h - 160) / 260, 0, 1)[..., None]
    color = color * (1 - rockiness * 0.7) + ROCK * rockiness * 0.7
    gy, gx = np.gradient(blur(h, 2 * K))
    shade = np.clip(1 + (-gx - gy) * 0.035 * K, 0.72, 1.22)
    color = np.clip(color * shade[..., None], 0, 1)
    # Painted ground: broad light and dark patches plus fine speckle.
    patches = blur(noise(rng, rec), 30 * K)
    patches = (patches - patches.mean()) / (patches.std() + 1e-6)
    speckle = blur(noise(rng, rec), 1.5 * K) - 0.5
    color = np.clip(color * (1 + patches[..., None] * 0.06 + speckle[..., None] * 0.1), 0, 1)

    # Beaches: sand on low land next to the sea.
    to_sea = distance(sea_mask, round(14 * K)) / K
    sand = np.clip((14 - to_sea) / 8, 0, 1) * np.clip((40 - h) / 30, 0, 1)
    color = color * (1 - sand[..., None]) + SAND * sand[..., None]

    # Sea: shallow near the coast, deep offshore, paper at the edges.
    to_land = distance(land | inland_water, round(70 * K)) / K
    depth = np.clip(to_land / 70, 0, 1)[..., None]
    sea = SHALLOW * (1 - depth) + DEEP * depth
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    edge = np.minimum(np.minimum(xx, SIZE - 1 - xx), np.minimum(yy, SIZE - 1 - yy)) / (34.0 * K)
    wobble = blur(noise(rng, rec), 18 * K)
    wobble = (wobble - wobble.mean()) / (wobble.std() + 1e-6)
    fade = np.clip(edge - 0.3 + wobble * 0.14, 0, 1)[..., None]
    sea = sea * fade + PAPER * (1 - fade)
    foam = np.clip(1 - np.abs(to_land - 3) / 2.2, 0, 1)[..., None] * 0.8
    sea = sea * (1 - foam) + FOAM * foam
    color = np.where(sea_mask[..., None], sea, color)

    # Lake, river and pools.
    lake_edge = np.clip(1 - distance(land, round(4 * K)) / (4 * K), 0, 1)[..., None] * 0.35
    lake = LAKE * (1 - lake_edge) + np.array([60, 140, 160]) / 255 * lake_edge
    color = np.where(inland_water[..., None], lake, color)

    # Trees in clumps (a low-frequency density field) and rocks on the heights,
    # scattered with a fixed seed (placed on the 1000-px map, drawn at SIZE).
    clumps = blur(noise(rng, rec), 22 * K)
    if rng is not None:
        zone_big = np.asarray(Image.fromarray(zones.astype(np.uint8)).resize((SIZE, SIZE), Image.NEAREST))
        near_water = distance(~land, 4) < 4
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
                rec["stamps"].append((x, y, r, body, True))
                rec["stamps"].append((x - r * 0.45, y - r * 0.55, r * 0.55, np.clip(body * 1.18, 0, 1), False))
            else:
                rec["stamps"].append((x, y, 3 + rng.random() * 2.6, ROCK * (0.85 + rng.random() * 0.25), True))
    for x, y, r, body, shadow in rec["stamps"]:
        stamp(color, None, x * K, y * K, r * K, body, shadow=shadow)

    # Inked coast and shorelines.
    coast_d = distance(land, round(2 * K))
    coast = (coast_d > 0.5) & (coast_d <= 1.5 * K)
    ink_a = blur(coast.astype(np.float32), 0.7 * K)[..., None] * 0.75
    color = color * (1 - ink_a) + INK * ink_a

    # Paper grain over everything.
    grain = blur(noise(rng, rec), 1.2 * K) - 0.5
    color = np.clip(color * (1 + grain[..., None] * 0.12), 0, 1)

    Image.fromarray((color * 255 + 0.5).astype(np.uint8), "RGB").save(out)
    print("wrote", out.relative_to(ROOT), f"({SIZE}x{SIZE}, {MAP_SPAN} studs)")
    return rec


if __name__ == "__main__":
    main()
