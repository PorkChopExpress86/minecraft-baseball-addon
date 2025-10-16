# Spawn an armor stand and equip full baseball uniform for visual preview
summon armor_stand ~ ~ ~ minecraft:armor_stand
# Give it a moment, then target the nearest one
replaceitem entity @e[type=armor_stand,c=1,rm=0] slot.armor.head 0 baseball:helmet 1
replaceitem entity @e[type=armor_stand,c=1,rm=0] slot.armor.chest 0 baseball:jersey 1
replaceitem entity @e[type=armor_stand,c=1,rm=0] slot.armor.legs 0 baseball:pants 1
replaceitem entity @e[type=armor_stand,c=1,rm=0] slot.armor.feet 0 baseball:cleats 1
replaceitem entity @e[type=armor_stand,c=1,rm=0] slot.weapon.mainhand 0 baseball:bat 1
replaceitem entity @e[type=armor_stand,c=1,rm=0] slot.weapon.offhand 0 baseball:glove 1
