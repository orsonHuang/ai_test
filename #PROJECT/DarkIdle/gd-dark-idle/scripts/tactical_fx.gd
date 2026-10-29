extends Control
const CENTERS: Array = [Vector2(220,175),Vector2(720,185),Vector2(1035,175),Vector2(1350,175)]
var reduced: bool = false
var burns: Array = [0,0,0]
var particles: Array = []
var trails: Array = []
var history: Array = []
var clock: float = 0.0

func clear_effects() -> void:
    particles.clear()
    trails.clear()
    burns = [0,0,0]
    history.clear()
    for node in get_children():
        node.queue_free()

func floating(actor: int, text: String, color: Color, kind: String = "damage") -> void:
    if actor < 0 or actor > 3:
        return
    var label: Label = Label.new()
    label.text = text
    label.add_theme_color_override("font_color",color)
    label.add_theme_color_override("font_outline_color",Color(0.08,0.04,0.02))
    label.add_theme_constant_override("outline_size",5)
    label.add_theme_font_size_override("font_size",30 if kind == "blast" else (22 if kind == "skill" else 19))
    label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    label.size = Vector2(240,40)
    var channel: String = kind if kind in ["skill","buff"] else "damage"
    var occupied: Array = []
    for existing in get_children():
        if existing.get_meta("actor",-1) == actor and existing.get_meta("channel","") == channel:
            occupied.append(existing.get_meta("lane",0))
    var lane: int = 0
    while lane in occupied:
        lane += 1
    var point: Vector2 = Vector2(CENTERS[actor].x-120,200+lane*18)
    if kind == "skill":
        point.y = (53 if actor == 0 else 108)+lane*26
    elif kind == "buff":
        point.y = 160+lane*20
    label.position = point
    label.mouse_filter = Control.MOUSE_FILTER_IGNORE
    label.set_meta("actor",actor)
    label.set_meta("feedback_kind",kind)
    label.set_meta("channel",channel)
    label.set_meta("lane",lane)
    add_child(label)
    history.append({"actor":actor,"text":text,"kind":kind})
    if history.size() > 300:
        history.pop_front()
    var tween: Tween = label.create_tween().set_parallel()
    var rise: int = 10 if reduced else (20 if kind == "skill" else 32)
    tween.tween_property(label,"position:y",point.y-rise,0.85)
    tween.tween_property(label,"modulate:a",0.0,0.35).set_delay(0.7)
    tween.chain().tween_callback(label.queue_free)

func projectile(from: int, to: int) -> void:
    trails.append({"from":CENTERS[from]-Vector2(0,50),"to":CENTERS[to],"age":0.0})

func burst(actor: int, strength: int) -> void:
    var count: int = 8 if reduced else mini(32,12+floori(strength/8.0))
    for i in range(count):
        var angle: float = TAU*i/count
        particles.append({"p":CENTERS[actor],"v":Vector2(cos(angle),sin(angle))*float(50+i%5*24),"age":0.0,"life":0.55+(i%3)*0.1})

func _process(delta: float) -> void:
    clock += delta
    for item in particles:
        item.age += delta
    for item in trails:
        item.age += delta
    particles = particles.filter(func(item: Dictionary) -> bool: return item.age < item.life)
    trails = trails.filter(func(item: Dictionary) -> bool: return item.age < 0.45)
    queue_redraw()

func _draw() -> void:
    for i in range(3):
        if burns[i] <= 0:
            continue
        var base: Vector2 = CENTERS[i+1]+Vector2(0,58)
        for j in range(mini(6,burns[i])):
            var x: float = (j-2.5)*15
            var points: PackedVector2Array = [base+Vector2(x-9,0),base+Vector2(x+sin(clock*3+j)*5,-18-mini(burns[i],12)*2),base+Vector2(x+9,0)]
            draw_colored_polygon(points,Color(0.95,0.25,0.04,0.62))
    for particle in particles:
        var p: Vector2 = particle.p+particle.v*particle.age
        draw_circle(p,4*(1-particle.age/particle.life),Color(1,0.6,0.18,1-particle.age/particle.life))
    for trail in trails:
        var p: Vector2 = trail.from.lerp(trail.to,clampf(trail.age/0.3,0,1))
        draw_line(p-Vector2(35,0),p,Color(0.95,0.28,0.04),4)
        draw_circle(p,6,Color(1,0.7,0.25))
