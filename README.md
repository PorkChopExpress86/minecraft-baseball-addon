# Baseball Addon

A Minecraft Bedrock Edition addon that adds a full baseball-themed gear set — bat, helmet, jersey, pants, cleats, catcher's mask, and catcher's vest. The Home Run Bat applies Smash-Bros-style knockback and sets targets on fire when it lands a hit.

## Requirements

- Minecraft Bedrock Edition **1.21.80 or higher**
- **Beta APIs** enabled on the world (required for the bat's knockback script)

## Install

1. Download [`Baseball_Addon.mcaddon`](Baseball_Addon.mcaddon) from this repo.
2. Open it — on Windows, double-click it; on iPad/iPhone, tap it in the Files app (or AirDrop it over). Minecraft launches and imports both packs automatically.
3. In your world's settings, activate both **Baseball Addon BP** and **Baseball Addon RP** under Add-Ons, then enable **Beta APIs** under Experiments.

Full step-by-step instructions (including manual install, crafting recipes for every item, and a troubleshooting table) are in [install_instructions.md](install_instructions.md).

## Items

| Item | Slot | Notes |
|---|---|---|
| Home Run Bat | Mainhand | Craftable weapon; SSB-style knockback + fire on hit |
| Baseball Helmet | Head | |
| Baseball Jersey | Chest | |
| Baseball Pants | Legs | |
| Baseball Cleats | Feet | |
| Catcher's Mask | Head | Full-head cage, face stays visible |
| Catcher's Vest | Chest | Heavier armor than the jersey |

Give yourself the full set with `/give @s baseball:bat` etc. (see [install_instructions.md](install_instructions.md) for the full command list and crafting recipes).

## Development

```powershell
# After any change: regenerate textures, validate, deploy, and rebuild the .mcaddon
python generate_textures.py
$env:PYTHONIOENCODING="utf-8"; python validate_addon.py
.\Install-BaseballAddon.ps1
```

`Install-BaseballAddon.ps1` installs/updates the packs into your local `com.mojang` folder and existing world saves, then rebuilds `Baseball_Addon.mcaddon` from current source. Run `python build_mcaddon.py` directly if you just want the `.mcaddon` file without a full local install.

See [CLAUDE.md](CLAUDE.md) for the full project structure, environment notes, and known gotchas, and [ERRORS.md](ERRORS.md) for a log of bugs hit during development and how they were fixed.

## License

[MIT](LICENSE)
