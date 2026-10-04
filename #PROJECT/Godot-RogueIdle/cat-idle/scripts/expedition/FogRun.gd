@tool
class_name FogRun
extends RefCounted

const Combat = preload("res://scripts/expedition/FogCombat.gd")
const SET_NAMES: Dictionary = {"thorn": "荆棘", "storm": "猎风", "ember": "余烬", "": "行旅"}
const SLOT_NAMES: Dictionary = {"weapon": "武器", "armor": "护甲", "charm": "护符"}
var catalog: FogCatalog
var tables: Dictionary = {}
var data: Dictionary = {}
var error_message: String = ""

func configure(source: FogCatalog) -> void:
    catalog = source
    for table_name: String in ["regions", "units", "activities", "equipment", "affixes", "sets", "skills", "events"]:
        tables[table_name] = catalog.table(table_name)

func new_run(seed_value: int, style: String = "thorn", companion: String = "priest") -> void:
    var presets: Dictionary = {"thorn": ["guard", "resolve", "threat"], "storm": ["burst", "fury", "ready"],
        "ember": ["fire", "regen", "ready"]}
    var preset: Array = presets.get(style, presets.thorn)
    data = {"schema": 1, "rules_version": catalog.rules_version, "seed": seed_value,
        "run_id": "%d-%d" % [seed_value, Time.get_ticks_usec()], "phase": "region", "current": "village",
        "level": 1, "gold": int(catalog.rule("start_gold")), "party": [],
        "regions": {}, "revealed": [], "visited": ["village"], "inventory": [],
        "equipped": {"weapon": "", "armor": "", "charm": ""}, "ledger": {},
        "active": preset[0], "passive": preset[1], "policy": preset[2], "target": "front",
        "next_buff": {}, "used_events": [], "serial": 0, "claimed": [], "pending": {}, "battle": {},
        "history": ["小队在鹿鸣村集结。"], "last_report": {}, "ap_spent": {}, "outcome": ""}
    if companion not in ["priest", "ranger", "guardian"]:
        companion = "priest"
    data.party = [{"id": "hero", "hp": int(tables.units.hero.hp)},
        {"id": companion, "hp": int(tables.units[companion].hp)}]
    _reveal_neighbours("village")
    error_message = ""

func restore(snapshot: Dictionary) -> bool:
    if int(snapshot.get("schema", 0)) != 1 or snapshot.get("rules_version") != catalog.rules_version:
        return _reject("此存档属于不同规则版本，原文件已保留。")
    for field: String in ["party", "inventory", "visited", "revealed", "claimed"]:
        if not snapshot.get(field) is Array:
            return _reject("存档结构不完整：" + field)
    if not tables.regions.has(snapshot.get("current", "")):
        return _reject("存档地区无效。")
    if snapshot.get("phase", "") not in ["region", "battle", "reward", "event", "ended"]:
        return _reject("存档流程状态无效。")
    data = snapshot.duplicate(true)
    if data.phase == "battle":
        data.battle.paused = true
    error_message = ""
    return true

func _reject(message: String) -> bool:
    error_message = message
    return false

func _rng(channel: String) -> RandomNumberGenerator:
    var generator: RandomNumberGenerator = RandomNumberGenerator.new()
    generator.seed = absi(("%s/%s" % [data.seed, channel]).hash())
    return generator

func region(region_id: String = "") -> Dictionary:
    return tables.regions.get(str(data.get("current", "village")) if region_id.is_empty() else region_id, {})

func local_state() -> Dictionary:
    return data.regions.get(str(data.current), {})

func budget() -> int:
    return int(local_state().get("ap", 0))

func can_edit() -> bool:
    return not data.is_empty() and data.phase == "region"

func _reveal_neighbours(region_id: String) -> void:
    var to_reveal: Array = [region_id]
    to_reveal.append_array(tables.regions[region_id].adjacent_ids)
    for id_value: String in to_reveal:
        if data.revealed.has(id_value):
            continue
        data.revealed.append(id_value)
        if int(tables.regions[id_value].stage) > 0 and int(tables.regions[id_value].stage) < 4:
            _generate_area(id_value)

func _generate_area(region_id: String) -> void:
    if data.regions.has(region_id):
        return
    var generator: RandomNumberGenerator = _rng("area/" + region_id)
    var choices: Array = ["chest", "event", "patrol", "recruit", "merchant"]
    var picked: Array = []
    if int(tables.regions[region_id].stage) == 1:
        picked.append("recruit")
        choices.erase("recruit")
    while picked.size() < int(catalog.rule("optional_activities")):
        var weight_sum: int = 0
        for choice: String in choices:
            weight_sum += int(tables.activities[choice].draw_weight)
        var roll: int = generator.randi_range(1, weight_sum)
        for choice: String in choices:
            roll -= int(tables.activities[choice].draw_weight)
            if roll <= 0:
                picked.append(choice)
                choices.erase(choice)
                break
    var available_events: Array = tables.events.keys().filter(func(id_value: String) -> bool: return not data.used_events.has(id_value))
    if available_events.is_empty():
        available_events = tables.events.keys()
    available_events.sort()
    var event_id: String = str(available_events[generator.randi_range(0, available_events.size() - 1)])
    data.used_events.append(event_id)
    var candidates: Array = ["priest", "ranger", "guardian"]
    for i: int in range(candidates.size() - 1, 0, -1):
        var j: int = generator.randi_range(0, i)
        var swap: String = candidates[i]
        candidates[i] = candidates[j]
        candidates[j] = swap
    var tier: int = int(tables.regions[region_id].stage)
    var merchant_item: Dictionary = _make_item("", tier, "shop/" + region_id, "", "fine")
    var forge_items: Dictionary = {}
    for slot: String in ["weapon", "armor", "charm"]:
        forge_items[slot] = _make_item("", tier, "forge/%s/%s" % [region_id, slot], slot, "fine")
    data.regions[region_id] = {"ap": int(catalog.rule("region_ap")), "wins": 0, "leveled": false,
        "activities": picked, "completed": [], "event_id": event_id, "candidates": candidates,
        "merchant_item": merchant_item, "forge_items": forge_items}

func move_to(region_id: String) -> bool:
    if not can_edit():
        return _reject("先完成当前事件或领取结算。")
    if not region().next_ids.has(region_id):
        return _reject("只能进入当前位置相邻的前方地区。")
    data.current = region_id
    data.visited.append(region_id)
    _reveal_neighbours(region_id)
    _record("进入%s，剩余生命延续。" % region().name)
    return true

func _record(message: String) -> void:
    data.history.append(message)
    error_message = ""

func activity_error(activity: String) -> String:
    if not can_edit():
        return "请先处理当前待结算内容"
    if data.current == "village":
        return "从地图选择一个前方地区"
    if data.current == "castle":
        return "" if activity == "dungeon" else "魔王城仅提供最终战"
    if not tables.activities.has(activity):
        return "未知活动"
    if activity not in ["dungeon", "rest"] and not local_state().activities.has(activity):
        return "这个地区没有此活动"
    if local_state().completed.has(activity):
        return "本区活动已完成"
    if budget() < int(tables.activities[activity].ap_cost):
        return "剩余时段不足"
    if activity == "rest" and _party_full():
        return "全队已满生命"
    return ""

func _spend(activity: String) -> bool:
    var issue: String = activity_error(activity)
    if not issue.is_empty():
        return _reject(issue)
    if data.current != "castle":
        var cost: int = int(tables.activities[activity].ap_cost)
        local_state().ap = budget() - cost
        data.ap_spent[activity] = int(data.ap_spent.get(activity, 0)) + cost
        if int(tables.activities[activity].limit_per_region) == 1:
            local_state().completed.append(activity)
    data.serial = int(data.serial) + 1
    error_message = ""
    return true

func members(for_battle: bool = false) -> Array:
    var output: Array = []
    for member: Dictionary in data.party:
        var row: Dictionary = tables.units[str(member.id)].duplicate(true)
        var levels: int = int(data.level) - 1
        row.max_hp = int(row.hp) + int(row.hp_per_level) * levels
        row.atk = int(row.atk) + int(row.atk_per_level) * levels
        if int(row.armor_every_levels) > 0:
            row.armor = int(row.armor) + floori(float(levels) / float(row.armor_every_levels))
        if member.id == "hero":
            for slot: String in ["weapon", "armor", "charm"]:
                var item: Dictionary = find_item(str(data.equipped[slot]))
                for stat: String in item.get("stats", {}):
                    var field: String = "max_hp" if stat == "hp" else stat
                    row[field] = int(row.get(field, 0)) + int(item.stats[stat])
            var atk_bonus: float = 0.0
            if data.passive == "fury":
                atk_bonus += catalog.rule("fury_atk_pct")
                row.armor = int(row.armor) + int(catalog.rule("fury_armor"))
            elif data.passive == "resolve":
                row.armor = int(row.armor) + int(catalog.rule("resolve_armor"))
                row.speed = int(row.speed) + int(catalog.rule("resolve_speed"))
            if for_battle:
                atk_bonus += float(data.next_buff.get("next_hero_atk_pct", 0))
            row.atk = roundi(float(row.atk) * (1.0 + atk_bonus / 100.0))
        row.armor = maxi(0, int(row.armor))
        row.hp = mini(int(member.hp), int(row.max_hp))
        output.append(row)
    return output

func _party_full() -> bool:
    for member: Dictionary in members():
        if int(member.hp) < int(member.max_hp):
            return false
    return true

func _heal_party(percent: float, hero_only: bool = false) -> void:
    var current_members: Array = members()
    for i: int in range(current_members.size()):
        var member: Dictionary = current_members[i]
        if hero_only and member.id != "hero":
            continue
        data.party[i].hp = mini(int(member.max_hp), int(member.hp) + floori(float(member.max_hp) * percent / 100.0))

func rest() -> bool:
    if not _spend("rest"):
        return false
    _heal_party(catalog.rule("rest_heal_pct"))
    _record("营地休整：全队恢复50%最大生命。")
    return true

func recruit_candidates() -> Array:
    var owned: Array = data.party.map(func(member: Dictionary) -> String: return str(member.id))
    return local_state().get("candidates", []).filter(func(id_value: String) -> bool: return not owned.has(id_value)).slice(0, 2)

func recruit(id_value: String, replace_index: int = -1) -> bool:
    if not recruit_candidates().has(id_value):
        return _reject("候选已在队伍或不属于本区招募。")
    if data.party.size() >= int(catalog.rule("party_max")) and (replace_index < 0 or replace_index >= data.party.size() or data.party[replace_index].id == "hero"):
        return _reject("请选择要替换的随从，主角不能替换。")
    var ratio: float = 1.0
    for member: Dictionary in members():
        ratio = minf(ratio, float(member.hp) / float(member.max_hp))
    if not _spend("recruit"):
        return false
    var row: Dictionary = tables.units[id_value]
    var hp: int = int(row.hp) + int(row.hp_per_level) * (int(data.level) - 1)
    var incoming: Dictionary = {"id": id_value, "hp": maxi(1, floori(hp * ratio))}
    if data.party.size() >= int(catalog.rule("party_max")):
        data.party[replace_index] = incoming
    else:
        data.party.append(incoming)
    _record("%s 加入小队，生命按队伍最低比例继承。" % row.name)
    return true

func configure_tactics(active: String, passive: String, target: String, policy: String) -> bool:
    if not can_edit():
        return _reject("战斗与结算期间不能改战术。")
    if active not in ["guard", "burst", "fire"] or passive not in ["regen", "fury", "resolve"] or target not in ["front", "lowest", "marked"]:
        return _reject("战术配置无效。")
    if policy != "ready" and not (active == "guard" and policy == "threat") and not (active == "burst" and policy == "mark"):
        return _reject("此释放策略不适用于所选技能。")
    data.active = active
    data.passive = passive
    data.target = target
    data.policy = policy
    _clamp_health()
    _record("战术已更新。")
    return true

func swap_formation(index: int) -> bool:
    if not can_edit() or index < 0 or index >= data.party.size() - 1:
        return _reject("当前不能调整这个阵位。")
    var previous: Dictionary = data.party[index]
    data.party[index] = data.party[index + 1]
    data.party[index + 1] = previous
    _record("已交换相邻阵位。")
    return true

func find_item(item_id: String) -> Dictionary:
    for item: Dictionary in data.inventory:
        if str(item.id) == item_id:
            return item
    return {}

func equip(item_id: String) -> bool:
    if not can_edit():
        return _reject("先完成当前结算。")
    var item: Dictionary = find_item(item_id)
    if item.is_empty():
        return _reject("装备不存在。")
    data.equipped[str(item.slot)] = item_id
    _clamp_health()
    _record("装备了%s。" % item.name)
    return true

func _clamp_health() -> void:
    var current_members: Array = members()
    for i: int in range(current_members.size()):
        data.party[i].hp = int(current_members[i].hp)

func set_status() -> Dictionary:
    var counts: Dictionary = {}
    for slot: String in ["weapon", "armor", "charm"]:
        var family: String = str(find_item(str(data.equipped[slot])).get("set_id", ""))
        if not family.is_empty():
            counts[family] = int(counts.get(family, 0)) + 1
    for family: String in counts:
        if int(counts[family]) >= 2:
            return {"id": family, "count": int(counts[family]), "name": SET_NAMES[family]}
    return {"id": "", "count": 0, "name": "尚未成套"}

func _make_item(family: String, tier: int, key: String, forced_slot: String = "", quality: String = "") -> Dictionary:
    var generator: RandomNumberGenerator = _rng(key)
    var slots: Array = ["weapon", "armor", "charm"]
    var missing: Array = []
    if not family.is_empty():
        var acquired: Array = data.ledger.get(family, [])
        for slot: String in slots:
            if not acquired.has(slot):
                missing.append(slot)
    var pool: Array = missing if not missing.is_empty() else slots
    var slot: String = forced_slot if not forced_slot.is_empty() else str(pool[generator.randi_range(0, pool.size() - 1)])
    if quality.is_empty():
        quality = "fine" if generator.randf() < catalog.rule("boss_fine_chance_pct") / 100.0 else "normal"
    var affix_ids: Array = ["hardy", "sharp", "swift"]
    var affix_id: String = affix_ids[generator.randi_range(0, affix_ids.size() - 1)]
    var affix: Dictionary = tables.affixes[affix_id]
    var slot_data: Dictionary = tables.equipment[slot]
    var item_stats: Dictionary = {}
    for stat: String in ["hp", "atk", "armor", "speed"]:
        var value: float = float(slot_data["base_" + stat]) + float(slot_data[stat + "_per_tier"]) * (tier - 1)
        item_stats[stat] = roundi(value * (catalog.rule("fine_stat_mult") if quality == "fine" else 1.0))
    var affix_stat: String = "hp" if affix.stat == "max_hp" else str(affix.stat)
    item_stats[affix_stat] = int(item_stats[affix_stat]) + int(affix.value)
    return {"id": key, "name": "%s · %s" % [SET_NAMES.get(family, "行旅"), SLOT_NAMES[slot]],
        "set_id": family, "slot": slot, "tier": tier, "quality": quality, "affix": affix_id,
        "affix_name": affix.name, "stats": item_stats}

func open_chest() -> bool:
    if not _spend("chest"):
        return false
    var key: String = "chest/%s/%d" % [data.current, data.serial]
    data.pending = {"id": key, "item": _make_item("", int(region().stage), key, "", "normal"),
        "gold": int(catalog.rule("chest_gold")), "kind": "chest"}
    data.phase = "reward"
    return true

func merchant(choice: String) -> bool:
    if choice not in ["heal", "gear"]:
        return _reject("交易选项无效。")
    var price: int = int(catalog.rule("merchant_heal_gold" if choice == "heal" else "merchant_gear_gold"))
    if int(data.gold) < price:
        return _reject("金币不足，尚未扣除时段。")
    if choice == "heal" and _party_full():
        return _reject("全队已满生命。")
    if not _spend("merchant"):
        return false
    data.gold = int(data.gold) - price
    if choice == "heal":
        _heal_party(catalog.rule("merchant_heal_pct"))
        _record("购买补给，全队恢复80%最大生命。")
    else:
        data.pending = {"id": "shop/" + str(data.current), "item": local_state().merchant_item.duplicate(true),
            "gold": 0, "kind": "merchant"}
        data.phase = "reward"
    return true

func begin_event() -> bool:
    if not _spend("event"):
        return false
    data.phase = "event"
    return true

func event_definition() -> Dictionary:
    return tables.events.get(str(local_state().get("event_id", "")), {})

func event_choice_error(branch: String) -> String:
    if data.phase != "event" or branch not in ["a", "b"]:
        return "当前没有待选择事件"
    var outcome: String = str(event_definition()["outcome_" + branch])
    for command: String in outcome.split(";"):
        var pieces: PackedStringArray = command.split(":")
        var amount: float = float(pieces[1])
        if pieces[0] == "gold" and int(data.gold) + amount < 0:
            return "金币不足"
        if pieces[0] == "hero_hp_cost":
            for member: Dictionary in data.party:
                if member.id == "hero" and int(member.hp) <= amount:
                    return "主角生命不足以支付并存活"
    return ""

func choose_event(branch: String, slot: String = "weapon") -> bool:
    var issue: String = event_choice_error(branch)
    if not issue.is_empty():
        return _reject(issue)
    if slot not in ["weapon", "armor", "charm"]:
        return _reject("装备部位无效。")
    var event: Dictionary = event_definition()
    var item: Dictionary = {}
    var key: String = "event/%s/%d" % [data.current, data.serial]
    for command: String in str(event["outcome_" + branch]).split(";"):
        var parts: PackedStringArray = command.split(":")
        var amount: float = float(parts[1])
        match str(parts[0]):
            "gold":
                data.gold = int(data.gold) + int(amount)
            "hero_hp_cost":
                for member: Dictionary in data.party:
                    if member.id == "hero":
                        member.hp = int(member.hp) - int(amount)
            "party_heal_pct":
                _heal_party(amount)
            "hero_heal_pct":
                _heal_party(amount, true)
            "gear_choice_fine":
                item = local_state().forge_items[slot].duplicate(true)
            "gear_random_normal":
                item = _make_item("", int(region().stage), key, "", "normal")
            _:
                if str(parts[0]).begins_with("next_"):
                    data.next_buff = {str(parts[0]): amount}
    data.phase = "region"
    if not item.is_empty():
        data.pending = {"id": key, "item": item, "gold": 0, "kind": "event"}
        data.phase = "reward"
    _record("%s：选择%s。" % [event.name, event["option_" + branch]])
    return true

func preview_enemies(activity: String) -> Array:
    var current: Dictionary = region()
    var ids: Array = []
    var final_battle: bool = data.current == "castle"
    if final_battle:
        ids = ["king", "shadow"]
    elif activity == "dungeon":
        ids.append(str(current.family))
        if int(current.stage) == 2:
            ids.append("raider")
        elif int(current.stage) == 3:
            ids.append("acolyte" if current.family == "ember" else "stalker")
    else:
        ids = ["raider"] if int(current.stage) == 1 else (["raider", "stalker"] if int(current.stage) == 2 else ["stalker", "acolyte"])
    var enemies: Array = []
    for id_value: String in ids:
        var row: Dictionary = tables.units[id_value].duplicate(true)
        var hp_factor: float = float(current.hp_mult)
        var attack_factor: float = float(current.atk_mult)
        if row.kind == "boss" and not final_battle:
            var repeats: int = mini(int(catalog.rule("repeat_step_cap")), int(local_state().wins))
            hp_factor *= 1.0 + repeats * catalog.rule("repeat_hp_step_pct") / 100.0
            attack_factor *= 1.0 + repeats * catalog.rule("repeat_atk_step_pct") / 100.0
            row.name = current.boss_name
        hp_factor *= 1.0 + float(data.next_buff.get("next_enemy_hp_pct", 0)) / 100.0
        attack_factor *= 1.0 + float(data.next_buff.get("next_enemy_atk_pct", 0)) / 100.0
        row.max_hp = roundi(float(row.hp) * hp_factor)
        row.hp = row.max_hp
        row.atk = roundi(float(row.atk) * attack_factor)
        row.armor = maxi(0, int(row.armor) + int(data.next_buff.get("next_enemy_armor_flat", 0)))
        enemies.append(row)
    return enemies

func begin_battle(activity: String) -> bool:
    if activity not in ["dungeon", "patrol"]:
        return _reject("不是战斗活动。")
    var enemies: Array = preview_enemies(activity)
    var party: Array = members(true)
    var set_info: Dictionary = set_status()
    var options: Dictionary = {"active": data.active, "passive": data.passive, "policy": data.policy,
        "target": data.target, "set_id": set_info.id, "set_count": set_info.count,
        "opening_shield": int(data.next_buff.get("next_hero_shield", 0))}
    if not _spend(activity):
        return false
    var key: String = "battle/%s/%d" % [data.current, data.serial]
    var fight: FogCombat = Combat.new()
    var report: Dictionary = fight.simulate(party, enemies, options, catalog)
    var item: Dictionary = {}
    var gold: int = 0
    if report.outcome == "victory" and data.current != "castle":
        if activity == "dungeon":
            item = _make_item(str(region().family), int(region().stage), key)
        else:
            gold = int(catalog.rule("patrol_gold"))
    data.next_buff = {}
    data.battle = {"id": key, "activity": activity, "report": report, "index": 0, "paused": false,
        "speed": 1, "item": item, "gold": gold}
    data.phase = "battle"
    _record("小队开始%s。" % ("最终战" if data.current == "castle" else tables.activities[activity].name))
    return true

func advance_battle(skip: bool = false) -> bool:
    if data.phase != "battle":
        return _reject("没有进行中的战斗。")
    var last: int = data.battle.report.frames.size() - 1
    data.battle.index = last if skip else mini(last, int(data.battle.index) + 1)
    if int(data.battle.index) >= last:
        data.pending = {"id": data.battle.id, "kind": "battle", "item": data.battle.item,
            "gold": data.battle.gold}
        data.phase = "reward"
    return true

func battle_frame() -> Dictionary:
    if data.get("battle", {}).is_empty():
        return {}
    return data.battle.report.frames[int(data.battle.index)]

func claim_reward(equip_now: bool = false) -> bool:
    if data.phase != "reward" or data.pending.is_empty():
        return _reject("没有待领取奖励。")
    var pending: Dictionary = data.pending.duplicate(true)
    if data.claimed.has(pending.id):
        return _reject("这个结算已经领取。")
    if pending.kind == "battle":
        var report: Dictionary = data.battle.report
        data.last_report = {"outcome": report.outcome, "rounds": report.rounds,
            "stats": report.stats.duplicate(true), "first_fall": report.first_fall}
        for member: Dictionary in data.party:
            for unit: Dictionary in report.units:
                if unit.side == "ally" and unit.id == member.id:
                    member.hp = int(unit.hp)
        if report.outcome == "defeat":
            data.phase = "ended"
            data.outcome = "defeat"
        else:
            for member: Dictionary in data.party:
                for unit: Dictionary in report.units:
                    if unit.side == "ally" and unit.id == member.id:
                        member.hp = maxi(1, int(unit.hp))
            if data.current == "castle":
                data.phase = "ended"
                data.outcome = "victory"
            else:
                if not bool(local_state().leveled):
                    local_state().leveled = true
                    data.level = mini(int(catalog.rule("level_cap")), int(data.level) + 1)
                    _record("本区首次战斗胜利，小队升至%d级；生命上限增加，不自动回血。" % data.level)
                if data.battle.activity == "dungeon":
                    local_state().wins = int(local_state().wins) + 1
                data.phase = "region"
    else:
        data.phase = "region"
    data.gold = int(data.gold) + int(pending.get("gold", 0))
    var item: Dictionary = pending.get("item", {})
    if not item.is_empty():
        data.inventory.append(item)
        var family: String = str(item.set_id)
        if not family.is_empty():
            if not data.ledger.has(family):
                data.ledger[family] = []
            if not data.ledger[family].has(item.slot):
                data.ledger[family].append(item.slot)
        if equip_now and data.phase == "region":
            data.equipped[str(item.slot)] = str(item.id)
        _record("获得%s，%s。" % [item.name, "已装备" if equip_now else "已收入背包"])
    data.claimed.append(pending.id)
    data.pending = {}
    _clamp_health()
    error_message = ""
    return true

func item_description(item: Dictionary) -> String:
    if item.is_empty():
        return "空"
    var attributes: PackedStringArray = []
    var names: Dictionary = {"hp": "生命", "atk": "攻击", "armor": "护甲", "speed": "速度"}
    for stat: String in ["hp", "atk", "armor", "speed"]:
        if int(item.stats.get(stat, 0)) != 0:
            attributes.append("%s +%d" % [names[stat], item.stats[stat]])
    return "%s  ·  %s T%d\n%s\n词条：%s" % [item.name, "精良" if item.quality == "fine" else "普通",
        item.tier, " / ".join(attributes), item.affix_name]
