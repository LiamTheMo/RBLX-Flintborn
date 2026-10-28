"""007 Coal (references/007.png): three chunky dark faceted coal chunks (a tall main chunk and two side chunks)
on three pale base rocks.

    import importlib, m007; importlib.reload(m007); m007.build()

Parts as on the sheet (5 reusable parts): Main Chunk, Side Chunk (Left), Side Chunk (Right), Base Rock (Left),
Base Rock (Center), Base Rock (Right). The hero is their union.
"""
import kit_mcp as K
import kit_models as M
import m004

NUM, TITLE, SHEET = 7, "Coal", "M007"
COAL, COAL_GREY, BASE, BASE_COOL = "m007_coal", "m007_coal_grey", "m007_base_rock", "m007_base_rock_cool"

# upright faceted chunk: wide shoulders a little above the base, a blunt faceted crown
CHUNK = [(0.0, 0.82, 7), (0.3, 1.0, 8), (0.62, 0.95, 7), (0.85, 0.7, 6), (1.0, 0.32, 4)]
BASE_RINGS = [(0.0, 0.94, 8), (0.4, 1.0, 8), (0.75, 0.74, 7), (1.0, 0.36, 4)]
# (label, x, y, w, d, h, seed, rings, material)
PIECES = (("MainChunk", 0.0, 0.7, 5.2, 4.6, 7.2, 7011, CHUNK, COAL),
          ("SideChunkLeft", -3.3, 0.1, 3.7, 3.3, 5.0, 7012, CHUNK, COAL),
          ("SideChunkRight", 3.3, -0.1, 3.5, 3.1, 4.7, 7013, CHUNK, COAL),
          ("BaseRockCenter", 0.0, -2.2, 5.0, 3.8, 2.6, 7021, BASE_RINGS, BASE),
          ("BaseRockLeft", -4.2, -1.7, 2.3, 2.1, 1.4, 7022, BASE_RINGS, BASE),
          ("BaseRockRight", 4.1, -1.8, 2.1, 1.9, 1.3, 7023, BASE_RINGS, BASE))
EXTRA = ((-2.0, -2.9, 1.5, 1.3, 0.9, 7024), (2.4, -2.8, 1.6, 1.4, 1.0, 7025), (-4.4, 0.9, 1.4, 1.3, 0.9, 7026),
         (4.4, 0.8, 1.3, 1.2, 0.8, 7027))


def palette():
    K.set_colour(COAL, "#2C2C31", rough=0.6)
    K.set_colour(COAL_GREY, "#3B3B42", rough=0.6)
    K.set_colour(BASE, "#958682", rough=0.92)
    K.set_colour(BASE_COOL, "#8C8382", rough=0.92)


def piece(a, label, at_origin=False):
    _, x, y, w, d, h, seed, rings, mat = next(p for p in PIECES if p[0] == label)
    vs = K.hull_rock(a, (w, d, h), loc=(0, 0, 0) if at_origin else (x, y, 0), seed=seed, mat=mat, rings=rings,
                     jitter=0.06, rot=0.4 * (seed % 7), keep_bottom=True)
    if mat == COAL:
        K.blend(a, vs, COAL, COAL_GREY, K.noise_field(scale=0.3, seed=seed), level=0.1, width=0.4, steps=1)
    else:
        K.blend(a, vs, BASE, BASE_COOL, K.noise_field(scale=0.3, seed=seed), level=0.15, width=0.4, steps=1)
    K.texture(a, vs, amp=0.04, scale=0.4, jitter=0.04, seed=seed)
    return vs


def extras(a):
    for x, y, w, d, h, seed in EXTRA:
        vs = K.hull_rock(a, (w, d, h), loc=(x, y, 0), seed=seed, mat=BASE, rings=BASE_RINGS, jitter=0.06,
                         rot=0.5 * (seed % 5), keep_bottom=True)
        K.texture(a, vs, amp=0.04, scale=0.5, jitter=0.04, seed=seed)


def hero(a):
    for p in PIECES:
        piece(a, p[0])
    extras(a)


NOTES = {
    "Coal": "coal resource: a tall dark faceted main chunk with a side chunk each side, on a centre base rock and "
            "smaller pale base rocks round the foot; broad flat faces; one closed mesh",
    "CoalMainChunk": "Main Chunk: tall dark faceted coal chunk",
    "CoalSideChunkLeft": "Side Chunk (Left): dark faceted coal chunk",
    "CoalSideChunkRight": "Side Chunk (Right): dark faceted coal chunk",
    "CoalBaseRockCenter": "Base Rock (Center): broad pale faceted rock",
    "CoalBaseRockLeft": "Base Rock (Left): small pale faceted rock",
    "CoalBaseRockRight": "Base Rock (Right): small pale faceted rock",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Coal", "hero", hero, 4000, "hull")]
    specs += [(f"Coal{p[0]}", "part", (lambda L: lambda a: piece(a, L, True))(p[0]), 1000, "hull") for p in PIECES]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES.get(n.replace("M007", ""), ""), budget=b, collision=c)
            for n, r, fn, b, c in specs]
    audits = []
    for o in objs:
        if o.get("kit_role") == "hero":
            M.union_loose(o)
            m004.floor_cut(o)
        audits.append(M.finish(o, union=False))
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, parts = objs[0], objs[1:]
        saved = M.explode(parts, {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            for o, p in zip(parts, PIECES):
                lift = 4.0 if "Chunk" in p[0] else 0.0
                o.location = (hx + 40 + p[1] * 1.25, hy + p[2], lift)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": (parts, -12, 12)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
