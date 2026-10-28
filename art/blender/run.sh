#!/usr/bin/env bash
# Run a Blender build script headless with an honest exit code.
#
#   art/blender/run.sh scripts/build_03_furnishings.py [expected_output ...]
#
# - Python exceptions make Blender exit 1 (--python-exit-code), instead of the
#   default 0 that hides crashes.
# - stdin is /dev/null, so nothing can hang waiting for input.
# - The full log goes to art/blender/logs/<script>.log; only a short summary is
#   printed, so callers never need a trailing `| grep` (which exits 1 when it
#   finds nothing and makes a clean run look failed).
# - Every expected output file must have been rewritten by this run, otherwise
#   the run fails. With no outputs given, the script's default .blend is checked.
#
# Exit codes: 0 ok, 1 Blender/Python error, 2 an expected output was not updated.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLENDER="${BLENDER_PATH:-D:/Steam/steamapps/common/Blender/blender.exe}"
SCRIPT="$1"; shift
[ -f "$SCRIPT" ] || SCRIPT="$HERE/$SCRIPT"
NAME="$(basename "$SCRIPT" .py)"
mkdir -p "$HERE/logs"
# Runs with different arguments get their own log, so parallel runs of one
# script (e.g. several build_kit.py modules) never overwrite each other's.
TAG="$(printf '%s' "${BLENDER_ARGS:-}" | tr -cs 'A-Za-z0-9' '_' | sed 's/^_//; s/_$//')"
LOG="$HERE/logs/$NAME${TAG:+-$TAG}.log"

OUTPUTS=("$@")
if [ ${#OUTPUTS[@]} -eq 0 ]; then
  case "$NAME" in
    build_lobby) OUTPUTS=("$HERE/lobby/FlintbornLobby.blend") ;;
    build_showcase) OUTPUTS=("$HERE/renders/final/flintborn_showcase.png") ;;
    build_08_vfx) OUTPUTS=("$HERE/renders/08_vfx.png") ;;
    build_*) OUTPUTS=("$HERE/assets/${NAME#build_}.blend") ;;
  esac
fi

STAMP="$(mktemp)"
START=$(date +%s)
# Extra script arguments go in BLENDER_ARGS, e.g. BLENDER_ARGS="--audit /tmp/audit".
# shellcheck disable=SC2086
"$BLENDER" --background --factory-startup --python-exit-code 1 --python "$SCRIPT" -- ${BLENDER_ARGS:-} \
  < /dev/null > "$LOG" 2>&1
CODE=$?
SECS=$(( $(date +%s) - START ))

echo "[$NAME] blender exit $CODE in ${SECS}s, log: $LOG"
if [ $CODE -ne 0 ] || grep -q "^Traceback" "$LOG"; then
  echo "[$NAME] FAILED. Last error lines:"
  grep -n -A12 "^Traceback" "$LOG" | tail -20
  [ $CODE -ne 0 ] || CODE=1
  rm -f "$STAMP"; exit $CODE
fi

STATUS=0
for f in "${OUTPUTS[@]}"; do
  if [ -f "$f" ] && [ "$f" -nt "$STAMP" ]; then
    echo "[$NAME] updated: $f"
  else
    echo "[$NAME] NOT UPDATED: $f"; STATUS=2
  fi
done
rm -f "$STAMP"
grep -E "OVER BUDGET|^(STATS|SHOWCASE|FB03 DONE)" "$LOG" | tail -5 || true
exit $STATUS
