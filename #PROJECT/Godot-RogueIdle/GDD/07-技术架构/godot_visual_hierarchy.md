# Godot Demo可视化场景层次结构

## 顶层场景结构

```
Main Scene (Main.tscn)
│
├── GameData (Node)
│   ├── PlayerStats (Dictionary)
│   ├── EnemyDatabase (Array)
│   └── GameSettings (Dictionary)
│
├── AudioManager (Node)
│   ├── MusicPlayer (AudioStreamPlayer)
│   ├── SFXPlayer (AudioStreamPlayer)
│   └── SoundBank (Dictionary)
│
├── UIManager (CanvasLayer)
│   ├── BattleHUD (BattleHUD.tscn)
│   │   ├── HealthContainer (HBoxContainer)
│   │   │   ├── HealthIcon (TextureRect)
│   │   │   └── HealthBar (TextureProgress)
│   │   ├── DamagePopups (Node)
│   │   └── ActionButtons (HBoxContainer)
│   ├── Inventory (Inventory.tscn)
│   │   ├── ItemGrid (GridContainer)
│   │   ├── SelectedItemInfo (VBoxContainer)
│   │   └── CloseButton (Button)
│   ├── MapSelection (MapSelection.tscn)
│   │   ├── MapNodes (Node)
│   │   │   ├── NodeA (Control)
│   │   │   ├── NodeB (Control)
│   │   │   └── NodeC (Control)
│   │   ├── PathLines (Node2D)
│   │   └── ConfirmButton (Button)
│   ├── HealthBar (TextureRect)
│   ├── DamagePopup (Label)
│   └── PauseMenu (Control)
│
├── GameStateManager (Node)
│   ├── CurrentState (String) - "MENU", "PLAYING", "PAUSED", "GAME_OVER"
│   ├── CurrentLevel (String)
│   ├── PlayerLevel (int)
│   └── Score (int)
│
├── PlayerSpawnPoint (Position2D)
│
├── CurrentLevel (Level.tscn)
│   ├── TileMap (TileMap)
│   ├── SpawnPoints (Node)
│   │   ├── EnemySpawnPoint1 (Position2D)
│   │   ├── EnemySpawnPoint2 (Position2D)
│   │   └── ItemSpawnPoint (Position2D)
│   ├── Doors (Node)
│   │   ├── Door1 (Door.tscn)
│   │   └── Door2 (Door.tscn)
│   ├── Chests (Node)
│   │   └── Chest1 (Chest.tscn)
│   ├── Exit (Area2D)
│   ├── Player (Player.tscn)
│   │   ├── CollisionShape2D (CollisionShape2D)
│   │   ├── Sprite (Sprite)
│   │   ├── AnimationPlayer (AnimationPlayer)
│   │   ├── Stats (Node)
│   │   │   ├── Health (int)
│   │   │   ├── MaxHealth (int)
│   │   │   ├── AttackPower (int)
│   │   │   └── Defense (int)
│   │   ├── Weapon (Node2D)
│   │   └── AttackArea (Area2D)
│   ├── Enemies (Node)
│   │   ├── Enemy1 (Enemy.tscn)
│   │   │   ├── CollisionShape2D (CollisionShape2D)
│   │   │   ├── Sprite (Sprite)
│   │   │   ├── AnimationPlayer (AnimationPlayer)
│   │   │   ├── Stats (Node)
│   │   │   │   ├── Health (int)
│   │   │   │   ├── MaxHealth (int)
│   │   │   │   ├── AttackPower (int)
│   │   │   │   └── Defense (int)
│   │   │   ├── DetectionArea (Area2D)
│   │   │   ├── DropSystem (Node)
│   │   │   └── AIController (Node)
│   │   └── Enemy2 (Enemy.tscn)
│   └── Items (Node)
│       └── Item1 (Item.tscn)
│
└── Camera2D (Camera2D)
```

## 信号流向示意图

```
输入系统
    ↓
Player (移动/攻击)
    ↓
Enemy (检测/响应)
    ↓
战斗系统 (伤害计算)
    ↓
UI系统 (显示血量/伤害数字)
    ↓
游戏状态管理 (判断胜负)
    ↓
关卡管理 (切换场景/生成敌人)
    ↓
音频系统 (播放音效)
```

## 场景生命周期管理

### 场景加载顺序
1. Main.tscn (初始化全局管理器)
2. GameData (载入游戏数据)
3. AudioManager (设置音频系统)
4. CurrentLevel (载入当前关卡)
5. Player (实例化玩家角色)
6. UI (显示游戏界面)

### 场景卸载顺序
1. UI (隐藏界面)
2. Player (保存玩家数据)
3. CurrentLevel (清理关卡内容)
4. 清理临时对象 (敌人、道具等)
5. 保留全局管理器 (GameData, AudioManager等)

## 常用节点组 (Groups)

### "enemies" 组
- 包含所有敌人节点
- 用于批量处理敌人逻辑

### "items" 组
- 包含所有可拾取物品
- 用于碰撞检测和拾取逻辑

### "doors" 组
- 包含所有门节点
- 用于统一控制门的开关逻辑

### "player_attacks" 组
- 包含玩家所有攻击节点
- 用于处理攻击碰撞逻辑

### "interactive_objects" 组
- 包含所有可交互对象（宝箱、开关等）
- 用于统一处理交互逻辑