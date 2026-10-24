#!/usr/bin/env python3
"""Upload the HUD sprites (art/ui/sprites/*.png) to Roblox and record their ids.

Uses the Open Cloud Assets API (POST https://apis.roblox.com/assets/v1/assets,
assetType Decal), polls each returned operation, and writes the resulting image
asset ids into src/shared/UI/UiAssetIds.json, which UiAssets.luau reads. Names
already in that file are skipped, so re-running only uploads what is new.

Default is a dry run that lists what would upload and touches nothing. Uploading
is an outward action: it needs --upload plus these environment variables:

  ROBLOX_API_KEY            Open Cloud key with asset write permission
  ROBLOX_CREATOR_USER_ID    or ROBLOX_CREATOR_GROUP_ID (exactly one)

--sprites regenerates src/shared/UI/UiSprites.json (sizes and 9-slice insets)
from art/ui/sprites/manifest.json. It is local only and needs no key.

  python scripts/roblox_upload_ui_assets.py               # dry run
  python scripts/roblox_upload_ui_assets.py --sprites     # refresh UiSprites.json
  python scripts/roblox_upload_ui_assets.py --upload --only frame_slot,icon_heart
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "art" / "ui" / "sprites"
MANIFEST = SPRITES / "manifest.json"
IDS_FILE = ROOT / "src" / "shared" / "UI" / "UiAssetIds.json"
SPRITES_FILE = ROOT / "src" / "shared" / "UI" / "UiSprites.json"

ASSETS_URL = "https://apis.roblox.com/assets/v1/assets"
OPERATIONS_URL = "https://apis.roblox.com/assets/v1/"
DELIVERY_URL = "https://apis.roblox.com/asset-delivery-api/v1/assetId/"
MAX_BYTES = 20 * 1024 * 1024
POLL_SECONDS = 2
POLL_LIMIT_SECONDS = 120


def sprite_files():
    """Every sprite PNG; files starting with "_" are contact sheets and tests."""
    if not SPRITES.is_dir():
        return []
    return sorted(p for p in SPRITES.glob("*.png") if not p.name.startswith("_"))


def load_json(path):
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8") or "{}")
    if not isinstance(data, dict):
        raise ValueError(f"{path} must hold a JSON object")
    return data


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def pending(files, ids, only):
    chosen = []
    for file in files:
        name = file.stem
        if only and name not in only:
            continue
        if name in ids:
            continue
        chosen.append(file)
    return chosen


def creator_from_env():
    user = os.environ.get("ROBLOX_CREATOR_USER_ID", "").strip()
    group = os.environ.get("ROBLOX_CREATOR_GROUP_ID", "").strip()
    if bool(user) == bool(group):
        raise ValueError("Set exactly one of ROBLOX_CREATOR_USER_ID or ROBLOX_CREATOR_GROUP_ID")
    value = user or group
    if not value.isdecimal():
        raise ValueError("The creator id must be numeric")
    return {"userId": value} if user else {"groupId": value}


def sync_sprites():
    """UiSprites.json = {name: {w, h, slice}} copied from the slicer's manifest."""
    manifest = load_json(MANIFEST)
    if not manifest:
        raise ValueError(f"No manifest at {MANIFEST}")
    out = {}
    for name, entry in sorted(manifest.items()):
        slice_ = entry.get("slice")
        if slice_ is not None and (not isinstance(slice_, list) or len(slice_) != 4):
            raise ValueError(f"Bad slice for {name}: {slice_!r}")
        out[name] = {"w": int(entry["w"]), "h": int(entry["h"]), "slice": slice_}
    write_json(SPRITES_FILE, out)
    sliced = sum(1 for v in out.values() if v["slice"])
    print(f"Wrote {SPRITES_FILE.relative_to(ROOT)}: {len(out)} sprites ({sliced} 9-sliced)")


class Cloud:
    def __init__(self, key, creator):
        self.key = key
        self.creator = creator

    def _send(self, request):
        for attempt in range(5):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code in (429, 500, 502, 503, 504) and attempt < 4:
                    time.sleep(3 * (2 ** attempt))
                    continue
                body = exc.read(800).decode("utf-8", errors="replace")
                raise RuntimeError(f"Roblox API HTTP {exc.code}: {body}") from None
        raise RuntimeError("Roblox API retries exhausted")

    def upload(self, file):
        payload = {
            "assetType": "Decal",
            "displayName": f"Flintborn UI {file.stem}"[:50],
            "description": "Flintborn HUD sprite",
            "creationContext": {"creator": self.creator},
        }
        boundary = uuid.uuid4().hex
        body = b"".join([
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="request"\r\n',
            b"Content-Type: application/json\r\n\r\n",
            json.dumps(payload).encode("utf-8"),
            f"\r\n--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="fileContent"; filename="{file.name}"\r\n'.encode(),
            b"Content-Type: image/png\r\n\r\n",
            file.read_bytes(),
            f"\r\n--{boundary}--\r\n".encode(),
        ])
        request = urllib.request.Request(ASSETS_URL, data=body, method="POST", headers={
            "x-api-key": self.key,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        })
        return self._send(request)

    def wait(self, operation):
        path = operation.get("path", "")
        if not path.startswith("operations/"):
            raise RuntimeError(f"Unexpected operation: {operation!r}")
        started = time.monotonic()
        while not operation.get("done"):
            if time.monotonic() - started > POLL_LIMIT_SECONDS:
                raise RuntimeError(f"Timed out waiting for {path}")
            time.sleep(POLL_SECONDS)
            request = urllib.request.Request(OPERATIONS_URL + path, headers={"x-api-key": self.key})
            operation = self._send(request)
        if "error" in operation:
            raise RuntimeError(f"Upload failed: {operation['error']!r}")
        asset_id = (operation.get("response") or {}).get("assetId")
        if not str(asset_id or "").isdecimal():
            raise RuntimeError(f"No asset id in {operation!r}")
        return int(asset_id)

    def image_id(self, decal_id):
        """An ImageLabel needs the Image asset behind a Decal, not the Decal itself.

        Fetches the decal's content through Open Cloud asset delivery: a Decal is a
        small XML file whose <url> names the image id; an Image is PNG bytes (the id
        is already an image). Returns (image_id, how) and falls back to the decal id
        when delivery is not permitted for this key.
        """
        try:
            meta = self._send(urllib.request.Request(DELIVERY_URL + str(decal_id), headers={"x-api-key": self.key}))
            location = meta.get("location") or ""
            if not location.startswith("https://"):
                return decal_id, f"no delivery location ({meta!r:.120})"
            with urllib.request.urlopen(location, timeout=60) as response:
                content = response.read(200000)
        except RuntimeError as exc:
            return decal_id, f"delivery failed: {exc}"
        if content.startswith(b"\x89PNG"):
            return decal_id, "already an image"
        match = re.search(rb"<url>[^<]*?id=(\d+)\s*</url>", content)
        if match:
            return int(match.group(1)), "resolved from decal"
        return decal_id, f"unrecognised content {content[:60]!r}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="list what would upload (default)")
    mode.add_argument("--upload", action="store_true", help="upload for real and write UiAssetIds.json")
    parser.add_argument("--only", default="", help="comma-separated sprite names to consider")
    parser.add_argument("--sprites", action="store_true", help="regenerate UiSprites.json from the manifest")
    args = parser.parse_args(argv)

    if args.sprites:
        sync_sprites()

    only = {name.strip() for name in args.only.split(",") if name.strip()}
    files = sprite_files()
    ids = load_json(IDS_FILE)
    todo = pending(files, ids, only)
    too_big = [f for f in todo if f.stat().st_size > MAX_BYTES]
    if too_big:
        raise ValueError("Over 20 MB: " + ", ".join(f.name for f in too_big))

    if not args.upload:
        print(f"DRY RUN: {len(files)} sprites found, {len(ids)} already uploaded, {len(todo)} would upload")
        for file in todo:
            print(f"  would upload {file.stem:28s} {file.stat().st_size:>8d} bytes")
        if not os.environ.get("ROBLOX_API_KEY"):
            print("(ROBLOX_API_KEY is not set; --upload would refuse to run)")
        print("Nothing was uploaded. Re-run with --upload to upload.")
        return 0

    key = os.environ.get("ROBLOX_API_KEY", "").strip()
    if not key:
        raise ValueError("ROBLOX_API_KEY is required for --upload")
    cloud = Cloud(key, creator_from_env())
    for index, file in enumerate(todo, 1):
        decal_id = cloud.wait(cloud.upload(file))
        asset_id, how = cloud.image_id(decal_id)
        ids[file.stem] = asset_id
        # Saved after every upload so an interrupted run never repeats one.
        write_json(IDS_FILE, ids)
        print(f"[{index}/{len(todo)}] {file.stem} -> rbxassetid://{asset_id} (decal {decal_id}: {how})")
    print(f"Uploaded {len(todo)}; {IDS_FILE.relative_to(ROOT)} now lists {len(ids)} ids")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
