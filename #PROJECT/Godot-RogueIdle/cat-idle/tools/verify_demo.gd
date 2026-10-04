extends SceneTree

var checks: int = 0
var failures: Array[String] = []

func _init() -> void:
    var packed: PackedScene = load("res://scenes/expedition/ExpeditionDemo.tscn") as PackedScene
    _check(packed != null, "Main scene loads")
    if packed == null:
        quit(1)
        return
    var scene: Node = packed.instantiate()
    var count: int = _walk(scene)
    var pages: Node = scene.find_child("Pages", true, false)
    _check(pages.get_child_count() == 3, "Three native page instances")
    for page: Node in pages.get_children():
        _check(not page.scene_file_path.is_empty(), "Page keeps PackedScene reference: " + page.name)
    var world: Node = scene.find_child("World", true, false)
    _check(world.get_child_count() == 9, "Nine editable map tiles")
    for tile: Node in world.get_children():
        _check(tile.scene_file_path.ends_with("RegionTile.tscn"), "Tile instance: " + tile.name)
        _check(tile.get("definition") is FogRegion, "Tile resource: " + tile.name)
        _check(tile.get("definition").polygon.size() >= 3, "Tile geometry: " + tile.name)
    var config: FogCatalog = scene.get("catalog")
    _check(config != null and config.regions.size() == 9, "Catalog binding")
    _check(config.units.size() == 12 and config.events.size() == 6, "M1 content counts")
    _check(int(config.table("units").hero.atk) == 24, "Normal hero configuration")
    _check(is_equal_approx(float(scene.get("playback_interval")), 0.65), "Restored Inspector parameter")
    _check(ProjectSettings.get_setting("application/run/main_scene") == "res://scenes/expedition/ExpeditionDemo.tscn", "F5 entry")
    scene.free()
    print("VERIFY_DEMO: " + JSON.stringify({"checks": checks, "native_nodes": count, "failures": failures}))
    quit(0 if failures.is_empty() else 1)

func _check(condition: bool, message: String) -> void:
    checks += 1
    if not condition:
        failures.append(message)
        push_error(message)

func _walk(node: Node) -> int:
    var total: int = 1
    if node.get_parent() != null:
        _check(node.owner != null, "Saved owner: " + str(node.name))
    var attached: Script = node.get_script() as Script
    if attached != null:
        _check(attached.can_instantiate(), "Valid script: " + attached.resource_path)
    for child: Node in node.get_children():
        total += _walk(child)
    return total
