extends Control
const Rules = preload("res://scripts/battle_rules.gd")
const BALANCE = preload("res://resources/balance.tres")
const ATLAS = preload("res://assets/units.png")
@export_range(0.1,2.0) var playback_interval: float = 0.55
var plan: Array = Rules.default_plan()
var passives: Array = Rules.default_passives()
var events: Array = []
var cursor: int = -1
var running: bool = false
var paused: bool = false
var log_lines: Array = []
var speed: float = 1.0
var result_data: Dictionary = {}
var _unit_tweens: Dictionary = {}
var _shake_tween: Tween
@onready var fx: Control = $Battle/FX
@onready var timer: Timer = $Playback
@onready var combatants: Array = [$Battle/Mage,$Battle/Enemy1,$Battle/Enemy2,$Battle/Enemy3]
@onready var row_box: VBoxContainer = $ActivePanel/Rows

func _ready() -> void:
    _load_plan()
    _set_portraits()
    _prepare_rows()
    $Controls/Preset.add_item("战术预设 · 燃爆连段")
    $Controls/Preset.add_item("战术预设 · 单点引爆")
    $Controls/Preset.add_item("战术预设 · 防守蓄火")
    $Controls/Preset.item_selected.connect(_preset)
    for text in ["1× 速度","2× 速度","4× 速度"]:
        $Controls/Speed.add_item(text)
    $Controls/Speed.item_selected.connect(func(i: int) -> void:
        speed = [1.0,2.0,4.0][i]
        timer.wait_time = playback_interval/speed)
    $Controls/Start.pressed.connect(start_battle)
    $Controls/Pause.pressed.connect(toggle_pause)
    $Controls/Step.pressed.connect(step_once)
    $Controls/Reset.pressed.connect(reset_battle)
    $Controls/Save.pressed.connect(_save_plan)
    $Controls/Help.pressed.connect(_show_help)
    $Controls/Sound.button_pressed = true
    $Controls/Motion.toggled.connect(func(value: bool) -> void: fx.reduced = value)
    timer.timeout.connect(_advance)
    reset_battle()

func _set_portraits() -> void:
    var regions: Array = [Rect2(0,0,540,724),Rect2(540,0,475,724),Rect2(1015,0,565,724),Rect2(1580,0,592,724)]
    for i in range(4):
        var texture: AtlasTexture = AtlasTexture.new()
        texture.atlas = ATLAS
        texture.region = regions[i]
        combatants[i].get_node("Art").texture = texture
        combatants[i].get_node("Name").text = "烬火法师" if i == 0 else Rules.ENEMY_NAMES[i-1]
        var fill: StyleBoxFlat = StyleBoxFlat.new()
        fill.bg_color = Color("#a33421") if i else Color("#59756c")
        combatants[i].get_node("Health").add_theme_stylebox_override("fill",fill)
        var back: StyleBoxFlat = StyleBoxFlat.new()
        back.bg_color = Color("#302720")
        combatants[i].get_node("Health").add_theme_stylebox_override("background",back)

func _prepare_rows() -> void:
    for i in range(7):
        var row: Node = row_box.get_child(i)
        for definition in Rules.SKILLS:
            row.get_node("Skill").add_item(definition.name)
        for text in ["无附加条件","目标已有燃烧","目标燃烧 ≥ 4","自身生命 < 50%"]:
            row.get_node("Condition").add_item(text)
        for text in ["燃烧最多","生命最低","最前方敌人","全体敌人"]:
            row.get_node("Target").add_item(text)
        row.get_node("Target").set_item_disabled(3,true)
        row.get_node("Enabled").toggled.connect(func(value: bool) -> void: plan[i].enabled = value)
        row.get_node("Skill").item_selected.connect(func(index: int) -> void:
            plan[i].id = Rules.SKILLS[index].id
            _refresh_rows())
        row.get_node("Condition").item_selected.connect(func(index: int) -> void: plan[i].condition = index)
        row.get_node("Target").item_selected.connect(func(index: int) -> void: plan[i].target = index)
        row.get_node("Up").pressed.connect(func() -> void: _move_rule(i,-1))
        row.get_node("Down").pressed.connect(func() -> void: _move_rule(i,1))
        row.get_node("Info").pressed.connect(func() -> void: _show_skill(plan[i].id))
    for i in range(3):
        var row: Node = $PassivePanel.get_node("P%d" % i)
        for text in ["总是","生命 < 50%","RP ≥ 2"]:
            row.get_node("Condition").add_item(text)
        row.get_node("Enabled").toggled.connect(func(value: bool) -> void: passives[i].enabled = value)
        row.get_node("Condition").item_selected.connect(func(index: int) -> void: passives[i].condition = index)
        row.get_node("Info").pressed.connect(func() -> void:
            for definition in Rules.PASSIVES:
                if definition.id == passives[i].id:
                    _details(definition.name,definition.desc+"\n\n附加条件在触发时检查，扣除 RP 前判断。"))
    _refresh_rows()

func _refresh_rows() -> void:
    for i in range(7):
        var row: Node = row_box.get_child(i)
        row.get_node("Order").text = "%02d" % (i+1)
        row.get_node("Enabled").set_pressed_no_signal(plan[i].enabled)
        for j in range(Rules.SKILLS.size()):
            if Rules.SKILLS[j].id == plan[i].id:
                row.get_node("Skill").select(j)
        row.get_node("Condition").select(plan[i].condition)
        row.get_node("Target").select(plan[i].target)
        if plan[i].id in ["wall","funeral","inferno"]:
            row.get_node("Target").select(3)
        elif plan[i].id == "double":
            row.get_node("Target").select(0)
        row.get_node("Target").disabled = running or plan[i].id in ["double","wall","funeral","inferno"]
        row.get_node("Cost").text = "%d AP" % Rules.skill(plan[i].id).cost
        row.get_node("Up").disabled = running or i == 0
        row.get_node("Down").disabled = running or i == 6
        row.get_node("Skill").tooltip_text = Rules.skill(plan[i].id).desc
    for i in range(3):
        var row: Node = $PassivePanel.get_node("P%d" % i)
        for definition in Rules.PASSIVES:
            if definition.id == passives[i].id:
                row.get_node("Name").text = definition.name+" · "+definition.timing
                row.get_node("Name").tooltip_text = definition.timing+" · "+definition.desc
        row.get_node("Enabled").set_pressed_no_signal(passives[i].enabled)
        row.get_node("Condition").select(passives[i].condition)

func _move_rule(index: int, direction: int) -> void:
    var next: int = index+direction
    if running or next < 0 or next >= plan.size():
        return
    var item: Dictionary = plan[index]
    plan[index] = plan[next]
    plan[next] = item
    _refresh_rows()

func _preset(index: int) -> void:
    plan = Rules.default_plan()
    passives = Rules.default_passives()
    var ids: Array = []
    if index == 1:
        ids = ["ignite","double","burst","burst","ignite","inferno","spread"]
    elif index == 2:
        ids = ["wall","spread","double","funeral","burst","ignite","inferno"]
        passives[0].enabled = false
    if not ids.is_empty():
        for i in range(7):
            plan[i].id = ids[i]
    _refresh_rows()
    _log("预设已载入，可修改顺序与条件。")

func _lock_controls(value: bool) -> void:
    for row in row_box.get_children():
        for widget in row.get_children():
            if widget is BaseButton and widget.name != "Info":
                widget.disabled = value
    for i in range(3):
        $PassivePanel.get_node("P%d/Enabled" % i).disabled = value
        $PassivePanel.get_node("P%d/Condition" % i).disabled = value
    $Controls/Preset.disabled = value
    $Controls/Start.disabled = value
    $Controls/Save.disabled = value
    _refresh_rows()

func start_battle() -> void:
    if running:
        return
    var engine = Rules.new()
    events = engine.simulate(plan.duplicate(true),passives.duplicate(true),BALANCE)
    cursor = -1
    running = true
    paused = false
    timer.paused = false
    result_data = {}
    log_lines.clear()
    $Controls/Pause.text = "暂停"
    _lock_controls(true)
    timer.wait_time = playback_interval/speed
    _advance()
    timer.start()

func toggle_pause() -> void:
    if not running:
        return
    paused = not paused
    $Controls/Pause.text = "继续" if paused else "暂停"
    timer.paused = paused

func step_once() -> void:
    if not running:
        start_battle()
    paused = true
    timer.paused = true
    $Controls/Pause.text = "继续"
    _advance()

func reset_battle() -> void:
    timer.stop()
    timer.paused = false
    running = false
    paused = false
    cursor = -1
    events.clear()
    result_data.clear()
    log_lines.clear()
    fx.clear_effects()
    for tween in _unit_tweens.values():
        if tween.is_valid():
            tween.kill()
    _unit_tweens.clear()
    if _shake_tween and _shake_tween.is_valid():
        _shake_tween.kill()
    $Battle.position = Vector2(28,78)
    for unit in combatants:
        unit.get_node("Art").position = Vector2(5,12)
    $SoundPlayer.stop()
    $Controls/Pause.disabled = false
    $Controls/Step.disabled = false
    _lock_controls(false)
    var initial: Dictionary = {"hp":BALANCE.hero_health,"round":0,"ap":BALANCE.action_points,"rp":BALANCE.reaction_points,"charge":false,"enemies":[]}
    for i in range(3):
        initial.enemies.append({"hp":BALANCE.enemy_health[i],"max_hp":BALANCE.enemy_health[i],"burn":0})
    _render_state(initial)
    $Battle/Banner.text = "战前编排  /  先铺火，再翻倍与扩散"
    $Controls/Pause.text = "暂停"
    for row in row_box.get_children():
        row.modulate = Color.WHITE
    _log("三只小怪只会普通攻击：%d / %d / %d 伤害。" % [BALANCE.enemy_damage[0],BALANCE.enemy_damage[1],BALANCE.enemy_damage[2]])
    _log("每回合恢复 %d AP、%d RP；燃烧每层 %d 伤害。" % [BALANCE.action_points,BALANCE.reaction_points,BALANCE.burn_damage])
    _log("炎爆、炼狱立即引爆保留燃烧；回合末引爆清空。")

func _advance() -> void:
    if not running or cursor+1 >= events.size():
        return
    cursor += 1
    var event: Dictionary = events[cursor]
    _render_state(event.state)
    _log(event.text)
    var color: Color = Color("#f6d7a0")
    match event.kind:
        "cast":
            $Battle/Banner.text = event.text
            if event.skill in ["wall","funeral","inferno"]:
                for i in range(3):
                    if event.state.enemies[i].hp > 0:
                        fx.projectile(i)
            else:
                fx.projectile(event.target)
            _sound("cast")
            _animate_unit(0,0)
        "hit","blast":
            fx.floating(event.target,str(event.amount),Color("#ffbf66") if event.kind == "blast" else color,event.kind == "blast")
            _animate_unit(event.target+1,1)
            if event.kind == "blast":
                fx.burst(event.target,event.amount)
                _sound("blast")
                if not fx.reduced:
                    if _shake_tween and _shake_tween.is_valid():
                        _shake_tween.kill()
                    _shake_tween = create_tween()
                    _shake_tween.tween_property($Battle,"position",Vector2(32,78),0.035)
                    _shake_tween.tween_property($Battle,"position",Vector2(24,78),0.04)
                    _shake_tween.tween_property($Battle,"position",Vector2(28,78),0.08)
            else:
                _sound("hit")
        "burn":
            fx.floating(event.target,"+%d 燃烧" % event.amount,Color("#ffa15b"))
        "hurt":
            fx.floating(-1,"-%d" % event.amount,Color("#ff7860"))
            _animate_unit(0,1)
            _sound("hit")
        "enemy":
            _animate_unit(event.target+1,0)
            $Battle/Banner.text = event.text
        "shield","charge","mana":
            fx.floating(-1,{"shield":"炎盾","charge":"蓄能 ×2","mana":"AP +1"}[event.kind],Color("#a6dbef"))
            _sound("buff")
        "detonate":
            $Battle/Banner.text = event.text
            fx.burst(event.target,event.amount)
        "round","end_round":
            $Battle/Banner.text = event.text
        "result":
            timer.stop()
            result_data = event
            paused = true
            $Controls/Pause.disabled = true
            $Controls/Step.disabled = true
            $Battle/Banner.text = event.text+"  /  最高 %d 层" % event.peak_burn
            _log("实伤 %d · %d 回合 · 点击返回编排可重试" % [event.total_damage,event.state.round])
    for row in row_box.get_children():
        var i: int = row.get_index()
        row.modulate = Color(1,0.74,0.5) if i == event.get("slot",-1) and plan[i].id == event.skill else Color.WHITE
    # Group rapid hit/buff records visually; hold cast and detonation beats longer.
    var beats: Dictionary = {"cast":1.0,"hit":0.16,"burn":0.18,"detonate":0.65,"blast":0.6,"death":0.2,"skip":0.18,"enemy":0.8,"hurt":0.5,"round":1.2,"end_round":1.2}
    timer.wait_time = playback_interval*float(beats.get(event.kind,0.7))/speed

func _render_state(state: Dictionary) -> void:
    $Status.text = "第 %d 回合     生命 %d / %d     ◆ AP %d     ● RP %d     %s" % [state.round,state.hp,BALANCE.hero_health,state.ap,state.rp,"蓄能：下一行动新增燃烧 ×2" if state.charge else "燃烧：每层 %d 伤害；回合末结算并清空" % BALANCE.burn_damage]
    combatants[0].get_node("Health").max_value = BALANCE.hero_health
    combatants[0].get_node("Health").value = state.hp
    combatants[0].get_node("Numbers").text = "%d / %d" % [state.hp,BALANCE.hero_health]
    combatants[0].get_node("Art").modulate = Color.WHITE if state.hp > 0 else Color(0.4,0.4,0.4,0.25)
    for i in range(3):
        var enemy: Dictionary = state.enemies[i]
        var unit: Control = combatants[i+1]
        unit.get_node("Health").max_value = enemy.max_hp
        unit.get_node("Health").value = enemy.hp
        unit.get_node("Numbers").text = "%d / %d   · 攻 %d" % [enemy.hp,enemy.max_hp,BALANCE.enemy_damage[i]]
        unit.get_node("Burn").text = "燃烧 %d 层  /  预计 %d" % [enemy.burn,enemy.burn*BALANCE.burn_damage] if enemy.burn > 0 else ""
        unit.get_node("BurnPlate").visible = enemy.burn > 0
        unit.get_node("Art").modulate = Color.WHITE if enemy.hp > 0 else Color(0.4,0.4,0.4,0.20)
        fx.burns[i] = enemy.burn if enemy.hp > 0 else 0

func _animate_unit(index: int, kind: int) -> void:
    if fx.reduced:
        return
    var art: Control = combatants[index].get_node("Art")
    var origin: Vector2 = Vector2(5,12)
    if _unit_tweens.has(index) and _unit_tweens[index].is_valid():
        _unit_tweens[index].kill()
    var tween: Tween = create_tween()
    _unit_tweens[index] = tween
    if kind == 0:
        tween.tween_property(art,"position",origin+Vector2(15 if index == 0 else -15,-3),0.12/speed)
    else:
        tween.tween_property(art,"position",origin+Vector2(-7 if index == 0 else 7,0),0.06/speed)
    tween.tween_property(art,"position",origin,0.18/speed)

func _sound(id: String) -> void:
    if not $Controls/Sound.button_pressed:
        return
    $SoundPlayer.stream = load("res://assets/%s.wav" % id)
    $SoundPlayer.play()

func _log(message: String) -> void:
    log_lines.append(message)
    if log_lines.size() > 45:
        log_lines.pop_front()
    $LogPanel/Log.text = "\n".join(log_lines)

func _details(title: String, body: String) -> void:
    $Details.title = title
    $Details/Text.text = body
    $Details.popup_centered(Vector2i(680,400))

func _show_skill(id: String) -> void:
    var definition: Dictionary = Rules.skill(id)
    _details(definition.name+" · %d AP" % definition.cost,definition.desc+"\n\n触发时机：法师行动阶段，按列表从上到下。\n每条规则每回合最多一次；失败的规则跳过且不扣 AP。\n\n条件：目标燃烧门槛先筛选，再按目标偏好选择。全体技能只需存在合格目标即可发动，作用于全部存活敌人。\n\n蓄能：本次新增燃烧 ×2；翻倍技能的新增部分也翻倍（3 → 9）。")

func _show_help() -> void:
    _details("燃爆法师 · 体验规则","[b]一轮战斗[/b]\n法师按序施法 → 敌人依次普攻 → 燃烧引爆清空。每轮恢复 AP / RP，最多 8 轮。\n\n[b]组建连段[/b]\n火墙铺火 → 爆燃培养种子 → 火星扩散 → 火葬翻倍 → 炼狱引爆。魔力恢复补充最后一点 AP。\n\n[b]反应资源[/b]\n蓄能、魔力恢复与炎盾竞争 RP。可以关闭蓄能，留点数抵挡攻击。\n\n[b]操作[/b]\n↑↓调整顺序；可替换技能、设置条件与目标。暂停、单步、变速可检查原因。保存战术后重开游戏仍保留。\n\n此版本为规则体验样片；所有技能直接开放，无付费、计时门槛或离线收益。")

func _save_plan() -> void:
    var file: FileAccess = FileAccess.open("user://tactics.json",FileAccess.WRITE)
    if file == null:
        _log("保存失败：无法写入战术文件")
        return
    file.store_string(JSON.stringify({"version":1,"plan":plan,"passives":passives}))
    _log("战术已保存，下次启动自动恢复。")

func _load_plan() -> void:
    if not FileAccess.file_exists("user://tactics.json"):
        return
    var parser: JSON = JSON.new()
    if parser.parse(FileAccess.get_file_as_string("user://tactics.json")) != OK:
        return
    var data: Variant = parser.data
    if not data is Dictionary or data.get("version",0) != 1:
        return
    var saved: Variant = data.get("plan",[])
    var saved_passives: Variant = data.get("passives",[])
    if not saved is Array or saved.size() != 7 or not saved_passives is Array or saved_passives.size() != 3:
        return
    for rule in saved:
        if not rule is Dictionary or Rules.skill(str(rule.get("id",""))).is_empty():
            return
        var condition: Variant = rule.get("condition",null)
        var target: Variant = rule.get("target",null)
        if not rule.get("enabled",null) is bool or not typeof(condition) in [TYPE_INT,TYPE_FLOAT] or not typeof(target) in [TYPE_INT,TYPE_FLOAT]:
            return
        if condition != int(condition) or target != int(target) or not int(condition) in range(4) or not int(target) in range(3):
            return
        rule.condition = int(condition)
        rule.target = int(target)
    for i in range(3):
        var rule: Variant = saved_passives[i]
        if not rule is Dictionary or rule.get("id","") != Rules.default_passives()[i].id or not rule.get("enabled",null) is bool:
            return
        var condition: Variant = rule.get("condition",null)
        if not typeof(condition) in [TYPE_INT,TYPE_FLOAT] or condition != int(condition) or not int(condition) in range(3):
            return
        rule.condition = int(condition)
    plan = saved
    passives = saved_passives
