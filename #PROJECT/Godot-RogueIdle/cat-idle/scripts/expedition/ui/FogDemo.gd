extends Control

@export var catalog: FogCatalog
## Seconds per combat event at 1x; calculations are independent of playback.
@export_range(0.1, 2.0, 0.05) var playback_interval: float = 0.65
@export var save_path: String = FogSave.SLOT
var run: FogRun = FogRun.new()
var started: bool = false
var selected_region: String = "briar"
var inventory_ids: Array[String] = []
var activity_ids: Array[String] = []
var modal_actions: Array[Callable] = []
var elapsed: float = 0.0
var save_message: String = "准备出发"
const SET_HELP: Dictionary = {
    "thorn": "荆棘 · 2件：受直接攻击后反击，每回合一次。\n3件：反击后获得护盾。适合前排生存。",
    "storm": "猎风 · 2件：攻击被标记目标增伤。\n3件：每回合首次命中标记目标追加追击。适合游侠协同。",
    "ember": "余烬 · 2件：直接命中附加灼烧。\n3件：灼烧造成伤害后治疗主角，每回合有上限。"}
const ACTIVE_IDS: Array[String] = ["guard", "burst", "fire"]
const PASSIVE_IDS: Array[String] = ["resolve", "regen", "fury"]
const TARGET_IDS: Array[String] = ["front", "lowest", "marked"]
const POLICY_IDS: Array[String] = ["ready", "threat", "mark"]

func n(node_name: String) -> Node:
    return find_child(node_name, true, false)

func _ready() -> void:
    DisplayServer.window_set_title("雾境远征 · Godot Demo")
    run.configure(catalog)
    run.new_run(42)
    _connect_button("NewRun", _new_run_modal)
    _connect_button("ContinueRun", _continue_run)
    _connect_button("Help", _help)
    _connect_button("EnterRegion", _enter_region)
    _connect_button("ApplyTactics", _apply_tactics)
    _connect_button("SwapFront", func() -> void: _commit(run.swap_formation(0)))
    _connect_button("SwapRear", func() -> void: _commit(run.swap_formation(1)))
    _connect_button("EquipItem", _equip_selected)
    _connect_button("Pause", _toggle_pause)
    _connect_button("Skip", _skip_battle)
    _connect_button("Claim", _show_pending)
    _connect_button("Pending", _show_pending)
    for speed: int in [1, 2, 4]:
        _connect_button("Speed%d" % speed, _set_speed.bind(speed))
    for i: int in range(5):
        _connect_button("Activity%d" % i, _activity.bind(i))
    for i: int in range(3):
        _connect_button("ModalAction%d" % i, _modal_action.bind(i))
    for tile: Node in n("World").get_children():
        tile.region_selected.connect(_select_region)
    n("Inventory").item_selected.connect(_inventory_selected)
    _fill_options("ActiveChoice", ["铁壁：护盾40 + 普攻", "重击：185%攻击", "火种：90%攻击 + 2层灼烧"])
    _fill_options("PassiveChoice", ["坚韧：护甲+3 / 速度-2", "复苏：行动前恢复6生命", "强攻：攻击+15% / 护甲-2"])
    _fill_options("TargetChoice", ["优先前排", "最低生命比例", "优先标记目标"])
    _fill_options("PolicyChoice", ["冷却完毕即释放", "铁壁：等待重击威胁", "重击：最多等待一次标记"])
    _render()
    _new_run_modal()

func _connect_button(node_name: String, callback: Callable) -> void:
    n(node_name).pressed.connect(callback)

func _fill_options(node_name: String, labels: Array) -> void:
    var box: OptionButton = n(node_name)
    box.clear()
    for label: String in labels:
        box.add_item(label)

func _process(delta: float) -> void:
    if not started or run.data.phase != "battle" or bool(run.data.battle.paused):
        return
    elapsed += delta * float(run.data.battle.speed)
    if elapsed >= playback_interval:
        elapsed = 0.0
        run.advance_battle()
        _save()
        _render_battle()
        n("Pending").visible = run.data.phase == "reward"
        if run.data.phase == "reward":
            _render()

func _save() -> void:
    if not started:
        return
    var result: Dictionary = FogSave.save_state(run.data, save_path)
    save_message = str(result.message)
    n("SaveStatus").text = save_message
    n("SaveStatus").modulate = Color("#91bba9") if result.ok else Color("#fa9284")

func _commit(ok: bool) -> void:
    if not ok:
        n("Footer").text = run.error_message
        return
    _save()
    _render()

func _render() -> void:
    n("Summary").text = "小队 Lv.%d     金币 %d     %s" % [run.data.level, run.data.gold, run.region().name]
    n("ContinueRun").disabled = not FogSave.has_save(save_path)
    n("Budget").text = "区域时段  %d / 6" % run.budget() if run.data.current not in ["village", "castle"] else ("最后一战" if run.data.current == "castle" else "整备后出发")
    n("BudgetBar").value = run.budget()
    var party: Array = run.members()
    for i: int in range(3):
        n("Party%d" % i).display_unit(party[i] if i < party.size() else {}, i)
    n("PartyNote").text = "前排承受多数攻击\n跨区不回血 · 休整消耗1时段"
    var set_info: Dictionary = run.set_status()
    n("SetSummary").text = "%s%s" % [set_info.name, " · %d件" % set_info.count if int(set_info.count) > 0 else ""]
    for tile: Node in n("World").get_children():
        tile.refresh(run.data.revealed.has(tile.definition.id), run.data.current == tile.definition.id,
            run.region().next_ids.has(tile.definition.id), selected_region == tile.definition.id)
    _render_region()
    _render_loadout()
    _render_battle()
    n("Pending").visible = started and run.data.phase in ["event", "reward", "ended"]
    n("Pending").text = "查看远征结果" if run.data.phase == "ended" else "处理待结算内容"
    n("Footer").text = str(run.data.history.back()) if started else "选择远征流派与首名伙伴，向北穿越三个地区。"

func _select_region(id_value: String) -> void:
    selected_region = id_value
    _render()

func _render_region() -> void:
    var row: Dictionary = run.region(selected_region)
    var known: bool = run.data.revealed.has(selected_region)
    var visible_info: bool = known or bool(row.initial_landmark)
    n("RegionTitle").text = row.name if visible_info else "未探明地区"
    var details: String = ""
    if visible_info:
        details = "[color=#e6c780]%s[/color]\n%s\n\n" % [row.boss_name, SET_HELP.get(row.family, "攻破魔王城，结束本次远征。")]
        details += "已揭雾：活动已确定。" if known else "远方地标：可规划掉落路线，活动仍未知。"
    else:
        details = "进入相邻地区后，自动揭开迷雾。\n\n每次只能沿相邻地区向北前进。"
    if selected_region == run.data.current:
        if run.data.current == "village":
            details = "鹿鸣村 · 远征起点\n\n选择一个北方相邻地区，踏上旅途。"
        elif run.data.current != "castle":
            details += "\n副本已胜 %d 次，重复挑战首领会变强。" % run.local_state().wins
    n("RegionDescription").text = details
    var can_enter: bool = started and run.can_edit() and run.region().next_ids.has(selected_region)
    n("EnterRegion").disabled = not can_enter
    n("EnterRegion").text = "前往 %s →" % row.name if can_enter else ("当前位置" if selected_region == run.data.current else "选择相邻前方地区")
    n("ActivityHeading").text = "当前地区 · 可用行动"
    activity_ids.clear()
    if run.data.current == "castle":
        activity_ids.append("dungeon")
    elif run.data.current != "village":
        activity_ids.assign(["dungeon", "rest"])
        activity_ids.append_array(run.local_state().activities)
    for i: int in range(5):
        var button: Button = n("Activity%d" % i)
        button.visible = i < activity_ids.size()
        if i >= activity_ids.size():
            continue
        var id_value: String = activity_ids[i]
        var issue: String = run.activity_error(id_value)
        var cost: int = 0 if run.data.current == "castle" else int(run.tables.activities[id_value].ap_cost)
        button.text = "%s  ·  %d时段" % [run.tables.activities[id_value].name, cost]
        button.disabled = not started or not issue.is_empty()
        button.tooltip_text = issue if not issue.is_empty() else "查看详情后执行"
    n("ActivityHint").text = "时段用尽，可选择相邻前方地区。" if run.budget() == 0 and run.data.current not in ["village", "castle"] else "可以提前离开。未用完的时段不会保留。"

func _enter_region() -> void:
    var target: String = selected_region
    if run.budget() > 0:
        _modal("离开这个地区？", "将放弃剩余 %d 时段，生命与装备延续。离开后不能返回。" % run.budget(),
            ["确认前往", "继续探索"], [func() -> void: _move(target), _close_modal])
    else:
        _move(target)

func _move(target: String) -> void:
    _close_modal()
    _commit(run.move_to(target))

func _activity(index: int) -> void:
    if not started or index >= activity_ids.size():
        return
    var activity: String = activity_ids[index]
    match activity:
        "dungeon", "patrol":
            var preview: String = "自动回合战斗。入场支付时段，战败则本次远征结束。\n\n"
            for enemy: Dictionary in run.preview_enemies(activity):
                preview += "%s  ·  生命%d / 攻击%d / 护甲%d / 速度%d\n" % [enemy.name, enemy.hp, enemy.atk, enemy.armor, enemy.speed]
            preview += "\n" + _boss_hint(str(run.region().family))
            _modal("挑战预览", preview, ["出战", "返回整备"], [func() -> void: _start_battle(activity), _close_modal])
        "rest":
            _modal("营地休整", "消耗1时段，全队恢复50%最大生命。", ["休整", "取消"],
                [func() -> void: _close_modal(); _commit(run.rest()), _close_modal])
        "chest":
            _close_modal()
            _commit(run.open_chest())
            _show_pending()
        "recruit":
            _recruit_modal()
        "merchant":
            _modal("旅行商人 · 每区一次", "交易消耗1时段。\n补给：25金币，全队恢复80%最大生命。\n装备：30金币，购买下列精良装备。\n\n" + run.item_description(run.local_state().merchant_item),
                ["购买补给", "购买装备", "离开"], [_trade.bind("heal"), _trade.bind("gear"), _close_modal])
        "event":
            _modal("调查 · " + str(run.event_definition().name), "消耗1时段进入事件，再选择一项结果。", ["调查", "离开"],
                [func() -> void: _commit(run.begin_event()); _show_pending(), _close_modal])

func _boss_hint(family: String) -> String:
    return str({"thorn": "首领每3回合重击前排，准备护盾或调整前排。",
        "storm": "第2回合瞄准，第3回合攻击后排，避免脆弱成员落在后排。",
        "ember": "首轮点燃，第3回合群攻，对灼烧目标更强。",
        "king": "魔王每3回合群攻，暗影随从攻击后排。"} .get(family, "速度决定出手顺序。"))

func _start_battle(activity: String) -> void:
    if run.begin_battle(activity):
        _close_modal()
        elapsed = 0.0
        _save()
        _render()
        n("Pages").current_tab = 2
    else:
        n("ModalDescription").text = run.error_message

func _recruit_modal() -> void:
    var candidates: Array = run.recruit_candidates()
    var labels: Array = []
    var actions: Array[Callable] = []
    for candidate: String in candidates:
        labels.append("招募 " + str(run.tables.units[candidate].name))
        actions.append(_recruit.bind(candidate))
    labels.append("离开")
    actions.append(_close_modal)
    _modal("招募旅伴", "消耗1时段。新成员按小队最低生命比例加入。\n牧师：治疗低血量队友\n游侠：标记与输出\n卫士：保护当前前排\n\n最多两名随从；满队时需替换一名。", labels, actions)
    if run.data.party.size() == 3:
        n("ModalOptionA").visible = true
        n("ModalOptionA").clear()
        for i: int in range(run.data.party.size()):
            if run.data.party[i].id != "hero":
                n("ModalOptionA").add_item("替换 " + str(run.tables.units[run.data.party[i].id].name), i)

func _recruit(candidate: String) -> void:
    var replacement: int = n("ModalOptionA").get_selected_id() if run.data.party.size() == 3 else -1
    if run.recruit(candidate, replacement):
        _close_modal()
        _commit(true)
    else:
        n("ModalDescription").text = run.error_message

func _trade(choice: String) -> void:
    if run.merchant(choice):
        _close_modal()
        _commit(true)
        _show_pending()
    else:
        n("ModalDescription").text = run.error_message + "\n时段未扣除，选择另一项或离开。"

func _render_loadout() -> void:
    var parts: PackedStringArray = []
    for member: Dictionary in run.members():
        parts.append(str(member.name))
    n("Formation").text = "前排  " + "  →  ".join(parts) + "  后排"
    n("SwapFront").disabled = not started or not run.can_edit() or run.data.party.size() < 2
    n("SwapRear").disabled = not started or not run.can_edit() or run.data.party.size() < 3
    n("ActiveChoice").select(ACTIVE_IDS.find(str(run.data.active)))
    n("PassiveChoice").select(PASSIVE_IDS.find(str(run.data.passive)))
    n("TargetChoice").select(TARGET_IDS.find(str(run.data.target)))
    n("PolicyChoice").select(POLICY_IDS.find(str(run.data.policy)))
    n("ApplyTactics").disabled = not started or not run.can_edit()
    var equipped: String = ""
    for slot: String in ["weapon", "armor", "charm"]:
        equipped += "[color=#e6c780]%s[/color]\n%s\n\n" % [FogRun.SLOT_NAMES[slot], run.item_description(run.find_item(str(run.data.equipped[slot])))]
    n("Equipped").text = equipped
    var previous_id: String = ""
    var selected: PackedInt32Array = n("Inventory").get_selected_items()
    if not selected.is_empty() and selected[0] < inventory_ids.size():
        previous_id = inventory_ids[selected[0]]
    n("Inventory").clear()
    inventory_ids.clear()
    for item: Dictionary in run.data.inventory:
        inventory_ids.append(str(item.id))
        var wearing: bool = run.data.equipped[item.slot] == item.id
        n("Inventory").add_item(("%s  T%d" % [item.name, item.tier]) + (" · 已装备" if wearing else ""))
    var index: int = inventory_ids.find(previous_id)
    if index >= 0:
        n("Inventory").select(index)
        _inventory_selected(index)
    else:
        n("Comparison").text = "选择背包中的装备查看属性与替换对比。\n\n" + str(SET_HELP.get(run.set_status().id, "同一套装的2件与3件可激活不同效果。"))
        n("EquipItem").disabled = true

func _apply_tactics() -> void:
    _commit(run.configure_tactics(ACTIVE_IDS[n("ActiveChoice").selected], PASSIVE_IDS[n("PassiveChoice").selected],
        TARGET_IDS[n("TargetChoice").selected], POLICY_IDS[n("PolicyChoice").selected]))

func _inventory_selected(index: int) -> void:
    if index < 0 or index >= inventory_ids.size():
        return
    var item: Dictionary = run.find_item(inventory_ids[index])
    var old: Dictionary = run.find_item(str(run.data.equipped[item.slot]))
    n("Comparison").text = "[color=#e6c780]选中装备[/color]\n%s\n\n当前同部位\n%s\n\n%s" % [
        run.item_description(item), run.item_description(old), SET_HELP.get(item.set_id, "行旅装备无套装效果。")]
    n("EquipItem").disabled = not started or not run.can_edit() or old.get("id", "") == item.id

func _equip_selected() -> void:
    var selected: PackedInt32Array = n("Inventory").get_selected_items()
    if not selected.is_empty():
        _commit(run.equip(inventory_ids[selected[0]]))

func _render_battle() -> void:
    var frame: Dictionary = run.battle_frame()
    var allies: Array = []
    var enemies: Array = []
    if not frame.is_empty():
        for unit: Dictionary in frame.units:
            if unit.side == "ally":
                allies.append(unit)
            else:
                enemies.append(unit)
    for i: int in range(3):
        n("Ally%d" % i).display_unit(allies[i] if i < allies.size() else {}, i)
        n("Enemy%d" % i).display_unit(enemies[i] if i < enemies.size() else {}, i)
    n("RoundTitle").text = "第 %d 回合" % frame.get("round", 0) if not frame.is_empty() else "等待第一场战斗"
    n("BattleIntent").text = str(frame.get("text", "整备技能与阵位后，在地图选择副本或巡逻。"))
    var lines: PackedStringArray = []
    if not run.data.battle.is_empty():
        for i: int in range(maxi(0, int(run.data.battle.index) - 80), int(run.data.battle.index) + 1):
            var entry: Dictionary = run.data.battle.report.frames[i]
            lines.append("[color=#82999f]R%02d[/color]  %s" % [entry.round, entry.text])
    n("CombatLog").text = "\n".join(lines)
    var active: bool = started and run.data.phase == "battle"
    n("Pause").disabled = not active
    n("Pause").text = "继续" if bool(run.data.battle.get("paused", false)) else "暂停"
    n("Skip").disabled = not active
    for speed: int in [1, 2, 4]:
        n("Speed%d" % speed).disabled = not active
        n("Speed%d" % speed).text = ("%dx ✓" if int(run.data.battle.get("speed", 1)) == speed else "%dx") % speed
    n("Claim").disabled = not started or run.data.phase not in ["reward", "ended"]
    n("Claim").text = "远征结果" if run.data.phase == "ended" else "查看战报 / 领取"

func _toggle_pause() -> void:
    if run.data.phase == "battle":
        run.data.battle.paused = not run.data.battle.paused
        _save()
        _render_battle()

func _set_speed(speed: int) -> void:
    if run.data.phase == "battle":
        run.data.battle.speed = speed
        _save()
        _render_battle()

func _skip_battle() -> void:
    _commit(run.advance_battle(true))
    _show_pending()

func _report_text(report: Dictionary) -> String:
    var text: String = "%s · %d回合\n" % ["战斗胜利" if report.outcome == "victory" else "小队战败", report.rounds]
    for stat: Dictionary in report.stats.values():
        text += "%s  直伤%d / 反击%d / 追击%d / 灼烧%d / 治疗%d / 吸收%d\n" % [
            stat.name, stat.direct, stat.counter, stat.chase, stat.burn, stat.healing, stat.absorbed]
    var fallen: String = str(report.get("first_fall", ""))
    text += "\n首个倒下的队友：%s" % ("无" if fallen.is_empty() else fallen)
    return text

func _show_pending() -> void:
    match str(run.data.phase):
        "reward":
            var text: String = ""
            if run.data.pending.kind == "battle":
                text = _report_text(run.data.battle.report) + "\n\n"
            var item: Dictionary = run.data.pending.get("item", {})
            text += run.item_description(item) + "\n" if not item.is_empty() else ""
            text += "金币 +%d" % run.data.pending.get("gold", 0)
            _modal("结算", text, ["领取并装备", "收入背包"], [_claim.bind(true), _claim.bind(false)])
            if item.is_empty():
                n("ModalAction0").text = "确认结算"
                n("ModalAction1").visible = false
        "event":
            var event: Dictionary = run.event_definition()
            _modal(event.name, "选择一个结果。调查时段已支付。\n\nA · %s\n%s\n\nB · %s\n%s" % [
                event.option_a, _describe_effects(event.outcome_a), event.option_b, _describe_effects(event.outcome_b)],
                [event.option_a, event.option_b], [_choose_event.bind("a"), _choose_event.bind("b")])
            for i: int in range(2):
                var issue: String = run.event_choice_error("a" if i == 0 else "b")
                n("ModalAction%d" % i).disabled = not issue.is_empty()
                n("ModalAction%d" % i).tooltip_text = issue
            if event.id == "forge":
                _fill_options("ModalOptionA", ["打造武器", "打造护甲", "打造护符"])
                n("ModalOptionA").visible = true
        "ended":
            var text: String = ("魔王已倒下，小队完成了远征。" if run.data.outcome == "victory" else "远征在这里结束。可以换一种路线与构筑重来。") + "\n\n"
            text += _report_text(run.data.last_report) + "\n\n路径："
            for id_value: String in run.data.visited:
                text += str(run.region(id_value).name) + "  "
            _modal("远征胜利" if run.data.outcome == "victory" else "远征结束", text,
                ["再启远征", "查看地图"], [_new_run_modal, _close_modal])

func _describe_effects(effects: String) -> String:
    var labels: Dictionary = {"gold": "金币", "hero_hp_cost": "主角支付生命", "party_heal_pct": "全队恢复最大生命%",
        "hero_heal_pct": "主角恢复最大生命%", "next_hero_atk_pct": "下场主角攻击%", "next_enemy_hp_pct": "下场敌方生命%",
        "next_enemy_atk_pct": "下场敌方攻击%", "next_enemy_armor_flat": "下场敌方护甲",
        "next_hero_shield": "下场主角护盾", "gear_choice_fine": "自选部位精良装备", "gear_random_normal": "随机普通装备"}
    var output: PackedStringArray = []
    for part: String in effects.split(";"):
        var pieces: PackedStringArray = part.split(":")
        output.append("%s %s" % [labels.get(pieces[0], pieces[0]), pieces[1]])
    return "；".join(output)

func _choose_event(branch: String) -> void:
    var slots: Array[String] = ["weapon", "armor", "charm"]
    if run.choose_event(branch, slots[maxi(0, n("ModalOptionA").selected)]):
        _close_modal()
        _commit(true)
        _show_pending()

func _claim(equip_now: bool) -> void:
    if run.claim_reward(equip_now):
        _close_modal()
        _commit(true)
        if run.data.phase == "ended":
            _show_pending()
        else:
            n("Pages").current_tab = 0

func _modal(title: String, description: String, labels: Array, actions: Array) -> void:
    n("Modal").visible = true
    n("ModalTitle").text = title
    n("ModalDescription").text = description
    n("ModalOptionA").visible = false
    n("ModalOptionB").visible = false
    modal_actions.assign(actions)
    for i: int in range(3):
        var button: Button = n("ModalAction%d" % i)
        button.visible = i < labels.size()
        button.disabled = false
        button.tooltip_text = ""
        if i < labels.size():
            button.text = labels[i]

func _modal_action(index: int) -> void:
    if index < modal_actions.size():
        modal_actions[index].call()

func _close_modal() -> void:
    n("Modal").visible = false

func _new_run_modal() -> void:
    _modal("雾境远征", "带领三人小队，向北攻破魔王城。\n\n每区6个时段：刷副本成套、招募伙伴，或为下一战休整。\n先选择开局战术与一名同行伙伴。\n\n新远征开始后将替换当前续档。", ["开始远征", "继续存档", "返回"],
        [_start_new_run, _continue_run, _close_modal])
    _fill_options("ModalOptionA", ["荆棘路线 · 铁壁 / 坚韧", "猎风路线 · 重击 / 强攻", "余烬路线 · 火种 / 复苏"])
    _fill_options("ModalOptionB", ["同行：牧师（治疗）", "同行：游侠（标记）", "同行：卫士（护盾）"])
    n("ModalOptionA").visible = true
    n("ModalOptionB").visible = true
    n("ModalAction1").disabled = not FogSave.has_save(save_path)
    n("ModalAction2").visible = started

func _start_new_run() -> void:
    var styles: Array[String] = ["thorn", "storm", "ember"]
    var companions: Array[String] = ["priest", "ranger", "guardian"]
    run.new_run(int(Time.get_unix_time_from_system()) % 2147483647, styles[n("ModalOptionA").selected], companions[n("ModalOptionB").selected])
    started = true
    selected_region = "briar"
    n("Pages").current_tab = 0
    _close_modal()
    _commit(true)

func _continue_run() -> void:
    var result: Dictionary = FogSave.load_state(save_path)
    if not result.ok:
        n("ModalDescription").text = result.message
        n("Footer").text = result.message
        return
    if not run.restore(result.state):
        n("ModalDescription").text = run.error_message
        return
    started = true
    selected_region = str(run.data.current)
    _close_modal()
    _render()
    n("Footer").text = "已从备份恢复。" if result.from_backup else "已继续远征；战斗回放保持暂停。"
    n("Pages").current_tab = 2 if run.data.phase == "battle" else 0
    _show_pending()

func _help() -> void:
    _modal("远征手册", "1. 地图上选择相邻北方地区，再点击前往。地标可以提前查看套装。\n\n2. 副本2时段，其他活动1时段。可提前离开，不能回头。\n\n3. 整备页可免费换技能、阵位和主角装备。2件与3件套会改变战斗方式。\n\n4. 战斗全自动，速度决定每回合顺序。暂停、加速、跳过只影响观看。\n\n5. 每区首次战斗胜利升级；生命不会随升级或跨区恢复。\n\n6. 每次操作自动存档。关闭后可继续，战利品不会重复领取。", ["明白了"], [_close_modal])
