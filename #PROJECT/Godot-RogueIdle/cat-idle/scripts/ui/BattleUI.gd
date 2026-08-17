class_name BattleUI
extends Control

@export var battle_manager: BattleManager
@export var log_label: RichTextLabel
@export var restart_button: Button
@export var player_hp_bar: ProgressBar
@export var enemy_hp_bar: ProgressBar
@export var player_info: Label
@export var enemy_info: Label
@export var turn_indicator: Label

var log_lines: Array[String] = []
const MAX_LOG_LINES: int = 6

func _ready():
	if battle_manager == null:
		battle_manager = get_node_or_null("../../BattleManager")
	if log_label == null:
		log_label = get_node_or_null("LogPanel/LogLabel")
	if restart_button == null:
		restart_button = get_node_or_null("RestartButton")
	if player_hp_bar == null:
		player_hp_bar = get_node_or_null("LeftPanel/PlayerHPBar")
	if enemy_hp_bar == null:
		enemy_hp_bar = get_node_or_null("RightPanel/EnemyHPBar")
	if player_info == null:
		player_info = get_node_or_null("LeftPanel/PlayerInfo")
	if enemy_info == null:
		enemy_info = get_node_or_null("RightPanel/EnemyInfo")
	if turn_indicator == null:
		turn_indicator = get_node_or_null("TopBar/TurnIndicator")

	if battle_manager == null:
		return
	battle_manager.log_message.connect(_on_log_message)
	battle_manager.turn_started.connect(_on_turn_started)
	battle_manager.battle_ended.connect(_on_battle_ended)
	if restart_button != null:
		restart_button.pressed.connect(_on_restart)

func _on_log_message(text: String):
	log_lines.append(text)
	if log_lines.size() > MAX_LOG_LINES:
		log_lines.remove_at(0)
	if log_label != null:
		log_label.text = "\n".join(log_lines)

func _on_turn_started(character: BattleCharacter):
	if turn_indicator != null:
		turn_indicator.text = "%s 的回合" % character.data.display_name
	_update_bars()

func _on_battle_ended(winner_is_player: bool):
	if turn_indicator != null:
		turn_indicator.text = "玩家%s" % ("胜利" if winner_is_player else "战败")
	_update_bars()

func _on_restart():
	if battle_manager != null:
		battle_manager.restart()
		log_lines.clear()
		if log_label != null:
			log_label.text = ""

func _process(_delta: float):
	_update_bars()

func _update_bars():
	if battle_manager == null:
		return
	if battle_manager.player != null and player_hp_bar != null:
		player_hp_bar.max_value = battle_manager.player.data.max_hp
		player_hp_bar.value = battle_manager.player.data.current_hp
	if battle_manager.enemy != null and enemy_hp_bar != null:
		enemy_hp_bar.max_value = battle_manager.enemy.data.max_hp
		enemy_hp_bar.value = battle_manager.enemy.data.current_hp
	_update_info()

func _update_info():
	if battle_manager == null:
		return
	if battle_manager.player != null and player_info != null:
		var d = battle_manager.player.data
		player_info.text = "攻:%d 防:%d 速:%d 暴:%.0f%%" % [d.attack, d.defense, d.speed, d.crit_rate * 100]
	if battle_manager.enemy != null and enemy_info != null:
		var d = battle_manager.enemy.data
		enemy_info.text = "攻:%d 防:%d 速:%d 暴:%.0f%%" % [d.attack, d.defense, d.speed, d.crit_rate * 100]
