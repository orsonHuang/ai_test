class_name BattleCharacter
extends Node2D

signal hp_changed(character: BattleCharacter, current: int, maximum: int)
signal died(character: BattleCharacter)

@export var data: CharacterData
@export var display_position: Vector2 = Vector2.ZERO

var action_meter: float = 0.0
var skill_cooldowns: Dictionary = {}
var buffs: Array[Dictionary] = []

@onready var body: ColorRect = $Body
@onready var name_label: Label = $NameLabel
@onready var hp_bar: ProgressBar = $HPBar

func _ready():
	if data == null:
		return
	data.reset()
	position = display_position
	_update_visual()
	_update_hp_bar()

func _process(delta: float):
	if data == null or not data.is_alive():
		return
	action_meter += data.speed * data.attack_speed * delta * 5.0
	if action_meter >= 100.0:
		action_meter = 100.0

func reset_action():
	action_meter = 0.0

func take_damage(amount: int, is_crit: bool = false) -> int:
	var actual: int = DamageCalculator.apply_damage(self, amount)
	hp_changed.emit(self, data.current_hp, data.max_hp)
	_update_hp_bar()
	_spawn_floating_number(actual, is_crit)
	if not data.is_alive():
		died.emit(self)
	return actual

func heal(amount: int):
	data.current_hp = mini(data.max_hp, data.current_hp + amount)
	hp_changed.emit(self, data.current_hp, data.max_hp)
	_update_hp_bar()
	_spawn_floating_number(amount, false, true)

func add_shield(amount: int):
	data.current_shield += amount

func _update_visual():
	if body != null:
		body.color = data.color
	if name_label != null:
		name_label.text = data.display_name

func _update_hp_bar():
	if hp_bar != null and data != null:
		hp_bar.max_value = data.max_hp
		hp_bar.value = data.current_hp

func _spawn_floating_number(value: int, is_crit: bool, is_heal: bool = false):
	var fn: Label = load("res://scenes/FloatingNumber.tscn").instantiate()
	fn.text = str(value)
	fn.global_position = global_position + Vector2(randf_range(-20, 20), -30)
	if is_crit:
		fn.modulate = Color.YELLOW
		fn.scale = Vector2(1.5, 1.5)
	elif is_heal:
		fn.modulate = Color.GREEN
	else:
		fn.modulate = Color.WHITE
	get_tree().root.add_child(fn)
