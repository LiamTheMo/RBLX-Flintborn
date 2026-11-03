#!/usr/bin/env python3
"""Run the headless Luau specs under tests/luau with the standalone `luau` CLI.

Game modules are written for Roblox: they `require(script.Parent.X)` and use
datatypes like Color3 and Vector3. The CLI has neither, so each spec runs in a
generated bundle: prelude.luau (minimal datatype stubs, a fake `script`/`game`
instance tree, and a require that resolves it) followed by every module under
src/shared, src/server and tests/luau/support (MOUNTS) as a loader function (a
JSON file as a module returning its table, as Rojo builds it), followed by the
spec itself. support/ holds helpers several specs share (a fake clock and task
scheduler, engine signals); specs require them from ServerStorage.TestSupport.

Only pure-logic modules are testable this way -- anything touching Instances,
services, or the network still needs a Studio playtest. Server services are
testable when a spec injects fakes for the Roblox services they use.

    python3 tests/luau/run.py       # every *.spec.luau here, one bundle each
"""
import json
import shutil
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
# The release scripts' JSON -> Luau converter, so specs see JSON modules exactly
# as they are published (ASCII-only, with \u{...} escapes the luau CLI accepts).
from roblox_cloud_sync import json_to_luau  # noqa: E402

# Rojo mount points for the modules a spec may require, keyed by the
# instance path the game code sees.
MOUNTS = {
    ("ReplicatedStorage", "Shared"): ROOT / "src" / "shared",
    # Server modules are testable when their Roblox services are injected (fakes in specs).
    ("ServerScriptService", "Server"): ROOT / "src" / "server",
    # Shared spec helpers (fake clock and scheduler, engine signals); test-only,
    # not part of the game.
    ("ServerStorage", "TestSupport"): HERE / "support",
}


def module_entries():
    entries = []
    for prefix, folder in MOUNTS.items():
        for file in sorted(folder.rglob("*")):
            if file.suffix not in (".luau", ".json"):
                continue
            # Entry-point scripts (init.server/init.client) are not requirable modules.
            if file.name.endswith((".server.luau", ".client.luau")):
                continue
            rel = file.relative_to(folder).with_suffix("")
            parts = list(rel.parts)
            if parts[-1] == "init":
                parts = parts[:-1]
            path = list(prefix) + parts
            if file.suffix == ".json":
                # Rojo turns a JSON file into a module returning its table.
                source = json_to_luau(file.read_text(encoding="utf-8"))
            else:
                source = file.read_text(encoding="utf-8")
            entries.append((path, source))
    return entries


# How server services and shared rules refuse a request: `return false, "Code"`,
# `return nil, "Code"` or `fail("Code")` (admission). reasons.spec.luau checks
# that every such code has player-facing text in shared/UI/ReasonText.
REFUSAL_PATTERNS = (
    # Only after `return`, so a model part's name (`..., nil, "Trunk")`) is not one.
    re.compile(r'\breturn\s+(?:false|nil),\s*"([A-Z][A-Za-z]+)"'),
    re.compile(r'\bfail\(\s*"([A-Z][A-Za-z]+)"'),
)


def refusal_codes() -> list:
    """Every refusal code written in src/server and src/shared, sorted."""
    codes = set()
    for folder in (ROOT / "src" / "server", ROOT / "src" / "shared"):
        for file in folder.rglob("*.luau"):
            text = file.read_text(encoding="utf-8")
            for pattern in REFUSAL_PATTERNS:
                codes.update(pattern.findall(text))
    return sorted(codes)


def build_bundle(spec: Path) -> str:
    chunks = [(HERE / "prelude.luau").read_text(encoding="utf-8")]
    # The scanned refusal codes, for reasons.spec.luau.
    chunks.append("__SERVER_REFUSAL_CODES = {" + ", ".join(json.dumps(c) for c in refusal_codes()) + "}\n")
    for path, source in module_entries():
        chunks.append(
            "__defineModule({path}, function(script)\n{source}\nend)\n".format(
                path="{" + ", ".join(json.dumps(p) for p in path) + "}",
                source=source,
            )
        )
    chunks.append("__runSpec({name}, function()\n{source}\nend)\n".format(
        name=json.dumps(spec.name), source=spec.read_text(encoding="utf-8")))
    return "\n".join(chunks)


def require_cycles() -> list:
    """Sibling services/controllers requiring each other in a loop deadlock at
    runtime in Roblox, so the static graph must be acyclic."""
    cycles = []
    for folder in (ROOT / "src" / "server" / "Services", ROOT / "src" / "client" / "Controllers"):
        graph = {
            path.stem: re.findall(r"require\(script\.Parent\.(\w+)\)", path.read_text(encoding="utf-8"))
            for path in folder.glob("*.luau")
        }
        state, stack = {}, []

        def visit(name):
            state[name] = 1
            stack.append(name)
            for nxt in graph.get(name, []):
                if state.get(nxt) == 1:
                    cycles.append(" -> ".join(stack[stack.index(nxt):] + [nxt]))
                elif nxt not in state:
                    visit(nxt)
            stack.pop()
            state[name] = 2

        for name in graph:
            if name not in state:
                visit(name)
    return cycles


def main() -> int:
    luau = shutil.which("luau")
    if luau is None:
        print("luau CLI not found on PATH (cargo install luau-cli)", file=sys.stderr)
        return 1

    specs = sorted(HERE.glob("*.spec.luau"))
    if not specs:
        print("No specs found", file=sys.stderr)
        return 1

    cycles = require_cycles()
    for cycle in cycles:
        print(f"REQUIRE CYCLE: {cycle}")
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for spec in specs:
            bundle = Path(tmp) / (spec.stem + ".bundle.luau")
            bundle.write_text(build_bundle(spec), encoding="utf-8")
            result = subprocess.run([luau, str(bundle)], capture_output=True, text=True)
            sys.stdout.write(result.stdout)
            sys.stderr.write(result.stderr)
            if result.returncode != 0 or "SPEC FAILED" in result.stdout:
                failed += 1

    print(f"{len(specs) - failed}/{len(specs)} spec files passed")
    if cycles:
        print(f"{len(cycles)} require cycle(s) found")
    return 1 if failed or cycles else 0


if __name__ == "__main__":
    sys.exit(main())
