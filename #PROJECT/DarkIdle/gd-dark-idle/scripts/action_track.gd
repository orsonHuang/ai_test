extends Panel
var positions: Array = [0.84,0.61,0.38,0.16]
var active_actor: int = -1
var tweens: Array = []

func update_track(state: Dictionary, animate: bool, speed: float = 1.0) -> void:
    for tween in tweens:
        if tween.is_valid():
            tween.kill()
    tweens.clear()
    positions = state.timeline.duplicate()
    active_actor = state.actor
    for i in range(4):
        var portrait: Control = get_node("Actor%d" % i)
        var alive: bool = state.hp > 0 if i == 0 else state.enemies[i-1].hp > 0
        portrait.visible = alive and not state.done[i]
        var destination: Vector2 = Vector2(122+positions[i]*1300-22,10)
        var scale_to: Vector2 = Vector2.ONE*(1.28 if active_actor == i else 1.0)
        if animate:
            var tween: Tween = create_tween().set_parallel()
            tween.tween_property(portrait,"position",destination,0.6/speed)
            tween.tween_property(portrait,"scale",scale_to,0.6/speed)
            tweens.append(tween)
        else:
            portrait.position = destination
            portrait.scale = scale_to
        portrait.modulate = Color(1,0.72,0.3) if active_actor == i else Color.WHITE
