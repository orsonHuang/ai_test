extends SceneTree
func _initialize() -> void:
    var suite = load("res://tests/v2_suite.gd").new()
    var result: Dictionary = suite.run()
    print(JSON.stringify(result))
    quit(1 if result.failed > 0 else 0)
