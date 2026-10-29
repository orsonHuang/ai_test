extends RefCounted
const Rules = preload("res://scripts/combat_rules.gd")
const PATH: String = "user://tactics_v2.json"

static func valid_number(value: Variant, low: int, high: int) -> bool:
    return typeof(value) in [TYPE_INT,TYPE_FLOAT] and value == int(value) and int(value) >= low and int(value) <= high

static func validate(data: Variant) -> Dictionary:
    if not data is Dictionary or data.get("version") != 2:
        return {}
    var active: Variant = data.get("plan")
    var passive: Variant = data.get("passives")
    if not active is Array or active.size() != 4 or not passive is Array or passive.size() != 2:
        return {}
    for group in [active,passive]:
        var reaction: bool = group == passive
        for entry in group:
            if not entry is Dictionary or not entry.get("id") is String or not entry.get("enabled") is bool:
                return {}
            var id: String = entry.id
            if id != "" and (Rules.skill(id).is_empty() or Rules.is_passive(id) != reaction):
                return {}
            if not valid_number(entry.get("condition"),0,2 if reaction else 3) or not valid_number(entry.get("target"),0,3):
                return {}
    if not valid_number(data.get("marked"),-1,2) or not data.get("click_target") is bool:
        return {}
    return data.duplicate(true)

static func read_data() -> Dictionary:
    if not FileAccess.file_exists(PATH):
        return {}
    var parser: JSON = JSON.new()
    if parser.parse(FileAccess.get_file_as_string(PATH)) != OK:
        return {}
    return validate(parser.data)

static func save_data(plan: Array, passives: Array, marked: int, click_target: bool) -> bool:
    var data: Dictionary = {"version":2,"plan":plan,"passives":passives,"marked":marked,"click_target":click_target}
    if validate(data).is_empty():
        return false
    var file: FileAccess = FileAccess.open(PATH,FileAccess.WRITE)
    if file == null:
        return false
    file.store_string(JSON.stringify(data))
    return true
