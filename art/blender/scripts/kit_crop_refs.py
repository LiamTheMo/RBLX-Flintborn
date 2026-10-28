"""Cut kit reference sheets into one strip per subject row.

    BLENDER_ARGS="W01 R01" art/blender/run.sh scripts/kit_crop_refs.py <expected png>

Finds the sheet's horizontal grid lines (long runs of pixels darker than the
paper) and writes art/reference/kit/rows/<sheet>_row<N>.png for the four
subject rows, at full resolution, so a builder can study one subject closely.
"""

import glob
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(os.path.dirname(os.path.dirname(HERE)), "reference", "kit")
OUT = os.path.join(REF, "rows")


def load(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1]  # top-down
    bpy.data.images.remove(img)
    return px


def grid_lines(px):
    lum = px[..., :3].mean(axis=2)
    paper = np.median(lum)
    dark = (lum < paper - 0.06).mean(axis=1)
    ys = [y for y in range(len(dark)) if dark[y] > 0.55]
    # merge runs of adjacent lines
    lines = []
    for y in ys:
        if lines and y - lines[-1][-1] <= 3:
            lines[-1].append(y)
        else:
            lines.append([y])
    # (y, strength): grid rules span the whole table, artwork rarely does
    return [(int(sum(r) / len(r)), float(max(dark[y] for y in r))) for r in lines]


# Sheets whose layout defeats the detector (no shared column-header row), cut by hand.
ROW_OVERRIDES = {
    "W14": [(28, 279), (279, 512), (512, 759), (759, 980)],
}


def rows_from(lines, h):
    """Four even subject rows between the column-header line and the last grid
    line, each cut snapped to the nearest detected line (artwork also trips the
    detector, so only lines near the expected cuts count)."""
    top = next(y for y, _ in lines if y > h * 0.06)
    bottom = lines[-1][0]
    cuts = [top]
    for i in (1, 2, 3):
        want = top + (bottom - top) * i / 4
        near = [(y, s) for y, s in lines if abs(y - want) < h * 0.07] or lines
        # strongest rule near the expected cut; distance only breaks ties
        cuts.append(max(near, key=lambda l: (round(l[1], 2), -abs(l[0] - want)))[0])
    cuts.append(bottom)
    return [(cuts[i], cuts[i + 1]) for i in range(4)]


def save(px, path):
    h, w = px.shape[:2]
    img = bpy.data.images.new("crop", w, h, alpha=True)
    img.pixels = np.ascontiguousarray(px[::-1]).ravel()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    os.makedirs(OUT, exist_ok=True)
    for sheet in args:
        path = glob.glob(os.path.join(REF, sheet + "_*.png"))[0]
        px = load(path)
        h = px.shape[0]
        lines = grid_lines(px)
        rows = ROW_OVERRIDES.get(sheet) or rows_from(lines, h)
        print(f"KITCROP {sheet} rows={rows}")
        for i, (y0, y1) in enumerate(rows, 1):
            save(px[max(0, y0 - 2):min(h, y1 + 2)], os.path.join(OUT, f"{sheet}_row{i}.png"))


main()
