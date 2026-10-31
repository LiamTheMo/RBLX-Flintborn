# Working in this repo

**Game UI** (screens, the Kit, UI art): start with [`docs/ui/STYLE_GUIDE.md`](docs/ui/STYLE_GUIDE.md).

## Shell commands (Bash tool)
- **Never run a command that reads stdin without input.** A bare `cat > file`, `read`, or a tool that waits for input blocks forever: the shell's stdin stays open, so the command hits the timeout and is killed. Write files with the Write/Edit tools or a heredoc (`cat > file <<'EOF' ... EOF`). Add `< /dev/null` to anything that might prompt.
- **Give long commands a long timeout.** The Bash default is 120 s. Blender builds and renders often take longer: pass `timeout: 600000` (10 min), or run with `run_in_background: true` and wait for the completion notification. Don't stop a backgrounded Blender run just because it is slow; check its output file first.
- There is no system Python on this machine. Use Blender's Python for scripts (`blender --background --factory-startup --python <script>`), or the uv-installed `C:/Users/Orang/.local/bin/python3.14.exe` for plain Python such as `tests/test_cloud_live_publish.py`.

## Blender art pipeline
See [`art/blender/README.md`](art/blender/README.md). **Always run Blender builds through the wrapper:**

```bash
art/blender/run.sh scripts/build_07_terrain_kit.py
```

Why: bare `blender --python` exits 0 even when the script crashes, and a trailing `| grep Error` exits 1 when the build is clean. Together these make failures look like successes and successes look like failures. `run.sh`:
- adds `--python-exit-code 1`;
- feeds stdin from `/dev/null`;
- writes the full log to `art/blender/logs/`;
- prints a short summary;
- exits 2 if the expected output (`assets/<sheet>.blend` by default) was not rewritten by this run.

Pass extra script arguments with `BLENDER_ARGS="--audit <dir>"`, and environment flags (for example `FB_ONLY=Name`) as usual. Don't pipe its output through `grep`.

**Edit code with the Edit tool, not `sed -i`/`perl -pi`.** A substitution whose pattern doesn't match changes nothing and reports nothing, so the fix silently isn't applied. If you do use one, confirm the change with a `grep` that is expected to match.

Sheet scripts in `art/blender/scripts/` each own one `.blend` in `art/blender/assets/`. The lobby (`build_lobby.py`) links those libraries, so rebuild a sheet first and then the lobby. Only the main session drives the open Blender GUI through the Blender MCP.
