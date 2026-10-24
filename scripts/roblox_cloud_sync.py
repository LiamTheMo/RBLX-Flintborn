#!/usr/bin/env python3
"""Fail-closed code-only Roblox Studio synchronization via Open Cloud Engine Instances.

No place publishing, instance creation, deletion, or non-script writes are supported.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_TYPES = ("Script", "LocalScript", "ModuleScript")
EXTENSIONS = (".luau", ".lua")
# Rojo turns any other `*.json` file into a ModuleScript that returns the
# decoded JSON. These suffixes mean something else to Rojo and are never
# JSON modules, so they are skipped.
JSON_EXTENSION = ".json"
NON_MODULE_JSON = (".project.json", ".meta.json", ".model.json")
SOURCE_EXTENSIONS = EXTENSIONS + (JSON_EXTENSION,)
ALLOWED_SOURCE_ROOTS = ("src/server", "src/client", "src/shared")
# Indentation stops growing past this depth so deep JSON cannot blow up the
# generated source quadratically.
MAX_INDENT_DEPTH = 32


def is_json_module(path):
    name = path.name
    return name.endswith(JSON_EXTENSION) and not name.endswith(NON_MODULE_JSON)


def kind(path):
    name = path.name
    if name.endswith(JSON_EXTENSION):
        if not is_json_module(path):
            return None
        stem = name[:-len(JSON_EXTENSION)]
        if not stem:
            raise ValueError("JSON module without a name: " + str(path))
        # Rojo has no `init.json` rule: the instance is always named after the file.
        return "ModuleScript", stem
    if name.endswith((".server.luau", ".server.lua")):
        return "Script", name.split(".server.")[0]
    if name.endswith((".client.luau", ".client.lua")):
        return "LocalScript", name.split(".client.")[0]
    if name.endswith(EXTENSIONS):
        return "ModuleScript", name.rsplit(".", 1)[0]
    return None


def discover():
    project = json.loads((ROOT / "default.project.json").read_text(encoding="utf-8"))
    entries = {}
    def add_source(directory, destination):
        for file in sorted(directory.rglob("*")):
            if not file.is_file() or not file.name.endswith(SOURCE_EXTENSIONS):
                continue
            if any(parent.name.endswith(".project.json") for parent in file.parents):
                raise ValueError("Nested Rojo project requires explicit support: " + str(file))
            spec = kind(file)
            if spec is None:
                continue
            class_name, name = spec
            relative = file.relative_to(directory)
            if name == "init" and not is_json_module(file):
                parts = destination + relative.parts[:-1]
            else:
                parts = destination + relative.parts[:-1] + (name,)
            if not parts or parts in entries:
                raise ValueError("Ambiguous target mapping: " + "/".join(parts))
            entries[parts] = (file, class_name)

    def walk(node, destination):
        if not isinstance(node, dict):
            return
        path = node.get("$path")
        if isinstance(path, str):
            source = ROOT / path
            if path.replace("\\", "/").rstrip("/") in ALLOWED_SOURCE_ROOTS:
                if not source.is_dir():
                    raise ValueError("Missing mapped code directory: " + path)
                add_source(source, destination)
            elif source.is_file() and path.replace("\\", "/").startswith(tuple(x + "/" for x in ALLOWED_SOURCE_ROOTS)):
                spec = kind(source)
                if spec:
                    class_name, name = spec
                    is_init = name == "init" and not is_json_module(source)
                    parts = destination if is_init else destination[:-1] + (name,)
                    if parts in entries:
                        raise ValueError("Duplicate script target: " + "/".join(parts))
                    entries[parts] = (source, class_name)
        for child_name, child in node.items():
            if not child_name.startswith("$"):
                walk(child, destination + (child_name,))

    walk(project["tree"], ())
    if not entries:
        raise ValueError("No scripts mapped from approved Rojo source roots")
    return entries


class _JsonNumber(str):
    """A JSON number kept as its original text (a valid Luau numeral)."""


def _reject_constant(name):
    raise ValueError("Non-standard JSON constant: " + name)


_LUAU_ESCAPES = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t"}


def luau_string(text):
    """Quote text as an ASCII-only Luau string literal."""
    out = ['"']
    for ch in text:
        code = ord(ch)
        if ch in _LUAU_ESCAPES:
            out.append(_LUAU_ESCAPES[ch])
        elif 0x20 <= code < 0x7F:
            out.append(ch)
        elif code < 0x80:
            out.append("\\x%02X" % code)  # other control characters and DEL
        elif 0xD800 <= code <= 0xDFFF:
            raise ValueError("Unpaired UTF-16 surrogate in JSON string")
        else:
            out.append("\\u{%X}" % code)
    out.append('"')
    return "".join(out)


def json_to_luau(text, origin=None):
    """Convert JSON text to a Luau module returning the equivalent value.

    Objects become `["key"] = value` tables (duplicate keys: last wins, as in
    Rojo), arrays become sequential tables, true/false/null become
    true/false/nil and numbers keep their JSON spelling. The output is
    deterministic, ASCII-only, and built without recursion.
    """
    try:
        value = json.loads(text, parse_int=_JsonNumber, parse_float=_JsonNumber,
                           parse_constant=_reject_constant)
    except RecursionError:
        raise ValueError("JSON nesting is too deep to convert") from None
    out = []
    if origin:
        out.append("-- Generated from %s by the release scripts. Edit the JSON in Git.\n" % origin)
    out.append("return ")
    stack = [(False, value, 0)]
    while stack:
        is_text, item, depth = stack.pop()
        if is_text:
            out.append(item)
        elif isinstance(item, (dict, list)):
            if not item:
                out.append("{}")
                continue
            inner = "\t" * min(depth + 1, MAX_INDENT_DEPTH)
            entries = item.items() if isinstance(item, dict) else ((None, x) for x in item)
            pending = []
            for key, child in entries:
                label = "" if key is None else "[" + luau_string(key) + "] = "
                pending.append((True, "\n" + inner + label, depth))
                pending.append((False, child, depth + 1))
                pending.append((True, ",", depth))
            pending.append((True, "\n" + "\t" * min(depth, MAX_INDENT_DEPTH) + "}", depth))
            out.append("{")
            stack.extend(reversed(pending))
        elif item is True:
            out.append("true")
        elif item is False:
            out.append("false")
        elif item is None:
            out.append("nil")
        elif isinstance(item, _JsonNumber):
            out.append(str.__str__(item))
        elif isinstance(item, str):
            out.append(luau_string(item))
        else:
            raise ValueError("Unsupported JSON value: " + type(item).__name__)
    out.append("\n")
    return "".join(out)


def local_source(file):
    """The Source a mapped file should have in Roblox, matching Rojo."""
    text = file.read_text(encoding="utf-8")
    if is_json_module(file):
        try:
            return json_to_luau(text, origin=file.name)
        except ValueError as error:
            raise ValueError("Invalid JSON module %s: %s" % (file, error)) from None
    return text


class Cloud:
    def __init__(self):
        self.key = os.environ.get("ROBLOX_API_KEY", "")
        self.universe = os.environ.get("ROBLOX_UNIVERSE_ID", "")
        self.place = os.environ.get("ROBLOX_PLACE_ID", "")
        if not self.key or not self.universe.isdecimal() or not self.place.isdecimal():
            raise ValueError("ROBLOX_API_KEY and numeric ROBLOX_UNIVERSE_ID/ROBLOX_PLACE_ID required")
        self.base = "https://apis.roblox.com/cloud/v2/universes/%s/places/%s" % (self.universe, self.place)

    def request(self, method, url, payload=None):
        if not url.startswith("https://apis.roblox.com/cloud/v2/"):
            raise ValueError("Refusing unexpected Open Cloud URL")
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if data is not None and len(data) >= 200000:
            raise ValueError("Open Cloud update exceeds safe 200 KB payload limit")
        for attempt in range(5):
            req = urllib.request.Request(url, data=data, method=method, headers={
                "x-api-key": self.key, "content-type": "application/json",
            })
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as error:
                body = error.read(1024).decode("utf-8", errors="replace")
                if error.code in (429, 500, 502, 503, 504) and attempt < 4:
                    time.sleep(min(2 ** attempt * 2, 16))
                    continue
                raise RuntimeError("Roblox API HTTP %s (%s): %s" % (error.code, method, body)) from None
        raise RuntimeError("Roblox API exhausted retries")

    def operation(self, method, url, payload=None):
        initial = self.request(method, url, payload)
        if initial.get("done") is True:
            result = initial
        else:
            path = initial.get("path", "")
            prefix = "universes/%s/places/%s/instances/" % (self.universe, self.place)
            if not path.startswith(prefix) or "/operations/" not in path:
                raise RuntimeError("Unexpected Roblox operation path")
            operation_url = "https://apis.roblox.com/cloud/v2/" + path
            result = None
            for _ in range(12):
                time.sleep(5)
                status = self.request("GET", operation_url)
                if status.get("done"):
                    result = status
                    break
            if result is None:
                raise RuntimeError("Roblox operation timed out: " + path)
        if result.get("error"):
            raise RuntimeError("Roblox operation failed: " + str(result["error"]))
        if not result.get("done"):
            raise RuntimeError("Roblox operation did not complete")
        return result.get("response", {})

    def children(self, instance_id):
        return self.operation("GET", self.base + "/instances/" + instance_id + ":listChildren").get("instances", [])

    def instance(self, instance_id):
        data = self.operation("GET", self.base + "/instances/" + instance_id)
        return data.get("engineInstance", data.get("instance", data))

    def patch(self, instance_id, class_name, source):
        return self.operation("PATCH", self.base + "/instances/" + instance_id,
                              {"engineInstance": {"Details": {class_name: {"Source": source}}}})


def script_source(record, expected_class):
    details = record.get("Details") or {}
    if not isinstance(details, dict) or expected_class not in details:
        raise ValueError("Expected %s but Roblox returned %s" %
                         (expected_class, list(details)))
    source = details[expected_class].get("Source")
    if not isinstance(source, str):
        raise ValueError("Roblox did not return readable Source for " + expected_class)
    return source


def preflight(cloud, entries):
    cache = {}
    selected = []
    errors = []
    def children(parent):
        if parent not in cache:
            cache[parent] = cloud.children(parent)
        return cache[parent]
    for path, (file, expected_class) in entries.items():
        parent = "root"
        try:
            for name in path:
                candidates = [item for item in children(parent)
                              if item.get("engineInstance", {}).get("Name") == name]
                if len(candidates) != 1:
                    raise ValueError("Expected exactly one instance named " + name)
                record = candidates[0].get("engineInstance") or {}
                parent = record.get("Id") or ""
                if not parent or not re.fullmatch(r"[A-Za-z0-9-]{4,80}", parent):
                    raise ValueError("Invalid instance ID")
            record = cloud.instance(parent)
            source = script_source(record, expected_class)
            local = local_source(file)
            # Fail before ANY write if a script cannot be safely resolved.
            selected.append((path, parent, expected_class, source, local))
        except (ValueError, RuntimeError) as error:
            errors.append("/".join(path) + ": " + str(error))
    if errors:
        raise ValueError("Cloud preflight failed (no writes performed):\n" + "\n".join(errors[:30]) +
                         ("\n... additional errors: %s" % (len(errors) - 30) if len(errors) > 30 else ""))
    return selected


def main():
    parser = argparse.ArgumentParser()
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--check", action="store_true", help="Validate local Rojo-to-script mappings; no network")
    choice.add_argument("--dry-run", action="store_true", help="Read-only cloud preflight and diff")
    choice.add_argument("--deploy", action="store_true", help="Update changed existing scripts (never publish a place)")
    args = parser.parse_args()
    entries = discover()
    json_modules = sum(1 for file, _ in entries.values() if is_json_module(file))
    print("Validated %d Git-managed scripts (%d JSON modules published as Luau tables); "
          "all Studio assets are excluded." % (len(entries), json_modules), flush=True)
    if args.check:
        for target, (file, kind_name) in sorted(entries.items()):
            local_source(file)  # surfaces invalid JSON modules offline
            suffix = " [JSON -> Luau table]" if is_json_module(file) else ""
            print("%s (%s) <- %s%s" % ("/".join(target), kind_name,
                                       file.relative_to(ROOT).as_posix(), suffix))
        return
    cloud = Cloud()
    selected = preflight(cloud, entries)
    changes = [x for x in selected if x[3] != x[4]]
    print("Preflight passed: %d mapped scripts, %d changed." % (len(selected), len(changes)), flush=True)
    if args.dry_run:
        for path, _, _, _, _ in changes:
            print("WOULD UPDATE " + "/".join(path))
        return
    for path, instance_id, class_name, _, source in changes:
        cloud.patch(instance_id, class_name, source)
        current = cloud.instance(instance_id)
        if script_source(current, class_name) != source:
            raise RuntimeError("Post-update verification failed: " + "/".join(path))
        print("UPDATED " + "/".join(path), flush=True)
    print("Cloud script sync complete. Live publication is a separate manual operation.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError, urllib.error.URLError) as error:
        print("SAFE STOP: " + str(error), file=sys.stderr)
        sys.exit(1)
