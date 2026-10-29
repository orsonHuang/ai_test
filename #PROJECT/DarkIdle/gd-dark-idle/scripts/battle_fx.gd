extends Control
var reduced: bool = false
var embers: Array = []
var trails: Array = []
var burns: Array = [0,0,0]
var clock: float = 0.0
const POINTS: Array = [Vector2(770,170),Vector2(1075,170),Vector2(1360,170)]

func clear_effects() -> void:
    embers.clear()
    trails.clear()
    burns = [0,0,0]
    for label in get_children():
        label.queue_free()
    queue_redraw()

func _process(delta: float) -> void:
    clock += delta
    for effect in embers:
        effect.age += delta
    embers = embers.filter(func(e: Dictionary) -> bool: return e.age < e.life)
    for trail in trails:
        trail.age += delta
    trails = trails.filter(func(e: Dictionary) -> bool: return e.age < 0.4)
    queue_redraw()

func burst(index: int, strength: int) -> void:
    var point: Vector2 = Vector2(220,150) if index < 0 else POINTS[index]
    var count: int = 8 if reduced else mini(36,12+strength/4)
    for i in range(count):
        var angle: float = TAU*i/count
        embers.append({"p":point,"v":Vector2(cos(angle),sin(angle))*float(50+i%5*28),"age":0.0,"life":0.5+0.06*(i%5)})

func projectile(index: int) -> void:
    if index >= 0:
        trails.append({"from":Vector2(240,120),"to":POINTS[index],"age":0.0})

func floating(index: int, message: String, color: Color, big: bool = false) -> void:
    var label: Label = Label.new()
    label.text = message
    label.add_theme_color_override("font_color",color)
    label.add_theme_color_override("font_outline_color",Color(0.12,0.06,0.03))
    label.add_theme_constant_override("outline_size",4)
    label.add_theme_font_size_override("font_size",34 if big else 23)
    var point: Vector2 = Vector2(185,120) if index < 0 else POINTS[index]-Vector2(55,55)
    if message.contains("燃烧"):
        point.y += 44
    elif big:
        point.y -= 20
    label.position = point
    label.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(label)
    var tween: Tween = label.create_tween().set_parallel()
    tween.tween_property(label,"position:y",point.y-60,1.0).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
    tween.tween_property(label,"modulate:a",0.0,1.0).set_delay(0.15)
    tween.chain().tween_callback(label.queue_free)

func _draw() -> void:
    for i in range(3):
        var amount: int = burns[i]
        if amount <= 0:
            continue
        var p: Vector2 = POINTS[i]+Vector2(0,40)
        for j in range(mini(7,amount)):
            var offset: float = sin(clock*3+j*2)*5
            var x: float = (j-3)*14
            var points: PackedVector2Array = [p+Vector2(x-9,0),p+Vector2(x+offset,-20-mini(amount,16)*2-j%3*10),p+Vector2(x+9,0)]
            draw_colored_polygon(points,Color(0.9,0.24,0.06,0.6))
    for effect in embers:
        var p: Vector2 = effect.p+effect.v*effect.age+Vector2(0,70)*effect.age*effect.age
        draw_circle(p,3.0*(1.0-effect.age/effect.life),Color(1.0,0.44,0.10,1.0-effect.age/effect.life))
    for trail in trails:
        var progress: float = clampf(trail.age/0.3,0,1)
        var p: Vector2 = trail.from.lerp(trail.to,progress)
        draw_line(p-Vector2(45,0),p,Color(0.84,0.20,0.05),5)
        draw_circle(p,7,Color(1.0,0.62,0.18))
