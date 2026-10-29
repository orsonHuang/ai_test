extends RefCounted
const SKILLS: Array = [
    {"id":"ignite","name":"点燃","cost":1,"damage":4,"desc":"单体攻击，附加 1 层燃烧。"},
    {"id":"wall","name":"火墙","cost":1,"damage":3,"desc":"攻击所有存活敌人，各附加 1 层燃烧。"},
    {"id":"double","name":"爆燃","cost":1,"damage":4,"desc":"攻击燃烧最多的敌人，令其燃烧翻倍。"},
    {"id":"spread","name":"火星","cost":1,"damage":2,"desc":"攻击一个目标，将它的燃烧层数复制叠加到其他存活敌人。源目标保留层数。"},
    {"id":"funeral","name":"火葬","cost":2,"damage":3,"desc":"攻击全体，所有敌人的燃烧层数翻倍。"},
    {"id":"burst","name":"炎爆","cost":1,"damage":4,"desc":"单体增加 2 层燃烧，立即引爆且保留层数；技能仍消耗 1 AP。"},
    {"id":"inferno","name":"炼狱","cost":2,"damage":0,"desc":"全体增加 1 层燃烧，立即引爆且保留层数；无额外直伤，技能消耗 2 AP。"}
]
const PASSIVES: Array = [
    {"id":"shield","name":"炎盾","desc":"受到攻击前：减伤 50%，攻击者 +1 层燃烧。","timing":"受击前"},
    {"id":"mana","name":"魔力恢复","desc":"下个法术 AP 不足时：恢复 1 AP。每轮最多一次。","timing":"AP 不足时"},
    {"id":"charge","name":"蓄能","desc":"本轮首次施法前：下一次行动新增的燃烧层数翻倍，之后消耗蓄能。","timing":"首次施法前"}
]
const ENEMY_NAMES: Array = ["灰烬刺球","鹿面巡守","枯枝稻人"]
var events: Array = []
var state: Dictionary = {}
var cfg: Resource
var total_damage: int = 0
var peak_burn: int = 0
var current_slot: int = -1

static func default_plan() -> Array:
    var result: Array = []
    for id in ["wall","double","spread","funeral","inferno","burst","ignite"]:
        result.append({"id":id,"enabled":true,"condition":0,"target":0})
    return result

static func default_passives() -> Array:
    return [{"id":"charge","enabled":true,"condition":0},{"id":"mana","enabled":true,"condition":0},{"id":"shield","enabled":true,"condition":0}]

static func skill(id: String) -> Dictionary:
    for item in SKILLS:
        if item.id == id:
            return item
    return {}

func alive() -> Array:
    var result: Array = []
    for i in range(3):
        if state.enemies[i].hp > 0:
            result.append(i)
    return result

func record(kind: String, text: String, target: int = -2, amount: int = 0, id: String = "") -> void:
    events.append({"kind":kind,"text":text,"target":target,"amount":amount,"skill":id,"slot":current_slot,"state":state.duplicate(true)})

func add_burn(index: int, count: int, id: String) -> void:
    if state.enemies[index].hp <= 0 or count <= 0:
        return
    state.enemies[index].burn += count
    peak_burn = maxi(peak_burn, state.enemies[index].burn)
    record("burn", "%s +%d 燃烧 → %d 层" % [ENEMY_NAMES[index],count,state.enemies[index].burn], index, count, id)

func hit(index: int, damage: int, id: String, kind: String = "hit") -> void:
    if state.enemies[index].hp <= 0:
        return
    var actual: int = mini(damage, state.enemies[index].hp)
    state.enemies[index].hp -= actual
    total_damage += actual
    record(kind, "%s 受到 %d 伤害%s" % [ENEMY_NAMES[index],damage," · 击败" if state.enemies[index].hp == 0 else ""], index, damage, id)
    if state.enemies[index].hp == 0:
        state.enemies[index].burn = 0
        record("death", "%s 化作灰烬" % ENEMY_NAMES[index], index, 0, id)

func detonate(index: int, clear: bool, id: String) -> void:
    var stacks: int = state.enemies[index].burn
    if stacks <= 0 or state.enemies[index].hp <= 0:
        return
    if clear:
        state.enemies[index].burn = 0
    record("detonate", "%d 层 × %d = %d · %s" % [stacks,cfg.burn_damage,stacks*cfg.burn_damage,"清空燃烧" if clear else "保留燃烧"], index, stacks*cfg.burn_damage, id)
    hit(index, stacks*cfg.burn_damage, id, "blast")

func target_for(rule: Dictionary) -> int:
    var candidates: Array = alive()
    if int(rule.get("condition",0)) == 1:
        candidates = candidates.filter(func(i: int) -> bool: return state.enemies[i].burn > 0)
    elif int(rule.get("condition",0)) == 2:
        candidates = candidates.filter(func(i: int) -> bool: return state.enemies[i].burn >= 4)
    elif int(rule.get("condition",0)) == 3 and float(state.hp)/cfg.hero_health >= 0.5:
        return -1
    if candidates.is_empty():
        return -1
    var best: int = candidates[0]
    for index in candidates:
        if rule.id == "double" or int(rule.get("target",0)) == 0:
            if state.enemies[index].burn > state.enemies[best].burn:
                best = index
        elif int(rule.get("target",0)) == 1 and state.enemies[index].hp < state.enemies[best].hp:
            best = index
    return best

func passive_ok(rule: Dictionary) -> bool:
    var condition: int = int(rule.get("condition",0))
    return condition == 0 or (condition == 1 and float(state.hp)/cfg.hero_health < 0.5) or (condition == 2 and state.rp >= 2)

func reaction(id: String, passives: Array, attacker: int = -1) -> bool:
    for rule in passives:
        if rule.id != id or not rule.enabled:
            continue
        if state.rp < 1 or not passive_ok(rule):
            record("skip","%s：反应点或附加条件不满足" % id,-2,0,id)
            return false
        state.rp -= 1
        match id:
            "charge":
                state.charge = true
                record("charge","蓄能 · 下一次行动新增燃烧 ×2",-1,0,id)
            "mana":
                state.ap += 1
                record("mana","魔力恢复 · AP +1",-1,1,id)
            "shield":
                record("shield","炎盾 · 本次减伤 50%",-1,0,id)
                add_burn(attacker,1,id)
        return true
    return false

func cast(rule: Dictionary) -> void:
    var definition: Dictionary = skill(rule.id)
    var selected: int = target_for(rule)
    var targets: Array = alive() if rule.id in ["wall","funeral","inferno"] else [selected]
    var factor: int = 2 if state.charge else 1
    state.charge = false
    state.ap -= definition.cost
    # Snapshot spread source before direct damage (even if that damage defeats source).
    var source_stacks: int = state.enemies[selected].burn
    record("cast","%s · -%d AP%s" % [definition.name,definition.cost," · 蓄能生效" if factor == 2 else ""],selected,0,rule.id)
    for index in targets:
        if definition.damage > 0:
            hit(index,definition.damage,rule.id)
        match rule.id:
            "ignite","wall","inferno":
                add_burn(index,factor,rule.id)
            "burst":
                add_burn(index,2*factor,rule.id)
            "double","funeral":
                add_burn(index,state.enemies[index].burn*factor,rule.id)
    if rule.id == "spread":
        for index in alive():
            if index != selected:
                add_burn(index,source_stacks*factor,rule.id)
    if rule.id in ["burst","inferno"]:
        for index in targets:
            detonate(index,false,rule.id)

func simulate(plan: Array, passives: Array, config: Resource) -> Array:
    cfg = config
    events = []
    total_damage = 0
    peak_burn = 0
    current_slot = -1
    state = {"hp":cfg.hero_health,"ap":0,"rp":0,"round":0,"charge":false,"enemies":[]}
    for i in range(3):
        state.enemies.append({"hp":cfg.enemy_health[i],"max_hp":cfg.enemy_health[i],"burn":0})
    record("ready","战前规则已锁定")
    for round_index in range(1,cfg.max_rounds+1):
        state.round = round_index
        state.ap = cfg.action_points
        state.rp = cfg.reaction_points
        state.charge = false
        record("round","第 %d 回合 · AP / RP 恢复" % round_index)
        var mana_used: bool = false
        var cast_started: bool = false
        for slot in range(plan.size()):
            current_slot = slot
            var rule: Dictionary = plan[slot]
            if not rule.enabled or alive().is_empty():
                continue
            if target_for(rule) == -1:
                record("skip","%s：没有满足条件的目标" % skill(rule.id).name,-2,0,rule.id)
                continue
            if state.ap < skill(rule.id).cost and not mana_used:
                mana_used = reaction("mana",passives)
            if state.ap < skill(rule.id).cost:
                record("skip","%s：AP 不足" % skill(rule.id).name,-2,0,rule.id)
                continue
            if not cast_started:
                reaction("charge",passives)
                cast_started = true
            cast(rule)
        current_slot = -1
        if alive().is_empty():
            break
        for index in alive():
            record("enemy","%s 准备普通攻击 · %d" % [ENEMY_NAMES[index],cfg.enemy_damage[index]],index)
            var blocked: bool = reaction("shield",passives,index)
            var damage: int = int(ceil(cfg.enemy_damage[index]*(1.0-cfg.shield_reduction))) if blocked else cfg.enemy_damage[index]
            state.hp = maxi(0,state.hp-damage)
            record("hurt","法师 -%d 生命%s" % [damage," · 炎盾减伤" if blocked else ""],-1,damage)
            if state.hp == 0:
                break
        if state.hp == 0:
            break
        record("end_round","回合结束 · 燃烧依次引爆并清空")
        for index in alive():
            detonate(index,true,"round_end")
        if alive().is_empty():
            break
    var victory: bool = alive().is_empty() and state.hp > 0
    record("result","胜利 · 核爆完成" if victory else ("失败 · 法师倒下" if state.hp == 0 else "失败 · 超过回合上限"))
    events[-1]["victory"] = victory
    events[-1]["total_damage"] = total_damage
    events[-1]["peak_burn"] = peak_burn
    return events
