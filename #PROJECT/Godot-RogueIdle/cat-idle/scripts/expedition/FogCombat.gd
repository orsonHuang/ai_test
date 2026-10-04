@tool
class_name FogCombat
extends RefCounted

var catalog: FogCatalog
var skill_rows: Dictionary = {}
var rules: Dictionary = {}
var units: Array = []
var frames: Array = []
var stats: Dictionary = {}
var round_number: int = 0
var serial: int = 0
var options: Dictionary = {}
var result: String = ""
var first_fall: String = ""

func simulate(party: Array, enemies: Array, config: Dictionary, source: FogCatalog) -> Dictionary:
    catalog = source
    rules = catalog.rules
    skill_rows = catalog.table("skills")
    units = party.duplicate(true)
    units.append_array(enemies.duplicate(true))
    frames = []
    stats = {}
    options = config.duplicate(true)
    result = ""
    first_fall = ""
    serial = 0
    round_number = 0
    for index: int in range(units.size()):
        var unit: Dictionary = units[index]
        unit["uid"] = index
        unit["shield"] = 0
        unit["cd"] = 0
        unit["burn"] = 0
        unit["burn_ticks"] = 0
        unit["burn_source"] = -1
        unit["mark"] = 0
        unit["aim"] = -1
        unit["waited"] = false
        unit["counter_round"] = 0
        unit["chase_round"] = 0
        unit["burn_healed"] = 0
        unit["base_atk"] = int(unit.atk)
        stats[str(index)] = {"name": unit.name, "direct": 0, "counter": 0, "chase": 0,
            "burn": 0, "healing": 0, "absorbed": 0}
    var opening_shield: int = int(options.get("opening_shield", 0))
    if opening_shield > 0:
        _shield(_hero(), opening_shield)
    for next_round: int in range(1, int(rules.battle_round_cap) + 1):
        round_number = next_round
        for unit: Dictionary in units:
            unit.burn_healed = 0
            if unit.side == "enemy":
                var pressure: int = maxi(0, round_number - int(rules.enrage_start_round) + 1)
                unit.atk = roundi(float(unit.base_atk) * (1.0 + pressure * float(rules.enrage_atk_step_pct) / 100.0))
            unit["intent"] = _intent(unit)
        _frame("第 %d 回合  ·  %s" % [round_number, _enemy_intents()], -1, "round")
        var queue: Array = units.filter(func(u: Dictionary) -> bool: return int(u.hp) > 0)
        queue.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
            return int(a.speed) > int(b.speed) if int(a.speed) != int(b.speed) else int(a.uid) < int(b.uid))
        for unit: Dictionary in queue:
            if int(unit.hp) <= 0:
                continue
            _burn_tick(unit)
            if _ended():
                break
            if int(unit.hp) <= 0:
                continue
            if unit.id == "hero" and options.get("passive") == "regen":
                _heal(unit, unit, int(rules.regen_heal))
            var ready: bool = int(unit.cd) == 0
            if not ready:
                unit.cd = int(unit.cd) - 1
            if unit.side == "ally":
                _ally_turn(unit, ready)
            else:
                _enemy_turn(unit)
            unit.mark = maxi(0, int(unit.mark) - 1)
            if _ended():
                break
        if not result.is_empty():
            break
    if result.is_empty():
        result = "defeat"
        _frame("战线崩溃：达到回合上限。", -1, "result")
    else:
        _frame("战斗胜利" if result == "victory" else "小队全灭", -1, "result")
    return {"outcome": result, "units": units.duplicate(true), "frames": frames,
        "stats": stats.duplicate(true), "rounds": round_number, "first_fall": first_fall}

func _hero() -> Dictionary:
    for unit: Dictionary in units:
        if unit.id == "hero":
            return unit
    return {}

func _alive(side: String) -> Array:
    return units.filter(func(unit: Dictionary) -> bool: return unit.side == side and int(unit.hp) > 0)

func _target(side: String, mode: String = "front") -> Dictionary:
    var candidates: Array = _alive(side)
    if candidates.is_empty():
        return {}
    if mode == "rear":
        return candidates.back()
    if mode == "lowest":
        candidates.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
            var av: float = float(a.hp) / float(a.max_hp)
            var bv: float = float(b.hp) / float(b.max_hp)
            return av < bv if not is_equal_approx(av, bv) else int(a.uid) < int(b.uid))
    elif mode == "marked":
        for candidate: Dictionary in candidates:
            if int(candidate.mark) > 0:
                return candidate
    return candidates.front()

func _ally_turn(unit: Dictionary, ready: bool) -> void:
    var target: Dictionary = _target("enemy", str(options.get("target", "front")))
    if target.is_empty():
        return
    var skill_id: String = ""
    if unit.id == "hero":
        skill_id = str(options.get("active", "guard"))
        var policy: String = str(options.get("policy", "ready"))
        if ready and skill_id == "guard" and policy == "threat":
            ready = _pending_threat(int(unit.uid))
            if not ready:
                _frame("远征者保留坚守，等待已预告的重击。", int(unit.uid), "policy")
        if ready and skill_id == "burst" and policy == "mark":
            if int(target.mark) == 0 and not bool(unit.waited):
                unit.waited = true
                ready = false
                _frame("远征者保留破势，等待一次标记。", int(unit.uid), "policy")
    elif unit.id == "priest":
        skill_id = "mend"
        var patient: Dictionary = _target("ally", "lowest")
        if ready and float(patient.hp) / float(patient.max_hp) < float(rules.priest_heal_threshold_pct) / 100.0:
            var heal_skill: Dictionary = skill_rows[skill_id]
            _heal(unit, patient, int(heal_skill.heal))
            unit.cd = int(heal_skill.cooldown_actions)
            return
        ready = false
    elif unit.id == "ranger":
        skill_id = "mark_shot"
    elif unit.id == "guardian":
        skill_id = "protect"
    if not ready or skill_id.is_empty():
        _hit(unit, target, 1.0, "direct", true)
        unit["acted_round"] = round_number
        return
    var skill: Dictionary = skill_rows[skill_id]
    unit.cd = int(skill.cooldown_actions)
    unit.waited = false
    if skill_id == "guard":
        _shield(unit, int(skill.shield))
    elif skill_id == "protect":
        _shield(_target("ally"), int(skill.shield))
        target = _target("enemy")
    elif skill_id == "mark_shot":
        target.mark = int(rules.mark_target_actions)
        _frame("%s 标记了 %s" % [unit.name, target.name], int(unit.uid), "mark")
    _hit(unit, target, float(skill.attack_coeff), "direct", true)
    if skill_id == "fire" and int(target.hp) > 0:
        _apply_burn(unit, target, int(skill.burn_stacks))
    unit["acted_round"] = round_number

func _enemy_turn(unit: Dictionary) -> void:
    unit["acted_round"] = round_number
    var phase: int = (round_number - 1) % 3
    var id: String = str(unit.id)
    var target: Dictionary = _target("ally")
    if target.is_empty():
        return
    if id == "thorn":
        if phase == 1:
            _frame("%s 蓄力：下一回合重击前排。" % unit.name, int(unit.uid), "charge")
            return
        _hit(unit, target, 2.0 if phase == 2 else 1.0, "direct")
    elif id == "storm":
        if phase == 1:
            unit.aim = int(_target("ally", "rear").uid)
            _frame("%s 瞄准 %s" % [unit.name, units[int(unit.aim)].name], int(unit.uid), "charge")
            return
        target = _target("ally", "rear")
        if phase == 2 and int(unit.aim) >= 0 and int(units[int(unit.aim)].hp) > 0:
            target = units[int(unit.aim)]
        _hit(unit, target, 1.8 if phase == 2 else 1.0, "direct")
        if phase == 2:
            unit.aim = -1
    elif id == "ember" or id == "king":
        if phase == 1:
            _frame("%s 蓄力：下一回合攻击全队。" % unit.name, int(unit.uid), "charge")
            return
        if phase == 2:
            for ally: Dictionary in _alive("ally"):
                var coeff: float = 1.3 if id == "king" else (1.04 if int(ally.burn) > 0 else 0.8)
                _hit(unit, ally, coeff, "direct")
        else:
            _hit(unit, target, 1.0 if id == "king" else 0.8, "direct")
            if id == "ember" and int(target.hp) > 0:
                _apply_burn(unit, target, 1)
    elif id == "stalker" or id == "shadow":
        _hit(unit, _target("ally", "rear"), 1.0, "direct")
    elif id == "acolyte" and phase == 2:
        target = _target("ally", "lowest")
        _hit(unit, target, 0.8, "direct")
        if int(target.hp) > 0:
            _apply_burn(unit, target, 1)
    else:
        _hit(unit, target, 1.0, "direct")

func _hit(attacker: Dictionary, target: Dictionary, coeff: float, kind: String, primary: bool = false) -> void:
    if attacker.is_empty() or target.is_empty() or int(attacker.hp) <= 0 or int(target.hp) <= 0:
        return
    var bonus: float = 1.0
    var set_id: String = str(options.get("set_id", ""))
    var pieces: int = int(options.get("set_count", 0))
    if attacker.id == "hero" and primary and set_id == "storm" and pieces >= 2 and int(target.mark) > 0:
        bonus += _set_value("storm", 2) / 100.0
    var defense: int = maxi(0, int(target.armor) - (int(rules.mark_armor_reduction) if int(target.mark) > 0 else 0))
    var damage: int = maxi(1, roundi(float(attacker.atk) * coeff * bonus - defense))
    var absorbed: int = mini(int(target.shield), damage)
    target.shield = int(target.shield) - absorbed
    stats[str(target.uid)].absorbed += absorbed
    var loss: int = mini(int(target.hp), damage - absorbed)
    target.hp = int(target.hp) - loss
    stats[str(attacker.uid)][kind] += loss
    var tag: String = {"direct": "攻击", "counter": "反击", "chase": "追击"}.get(kind, kind)
    _frame("%s %s %s：%d伤害%s" % [attacker.name, tag, target.name, loss,
        " · 护盾吸收%d" % absorbed if absorbed > 0 else ""], int(attacker.uid), kind)
    if int(target.hp) <= 0:
        if first_fall.is_empty() and target.side == "ally":
            first_fall = "%s 被 %s 的%s击倒" % [target.name, attacker.name, tag]
        _frame("%s 倒下了" % target.name, int(target.uid), "down")
    if target.id == "hero" and int(target.hp) > 0 and kind == "direct" and attacker.side == "enemy":
        if set_id == "thorn" and pieces >= 2 and int(target.counter_round) != round_number:
            target.counter_round = round_number
            _hit(target, attacker, _set_value("thorn", 2), "counter")
            if pieces >= 3:
                _shield(target, int(_set_value("thorn", 3)))
    if attacker.id == "hero" and primary and int(target.hp) > 0:
        if set_id == "storm" and pieces >= 3 and int(target.mark) > 0 and int(attacker.chase_round) != round_number:
            attacker.chase_round = round_number
            _hit(attacker, target, _set_value("storm", 3), "chase")
        elif set_id == "ember" and pieces >= 2:
            _apply_burn(attacker, target, int(_set_value("ember", 2)))

func _set_value(set_id: String, pieces: int) -> float:
    return float(catalog.table("sets").get("%s_%d" % [set_id, pieces], {}).get("value", 0.0))

func _apply_burn(source: Dictionary, target: Dictionary, count: int) -> void:
    target.burn = mini(int(rules.burn_stack_cap), int(target.burn) + count)
    target.burn_ticks = int(rules.burn_ticks)
    target.burn_source = int(source.uid)
    _frame("%s 燃烧 %d层 · 剩余%d跳" % [target.name, target.burn, target.burn_ticks], int(source.uid), "status")

func _burn_tick(unit: Dictionary) -> void:
    if int(unit.burn_ticks) <= 0 or int(unit.burn) <= 0:
        return
    var damage: int = mini(int(unit.hp), int(unit.burn) * int(rules.burn_damage_per_stack))
    unit.hp = int(unit.hp) - damage
    unit.burn_ticks = int(unit.burn_ticks) - 1
    var source_id: int = int(unit.burn_source)
    if source_id >= 0:
        stats[str(source_id)].burn += damage
    _frame("%s 受到%d灼烧伤害" % [unit.name, damage], int(unit.uid), "burn")
    if int(unit.hp) <= 0 and first_fall.is_empty() and unit.side == "ally":
        first_fall = "%s 被灼烧击倒" % unit.name
    var hero: Dictionary = _hero()
    if source_id == int(hero.get("uid", -2)) and int(hero.get("hp", 0)) > 0:
        if options.get("set_id") == "ember" and int(options.get("set_count", 0)) >= 3:
            var cap: int = int(catalog.table("sets").ember_3.heal_cap_per_round)
            var healing: int = mini(int(_set_value("ember", 3)), maxi(0, cap - int(hero.burn_healed)))
            hero.burn_healed = int(hero.burn_healed) + healing
            _heal(hero, hero, healing)
    if int(unit.burn_ticks) <= 0:
        unit.burn = 0

func _heal(source: Dictionary, target: Dictionary, amount: int) -> void:
    if int(target.hp) <= 0:
        return
    var actual: int = mini(amount, int(target.max_hp) - int(target.hp))
    if actual <= 0:
        return
    target.hp = int(target.hp) + actual
    stats[str(source.uid)].healing += actual
    _frame("%s 治疗 %s +%d" % [source.name, target.name, actual], int(source.uid), "heal")

func _shield(target: Dictionary, amount: int) -> void:
    if target.is_empty() or int(target.hp) <= 0:
        return
    var cap: int = floori(float(target.max_hp) * float(rules.shield_max_hp_pct) / 100.0)
    var actual: int = mini(amount, maxi(0, cap - int(target.get("shield", 0))))
    target.shield = int(target.get("shield", 0)) + actual
    if actual > 0:
        _frame("%s 获得%d护盾" % [target.name, actual], int(target.uid), "shield")

func _pending_threat(hero_id: int) -> bool:
    if round_number % 3 != 0:
        return false
    for enemy: Dictionary in _alive("enemy"):
        if int(enemy.get("acted_round", 0)) == round_number:
            continue
        if enemy.id == "king" or enemy.id == "ember":
            return true
        if enemy.id == "thorn" and int(_target("ally").uid) == hero_id:
            return true
        if enemy.id == "storm" and int(enemy.aim) == hero_id:
            return true
    return false

func _intent(unit: Dictionary) -> String:
    if unit.side == "ally":
        return "按战前策略行动"
    var phase: int = (round_number - 1) % 3
    if unit.id == "thorn":
        return ["攻击前排", "蓄力 → 前排重击", "重击前排 ×2"][phase]
    if unit.id == "storm":
        return ["攻击后排", "瞄准后排", "瞄准射击 ×1.8"][phase]
    if unit.id == "ember":
        return ["前排附灼烧", "蓄力 → 烈焰", "全队烈焰"][phase]
    if unit.id == "king":
        return ["攻击前排", "蓄力 → 横扫", "全队横扫 ×1.3"][phase]
    if unit.id == "stalker" or unit.id == "shadow":
        return "袭击后排"
    return "附灼烧" if unit.id == "acolyte" and phase == 2 else "攻击前排"

func _enemy_intents() -> String:
    var labels: PackedStringArray = []
    for unit: Dictionary in _alive("enemy"):
        labels.append("%s：%s" % [unit.name, unit.intent])
    return " / ".join(labels)

func _ended() -> bool:
    if _alive("ally").is_empty():
        result = "defeat"
    elif _alive("enemy").is_empty():
        result = "victory"
    return not result.is_empty()

func _frame(text: String, actor: int, kind: String) -> void:
    serial += 1
    frames.append({"index": serial, "round": round_number, "text": text, "actor": actor,
        "kind": kind, "units": units.duplicate(true)})
