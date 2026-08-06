# Godot Demo系统信号连接关系

## 信号连接概览

### 1. 战斗系统信号连接

```
[Player] 
├── health_changed(new_health, max_health) → [UIManager::HealthBar]
├── damage_taken(damage_amount) → [UIManager::DamagePopup]
├── attack_performed(target) → [Enemy::take_damage()]
└── died() → [GameStateManager::handle_player_death()]

[Enemy]
├── health_changed(new_health, max_health) → [UIManager::EnemyHealthBar]
├── damage_taken(damage_amount) → [UIManager::DamagePopup]
├── died(enemy_type, drop_items) → [DropSystem::spawn_drops()]
└── attack_performed(target) → [Player::take_damage()]

[Weapon]
└── attack_triggered() → [Player::perform_attack()]
```

### 2. 地图与关卡系统信号连接

```
[Level]
├── level_loaded(level_data) → [GameStateManager::update_game_state()]
├── exit_entered() → [GameStateManager::prepare_level_transition()]
├── enemy_spawned(enemy_instance) → [GameStateManager::register_enemy()]
└── chest_opened(chest_id, items) → [Inventory::add_items()]

[MapSelection]
├── node_selected(node_id) → [Level::load_level_for_node()]
├── path_confirmed(start_node, end_node) → [GameStateManager::start_level_transition()]
└── map_closed() → [GameStateManager::resume_game()]

[Door]
├── door_opened(door_id) → [Level::activate_door()]
└── door_passed(player_position) → [Level::change_room()]
```

### 3. 游戏管理系统信号连接

```
[GameStateManager]
├── game_paused() → [UIManager::show_pause_menu()]
├── game_resumed() → [UIManager::hide_pause_menu()]
├── level_started(level_info) → [Level::initialize_level()]
├── level_completed(completion_data) → [MapSelection::unlock_next_nodes()]
├── player_respawned() → [Player::reset_stats()]
└── game_over() → [UIManager::show_game_over_screen()]

[GameData]
├── player_stat_changed(stat_name, new_value) → [UIManager::update_stat_display()]
├── inventory_changed(item_list) → [Inventory::refresh_display()]
├── equipment_changed(equipment_slot, item) → [Player::update_equipment()]
└── game_saved(save_data) → [GameStateManager::confirm_save()]
```

### 4. UI系统信号连接

```
[UIManager]
├── pause_requested() → [GameStateManager::toggle_pause()]
├── inventory_requested() → [Inventory::toggle_visibility()]
├── menu_button_pressed(button_id) → [GameStateManager::handle_menu_action()]
└── settings_changed(settings) → [AudioManager::apply_settings()]

[Inventory]
├── item_used(item_id) → [Player::use_item()]
├── item_equipped(item_id, slot) → [Player::equip_item()]
├── item_dropped(item_id) → [Level::spawn_item_on_ground()]
└── inventory_closed() → [UIManager::focus_player()]

[BattleHUD]
├── special_attack_requested() → [Player::perform_special_attack()]
└── heal_requested() → [Player::use_healing_item()]
```

### 5. 音频与效果系统信号连接

```
[AudioManager]
├── play_sfx(sound_name, position) → [AudioStreamPlayer2D::play_sound()]
├── play_music(music_name) → [AudioStreamPlayer::play_track()]
└── volume_changed(volume_type, level) → [AudioServer::set_volume_scale()]

[DropSystem]
└── item_dropped(item_type, position) → [AudioManager::play_drop_sound()]
```

## 主要信号接口定义

### Player.gd 信号接口
```gdscript
# 玩家状态变化信号
signal health_changed(new_health, max_health)
signal damage_taken(damage_amount)
signal attack_performed(target)
signal died()
signal stat_changed(stat_name, old_value, new_value)

# 玩家行为信号
signal moved(direction)
signal item_used(item_id)
signal equipment_changed(equipment_slot, item)
```

### Enemy.gd 信号接口
```gdscript
# 敌人状态变化信号
signal health_changed(new_health, max_health)
signal damage_taken(damage_amount)
signal died(enemy_type, drop_items)
signal detected_player(player)

# AI行为信号
signal started_chasing(player)
signal stopped_chasing()
signal attack_performed(target)
```

### GameStateManager.gd 信号接口
```gdscript
# 游戏状态变化信号
signal game_paused()
signal game_resumed()
signal level_started(level_info)
signal level_ended(result_data)
signal level_transition_started(from_level, to_level)
signal level_transition_completed(to_level)
signal player_respawned()
signal game_over()

# 系统事件信号
signal player_level_up(new_level)
signal achievement_unlocked(achievement_id)
signal score_updated(new_score)
```

### Level.gd 信号接口
```gdscript
# 关卡状态信号
signal level_loaded(level_data)
signal level_unloaded()
signal enemies_cleared()
signal exit_entered()
signal door_opened(door_id)
signal chest_opened(chest_id, items)

# 生成与交互信号
signal enemy_spawned(enemy_instance)
signal item_spawned(item_instance)
signal player_entered_room(room_id)
signal room_cleared(room_id)
```

### MapSelection.gd 信号接口
```gdscript
# 地图选择信号
signal node_selected(node_id)
signal node_hovered(node_id)
signal path_confirmed(start_node, end_node)
signal map_closed()
signal level_ready(level_data)

# 进度更新信号
signal nodes_unlocked(node_ids)
signal current_position_changed(node_id)
```