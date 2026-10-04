@tool
extends Control
## World scale and position are derived from the available container size; edit vertices in FogRegion resources.
@export var reference_size: Vector2 = Vector2(600, 640):
    set(value):
        reference_size = value
        if is_node_ready():
            _resize_world()
func _ready() -> void:
    resized.connect(_resize_world)
    _resize_world()
func _resize_world() -> void:
    if not has_node("World") or reference_size.x <= 0.0 or reference_size.y <= 0.0:
        return
    var factor: float = minf(size.x / reference_size.x, size.y / reference_size.y)
    $World.scale = Vector2.ONE * factor
    $World.position = (size - reference_size * factor) * 0.5
