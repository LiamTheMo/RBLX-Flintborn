#!/usr/bin/env python3
"""Capture a code-built screen without Roblox Studio.

Bundles gui_env.luau (a headless GUI runtime), every module under src/shared
and src/client (JSON files become table modules, as Rojo does) and a scene
script from scenes/, runs it with the standalone `luau` CLI, and renders the
instance tree the scene dumps with render.py. The capture is drawn from the
game's own Luau code, so it shows what that code builds.

    python3 art/ui/capture/capture.py lobby                 # -> art/ui/captures/lobby.png
    python3 art/ui/capture/capture.py journal --out x.png --bg none
    python3 art/ui/capture/capture.py --all

Needs `luau` on PATH (cargo install luau-cli), numpy and Pillow. Text uses the
fonts in art/ui/fonts when present (Merriweather is Roblox's "serif" family).
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import render  # noqa: E402

MOUNTS = {
    ("ReplicatedStorage", "Shared"): ROOT / "src" / "shared",
    ("StarterPlayer", "StarterPlayerScripts", "Client"): ROOT / "src" / "client",
}
OUT = ROOT / "art" / "ui" / "captures"
SPRITES = ROOT / "art" / "ui" / "sprites"
IDS_FILE = ROOT / "src" / "shared" / "UI" / "UiAssetIds.json"
# Stand-in ids for sliced art that is not uploaded yet, so a capture shows the
# screen as it will look once it is (pass --uploaded-only to see the fallbacks).
PREVIEW_BASE = 990000000


def preview_ids():
    """{name: id} for every sprite PNG without an uploaded id."""
    ids = json.loads(IDS_FILE.read_text(encoding="utf-8"))
    missing = sorted(p.stem for p in SPRITES.glob("*.png") if not p.stem.startswith("_") and p.stem not in ids)
    return {name: PREVIEW_BASE + i for i, name in enumerate(missing)}


def lua_literal(value, indent=0):
    """A JSON value as a Luau table constructor."""
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, list):
        return "{" + ", ".join(lua_literal(v) for v in value) + "}"
    items = ", ".join("[%s] = %s" % (json.dumps(k), lua_literal(v)) for k, v in value.items())
    return "{" + items + "}"


def module_entries(extra_ids):
    entries = []
    for prefix, folder in MOUNTS.items():
        for file in sorted(folder.rglob("*")):
            if file.suffix not in (".luau", ".json") or file.name.endswith((".server.luau", ".client.luau")):
                continue
            rel = file.relative_to(folder).with_suffix("")
            parts = list(rel.parts)
            if parts[-1] == "init":
                parts = parts[:-1]
            if file.suffix == ".json":
                data = json.loads(file.read_text(encoding="utf-8"))
                if file == IDS_FILE:
                    data = {**data, **extra_ids}
                source = "return " + lua_literal(data)
            else:
                source = file.read_text(encoding="utf-8")
            entries.append((list(prefix) + parts, source))
    return entries


def bundle(scene: Path, extra_ids) -> str:
    chunks = [(HERE / "gui_env.luau").read_text(encoding="utf-8")]
    for path, source in module_entries(extra_ids):
        chunks.append("__defineModule({%s}, function(script)\n%s\nend)\n"
                      % (", ".join(json.dumps(p) for p in path), source))
    chunks.append(scene.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def run_scene(name: str, extra_ids):
    luau = shutil.which("luau")
    if luau is None:
        sys.exit("luau CLI not found on PATH (cargo install luau-cli)")
    scene = HERE / "scenes" / f"{name}.luau"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"{name}.bundle.luau"
        path.write_text(bundle(scene, extra_ids), encoding="utf-8")
        result = subprocess.run([luau, str(path)], capture_output=True, text=True)
    out = result.stdout
    for line in out.splitlines():
        if not line.startswith("@@GUI@@"):
            print(line)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit(f"scene {name} failed")
    dumps = [chunk.split("@@END@@")[0] for chunk in out.split("@@GUI@@")[1:]]
    if not dumps:
        sys.exit(f"scene {name} dumped nothing")
    return [json.loads(d) for d in dumps]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scene", nargs="?")
    parser.add_argument("--out")
    parser.add_argument("--bg", choices=["scene", "none"], default="scene")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--uploaded-only", action="store_true")
    args = parser.parse_args()
    extra_ids = {} if args.uploaded_only else preview_ids()
    if extra_ids:
        print(f"previewing {len(extra_ids)} sprites that are not uploaded yet")
    render.BY_ID.update({str(v): k for k, v in extra_ids.items()})
    names = sorted(p.stem for p in (HERE / "scenes").glob("*.luau")) if args.all else [args.scene]
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names:
        for index, tree in enumerate(run_scene(name, extra_ids)):
            suffix = "" if index == 0 else f"_{index + 1}"
            out = Path(args.out) if args.out and len(names) == 1 and index == 0 else OUT / f"{name}{suffix}.png"
            render.render(tree, out, background=args.bg)
            print("wrote", out)


if __name__ == "__main__":
    main()
