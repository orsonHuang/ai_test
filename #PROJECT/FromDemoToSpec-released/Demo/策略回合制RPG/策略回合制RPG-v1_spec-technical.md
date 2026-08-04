# 策略回合制RPG · 技术架构 Spec v0.1

> **模板用途**：由 AI 从 HTML 原型自动提取。面向"交付给程序员"场景。
> **来源原型**：`Demo/策略回合制RPG/策略回合制RPG-v1_mvp.html`
> **提取时间**：2026-06-15
> **人工复核**：[✓] 已复核
> **配套通用 spec**：[✓] 同目录 `策略回合制RPG-v1_spec.md`

---

## 一、概述

| 字段 | 内容 |
|------|------|
| 原型名称 | 策略回合制RPG |
| 原型类型 | 战斗 / 对抗类（回合制 RPG 小队战斗） |
| 文件规模 | ~1550 行，10 个主要模块 |
| 运行时长 | 单局约 2~5 分钟（3 波战斗） |
| 关键运行时假设 | 浏览器直接打开，单文件零依赖，无网络，无 localStorage，桌面端 |

---

## 二、架构概览

### 2.1 模块依赖图

> 来源：原型代码顶层模块划分

```
CONFIG ──────────────────────────────────────────┐
  │                                               │
  ▼                                               │
DATA_TEMPLATES (PARTY/ENEMY/WAVE_DEFS)            │
  │                                               │
  ▼                                               │
State ──── EventBus ──── Logic Layer ──── Render Layer
  │            │              │                  │
  │            │     ┌────────┼────────┐    ┌────┼────┐
  │            │     │        │        │    │    │    │
  │            ▼     ▼        ▼        ▼    ▼    ▼    ▼
  │        事件分发  TurnMgr  AI    Combat  ActionBar EnemyZone
  │                 │        │       │     PartyZone CmdPanel
  │                 │        │       │     FxZone   DebugPanel
  │                 │        │       │     TuningPanel
  │                 ▼        ▼       ▼
  │             checkBattleEnd  calcDamage
  │                              checkShieldHit
  │                              applyDamage/Heal/Buff
  │
  └─── 参数热调 (tuneParam ──→ CONFIG ──→ 下次计算)
```

依赖规则：
- Logic Layer **不引用** Render Layer 的任何函数或 DOM
- Render Layer **只读** State，不修改 State
- Logic ↔ Render 通过 EventBus 单向通信
- CONFIG 被 Logic 读取，被 Debug Panel 通过 tuneParam 修改

### 2.2 主循环类型

| 类型 | 是否采用 | 说明 |
|------|---------|------|
| setInterval（固定 tick） | [ ] | 不使用 |
| requestAnimationFrame（帧驱动） | [ ] | 不使用 |
| 事件驱动（无主循环） | [✓] | 回合制战斗，行动触发 → setTimeout 延迟 → 下一行动，无持续 tick |
| 混合 | [ ] | — |

说明：核心循环为 `nextTurn() → startActorTurn() → 玩家操作/AI 自动执行 → setTimeout(ANIM_DELAY) → nextTurn()`。无固定帧更新需求，渲染在每次 EventBus 事件后全量 refresh（renderAll）。

### 2.3 关键设计权衡

| 取舍点 | 选定方案 | 备选方案 | 理由 |
|--------|---------|---------|------|
| 渲染策略 | 每次事件后全量 renderAll | 增量 DOM 更新 | 回合制渲染频率低（~每 1-2s 一次），全量刷新简单可靠，性能无瓶颈 |
| 行动队模型 | 出队→执行→入队（环形队列） | 维护 fixed 轮次数组 + 索引指针 | 环形队列天然适配"暗影步拉条"功能，且死亡单位自动过滤 |
| BP 固定消耗技能 | UI 跳过 BP 选择直接进入目标选择 | 统一 BP 选择流程 | 蓄力斩固定 2BP 的特性需要减少一步操作，否则用户困惑 |
| 动画延迟 | 固定 setTimeout(CONFIG.ANIM_DELAY) | Promise/then 链 | 简单直接，回合制对异步链要求不高 |

---

## 三、数据模型

### 3.1 全局 State 对象

> 来源：原型代码 L593-L609（state 对象）

```js
const state = {
  phase: 'idle',        // string — 战斗阶段（见 §3.3 状态机）
  currentWave: 1,       // number — 当前波次（1~3）
  totalWaves: 3,        // number — 总波次数
  party: [],            // Character[] — 玩家角色数组（4 个）
  enemies: [],          // Enemy[] — 当前波次敌人数组
  actionQueue: [],       // Actor[] — 行动队环形队列
  currentActor: null,   // {type:'party'|'enemy', index:number}|null — 当前行动者
  turnCount: 0,         // number — 总行动计数
  selectedSkill: null,  // Skill|null — 当前选中技能
  bpToSpend: 0,         // number — 当前 BP 消耗选择
  commandStep: 'action', // string — 操作面板步骤：action|skill_select|bp_select|target_select
  log: []               // string[] — 日志缓冲（上限 50 条）
};
```

### 3.2 关键数据结构

| 名称 | 类型 | 用途 | 关键字段 |
|------|------|------|---------|
| `CONFIG` | const object | 可调参数集中管理 | DAMAGE_MULT, ENEMY_HP_MULT, BP_RATE, SP_REGEN, SHIELD_MULT, BREAK_DMG_BONUS 等 |
| `PARTY_TEMPLATES` | const array[4] | 角色模板（仅初始化时克隆） | id, name, hp, sp, atk, def, spd, atkType, skills[] |
| `ENEMY_TEMPLATES` | const object | 敌人模板（按 id 索引） | wolf, mage, elite 各包含 hp/atk/def/spd/weaknesses[]/shield/aiType |
| `WAVE_DEFS` | const array[3] | 波次敌人组合 | 每波为 Enemy template 引用数组 |
| `Character` (运行时) | object | 玩家角色实例 | id, name, hp/maxHp, sp/maxSp, atk, def, spd, bp, buffs[], isGuarding, isDead, skills[] |
| `Enemy` (运行时) | object | 敌人实例 | id, name, hp/maxHp, atk, def, spd, weaknesses[], shield/maxShield, isBroken, buffs[], isDead, chargeCountdown |
| `Skill` | object | 技能定义 | name, type, target, multiplier, spCost, bpCost, desc |
| `Actor` | object | 行动队条目 | {type:'party'\|'enemy', index:number, spd:number, name:string} |

### 3.3 状态机定义

> 来源：原型代码 phase 字段 + checkBattleEnd / nextTurn / startBattle 等函数

```
                    ┌─────────┐
        resetGame → │  idle   │ ← resetGame
                    └────┬────┘
                  startBattle()
                         │
                         ▼
                   ┌───────────┐
                   │wave_intro │ ← continueAfterWave()
                   └─────┬─────┘
                 1.5s 后 buildActionQueue()
                         │
                         ▼
              ┌─────────────────────┐
         ┌───→│    player_turn      │←──┐
         │    └─────────┬───────────┘   │
         │    操作完成    │               │ setTimeout
         │    +ANIM_DELAY│               │ +ANIM_DELAY
         │              ▼               │
         │    ┌─────────────────────┐   │
         └────│    enemy_turn       │───┘
              └─────────┬───────────┘
               AI 执行后  │
              +ANIM_DELAY │
                         ▼
                   checkBattleEnd()
                    │    │       │
           全灭敌方  │    │全灭己方│ 否（继续）
                    ▼    ▼       │
           ┌──────────┐ ┌──────┐ │
           │wave_clear│ │defeat│ │
           └────┬─────┘ └──────┘ │
         1.5s后  │               │
        最后一波?│               │
        ┌───┴───┐               │
        │ 否    │ 是            │
        ▼       ▼               │
   wave_intro  victory          │
                                │
               ┌────────────────┘
               │ 继续 nextTurn()
```

合法转换矩阵：

| from \ to | idle | wave_intro | player_turn | enemy_turn | wave_clear | victory | defeat |
|-----------|------|-----------|-------------|------------|------------|---------|--------|
| idle | — | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| wave_intro | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| player_turn | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ |
| enemy_turn | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ | ✓ |
| wave_clear | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| victory | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| defeat | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

---

## 四、核心算法（伪代码）

### 4.1 行动队构建（buildActionQueue）

> 来源：原型代码 L676-L705

```
function buildActionQueue():
  1. 遍历 state.party，收集存活角色 → Actor{type:'party', index, spd, name}
  2. 遍历 state.enemies，收集存活敌人 → Actor{type:'enemy', index, spd, name}
  3. 按 spd 降序排序
  4. 赋值 state.actionQueue

边界处理：
  - 若 party 全部阵亡 → 收集到的 Actor 数组仅含敌人
  - 若 enemies 全部阵亡 → 仅含角色（后续 checkBattleEnd 会拦截）
  - 排序稳定（spd 相同时先排入者优先）
```

### 4.2 伤害计算（calcDamage）

> 来源：原型代码 L736-L746

```
function calcDamage(attacker, defender, skillMultiplier, bpMultiplier, atkType):
  1. rawAtk = getEffectiveAtk(attacker)  // 含 buff 加成
  2. rawDef = getEffectiveDef(defender)   // 含 buff 加成
  3. breakBonus = defender.isBroken ? BREAK_DMG_BONUS : 1.0
  4. guardReduction = defender.isGuarding ? GUARD_REDUCTION : 1.0
  5. base = rawAtk × skillMultiplier × bpMultiplier × breakBonus - rawDef × DEF_FACTOR
  6. clamped = max(1, floor(base))
  7. final = floor(clamped × DAMAGE_MULT)
  8. return final

边界处理：
  - 负数伤害 → max(1, floor(base)) 保证最低 1 点
  - 破防加成 → BREAK_DMG_BONUS 默认为 1.5
  - 防御减伤 → GUARD_REDUCTION 默认为 0.5（受伤减半）
  - DAMAGE_MULT 在 floor 之后乘，避免浮点累积误差
```

### 4.3 弱点命中与破防（checkShieldHit）

> 来源：原型代码 L776-L788

```
function checkShieldHit(defender, atkType):
  1. if defender.isBroken → return false（已破防，不再扣盾）
  2. if defender.weaknesses 不存在 → return false
  3. if defender.weaknesses 包含 atkType:
     a. defender.shield = max(0, defender.shield - 1)
     b. if defender.shield === 0:
        - defender.isBroken = true
        - defender.brokenTurns = 1
        - defender.chargeCountdown = 0  // 打断蓄力
        - emit 'enemy_broken'
     c. return true
  4. return false

边界处理：
  - 非弱点命中不扣盾（直接 return false）
  - 盾值不会负数（max(0, ...)）
  - 破防即打断蓄力（chargeCountdown 归零）
```

### 4.4 玩家行动执行（executePlayerAction）

> 来源：原型代码 L808-L886

```
function executePlayerAction(actor, skill, bpSpent, targetActor):
  1. 获取 caster = getUnit(actor), target = getUnit(targetActor)
  2. 预检查：caster 非空、非死亡
  3. if skill:
     a. SP 检查：caster.sp < skill.spCost → 记录错误 + return false
     b. BP 检查：bpSpent > caster.bp → 记录错误 + return false
     c. 扣除 SP、BP
     d. bpMultiplier = 1.0 + bpSpent × 0.5  // 技能增幅
     e. 按 skill.type 分派：
        - 'heal': 调用 applyHeal，emit action_executed
        - 'buff': 调用 applyBuff（全体则循环），emit action_executed
        - 其他: 调用 calcDamage + applyDamage + checkShieldHit，emit action_executed
     f. 特殊处理：圣光自回 20% 伤害、暗影步拉队友
  4. else（普攻）:
     a. 扣除 BP
     b. hits = 1 + bpSpent
     c. 循环 hits 次：calcDamage + applyDamage + checkShieldHit（每段独立破防判定）
     d. emit action_executed（每段都 emit）
  5. return true

边界处理：
  - SP/BP 双检查（UI 层 disabled + 逻辑层二次守卫）
  - 普攻多段攻击，每段独立判定破防 → 普攻 BP 增幅是主要的快速破防手段
  - 圣光自回基于实际伤害（非原始计算值）
```

### 4.5 敌人 AI（executeEnemyAction）

> 来源：原型代码 L888-L962

```
function executeEnemyAction(actor):
  1. 获取 enemy = getUnit(actor)
  2. if enemy.isBroken → 跳过回合，return
  3. if enemy.aiType === 'charger':
     a. if chargeCountdown > 0: chargeCountdown-- ; if 归零后 → 释放 2.0× 高伤（目标 HP 最低角色）；chargeCountdown = -1; return
     b. if chargeCountdown === 0: 开始蓄力，chargeCountdown = 3；自身 DEF↑30%·2回合；return
  4. if enemy.aiType === 'buffer' && 自身无 DEF↑ buff:
     → 施加 DEF↑30%·3回合；return
  5. 攻击：target = HP 最低角色；计算伤害 + applyDamage；emit action_executed

边界处理：
  - 被破防 → 无条件跳过（含蓄力被打断）
  - chargeCountdown 状态机：-1(可蓄力) → 3→2→1→0(释放)
  - buffer 类型仅在无buff时补buff，避免无限叠加
```

### 4.6 回合流转（nextTurn + startActorTurn）

> 来源：原型代码 L986-L1038

```
function nextTurn():
  1. if checkBattleEnd() → return（胜负/波次清除已被处理）
  2. 过滤 actionQueue 中的死亡单位
  3. actor = getNextActor()：从队首取出 + 重新入队尾
  4. if actor === null: buildActionQueue() 重建 → 再取；仍空则 checkBattleEnd()
  5. startActorTurn(actor)

function startActorTurn(actor):
  1. state.currentActor = actor
  2. state.turnCount++
  3. 重置 commandStep/selectedSkill/bpToSpend
  4. onTurnStart(actor) — BP 恢复、SP 恢复、buff 倒计时、破防倒计时
  5. if actor 是玩家角色: phase='player_turn', emit 'player_turn_start'
  6. else: phase='enemy_turn', emit 'enemy_turn_start'
     → setTimeout(executeEnemyAction, ENEMY_AI_DELAY)
     → setTimeout(nextTurn, ENEMY_AI_DELAY + ANIM_DELAY)

边界处理：
  - 行动者入队后死亡（如 AoE 溅射）→ 入队时重新过滤
  - buildActionQueue 重试仅一次（避免死循环）
  - setTimeout 链不中断（保证事件驱动的回合流转）
```

---

## 五、事件与接口

### 5.1 事件清单（EventBus）

> 来源：原型代码 L1489-L1537

| 事件名 | 触发时机 | 携带数据 | 监听方 |
|--------|---------|---------|--------|
| `action_executed` | 攻击/技能/治疗执行完毕 | `{caster, targets[], skill?, damage, heal, isBuff?, isHeal?, hitIndex?, totalHits?}` | renderAll + floating 数字动画 |
| `enemy_broken` | 敌人盾值归零 | `{enemy}` | BREAK 特效 + overlay |
| `unit_died` | 单位 HP≤0 | `{unit}` | renderAll |
| `wave_cleared` | 当前波次全灭 | `{wave}` | overlay 动画 + setTimeout → continueAfterWave |
| `wave_intro` | 波次登场 | `{wave}` | renderAll |
| `battle_end` | 胜利/失败 | `{result:'victory'\|'defeat'}` | overlay 动画 + 命令面板切换 |
| `battle_started` | startBattle() 调用 | `{}` | renderAll |
| `player_turn_start` | 玩家角色回合开始 | `{actor, unit}` | renderAll（激活操作面板） |
| `enemy_turn_start` | 敌人回合开始 | `{actor, unit}` | renderAll（禁用操作面板） |
| `game_reset` | resetGame() 调用 | `{}` | renderAll |
| `config_changed` | tuneParam 调用 | `{param, value}` | renderTuningPanel |
| `log_entry` | 日志写入 | `line:string` | 追加到 debugLog 面板 |

### 5.2 对外接口

> 来源：原型代码全局 window.* 函数

| 接口名 | 用途 | 参数 | 返回 |
|--------|------|------|------|
| `window.logEvent(msg)` | 全局日志 | `msg: string` | void |
| `startBattle()` | 开始战斗 | 无 | void |
| `resetGame()` | 重置游戏 | 无 | void |
| `tuneParam(param, value)` | 热调参数 | `param: string, value: number` | void |
| `onSelectAction(action)` | 操作面板：选择行动类型 | `'attack'\|'skill'` | void |
| `onSelectSkill(idx)` | 操作面板：选择技能 | `idx: number` | void |
| `onSelectBP(bp)` | 操作面板：选择 BP 档位 | `bp: number` | void |
| `onBack()` | 操作面板：返回上一步 | 无 | void |
| `playerDefend()` | 执行防御 | 无 | void |

---

## 六、存储方案

> 来源：原型代码 localStorage / sessionStorage 搜索

**无存储方案**。本原型为纯内存运行，刷新页面即丢失所有状态。

- 无 localStorage / sessionStorage / IndexedDB 调用
- 无存档/读档功能
- 转开发时建议补上：战斗中断存档（localStorage/SQLite）、战斗回放（action log 序列化）

---

## 七、性能预算

> 来源：原型代码显式上限保护 + 设计分析

| 性能维度 | 上限/预算 | 当前实现 |
|---------|----------|---------|
| 单帧渲染时间 | 不适用（无持续帧循环） | 每次 renderAll 约 2~5ms（全量 innerHTML 重绘，8~10 张 unit card） |
| DOM 节点总数 | < 200 | ~150（4 角色卡 + 4 敌卡 + 行动条 ~10 芯片 + 操作面板 ~6 按钮） |
| 内存峰值 | < 2MB | < 200KB（state 对象 + 少量字符串日志） |
| 主循环 deltaTime 上限 | 不适用（事件驱动） | setTimeout 使用固定延迟，无 deltaTime 漂移 |
| 特效/伤害数字上限 | 1 个/行动（1.3s 后自动移除） | 每次 action_executed 创建 1 个 floating-num div，setTimeout 1.3s remove |
| 日志缓冲 | 50 条 | state.log 数组 shift() 削峰 |

**无性能风险项**：回合制、低频渲染（~1-2s/次）、DOM 规模小。转正式工程时若改为实时动画（帧驱动），需重新评估。

---

## 八、边界条件与容错

### 8.1 数据边界

| 边界类型 | 触发条件 | 当前处理 | 转开发建议 |
|---------|---------|---------|-----------|
| HP 减为负 | 伤害 > 当前 HP | `Math.max(0, hp - damage)` | 保留 |
| HP 溢出治疗 | 治疗量 > 缺口 | `Math.min(maxHp, hp + heal)` | 保留 |
| BP 溢出 | BP + BP_RATE > 5 | `Math.min(BP_MAX, bp + BP_RATE)` | 保留；若增加 BP 上限道具需改为动态上限 |
| SP 溢出 | SP + SP_REGEN > maxSp | `Math.min(maxSp, sp + SP_REGEN)` | 保留 |
| 伤害为 0 或负 | 公式结果 ≤ 0 | `max(1, floor(...))` | 保留；建议工程实现时加断言日志 |
| 盾值归零 | 弱点连续命中 | 精确扣至 0 | 保留 |
| ENEMY_HP_MULT/SHIELD_MULT 改为非整数 | 用户拖滑条 | Math.floor/Math.round 取整 | 保留 |

### 8.2 状态机边界（非法转换）

| 非法转换 | 触发条件 | 当前处理 | 转开发建议 |
|---------|---------|---------|-----------|
| idle → player_turn（跳过 wave_intro） | 直接调用 startActorTurn | startBattle 流程硬编码为 wave_intro → buildActionQueue → nextTurn，不暴露捷径 | 工程实现建议用状态机库（如 XState）强制转换规则 |
| player_turn 下响应点击两次 | 快速双击 | 第一次点击后 setTimeout ANIM_DELAY 期间 phase 未变回 player_turn，但 commandStep 可能在 target_select | 当前依赖 UI 禁用（renderAll 重绘按钮）；工程实现建议加 `actionLocked` 标志 |
| victory/defeat 下继续流转 | checkBattleEnd 返回 true 后仍有 setTimeout 未触发 | nextTurn 入口即检查 phase，已结束直接 return | 保留 guard 模式；若改用 async/await 需清理 pending timeout |
| 死亡单位仍在行动队 | buildActionQueue 与 filtered queue 不同步 | nextTurn 入口重新 filter 死亡单位 | 工程实现建议：死亡时立刻从 actionQueue splice |

### 8.3 UI/交互边界

| 边界类型 | 触发条件 | 当前处理 | 转开发建议 |
|---------|---------|---------|-----------|
| 非玩家回合点击单位卡片 | phase !== 'player_turn' | bindUnitClicks 中检查 `if (state.phase !== 'player_turn') return` | 保留 |
| SP 不足选择技能 | unit.sp < skill.spCost | UI 层 button disabled；逻辑层二次守卫 + logEvent 报错 | 保留双重守卫；工程实现建议 UI 层显示红色"SP 不足"提示 |
| BP 不足选择增幅 | bpSpent > unit.bp | BP selector 只渲染 0~unit.bp 的选项 | 保留 |
| 选择已死亡目标 | target.isDead | UI 层 .dead 卡片 pointer-events:none；逻辑层 getUnit 检查 | 保留 |
| 全部角色阵亡 | party.every(p => p.isDead) | checkBattleEnd 判定 defeat | 保留 |
| 操作面板步骤回退 | 用户在 bp_select 按返回 | onBack 根据当前步骤回退到 action/skill_select | 工程实现建议用栈管理步骤历史 |

### 8.4 性能边界

| 边界类型 | 触发条件 | 当前处理 | 转开发建议 |
|---------|---------|---------|-----------|
| 伤害数字 DOM 堆积 | 高频 action_executed | setTimeout 1.3s 自动 remove | 若改为实时战斗需加对象池 |
| 日志无限增长 | log 数组持续 push | 上限 50 条，超出 shift | 保留；工程实现建议上限 200 + 虚拟滚动 |
| renderAll 全量重绘 | 每次事件触发 | innerHTML 重设 | 当前规模 OK；工程实现建议 React/Vue 虚拟 DOM 或 Canvas 渲染 |

### 8.5 异常兜底

| 异常类型 | 处理方式 | 转开发建议 |
|---------|---------|-----------|
| 无显式 try-catch | 依赖条件守卫（phase/SP/BP/unit 非空检查） | 工程实现建议：关键路径（calcDamage/executePlayerAction/nextTurn）加 try-catch + 错误日志上报 |
| 行动队为空 | buildActionQueue 重建；若仍空则 checkBattleEnd | 保留 |
| getUnit 返回 null | 各入口函数 `if (!unit) return` | 工程实现建议：TypeScript 强类型 + 非空断言消除此类守卫 |

---

## 九、已知问题

> 来源：原型代码 TODO/FIXME/HACK 扫描 + 通用 spec 同步项

| 位置 | 描述 | 类型 | 严重度 |
|------|------|------|-------|
| 全代码 | 无 TODO/FIXME/HACK 注释 | — | — |
| executePlayerAction (L808) | SP/BP 不足时仅写日志 + return false，无 UI 层错误提示（当前依赖 UI 层 disabled 防御） | 改进项 | P2 |
| renderAll (L1137) | 全量 innerHTML 重绘，若未来单位数增加（>20）可能产生闪烁 | 待定 | P2 |
| executeEnemyAction (L888) | findTargetByThreat 函数体为空（仅返回 null），AI 威胁评估未实现 | 待定 | P1 |

> 扫描时间：2026-06-15

---

## 版本记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.1 | 2026-06-15 | AI 自动提取初稿 |
| v1.0 | — | 待人工复核 |
