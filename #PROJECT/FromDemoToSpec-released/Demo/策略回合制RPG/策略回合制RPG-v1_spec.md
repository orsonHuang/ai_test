# 策略回合制RPG · 战斗系统 Spec v0.1

> **模板用途**：由 AI 从 HTML 原型自动提取并填入。人工复核后升为 v1.0。
> **来源原型**：`Demo/策略回合制RPG/策略回合制RPG-v1_mvp.html`
> **提取时间**：2026-06-15
> **人工复核**：[✓] 已复核
> **配套 technical spec**：[✓] 同目录 `策略回合制RPG-v1_spec-technical.md`

---

## 一、概述

| 字段 | 内容 |
|------|------|
| 游戏名称 | 策略回合制RPG |
| 对战模式 | PvE（玩家 4 人小队 vs AI 3 波敌人） |
| 战场规格 | 无网格，队列对排型 |
| 核心验证目标 | BP 增幅 + 弱点破防双系统是否产生多路线策略空间，避免单一最优解 |

---

## 二、数值设计

### 2.1 全局参数表

> 来源：原型代码 L521-L532（CONFIG 对象）

| 参数名 | 默认值 | 可调范围 | 说明 |
|--------|--------|----------|------|
| `DAMAGE_MULT` | 1.0 | 0.5 ~ 3.0 | 全局伤害倍率 |
| `ENEMY_HP_MULT` | 1.0 | 0.5 ~ 3.0 | 敌人最大 HP 倍率（重置后生效） |
| `BP_RATE` | 1 | 1 ~ 3 | 每回合 BP 增长量 |
| `SHIELD_MULT` | 1.0 | 0.5 ~ 2.0 | 敌人初始盾值倍率（重置后生效） |
| `SP_REGEN` | 5 | 0 ~ 20 | 每回合 SP 恢复量 |
| `BREAK_DMG_BONUS` | 1.5 | 1.0 ~ 3.0 | 破防后受伤倍率加成 |
| `BP_MAX` | 5 | — | BP 上限（固定） |
| `DEF_FACTOR` | 0.3 | — | 防御减伤系数（固定） |
| `GUARD_REDUCTION` | 0.5 | — | 防御姿态受伤减少比例（固定） |
| `ENEMY_AI_DELAY` | 800 | — | 敌方 AI 行动延迟 ms（固定） |
| `ANIM_DELAY` | 500 | — | 行动后动画等待 ms（固定） |
| `WAVE_TRANS_DELAY` | 1500 | — | 波次过渡等待 ms（固定） |

### 2.2 伤害公式

> 来源：原型代码 L736-L746（calcDamage 函数）

```
baseDamage = ATK × skillMultiplier × bpMultiplier × breakBonus - DEF × DEF_FACTOR
finalDamage = max(1, floor(baseDamage)) × DAMAGE_MULT
```

**BP 倍率表（技能）**：

| 消耗 BP | bpMultiplier |
|---------|-------------|
| 0 | 1.0 |
| 1 | 1.5 |
| 2 | 2.0 |
| 3 | 3.0 |

**BP 倍率表（普攻）**：每消耗 1 BP 额外打 1 段（每段独立判定破防扣盾），每段伤害按 bpMultiplier=1.0 计算。

边界：
- 最小伤害：1（floor 后 max 保证）
- 最大伤害：无硬上限（由数值域自然约束）
- 暴击机制：无
- 破防加成：breakBonus = BREAK_DMG_BONUS（若 isBroken） else 1.0
- 防御减免：guardReduction = GUARD_REDUCTION（若 isGuarding） else 1.0

**数值示例**：

| 场景 | ATK | 倍率 | BP | 破防 | DEF | 伤害 |
|------|-----|------|-----|------|-----|------|
| 剑士普攻狼(0BP) | 120 | 1.0 | 1.0 | 否 | 30 | 111 |
| 剑士普攻狼(2BP, 3段) | 120 | 1.0×3 | 1.0 | 否 | 30 | 111×3 |
| 剑士蓄力斩破防精英 | 120 | 2.5 | 1.0 | 1.5 | 70 | 429 |
| 学者火球术破防法师(2BP) | 140 | 1.8 | 2.0 | 1.5 | 40 | 744 |
| 舞娘暗影步狼(1BP) | 100 | 1.4 | 1.5 | 否 | 30 | 201 |

---

## 三、单位设计

### 3.1 角色属性表

> 来源：原型代码 L539-L577（PARTY_TEMPLATES 数组）

| 名称 | 职业 | HP | SP | ATK | DEF | SPD | 普攻类型 | 阵营 |
|------|------|-----|-----|-----|-----|-----|---------|------|
| 剑士 | 战士 | 800 | 60 | 120 | 80 | 70 | 斩 | 玩家 |
| 学者 | 法师 | 500 | 150 | 140 | 40 | 60 | 打 | 玩家 |
| 神官 | 治疗 | 650 | 120 | 80 | 60 | 80 | 打 | 玩家 |
| 舞娘 | 辅助 | 550 | 100 | 100 | 50 | 110 | 突 | 玩家 |

### 3.2 敌人属性表

> 来源：原型代码 L578-L582（ENEMY_TEMPLATES 对象）

| 名称 | HP | ATK | DEF | SPD | 弱点 | 盾值 | AI 类型 | 特殊行为 |
|------|-----|-----|-----|-----|------|------|---------|---------|
| 狼 | 300 | 60 | 30 | 50 | 斩 | 2 | basic | 纯攻击 |
| 暗法师 | 400 | 80 | 40 | 70 | 突、光 | 3 | buffer | 若无 DEF↑ buff → 施加 DEF↑30%·3回合 |
| 精英魔将 | 900 | 120 | 70 | 40 | 打、冰 | 4 | charger | 每 4 回合开始蓄力(3回合)，蓄力结束释放 2.0× 高伤；破防打断蓄力 |

### 3.3 技能表

> 来源：原型代码 L539-L577（各角色 skills 数组）

| 技能名 | 所属角色 | 类型 | 目标 | 倍率 | SP 消耗 | BP 消耗 | 冷却 | 说明 |
|--------|---------|------|------|------|---------|---------|------|------|
| 横斩 | 剑士 | 斩 | 全体 | 0.7 | 12 | 0 | 无 | 斩属性全体攻击 |
| 蓄力斩 | 剑士 | 斩 | 单体 | 2.5 | 18 | 2 | 无 | 斩属性单体高伤·固定消耗 2BP（不可进一步增幅） |
| 火球术 | 学者 | 火 | 单体 | 1.8 | 10 | 0 | 无 | 火属性单体 |
| 冰霜风暴 | 学者 | 冰 | 全体 | 1.2 | 22 | 0 | 无 | 冰属性全体 |
| 治愈术 | 神官 | 治疗 | 友方单体 | 0.8 | 8 | 0 | 无 | 恢复 ATK×0.8 HP |
| 圣光 | 神官 | 光 | 单体 | 1.6 | 14 | 0 | 无 | 光属性单体 + 自回伤害量 20% HP |
| 月光之舞 | 舞娘 | buff | 全体友方 | — | 15 | 0 | 无 | 全体 ATK↑30%·持续 2 回合 |
| 暗影步 | 舞娘 | 突 | 单体 | 1.4 | 10 | 0 | 无 | 突属性单体 + 拉队友行动条前移 2 位 |

---

## 四、战斗规则

### 4.1 回合结构

> 来源：原型代码 L1011-L1038（startActorTurn 函数）、L986-L1008（nextTurn 函数）

每回合依次执行：

```
1. 从行动队中取出队首单元作为当前行动者
2. 回合开始处理：
   a. 若为玩家角色：BP += BP_RATE（上限 BP_MAX），SP += SP_REGEN（上限 maxSp），buff 回合 -1，清除防御姿态
   b. 若为敌人：检查破防状态（到期则恢复盾值），buff 回合 -1
3. 若为玩家回合：暂停等待玩家操作
4. 若为敌人回合：AI 自动决策 → 延迟执行
5. 行动完毕 → 行动者重新排入队尾
6. 检查胜负 → 未结束则回到步骤 1
```

### 4.2 移动规则

不适用（无网格系统）。本原型采用"队列对排"模式，无位置/移动维度。

### 4.3 行动顺序规则

> 来源：原型代码 L676-L705（buildActionQueue 函数）

- 所有存活单位按 SPD 降序排列构成行动队
- 单位行动后将自身重新排入队尾（维持 SPD 降序）
- 舞娘「暗影步」可将指定队友在队列中前移 2 位（不低于队首）
- 单位死亡后自动从行动队中移除

### 4.4 胜负条件

> 来源：原型代码 L965-L983（checkBattleEnd 函数）

- **胜利条件**：3 波敌人全部消灭
- **失败条件**：己方 4 名角色全部阵亡
- **波次过渡**：每波敌人全灭后，自动进入下一波（共 3 波）

### 4.5 AI 行为说明

> 来源：原型代码 L888-L962（executeEnemyAction 函数）

**通用优先级**（从高到低）：

1. **若被破防** → 跳过回合
2. **蓄力技已就绪**（chargeCountdown=0）→ 释放蓄力技（2.0× 高伤，目标：HP 最低角色）
3. **需开始蓄力**（charger 类型 & chargeCountdown=-1）→ 开始蓄力（倒计时 3 回合）+ 自身 DEF↑30%·2回合
4. **施放增益**（buffer 类型 & 自身无 DEF↑）→ 自身 DEF↑30%·3回合
5. **攻击**：目标选择——攻击 HP 最低的角色

**精英蓄力被打断**：破防时 chargeCountdown 重置为 0，下次 AI 行动时重新开始蓄力周期。

---

## 五、系统设计

### 5.1 状态定义

> 来源：原型代码 L593-L609（state 对象）

| 字段名 | 类型 | 初始值 | 含义 |
|--------|------|--------|------|
| `phase` | string | `'idle'` | 战斗阶段：idle / wave_intro / player_turn / enemy_turn / wave_clear / victory / defeat |
| `currentWave` | number | 1 | 当前波次编号（1~3） |
| `totalWaves` | number | 3 | 总波次数 |
| `party` | array | `[]` | 玩家角色数组（4 个 Character） |
| `enemies` | array | `[]` | 当前波次敌人数组 |
| `actionQueue` | array | `[]` | 行动队（按 SPD 排序） |
| `currentActor` | object\|null | null | 当前行动者 {type, index} |
| `turnCount` | number | 0 | 总行动计数 |
| `selectedSkill` | object\|null | null | 当前选中的技能 |
| `bpToSpend` | number | 0 | 当前选择的 BP 消耗量 |
| `commandStep` | string | `'action'` | 操作面板步骤：action / skill_select / bp_select / target_select |

### 5.2 事件清单

> 来源：原型代码 L1489-L1537（EventBus.on 注册点）

| 事件名 | 触发时机 | 携带数据 | 监听方 |
|--------|----------|----------|--------|
| `action_executed` | 任意攻击/技能/治疗执行完毕 | {caster, targets[], skill, damage, heal} | 渲染层（动画+面板刷新） |
| `enemy_broken` | 敌人盾值归零 | {enemy} | 渲染层（BREAK 特效） |
| `unit_died` | 单位 HP≤0 | {unit} | 渲染层（面板刷新） |
| `wave_cleared` | 当前波次全灭 | {wave} | 渲染层（过渡提示）+ 逻辑层（下一波） |
| `wave_intro` | 波次登场 | {wave} | 渲染层（面板刷新） |
| `battle_end` | 胜利或失败 | {result: 'victory'\|'defeat'} | 渲染层（结果画面） |
| `battle_started` | 战斗开始 | {} | 渲染层（面板刷新） |
| `player_turn_start` | 玩家角色回合开始 | {actor, unit} | 渲染层（操作面板激活） |
| `enemy_turn_start` | 敌人回合开始 | {actor, unit} | 渲染层（AI 自动执行） |
| `game_reset` | 游戏重置 | {} | 渲染层（面板刷新） |
| `config_changed` | 调试滑条参数变化 | {param, value} | 渲染层（参数显示更新） |
| `log_entry` | 日志写入 | line（字符串） | 渲染层（日志面板追加） |

### 5.3 关键事件流

> 来源：原型代码 logEvent 调用推断

```
[时间轴] 完整一局流程：

idle → "战斗开始！"
  → wave_intro → "第 1 波敌人出现！"
  → 构建行动队（按 SPD 降序）
  → player_turn_start → "{角色} 的回合"
    → 选行动→BP→目标 → action_executed（伤害/治疗/破防）
    → enemy_broken（若盾归零）
    → unit_died（若 HP=0）
    → wave_cleared（若全灭）
  → enemy_turn_start → "{敌人} 行动中..."
    → action_executed
    → unit_died
  → ...循环...
  → battle_end → "胜利！" / "失败"
```

---

## 六、边界条件与容错

> **必填段**。从原型代码 + 试玩观察中提取。

### 6.1 数据边界（HP/伤害/BP 等数值越界）

| 边界类型 | 触发条件 | 当前处理 |
|---------|---------|---------|
| HP 减为负 | calcDamage 结果 > 当前 HP | clamp 到 0（Math.max(0, ...)），触发 unit_died 事件 |
| HP 溢出治疗 | applyHeal 结果 > maxHp | clamp 到 maxHp |
| BP 溢出 | 回合开始 BP + BP_RATE > BP_MAX | clamp 到 BP_MAX(5) |
| SP 溢出 | 回合开始 SP + SP_REGEN > maxSp | clamp 到 maxSp |
| 伤害为 0 或负 | ATK×倍率 - DEF×0.3 ≤ 0 | max(1, floor(...)) 保证最小伤害 1 |
| 盾值归零 | 弱点命中累减 | 精确扣至 0，触发破防；不会出现负数 |
| 防御 DEF 减伤超标 | ATK×倍率 × 破防加成 < DEF×0.3 | 最小伤害 1 保证 |

### 6.2 状态/交互边界（回合/技能/动画的非法切换）

| 边界类型 | 触发条件 | 当前处理 |
|---------|---------|---------|
| 非玩家回合点击操作 | state.phase !== 'player_turn' | bindUnitClicks 中 phase 检查，提前 return |
| SP 不足使用技能 | onSelectSkill 检查 unit.sp < skill.spCost | 按钮 disabled（无法点击） |
| BP 不足选择增幅 | BP selector 只显示 0~unit.bp | 超出 bp 的选项不渲染 |
| SP 不足二重校验 | executePlayerAction 入口再次检查 SP/BP | 写日志 + return false |
| 选择已死亡目标 | processPlayerAction 传入 target | getUnit 取到 isDead=true → 不执行（逻辑层防御）；UI 层 .dead 卡片 pointer-events:none |
| 行动队为空 | nextTurn → getNextActor 返回 null | 重建行动队（buildActionQueue），若仍为空则 checkBattleEnd |
| 胜负判定后双重触发 | checkBattleEnd 返回 true | nextTurn 入口即检查 checkBattleEnd，已结束时 return |
| 动画未完成切回合 | 玩家操作执行后 | setTimeout(CONFIG.ANIM_DELAY) 后才调用 nextTurn |

### 6.3 性能边界（单位数/特效数 上限）

| 边界类型 | 触发条件 | 当前处理 |
|---------|---------|---------|
| 伤害数字 DOM 堆积 | action_executed 高频触发，每次创建新 floating-num | setTimeout 1.3s 后自动 remove |
| 日志条目过长 | log 数组 push，state.log 持续增长 | 上限 50 条，超出 shift 最旧 |
| 行动条渲染 | actionQueue 每次 renderAll 重建 innerHTML | 当前规模（4+4=8 单位），DOM 操作轻量 |

### 6.4 异常兜底（try-catch / fallback）

> 来源：原型代码 try-catch 块 + 显式 fallback 逻辑

| 异常类型 | 处理方式 |
|---------|---------|
| 无 try-catch 块 | 原型未显式使用 try-catch，依赖条件守卫（SP/BP/phase 检查）做防御 |
| 空 actionQueue | buildActionQueue 在 nextTurn 中重建，若结果仍为空则 checkBattleEnd |
| getUnit 取到 null | onTurnStart/executePlayerAction 等函数入口检查 `if (!unit || unit.isDead) return` |

---

## 七、已知问题

> 来源：原型代码 `// TODO` / `// FIXME` / `// HACK` 注释

| 位置（函数名 + 行号） | 描述 | 类型 |
|----------------------|------|------|
| 无 | 本版本已扫描主要逻辑模块（calcDamage / executePlayerAction / executeEnemyAction / checkBattleEnd / buildActionQueue），未发现 TODO/FIXME/HACK 注释 | — |

> 扫描时间：2026-06-15

---

## 版本记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.1 | 2026-06-15 | AI 自动提取初稿 |
| v1.0 | — | 待人工复核 |
