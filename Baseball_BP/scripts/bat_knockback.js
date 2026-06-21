import { world } from "@minecraft/server";

// Applies SSB-style Home Run Bat knockback: massive upward + outward launch.
//
// Uses the @minecraft/server 2.x applyKnockback(horizontalForce, vertical)
// signature. The old 4-argument form (directionX, directionZ, horizontalStrength,
// verticalStrength) was REMOVED in 2.0.0 (MC 1.21.80). The horizontal force is now
// a VectorXZ whose magnitude carries the strength, so direction * strength replaces
// the old separate args. Vertical strength is unchanged.
world.afterEvents.entityHurt.subscribe((event) => {
  // Whole handler is guarded: in 2.x getComponent/applyKnockback can throw if an
  // entity involved has gone invalid (despawned/died) between the hit and here.
  try {
    const { hurtEntity, damageSource } = event;
    if (damageSource.cause !== "entityAttack" || !damageSource.damagingEntity) return;

    const attacker = damageSource.damagingEntity;
    const equippable = attacker.getComponent("minecraft:equippable");
    if (!equippable) return;

    const held = equippable.getEquipment("Mainhand");
    if (!held || held.typeId !== "baseball:bat") return;

    const aPos = attacker.location;
    const ePos = hurtEntity.location;

    const dx = ePos.x - aPos.x;
    const dz = ePos.z - aPos.z;
    const dist = Math.sqrt(dx * dx + dz * dz) || 1;

    // Horizontal force (direction * 25.0) sends them flying across the field;
    // 12.5 vertical lift is the Smash-Bros pop-up. (5x the original launch.)
    hurtEntity.applyKnockback(
      { x: (dx / dist) * 25.0, z: (dz / dist) * 25.0 },
      12.5
    );
    hurtEntity.setOnFire(5);
  } catch (e) {
    // ignore — an involved entity was invalid this tick
  }
});
