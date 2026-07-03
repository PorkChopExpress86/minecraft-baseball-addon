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
  animations/         *.animation.json — hold_first/third_person poses (orients held items; see bat note)
  textures/items/     16x16 item icons (PNG)
  textures/models/    64x32 worn-armor atlases (PNG)
generate_textures.py  Procedural PNG generator — run this after any texture change
validate_addon.py     Static checker — run before every deploy
build_mcaddon.py      Zips Baseball_BP + Baseball_RP into Baseball_Addon.mcaddon (iPad/iPhone install file)
Baseball_Addon.mcaddon  Build output (regenerated every run, not hand-edited) — send this to iOS devices
Install-BaseballAddon.ps1   PowerShell installer/updater for com.mojang; also runs build_mcaddon.py at the end
```

## How to Develop

```powershell
# After any change: regenerate textures, validate, deploy
python generate_textures.py
$env:PYTHONIOENCODING="utf-8"; python validate_addon.py
.\Install-BaseballAddon.ps1
```

`Install-BaseballAddon.ps1` ends by running `build_mcaddon.py`, which zips `Baseball_BP` + `Baseball_RP` into `Baseball_Addon.mcaddon` at the project root — the file to send to iPad/iPhone (AirDrop, email, or a cloud-drive app; tapping it in Files opens Minecraft and imports both packs). It always rebuilds from current source, so it never goes stale after a version bump. Run `python build_mcaddon.py` directly if you want the file without doing a full local install/deploy.

## Environment
- Platform: Windows 11, standalone Minecraft Bedrock launcher (not UWP Store)
- Pack install path: `%APPDATA%\Minecraft Bedrock\Users\Shared\games\com.mojang` (resource_packs / behavior_packs)
- World saves path: `%APPDATA%\Minecraft Bedrock\Users\<profile-id>\games\com.mojang\minecraftWorlds` (NOT Shared)
- Pack UUIDs: RP = `3038a3ba-3bf7-4049-9620-3d4fdbc702fd`, BP = `2f0a7fe1-4bdf-4190-979e-6fbb7ea95618`
- Current version: `[1, 4, 1]`
- Script API: `@minecraft/server` 2.0.0 (min_engine_version [1, 21, 80])

## Key Files
- `bat_knockback.js` — uses `applyKnockback({x,z}, vertical)` 2-arg form (4-arg form removed in 2.0.0); `setOnFire(seconds)` for fire
- **Held-item orientation is controlled by HOLD ANIMATIONS, not the geometry's baked `rotation`** (`animation.baseball.bat.hold_third_person` / `hold_first_person` in `Baseball_RP/animations/bat.animation.json`, wired via `animations` + `scripts.animate` in `bat.player.json`). POSITION is controlled by where the grip is MODELED: Bedrock renders hand-bound geometry **24 units lower than modeled** (undocumented engine quirk, matches vanilla `trident.geo.json`), so **model the grip at y≈21-24** and set the bone pivot to `[0, 24, 0]` (the pivot is only the rotation center — put it at the grip so hold-animation rotations spin around the fist). The earlier "pivot `[0,0,0]` seats in the fist" model (2026-06-24) was wrong — it actually rendered the whole bat 24 units below the fist (player gripping the barrel, handle at their shins, visible in the 06-24 screenshots). The baked geometry `rotation` is kept at `[0,0,0]`.
- **2026-06-24 finding corrected 2026-06-30**: the original session concluded baked geometry `rotation` was "overridden by Minecraft's default hold pose" because `hold_third_person` appeared to have no effect in-game. Root cause was actually a `"comment"` key left inside the `bat` bone's rotation object in `bat.animation.json` — `"comment"` is a documented-safe convention inside geometry **cubes**, but the official `actor_animation:1.8.0` schema does NOT list `comment` as a valid property of an animation bone (only `relative_to`, `position`, `rotation`, `scale` are allowed), so it was silently breaking the third-person pose specifically. `hold_first_person` had no `comment` key and was presumably applying correctly the whole time. Lesson: never put a `"comment"` field inside an animation bone's pose object — geometry cubes tolerate it, animation bones don't.
- `bat.geo.json` — knob at local y=21, barrel up the +Y axis to the end cap at y≈49; bone pivot `[0, 24, 0]` (grip at the fist, see position note above). Hold animations (2026-07-01) use vanilla trident wield values as the starting point — third person `rotation [97, -1.5, -49]` + `position [1.5, -2.5, -10.5]`, first person `rotation [152, -9, 25]` + `position [-7, -3, -2]` — which supersede the old `[0,0,135]` guess and its Z-axis calibration (that was derived while the pose was broken/misplaced; treat it as void). Positive X pitches an upright-modeled weapon forward. Still needs an in-game screenshot check; tweak per-axis from these values. The offline previewer `scratchpad/render_bat.py` models the *baked* rotation only, so it does NOT predict the hold-animation pose — trust in-game screenshots for held-item orientation.
- `helmet.geo.json` / `catcher_mask.geo.json` — binding: `q.item_slot_to_bone_name(context.item_slot)`, pivot `[0, 24, 0]`
- **Head gear must not hide the player's face** (player head cube = y24-32, face = its front/north UV region `[8,8]..[15,15]`). Two working approaches in this addon: (1) `helmet.geo.json` = a CROWN cube on TOP of the head (`y30-34`) + brim at brow `y30` — geometry simply doesn't cover the face (uses opaque `armor` material, solid-navy texture). (2) `catcher_mask.geo.json` = full-head cap cube, but `armor_catcher_mask()` in `generate_textures.py` clears the face UV region to TRANSPARENT (`rect(8,8,15,15, TRANSPARENT)`) AND the attachable uses `entity_alphatest` material so the face shows through the cage. Don't give the helmet a full opaque head shell — it blanks the face.
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
