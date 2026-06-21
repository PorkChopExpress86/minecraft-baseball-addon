# Baseball Addon — Project Notes

## Overview
Minecraft Bedrock Edition addon adding baseball-themed gear: bat, helmet, jersey, pants, cleats, catcher's mask, and catcher's vest. The bat script applies SSB-style knockback + fire damage on hit.

## File Structure
```
Baseball_BP/          Behavior pack (items, recipes, scripts, manifest)
  items/              One .json per item (identifier, armor, wearable, icon, durability)
  recipes/            Crafting table recipes for every item
  scripts/            bat_knockback.js — @minecraft/server 2.0.0 event handler
  texts/              en_US.lang — display names for all items
Baseball_RP/          Resource pack (models, textures, attachables, manifest)
  models/entity/      *.geo.json — 3D geometry for each wearable/holdable
  attachables/        *.player.json — binds items to player skeleton
  textures/items/     16x16 item icons (PNG)
  textures/models/    64x32 worn-armor atlases (PNG)
generate_textures.py  Procedural PNG generator — run this after any texture change
validate_addon.py     Static checker — run before every deploy
Install-BaseballAddon.ps1   PowerShell installer/updater for com.mojang
```

## How to Develop

```powershell
# After any change: regenerate textures, validate, deploy
python generate_textures.py
$env:PYTHONIOENCODING="utf-8"; python validate_addon.py
.\Install-BaseballAddon.ps1
```

## Environment
- Platform: Windows 11, standalone Minecraft Bedrock launcher (not UWP Store)
- Pack install path: `%APPDATA%\Minecraft Bedrock\Users\Shared\games\com.mojang` (resource_packs / behavior_packs)
- World saves path: `%APPDATA%\Minecraft Bedrock\Users\<profile-id>\games\com.mojang\minecraftWorlds` (NOT Shared)
- Pack UUIDs: RP = `3038a3ba-3bf7-4049-9620-3d4fdbc702fd`, BP = `2f0a7fe1-4bdf-4190-979e-6fbb7ea95618`
- Current version: `[1, 4, 0]`
- Script API: `@minecraft/server` 2.0.0 (min_engine_version [1, 21, 80])

## Key Files
- `bat_knockback.js` — uses `applyKnockback({x,z}, vertical)` 2-arg form (4-arg form removed in 2.0.0); `setOnFire(seconds)` for fire
- `bat.geo.json` — bat bone rotation `[135, 0, 0]` (barrel points up-forward like a sword; pivot Y=14 sits at handle grip center)
- `helmet.geo.json` / `catcher_mask.geo.json` — binding: `q.item_slot_to_bone_name(context.item_slot)`, pivot `[0, 24, 0]`
- `jersey.geo.json` / `catcher_vest.geo.json` — three bone pairs: body, rightarm, leftarm with binding strings `'body'`, `'rightarm'`, `'leftarm'`

## Gotchas
- **Manifest version bumps require THREE edits**: RP header, BP header, AND the RP dependency line inside BP manifest — miss any one and the packs may fail to resolve
- **validate_addon.py needs UTF-8**: `$env:PYTHONIOENCODING="utf-8"` before running on Windows or it crashes on box-drawing chars
- **Armor render controller** `controller.render.armor` expects exact binding strings — `'body'`, `'rightarm'`, `'leftarm'` (single-quoted MoLang strings, not identifiers)
- **generate_textures.py uses no external libs** — pure stdlib (`struct`, `zlib`, `os`); no PIL/Pillow needed
- Items share pants (`baseball:pants`) and cleats (`baseball:cleats`) between the jersey and catcher vest sets
- **Worlds load their OWN embedded pack copy** from `<world>\resource_packs\` / `<world>\behavior_packs\`, NOT the global Shared library — editing Shared or bumping the `world_*_packs.json` version token does nothing visible; the embedded folder content must be refreshed. `Update-WorldPacks` mirrors source into each world's embedded copy (located by UUID) and aligns the version reference.
- **Editing pack files without bumping the version leaves stale copies** — `Sync-Pack` now hashes (`Test-FolderContentMatches`) and re-syncs on content drift even when versions match
- **Minecraft caches packs in memory while running** — after any install, fully exit to desktop (not just leave the world) and reopen, or changes won't appear
- **World saves are under a user profile ID, NOT Shared** — installer scans all subdirs of `Users\` to find them; Shared only holds pack libraries
- **All scripts use relative paths** — `$PSScriptRoot`, `Path(__file__).parent`, or CWD-relative — so the project can be moved freely without any path edits
- **Do NOT use non-ASCII characters in PS1 string literals** — em dashes `—` and box-drawing chars `──` contain UTF-8 bytes (e.g. `0x94`) that Windows-1252 maps to `"`, silently closing the string and causing parse errors; use `--` instead
