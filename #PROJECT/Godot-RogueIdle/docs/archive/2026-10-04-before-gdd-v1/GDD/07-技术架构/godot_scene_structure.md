# Godot Demo场景结构设计

## 主要场景结构

### 1. Main.tscn (主场景)
```
Main (Node)
├── GameData (Node) - 游戏数据管理器
├── AudioManager (Node) - 音频管理器
├── UIManager (CanvasLayer) - UI管理器
│   ├── HealthBar (TextureRect) - 生命值显示
│   ├── DamagePopup (Label) - 伤害弹出
│   └── PauseMenu (Control) - 暂停菜单
├── GameStateManager (Node) - 游戏状态管理器
├── PlayerSpawnPoint (Position2D) - 玩家出生点
├── CurrentLevel (Node2D) - 当前关卡容器
└── Camera2D (Camera2D) - 相机
```

### 2. Player.tscn (玩家角色)
```
Player (KinematicBody2D)
├── CollisionShape2D (CollisionShape2D) - 碰撞形状
├── Sprite (Sprite) - 角色精灵
├── AnimationPlayer (AnimationPlayer) - 动画播放器
├── Stats (Node) - 属性管理器
│   ├── Health (int) - 生命值
│   ├── MaxHealth (int) - 最大生命值
│   ├── AttackPower (int) - 攻击力
│   └── Defense (int) - 防御力
├── Weapon (Node2D) - 武器节点
└── AttackArea (Area2D) - 攻击区域
```

### 3. Enemy.tscn (敌人模板)
```
Enemy (KinematicBody2D)
├── CollisionShape2D (CollisionShape2D) - 碰撞形状
├── Sprite (Sprite) - 敌人精灵
├── AnimationPlayer (AnimationPlayer) - 动画播放器
├── Stats (Node) - 敌人属性管理器
│   ├── Health (int) - 生命值
│   ├── MaxHealth (int) - 最大生命值
│   ├── AttackPower (int) - 攻击力
│   └── Defense (int) - 防御力
├── DetectionArea (Area2D) - 检测区域
├── DropSystem (Node) - 掉落系统
└── AIController (Node) - AI控制器
```

### 4. Level.tscn (关卡模板)
```
Level (Node2D)
├── TileMap (TileMap) - 地图瓦片
├── SpawnPoints (Node) - 生成点组
│   ├── EnemySpawnPoint (Position2D) - 敌人生存点
│   └── ItemSpawnPoint (Position2D) - 物品生存点
├── Doors (Node) - 门节点组
├── Chests (Node) - 宝箱节点组
└── Exit (Area2D) - 出口区域
```

### 5. UI相关场景

#### BattleHUD.tscn (战斗界面)
```
BattleHUD (Control)
├── HealthContainer (HBoxContainer)
│   ├── HealthIcon (TextureRect) - 生命图标
│   └── HealthBar (TextureProgress) - 生命条
├── DamagePopups (Node) - 伤害弹出容器
└── ActionButtons (HBoxContainer) - 操作按钮
```

#### Inventory.tscn (背包界面)
```
Inventory (Panel) - 背包面板
├── ItemGrid (GridContainer) - 物品网格
├── SelectedItemInfo (VBoxContainer) - 选中物品信息
└── CloseButton (Button) - 关闭按钮
```

#### MapSelection.tscn (地图选择界面)
```
MapSelection (Control)
├── MapNodes (Node) - 地图节点组
│   ├── NodeA (Control) - 节点A
│   ├── NodeB (Control) - 节点B
│   └── NodeC (Control) - 节点C
├── PathLines (Node2D) - 连接线
└── ConfirmButton (Button) - 确认按钮
```