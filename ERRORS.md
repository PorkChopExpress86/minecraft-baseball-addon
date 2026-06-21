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
