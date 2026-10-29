extends RefCounted

const SKILLS: Array = [
    {"id":"ignite","name":"点燃","cost":1,"damage":4,"icon":0,"desc":"对单体造成 4 伤害，附加 1 层燃烧。"},
    {"id":"wall","name":"火墙","cost":1,"damage":3,"icon":1,"desc":"对全体造成 3 伤害，各附加 1 层燃烧。"},
    {"id":"double","name":"爆燃","cost":1,"damage":4,"icon":2,"desc":"对燃烧最多的敌人造成 4 伤害，使其燃烧层数翻倍。"},
    {"id":"spread","name":"火星","cost":1,"damage":2,"icon":3,"desc":"对单体造成 2 伤害，将其燃烧层数复制给其他敌人。"},
    {"id":"funeral","name":"火葬","cost":2,"damage":3,"icon":4,"desc":"对全体造成 3 伤害，使所有敌人的燃烧层数翻倍。"},
    {"id":"burst","name":"炎爆","cost":1,"damage":4,"icon":5,"desc":"单体附加 2 层燃烧，造成 4 伤害并引爆，保留层数。击杀时将燃烧转移给下个敌人。"},
    {"id":"inferno","name":"炼狱","cost":2,"damage":0,"icon":6,"desc":"全体附加 1 层燃烧并引爆，保留层数。"}
]
const PASSIVES: Array = [
    {"id":"shield","name":"炎盾","cost":1,"icon":7,"timing":"受击前","desc":"受击前减伤 50%，攻击者附加 1 层燃烧。"},
    {"id":"mana","name":"魔力恢复","cost":1,"icon":8,"timing":"AP 不足时","desc":"施法点数不足时恢复 1 AP，每回合一次。"},
    {"id":"charge","name":"蓄能","cost":1,"icon":9,"timing":"首次施法前","desc":"本回合首次施法前，使下一行动新增的燃烧层数翻倍。"}
]
const ENEMIES: Array = [
    {"name":"灰烬刺球","attack":"棘刺冲撞","icon":10,"ap":1,"rp":0,"passive":""},
    {"name":"鹿面巡守","attack":"枯枝爪击","icon":11,"ap":1,"rp":1,"passive":"枯木护身"},
    {"name":"枯枝稻人","attack":"横扫","icon":12,"ap":1,"rp":0,"passive":""}
]
const CONDITIONS: Array = ["总是","目标已有燃烧","目标燃烧 ≥ 4","自身生命 < 50%"]
const TARGETS: Array = ["标记目标优先","燃烧最多","生命值最低","最前方敌人"]
var cfg: Resource
var state: Dictionary = {}
var events: Array = []
var slot: int = -1
var preferred_target: int = -1
var total_damage: int = 0
var peak_burn: int = 0

static func skill(id: String) -> Dictionary:
    for definition in SKILLS + PASSIVES:
        if definition.id == id:
            return definition
    return {}

static func is_passive(id: String) -> bool:
    return id in ["shield","mana","charge"]

static func rule(id: String) -> Dictionary:
    return {"id":id,"enabled":true,"condition":0,"target":0}

static func default_plan() -> Array:
    return [rule("wall"),rule("double"),rule("spread"),rule("burst")]

static func default_passives() -> Array:
    return [rule("charge"),rule("shield")]

func initialize(config: Resource, marked: int = -1) -> void:
    cfg = config
    preferred_target = marked
    events.clear()
    slot = -1
    total_damage = 0
    peak_burn = 0
    state = {"hp":cfg.hero_health,"ap":cfg.action_points,"rp":cfg.reaction_points,"round":0,"charge":false,"actor":-1,"timeline":[0.84,0.61,0.38,0.16],"done":[false,false,false,false],"enemies":[]}
    for i in range(3):
        state.enemies.append({"hp":cfg.enemy_health[i],"max_hp":cfg.enemy_health[i],"burn":0,"ap":ENEMIES[i].ap,"rp":ENEMIES[i].rp})

func record(kind: String, text: String = "", target: int = -1, amount: int = 0, id: String = "", actor: int = -2) -> void:
    events.append({"kind":kind,"text":text,"target":target,"amount":amount,"skill":id,"slot":slot,"actor":state.actor if actor == -2 else actor,"state":state.duplicate(true)})

func alive() -> Array:
    var result: Array = []
    for i in range(3):
        if state.enemies[i].hp > 0:
            result.append(i)
    return result

func actor_alive(actor: int) -> bool:
    return state.hp > 0 if actor == 0 else state.enemies[actor-1].hp > 0

func begin_turn(actor: int) -> void:
    var advance: float = 1.0-float(state.timeline[actor])
    for i in range(4):
        if actor_alive(i):
            state.timeline[i] = clampf(state.timeline[i]+advance,0.0,1.0)
    state.actor = actor
    record("turn","烬火法师" if actor == 0 else ENEMIES[actor-1].name,-1,0,"",actor)

func end_turn(actor: int) -> void:
    var remaining: int = state.ap if actor == 0 else state.enemies[actor-1].ap
    if actor == 0:
        state.ap = 0
    else:
        state.enemies[actor-1].ap = 0
    if remaining > 0:
        record("wait","无可执行技能 · 放弃剩余 %d AP" % remaining,-1,remaining,"",actor)
    state.done[actor] = true
    state.timeline[actor] = 0.0
    state.actor = -1
    record("turn_end","",-1,0,"",actor)

func shift_initiative(actor: int, position: float) -> void:
    if actor < 0 or actor >= 4 or not actor_alive(actor):
        return
    state.timeline[actor] = clampf(position,0.0,1.0)
    record("timeline_shift","行动位置改变",-1,0,"",actor)

func next_actor(pending: Array) -> int:
    var best: int = -1
    for actor in pending:
        if actor_alive(actor) and not state.done[actor] and (best < 0 or state.timeline[actor] > state.timeline[best]):
            best = actor
    return best

func add_burn(index: int, count: int, id: String) -> void:
    if index < 0 or count <= 0 or state.enemies[index].hp <= 0:
        return
    state.enemies[index].burn += count
    peak_burn = maxi(peak_burn,state.enemies[index].burn)
    record("burn","燃烧",index,count,id,index+1)

func hit(index: int, damage: int, id: String, kind: String = "hit") -> void:
    if state.enemies[index].hp <= 0 or damage <= 0:
        return
    if kind == "hit" and index == 1 and state.enemies[index].rp > 0:
        state.enemies[index].rp -= 1
        damage = int(ceil(damage*0.5))
        record("enemy_guard","枯木护身",index,0,"guard",index+1)
    var actual: int = mini(damage,state.enemies[index].hp)
    state.enemies[index].hp -= actual
    total_damage += actual
    record(kind,"",index,damage,id)
    if state.enemies[index].hp == 0:
        state.enemies[index].burn = 0
        state.enemies[index].ap = 0
        state.enemies[index].rp = 0
        state.done[index+1] = true
        record("death",ENEMIES[index].name,index,0,id)

func detonate(index: int, clear: bool, id: String) -> void:
    var count: int = state.enemies[index].burn
    if count <= 0 or state.enemies[index].hp <= 0:
        return
    if clear:
        state.enemies[index].burn = 0
    record("detonate","燃烧引爆",index,count*cfg.burn_damage,id,index+1)
    hit(index,count*cfg.burn_damage,id,"blast")

func target_for(entry: Dictionary) -> int:
    var candidates: Array = alive()
    var condition: int = int(entry.get("condition",0))
    if condition == 1:
        candidates = candidates.filter(func(i: int) -> bool: return state.enemies[i].burn > 0)
    elif condition == 2:
        candidates = candidates.filter(func(i: int) -> bool: return state.enemies[i].burn >= 4)
    elif condition == 3 and float(state.hp)/cfg.hero_health >= 0.5:
        return -1
    if candidates.is_empty():
        return -1
    var preference: int = 1 if entry.id == "double" else int(entry.get("target",0))
    if preference == 0 and preferred_target in candidates:
        return preferred_target
    var best: int = candidates[0]
    for i in candidates:
        if preference == 1 and state.enemies[i].burn > state.enemies[best].burn:
            best = i
        elif preference == 2 and state.enemies[i].hp < state.enemies[best].hp:
            best = i
    return best

func passive_ok(entry: Dictionary) -> bool:
    var condition: int = int(entry.get("condition",0))
    return condition == 0 or (condition == 1 and float(state.hp)/cfg.hero_health < 0.5) or (condition == 2 and state.rp >= 2)

func reaction(id: String, passives: Array, attacker: int = -1) -> bool:
    for entry in passives:
        if entry.id != id or not entry.enabled or state.rp <= 0 or not passive_ok(entry):
            continue
        state.rp -= 1
        if id == "charge":
            state.charge = true
        elif id == "mana":
            state.ap += 1
        record(id,skill(id).name,-1,0,id,0)
        if id == "shield":
            add_burn(attacker,1,id)
        return true
    return false

func transfer_burn(from: int, count: int) -> void:
    if count <= 0:
        return
    for offset in range(1,3):
        var next: int = (from+offset)%3
        if state.enemies[next].hp > 0:
            record("transfer","余烬转移",next,count,"burst",from+1)
            add_burn(next,count,"burst")
            return

func cast(entry: Dictionary) -> void:
    var definition: Dictionary = skill(entry.id)
    var selected: int = target_for(entry)
    if selected < 0 or definition.is_empty():
        return
    var targets: Array = alive() if entry.id in ["wall","funeral","inferno"] else [selected]
    var factor: int = 2 if state.charge else 1
    state.charge = false
    state.ap -= definition.cost
    var source: int = state.enemies[selected].burn
    record("cast",definition.name,selected,0,entry.id,0)
    if entry.id == "burst":
        add_burn(selected,2*factor,entry.id)
        var retained: int = state.enemies[selected].burn
        hit(selected,definition.damage,entry.id)
        detonate(selected,false,entry.id)
        if state.enemies[selected].hp == 0:
            transfer_burn(selected,retained)
        return
    for index in targets:
        hit(index,definition.damage,entry.id)
        if entry.id in ["ignite","wall","inferno"]:
            add_burn(index,factor,entry.id)
        elif entry.id in ["double","funeral"]:
            add_burn(index,state.enemies[index].burn*factor,entry.id)
    if entry.id == "spread":
        for index in alive():
            if index != selected:
                add_burn(index,source*factor,entry.id)
    if entry.id == "inferno":
        for index in targets:
            detonate(index,false,entry.id)

func hero_turn(plan: Array, passives: Array) -> void:
    var mana_used: bool = false
    var first_cast: bool = true
    for index in range(plan.size()):
        slot = index
        var entry: Dictionary = plan[index]
        if not entry.enabled or skill(entry.id).is_empty() or alive().is_empty():
            continue
        if target_for(entry) < 0:
            record("skip",skill(entry.id).name+" · 条件未满足",-1,0,entry.id,0)
            continue
        if state.ap < skill(entry.id).cost and not mana_used:
            mana_used = reaction("mana",passives)
        if state.ap < skill(entry.id).cost:
            record("skip",skill(entry.id).name+" · AP 不足",-1,0,entry.id,0)
            continue
        if first_cast:
            reaction("charge",passives)
            first_cast = false
        cast(entry)
    slot = -1

func enemy_turn(index: int, passives: Array) -> void:
    if state.enemies[index].ap <= 0:
        return
    state.enemies[index].ap -= 1
    record("enemy",ENEMIES[index].attack,-1,cfg.enemy_damage[index],"attack",index+1)
    var guarded: bool = reaction("shield",passives,index)
    var damage: int = int(ceil(cfg.enemy_damage[index]*(1.0-cfg.shield_reduction))) if guarded else cfg.enemy_damage[index]
    state.hp = maxi(0,state.hp-damage)
    record("hurt","",-1,damage,"attack",index+1)

func simulate(plan: Array, passives: Array, config: Resource, marked: int = -1) -> Array:
    initialize(config,marked)
    record("ready","战术锁定")
    for round_index in range(1,cfg.max_rounds+1):
        state.round = round_index
        state.ap = cfg.action_points
        state.rp = cfg.reaction_points
        state.charge = false
        state.done = [false,true,true,true]
        for i in alive():
            state.enemies[i].ap = ENEMIES[i].ap
            state.enemies[i].rp = ENEMIES[i].rp
            state.done[i+1] = false
        record("round","第 %d 回合" % round_index)
        var pending: Array = [0,1,2,3]
        while not pending.is_empty() and state.hp > 0 and not alive().is_empty():
            var actor: int = next_actor(pending)
            if actor < 0:
                break
            pending.erase(actor)
            begin_turn(actor)
            if actor == 0:
                hero_turn(plan,passives)
            else:
                enemy_turn(actor-1,passives)
            end_turn(actor)
        if state.hp <= 0 or alive().is_empty():
            break
        record("end_round","燃烧结算")
        for i in alive():
            detonate(i,true,"round_end")
        if alive().is_empty():
            break
    var victory: bool = state.hp > 0 and alive().is_empty()
    record("result","胜利" if victory else "战败")
    events[-1].merge({"victory":victory,"total_damage":total_damage,"peak_burn":peak_burn})
    return events

func preview(id: String, config: Resource) -> Array:
    initialize(config,0)
    state.ap = 9
    state.actor = 0
    for i in range(3):
        state.enemies[i].hp = 40 if i == 0 and id == "burst" else 500
        state.enemies[i].max_hp = state.enemies[i].hp
        state.enemies[i].burn = 3 if i == 0 else 1
    record("ready","效果预览")
    if is_passive(id):
        if id == "shield":
            begin_turn(1)
            enemy_turn(0,[rule(id)])
            end_turn(1)
        elif id == "mana":
            state.ap = 0
            reaction(id,[rule(id)],0)
            cast(rule("ignite"))
        else:
            reaction(id,[rule(id)],0)
            cast(rule("ignite"))
    else:
        cast(rule(id))
    record("preview_end","效果预览结束")
    return events
