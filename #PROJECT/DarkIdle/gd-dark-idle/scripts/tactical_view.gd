extends Control
const Rules = preload("res://scripts/combat_rules.gd")
const Store = preload("res://scripts/tactics_store.gd")
const BALANCE = preload("res://resources/balance_v2.tres")
const ICONS = preload("res://assets/v2/icons.png")
const PORTRAITS = preload("res://assets/units.png")
const UNIT_KEYS: Array = ["mage","soot","antler","straw"]
var plan: Array = Rules.default_plan()
var passives: Array = Rules.default_passives()
var marked: int = -1
var click_target: bool = true
var running: bool = false
var previewing: bool = false
var paused: bool = false
var speed: float = 1.0
var events: Array = []
var cursor: int = -1
var result_data: Dictionary = {}
var previous_result: Dictionary = {}
var shown_state: Dictionary = {}
var selected_group: int = 0
var selected_slot: int = 0
var candidate: String = ""
var detail_skill: String = ""
var detail_focus: Dictionary = {}
var units: Array = []
var skipped: Array = []
var shake_tween: Tween
@onready var timer: Timer = $Playback
@onready var fx: Control = $Battle/FX

func _ready() -> void:
    var saved: Dictionary = Store.read_data()
    if not saved.is_empty():
        plan = saved.plan
        passives = saved.passives
        marked = int(saved.marked)
        click_target = saved.click_target
    _prepare_units()
    _prepare_controls()
    reset_battle()

func icon(index: int) -> AtlasTexture:
    var texture: AtlasTexture = AtlasTexture.new()
    texture.atlas = ICONS
    var cell: Vector2 = ICONS.get_size()/Vector2(5,3)
    texture.region = Rect2(Vector2(index%5,floori(index/5.0))*cell,cell)
    return texture

func _portrait(index: int) -> AtlasTexture:
    var regions: Array = [Rect2(140,100,340,320),Rect2(570,320,370,300),Rect2(1030,100,360,320),Rect2(1640,80,390,320)]
    var texture: AtlasTexture = AtlasTexture.new()
    texture.atlas = PORTRAITS
    texture.region = regions[index]
    return texture

func _prepare_units() -> void:
    var metrics: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/v2/animation_metrics.json"))
    for i in range(4):
        var unit: Control = $Battle.get_node("Unit%d" % i)
        units.append(unit)
        unit.get_node("Art").sprite_frames = load("res://resources/%s_frames.tres" % UNIT_KEYS[i])
        unit.configure(i,metrics[UNIT_KEYS[i]])
        unit.get_node("Name").text = "烬火法师" if i == 0 else Rules.ENEMIES[i-1].name
        unit.get_node("Inspect").mouse_entered.connect(func() -> void: show_unit(i))
        unit.get_node("Inspect").pressed.connect(func() -> void: choose_target(i-1))
        unit.get_node("Intent").mouse_entered.connect(func() -> void: show_intent(i,false))
        unit.get_node("Intent").pressed.connect(func() -> void: show_intent(i,false))
        unit.get_node("Reaction").mouse_entered.connect(func() -> void: show_intent(i,true))
        unit.get_node("Reaction").pressed.connect(func() -> void: show_intent(i,true))
        unit.get_node("Burn").mouse_entered.connect(func() -> void: show_burn(i))
        unit.get_node("Burn").pressed.connect(func() -> void: show_burn(i))
        if i == 0:
            unit.get_node("Intent").visible = false
            unit.get_node("Reaction").visible = false
        else:
            unit.get_node("Intent/IntentIcon").texture = icon(Rules.ENEMIES[i-1].icon)
        $Track.get_node("Actor%d/Portrait" % i).texture = _portrait(i)
        $Track.get_node("Actor%d" % i).mouse_entered.connect(func() -> void: show_unit(i))
        $Track.get_node("Actor%d" % i).pressed.connect(func() -> void: show_unit(i))
        var fill: StyleBoxFlat = StyleBoxFlat.new()
        fill.bg_color = Color("#718f7a") if i == 0 else Color("#a63b24")
        unit.get_node("Health").add_theme_stylebox_override("fill",fill)

func _prepare_controls() -> void:
    for group in range(2):
        var count: int = 4 if group == 0 else 2
        for i in range(count):
            var slot: Button = slot_node(group,i)
            slot.pressed.connect(func() -> void: open_library(group,i))
            slot.mouse_entered.connect(func() -> void: show_slot(group,i))
            slot.get_node("Tune").pressed.connect(func() -> void: tune_slot(group,i))
            slot.get_node("Tune").mouse_entered.connect(func() -> void: show_slot(group,i))
            if group == 0:
                slot.get_node("Left").pressed.connect(func() -> void: move_slot(i,-1))
                slot.get_node("Right").pressed.connect(func() -> void: move_slot(i,1))
    for i in range(7):
        $Library.get_node("Choice%d" % i).mouse_entered.connect(func() -> void: show_candidate(i,false))
        $Library.get_node("Choice%d" % i).pressed.connect(func() -> void: show_candidate(i,true))
    $Library/Close.pressed.connect(close_library)
    $Library/Equip.pressed.connect(equip_candidate)
    $Library/Remove.pressed.connect(remove_slot)
    $Details/Preview.pressed.connect(preview_skill)
    $Details/Config/Condition.item_selected.connect(_condition_changed)
    $Details/Config/Target.item_selected.connect(_target_changed)
    $Details/Config/Enabled.toggled.connect(func(value: bool) -> void:
        selected_rule().enabled = value
        refresh_slots())
    for text in ["战术 · 扩散燃爆","战术 · 单点击杀","战术 · 全场焚烧"]:
        $Controls/Preset.add_item(text)
    $Controls/Preset.allow_reselect = true
    $Controls/Preset.item_selected.connect(preset)
    for text in ["1× 速度","2× 速度","4× 速度"]:
        $Controls/Speed.add_item(text)
    $Controls/Speed.item_selected.connect(func(i: int) -> void: speed = [1.0,2.0,4.0][i])
    $Controls/Start.pressed.connect(start_battle)
    $Controls/Pause.pressed.connect(toggle_pause)
    $Controls/Step.pressed.connect(step_once)
    $Controls/Reset.pressed.connect(reset_battle)
    $Controls/Save.pressed.connect(save_tactics)
    $Controls/Settings.pressed.connect(func() -> void: $Settings.visible = not $Settings.visible)
    $Settings/Close.pressed.connect(func() -> void: $Settings.hide())
    $Settings/ClickTarget.set_pressed_no_signal(click_target)
    $Settings/ClickTarget.toggled.connect(func(value: bool) -> void:
        click_target = value
        refresh_slots())
    $Settings/ClearTarget.pressed.connect(func() -> void:
        if not running and not previewing:
            marked = -1
            render_state(shown_state)
            refresh_slots())
    $Settings/Motion.toggled.connect(func(value: bool) -> void: fx.reduced = value)
    $Settings/Sound.button_pressed = true
    timer.timeout.connect(advance)
    $PreviewReset.timeout.connect(_finish_preview)

func slot_node(group: int, index: int) -> Button:
    return $Slots.get_node("A%d" % index) if group == 0 else $Reactions.get_node("P%d" % index)

func selected_rule() -> Dictionary:
    return plan[selected_slot] if selected_group == 0 else passives[selected_slot]

func refresh_slots() -> void:
    var ap_total: int = 0
    for group in range(2):
        var entries: Array = plan if group == 0 else passives
        for i in range(entries.size()):
            var entry: Dictionary = entries[i]
            var button: Button = slot_node(group,i)
            var definition: Dictionary = Rules.skill(entry.id)
            button.get_node("Icon").texture = icon(definition.icon) if not definition.is_empty() else null
            button.get_node("Name").text = definition.name if not definition.is_empty() else "+ 装备"
            button.get_node("Cost").text = ("%d AP" % definition.cost if group == 0 else "1 RP · "+definition.timing) if not definition.is_empty() else "空技能槽"
            button.disabled = running or previewing
            button.get_node("Tune").disabled = running or previewing or definition.is_empty()
            button.modulate = Color.WHITE if entry.enabled else Color(0.5,0.5,0.5)
            if group == 0:
                button.get_node("Condition").text = Rules.CONDITIONS[entry.condition]
                button.get_node("Left").disabled = running or previewing or i == 0
                button.get_node("Right").disabled = running or previewing or i == 3
                if entry.enabled and not definition.is_empty():
                    ap_total += definition.cost
    $ActiveTitle.text = "行动序列 · 4 个装备槽    %d / %d AP" % [ap_total,BALANCE.action_points]
    $ActiveTitle.modulate = Color(1,0.68,0.35) if ap_total > BALANCE.action_points else Color.WHITE
    $TargetHint.text = "优先目标："+(Rules.ENEMIES[marked].name if marked >= 0 else "自动")
    for control_name in ["Start","Preset","Save"]:
        $Controls.get_node(control_name).disabled = running or previewing
    $Settings/ClickTarget.disabled = running or previewing
    $Settings/ClearTarget.disabled = running or previewing

func open_library(group: int, index: int) -> void:
    if running or previewing:
        return
    selected_group = group
    selected_slot = index
    candidate = selected_rule().id
    $Settings.hide()
    $Library.show()
    $Library/Title.text = ("行动槽 %d" if group == 0 else "反应槽 %d") % (index+1)+" / 选择装备"
    var definitions: Array = Rules.SKILLS if group == 0 else Rules.PASSIVES
    for i in range(7):
        var button: Button = $Library.get_node("Choice%d" % i)
        button.visible = i < definitions.size()
        if i < definitions.size():
            button.get_node("Icon").texture = icon(definitions[i].icon)
            button.get_node("Name").text = definitions[i].name
            button.get_node("Cost").text = "%d %s" % [definitions[i].cost,"AP" if group == 0 else "RP"]
            button.modulate = Color(1,0.71,0.38) if definitions[i].id == candidate else Color.WHITE
    if candidate != "":
        show_skill(candidate,false)
    else:
        show_text("选择一项技能","悬停查看效果，点击候选后装备。")

func show_candidate(index: int, select: bool) -> void:
    var definitions: Array = Rules.SKILLS if selected_group == 0 else Rules.PASSIVES
    if index >= definitions.size():
        return
    if select:
        candidate = definitions[index].id
        for i in range(definitions.size()):
            $Library.get_node("Choice%d" % i).modulate = Color(1,0.71,0.38) if i == index else Color.WHITE
    show_skill(definitions[index].id,false)

func close_library() -> void:
    $Library.hide()
    if not previewing:
        show_slot(selected_group,selected_slot)

func equip_candidate() -> void:
    if running or previewing or candidate == "":
        return
    if selected_group == 1:
        var other: int = 1-selected_slot
        if passives[other].id == candidate:
            passives[other] = selected_rule().duplicate(true)
    selected_rule().id = candidate
    selected_rule().condition = 0
    selected_rule().target = 0
    selected_rule().enabled = true
    $Library.hide()
    refresh_slots()
    show_skill(candidate,true)

func remove_slot() -> void:
    if running or previewing:
        return
    selected_rule().id = ""
    $Library.hide()
    refresh_slots()
    show_text("空技能槽","点击技能槽装备法术。")

func tune_slot(group: int, index: int) -> void:
    selected_group = group
    selected_slot = index
    $Library.hide()
    $Settings.hide()
    show_skill(selected_rule().id,true)

func show_slot(group: int, index: int) -> void:
    var entry: Dictionary = plan[index] if group == 0 else passives[index]
    if entry.id == "":
        show_text("空技能槽","点击装备行动技能。" if group == 0 else "点击装备反应技能。")
    else:
        show_skill(entry.id,false)

func show_skill(id: String, configure: bool = false) -> void:
    var definition: Dictionary = Rules.skill(id)
    if definition.is_empty():
        return
    detail_skill = id
    detail_focus.clear()
    $Details/Icon.texture = icon(definition.icon)
    $Details/Title.text = definition.name
    $Details/Cost.text = "%d %s" % [definition.cost,"RP" if Rules.is_passive(id) else "AP"]
    $Details/Text.text = definition.desc
    $Details/Preview.visible = not running
    $Details/Preview.disabled = previewing
    $Details/Config.visible = configure and not running and not previewing
    if configure:
        configure_rule()

func show_text(title: String, body: String, cost: String = "", texture: Texture2D = null) -> void:
    detail_skill = ""
    detail_focus.clear()
    $Details/Title.text = title
    $Details/Text.text = body
    $Details/Cost.text = cost
    $Details/Icon.texture = texture
    $Details/Config.hide()
    $Details/Preview.hide()

func configure_rule() -> void:
    var entry: Dictionary = selected_rule()
    var options: OptionButton = $Details/Config/Condition
    options.clear()
    var labels: Array = Rules.CONDITIONS if selected_group == 0 else ["总是","自身生命 < 50%","RP ≥ 2"]
    for text in labels:
        options.add_item(text)
    options.select(int(entry.condition))
    var targets: OptionButton = $Details/Config/Target
    targets.clear()
    var fixed: bool = selected_group == 1 or entry.id in ["double","wall","funeral","inferno"]
    if fixed:
        targets.add_item("自身 / 固定时机" if selected_group == 1 else ("燃烧最多" if entry.id == "double" else "全体敌人"))
    else:
        for text in Rules.TARGETS:
            targets.add_item(text)
        targets.select(int(entry.target))
    targets.disabled = fixed
    $Details/Config/Enabled.set_pressed_no_signal(entry.enabled)
    $Details/Config/Label.text = ("调整行动槽 %d" if selected_group == 0 else "调整反应槽 %d") % (selected_slot+1)

func _condition_changed(index: int) -> void:
    selected_rule().condition = index
    refresh_slots()

func _target_changed(index: int) -> void:
    selected_rule().target = index

func move_slot(index: int, direction: int) -> void:
    var next: int = index+direction
    if running or previewing or next < 0 or next >= 4:
        return
    var old: Dictionary = plan[index]
    plan[index] = plan[next]
    plan[next] = old
    selected_slot = next
    selected_group = 0
    refresh_slots()
    show_skill(plan[next].id,true)

func show_unit(actor: int) -> void:
    if shown_state.is_empty():
        return
    if actor == 0:
        var names: Array = []
        for entry in passives:
            if not Rules.skill(entry.id).is_empty():
                names.append(Rules.skill(entry.id).name)
        show_text("烬火法师","反应装备："+"、".join(names),"生命 %d/%d · AP %d · RP %d" % [shown_state.hp,BALANCE.hero_health,shown_state.ap,shown_state.rp],_portrait(0))
    else:
        var enemy: Dictionary = shown_state.enemies[actor-1]
        var data: Dictionary = Rules.ENEMIES[actor-1]
        show_text(data.name,"主动：%s · %d 伤害\n被动：%s" % [data.attack,BALANCE.enemy_damage[actor-1],data.passive if data.passive != "" else "无"],"生命 %d/%d · AP %d · RP %d" % [enemy.hp,enemy.max_hp,enemy.ap,enemy.rp],_portrait(actor))
    detail_focus = {"kind":"unit","actor":actor}

func show_intent(actor: int, reaction: bool) -> void:
    if actor == 0:
        show_unit(actor)
        return
    var index: int = actor-1
    var data: Dictionary = Rules.ENEMIES[index]
    if reaction:
        show_text(data.passive if data.passive != "" else "无被动", "受到直接攻击前减伤 50%，每回合一次。" if index == 1 else "此敌人没有反应技能。","1 RP" if index == 1 else "0 RP",icon(7) if index == 1 else null)
    else:
        show_text(data.attack,"对法师造成 %d 伤害。" % BALANCE.enemy_damage[index],"1 AP · 主动",icon(data.icon))

func show_burn(actor: int) -> void:
    if actor <= 0:
        return
    var count: int = shown_state.enemies[actor-1].burn
    show_text("燃烧","回合末造成 %d 伤害并清空。即时引爆保留层数。" % (count*BALANCE.burn_damage),"%d 层" % count,icon(13))
    detail_focus = {"kind":"burn","actor":actor}

func choose_target(index: int) -> void:
    if index < 0:
        show_unit(0)
        return
    if click_target and not running and not previewing:
        marked = -1 if marked == index else index
        refresh_slots()
        render_state(shown_state)
    show_unit(index+1)

func preset(index: int) -> void:
    if running or previewing:
        return
    plan = Rules.default_plan()
    passives = Rules.default_passives()
    if index == 1:
        plan = [Rules.rule("ignite"),Rules.rule("double"),Rules.rule("burst"),Rules.rule("burst")]
    elif index == 2:
        plan = [Rules.rule("wall"),Rules.rule("funeral"),Rules.rule("inferno"),Rules.rule("ignite")]
        passives = [Rules.rule("charge"),Rules.rule("mana")]
    reset_battle()

func _initial_state() -> Dictionary:
    var engine = Rules.new()
    engine.initialize(BALANCE,marked)
    return engine.state.duplicate(true)

func reset_battle() -> void:
    timer.stop()
    timer.paused = false
    $PreviewReset.stop()
    running = false
    previewing = false
    paused = false
    cursor = -1
    events.clear()
    skipped.clear()
    result_data.clear()
    fx.clear_effects()
    if shake_tween and shake_tween.is_valid():
        shake_tween.kill()
    $Battle.position = Vector2(28,138)
    $Battle/Banner.text = ""
    $Controls/Pause.text = "暂停"
    $Controls/Pause.disabled = false
    $Controls/Step.disabled = false
    $Library.hide()
    $Library/Equip.disabled = false
    $Library/Remove.disabled = false
    $SoundPlayer.stop()
    for unit in units:
        unit.reset_animation()
    render_state(_initial_state())
    refresh_slots()
    show_text("战前准备","点击技能槽装备法术。\n点击怪物标记优先目标。")
    $Feedback.text = "悬停人物、技能和意图查看详情"

func start_battle() -> void:
    if running or previewing:
        return
    $Library.hide()
    $Settings.hide()
    events = Rules.new().simulate(plan.duplicate(true),passives.duplicate(true),BALANCE,marked)
    cursor = -1
    running = true
    paused = false
    timer.paused = false
    result_data.clear()
    skipped.clear()
    fx.clear_effects()
    refresh_slots()
    $Details/Config.hide()
    $Details/Preview.hide()
    advance()

func preview_skill() -> void:
    if detail_skill == "" or running or previewing:
        return
    events = Rules.new().preview(detail_skill,BALANCE)
    cursor = -1
    previewing = true
    paused = false
    timer.paused = false
    fx.clear_effects()
    refresh_slots()
    $Details/Preview.disabled = true
    $Library/Equip.disabled = true
    $Library/Remove.disabled = true
    advance()

func _finish_preview() -> void:
    previewing = false
    timer.stop()
    fx.clear_effects()
    render_state(_initial_state())
    refresh_slots()
    $Library/Equip.disabled = false
    $Library/Remove.disabled = false
    $Details/Preview.disabled = false
    $Battle/Banner.text = ""
    for unit in units:
        unit.reset_animation()

func toggle_pause() -> void:
    if not running or not result_data.is_empty():
        return
    paused = not paused
    timer.paused = paused
    $Controls/Pause.text = "继续" if paused else "暂停"
    if not paused and timer.is_stopped():
        timer.start(0.1)

func step_once() -> void:
    if previewing or not result_data.is_empty():
        return
    if not running:
        start_battle()
    paused = true
    timer.stop()
    timer.paused = true
    $Controls/Pause.text = "继续"
    advance()

func render_state(state: Dictionary, animate_track: bool = false) -> void:
    shown_state = state.duplicate(true)
    $Round.text = "技能预览" if previewing else ("战前编排" if state.round == 0 else "第 %d 回合" % state.round)
    $Track.update_track(state,animate_track,speed)
    for i in range(4):
        var data: Dictionary = {"hp":state.hp,"max_hp":BALANCE.hero_health,"ap":state.ap,"rp":state.rp} if i == 0 else state.enemies[i-1]
        units[i].get_node("Health").max_value = data.max_hp
        units[i].get_node("Health").value = data.hp
        units[i].get_node("Numbers").text = "%d/%d · AP %d  RP %d" % [data.hp,data.max_hp,data.ap,data.rp]
        units[i].get_node("Art").modulate = Color.WHITE if data.hp > 0 else Color(0.35,0.35,0.35,0.18)
        units[i].set_selected(i-1 == marked and i > 0 and data.hp > 0)
        if i > 0:
            units[i].get_node("Intent").visible = data.hp > 0
            units[i].get_node("Reaction").visible = data.hp > 0
            units[i].get_node("Intent/IntentCost").text = "主动 · %d AP" % data.ap
            units[i].get_node("Intent").modulate = Color.WHITE if data.ap > 0 else Color(0.55,0.55,0.55)
            units[i].get_node("Reaction").text = ("护身" if i == 2 else "无被动")+" · %d RP" % data.rp
            units[i].get_node("Burn").visible = data.burn > 0
            units[i].get_node("Burn").text = "燃烧 %d · %d伤" % [data.burn,data.burn*BALANCE.burn_damage]
            fx.burns[i-1] = data.burn if data.hp > 0 else 0
    if not detail_focus.is_empty():
        var focus: Dictionary = detail_focus.duplicate()
        if focus.kind == "unit":
            show_unit(focus.actor)
        elif focus.kind == "burn":
            show_burn(focus.actor)

func advance() -> void:
    if (not running and not previewing) or cursor+1 >= events.size():
        return
    cursor += 1
    var event: Dictionary = events[cursor]
    render_state(event.state,event.kind == "turn")
    var hold: float = 0.12
    match event.kind:
        "round":
            $Battle/Banner.text = "第 %d 回合\nAP / RP 已恢复" % event.state.round
            $Feedback.text = "新回合 · 存活角色重新进入行动轴"
            hold = maxf(1.3,0.7*speed)
        "turn":
            $Battle/Banner.text = ""
            hold = 0.75
        "turn_end":
            $Feedback.text = "行动结束 · 退出本轮行动轴"
            hold = 0.3
        "wait":
            fx.floating(event.actor,"待机",Color("#b6c9cb"),"skill")
            $Feedback.text = event.text
            hold = 0.6
        "cast":
            units[0].attack(speed)
            fx.floating(0,event.text,Color("#ffe2aa"),"skill")
            if event.skill in ["wall","funeral","inferno"]:
                for i in range(3):
                    if event.state.enemies[i].hp > 0:
                        fx.projectile(0,i+1)
            else:
                fx.projectile(0,event.target+1)
            _sound("cast")
            hold = 0.52
        "enemy":
            units[event.actor].attack(speed)
            fx.floating(event.actor,event.text,Color("#f4bb84"),"skill")
            hold = 0.52
        "hit","blast":
            fx.floating(event.target+1,str(event.amount),Color("#ffb84d") if event.kind == "blast" else Color("#f5e2c1"),event.kind)
            if event.kind == "blast":
                fx.burst(event.target+1,event.amount)
                _sound("blast")
                if not fx.reduced:
                    if shake_tween and shake_tween.is_valid():
                        shake_tween.kill()
                    shake_tween = create_tween()
                    shake_tween.tween_property($Battle,"position",Vector2(31,138),0.04)
                    shake_tween.tween_property($Battle,"position",Vector2(25,138),0.04)
                    shake_tween.tween_property($Battle,"position",Vector2(28,138),0.08)
                hold = 0.3
            else:
                _sound("hit")
        "burn":
            fx.floating(event.target+1,"燃烧 +%d" % event.amount,Color("#ff9c43"),"buff")
        "hurt":
            fx.floating(0,"-%d" % event.amount,Color("#ff7657"))
            _sound("hit")
            hold = 0.25
        "shield","mana","charge","enemy_guard":
            fx.floating(event.actor,event.text,Color("#9ddce3"),"skill")
            _sound("buff")
            hold = 0.34
        "detonate":
            fx.floating(event.target+1,"燃烧引爆",Color("#ffc86c"),"skill")
            fx.burst(event.target+1,event.amount)
            hold = 0.28
        "transfer":
            fx.projectile(event.actor,event.target+1)
            fx.floating(event.target+1,"余烬转移",Color("#ffc86c"),"skill")
            hold = 0.4
        "skip":
            skipped.append(event.text)
            $Feedback.text = event.text
            hold = 0.2
        "end_round":
            $Battle/Banner.text = "第 %d 回合结束\n燃烧结算" % event.state.round
            $Feedback.text = "所有角色 AP 已用完 · 结算燃烧"
            hold = maxf(1.0,0.6*speed)
        "result":
            result_data = event
            $Battle/Banner.text = event.text+"\n剩余 %d 生命" % event.state.hp
            $Controls/Pause.disabled = true
            $Controls/Step.disabled = true
            var comparison: String = ""
            if not previous_result.is_empty():
                comparison = "\n较上一场：生命 %+d · 回合 %+d" % [event.state.hp-previous_result.hp,event.state.round-previous_result.round]
            show_text("战斗复盘","%d 回合 · 最高 %d 层燃烧%s\n%s" % [event.state.round,event.peak_burn,comparison,"没有因条件或 AP 跳过行动" if skipped.is_empty() else "跳过："+skipped[-1]],"剩余 %d 生命 · 实伤 %d" % [event.state.hp,event.total_damage])
            previous_result = {"hp":event.state.hp,"round":event.state.round}
            $Feedback.text = "返回编排，调整技能再试一场"
            return
        "preview_end":
            $PreviewReset.start()
            return
    for i in range(4):
        slot_node(0,i).modulate = Color(1,0.68,0.33) if event.slot == i and event.kind in ["cast","burn","blast","hit"] else Color.WHITE
    if not paused:
        timer.start(maxf(0.035,hold/speed))

func _sound(id: String) -> void:
    if not $Settings/Sound.button_pressed:
        return
    $SoundPlayer.stream = load("res://assets/%s.wav" % id)
    $SoundPlayer.play()

func save_tactics() -> void:
    $Feedback.text = "战术已保存" if Store.save_data(plan,passives,marked,click_target) else "保存失败，请重试"
