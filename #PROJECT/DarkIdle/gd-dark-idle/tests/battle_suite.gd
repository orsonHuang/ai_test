extends RefCounted
const Rules = preload("res://scripts/battle_rules.gd")
const Balance = preload("res://resources/balance.tres")
var checks: Array = []

func check(ok: bool, name: String, details: Variant = null) -> void:
    checks.append({"name":name,"passed":ok,"details":details})

func fixture(stacks: Array = [0,0,0]):
    var engine = Rules.new()
    engine.cfg = Balance.duplicate()
    engine.state = {"hp":120,"ap":20,"rp":3,"round":1,"charge":false,"enemies":[]}
    for i in range(3):
        engine.state.enemies.append({"hp":1000,"max_hp":1000,"burn":stacks[i]})
    return engine

func rule(id: String, condition: int = 0, target: int = 0) -> Dictionary:
    return {"id":id,"enabled":true,"condition":condition,"target":target}

func burns(engine) -> Array:
    return engine.state.enemies.map(func(enemy: Dictionary) -> int: return enemy.burn)

func count_event(events: Array, kind: String) -> int:
    return events.filter(func(event: Dictionary) -> bool: return event.kind == kind).size()

func run() -> Dictionary:
    checks.clear()
    var engine = fixture()
    engine.cast(rule("ignite"))
    check(burns(engine) == [1,0,0] and engine.state.enemies[0].hp == 996 and engine.state.ap == 19,"点燃：单体直伤 + 一层 / 1 AP")
    engine = fixture()
    engine.cast(rule("wall"))
    check(burns(engine) == [1,1,1] and engine.state.enemies[2].hp == 997,"火墙：全体直伤 + 一层")
    engine = fixture([1,3,2])
    engine.cast(rule("double",0,2))
    check(burns(engine) == [1,6,2],"爆燃：无视目标偏好，选择燃烧最多并翻倍")
    engine = fixture([4,1,2])
    engine.cast(rule("spread"))
    check(burns(engine) == [4,5,6],"火星：复制叠加，保留源目标")
    engine = fixture([4,1,2])
    engine.state.enemies[0].hp = 1
    engine.cast(rule("spread"))
    check(burns(engine) == [0,5,6],"火星：源目标被直伤击败仍按施法快照扩散")
    engine = fixture([1,3,0])
    engine.cast(rule("funeral"))
    check(burns(engine) == [2,6,0] and engine.state.ap == 18,"火葬：全体翻倍 / 零层仍为零 / 2 AP")
    engine = fixture([3,0,0])
    engine.cast(rule("burst"))
    check(burns(engine) == [5,0,0] and engine.state.enemies[0].hp == 956,"炎爆：+2 后立即引爆 40，保留五层")
    engine.detonate(0,true,"round_end")
    check(engine.state.enemies[0].hp == 916 and burns(engine) == [0,0,0],"回合末再次引爆 40 后清空")
    engine = fixture([1,2,3])
    engine.cast(rule("inferno"))
    check(burns(engine) == [2,3,4] and engine.state.enemies[2].hp == 968 and engine.state.ap == 18,"炼狱：全体 +1 再引爆 / 无额外直伤 / 保留 / 2 AP")
    engine = fixture()
    engine.state.charge = true
    engine.cast(rule("wall"))
    engine.cast(rule("wall"))
    check(burns(engine) == [3,3,3] and not engine.state.charge,"蓄能：仅下一行动新增层数翻倍")
    engine = fixture([3,0,0])
    engine.state.charge = true
    engine.cast(rule("double"))
    check(burns(engine) == [9,0,0],"蓄能与翻倍：原有三层 + 新增六层 = 九层")
    engine = fixture([0,2,4])
    check(engine.target_for(rule("ignite",2,2)) == 2,"条件先过滤，再按目标偏好选取")
    check(engine.target_for(rule("ignite",3)) == -1,"生命门槛未到时跳过")
    engine.state.enemies[0].hp = 0
    check(engine.target_for(rule("ignite",0,2)) == 1,"阵亡目标不可选")
    engine = fixture()
    check(engine.reaction("shield",Rules.default_passives(),1) and engine.state.rp == 2 and burns(engine) == [0,1,0],"炎盾：受击前消耗 RP，攻击者叠火")
    engine.state.rp = 0
    check(not engine.reaction("shield",Rules.default_passives(),1) and burns(engine) == [0,1,0],"RP 不足时不触发炎盾")
    var cfg: Resource = Balance.duplicate()
    cfg.max_rounds = 1
    cfg.action_points = 0
    var events: Array = Rules.new().simulate([rule("ignite"),rule("ignite"),rule("ignite")],[{"id":"mana","enabled":true,"condition":0}],cfg)
    check(count_event(events,"mana") == 1 and count_event(events,"cast") == 1,"魔力恢复每轮最多一次，不产生资源循环")
    cfg.action_points = 6
    events = Rules.new().simulate([rule("ignite",2)],[],cfg)
    check(count_event(events,"cast") == 0 and events[-1].state.ap == 6,"条件不满足不消耗 AP")
    events = Rules.new().simulate([],Rules.default_passives(),cfg)
    var first_shield: int = -1
    var first_hurt: Dictionary = {}
    for i in range(events.size()):
        if events[i].kind == "shield" and first_shield < 0:
            first_shield = i
        if events[i].kind == "hurt":
            first_hurt = events[i]
            check(first_shield >= 0 and first_shield < i and first_hurt.amount == 6,"炎盾先于伤害结算，12 减至 6")
            break
    cfg.hero_health = 1
    events = Rules.new().simulate([rule("wall")],[],cfg)
    check(not events[-1].victory and count_event(events,"end_round") == 0,"法师阵亡立即失败，不追加回合末伤害")
    var baseline: Array = Rules.new().simulate(Rules.default_plan(),Rules.default_passives(),Balance)
    check(baseline[-1].victory and baseline[-1].state.round == 1 and baseline[-1].state.hp == 78,"默认核爆连段：一回合胜利 / 剩余 78 HP",baseline[-1])
    check(baseline == Rules.new().simulate(Rules.default_plan(),Rules.default_passives(),Balance),"相同输入完整事件序列确定一致")
    var bad_plan: Array = Rules.default_plan()
    for entry in bad_plan:
        entry.enabled = false
    events = Rules.new().simulate(bad_plan,[],Balance)
    check(not events[-1].victory and events[-1].state.hp == 0,"无行动且无反应：可达失败结果")
    cfg = Balance.duplicate()
    cfg.enemy_damage = PackedInt32Array([0,0,0])
    events = Rules.new().simulate(bad_plan,[],cfg)
    check(not events[-1].victory and events[-1].state.round == 8,"无进展战斗在第八回合结束")
    var invariant_ok: bool = true
    var rng: RandomNumberGenerator = RandomNumberGenerator.new()
    rng.seed = 20261029
    for sample in range(100):
        var random_plan: Array = []
        var random_passives: Array = Rules.default_passives()
        for slot in range(7):
            random_plan.append(rule(Rules.SKILLS[rng.randi_range(0,6)].id,rng.randi_range(0,3),rng.randi_range(0,2)))
        for passive in random_passives:
            passive.enabled = rng.randi_range(0,1) == 1
            passive.condition = rng.randi_range(0,2)
        events = Rules.new().simulate(random_plan,random_passives,Balance)
        for event in events:
            invariant_ok = invariant_ok and event.state.hp >= 0 and event.state.ap >= 0 and event.state.rp >= 0
            for enemy in event.state.enemies:
                invariant_ok = invariant_ok and enemy.hp >= 0 and enemy.burn >= 0
        invariant_ok = invariant_ok and events[-1].kind == "result" and events[-1].state.round <= 8
    check(invariant_ok,"100 组固定种子战术：资源不为负、结算有限且有结果")
    var failures: Array = checks.filter(func(entry: Dictionary) -> bool: return not entry.passed)
    return {"passed":checks.size()-failures.size(),"failed":failures.size(),"checks":checks}
