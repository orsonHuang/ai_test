extends Control
var actor_id: int = 0
var selected: bool = false
var offsets: Array = []
var attack_count: int = 0

func configure(id: int, data: Dictionary) -> void:
    actor_id = id
    offsets = data.offsets
    $Art.scale = Vector2.ONE*float(data.scale)
    $Art.frame_changed.connect(_align_feet)
    $Art.animation_finished.connect(func() -> void: $Art.play("idle"))
    $Art.play("idle")
    _align_feet()

func _align_feet() -> void:
    if offsets.is_empty():
        return
    var index: int = [0,1,2,3,0][$Art.frame] if $Art.animation == "attack" else 0
    $Art.offset = Vector2(offsets[index][0],offsets[index][1])

func attack(playback_speed: float = 1.0) -> void:
    attack_count += 1
    $Art.speed_scale = playback_speed
    $Art.stop()
    $Art.play("attack")

func reset_animation() -> void:
    $Art.stop()
    $Art.play("idle")
    $Art.modulate = Color.WHITE
    _align_feet()

func set_selected(value: bool) -> void:
    selected = value
    $Mark.visible = value
    queue_redraw()

func _draw() -> void:
    if selected:
        var points: PackedVector2Array = []
        for i in range(49):
            var angle: float = TAU*i/48
            points.append(Vector2(110+cos(angle)*70,246+sin(angle)*10))
        draw_polyline(points,Color(1,0.7,0.25),3,true)
