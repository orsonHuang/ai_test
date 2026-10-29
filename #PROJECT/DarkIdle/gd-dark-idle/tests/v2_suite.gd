extends RefCounted
const Rules = preload("res://scripts/combat_rules.gd")
const Store = preload("res://scripts/tactics_store.gd")
const BALANCE = preload("res://resources/balance_v2.tres")
var checks: Array = []

func check(label: String, ok: bool) -> void:
    checks.append({"name":label,"passed":ok})

func fixture() -> RefCounted:
    var r = Rules.new()
    r.initialize(BALANCE)
    r.state.ap = 20
    for e in r.state.enemies:
        e.hp = 500
        e.max_hp = 500
        e.rp = 0
    return r

func kinds(r: RefCounted, kind: String) -> Array:
    return r.events.filter(func(e: Dictionary) -> bool: return e.kind == kind)

func run() -> Dictionary:
    var r = fixture()
    r.cast(Rules.rule("ignite"))
    check("点燃扣1AP造成4伤并加1层",r.state.ap == 19 and r.state.enemies[0].hp == 496 and r.state.enemies[0].burn == 1)
    r = fixture()
    r.cast(Rules.rule("wall"))
    check("火墙覆盖全部存活目标",r.state.enemies.all(func(e: Dictionary) -> bool: return e.hp == 497 and e.burn == 1))
    r.state.enemies[2].burn = 3
    r.cast(Rules.rule("double"))
    check("爆燃自动选择最高层数并翻倍",r.state.enemies[2].burn == 6 and r.state.enemies[2].hp == 493)
    var entry: Dictionary = Rules.rule("spread")
    entry.target = 1
    r.cast(entry)
    check("火星复制源层数而非搬走",r.state.enemies[0].burn == 7 and r.state.enemies[1].burn == 7 and r.state.enemies[2].burn == 6)
    r = fixture()
    r.state.enemies[0].burn = 2
    r.state.enemies[1].burn = 3
    r.cast(Rules.rule("funeral"))
    check("火葬扣2AP翻倍全体既有燃烧",r.state.ap == 18 and r.state.enemies[0].burn == 4 and r.state.enemies[1].burn == 6 and r.state.enemies[2].burn == 0)
    r = fixture()
    r.state.enemies[0].burn = 3
    r.cast(Rules.rule("burst"))
    check("炎爆正常扣AP且即时引爆保留层数",r.state.ap == 19 and r.state.enemies[0].burn == 5 and r.state.enemies[0].hp == 456)
    r.detonate(0,true,"round_end")
    check("回合末再次结算后清空",r.state.enemies[0].hp == 416 and r.state.enemies[0].burn == 0)
    r = fixture()
    r.state.enemies[0].burn = 2
    r.cast(Rules.rule("inferno"))
    check("炼狱扣2AP逐目标即时引爆保留层数",r.state.ap == 18 and r.state.enemies[0].hp == 476 and r.state.enemies[0].burn == 3 and r.state.enemies[2].burn == 1)
    for kill_hp in [4,30]:
        r = fixture()
        r.state.enemies[0].hp = kill_hp
        r.state.enemies[0].burn = 3
        r.state.enemies[1].burn = 2
        r.cast(Rules.rule("burst"))
        check("炎爆%s击杀将5层叠给下个目标且不连爆" % ("直伤" if kill_hp == 4 else "引爆"),r.state.enemies[0].burn == 0 and r.state.enemies[1].burn == 7 and r.state.enemies[1].hp == 500 and kinds(r,"transfer").size() == 1)
    r = fixture()
    r.preferred_target = 2
    r.state.enemies[2].hp = 1
    r.state.enemies[2].burn = 3
    r.state.enemies[0].hp = 0
    r.cast(Rules.rule("burst"))
    check("转移循环跳过死亡单位",r.state.enemies[1].burn == 5 and kinds(r,"transfer")[0].target == 1)
    r = fixture()
    r.state.enemies[1].hp = 0
    r.state.enemies[2].hp = 0
    r.state.enemies[0].hp = 1
    r.cast(Rules.rule("burst"))
    check("最后敌人死亡无转移",kinds(r,"transfer").is_empty())
    r = fixture()
    r.preferred_target = 2
    check("标记目标优先",r.target_for(Rules.rule("ignite")) == 2)
    entry = Rules.rule("ignite")
    entry.condition = 1
    r.state.enemies[0].burn = 2
    check("标记不满足条件时选择合格目标",r.target_for(entry) == 0)
    entry.condition = 2
    check("无人满足条件时跳过",r.target_for(entry) == -1)
    entry.condition = 0
    entry.target = 2
    r.state.enemies[1].hp = 23
    check("最低生命设置覆盖标记",r.target_for(entry) == 1)
    r.state.enemies[1].rp = 1
    r.hit(1,5,"ignite")
    r.hit(1,5,"ignite")
    check("敌人反应花1RP减伤一次",r.state.enemies[1].hp == 15 and r.state.enemies[1].rp == 0 and kinds(r,"enemy_guard").size() == 1)
    r = fixture()
    r.enemy_turn(0,[Rules.rule("shield")])
    check("炎盾反击加层且减伤并扣RP",r.state.hp == 114 and r.state.rp == 2 and r.state.enemies[0].burn == 1 and r.state.enemies[0].ap == 0)
    r = fixture()
    r.state.ap = 1
    r.hero_turn([Rules.rule("wall"),Rules.rule("ignite"),Rules.rule("ignite")],[Rules.rule("mana")])
    check("恢复魔力每轮最多一次且不足技能跳过",kinds(r,"mana").size() == 1 and kinds(r,"cast").size() == 2 and kinds(r,"skip").size() == 1)
    r = fixture()
    r.hero_turn([Rules.rule("wall"),Rules.rule("ignite")],[Rules.rule("charge")])
    check("蓄能只放大首次行动新增层数",r.state.enemies[0].burn == 3 and r.state.enemies[2].burn == 2 and kinds(r,"charge").size() == 1)
    entry = Rules.rule("shield")
    entry.condition = 1
    r = fixture()
    r.enemy_turn(0,[entry])
    check("反应附加条件不满足不消耗RP",r.state.hp == 108 and r.state.rp == 3)
    r = fixture()
    r.shift_initiative(3,0.99)
    check("位移接口实际改变下次出手角色",r.next_actor([0,1,2,3]) == 3)
    r.begin_turn(3)
    check("出手者到达行动轴右端",is_equal_approx(r.state.timeline[3],1.0) and r.state.actor == 3)
    r.end_turn(3)
    check("行动结束清空AP并退出本轮行动轴",r.state.timeline[3] == 0 and r.state.actor == -1 and r.state.done[3] and r.state.enemies[2].ap == 0)
    r.shift_initiative(0,2.0)
    check("位移范围限制",r.state.timeline[0] == 1)
    var plan: Array = Rules.default_plan()
    var passives: Array = Rules.default_passives()
    var before: String = JSON.stringify([plan,passives])
    var a: Array = Rules.new().simulate(plan,passives,BALANCE)
    var b: Array = Rules.new().simulate(plan,passives,BALANCE)
    check("模拟确定性且不改输入",a == b and before == JSON.stringify([plan,passives]))
    check("默认方案能够取胜",a[-1].victory and a[-1].state.hp > 0)
    var round_end_events: Array = a.filter(func(e: Dictionary) -> bool: return e.kind=="end_round")
    check("本轮全员AP用完后才结算燃烧",not round_end_events.is_empty() and round_end_events.all(func(e: Dictionary) -> bool: return e.state.ap==0 and e.state.enemies.all(func(enemy: Dictionary) -> bool: return enemy.ap==0) and e.state.done.all(func(done: bool) -> bool: return done)))
    var next_round: Array = a.filter(func(e: Dictionary) -> bool: return e.kind=="round" and e.state.round==2)
    check("下一轮恢复存活者资源并重新入轴",next_round.size()==1 and next_round[0].state.ap==4 and next_round[0].state.rp==3 and not next_round[0].state.done[0] and next_round[0].state.enemies[1].ap==1 and not next_round[0].state.done[2])
    var failed: Array = Rules.new().simulate([],[],BALANCE)
    check("不装备行动与反应正常战败",not failed[-1].victory and failed[-1].state.hp == 0)
    check("无可执行技能以待机放弃剩余AP不锁死",failed.any(func(e: Dictionary) -> bool: return e.kind=="wait" and e.actor==0 and e.amount==4 and e.state.ap==0))
    var all_preview: bool = true
    for definition in Rules.SKILLS+Rules.PASSIVES:
        var preview: Array = Rules.new().preview(definition.id,BALANCE)
        all_preview = all_preview and preview[-1].kind == "preview_end" and preview.any(func(e: Dictionary) -> bool: return e.skill == definition.id)
    check("十项技能预览均结束且不改战术",all_preview and before == JSON.stringify([plan,passives]))
    var safe: bool = true
    var rng: RandomNumberGenerator = RandomNumberGenerator.new()
    rng.seed = 9137
    for i in range(150):
        var p: Array = []
        for j in range(4):
            var row: Dictionary = Rules.rule(Rules.SKILLS[rng.randi_range(0,6)].id)
            row.condition = rng.randi_range(0,3)
            row.target = rng.randi_range(0,3)
            p.append(row)
        var e: Array = Rules.new().simulate(p,passives,BALANCE,rng.randi_range(-1,2))
        for item in e:
            safe = safe and item.state.hp >= 0 and item.state.ap >= 0 and item.state.rp >= 0
            for enemy in item.state.enemies:
                safe = safe and enemy.hp >= 0 and enemy.burn >= 0 and enemy.ap >= 0 and enemy.rp >= 0
        safe = safe and e.size() < 1000 and e[-1].kind == "result"
    check("150组战术有限结束且资源无负值",safe)
    var data: Dictionary = {"version":2,"plan":plan,"passives":passives,"marked":2,"click_target":true}
    var restored: Dictionary = Store.validate(JSON.parse_string(JSON.stringify(data)))
    check("4加2存档可往返JSON",not restored.is_empty() and restored.plan.size() == 4 and restored.passives.size() == 2 and restored.plan[0].id == plan[0].id and int(restored.marked) == 2 and restored.click_target)
    for field in ["slots","group","fraction","type","target","version"]:
        var bad: Dictionary = data.duplicate(true)
        match field:
            "slots": bad.plan.pop_back()
            "group": bad.passives[0].id = "wall"
            "fraction": bad.plan[0].condition = 0.5
            "type": bad.plan[0].enabled = "true"
            "target": bad.marked = 8
            "version": bad.version = 1
        check("拒绝无效存档："+field,Store.validate(bad).is_empty())
    var passed: int = checks.filter(func(c: Dictionary) -> bool: return c.passed).size()
    return {"checks":checks,"passed":passed,"failed":checks.size()-passed,"default_result":a[-1]}
