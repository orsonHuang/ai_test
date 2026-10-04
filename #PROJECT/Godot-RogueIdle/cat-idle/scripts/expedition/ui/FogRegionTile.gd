@tool
extends Control
signal region_selected(region_id: String)

## The resource owns polygon vertices and label coordinates. These child properties are preview-driven.
@export var definition: FogRegion:
    set(value):
        if definition != null and definition.changed.is_connected(_definition_changed):
            definition.changed.disconnect(_definition_changed)
        definition = value
        if definition != null:
            definition.changed.connect(_definition_changed)
        if is_node_ready():
            refresh(true, false, false, false)

func _definition_changed() -> void:
    if Engine.is_editor_hint() and is_node_ready():
        refresh(true, false, false, false)

func _ready() -> void:
    refresh(true, false, false, false)

func _has_point(point: Vector2) -> bool:
    return definition != null and Geometry2D.is_point_in_polygon(point, definition.polygon)

func _gui_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
        region_selected.emit(definition.id)
        accept_event()

func refresh(known: bool, current: bool, reachable: bool, selected: bool) -> void:
    if definition == null or not is_node_ready():
        return
    $Land.polygon = definition.polygon
    $Land.color = definition.tint if known else Color("#202d38")
    $Border.points = definition.polygon
    $Border.closed = true
    $Border.width = 4.0 if current or selected else 2.0
    $Border.default_color = Color("#e6c780") if current or selected else (Color("#84cbb7") if reachable else Color("#557278"))
    $Caption.position = definition.label_position - Vector2(93, 18)
    $Caption.size = Vector2(186, 44)
    $Caption.text = definition.display_name if known or definition.initial_landmark else "未探明"
    $Caption.modulate = Color.WHITE if known or definition.initial_landmark else Color("#7b8d9b")
    $Detail.position = definition.label_position + Vector2(-103, 19)
    $Detail.size = Vector2(206, 26)
    var symbols: Dictionary = {"thorn": "荆棘", "storm": "猎风", "ember": "余烬", "king": "最终战", "": "集结"}
    $Detail.text = ("你在这里 · " if current else ("可前往 · " if reachable else "")) + str(symbols.get(definition.family, ""))
    if not known and not definition.initial_landmark:
        $Detail.text = "战争迷雾"
    tooltip_text = definition.boss_name if known or definition.initial_landmark else "进入相邻地区后揭开迷雾"
