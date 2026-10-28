#!/usr/bin/env bash
# Build a whole kit sheet into its .blend library and export it for Roblox.
#
#   art/blender/kit_export_sheet.sh W01 [W02 ...]
#
# Replaces the per-model export each verifier used to run (token budget): run it
# once per sheet after a workflow run. Writes art/blender/assets/kit/<SHEET>.blend
# and art/roblox/kit/<SHEET>/ (meshes, palette, water textures, manifest.json).
# Exit status is non-zero if any sheet's build or export fails.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$(dirname "$HERE")")"
cd "$ROOT" || exit 1
STATUS=0
for SHEET in "$@"; do
  OUT="$(BLENDER_ARGS="$SHEET --no-render" "$HERE/run.sh" scripts/build_kit.py "art/blender/assets/kit/$SHEET.blend")"
  CODE=$?
  printf '%s\n' "$OUT" | grep -E "STATS|FAILED|NOT UPDATED"
  grep -h "^KITPROBLEM" "$HERE/logs/build_kit-${SHEET}_no_render.log" 2>/dev/null | head -10
  if [ $CODE -ne 0 ]; then STATUS=1; echo "[$SHEET] build failed"; continue; fi
  OUT="$(BLENDER_ARGS="art/blender/assets/kit/$SHEET.blend" "$HERE/run.sh" scripts/export_kit_roblox.py \
    "art/roblox/kit/$SHEET/manifest.json")"
  CODE=$?
  printf '%s\n' "$OUT" | grep -E "STATS|FAILED|NOT UPDATED"
  grep -h "KITEXPORT PROBLEM" "$HERE/logs/export_kit_roblox-art_blender_assets_kit_${SHEET}_blend.log" 2>/dev/null | head -10
  if [ $CODE -ne 0 ]; then STATUS=1; echo "[$SHEET] export failed"; fi
done
exit $STATUS
