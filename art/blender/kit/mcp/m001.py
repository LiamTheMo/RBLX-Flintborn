"""001 Stone (references/001.png): a chunky faceted main rock with two support rocks set into its foot.

    import importlib, m001; importlib.reload(m001); m001.build()

Parts as on the sheet: Main Rock, Support Rock (Left), Support Rock (Right); the hero is their union.
"""
import math

import bmesh

import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 1, "Stone", "M001"
STONE, STONE_COOL = "m001_stone", "m001_stone_cool"

# Main rock: near-vertical lower sides bulging out a little above the base, a broad rounded shoulder and a
# broad blunt crown (about 32 hull points: broad flat faces, as the sheet's "Broad, Flat Faces").
MAIN = [(0.0, 0.88, 7), (0.25, 1.0, 8), (0.58, 0.94, 7), (0.84, 0.72, 6), (1.0, 0.36, 4)]
SUPPORT = [(0.0, 0.92, 6), (0.4, 1.0, 6), (0.75, 0.7, 5), (1.0, 0.25, 3)]
MAIN_SIZE = (6.8, 4.9, 5.0)
LEFT = ((-3.0, -0.75, 0.0), (2.3, 2.0, 1.65), 1012)        # centre, size, seed
RIGHT = ((3.15, 0.45, 0.0), (1.85, 1.7, 1.3), 1013)
CHAMFER = 0.02                                            # the sheet's "Hard Edge (Chamfered Look)"


def palette():
    K.set_colour(STONE, "#93898B", rough=0.92)   # measured against the sheet front view
    K.set_colour(STONE_COOL, "#838188", rough=0.92)


def rock(a, size, loc, seed, rings, rot=0.0, lean=(0.0, 0.0)):
    """One closed faceted rock with chamfered edges, warm/cool facet drift and a tone step per facet."""
    vs = K.hull_rock(a, size, loc=loc, seed=seed, mat=STONE, rings=rings, jitter=0.05, rot=rot, lean=lean,
                     keep_bottom=True)
    faces = K.faces_of(vs)
    edges = list({e for f in faces for e in f.edges})
    res = bmesh.ops.bevel(a.bm, geom=edges + vs, offset=CHAMFER * min(size), offset_type="OFFSET", segments=1,
                          profile=0.5, affect="EDGES", clamp_overlap=True)
    new_faces = res.get("faces", [])
    if new_faces:
        bmesh.ops.triangulate(a.bm, faces=[f for f in set(new_faces) | set(K.faces_of(vs)) if f.is_valid and len(f.verts) > 4])
    vs = list({v for f in faces + new_faces if f.is_valid for v in f.verts})
    K.blend(a, vs, STONE, STONE_COOL, K.noise_field(scale=0.22, seed=seed), level=0.18, width=0.45, steps=2)
    K.texture(a, vs, amp=0.04, scale=0.3, jitter=0.035, seed=seed)
    return vs


def main_rock(a, loc=(0, 0, 0)):
    return rock(a, MAIN_SIZE, loc, 1011, MAIN, rot=0.2)


def support(a, side, loc=None):
    c, size, seed = LEFT if side == "left" else RIGHT
    return rock(a, size, loc or c, seed, SUPPORT, rot=0.5 if side == "left" else -0.3)


def hero(a):
    main_rock(a)
    support(a, "left")
    support(a, "right")


NOTES = {
    "Stone": "stone resource: a chunky faceted main rock (broad flat faces, chamfered hard edges) with a support "
             "rock set into its foot on each side; parts unioned into one closed mesh",
    "StoneMainRock": "Main Rock alone: chunky faceted dome with a flat base",
    "StoneSupportRockLeft": "Support Rock (Left): small faceted rock, sits in the main rock's left foot",
    "StoneSupportRockRight": "Support Rock (Right): smaller faceted rock, sits in the main rock's right foot",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Stone", "hero", hero, 4000, "hull"),
             ("StoneMainRock", "part", lambda a: main_rock(a), 1000, "hull"),
             ("StoneSupportRockLeft", "part", lambda a: support(a, "left", (0, 0, 0)), 1000, "hull"),
             ("StoneSupportRockRight", "part", lambda a: support(a, "right", (0, 0, 0)), 1000, "hull")]
    objs = [K.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    audits = [M.finish(o, union=(o.name == "Stone")) for o in objs]
    M.display(NUM, objs, TITLE)                       # its slot in the numbered-models display area
    hx = objs[0].location.x
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, main_o, l_o, r_o = objs
        # exploded shot: the main rock lifted above its two support rocks, as on the sheet
        saved = M.explode([main_o, l_o, r_o], {})
        main_o.location = (hx + 40, 0, 3.4)
        l_o.location = (hx + 40 - 2.4, -0.4, 0)
        r_o.location = (hx + 40 + 2.4, -0.4, 0)
        try:
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": ([main_o, l_o, r_o], -12, 12)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
