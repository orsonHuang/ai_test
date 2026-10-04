extends Label

var lifetime: float = 0.0
var velocity: Vector2 = Vector2.ZERO

func _ready():
	lifetime = 1.0
	velocity = Vector2(randf_range(-20, 20), -80)
	pivot_offset = size / 2

func _process(delta: float):
	lifetime -= delta
	position += velocity * delta
	velocity.y += 120.0 * delta
	modulate.a = clampf(lifetime, 0.0, 1.0)
	if lifetime <= 0.0:
		queue_free()
