class_name BattleManager
extends Node

signal turn_started(character: BattleCharacter)
signal battle_ended(winner_is_player: bool)
signal log_message(text: String)

@export var player_spawn: Marker2D
@export var enemy_spawn: Marker2D
@export var character_scene: PackedScene

var player_data: CharacterData
var enemy_data: CharacterData
var characters: Array[BattleCharacter] = []
var player: BattleCharacter = null
var enemy: BattleCharacter = null
var current_actor: BattleCharacter = null
var is_battling: bool = false
var turn_delay: float = 0.3
var turn_timer: float = 0.0

func _ready():
	_create_mock_data()
	_start_battle()

func _create_mock_data():
	player_data = CharacterData.new()
	player_data.id = "warrior"
	player_data.display_name = "战士"
	player_data.is_player = true
	player_data.max_hp = 200
	player_data.attack = 35
	player_data.defense = 12
	player_data.speed = 12
	player_data.crit_rate = 0.15
	player_data.crit_damage = 1.8
	player_data.attack_speed = 1.0
	player_data.skill_ids = PackedStringArray(["warrior_roar", "warrior_rampage", "warrior_thorns"])
	player_data.color = Color(0.2, 0.5, 0.9)

	enemy_data = CharacterData.new()
	enemy_data.id = "enemy_slime"
	enemy_data.display_name = "史莱姆"
	enemy_data.is_player = false
	enemy_data.max_hp = 150
	enemy_data.attack = 28
	enemy_data.defense = 6
	enemy_data.speed = 10
	enemy_data.crit_rate = 0.08
	enemy_data.crit_damage = 1.5
	enemy_data.attack_speed = 1.0
	enemy_data.skill_ids = PackedStringArray()
	enemy_data.color = Color(0.9, 0.3, 0.3)

func _process(delta: float):
	if not is_battling:
		return
	if current_actor != null:
		return

	# 行动条推进
	for c in characters:
		if c.data.is_alive():
			c.action_meter += c.data.speed * c.data.attack_speed * delta * 5.0

	# 选择下一个行动者
	var ready_character: BattleCharacter = null
	for c in characters:
		if c.data.is_alive() and c.action_meter >= 100.0:
			if ready_character == null or c.data.speed > ready_character.data.speed:
				ready_character = c

	if ready_character != null:
		current_actor = ready_character
		_turn(current_actor)

func _start_battle():
	if player_spawn == null:
		player_spawn = get_node_or_null("PlayerSpawn")
	if enemy_spawn == null:
		enemy_spawn = get_node_or_null("EnemySpawn")
	if character_scene == null:
		character_scene = load("res://scenes/BattleCharacter.tscn")

	player = character_scene.instantiate() as BattleCharacter
	player.data = player_data
	player.display_position = player_spawn.position if player_spawn else Vector2(300, 400)
	player.data.is_player = true
	add_child(player)

	enemy = character_scene.instantiate() as BattleCharacter
	enemy.data = enemy_data
	enemy.display_position = enemy_spawn.position if enemy_spawn else Vector2(900, 400)
	enemy.data.is_player = false
	add_child(enemy)

	characters = [player, enemy]
	is_battling = true
	log_message.emit("战斗开始！")

func _turn(actor: BattleCharacter):
	actor.reset_action()
	turn_started.emit(actor)

	if not actor.data.is_alive():
		current_actor = null
		return

	var target: BattleCharacter = enemy if actor.data.is_player else player
	if target == null or not target.data.is_alive():
		current_actor = null
		return

	# 简单 AI：随机普攻或技能
	var action_roll: float = randf()
	if action_roll < 0.25 and actor.data.skill_ids.size() > 0:
		var skill_index: int = randi() % actor.data.skill_ids.size()
		_use_skill(actor, target, actor.data.skill_ids[skill_index])
	else:
		_attack(actor, target)

	# 检查胜负
	await get_tree().create_timer(0.4).timeout
	_check_end()
	current_actor = null

func _attack(attacker: BattleCharacter, target: BattleCharacter):
	var damage: int = DamageCalculator.calculate_damage(attacker, target, 1.0)
	var is_crit: bool = randf() < attacker.data.crit_rate
	if is_crit:
		damage = int(round(damage * attacker.data.crit_damage / 1.5))
	var actual: int = target.take_damage(damage, is_crit)
	log_message.emit("%s 攻击 %s，造成 %d 点伤害%s" % [
		attacker.data.display_name, target.data.display_name, actual, "（暴击）" if is_crit else ""])

func _use_skill(actor: BattleCharacter, target: BattleCharacter, skill_id: String):
	match skill_id:
		"warrior_roar":
			actor.add_shield(15)
			log_message.emit("%s 使用【战斗怒吼】，获得 15 护盾" % actor.data.display_name)
		"warrior_rampage":
			var heal_amount: int = int(round(actor.data.max_hp * 0.08))
			actor.heal(heal_amount)
			log_message.emit("%s 使用【愈战愈勇】，恢复 %d 生命" % [actor.data.display_name, heal_amount])
		"warrior_thorns":
			actor.buffs.append({"id": "thorns", "value": 5, "turns": 3})
			log_message.emit("%s 使用【荆棘甲】，反弹伤害提升" % actor.data.display_name)
		_:
			_attack(actor, target)

func _check_end():
	if not player.data.is_alive():
		is_battling = false
		battle_ended.emit(false)
		log_message.emit("战斗结束，玩家战败。")
	elif not enemy.data.is_alive():
		is_battling = false
		battle_ended.emit(true)
		log_message.emit("战斗结束，玩家获胜！")

func restart():
	for c in characters:
		c.queue_free()
	characters.clear()
	current_actor = null
	is_battling = false
	_start_battle()
