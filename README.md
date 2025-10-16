# Minecraft Baseball Addon

A comprehensive baseball-themed addon for Minecraft Bedrock Edition, featuring custom armor, weapons, and throwable baseballs perfect for iPad and other devices.

## Features
- **Baseball Bat**: A powerful wooden weapon that deals 7 damage
- **Baseball Glove**: A leather shield that can block attacks
- **Baseball**: Throwable projectile that deals 6 damage and can be picked up after throwing
- **Baseball Helmet**: Armor with eye black effect (requires custom texture)
- **Baseball Jersey**: Chest armor with baseball uniform design
- **Baseball Pants**: Leg armor styled like baseball pants
- **Baseball Cleats**: Foot armor that looks like baseball shoes

## Installation Instructions for iPad/Bedrock Edition

1. **Download the latest release**:
   - Visit: https://github.com/PorkChopExpress86/minecraft-baseball-addon/releases
   - Download `BaseballAddon.mcaddon` (v1.0.2 or later)

2. **Install on iPad/Mobile Device**:
   - Tap the downloaded `.mcaddon` file in Safari or Files app
   - Minecraft will open automatically and import both packs
   - You'll see "Import Successful" messages

3. **Enable in World**:
   - Create a new world or edit an existing one
   - Go to Behavior Packs and activate "Baseball Addon BP"
   - Go to Resource Packs and activate "Baseball Addon RP"
   - Enable "Experimental Features" if prompted
   - **Important**: Make sure both packs show a checkmark/enabled state

## Crafting Recipes

### Baseball Bat
```
  S
 S
S
```
(S = Stick)

### Baseball Glove
```
L L
LLL
 L
```
(L = Leather)

### Baseball (Makes 4)
- 1 Leather + 2 String

### Baseball Armor
All armor pieces use standard armor crafting patterns with leather.

## Texture Notes
The addon includes placeholder texture files (.txt). You'll need to create actual 16x16 PNG images for:
- `baseball_bat.png`
- `baseball_glove.png`
- `baseball.png`
- `baseball_helmet.png`
- `baseball_jersey.png`
- `baseball_pants.png`
- `baseball_cleats.png`

For the eye black effect, edit the armor layer textures to include black stripes under the eye area.

## Compatibility
- Minecraft Bedrock Edition 1.19.0+
- Compatible with iPad, mobile devices, and other Bedrock platforms
- Requires experimental features enabled

## Usage
1. Craft your baseball equipment using leather and sticks
2. Equip the baseball helmet for eye black effect
3. Use the baseball bat as a weapon
4. Equip the baseball glove as a shield
5. Throw baseballs at enemies - they'll drop and can be picked up!

Enjoy your baseball adventure in Minecraft!

### Quick in-game preview (commands)
- Give yourself the kit: `/function baseball/kit`
- Spawn a preview armor stand wearing the uniform and holding items: `/function baseball/spawn_preview`

### Getting Individual Items
Use these commands (requires cheats enabled):
```
/give @p baseball:baseball 16
/give @p baseball:bat
/give @p baseball:glove
/give @p baseball:helmet
/give @p baseball:jersey
/give @p baseball:pants
/give @p baseball:cleats
```

## Troubleshooting

**Items not showing in Creative inventory?**
1. Make sure you downloaded **v1.0.2 or later** (earlier versions had bugs)
2. Verify both packs are enabled in world settings (not just added)
3. Check that Experimental Features are enabled
4. Try creating a fresh new world with the packs enabled from the start
5. On iPad, completely close and reopen Minecraft after importing

**Can't find items in Creative tabs?**
- Search for "baseball" in the Creative search bar
- Check these categories: Equipment (armor/tools), Items (baseball projectile)
- Use `/give` commands or `/function baseball/kit` instead

**Items have no texture?**
- Make sure the Resource Pack (RP) is enabled along with the Behavior Pack (BP)
- Check that both packs show up in Settings → Global Resources

Tip: You may need cheats enabled to run functions. In world settings, toggle "Activate Cheats."