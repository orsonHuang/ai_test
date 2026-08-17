@tool
class_name CharacterData
extends Resource

@export var id: String = ""
@export var display_name: String = "未命名"
@export var is_player: bool = true

# 基础属性
@export var max_hp: int = 100
@export var attack: int = 20
@export var defense: int = 5
@export var speed: int = 10
@export var crit_rate: float = 0.1
@export var crit_damage: float = 1.5
@export var attack_speed: float = 1.0

# 技能
@export var skill_ids: PackedStringArray = []

# 外观
@export var color: Color = Color.WHITE

var current_hp: int = max_hp
var current_shield: int = 0

func reset():
	current_hp = max_hp
	current_shield = 0

func is_alive() -> bool:
	return current_hp > 0
