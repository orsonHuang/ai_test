# Godot Demo接口规范文档

## 1. 信号接口规范

### 通用信号格式
```gdscript
signal signal_name(param1: Type, param2: Type, ...)
```

### 参数命名约定
- 使用小写字母开头的驼峰式命名法 (camelCase)
- 数值参数后缀使用单位 (health_points, damage_amount)
- 位置参数使用 _position 后缀 (world_position, grid_position)
- 时间参数使用 _seconds 或 _ms 后缀 (duration_seconds, delay_ms)

## 2. Player节点接口

### 信号定义
```gdscript
# 状态变化信号
signal health_changed(new_health: int, max_health: int)
signal damage_taken(damage_amount: int, source: Node)
signal attack_performed(target: Node, damage_dealt: int)
signal died()
signal stat_changed(stat_name: String, old_value: int, new_value: int)

# 行为信号
signal moved(direction: Vector2)
signal item_used(item_id: String, success: bool)
signal equipment_changed(equipment_slot: String, item: Dictionary)
signal special_attack_performed(attack_type: String)
```

### 方法接口
```gdscript
# 战斗方法
func take_damage(damage: int) -> void
func perform_attack(target: Node) -> bool
func perform_special_attack(attack_type: String) -> bool

# 状态管理方法
func add_health(amount: int) -> void
func change_stat(stat_name: String, modifier: int) -> void
func die() -> void

# 物品交互方法
func use_item(item_id: String) -> bool
func equip_item(item: Dictionary, slot: String) -> bool
func add_item_to_inventory(item: Dictionary) -> bool
```

## 3. Enemy节点接口

### 信号定义
```gdscript
# 状态变化信号
signal health_changed(new_health: int, max_health: int)
signal damage_taken(damage_amount: int, source: Node)
signal died(enemy_type: String, drop_items: Array)
signal detected_player(player: Node)

# AI行为信号
signal started_chasing(player: Node)
signal stopped_chasing()
signal attack_performed(target: Node, damage_dealt: int)
signal entered_detection_range(player: Node)
signal exited_detection_range(player: Node)
```

### 方法接口
```gdscript
# 战斗方法
func take_damage(damage: int, source: Node) -> void
func perform_attack(target: Node) -> void
func die() -> void

# AI方法
func detect_player() -> Node
func chase_player(player: Node) -> void
func patrol_area() -> void
func stop_movement() -> void

# 配置方法
func set_enemy_data(data: Dictionary) -> void
func get_enemy_type() -> String
```

## 4. Level节点接口

### 信号定义
```gdscript
# 关卡状态信号
signal level_loaded(level_data: Dictionary)
signal level_unloaded()
signal enemies_cleared()
signal exit_entered()
signal door_opened(door_id: String)
signal chest_opened(chest_id: String, items: Array)

# 生成与交互信号
signal enemy_spawned(enemy_instance: Node)
signal item_spawned(item_instance: Node)
signal player_entered_room(room_id: String)
signal room_cleared(room_id: String)
```

### 方法接口
```gdscript
# 关卡管理方法
func load_level(level_data: Dictionary) -> void
func unload_level() -> void
func initialize_level() -> void

# 生成方法
func spawn_enemy(enemy_type: String, position: Vector2) -> Node
func spawn_item(item_data: Dictionary, position: Vector2) -> Node
func spawn_chest(chest_data: Dictionary, position: Vector2) -> Node

# 房间管理方法
func open_door(door_id: String) -> void
func check_room_clear() -> bool
func activate_exit() -> void
```

## 5. GameStateManager接口

### 信号定义
```gdscript
# 游戏状态信号
signal game_paused()
signal game_resumed()
signal level_started(level_info: Dictionary)
signal level_ended(result_data: Dictionary)
signal level_transition_started(from_level: String, to_level: String)
signal level_transition_completed(to_level: String)
signal player_respawned()
signal game_over()

# 系统事件信号
signal player_level_up(new_level: int)
signal achievement_unlocked(achievement_id: String)
signal score_updated(new_score: int)
```

### 方法接口
```gdscript
# 状态管理方法
func start_game() -> void
func pause_game() -> void
func resume_game() -> void
func end_game() -> void

# 关卡管理方法
func start_level(level_name: String) -> void
func complete_level() -> void
func transition_to_level(target_level: String) -> void

# 数据管理方法
func save_game() -> void
func load_game() -> void
func reset_game() -> void
```

## 6. UI相关接口

### Inventory接口
```gdscript
# 信号定义
signal item_used(item_id: String)
signal item_equipped(item_id: String, slot: String)
signal item_dropped(item_id: String)
signal inventory_closed()

# 方法接口
func add_item(item: Dictionary) -> bool
func remove_item(item_id: String, amount: int = 1) -> bool
func use_item(item_id: String) -> bool
func equip_item(item_id: String, slot: String) -> bool
func refresh_display() -> void
func toggle_visibility() -> void
```

### MapSelection接口
```gdscript
# 信号定义
signal node_selected(node_id: String)
signal node_hovered(node_id: String)
signal path_confirmed(start_node: String, end_node: String)
signal map_closed()
signal level_ready(level_data: Dictionary)

# 方法接口
func highlight_node(node_id: String) -> void
func unlock_node(node_id: String) -> void
func select_path(start_node: String, end_node: String) -> void
func confirm_selection() -> void
func close_map() -> void
```

## 7. 音频管理接口

### AudioManager接口
```gdscript
# 信号定义
signal music_changed(music_name: String)
signal sfx_played(sfx_name: String)

# 方法接口
func play_music(music_name: String, loop: bool = true) -> void
func play_sfx(sfx_name: String, volume_db: float = 0.0) -> void
func stop_music() -> void
func set_global_volume(volume_db: float) -> void
func set_music_volume(volume_db: float) -> void
func set_sfx_volume(volume_db: float) -> void
```

## 8. 数据结构定义

### 敌人数据结构
```gdscript
{
    "type": "goblin",           # 敌人类型
    "name": "哥布林战士",       # 显示名称
    "level": 1,                 # 等级
    "health": 30,               # 生命值
    "max_health": 30,           # 最大生命值
    "attack_power": 8,          # 攻击力
    "defense": 2,               # 防御力
    "speed": 50,                # 移动速度
    "exp_reward": 10,           # 经验奖励
    "drops": [                  # 掉落物品
        {
            "item_id": "health_potion",
            "chance": 0.3,
            "amount": 1
        }
    ]
}
```

### 装备数据结构
```gdscript
{
    "id": "iron_sword",         # 物品ID
    "name": "铁剑",             # 显示名称
    "type": "weapon",           # 物品类型
    "slot": "right_hand",       # 装备槽位
    "stats": {                  # 属性加成
        "attack_power": 5,
        "defense": 0,
        "health_bonus": 0
    },
    "rarity": "common",         # 稀有度
    "value": 50                 # 价值
}
```

### 关卡数据结构
```gdscript
{
    "level_id": "forest_01",    # 关卡ID
    "name": "森林入口",         # 关卡名称
    "tilemap_data": [],         # 地图数据
    "enemy_spawns": [           # 敌人生存点
        {
            "type": "goblin",
            "position": [100, 100],
            "quantity": 3
        }
    ],
    "item_spawns": [],          # 物品生存点
    "exit_position": [500, 300], # 出口位置
    "music": "forest_theme"     # 背景音乐
}
```