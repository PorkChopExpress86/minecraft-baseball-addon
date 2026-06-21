# Baseball Add-on — Installation Instructions

## Prerequisites

- Minecraft Bedrock Edition **version 1.21.80 or higher** — the bat script uses the `@minecraft/server` 2.x API that shipped with 1.21.80
- The `Baseball_Addon.mcaddon` file (contains both packs)
- The bat's SSB-style knockback requires **Beta APIs** to be enabled on your world

> **Re-installing / updating?** If import fails with "duplicate detected", delete the previously-installed Baseball Addon packs first (in My Packs / the Behavior- and Resource-pack lists), then import again.

---

## Windows (PC)

### Step 1 — Install the add-on

Double-click `Baseball_Addon.mcaddon`. Minecraft will open and automatically import both packs. You'll see a confirmation message in-game.

**Manual install (alternative):** If double-clicking doesn't work, open File Explorer and paste the following into the address bar:

```
%APPDATA%\Minecraft Bedrock\Users\Shared\games\com.mojang
```

Then copy the `Baseball_BP` folder into `behavior_packs` and `Baseball_RP` into `resource_packs`.

### Step 2 — Enable the packs on a world

1. Launch Minecraft and go to **Play → Create New World** (or edit an existing one)
2. Scroll to **Add-Ons** in the left sidebar
3. Under **Behavior Packs**, find "Baseball Addon BP" and tap **+** to activate it
4. Under **Resource Packs**, find "Baseball Addon RP" and tap **+** to activate it

### Step 3 — Enable Script API (required for the bat knockback)

1. Still on the world settings screen, scroll to **Experiments**
2. Enable **"Beta APIs"** (also labeled "GameTest Framework" on some versions)
3. Accept the warning prompt

### Step 4 — Test it

Create/load the world, then run these commands:

```
/give @s baseball:bat
/give @s baseball:helmet
/give @s baseball:jersey
/give @s baseball:pants
/give @s baseball:cleats
/give @s baseball:catcher_mask
/give @s baseball:catcher_vest
```

---

## iPad (iOS / iPadOS)

### Step 1 — Install the add-on

Transfer `Baseball_Addon.mcaddon` to your iPad via AirDrop, iCloud Drive, Google Drive, or a USB cable. Open the **Files** app and tap `Baseball_Addon.mcaddon` — Minecraft will launch automatically and import both packs.

> If tapping the file doesn't open Minecraft, long-press the file → **Share → Copy to Minecraft**.

### Step 2 — Enable the packs on a world

1. Launch Minecraft → **Play → Create New World** (or edit an existing one)
2. Tap **Add-Ons** in the left menu
3. Under **Behavior Packs**, find "Baseball Addon BP" and tap **+**
4. Under **Resource Packs**, find "Baseball Addon RP" and tap **+**

### Step 3 — Enable Script API

1. Scroll to **Experiments** in the world settings
2. Enable **"Beta APIs"**
3. Confirm the warning

### Step 4 — Test it

Enter the world and run the same `/give` commands listed above.

---

## Getting the Items

### Quickest method — commands

If cheats are enabled on your world, open chat and run the `/give` commands from Step 4 above.

### Crafting recipes (all use a Crafting Table)

**Home Run Bat**
```
[ D ]
[PPP]
[ S ]
```
Diamond on top, three Oak Planks across the middle, Stick on the bottom.

**Helmet**
```
[WWW]
[L L]
```
Three White Wool across the top, Leather in the left and right of the second row.

**Jersey**
```
[L L]
[WWW]
[WWW]
```
Leather on the shoulders, then two full rows of White Wool.

**Pants**
```
[WWW]
[W W]
[W W]
```
Standard leggings shape, all White Wool.

**Cleats**
```
[L L]
[I I]
```
Leather on top-left and top-right, Iron Ingots below each.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Items show a `?` icon | `item_texture.json` short-name mismatch — re-copy the RP |
| Armor renders nothing | Geometry identifier doesn't match attachable — re-copy the RP |
| Bat knockback doesn't work | Beta APIs experiment is not enabled |
| All translations are missing | `en_US.lang` has a UTF-8 BOM — re-export the file without BOM |
| Pack doesn't appear in Add-Ons list | JSON syntax error in a manifest — run `validate_addon.py` on a PC first |
