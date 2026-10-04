@tool
class_name FogRegion
extends Resource

@export var id: String = ""
@export var display_name: String = ""
@export var boss_name: String = ""
@export_range(0, 4) var stage: int = 1
@export var ap: int = 6
@export var next_ids: PackedStringArray = []
@export var adjacent_ids: PackedStringArray = []
@export var family: String = ""
@export var initial_landmark: bool = false
@export var hp_mult: float = 1.0
@export var atk_mult: float = 1.0
@export_group("Editable map geometry")
@export var polygon: PackedVector2Array = []:
    set(value):
        polygon = value
        emit_changed()
@export var label_position: Vector2 = Vector2.ZERO:
    set(value):
        label_position = value
        emit_changed()
@export var tint: Color = Color("#344e48"):
    set(value):
        tint = value
        emit_changed()

func to_row() -> Dictionary:
    return {"id": id, "name": display_name, "boss_name": boss_name,
        "stage": stage, "ap": ap, "next_ids": Array(next_ids),
        "adjacent_ids": Array(adjacent_ids), "family": family,
        "initial_landmark": initial_landmark, "hp_mult": hp_mult, "atk_mult": atk_mult}
