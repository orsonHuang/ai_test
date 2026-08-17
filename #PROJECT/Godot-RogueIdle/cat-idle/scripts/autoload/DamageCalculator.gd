class_name DamageCalculator
extends RefCounted

const DEFENSE_FACTOR: float = 0.06

static func calculate_damage(attacker: BattleCharacter, target: BattleCharacter, skill_multiplier: float = 1.0) -> int:
	var base_attack: float = attacker.data.attack
	var damage: float = base_attack * skill_multiplier

	# 防御减伤
	var defense_reduction: float = 1.0 - (DEFENSE_FACTOR * target.data.defense) / (1.0 + DEFENSE_FACTOR * abs(target.data.defense))
	defense_reduction = clampf(defense_reduction, 0.1, 1.0)

	damage *= defense_reduction

	# 暴击判定
	var is_crit: bool = randf() < attacker.data.crit_rate
	if is_crit:
		damage *= attacker.data.crit_damage

	# 浮动 ±10%
	damage *= randf_range(0.9, 1.1)

	return maxi(1, int(round(damage)))

static func apply_damage(target: BattleCharacter, amount: int) -> int:
	var actual_damage: int = amount
	if target.data.current_shield > 0:
		var absorbed: int = mini(target.data.current_shield, actual_damage)
		target.data.current_shield -= absorbed
		actual_damage -= absorbed

	target.data.current_hp = maxi(0, target.data.current_hp - actual_damage)
	return actual_damage
