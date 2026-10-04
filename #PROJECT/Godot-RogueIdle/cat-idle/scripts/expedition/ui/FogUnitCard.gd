extends PanelContainer
func display_unit(unit: Dictionary, position_index: int = 0) -> void:
    visible = not unit.is_empty()
    if unit.is_empty():
        return
    $Rows/Name.text = "%02d  %s" % [position_index + 1, unit.name]
    var maximum: int = int(unit.get("max_hp", unit.hp))
    $Rows/Health.max_value = maximum
    $Rows/Health.value = int(unit.hp)
    $Rows/HealthText.text = "生命 %d / %d   护盾 %d" % [unit.hp, maximum, unit.get("shield", 0)]
    $Rows/Stats.text = "攻 %d    甲 %d    速 %d" % [unit.atk, unit.armor, unit.speed]
    var states: PackedStringArray = []
    if int(unit.get("burn", 0)) > 0:
        states.append("灼烧 %d" % unit.burn)
    if int(unit.get("mark", 0)) > 0:
        states.append("被标记")
    if int(unit.hp) <= 0:
        states.append("倒下")
    $Rows/Status.visible = unit.has("burn")
    if unit.get("side", "") == "enemy" and unit.has("intent"):
        states.insert(0, str(unit.intent))
    $Rows/Status.text = " · ".join(states) if not states.is_empty() else "就绪"
    modulate = Color("#74818a") if int(unit.hp) <= 0 else Color.WHITE
