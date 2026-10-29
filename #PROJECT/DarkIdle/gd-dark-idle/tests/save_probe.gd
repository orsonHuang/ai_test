extends RefCounted

func run(scene: Node) -> Dictionary:
    var path: String = "user://tactics.json"
    var old_text: String = FileAccess.get_file_as_string(path)
    var old_plan: Array = scene.plan.duplicate(true)
    var old_passives: Array = scene.passives.duplicate(true)
    var base: Dictionary = {"version":1,"plan":old_plan.duplicate(true),"passives":old_passives.duplicate(true)}
    var cases: Array = [{"name":"破损 JSON","text":"{broken"}]
    for kind in ["string_condition","fractional_condition","invalid_target","invalid_passive","unknown_version","missing_rows"]:
        var data: Dictionary = base.duplicate(true)
        data.plan[0].id = "ignite" if old_plan[0].id != "ignite" else "wall"
        match kind:
            "string_condition": data.plan[0].condition = "bad"
            "fractional_condition": data.plan[0].condition = 1.25
            "invalid_target": data.plan[0].target = 3
            "invalid_passive": data.passives[0].condition = "bad"
            "unknown_version": data.version = 2
            "missing_rows": data.plan.pop_back()
        cases.append({"name":kind,"text":JSON.stringify(data)})
    var checks: Array = []
    for entry in cases:
        var file: FileAccess = FileAccess.open(path,FileAccess.WRITE)
        file.store_string(entry.text)
        file.close()
        scene._load_plan()
        checks.append({"name":entry.name,"passed":scene.plan == old_plan and scene.passives == old_passives})
    var restored: FileAccess = FileAccess.open(path,FileAccess.WRITE)
    restored.store_string(old_text)
    restored.close()
    scene.plan = old_plan
    scene.passives = old_passives
    scene._load_plan()
    scene._refresh_rows()
    checks.append({"name":"恢复原存档后加载一致","passed":scene.plan == old_plan and scene.passives == old_passives})
    var failed: int = checks.filter(func(item: Dictionary) -> bool: return not item.passed).size()
    return {"passed":checks.size()-failed,"failed":failed,"checks":checks}
