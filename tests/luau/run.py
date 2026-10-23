#!/usr/bin/env python3
"""Run the headless Luau specs under tests/luau with the standalone `luau` CLI.

Game modules are written for Roblox: they `require(script.Parent.X)` and use
datatypes like Color3 and Vector3. The CLI has neither, so each spec runs in a
generated bundle: prelude.luau (minimal datatype stubs, a fake `script`/`game`
instance tree, and a require that resolves it) followed by every module under
src/shared as a loader function, followed by the spec itself.

Only pure-logic modules are testable this way -- anything touching Instances,
services, or the network still needs a Studio playtest.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

# Rojo mount points for the modules a spec may require, keyed by the
# instance path the game code sees.
MOUNTS = {
    ("ReplicatedStorage", "Shared"): ROOT / "src" / "shared",
    # Server modules are testable when their Roblox services are injected (fakes in specs).
    ("ServerScriptService", "Server"): ROOT / "src" / "server",
}


def module_entries():
    entries = []
    for prefix, folder in MOUNTS.items():
        for file in sorted(folder.rglob("*.luau")):
            # Entry-point scripts (init.server/init.client) are not requirable modules.
            if file.name.endswith((".server.luau", ".client.luau")):
                continue
            rel = file.relative_to(folder).with_suffix("")
            parts = list(rel.parts)
            if parts[-1] == "init":
                parts = parts[:-1]
            path = list(prefix) + parts
            entries.append((path, file.read_text(encoding="utf-8")))
    return entries


def build_bundle(spec: Path) -> str:
    chunks = [(HERE / "prelude.luau").read_text(encoding="utf-8")]
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


def main() -> int:
    luau = shutil.which("luau")
    if luau is None:
        print("luau CLI not found on PATH (cargo install luau-cli)", file=sys.stderr)
        return 1

    specs = sorted(HERE.glob("*.spec.luau"))
    if not specs:
        print("No specs found", file=sys.stderr)
        return 1

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
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
