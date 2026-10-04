@tool
class_name FogUnit
extends Resource

@export var id: String = ""
@export var display_name: String = ""
@export_enum("ally", "enemy") var side: String = "ally"
@export var kind: String = ""
@export_group("Combat")
@export_range(1, 5000) var hp: int = 100
@export_range(1, 500) var atk: int = 20
@export_range(0, 100) var armor: int = 3
@export_range(1, 100) var speed: int = 12
@export_group("Growth")
@export var hp_per_level: int = 0
@export var atk_per_level: int = 0
@export var armor_every_levels: int = 0

func to_row() -> Dictionary:
    return {"id": id, "name": display_name, "side": side, "kind": kind,
        "hp": hp, "atk": atk, "armor": armor, "speed": speed,
        "hp_per_level": hp_per_level, "atk_per_level": atk_per_level,
        "armor_every_levels": armor_every_levels}
