"""Helpers the place tools (roblox_lobby_map.py, roblox_character.py) share."""
import hashlib
import json

import roblox_upload_ui_assets as uploader
from roblox_cloud_sync import luau_string


def sha1(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def load_ids(path):
    """An asset_ids.json with its "images" and "models" tables."""
    data = uploader.load_json(path)
    data.setdefault("images", {})
    data.setdefault("models", {})
    return data


def lua_str(text):
    """Text as an ASCII-only Luau string literal (\\u{...} escapes, which Luau reads)."""
    return luau_string(text)


def lua_value(value):
    """JSON-compatible data as a compact Luau literal."""
    if isinstance(value, dict):
        return "{" + ",".join(f"[{lua_str(k)}]={lua_value(v)}" for k, v in value.items()) + "}"
    if isinstance(value, list):
        return "{" + ",".join(lua_value(v) for v in value) + "}"
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "nil"
    if isinstance(value, str):
        return lua_str(value)
    return repr(value)


def show(task):
    """Prints a task's JSON return value (or the raw output if it is not JSON)."""
    output = task.get("output") or {}
    values = output.get("results") or []
    value = values[0] if values else output
    try:
        value = json.loads(value)
    except (TypeError, ValueError):
        pass
    print(json.dumps(value, indent=1), flush=True)
