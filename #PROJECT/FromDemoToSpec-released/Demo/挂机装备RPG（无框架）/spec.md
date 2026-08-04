# 无尽道途 v2 —— 技术规格说明书

> **对应原型**：`index-v2.html`（804行单文件）
> **对应策划案**：`05-design-doc-endless-path-v2.md`
> **技术栈**：纯前端 - HTML5 + CSS3 + Vanilla JavaScript（ES6+）
> **运行时**：现代浏览器（Chrome/Firefox/Safari/Edge 最新两版）
> **文档状态**：[x] 草稿 / [ ] 评审中

---

## 目录

1. [架构概览](#1-架构概览)
2. [数据模型](#2-数据模型)
3. [宝箱系统](#3-宝箱系统)
4. [装备系统](#4-装备系统)
5. [战斗系统](#5-战斗系统)
6. [UI渲染系统](#6-ui渲染系统)
7. [动效系统](#7-动效系统)
8. [存储系统](#8-存储系统)
9. [游戏主循环](#9-游戏主循环)
10. [数值配置表](#10-数值配置表)
11. [接口与事件](#11-接口与事件)
12. [边界条件与容错](#12-边界条件与容错)

---

## 1. 架构概览

### 1.1 文件结构

```
原型验证（无框架）/
├── index-v2.html          # 游戏主文件（单文件包含全部HTML/CSS/JS）
├── 05-design-doc-...      # 策划文档
└── spec-v2.md             # 本文档
```

### 1.2 运行时架构

```
┌─────────────────────────────────────────────┐
│                  Game Loop                    │
│         requestAnimationFrame @ ~60fps       │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Chest    │  │  Battle   │  │   UI     │  │
│  │  Timer    │  │  Engine   │  │  Render  │  │
│  │ (3s/5s)   │  │ (tick)    │  │ (60fps)  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │        │
│       └──────┬───────┘              │        │
│              │                      │        │
│       ┌──────▼──────────────────────▼─────┐  │
│       │         GameState (G)              │  │
│       │  chests / equipment / gold / ...   │  │
│       └────────────────┬──────────────────┘  │
│                        │                      │
│       ┌────────────────▼──────────────────┐  │
│       │      localStorage (JSON)           │  │
│       │      自动保存 / 启动加载            │  │
│       └───────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### 1.3 模块依赖

```
Game Loop
  ├── Chest System  (宝箱生产 / 自动开启)
  │     └── Equipment Generator (装备生成)
  │           └── Affix Generator (词条生成)
  ├── Battle Engine (战斗逻辑)
  │     └── Damage Calculator (伤害计算)
  │           └── Player Stats (属性汇总)
  ├── UI Renderer (渲染引擎)
  │     ├── Top Bar (顶栏)
  │     ├── Equip Panel (装备栏)
  │     ├── Center Area (宝箱区)
  │     ├── Right Panel (属性面板)
  │     └── Bottom Bar (底栏)
  ├── Compare Modal (对比弹窗)
  ├── Battle Overlay (战斗界面)
  └── FX System (动效系统)
        ├── Damage Numbers (伤害数字)
        ├── Gold Fly (金币飘字)
        ├── Drop Beam (光柱)
        ├── Full Flash (全屏闪光)
        └── Screen Shake (震屏)
```

---

## 2. 数据模型

### 2.1 游戏主状态 `G`

```javascript
G = {
  // === 宝箱系统 ===
  chests: number,          // 当前宝箱数量 (0-100)
  chestTimer: number,      // 生产计时器 (ms)
  chestOpenTimer: number,  // 自动开启计时器 (ms)
  autoOpen: boolean,       // 自动开箱开关
  comparing: boolean,      // 是否正在对比装备
  pendingEq: object|null,  // 待确认的装备对象
  totalOpened: number,     // 总开箱次数

  // === 装备系统 ===
  equipment: {},           // { slot: [equipmentObj, ...] } 历史装备（预留）
  equipped: {},            // { slot: equipmentObj } 当前装备
  equipLevel: number,      // 全局装备等级 (≥1)
  gold: number,            // 金币数量

  // === 关卡系统 ===
  stage: number,           // 当前关卡 (≥1)
  maxStage: number,        // 历史最高关卡

  // === 战斗系统 ===
  battle: {
    active: boolean,
    playerHp: number,
    playerMaxHp: number,
    enemyHp: number,
    enemyMaxHp: number,
    plyAtkTimer: number,     // 玩家攻击计时器
    enemyAtkTimer: number,   // 敌人攻击计时器
    totalDmg: number,        // 累计造成伤害
    totalTaken: number,      // 累计承受伤害
    totalHeal: number,       // 累计治疗量
    critCount: number,       // 暴击次数
    ccTime: number,          // 累计控制时长 (ms)
    duration: number,        // 战斗时长 (s)
    startTime: number,       // 战斗开始时间戳 (ms)
    plyCcTimer: number,      // 玩家被控剩余时间
    enemyCcTimer: number,    // 敌人被控剩余时间
    enemy: {                 // 本场敌人快照
      hp, maxHp, atk, def,
      critRate, critDmg, atkSpeed,
      dodge, name
    },
    stats: {}                // 本场玩家属性快照
  },

  // === 持久化 ===
  lastSave: number          // 最后存档时间戳
}
```

### 2.2 装备对象 `Equipment`

```javascript
{
  id: string,              // 唯一ID (timestamp + random)
  slot: string,            // 槽位: SLOTS 之一
  name: string,            // 显示名称 (品质前缀 + 槽位名)
  quality: number,         // 品质索引 0-9
  affixes: [               // 词条数组
    { type: string, value: number }
  ],
  combatPower: number      // 战力 (由词条加权求和)
}
```

### 2.3 敌人对象 `Enemy`

```javascript
{
  hp: number,
  maxHp: number,
  atk: number,
  def: number,
  critRate: number,        // 小数 (e.g., 0.05 = 5%)
  critDmg: number,         // 小数 (e.g., 1.5 = 150%)
  atkSpeed: number,        // 每秒攻击次数
  dodge: number,           // 小数 (e.g., 0.05 = 5%)
  name: string
}
```

### 2.4 玩家属性汇总 `PlayerStats`

```javascript
// 由 getPlayerStats() 动态计算
{
  attack: number,           // = 装备攻击合计 + 10*equipLevel
  hp: number,               // = 装备HP合计 + 100*equipLevel
  defense: number,          // = 装备防御合计 + 5*equipLevel
  armorPen: number,
  critRate: number,         // 百分比单位 (e.g., 5 = 5%)
  critResist: number,
  critDamage: number,       // 百分比单位
  hit: number,
  dodge: number,
  dmgBonus: number,
  dmgReduce: number,
  fireMastery: number,
  waterMastery: number,
  earthMastery: number,
  windMastery: number,
  fireResist: number,
  waterResist: number,
  earthResist: number,
  windResist: number,
  healEffect: number,
  counterRate: number,
  lifeSteal: number,
  tenacity: number,
  atkSpeed: number          // 小数 (e.g., 0.5)
}
```

---

## 3. 宝箱系统

### 3.1 生产逻辑

```
每个 gameLoop tick:
  IF NOT comparing:
    chestTimer += deltaTime(ms)
    WHILE chestTimer >= 3000 AND chests < 100:
      chestTimer -= 3000
      chests += 1
```

- **生产间隔**：3000ms 固定
- **上限**：100个
- **暂停条件**：`comparing = true`（装备对比弹窗打开时）

### 3.2 自动开启逻辑

```
每个 gameLoop tick:
  IF autoOpen AND chests > 0 AND NOT comparing:
    chestOpenTimer += deltaTime(ms)
    IF chestOpenTimer >= 5000:
      chestOpenTimer = 0
      openChest()
```

- **开启间隔**：5000ms
- **复位条件**：对比弹窗关闭时 `chestOpenTimer = 0`
- **开关状态**：`autoOpen` 布尔值，通过底栏按钮切换

### 3.3 手动开启逻辑

```
onChestClick(event):
  IF chests <= 0 OR comparing: RETURN
  openChest()
  spawn click ripple at event position
```

### 3.4 开箱处理 `openChest()`

```
openChest():
  chests -= 1
  totalOpened += 1
  播放宝箱弹跳动画 (chestPop 500ms)

  slot = SLOTS[random(0, 12)]
  eq = genEquipment(slot)

  IF NOT equipped[slot] OR eq.combatPower > equipped[slot].combatPower:
    comparing = true
    pendingEq = eq
    showCompare(eq, equipped[slot], slot)
    spawnEquipBeam(slot, eq.quality)
    spawnFullFlash(qualityColor, quality >= 5)
    triggerShake()
  ELSE:
    gold += floor(eq.combatPower * 0.5)
    spawnGoldFly(chestPosition, goldAmount)
```

---

## 4. 装备系统

### 4.1 装备生成 `genEquipment(slot)`

```
genEquipment(slot):
  qualityIdx = rollQuality()
  primaryAffix = SLOT_PRIMARY[slot]
  [minAffix, maxAffix] = Q_AFFIX_COUNT[qualityIdx]
  affixCount = minAffix + random(0, maxAffix - minAffix)

  affixes = []
  usedTypes = Set()

  // 1. 主词条（必定包含，2.8倍数值加成）
  affixes.push({ type: primaryAffix, value: genAffixValue(primaryAffix, qualityIdx, isPrimary=true) })
  usedTypes.add(primaryAffix)

  // 2. 从剩余23种词条池不放回抽取
  pool = ALL_AFFIXES.filter(a => a !== primaryAffix)
  FOR i = 1 TO affixCount - 1:
    idx = random(0, pool.length - 1)
    type = pool.splice(idx, 1)[0]
    affixes.push({ type, value: genAffixValue(type, qualityIdx, isPrimary=false) })

  // 3. 计算战力
  cp = 0
  FOR EACH affix:
    IF AFFIX_IS_PCT[type]:  cp += value * 8
    ELSE IF type === 'atkSpeed': cp += value * 40
    ELSE IF type === 'hp': cp += value * 0.2
    ELSE: cp += value * 1.0
  cp = floor(cp)

  // 4. 生成名称
  name = qualityIdx > 0 ? prefixes[qualityIdx] + SLOT_NAMES[slot] : SLOT_NAMES[slot]

  RETURN { id, slot, name, quality: qualityIdx, affixes, combatPower: cp }
```

### 4.2 品质随机 `rollQuality()`

使用**权重轮盘赌**算法：
```
rollQuality():
  totalWeight = SUM(Q_WEIGHTS) = 100
  roll = random() * totalWeight
  cumulative = 0
  FOR i = 0 TO 9:
    cumulative += Q_WEIGHTS[i]
    IF roll <= cumulative: RETURN i
  RETURN 0
```

### 4.3 词条数值生成 `genAffixValue(type, qualityIdx, isPrimary)`

```
genAffixValue(type, qualityIdx, isPrimary):
  qm = Q_AFFIX_MULT[qualityIdx]   // 品质倍率

  IF AFFIX_IS_PCT[type]:
    // 百分比类词条
    base = (2 + random() * 5) * qm * (isPrimary ? 2.8 : 1)
    IF type === 'critRate':     base *= 0.5
    IF type === 'critDamage':   base *= 0.8
    IF type === 'counterRate':  base *= 0.35
    IF type === 'lifeSteal':    base *= 0.3
    IF type IN [dmgBonus, dmgReduce]: base *= 0.4
    IF type IN [hit, dodge]:    base *= 0.45
  ELSE:
    // 固定值类词条
    base = floor((15 + random() * 35) * qm * (isPrimary ? 2.8 : 1))
    IF type === 'hp':        base *= 3
    IF type === 'atkSpeed':  base = max(0.3, base * 0.02)

  // atkSpeed 保留1位小数
  IF type === 'atkSpeed':
    RETURN max(0.1, +(base * (0.85 + random() * 0.3)).toFixed(1))
  ELSE:
    RETURN max(1, floor(base * (0.85 + random() * 0.3)))
```

---

## 5. 战斗系统

### 5.1 战斗初始化 `startBattle()`

```
startBattle():
  IF battle.active OR comparing: RETURN

  stats = getPlayerStats()
  enemy = getStageEnemy(stage)

  battle = {
    active: true,
    playerHp: stats.hp,
    playerMaxHp: stats.hp,
    enemyHp: enemy.maxHp,
    enemyMaxHp: enemy.maxHp,
    plyAtkTimer: 0,
    enemyAtkTimer: 0,
    totalDmg: 0,
    totalTaken: 0,
    totalHeal: 0,
    critCount: 0,
    ccTime: 0,
    duration: 0,
    startTime: Date.now(),
    plyCcTimer: 0,
    enemyCcTimer: 0,
    enemy: enemy,
    stats: stats
  }

  显示战斗界面
  隐藏战后统计面板
```

### 5.2 战斗Tick逻辑

```
每个 gameLoop tick (dt = elapsed ms):

  IF NOT battle.active: SKIP

  b = battle

  // === 控制计时器衰减 ===
  IF b.enemyCcTimer > 0: b.enemyCcTimer = max(0, b.enemyCcTimer - dt)
  IF b.plyCcTimer > 0:   b.plyCcTimer = max(0, b.plyCcTimer - dt)

  // === 玩家攻击 ===
  pInterval = max(60, floor(1000 / (1 + b.stats.atkSpeed)))
  b.plyAtkTimer += dt
  WHILE b.plyAtkTimer >= pInterval AND b.enemyHp > 0 AND b.playerHp > 0:
    b.plyAtkTimer -= pInterval
    { dmg, isCrit } = calcPlayerDmg(b.stats)
    b.enemyHp = max(0, b.enemyHp - dmg)
    b.totalDmg += dmg

    // 吸血
    IF b.stats.lifeSteal:
      heal = floor(dmg * b.stats.lifeSteal / 100)
      b.playerHp = min(b.playerMaxHp, b.playerHp + heal)
      b.totalHeal += heal

    // 反击
    IF NOT isCrit AND random() < b.stats.counterRate / 100:
      counterDmg = floor(dmg * 0.5)
      b.enemyHp = max(0, b.enemyHp - counterDmg)
      b.totalDmg += counterDmg

    // 眩晕判定
    IF b.enemyCcTimer <= 0 AND random() < 0.08 * (1 + b.stats.tenacity / 200):
      b.enemyCcTimer = 500
      b.ccTime += 500

    // 伤害数字特效
    IF b.enemyHp <= 0: spawnDmgNum(cx, cy, dmg, 'kill')
    ELSE IF isCrit:    spawnDmgNum(cx, cy, dmg, 'crit')
    ELSE:              spawnDmgNum(cx, cy, dmg, 'normal')

  // === 敌人攻击（仅在未被眩晕时） ===
  eInterval = max(80, floor(1000 / b.enemy.atkSpeed))
  b.enemyAtkTimer += dt
  WHILE b.enemyAtkTimer >= eInterval AND b.enemyHp > 0 AND b.playerHp > 0 AND b.enemyCcTimer <= 0:
    b.enemyAtkTimer -= eInterval
    { dmg, dodged } = calcEnemyDmg(b.stats)
    IF NOT dodged:
      b.playerHp = max(0, b.playerHp - dmg)
      b.totalTaken += dmg
      spawnDmgNum(px, py, dmg, 'normal')
    // (闪避时不显示伤害数字)

  // === 结束判定 ===
  updateBattleHp()
  IF b.playerHp <= 0:
    triggerShake()
    endBattle(false)
  ELSE IF b.enemyHp <= 0:
    triggerShake()
    endBattle(true)
  ELSE IF Date.now() - b.startTime > 60000:
    // 超时：按血量百分比判胜负
    IF b.playerHp/b.playerMaxHp > b.enemyHp/b.enemyMaxHp:
      endBattle(true)
    ELSE:
      endBattle(false)
```

### 5.3 战斗结束 `endBattle(won)`

```
endBattle(won):
  battle.active = false
  battle.duration = (Date.now() - battle.startTime) / 1000  // 转秒

  IF won:
    IF stage >= maxStage: maxStage = stage + 1
    stage += 1
    gold += floor(stage * 10)

  显示战后统计面板
  结果文字: 胜利(金色) / 失败(红色)
  显示6项统计
  显示返回按钮
  renderAll() + save()
```

### 5.4 战斗结束后的状态保证

- `stage` 递增（胜利）或不变（失败）
- `maxStage` 跟踪历史最高
- 金币奖励仅在胜利时发放
- 关闭战斗界面后恢复宝箱系统正常运行

---

## 6. UI渲染系统

### 6.1 渲染触发

`renderAll()` 在以下时机被调用：
- 每个 `gameLoop` tick（约60fps）
- `openChest()` 完成后
- `equipPending()` / `sellPending()` 完成后
- `upgradeEquipLevel()` 完成后
- `toggleAutoOpen()` 完成后
- `closeBattle()` 完成后
- `resetGame()` 完成后
- `closeOffline()` (离线收益，v2暂未实现) 完成后

### 6.2 关键UI更新项

| UI元素 | 更新逻辑 | 格式 |
|--------|----------|------|
| 宝箱数量 | `G.chests` | 整数 0-100 |
| 金币 | `G.gold` | fmtNum (K/M/B/T) |
| 装备等级 | `G.equipLevel` | 整数 |
| 战力 | `getTotalCombatPower()` | fmtNum |
| 当前关卡 | `G.stage` | 整数 |
| 最高关卡 | `G.maxStage` | 整数 |
| 宝箱光晕 | chests>0 → .ready; chests≥100 → .full | |
| 宝箱提示文字 | comparing ? 发现更好 : (chests≥100 ? 满 : (chests>0 ? 点开 : 生产)) | |
| 开箱进度条 | `chestOpenTimer / 5000 * 100%` | |
| 装备列表 | 遍历SLOTS，渲染每件装备/空槽 | 动态HTML |
| 属性总览 | `getPlayerStats()` 遍历渲染 | 动态HTML |
| 关卡推荐战力 | `getStageReqPower(G.stage)` | fmtNum |
| 升级按钮 | 当前等级→目标等级 + 费用 | |

### 6.3 装备列表渲染

```
FOR EACH slot IN SLOTS:
  IF equipped[slot]:
    左彩色边框 + 图标 + 名称(品质色) + 品质标签 + 词条缩写(前3条) + 战力
  ELSE:
    半透明 + 图标 + 槽位名 + "-"
```

### 6.4 对比弹窗渲染

```
showCompare(newEq, current, slot):
  左栏: 当前装备
    IF current: 品质色名称 + 每个词条(数值, 增减箭头)
    ELSE: "空"
  右栏: 新装备 (边框随品质变色)
    品质色名称 + 品质标签 + 每个词条(数值, 增减箭头)
  底部: 装备按钮(金色) + 出售按钮(+N金币)
```

词条对比逻辑：
- 新 > 旧 → 绿色(class="better") + ▲
- 新 < 旧 → 红色(class="worse") + ▼
- 新 = 旧 → 无class无箭头
- 旧无此词条 → 新栏显示、旧栏不显示

---

## 7. 动效系统

### 7.1 动效类型与参数

| 动效 | 类名 | 动画 | 时长 | 帧率无关 |
|------|------|------|------|----------|
| 伤害数字(普) | .dmg-num.normal | floatUp: y+100, scale 0.5→1.2→0.8 | 800ms | 纯CSS |
| 伤害数字(暴) | .dmg-num.crit | floatUp + text-shadow glow | 800ms | 纯CSS |
| 伤害数字(杀) | .dmg-num.kill | floatUp + strong glow | 800ms | 纯CSS |
| 宝箱弹跳 | .chest-open | chestPop: scale 1→1.3→0.9→1 | 500ms | 纯CSS |
| 宝箱光晕(有) | .ready | drop-shadow constant | 持续 | 纯CSS |
| 宝箱光晕(满) | .full | chestGlow 脉冲 | 1.5s循环 | 纯CSS |
| 点击涟漪 | .click-ripple | ripOut: 扩散+消失 | 500ms | JS动态创建 |
| 品质光柱 | .drop-beam | beamDrop: scaleY展开 | 600ms | JS动态创建 |
| 全屏闪光 | .full-flash | flashBang: 淡出 | 500/700ms | JS动态创建 |
| 震屏 | .shake | 水平抖动±8px | 300ms | CSS class |
| 金币飘字 | .gold-fly | gf: Y位移+淡出 | 900ms | JS动态创建 |

### 7.2 动效触发条件

| 触发条件 | 动效 |
|----------|------|
| 手动点击宝箱 | 点击涟漪 |
| 开箱（任意方式） | 宝箱弹跳 |
| 开箱获更好装备 | 品质光柱 + 震屏 + (品质≥史诗)全屏闪光 |
| 开箱获传说+ | 强闪光(700ms) |
| 战斗普通攻击 | 白色伤害数字 |
| 战斗暴击 | 金色大号伤害数字 |
| 战斗击杀 | 红色超大号伤害数字 + 震屏 |
| 装备出售/关卡获胜 | 金币飘字 |

### 7.3 动效性能约束

- 伤害数字DOM元素上限：100个（超出后移除最早的）
  - **当前实现**：未做限制（单场战斗数字数量可控，800ms自动清除）
- 粒子效果上限：50个
  - **当前实现**：未使用粒子（v1的粒子在v2中未启用）
- 所有动画使用CSS animation/transition，不依赖JS动画帧
- DOM回收：setTimeout自动移除

---

## 8. 存储系统

### 8.1 存储方案

- **存储方式**：`localStorage`
- **Key**：`"endless_path_v2"`
- **格式**：JSON 字符串
- **触发时机**：每次 `save()` 调用时写入

### 8.2 保存时机

```
save() 调用点:
  - openChest() 完成后
  - equipPending() / sellPending() 完成后
  - upgradeEquipLevel() 完成后
  - endBattle() 完成后
  - toggleAutoOpen() 完成后
  - resetGame() 完成后
  - closeOffline() 完成后
```

### 8.3 加载逻辑

```
load():
  raw = localStorage.getItem("endless_path_v2")
  IF NOT raw: RETURN false

  saved = JSON.parse(raw)
  G = merge(createState(), saved)
  // 深度merge子对象
  G.equipment = saved.equipment || {}
  G.equipped = saved.equipped || {}
  G.battle = merge(createState().battle, saved.battle || {})

  // 数据完整性保证
  IF G.chests === undefined: G.chests = 0
  FOR EACH slot IN SLOTS:
    IF NOT G.equipped[slot]: G.equipped[slot] = null
  IF G.equipLevel < 1: G.equipLevel = 1
  IF G.stage < 1: G.stage = 1
  IF G.maxStage < 1: G.maxStage = 1

  RETURN true
```

### 8.4 重置逻辑

```
resetGame():
  IF NOT confirm("确定重置所有数据？"): RETURN
  localStorage.removeItem("endless_path_v2")
  G = createState()
  renderAll()
  save()
```

---

## 9. 游戏主循环

### 9.1 循环结构

```javascript
let lastTick = 0;

function loop(timestamp) {
  if (!lastTick) lastTick = timestamp;
  let dt = timestamp - lastTick;
  if (dt > 300) dt = 300;  // 防止切tab后的大delta
  lastTick = timestamp;

  // Phase 1: 宝箱系统
  updateChestSystem(dt);

  // Phase 2: 战斗系统
  updateBattle(dt);

  // Phase 3: 渲染
  renderAll();

  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);
```

### 9.2 Delta Time 保护

- `dt` 最大值限制：300ms
- 防止浏览器切到后台后切回时的大量计算
- 宝箱生产和战斗都使用累积式计时器，短时间内的多tick也能正确累加

### 9.3 暂停状态

当 `comparing = true` 时：
- 宝箱生产暂停
- 自动开箱暂停
- 手动开箱被拦截
- 战斗可正常进行（理论上不会同时发生）

---

## 10. 数值配置表

### 10.1 品质配置

| idx | 名称 | 权重 | 词条数[min,max] | 数值倍率 | 颜色 |
|-----|------|------|-----------------|----------|------|
| 0 | 普通 | 30 | [1,1] | 1.0x | #9d9d9d |
| 1 | 常见 | 25 | [1,2] | 1.3x | #4ae04a |
| 2 | 稀有 | 18 | [2,2] | 1.6x | #4a8af0 |
| 3 | 史诗 | 12 | [2,3] | 2.0x | #c04af0 |
| 4 | 传说 | 7 | [3,3] | 2.5x | #f08030 |
| 5 | 不朽 | 4 | [3,4] | 3.0x | #e04040 |
| 6 | 闪曜 | 2 | [4,4] | 3.6x | #888888 |
| 7 | 完美 | 1.2 | [4,5] | 4.2x | #fafafa |
| 8 | 传世 | 0.6 | [5,5] | 5.0x | #ffd700 |
| 9 | 至尊 | 0.2 | [5,6] | 6.0x | 彩虹 #ff4060→#4a8af0 |

### 10.2 槽位与主词条映射

| 槽位 | 主词条 | 英文key |
|------|--------|---------|
| 武器 | 攻击力 | attack |
| 帽子 | 生命值 | hp |
| 面具 | 暴击率 | critRate |
| 耳环 | 治疗效果 | healEffect |
| 项链 | 伤害加成 | dmgBonus |
| 衣服 | 防御力 | defense |
| 裤子 | 生命值 | hp |
| 护肩 | 防御力 | defense |
| 护膝 | 闪避 | dodge |
| 手套 | 攻击速度 | atkSpeed |
| 鞋子 | 闪避 | dodge |
| 披风 | 伤害减免 | dmgReduce |
| 腰带 | 生命值 | hp |

### 10.3 关卡敌人数值（第N关）

| 参数 | 公式 |
|------|------|
| HP | floor(100 × 1.18^(N-1)) |
| ATK | floor(15 × 1.14^(N-1)) |
| DEF | floor(5 × 1.10^(N-1)) |
| 暴击率 | 0.05 + N × 0.002 |
| 暴击伤害 | 1.5 + N × 0.01 |
| 攻速 | 1.0 + N × 0.01 |
| 闪避 | min(0.3, N × 0.005) |
| 推荐战力 | floor(50 × 1.16^(N-1)) |

### 10.4 装备升级花费

| 等级 | 花费（金币） | 累计花费 |
|------|-------------|----------|
| 1→2 | 100 | 100 |
| 2→3 | 150 | 250 |
| 3→4 | 225 | 475 |
| 4→5 | 337 | 812 |
| 5→6 | 506 | 1,318 |
| ... | 100 × 1.5^(L-1) | |
| 10→11 | 3,844 | ~9,400 |
| 20→21 | 221,683 | ~665,000 |

---

## 11. 接口与事件

### 11.1 全局函数（可供HTML onclick调用）

| 函数 | 参数 | 说明 |
|------|------|------|
| `onChestClick(event)` | MouseEvent | 手动开箱 |
| `equipPending()` | 无 | 确认装备替换 |
| `sellPending()` | 无 | 出售待确认装备 |
| `startBattle()` | 无 | 开始战斗 |
| `closeBattle()` | 无 | 关闭战斗界面 |
| `toggleAutoOpen()` | 无 | 切换自动开箱 |
| `upgradeEquipLevel()` | 无 | 升级装备等级 |
| `resetGame()` | 无 | 重置游戏 |

### 11.2 关键内部函数

| 函数 | 返回值 | 副作用 |
|------|--------|--------|
| `genEquipment(slot)` | Equipment | 无 |
| `getPlayerStats()` | PlayerStats | 无（纯计算） |
| `getTotalCombatPower()` | number | 无（纯计算） |
| `getStageEnemy(stage)` | Enemy | 无（纯计算） |
| `getStageReqPower(stage)` | number | 无（纯计算） |
| `getUpgradeCost()` | number | 无（纯计算） |
| `calcPlayerDmg(stats)` | {dmg, isCrit} | 修改 battle |
| `calcEnemyDmg(stats)` | {dmg, dodged} | 无 |
| `renderAll()` | void | 更新所有DOM |
| `save()` | void | 写localStorage |
| `load()` | boolean | 覆盖 G |

---

## 12. 边界条件与容错

### 12.1 数据边界

| 场景 | 处理方式 |
|------|----------|
| chests < 0 | openChest 开头检查，不可能 < 0 |
| chests > 100 | 生产循环检查上限 |
| equipLevel < 1 | createState 默认1，load时校验 |
| gold < 0 | 所有金币变动均为加法或确认后的减法，不会出现 |
| playerHp < 0 | 伤害计算时 Math.max(0, ...) |
| enemyHp < 0 | 伤害计算时 Math.max(0, ...) |
| critRate > 100% | 当前无上限限制，但百分比数值不会达到（最高品质+主词条+倍率 ≈ 6.0×2.8×0.5×5≈42%） |
| 战力为0 | 无装备时的合法状态 |
| equipLevel=0 | load时校验，强制 ≥ 1 |

### 12.2 状态机边界

| 场景 | 处理方式 |
|------|----------|
| 对比弹窗时点击宝箱 | `comparing` 拦截 |
| 对比弹窗时自动开箱 | game loop 检查 `!comparing` |
| 战斗中开箱 | 战斗为全屏遮罩，UI不可交互 |
| 战斗超时(60s) | 按HP百分比判胜负 |
| 敌人防御 > 玩家攻击 | 伤害最低为1 |
| localStorage 满 | try/catch 静默失败 |
| localStorage 数据损坏 | JSON.parse 异常 → load返回false，使用默认状态 |

### 12.3 UI边界

| 场景 | 处理方式 |
|------|----------|
| 装备栏滚动 | overflow-y: auto |
| 属性面板过长 | overflow-y: auto |
| 宝箱数字太大(>99) | 显示 "99+" 或实际数字（上限100） |
| 战力数字超长 | fmtNum 格式化为 K/M/B/T |
| 伤害数字超长 | fmtNum 格式化 |
| 弹窗宽度超限 | max-width: 95vw |

### 12.4 性能边界

| 场景 | 处理方式 |
|------|----------|
| deltaTime过大(切tab) | 上限300ms |
| 伤害数字累积过多 | 800ms自动移除 |
| 金币飘字累积 | 900ms自动移除 |
| 全屏闪光累积 | 500-700ms自动移除 |
| requestAnimationFrame未触发 | 无后备方案（现代浏览器均支持） |
