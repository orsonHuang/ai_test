@tool
class_name FogCatalog
extends Resource

@export var rules_version: String = "gdd-v1-demo-1"
@export var rules: Dictionary = {}
@export var regions: Array[Resource] = []
@export var units: Array[Resource] = []
@export var activities: Array[Resource] = []
@export var equipment: Array[Resource] = []
@export var affixes: Array[Resource] = []
@export var sets: Array[Resource] = []
@export var skills: Array[Resource] = []
@export var events: Array[Resource] = []

func table(table_name: String) -> Dictionary:
    var output: Dictionary = {}
    var entries: Array = get(table_name)
    for entry: Resource in entries:
        if entry.has_method("to_row"):
            var row: Dictionary = entry.call("to_row")
            output[str(row.id)] = row
        else:
            var row: Dictionary = entry.get("values").duplicate(true)
            row["id"] = str(entry.get("id"))
            if not row.has("name"):
                row["name"] = str(entry.get("display_name"))
            output[str(entry.get("id"))] = row
    return output

func rule(key: String) -> float:
    return float(rules.get(key, 0.0))

func region_resource(region_id: String) -> Resource:
    for entry: Resource in regions:
        if str(entry.get("id")) == region_id:
            return entry
    return null
