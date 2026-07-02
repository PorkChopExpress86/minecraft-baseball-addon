# Errors Log

## New addon content not visible in already-created worlds

**Symptom:** After editing a pack file (the bat angle fix in `bat.geo.json`, `[45,0,0]` -> `[135,0,0]`) and running the installer, existing worlds still rendered the old geometry. Installer reported success.
**Root cause:** Two independent gaps. (1) Each world stores its OWN embedded copy of the packs in `<world>\resource_packs\` and `<world>\behavior_packs\` — that embedded copy is what the world loads, not the global Shared library. The installer only updated Shared and the `world_*_packs.json` version token; it never refreshed embedded content. (2) `Sync-Pack` decided whether to copy purely by version-number comparison, so a content edit made WITHOUT a version bump (source stayed 1.4.0) left the Shared copy stale too — it reported "already up to date" and copied nothing.
**Fix:** Reworked `Install-BaseballAddon.ps1`: added `Test-FolderContentMatches` (SHA256 tree compare) so `Sync-Pack` re-syncs on content drift even at equal versions; reworked `Update-WorldPacks` to locate each world's embedded pack folder by UUID and mirror source content into it (via `Copy-PackContent`), in addition to aligning the version reference. Verified all embedded copies hash-match source afterward. NOTE: Minecraft must be fully closed (exit to desktop) and reopened for changes to load — a running client holds packs in memory.
**Date:** 2026-06-20

---

## Minecraft not found at expected UWP path

**Symptom:** Installer script found no valid com.mojang at `%LOCALAPPDATA%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang`
**Root cause:** User runs the new standalone Minecraft Bedrock launcher, not the UWP Microsoft Store version. The new launcher uses `%APPDATA%\Minecraft Bedrock\Users\Shared\games\com.mojang`.
**Fix:** Updated `Get-ComMojangPath` in `Install-BaseballAddon.ps1` to check `$MCRoamingShared` (`%APPDATA%\Minecraft Bedrock\Users\Shared\games\com.mojang`) first with a bare `Test-Path` (no subfolder check), then fall back to legacy paths.
**Date:** 2026-06-19

---

## Packs installed to wrong com.mojang — not visible in Minecraft

**Symptom:** Packs were copied successfully but did not appear in Minecraft's resource/behavior pack lists.
**Root cause:** Manually created `%LOCALAPPDATA%\Packages\...\LocalState\games\com.mojang\resource_packs` so the installer could run, but Minecraft reads from the new launcher path instead.
**Fix:** Directly copied packs to `%APPDATA%\Minecraft Bedrock\Users\Shared\games\com.mojang\{resource_packs,behavior_packs}`. Installer updated to find this path automatically.
**Date:** 2026-06-19

---

## validate_addon.py crashes with UnicodeEncodeError on Windows

**Symptom:** `UnicodeEncodeError: 'charmap' codec can't encode characters in position 2-3` when running `python validate_addon.py`
**Root cause:** The script prints box-drawing characters (─) which the default Windows cp1252 console encoding cannot handle.
**Fix:** Set `$env:PYTHONIOENCODING="utf-8"` before running: `$env:PYTHONIOENCODING="utf-8"; python validate_addon.py`
**Date:** 2026-06-20

---

## PS1 parse error from em dash in string literals

**Symptom:** `Unexpected token '}'` errors cascading through `Install-BaseballAddon.ps1` starting at the first closing brace after a `Write-*` call containing `—` or `──`.
**Root cause:** The file is UTF-8 without BOM. PowerShell 5.1 reads it with the Windows-1252 code page. The UTF-8 encoding of `—` (U+2014) is `E2 80 94`; byte `0x94` is `"` in Windows-1252, which prematurely closes the double-quoted string and corrupts the rest of the block.
**Fix:** Replaced all `—` with `--` and `──` with `--` inside PS1 string literals. Do not use non-ASCII characters in PowerShell string literals on this machine.
**Date:** 2026-06-20

---

## World saves not found — installer reported 0 worlds

**Symptom:** Installer's world-update phase printed `Checked 0 world(s)` despite two worlds having the addon applied.
**Root cause:** World saves live under a user profile directory (`Users\<profile-id>\games\com.mojang\minecraftWorlds`), not under `Users\Shared\` where packs are installed. The installer was only scanning the Shared path.
**Fix:** Updated the main block of `Install-BaseballAddon.ps1` to enumerate all subdirectories of `%APPDATA%\Minecraft Bedrock\Users\` and call `Update-WorldPacks` for each `minecraftWorlds` directory found.
**Date:** 2026-06-20

---

## Bat held straight down instead of like a sword

**Symptom:** Equipped bat pointed barrel straight downward rather than upward (sword-like) when held in hand.
**Root cause:** `bat.geo.json` bone rotation was `[45, 0, 0]`. The barrel cubes sit below the pivot (Y=-7 to 6, pivot Y=14), so at 45° X-rotation the barrel points down-forward. Needed an additional 90° to flip the barrel above the pivot.
**Fix:** Changed rotation in `Baseball_RP/models/entity/bat.geo.json` from `[45, 0, 0]` to `[135, 0, 0]`. The barrel now points up-forward; the knob drops below the hand; handle pivot at Y=14 remains in the grip area.
**Date:** 2026-06-20

---

## Baseball helmet completely hid the player's face

**Symptom:** Wearing `baseball:helmet` rendered a solid navy block over the entire head — no face visible. (Asked to ensure head gear lets the face show.)
**Root cause:** The cap geometry was a full 8×8×8 shell enclosing the whole head (`origin [-4,24,-4]`, `inflate 0.5`), and `armor_helmet()` paints the texture fully opaque navy with the opaque `armor` material. Nothing was transparent over the face and the geometry physically covered it. (The brim was also at `y24` = chin level, not the brow.)
**Fix:** Rebuilt `helmet.geo.json`: cap is now a CROWN on top of the head (`origin [-4.5,30,-4.5]`, `size [9,4,9]`) + brim raised to brow (`origin [-3.5,30,-8]`) + button on top — the geometry no longer covers the face region (y24-30). No texture/material change needed. (Contrast: `catcher_mask.geo.json` keeps a full cap but `armor_catcher_mask()` clears the face UV to transparent + uses `entity_alphatest`, so its face shows through the cage — that one was already correct.)
**Date:** 2026-06-24

---

## Held bat renders barrel-down and offset from the hand regardless of geometry rotation

**Symptom:** The equipped bat always rendered with the red barrel pointing straight DOWN and floating off to the player's side, never seated in the fist. Tried baked bone rotations `[135,0,0]`, `[45,0,0]`, `[-135,0,0]` (and pivots 18/14/4/0) — all looked barrel-down in-game. Changing the baked rotation a full 180° did not flip the bat.
**Root cause:** For a held-item attachable, the geometry bone's baked `rotation` is **overridden by Minecraft's default hold pose** — it does not orient the held item (a 180° change producing no flip proved this). Compounding it: an offline orthographic renderer that assumes "model +Y = world up" mispredicts the result; the real main-hand item frame differs (empirically, rotating about model-X swings the bat *sideways*, so model-X ≈ world forward/back and the lift/pitch axis is model-Z). The earlier 2026-06-20 entry's `[45]→[135]` "fix" was based on the wrong assumption that the baked rotation controls orientation. Also: a long bat (~28px) pointing down throws the barrel ~1.75 blocks from the hand, which reads as "not in the hand."
**Fix (in progress as of this date):** Switched orientation control to **hold animations** — added `Baseball_RP/animations/bat.animation.json` (`animation.baseball.bat.hold_first_person` / `hold_third_person`) wired via `animations` + `scripts.animate` in `bat.player.json`; reset the baked geometry `rotation` to `[0,0,0]` and pivot to `[0,0,0]` (grip at knob). Orientation is now tuned via the hold-animation `rotation` (calibrating on the Z axis, currently `[0,0,135]`; sign flip = forward-vs-back). The bat visibly responded to the hold animation (confirming the mechanism); final angle pending the next in-game screenshot. Trust in-game screenshots over the offline renderer for held-item orientation.
**Date:** 2026-06-24

---

## Bat rendered 24 units below the fist — player gripped the barrel, handle at their shins

**Symptom:** In every third-person screenshot the player's fist was on the red BARREL with the tan handle dangling down to shin level — the whole bat sat ~1.5 blocks too low. This was the real cause of the persistent "not seated in the hand" look that the 06-24 session tried to fix by moving the bone pivot.
**Root cause:** Bedrock renders hand-bound held geometry (root bone bound via `q.item_slot_to_bone_name`) **24 units lower than modeled** — an undocumented engine quirk, confirmed against vanilla `trident.geo.json` (grip modeled at y≈24, pivot `[0,24,0]`). The bat's grip was modeled at y=0 with pivot `[0,0,0]`, so the knob landed 24 units below the fist and only the barrel top reached the hand. The 06-24 calibration ("pivot `[0,0,0]` seats the knob in the fist"; "at rest the barrel points world-DOWN"; "lift axis is Z") was all derived while the model sat 24 units off — pivot changes only appeared to move the bat because nonzero baked rotations were active at the time. Treat that calibration as void. The `[0,0,135]` hold rotation built on it was equally unfounded.
**Fix:** Rebuilt per the minecraft-addon skill `references/rendering.md` > "Held-Item Hand Positioning": shifted all `bat.geo.json` cubes +21 in Y (knob y21-23, end cap y≈49) so the grip is modeled at y≈21-24, set pivot `[0, 24, 0]` (pivot = rotation center only; put it at the grip so hold rotations spin around the fist), and replaced both hold-animation poses with vanilla trident wield values — third person `rotation [97,-1.5,-49]` + `position [1.5,-2.5,-10.5]`, first person `rotation [152,-9,25]` + `position [-7,-3,-2]`. Bumped to v1.4.1 (three-place bump), validated, deployed to Shared + all 3 worlds. In-game screenshot verification still pending; tweak per-axis from the trident values if needed. Positive X pitches an upright-modeled weapon forward.
**Date:** 2026-07-01
