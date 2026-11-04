#!/usr/bin/env bash
# Ship one finished numbered model from the main session: build it into the open GUI kit file, save, export it for
# Roblox, check the record files, stage exactly its files and commit. Never pushes.
#
#   art/blender/kit/ship.sh M071 "feat(models): 071 Watchtower built by parallel modellers (verifier 8/10)"
#   art/blender/kit/ship.sh M071 "..." --dry-run         # print every step, run only the read-only checks
#
# Steps:
#   1. `mNNN.build()` in the GUI Blender (MCP bridge on port 9876, FlintbornWorldKit.blend open, kit_mcp.install()
#      already run there), then save the file. Fails if build() reports problems (--allow-problems ships anyway,
#      for a model committed with its leftovers noted after two verification rounds).
#   2. The Roblox export of that sheet through art/blender/run.sh; fails unless the log's STATS line reports
#      0 problems.
#   3. The spec and the builder (and the commit message) must not contain temp-folder paths or the names of coding
#      assistants or their vendors.
#   4. Stages exactly: the builder, the model's render folder, its export folder, the kit file and
#      docs/art/MODEL_PROGRESS.md (nothing may be staged beforehand), then commits with the message.
#
# Options: --dry-run, --skip-build (steps 2-4 only), --skip-export (for testing the staging), --no-commit (stop
# before staging), --allow-problems.
# Environment: PY (Python for the MCP call; default python3), BLENDER_PATH (for run.sh), PORT (default 9876),
# SHIP_KIT_BLEND (the .blend to export; default the kit file) and SHIP_EXPORT_OUT (export into this folder instead
# of art/roblox/kit/MNNN) for testing the export on a copy.
set -euo pipefail

usage() { sed -n '2,23p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
[ $# -ge 2 ] || usage
CODE="$1"; MSG="$2"; shift 2
DRY=0; SKIP_BUILD=0; SKIP_EXPORT=0; NO_COMMIT=0; ALLOW=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --skip-build) SKIP_BUILD=1 ;;
    --skip-export) SKIP_EXPORT=1 ;;
    --no-commit) NO_COMMIT=1 ;;
    --allow-problems) ALLOW=1 ;;
    *) echo "ship: unknown option $a"; usage ;;
  esac
done
[[ "$CODE" =~ ^M[0-9]{3}$ ]] || { echo "ship: model code must look like M071, got '$CODE'"; exit 2; }
[ -n "$MSG" ] || { echo "ship: empty commit message"; exit 2; }

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO"
REPO_NATIVE="$(pwd -W 2>/dev/null || pwd)"     # C:/... under Git Bash, for the Windows Python
NUM="${CODE#M}"
MOD="m$NUM"
BUILDER="art/blender/kit/mcp/$MOD.py"
RENDERS="art/blender/renders/models/$CODE"
SPEC="$RENDERS/${CODE}_spec.md"
KIT="art/blender/assets/kit/FlintbornWorldKit.blend"
EXPORT="art/roblox/kit/$CODE"
PROGRESS="docs/art/MODEL_PROGRESS.md"
PORT="${PORT:-9876}"
PY="${PY:-python3}"
EXPORT_BLEND="${SHIP_KIT_BLEND:-$KIT}"
EXPORT_OUT="${SHIP_EXPORT_OUT:-}"
step() { echo "== ship $CODE: $*"; }
fail() { echo "ship $CODE FAILED: $*"; exit 1; }

for f in "$BUILDER" "$SPEC" "$KIT" "$PROGRESS"; do
  [ -e "$f" ] || fail "missing $f"
done
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[ "$BRANCH" != "main" ] || fail "on main; switch to the active version branch first"

# ---- 1. build in the GUI and save --------------------------------------------------------------------------------
BUILD_CODE="import bpy, importlib, sys, time
ns = bpy.app.driver_namespace
assert 'KIT' in ns, 'kit helpers not installed in this Blender: run kit_mcp.install() first'
assert bpy.path.basename(bpy.data.filepath) == 'FlintbornWorldKit.blend', 'open file is ' + bpy.data.filepath
import kit_models, kit_parts, kit_verify, kit_build, $MOD
for m in (kit_models, kit_parts, kit_verify, kit_build, $MOD):
    importlib.reload(m)
t0 = time.time()
out = $MOD.build() or {}
bpy.ops.wm.save_mainfile()
result = {'problems': list(out.get('problems', [])) if isinstance(out, dict) else [], 'build_s': round(time.time() - t0, 1),
          'file': bpy.data.filepath, 'saved': not bpy.data.is_dirty}"
if [ $SKIP_BUILD -eq 1 ]; then
  step "1. build skipped (--skip-build)"
elif [ $DRY -eq 1 ]; then
  step "1. would send to the GUI on port $PORT (build, then save):"
  printf '%s\n' "$BUILD_CODE" | sed 's/^/     /'
else
  step "1. $MOD.build() in the GUI on port $PORT, then save (renders take a few minutes)"
  SHIP_CODE="$BUILD_CODE" SHIP_PORT="$PORT" SHIP_ALLOW="$ALLOW" SHIP_MCP="$REPO_NATIVE/art/blender/kit/mcp" "$PY" - <<'PYEOF'
import json, os, sys
sys.path.insert(0, os.environ["SHIP_MCP"])
import bgmcp
r = bgmcp.request(int(os.environ["SHIP_PORT"]), os.environ["SHIP_CODE"])
if r.get("status") != "ok":
    print("build call failed:", r.get("message") or r)
    sys.exit(1)
res = r["result"]
print(json.dumps({k: res[k] for k in ("build_s", "file", "saved")}))
if not res["saved"]:
    print("the kit file did not save")
    sys.exit(1)
if res["problems"]:
    print(f"build() reports {len(res['problems'])} problems:")
    for p in res["problems"]:
        print("   ", p)
    sys.exit(0 if os.environ["SHIP_ALLOW"] == "1" else 1)
PYEOF
fi

# ---- 2. export and its STATS line ----------------------------------------------------------------------------------
ARGS="$EXPORT_BLEND --sheet $CODE${EXPORT_OUT:+ --out $EXPORT_OUT}"
MANIFEST="${EXPORT_OUT:-$EXPORT}/manifest.json"
if [ $SKIP_EXPORT -eq 1 ]; then
  step "2. export skipped (--skip-export)"
elif [ $DRY -eq 1 ]; then
  step "2. would run: FB_RETINT=1 BLENDER_ARGS=\"$ARGS\" art/blender/run.sh scripts/export_kit_roblox.py $MANIFEST"
  step "   and require the log's STATS line to end in ', 0 problems'"
else
  step "2. export ($EXPORT_BLEND -> ${EXPORT_OUT:-$EXPORT})"
  set +e
  OUT="$(FB_RETINT=1 BLENDER_ARGS="$ARGS" art/blender/run.sh scripts/export_kit_roblox.py "$MANIFEST")"
  CODE_RUN=$?
  set -e
  printf '%s\n' "$OUT" | sed 's/^/     /'
  [ $CODE_RUN -eq 0 ] || fail "export exited $CODE_RUN"
  LOG="$(printf '%s\n' "$OUT" | sed -n 's/.*log: \(.*\)$/\1/p' | head -1)"
  [ -f "$LOG" ] || fail "export log not found ($LOG)"
  STATS="$(grep -E "^STATS " "$LOG" | tail -1 || true)"
  [ -n "$STATS" ] || fail "no STATS line in $LOG"
  [[ "$STATS" == "STATS $CODE:"* ]] || echo "     (note: the STATS line names another sheet; expected for a test copy)"
  [[ "$STATS" =~ ,\ 0\ problems$ ]] || { grep "KITEXPORT PROBLEM" "$LOG" | head -20; fail "export problems: $STATS"; }
  step "   $STATS"
fi

# ---- 3. record files: no temp paths, no assistant or vendor names -----------------------------------------------
step "3. checking $SPEC, $BUILDER and the commit message"
TEMP_PAT='AppData[\\/]|[\\/]tmp[\\/]|[\\/]Temp[\\/]|[A-Za-z]:[\\/]+Users[\\/]'
# the names are stored rot13-encoded so that this committed file doesn't name them either
NAME_PAT="$(printf '%s' 'Pynhqr|Naguebcvp|BcraNV|PungTCG|Pbcvybg|Trzvav|Pbqrk' | tr 'A-Za-z' 'N-ZA-Mn-za-m')"
BAD=0
for f in "$SPEC" "$BUILDER"; do
  if grep -n -E "$TEMP_PAT" "$f"; then echo "   ^ temp-folder path in $f"; BAD=1; fi
  if grep -n -i -w -E "$NAME_PAT" "$f"; then echo "   ^ assistant / vendor name in $f"; BAD=1; fi
done
if printf '%s' "$MSG" | grep -q -i -w -E "$NAME_PAT|co-authored-by"; then echo "   commit message names an assistant or adds a trailer"; BAD=1; fi
if printf '%s' "$MSG" | grep -q -E "$TEMP_PAT"; then echo "   commit message has a temp-folder path"; BAD=1; fi
[ $BAD -eq 0 ] || fail "record files need cleaning"

# ---- 4. stage exactly the model's files and commit ---------------------------------------------------------------
PATHS=("$BUILDER" "$RENDERS" "$EXPORT" "$KIT" "$PROGRESS")
if ! git diff --cached --quiet; then
  git diff --cached --name-only | sed 's/^/     staged: /'
  fail "something is already staged; unstage it first"
fi
if [ $DRY -eq 1 ] || [ $NO_COMMIT -eq 1 ]; then
  step "4. would stage (git add -A --) ${PATHS[*]}:"
  git status --porcelain --untracked-files=all -- "${PATHS[@]}" | sed 's/^/     /'
  step "   and commit on $BRANCH with: $MSG"
  step "done (nothing staged or committed)"
  exit 0
fi
step "4. staging and committing on $BRANCH"
git add -A -- "${PATHS[@]}"
while IFS= read -r f; do
  case "$f" in
    "$BUILDER"|"$RENDERS"/*|"$EXPORT"/*|"$KIT"|"$PROGRESS") ;;
    *) git reset -q; fail "unexpected staged path $f (staging undone)" ;;
  esac
done < <(git diff --cached --name-only)
git diff --cached --quiet && fail "nothing to commit"
git diff --cached --stat | tail -1
git commit -q -m "$MSG"
step "committed $(git rev-parse --short HEAD) on $BRANCH (not pushed)"
