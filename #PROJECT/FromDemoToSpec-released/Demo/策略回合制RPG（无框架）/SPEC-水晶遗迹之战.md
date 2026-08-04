# 水晶遗迹之战 — 技术规格文档 (SPEC)

> **版本**: v0.1 | **文件**: `battle.html` | **行数**: ~1200
> **依赖**: 零外部依赖，纯 HTML + CSS + Vanilla JS
> **浏览器**: 现代浏览器 (ES6+)

---

## 1. 项目结构

```
battle.html
├── <style>          CSS (~150行) — 布局/主题/动画
├── <div id="game">  HTML (~50行)  — DOM 骨架
└── <script>         JS  (~600行)  — 游戏逻辑
    ├── DATA            常量定义 (属性表/职业色)
    ├── STATE           全局状态 (GameState 对象)
    ├── ENTITY CLASSES  Character / Enemy 类
    ├── SKILLS          技能定义表
    ├── FACTORIES       实体创建函数
    ├── RENDER          渲染函数组
    ├── GAME FLOW       回合流转逻辑
    ├── PLAYER ACTIONS  玩家指令处理
    ├── ENEMY AI        敌方行为
    ├── BATTLE END      胜负判定
    └── INIT            启动入口
```

---

## 2. 核心数据结构

### 2.1 GameState（全局状态）

```javascript
GameState = {
  round: 1,               // 当前回合数
  phase: 'idle',          // idle | player_turn | enemy_turn | executing | ended
  turnQueue: [],          // 本回合行动顺序 (Character|Enemy)
  currentActorIdx: 0,     // 当前行动者在队列中的索引
  selectedBoost: 0,       // 玩家当前选择的 Boost 等级 (0~3)
  selectedSkill: null,    // 玩家当前选择的技能索引 (null=未选)
  targetingEnemy: false,  // 是否处于目标选择模式
  currentActor: null,     // 当前行动者引用
  battleLog: [],          // 战斗日志数组 [{msg, cls}]
}
```

### 2.2 Character 类

| 属性 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识 (warrior/scholar/thief) |
| name | string | 显示名 |
| job | string | 职业 (warrior/scholar/thief) |
| hp / maxHp | number | 生命值 |
| sp / maxSp | number | 技能点 |
| atk | number | 攻击力 |
| def | number | 防御力 |
| spd | number | 速度（决定行动顺序） |
| weapon | string | 普攻属性 (sword/dagger/staff) |
| bp / maxBp | number | Boost 点数 (初始2/上限5) |
| skills | Skill[] | 技能列表 (4个) |
| buffs | Object | Buff 映射 {buffName: 剩余回合} |
| isDefending | boolean | 本回是否防御 |
| hasActed | boolean | 本回是否已行动 |
| alive | boolean | 存活状态 |

### 2.3 Enemy 类

| 属性 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识 (boss/minion_a/minion_b) |
| name | string | 显示名 |
| isBoss | boolean | Boss 标记 (影响 AI 权重) |
| hp / maxHp | number | 生命值 |
| atk | number | 攻击力 |
| def | number | 防御力 |
| spd | number | 速度 |
| shield / maxShield | number | 护盾值/最大值 |
| weaknesses | string[] | 全弱点属性列表 |
| revealedWeakness | Set | 已揭示的弱点集合 |
| skills | Action[] | AI 行动池 |
| isBroken | boolean | 是否处于 Break 状态 |
| breakTimer | number | Break 剩余回合 |
| buffs | Object | Buff/Debuff 映射 |
| alive | boolean | 存活状态 |
| nextAction | Action | 本回合预定行动 (AI 预先决定) |

### 2.4 Skill 对象结构

```javascript
{
  name: '横斩',           // 显示名
  desc: '剑属性单体攻击',  // 简短描述
  cost: 5,               // SP 消耗
  type: 'damage',        // damage | buff | debuff
  power: 1.3,            // 伤害倍率 (damage 类型)
  element: 'sword',      // 属性 (null=无属性)
  target: 'single',      // single | all | self | single_enemy
  // 可选字段:
  critChance: 0.3,       // 暴击率 (暗袭)
  shieldBonus: 2,        // 额外削盾 (破甲击)
  randomElement: true,   // 随机元素 (元素风暴)
  buff: { defUp: 3 },    // Buff 效果
  debuff: { atkDown: 3 },// Debuff 效果
}
```

---

## 3. 状态机

```
                    ┌─────────┐
                    │  IDLE   │ (等待开始)
                    └────┬────┘
                         │ startBattle()
                         ▼
                  ┌──────────────┐
          ┌──────►│  startRound  │
          │       └──────┬───────┘
          │              │ 计算行动顺序
          │              │ 敌方AI决策
          │              ▼
          │    ┌──────────────────┐
          │    │  processNextTurn │◄───────┐
          │    └───┬──────┬───────┘        │
          │        │      │                │
          │   ┌────▼─┐ ┌──▼───┐           │
          │   │我方回合│ │敌方回合│          │
          │   │PLAYER │ │ENEMY │          │
          │   └──┬───┘ └──┬──┘           │
          │      │        │               │
          │      └───┬────┘               │
          │          │ 执行行动           │
          │          ▼                    │
          │   ┌─────────────┐            │
          │   │ finishAction │───────────►│ (还有行动者)
          │   └──────┬──────┘            │
          │          │ (本轮结束)         │
          │          ▼                    │
          │   ┌────────────┐             │
          │   │  endRound  │ BP+1        │
          │   └────────────┘             │
          │                              │
          │         ┌─────────┐          │
          └─────────┤ 胜利/失败 │◄─────────┘
                    └─────────┘
```

### 阶段说明

| 阶段 | 可交互 | 说明 |
|------|--------|------|
| `idle` | 否 | 战斗未开始 |
| `player_turn` | 是 | 玩家选择行动，指令面板激活 |
| `executing` | 否 | 行动执行中，动画播放 |
| `enemy_turn` | 否 | 敌方 AI 自动执行 |
| `ended` | 是(仅结果面板) | 战斗结束，显示胜负 |

---

## 4. 渲染系统

### 4.1 渲染函数

| 函数 | 职责 | DOM 目标 |
|------|------|----------|
| renderEnemies() | 绘制敌方卡片 (HP/护盾/弱点/意图) | #enemy-zone |
| renderParty() | 绘制我方卡片 (HP/SP/BP/Buff) | #party-zone |
| renderTurnOrder() | 绘制行动顺序时间轴 | #turn-order |
| renderCommandPanel() | 绘制指令面板/技能子面板 | #command-panel |
| renderLog() | 绘制战斗日志 (最近8条) | #battle-log |
| renderAll() | 统一调用上述所有函数 | — |

### 4.2 交互式渲染

敌方卡片在 `targetingEnemy = true` 时动态绑定点击事件：
```javascript
zone.querySelectorAll('.enemy-card').forEach(card => {
  card.onclick = () => {
    const eid = card.dataset.id;
    const enemy = enemies.find(e => e.id === eid && e.alive);
    if (enemy) executePlayerAction(enemy);
  };
});
```

### 4.3 伤害数字系统

```javascript
function showDamageNum(element, value, cls)
```
- 在目标元素父容器内创建 `<div class="damage-num">`
- CSS `position: absolute` + `floatUp` 动画 (1s)
- 类名决定颜色：normal(白) / crit(红) / break(金) / heal(绿)
- 动画结束后自动移除 DOM 节点

---

## 5. 伤害公式

### 5.1 完整计算路径

```
attackPower = ATK × attackBuff修正(atkUp=×1.4)
skillPower  = attackPower × 技能倍率 × boost修正(×1.0~1.75)
critRoll    = skillPower × 1.5 (if 暴击)
breakMult   = critRoll × 1.5 (if 目标Break中)
rawDamage   = floor(breakMult)
defense     = DEF × defBuff修正(defUp=×1.5, 防御姿态=×1.8)
finalDamage = max(1, rawDamage - floor(defense × 0.3))
```

### 5.2 敌方伤害

```
enemyAtk = ATK × atkDown修正(×0.6)
baseDmg  = enemyAtk × 行动倍率
finalDmg = max(1, baseDmg - floor(目标DEF × 0.4))
```

### 5.3 护盾削减

```
shieldHit = 1 (基值) + boostLevel + shieldBonus (破甲击=+2)
if 弱点命中:
    actualHit = min(shieldHit, remainingShield)
    shield -= actualHit
    if shield == 0: Break!
else:
    no shield reduction
```

### 5.4 特殊机制

| 机制 | 公式 |
|------|------|
| 敌方硬化的 defUp | def × 1.5, 与角色防御修正叠加 |
| 敌方 accDown | 命中率 = 70%, Math.random() 判定 |
| 角色受击防御姿态 | def × 1.8 (叠加 defUp = ×2.7) |

---

## 6. 敌方 AI

### 6.1 决策时机

- **每回合开始时**，`decideAction()` 被调用
- 行动意图存入 `nextAction`，显示在敌人卡片上
- 执行时从 `nextAction` 取行动

### 6.2 Boss AI (远古魔像)

| 条件 | 行动 | 概率 |
|------|------|------|
| rand < 0.35 | 硬化 (defUp 2回合) | 35% |
| rand < 0.65 | 地震 (全体 ×0.7) | 30% |
| else | 重击 (单体 ×1.3) | 35% |

### 6.3 杂兵 AI

| 敌人 | 条件 | 行动 | 概率 |
|------|------|------|------|
| 岩石傀儡 | rand < 0.7 | 撞击 (单体 ×0.9) | 70% |
| 岩石傀儡 | else | 碎石 (单体 ×0.9) | 30% |
| 水晶魔灵 | rand < 0.7 | 晶化射线 (单体 ×1.0) | 70% |
| 水晶魔灵 | else | 治愈波动 (Boss +40HP) | 30% |

### 6.4 Debuff 影响

AI 执行行动时受自身 Debuff 影响：
- atkDown → 攻击力 ×0.6
- accDown → 命中率 70%（单独判定每个目标）

---

## 7. 动画系统

### 7.1 CSS 动画列表

| 动画名 | 触发时机 | 效果 | 时长 |
|--------|----------|------|------|
| floatUp | 伤害/治疗数字 | 从目标位置上升 40px 后淡出 | 1s |
| shake | 受击 | 水平抖动 | 0.4s |
| pulse | 行动顺序当前位 | 光晕脉冲 | 持续 |
| popIn | 未使用(保留) | 缩放弹入 | — |
| fadeIn | 日志行/结果面板 | 淡入 | 0.3s/0.5s |
| scaleIn | 结果面板 | 缩放淡入 | 0.4s |

### 7.2 过渡动画

- HP 条：`transition: width 0.5s ease`
- 护盾图标：`transition: opacity 0.3s`
- BP 圆点：`transition: all 0.3s`
- 敌方卡片状态切换：`transition: all 0.3s`

---

## 8. UI 组件树

```
#game (flex-column, max-width:960px)
├── #header (flex-row)
│   ├── h1 "水晶遗迹之战"
│   └── .round "回合 N"
├── #turn-order (flex-row, overflow-x)
│   └── .slot.player/.enemy (.current/.done)
├── #battlefield (flex-column)
│   ├── #enemy-zone (flex-row, position:relative)
│   │   └── .enemy-card (.boss/.broken/.targeting)
│   │       ├── .e-name
│   │       ├── .e-hp-wrap > .e-hp-fill
│   │       ├── .e-stats
│   │       ├── .e-shield > .sh
│   │       ├── .e-weakness > .weak-tag (.revealed)
│   │       └── .e-intent
│   ├── #party-zone (flex-row, position:relative)
│   │   └── .char-card (.active/.acted)
│   │       ├── .c-name
│   │       ├── .c-hp > .fill
│   │       ├── .c-sp > .fill
│   │       ├── .c-stats
│   │       ├── .c-bp > .bp-dot (.filled)
│   │       └── .c-buffs > .buff-tag
│   └── #command-panel
│       ├── .actor-info
│       ├── .action-row
│       │   └── button (.boost/.attack/.skill/.defend)
│       └── #skill-panel > .skill-list > button.skill-btn
├── #battle-log
└── #result-overlay (.hidden)
    └── #result-box
```

---

## 9. 键盘快捷键

| 键位 | 功能 | 上下文限制 |
|------|------|------------|
| `B` | Boost 增幅 (循环 0→1→2→3→0) | player_turn 阶段 |
| `1` | 攻击 (进入目标选择) | player_turn 阶段 |
| `2` | 技能 (展开技能面板) | player_turn 阶段 |
| `3` | 防御 | player_turn 阶段 |
| `Esc` | 取消技能选择/目标选择 | player_turn 阶段 |

---

## 10. 主题变量

基于 CSS 自定义属性实现深色主题：

| 变量 | 色值 | 用途 |
|------|------|------|
| --bg | #1a1a2e | 页面背景 |
| --surface | #16213e | 主面板背景 |
| --surface2 | #0f3460 | 次级面板/卡片背景 |
| --accent | #e94560 | 强调色 (Boss/暴击) |
| --gold | #f5c842 | 金色 (BP/弱点/破盾) |
| --green | #2ecc71 | 绿色 (HP/治疗/己方) |
| --blue | #3498db | 蓝色 (我方/护盾) |
| --red | #e74c3c | 红色 (敌方/伤害) |
| --purple | #9b59b6 | 紫色 (SP/技能) |

---

## 11. 性能注意事项

- **全量重绘**: 每次状态变化调用 `renderAll()` 全量重绘 DOM，适用于当前数据量（≤10 实体）
- **事件绑定**: 敌方卡片点击事件在每次选目标时动态绑定（`card.onclick`），无事件委托
- **动画清理**: 伤害数字动画结束后 `setTimeout(() => remove(), 1000)` 自动清理
- **日志截断**: 超过 50 条日志自动 shift，只显示最近 8 条
- **定位**: 敌方/我方区域使用 `position: relative` 确保伤害数字绝对定位正确
