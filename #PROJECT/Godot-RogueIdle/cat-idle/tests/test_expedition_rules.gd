@tool
extends "res://addons/godot_ai/testing/test_suite.gd"

const Run = preload("res://scripts/expedition/FogRun.gd")
const Fight = preload("res://scripts/expedition/FogCombat.gd")
const Save = preload("res://scripts/expedition/FogSave.gd")
var source: FogCatalog

func suite_name() -> String:
    return "expedition_rules"

func suite_setup(_ctx: Dictionary) -> void:
    source = ResourceLoader.load("res://resources/expedition/catalog.tres", "", ResourceLoader.CACHE_MODE_REPLACE_DEEP) as FogCatalog

func _run(seed_value: int = 123, powered: bool = false) -> FogRun:
    var config: FogCatalog = source.duplicate() as FogCatalog
    config.units = []
    for template: Resource in source.units:
        config.units.append(template.duplicate())
    if powered:
        for unit: Resource in config.units:
            if unit.id == "hero":
                unit.atk = 2000
    var run: FogRun = Run.new()
    run.configure(config)
    run.new_run(seed_value)
    return run

func test_powered_fixture_does_not_mutate_shared_catalog() -> void:
    var powered: FogRun = _run(123, true)
    var normal: FogRun = _run(123)
    assert_eq(powered.tables.units.hero.atk, 2000)
    assert_eq(normal.tables.units.hero.atk, 24)
    assert_eq(source.table("units").hero.atk, 24)

func test_seed_fog_and_no_recursive_reveal() -> void:
    var a: FogRun = _run()
    var b: FogRun = _run()
    assert_eq(a.data.regions, b.data.regions)
    assert_eq(a.data.revealed.size(), 3)
    assert_false(a.data.revealed.has("ember"))
    assert_true(a.move_to("briar"))
    assert_true(a.data.revealed.has("quarry"))
    assert_false(a.data.revealed.has("frost"))
    assert_false(a.move_to("village"))
    assert_true(a.local_state().activities.has("recruit"))

func test_budget_no_double_claim_and_regional_growth() -> void:
    var run: FogRun = _run(123, true)
    run.move_to("briar")
    assert_true(run.begin_battle("dungeon"))
    assert_eq(run.budget(), 4)
    var snapshot: Dictionary = run.data.duplicate(true)
    var restored: FogRun = _run()
    assert_true(restored.restore(snapshot))
    assert_true(restored.data.battle.paused)
    assert_eq(restored.budget(), 4)
    run.advance_battle(true)
    assert_true(run.claim_reward(true))
    assert_eq(run.data.level, 2)
    assert_eq(run.data.inventory.size(), 1)
    assert_false(run.claim_reward(true))
    assert_eq(run.data.inventory.size(), 1)
    assert_true(run.begin_battle("dungeon"))
    run.advance_battle(true)
    run.claim_reward(true)
    assert_eq(run.data.level, 2)
    assert_eq(run.set_status().count, 2)
    assert_true(run.begin_battle("dungeon"))
    run.advance_battle(true)
    run.claim_reward(true)
    assert_eq(run.budget(), 0)
    assert_eq(run.data.ledger.thorn.size(), 3)
    assert_eq(run.set_status().count, 3)
    assert_false(run.begin_battle("dungeon"))
    assert_true(run.move_to("quarry"))
    assert_eq(run.budget(), 6)

func test_equipping_max_health_does_not_heal() -> void:
    var run: FogRun = _run(42, true)
    run.move_to("briar")
    run.data.party[0].hp = 15
    run.data.inventory.append(run._make_item("thorn", 1, "test/armor", "armor", "fine"))
    assert_true(run.equip("test/armor"))
    assert_eq(run.members()[0].hp, 15)
    assert_true(run.rest())
    assert_gt(run.members()[0].hp, 15)
    assert_eq(run.budget(), 5)

func test_recruit_respects_hero_after_formation_swap() -> void:
    var run: FogRun = _run()
    run.move_to("briar")
    run.data.party[0].hp = 80
    assert_true(run.swap_formation(0))
    var candidate: String = run.recruit_candidates()[0]
    assert_true(run.recruit(candidate))
    assert_eq(run.data.party.size(), 3)
    var arriving: Dictionary = run.members()[2]
    assert_true(float(arriving.hp) / float(arriving.max_hp) <= 0.5)
    run.move_to("river")
    run.local_state().activities = ["recruit", "event", "chest"]
    var next: String = run.recruit_candidates()[0]
    assert_false(run.recruit(next, 1))
    assert_eq(run.budget(), 6)
    assert_true(run.recruit(next, 0))

func test_battle_is_deterministic_and_attributes_burn() -> void:
    var run: FogRun = _run()
    run.move_to("briar")
    var party: Array = run.members()
    var enemies: Array = run.preview_enemies("dungeon")
    var options: Dictionary = {"active": "fire", "passive": "regen", "target": "front",
        "policy": "ready", "set_id": "ember", "set_count": 3}
    var first: Dictionary = Fight.new().simulate(party, enemies, options, source)
    var second: Dictionary = Fight.new().simulate(party, enemies, options, source)
    assert_eq(first, second)
    assert_true(first.frames.size() > 1)
    assert_true(int(first.rounds) <= int(source.rule("battle_round_cap")))
    assert_gt(int(first.stats["0"].burn), 0)

func test_event_invalid_branch_keeps_paid_entry_and_fallback() -> void:
    var run: FogRun = _run()
    run.move_to("briar")
    run.local_state().activities = ["event", "recruit", "chest"]
    run.local_state().event_id = "medic"
    run.data.gold = 0
    assert_true(run.begin_event())
    assert_eq(run.budget(), 5)
    assert_false(run.choose_event("a"))
    assert_eq(run.data.gold, 0)
    assert_eq(run.budget(), 5)
    assert_true(run.choose_event("b"))
    assert_eq(run.data.phase, "region")
    assert_false(run.begin_event())

func test_save_load_and_corruption_falls_back() -> void:
    var run: FogRun = _run()
    var path: String = "user://fog_test_transaction.json"
    assert_true(Save.save_state(run.data, path).ok)
    var original_gold: int = int(run.data.gold)
    run.data.gold = 999
    assert_true(Save.save_state(run.data, path).ok)
    var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
    file.store_string("interrupted")
    file.close()
    var recovered: Dictionary = Save.load_state(path)
    assert_true(recovered.ok)
    assert_true(recovered.from_backup)
    assert_eq(int(recovered.state.gold), original_gold)
    for candidate: String in [path, path + ".bak", path + ".tmp"]:
        if FileAccess.file_exists(candidate):
            DirAccess.remove_absolute(ProjectSettings.globalize_path(candidate))

func test_every_map_route_has_three_regions() -> void:
    var run: FogRun = _run()
    var paths: Array = [["village"]]
    var completed: int = 0
    while not paths.is_empty():
        var route: Array = paths.pop_front()
        if route.back() == "castle":
            assert_eq(route.size(), 5)
            completed += 1
            continue
        for next: String in run.tables.regions[route.back()].next_ids:
            var continuation: Array = route.duplicate()
            continuation.append(next)
            paths.append(continuation)
    assert_eq(completed, 6)

func test_burn_hits_health_without_spending_shield() -> void:
    var run: FogRun = _run()
    run.move_to("ember")
    var hero: Dictionary = run.members()[0]
    hero.armor = 100
    hero.atk = 1
    hero.hp = 500
    hero.max_hp = 500
    var enemy: Dictionary = run.tables.units.ember.duplicate(true)
    enemy.hp = 10000
    enemy.max_hp = 10000
    enemy.atk = 1
    var report: Dictionary = Fight.new().simulate([hero], [enemy],
        {"active": "guard", "passive": "resolve", "policy": "ready", "target": "front", "opening_shield": 80}, source)
    var checked: bool = false
    for index: int in range(1, report.frames.size()):
        var frame: Dictionary = report.frames[index]
        if frame.kind == "burn" and int(frame.actor) == 0:
            var before: Dictionary = report.frames[index - 1].units[0]
            var after: Dictionary = frame.units[0]
            assert_eq(after.shield, before.shield)
            assert_gt(int(before.shield), 0)
            assert_eq(int(before.hp) - int(after.hp), 7)
            checked = true
            break
    assert_true(checked)

func test_cooldown_uses_own_actions_and_speed_order() -> void:
    var run: FogRun = _run()
    var hero: Dictionary = run.members()[0]
    hero.hp = 10000
    hero.max_hp = 10000
    hero.atk = 1
    hero.speed = 20
    var enemy: Dictionary = run.tables.units.raider.duplicate(true)
    enemy.hp = 10000
    enemy.max_hp = 10000
    enemy.atk = 1
    var report: Dictionary = Fight.new().simulate([hero], [enemy],
        {"active": "guard", "passive": "resolve", "policy": "ready", "target": "front"}, source)
    var shield_rounds: Array = []
    var first_actor: int = -1
    for frame: Dictionary in report.frames:
        if first_actor == -1 and int(frame.actor) >= 0:
            first_actor = int(frame.actor)
        if frame.kind == "shield" and int(frame.actor) == 0:
            shield_rounds.append(int(frame.round))
    assert_eq(first_actor, 0)
    assert_eq(shield_rounds.slice(0, 3), [1, 4, 7])

func test_counter_once_per_round_and_no_recursive_chain() -> void:
    var run: FogRun = _run()
    var hero: Dictionary = run.members()[0]
    hero.hp = 10000
    hero.max_hp = 10000
    hero.atk = 10
    var enemy: Dictionary = run.tables.units.raider.duplicate(true)
    enemy.hp = 10000
    enemy.max_hp = 10000
    enemy.atk = 1
    var report: Dictionary = Fight.new().simulate([hero], [enemy, enemy.duplicate(true)],
        {"active": "guard", "passive": "resolve", "policy": "ready", "target": "front", "set_id": "thorn", "set_count": 3}, source)
    var counts: Dictionary = {}
    for frame: Dictionary in report.frames:
        if frame.kind == "counter":
            counts[frame.round] = int(counts.get(frame.round, 0)) + 1
    assert_true(not counts.is_empty())
    for value: int in counts.values():
        assert_eq(value, 1)

func test_defeat_claim_is_terminal_and_keeps_final_health() -> void:
    var run: FogRun = _run()
    run.move_to("briar")
    run.data.party = [{"id": "hero", "hp": 1}]
    run.configure_tactics("burst", "fury", "front", "ready")
    assert_true(run.begin_battle("dungeon"))
    assert_eq(run.data.battle.report.outcome, "defeat")
    run.advance_battle(true)
    assert_true(run.claim_reward())
    assert_eq(run.data.phase, "ended")
    assert_eq(run.data.party[0].hp, 0)
    assert_false(run.move_to("quarry"))
    assert_false(run.claim_reward())

