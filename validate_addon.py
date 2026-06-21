#!/usr/bin/env python3
"""
validate_addon.py — Static integrity checker for the Baseball Addon.

Catches the eight most common "silent failure" bugs before you load in Minecraft:
  1. JSON syntax errors
  2. Duplicate or reused UUIDs
  3. BP→RP manifest UUID dependency mismatch
  4. Item icon not registered in item_texture.json
  5. item_texture.json entry points to a missing PNG
  6. Attachable identifier doesn't match a BP item identifier
  7. Attachable geometry identifier doesn't match a .geo.json description identifier
  8. en_US.lang missing display-name entry for an item

Usage:
  python3 validate_addon.py
"""

import json, os, sys, re
from pathlib import Path

ROOT   = Path(__file__).parent
BP     = ROOT / "Baseball_BP"
RP     = ROOT / "Baseball_RP"
PASS   = "\033[32m PASS\033[0m"
FAIL   = "\033[31m FAIL\033[0m"
errors = []

def fail(msg):
    errors.append(msg)
    print(f"{FAIL}  {msg}")

def ok(msg):
    print(f"{PASS}  {msg}")

def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"JSON syntax error in {path}: {e}")
        return None
    except FileNotFoundError:
        fail(f"Missing required file: {path}")
        return None

# Load manifests early — several checks below depend on them
bp_manifest = load_json(BP / "manifest.json")
rp_manifest = load_json(RP / "manifest.json")

# ── 1. JSON validity ──────────────────────────────────────────────────────────
print("\n── 1. JSON syntax ──────────────────────────────────────────────────")
json_files = list(BP.rglob("*.json")) + list(RP.rglob("*.json"))
for f in sorted(json_files):
    data = load_json(f)
    if data is not None:
        ok(f.relative_to(ROOT))

# ── 2. UUID uniqueness ────────────────────────────────────────────────────────
print("\n── 2. UUID uniqueness ──────────────────────────────────────────────")
uuid_pat = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)

def extract_uuids_by_role(manifest_data):
    """Return sets of UUIDs split by role: header, modules, dependencies."""
    header_uuids = set()
    module_uuids = set()
    dep_uuids    = set()
    if not manifest_data:
        return header_uuids, module_uuids, dep_uuids
    h = manifest_data.get("header", {}).get("uuid", "")
    if h: header_uuids.add(h.lower())
    for m in manifest_data.get("modules", []):
        u = m.get("uuid", "")
        if u: module_uuids.add(u.lower())
    for d in manifest_data.get("dependencies", []):
        u = d.get("uuid", "")
        if u: dep_uuids.add(u.lower())
    return header_uuids, module_uuids, dep_uuids

bp_h, bp_m, bp_d = extract_uuids_by_role(bp_manifest)
rp_h, rp_m, _    = extract_uuids_by_role(rp_manifest)

# Within each manifest, header + module UUIDs must be distinct
for uid in bp_h & bp_m:
    fail(f"UUID {uid} used for both BP header and a BP module")
for uid in rp_h & rp_m:
    fail(f"UUID {uid} used for both RP header and a RP module")

# Across packs, own-identity UUIDs must not collide
# (BP dep→RP header is intentional and excluded from this check)
cross_collide = (bp_h | bp_m) & (rp_h | rp_m)
for uid in cross_collide:
    fail(f"UUID {uid} used in both BP and RP identity fields (must be unique)")

all_uuids = bp_h | bp_m | bp_d | rp_h | rp_m
ok(f"No forbidden UUID collisions (found {len(all_uuids)} total UUIDs)")

# ── 3. BP→RP manifest dependency ─────────────────────────────────────────────
print("\n── 3. Manifest BP→RP dependency ────────────────────────────────────")
if bp_manifest and rp_manifest:
    rp_header_uuid = rp_manifest.get("header", {}).get("uuid", "").lower()
    dep_uuids = [d.get("uuid", "").lower()
                 for d in bp_manifest.get("dependencies", [])
                 if "uuid" in d]
    if rp_header_uuid in dep_uuids:
        ok(f"BP dependencies include RP header UUID ({rp_header_uuid})")
    else:
        fail(f"BP manifest does not list RP header UUID {rp_header_uuid} in dependencies")

# ── 4 & 5. item_texture.json completeness + PNG files exist ──────────────────
print("\n── 4+5. item_texture.json ↔ PNG files ──────────────────────────────")
item_tex_path = RP / "textures" / "item_texture.json"
item_tex = load_json(item_tex_path)
registered_textures = {}
if item_tex:
    for short_name, entry in item_tex.get("texture_data", {}).items():
        tex_path_str = entry.get("textures", "")
        registered_textures[short_name] = tex_path_str
        # Minecraft appends .png if missing
        png_path = RP / (tex_path_str + ".png") if not tex_path_str.endswith(".png") else RP / tex_path_str
        if png_path.exists():
            ok(f"  {short_name} → {tex_path_str}.png exists")
        else:
            fail(f"  {short_name} → {tex_path_str}.png MISSING")

# ── 6. BP item identifiers ↔ attachable identifiers ──────────────────────────
print("\n── 6. BP items ↔ RP attachables ────────────────────────────────────")
bp_item_ids = set()
for f in sorted((BP / "items").glob("*.json")):
    data = load_json(f)
    if data:
        ident = data.get("minecraft:item", {}).get("description", {}).get("identifier", "")
        bp_item_ids.add(ident)
        # Check icon texture is registered
        icon = data.get("minecraft:item", {}).get("components", {}).get("minecraft:icon", {})
        tex_key = icon.get("texture", icon) if isinstance(icon, dict) else icon
        if tex_key in registered_textures:
            ok(f"  {ident}: icon '{tex_key}' registered in item_texture.json")
        else:
            fail(f"  {ident}: icon texture '{tex_key}' NOT in item_texture.json")

for f in sorted((RP / "attachables").glob("*.json")):
    data = load_json(f)
    if data:
        desc = data.get("minecraft:attachable", {}).get("description", {})
        att_id = desc.get("identifier", "")
        item_keys = list(desc.get("item", {}).keys())
        item_id = item_keys[0] if item_keys else att_id
        if item_id in bp_item_ids:
            ok(f"  Attachable '{att_id}' → BP item '{item_id}' exists")
        else:
            fail(f"  Attachable '{att_id}' references unknown BP item '{item_id}'")

# ── 7. Attachable geometry ↔ .geo.json identifier ────────────────────────────
print("\n── 7. Attachable geometry ↔ .geo.json identifiers ─────────────────")
geo_identifiers = set()
for f in sorted((RP / "models" / "entity").glob("*.geo.json")):
    data = load_json(f)
    if data:
        for geo in data.get("minecraft:geometry", []):
            geo_id = geo.get("description", {}).get("identifier", "")
            geo_identifiers.add(geo_id)

for f in sorted((RP / "attachables").glob("*.json")):
    data = load_json(f)
    if data:
        desc = data.get("minecraft:attachable", {}).get("description", {})
        att_id = desc.get("identifier", "")
        geo_ref = desc.get("geometry", {}).get("default", "")
        if geo_ref in geo_identifiers:
            ok(f"  Attachable '{att_id}': geometry '{geo_ref}' found in geo files")
        else:
            fail(f"  Attachable '{att_id}': geometry '{geo_ref}' NOT found in any .geo.json")

# ── 8. en_US.lang display name coverage ──────────────────────────────────────
print("\n── 8. en_US.lang display names ─────────────────────────────────────")
lang_path = BP / "texts" / "en_US.lang"
lang_keys = set()
if lang_path.exists():
    for line in lang_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            lang_keys.add(line.split("=")[0].strip())

for item_id in sorted(bp_item_ids):
    lang_key = f"item.{item_id}.name"
    if lang_key in lang_keys:
        ok(f"  {lang_key}")
    else:
        fail(f"  '{lang_key}' missing from en_US.lang")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "─" * 60)
if errors:
    print(f"\033[31m{len(errors)} error(s) found:\033[0m")
    for e in errors:
        print(f"  • {e}")
    sys.exit(1)
else:
    print(f"\033[32mAll checks passed — addon looks structurally sound.\033[0m")
    print("\nNext step: load in Minecraft with Creator > Content Log enabled.")
    print("In-game smoke test: /give @s baseball:bat  (and the rest of the set)")
