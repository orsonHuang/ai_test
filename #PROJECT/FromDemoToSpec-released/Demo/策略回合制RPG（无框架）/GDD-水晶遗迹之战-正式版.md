# 水晶遗迹之战 — 回合制RPG战斗

> **模板用途**：配合 HTML 原型验证工作流使用。AI 在「开始 Spec 提取」时自动预填程序侧信息（系统功能/页面清单/多语言 key），策划随后补体验侧（设计目的/埋点/动效/音效）。本模板是**正式开发策划案**，描述的是一份可直接交付程序/美术/音效/QA 执行的落地文档。
> **来源原型**：`battle.html` — [AI 预填]
> **对应 Spec**：`SPEC-水晶遗迹之战.md` — [AI 预填]
> **对应设计文档**：`GDD-水晶遗迹之战.md` — [AI 预填]
> **文档状态**：[x] 草稿 / [ ] 评审中 / [ ] 已确认
>
> **与 game/product 模板的分工**：
> - `GDD-水晶遗迹之战.md` = 设计意图文档，记录 WHY（为什么这样设计 / 验证结论 / 体验目标 / 平衡目标）
> - 本模板 = 落地策划案，记录 WHAT+HOW（系统功能 / 页面 / 埋点 / 动效 / 音效 / 多语言），是进入正式开发的执行依据
> - **AI 预填范围**：系统功能（从代码函数/事件提取）+ 页面需求（从 UI 切换逻辑提取）+ 多语言 key（从硬编码文本提取）；其余段标记"待策划填写"

#### 文档规范

- 一般内容使用正常字体
- **关键内容使用粗体字**
- **重要的内容使用红色粗体字**
- ~~删减内容用横线划掉~~
- 暂时搁置不实现的功能用灰色底色
- 最后版本的调整内容使用黄色底色
- 有争议或待确认内容使用红色底色

# 简介

### 设计目的

1. **【待策划填写】** 【本方案要实现什么目的？优化体验/补充内容/新增玩法/提升次留/等等】

### 设计内容

1. **【待策划填写】** 【本方案中，准备要做哪些东西？尽可能一句话描述一个内容】

### 名词解释（*）

| **名词** | **说明** |
|---|---|
| BP (Boost Point) | 增幅点数，每回合自动 +1，上限 5，消耗 1~3 点强化行动效果 |
| Break / 破盾 | 敌人护盾归零后进入的眩晕状态，持续 2 回合，期间受伤倍率 ×1.5 |
| Shield / 护盾 | 敌人持有的护盾值，仅弱点属性攻击可削减 |
| SP | 技能点，释放技能消耗的资源 |
| 弱点属性 | 敌人特有的受击弱点（剑/火/冰/雷/匕首等），初始隐藏，击中后揭示 |

# 参考内容

**【待策划填写】**

【参考图 — 歧路旅人战斗截图或概念图】

【参考链接】

# 方案概述

**【待策划填写】**

【能够快速过一遍方案的原型图】

【若需，可增加几句文本描述】

# 设计决策理由

> 记录本方案中最关键的 2~3 个设计决策——为什么选 A 不选 B？对后续实现有什么约束？
> 详细的体验目标、核心假设、验证结论已在 GDD-水晶遗迹之战.md 中记录，此处只保留"影响落地执行"的关键理由。

| 决策点 | 选择了什么 | 排除了什么 | 理由 | 对实现的约束 |
|--------|-----------|-----------|------|-------------|
| 战斗系统参考 | 歧路旅人 Break+BP 双资源系统 | 传统速度条（FF 式 ATB）/ 纯回合制 | Break 创造「计划→执行→回报」的策略节奏，BP 提供跨回合资源管理深度，二者耦合产生核心博弈 | 需要护盾状态机 + BP 积累/消耗逻辑 + 弱点揭示系统 |
| 行动顺序 | 每回合 SPD+随机波动排序，敌我混合 | 我方先行完再敌方（DQ 式）/ 纯速度决定（无随机） | 混合排列 + 随机波动增加不确定性，避免玩家精确计算最优解，提升临场紧张感 | 需要回合前排序算法 + 时间轴 UI 组件，敌方 AI 需预先决策（显示意图） |
| 视觉风格 | 深色扁平现代风（纯 CSS） | 像素复古风 / HD-2D / Canvas 绘制 | CSS 动画可实现丰富反馈（伤害弹出/抖动/脉冲/缩放），开发效率高，零美术资源依赖 | 无位图/精灵资源，所有视觉用 CSS 形状 + 文字表达；角色/敌人用卡片组件呈现 |

# 系统功能

【程序规则相关描述 — AI 预填】

## 模块 1：战斗回合流转

1. **回合开始**
    1. 调用 `startRound()` — 移除死亡实体、Buff/Debuff 倒计时 -1、Break 倒计时 -1
    2. 敌方 AI 预决策本回合行动（`decideAction()` → 存入 `nextAction`）
    3. 计算行动顺序：`initiative = SPD + random(0, 20)`，降序排列生成队列
    4. 渲染时间轴 UI（`renderTurnOrder()`）

2. **逐行动者执行**
    1. `processNextTurn()` 从队列取出下一个 `!hasActed && alive` 的实体
    2. 若为 **Character**：`phase = 'player_turn'`，显示指令面板（`renderCommandPanel()`）
    3. 若为 **Enemy**：`phase = 'executing'`，AI 自动执行，延迟 400ms+600ms

3. **行动完成**
    1. `finishAction(actor)` — 标记 `hasActed = true`，移除死亡实体，刷新 `allActors`
    2. 调用 `processNextTurn()` 继续或进入回合结束

4. **回合结束**
    1. `endRound()` — 所有存活角色 BP +1（上限 5），回合数 +1
    2. 调用 `startRound()` 进入下一回合

## 模块 2：Break / Shield 护盾击破系统

1. **护盾削减规则**
    1. 仅弱点属性攻击可削减护盾。非弱点攻击 = 无削减（日志提示 `非弱点`）
    2. 护盾削减量 = `1 (基值) + boostLevel + shieldBonus (破甲击=+2)`
    3. 命中弱点时，`revealedWeakness.add(element)` 揭示该属性
    4. 护盾 ≤ 0 → `isBroken = true; breakTimer = 2; shield = maxShield`

2. **Break 状态效果**
    1. 敌人跳过行动（队列中跳过）
    2. 受伤伤害 ×1.5（`getDamageMult()` 返回 1.5）
    3. 敌人卡片添加 `.broken` 类：边框变灰、透明度降低、显示 "BREAK" 水印

3. **Break 恢复**
    1. 每回合开始 `tickBreak()`：`breakTimer--`
    2. `breakTimer === 0` → `isBroken = false`，护盾保持 `maxShield`（进入新击破周期）

## 模块 3：BP Boost 增幅系统

1. **BP 机制**
    1. 初始 2 点，每回合结束 +1，上限 5
    2. 玩家点击「增幅」按钮循环切换消耗量（0→1→2→3→0），不可超过当前持有量

2. **Boost 效果**
    1. **普通攻击**：伤害 ×(1 + 0.3 × boostLevel)，削盾 +boostLevel 层
    2. **技能**：伤害 ×(1 + 0.25 × boostLevel)，削盾 +boostLevel 层
    3. **防御**：若 boostLevel > 0，额外获得 `defUp` 2 回合

3. **BP 显示**
    1. 角色卡片底部金色圆点（`.bp-dot`）
    2. `bp-dot.filled` 表示已持有，空圆点表示未获得

## 模块 4：弱点发现系统

1. **弱点配置**
    1. 每个敌人 3~4 个弱点（`weaknesses: string[]`）
    2. 初始全部隐藏，UI 显示为 `?`（`.weak-tag:not(.revealed)`）
    3. 用对应属性击中后 `revealedWeakness.add(element)`，标签变为金色 `.weak-tag.revealed`

2. **属性来源**
    1. 角色普攻 = 武器属性（剑=sword / 匕首=dagger / 杖=staff）
    2. 技能自带属性（火=fire / 冰=ice / 雷=lightning）
    3. 元素风暴每目标随机属性

## 模块 5：角色技能系统

1. **技能消耗**
    1. SP 不足时技能按钮置灰（`disabled`）
    2. 消耗在 `executePlayerAction()` 中扣除（`actor.sp -= skill.cost`）

2. **技能类型**
    1. `damage` — 伤害技能（含 element/shieldBonus/critChance/randomElement）
    2. `buff` — 增益技能（target=self，`Object.assign(target.buffs, skill.buff)`）
    3. `debuff` — 削益技能（target=single_enemy，降低敌方属性）
    4. 混合型 — damage + debuff（如烟雾弹，先伤害再施加 debuff）

3. **自瞄技能**
    1. `target === 'self'` 时，选择后立即执行（`handleSkillPick()` → `executePlayerActionSelf()`）

## 模块 6：敌方 AI 系统

1. **决策流程**
    1. 每回合开始 `decideAction(characters)` 基于权重随机选择行动
    2. 行动意图存入 `nextAction`，渲染到敌人卡片（`.e-intent`）

2. **Boss AI — 远古魔像**
    1. `rand < 0.35` → 硬化（defUp 2回合）
    2. `rand < 0.65` → 地震（全体 ×0.7）
    3. else → 重击（单体 ×1.3）

3. **杂兵 AI**
    1. **岩石傀儡**：70% 撞击（单体 ×0.9）/ 30% 碎石（单体 ×0.9）
    2. **水晶魔灵**：70% 晶化射线（单体 ×1.0）/ 30% 治愈波动（Boss +~40 HP）

4. **Debuff 影响**
    1. 敌方持有 `atkDown` 时，攻击力 ×0.6
    2. 敌方持有 `accDown` 时，命中率 70%（每个目标独立判定 `Math.random() > 0.7`）

## 模块 7：伤害计算

1. **我方伤害公式**
    1. `attackPower = ATK × atkUp修正(×1.4)`
    2. `skillPower = attackPower × 技能倍率 × boost修正`
    3. `critRoll = skillPower × 1.5 (if 暴击)`
    4. `breakMult = critRoll × 1.5 (if 目标Break中)`
    5. `rawDamage = floor(breakMult)`
    6. `defense = DEF × defUp修正(×1.5)`
    7. `finalDamage = max(1, rawDamage - floor(defense × 0.3))`

2. **敌方伤害公式**
    1. `enemyAtk = ATK × atkDown修正(×0.6)`
    2. `baseDmg = enemyAtk × 行动倍率`
    3. `finalDmg = max(1, baseDmg - floor(目标DEF × 0.4))`

## 模块 8：战斗结束

1. **胜利条件**：所有敌方 `!alive`
2. **失败条件**：所有我方 `!alive`
3. 触发时机：`processNextTurn()` 每次调用时检查
4. 结果面板：`#result-overlay` 淡入显示胜负 + 回合统计 +「重新战斗」按钮

# 页面需求

> 列出本方案涉及的全部 UI 页面/弹窗/面板，标注其功能、状态和备注。— [AI 预填]

| 页面/弹窗名称 | 功能描述 | 入口/触发条件 | 关闭方式 | 状态（新增/复用/修改） | 备注 |
|--------------|---------|-------------|---------|---------------------|------|
| 标题栏 `#header` | 显示"水晶遗迹之战"标题 + 当前回合数 | 战斗开始 | — | 新增 | 回合数每回合结束更新 |
| 行动时间轴 `#turn-order` | 横向排列本回合行动顺序（头像+箭头） | 每回合开始 | — | 新增 | 当前行动者放大高亮（`.current`），已行动者半透明（`.done`） |
| 敌方区域 `#enemy-zone` | 显示敌方卡片：HP/护盾/弱点/行动意图 | 战斗开始 | — | 新增 | 选目标时卡片高亮（`.targeting`），Break 中显示水印（`.broken`） |
| 我方区域 `#party-zone` | 显示我方卡片：HP/SP/BP/Buff/Debuff | 战斗开始 | — | 新增 | 当前行动者高亮（`.active`），已行动者半透明（`.acted`） |
| 指令面板 `#command-panel` | 显示当前行动角色 + 增幅/攻击/技能/防御按钮 | 我方角色回合（`phase='player_turn'`） | 行动执行后隐藏 | 新增 | 非玩家回合显示"等待行动..." |
| 技能子面板 `#skill-panel` | 展开当前角色 4 个技能（名称/SP消耗/描述） | 点击「技能」按钮 | 点击「取消」或执行技能后 | 新增 | SP 不足的技能按钮置灰；自瞄技能（target=self）选择后立即执行 |
| 目标提示 `#target-hint` | 显示"点击目标敌人" | 进入目标选择模式 | 选择目标或取消后 | 新增 | 仅在选择攻击/技能目标时显示 |
| 战斗日志 `#battle-log` | 显示最近 8 条战斗消息（伤害/破盾/Buff/治疗） | 战斗开始 | — | 新增 | 颜色区分：伤害=红/破盾=金/治疗=绿/Buff=紫/暴击=强调红 |
| 结果弹窗 `#result-overlay` | 战斗胜利/失败显示，含回合统计和重试按钮 | 战斗结束 | 点击「重新战斗」 | 新增 | 全屏半透明遮罩 + 居中卡片，scaleIn 动画 |
| 伤害数字 `.damage-num` | 在目标上方弹出浮动数字 | 每次造成/恢复HP时 | 1s 后自动移除 | 新增 | normal=白 / crit=红大 / break=金 / heal=绿 |

# 埋点需求

> 列出需要数据埋点的关键行为事件，标注触发时机和参数字段。— 【待策划填写】

| 事件ID | 事件名称 | 触发时机 | 参数字段 | 优先级 | 备注 |
|--------|---------|---------|---------|--------|------|
| | | | | | |
| | | | | | |

# 动效需求

> 列出需要视觉动效的元素，描述效果和触发条件。— [AI 预填已实现动效，待策划补充/调整]

| 动效对象 | 动效描述 | 触发条件 | 持续时间 | 优先级 | 参考/备注 |
|---------|---------|---------|---------|--------|----------|
| 伤害数字 | 从目标位置上升 40px 后淡出 | 每次造成/恢复 HP | 1s | P0 | `floatUp` CSS 动画 |
| 受击单位 | 水平抖动 | 受到伤害时 | 0.4s | P0 | `shake` CSS 动画 |
| 当前行动者 | 光晕脉冲（扩大缩小） | 在时间轴中为当前位 | 持续 | P0 | `pulse` CSS 动画 |
| 日志行 | 淡入 | 新日志写入 | 0.3s | P1 | `fadeIn` |
| 结果弹窗 | 缩放淡入 | 战斗结束 | 0.5s(遮罩)+0.4s(卡片) | P1 | `fadeIn` + `scaleIn` |
| 战斗日志 | 自动滚到底部 | 新日志写入 | 即时 | P1 | `scrollTop = scrollHeight` |
| HP/SP 条 | 平滑过渡 | HP/SP 变化 | 0.5s | P0 | `transition: width 0.5s ease` |
| 护盾图标 | 透明度渐变 | 护盾层数变化 | 0.3s | P1 | `transition: opacity 0.3s` |
| 敌人卡片选中 | 上移 2px + 金色光晕 | 进入目标选择模式悬停 | 0.2s | P1 | `transform: translateY(-2px)` |
| Boost 按钮 | 背景变金色 | Boost 被激活时 | 即时 | P1 | `.boosted` 类切换 |

# 音效需求

> 列出需要音效反馈的事件/状态，描述音效类型和参考。— 【待策划填写】

| 触发事件/状态 | 音效描述 | 类型（UI音效/环境音/角色音效等） | 优先级 | 参考音频 |
|-------------|---------|-------------------------------|--------|---------|
| | | | | |
| | | | | |

# 多语言key

> 列出所有需要多语言配置的文本 key 和对应文案。— [AI 预填]

| Key | 简体中文 | English | 使用位置 | 备注 |
|-----|---------|---------|---------|------|
| `battle.title` | 水晶遗迹之战 | Battle of Crystal Ruins | 标题栏 `#header h1` | |
| `battle.round` | 回合 | Round | 标题栏回合显示 | 动态拼接回合数 |
| `battle.turn_order_label` | 行动顺序 | Turn Order | 时间轴标签 | |
| `battle.waiting` | 等待行动... | Waiting... | 指令面板空闲状态 | |
| `battle.current_turn` | 当前行动: | Current: | 指令面板角色行动提示 | 动态拼接角色名 |
| `battle.select_target` | 点击目标敌人 | Select Target | 目标提示 | |
| `cmd.boost` | 增幅 | Boost | 增幅按钮 | |
| `cmd.attack` | 攻击 | Attack | 攻击按钮 | |
| `cmd.skill` | 技能 | Skills | 技能按钮 | |
| `cmd.defend` | 防御 | Defend | 防御按钮 | |
| `cmd.item` | 道具 | Items | 道具按钮（当前未实现） | |
| `cmd.cancel` | 取消 | Cancel | 技能子面板取消按钮 | |
| `skill.slash.name` | 横斩 | Cross Slash | 剑士技能1名称 | |
| `skill.slash.desc` | 剑属性单体攻击 | Sword single-target attack | 剑士技能1描述 | |
| `skill.full_strike.name` | 全力斩 | Full Strike | 剑士技能2名称 | |
| `skill.full_strike.desc` | 剑属性强力一击 | Powerful sword attack | 剑士技能2描述 | |
| `skill.taunt.name` | 挑衅 | Taunt | 剑士技能3名称 | |
| `skill.taunt.desc` | 吸引火力,自身防御UP(3回合) | Draw fire, DEF UP (3 turns) | 剑士技能3描述 | |
| `skill.armor_break.name` | 破甲击 | Armor Break | 剑士技能4名称 | |
| `skill.armor_break.desc` | 剑属性,额外削2层盾 | Sword, extra 2 shield break | 剑士技能4描述 | |
| `skill.fireball.name` | 火焰术 | Fireball | 学者技能1名称 | |
| `skill.fireball.desc` | 火属性单体攻击 | Fire single-target attack | 学者技能1描述 | |
| `skill.ice_blast.name` | 冰霜术 | Ice Blast | 学者技能2名称 | |
| `skill.ice_blast.desc` | 冰属性单体攻击 | Ice single-target attack | 学者技能2描述 | |
| `skill.lightning.name` | 雷电术 | Lightning | 学者技能3名称 | |
| `skill.lightning.desc` | 雷属性单体攻击 | Lightning single-target attack | 学者技能3描述 | |
| `skill.element_storm.name` | 元素风暴 | Element Storm | 学者技能4名称 | |
| `skill.element_storm.desc` | 全体随机属性攻击 | Random element AoE | 学者技能4描述 | |
| `skill.shadow_strike.name` | 暗袭 | Shadow Strike | 盗贼技能1名称 | |
| `skill.shadow_strike.desc` | 匕属性,高暴击率 | Dagger, high crit rate | 盗贼技能1描述 | |
| `skill.steal.name` | 偷取 | Steal | 盗贼技能2名称 | |
| `skill.steal.desc` | 降低单体敌人攻击(3回合) | Reduce enemy ATK (3 turns) | 盗贼技能2描述 | |
| `skill.shadow_clone.name` | 影分身 | Shadow Clone | 盗贼技能3名称 | |
| `skill.shadow_clone.desc` | 自身攻击UP(3回合) | Self ATK UP (3 turns) | 盗贼技能3描述 | |
| `skill.smoke_bomb.name` | 烟雾弹 | Smoke Bomb | 盗贼技能4名称 | |
| `skill.smoke_bomb.desc` | 全体敌人命中降低 | AoE enemy ACC down | 盗贼技能4描述 | |
| `char.warrior.name` | 奥伯里克 | Olberic | 剑士名称 | |
| `char.scholar.name` | 塞拉斯 | Cyrus | 学者名称 | |
| `char.thief.name` | 泰里翁 | Therion | 盗贼名称 | |
| `enemy.boss.name` | 远古魔像 | Ancient Golem | Boss 名称 | |
| `enemy.minion_a.name` | 岩石傀儡 | Rock Puppet | 杂兵A 名称 | |
| `enemy.minion_b.name` | 水晶魔灵 | Crystal Sprite | 杂兵B 名称 | |
| `enemy.skill.slam.name` | 重击 | Slam | Boss技能1名称 | |
| `enemy.skill.quake.name` | 地震 | Quake | Boss技能2名称 | |
| `enemy.skill.harden.name` | 硬化 | Harden | Boss技能3名称 | |
| `enemy.skill.bash.name` | 撞击 | Bash | 杂兵A技能名称 | |
| `enemy.skill.shard.name` | 碎石 | Shard | 杂兵A技能名称 | |
| `enemy.skill.ray.name` | 晶化射线 | Crystal Ray | 杂兵B技能1名称 | |
| `enemy.skill.heal.name` | 治愈波动 | Healing Wave | 杂兵B技能2名称 | |
| `log.battle_start` | === 水晶遗迹之战 开始！=== | === Battle Start! === | 战斗日志首行 | |
| `log.enemies` | 敌方: | Enemies: | 敌方列表日志 | 动态拼接 |
| `log.round` | --- 第 X 回合 --- | --- Round X --- | 回合分隔日志 | 动态拼接 |
| `log.defend` | 进入防御姿态 | entered defend stance | 防御日志 | |
| `log.defend_boosted` | 防御强化！防御力大幅上升 | Defense greatly increased! | Boost防御日志 | |
| `log.attack` | 攻击 | attacks | 攻击日志 | 动态拼接目标名 |
| `log.shield_break` | 护盾击破！进入 Break 状态！ | Shield Break! | 破盾日志 | |
| `log.shield_hit` | 护盾 | Shield | 削盾日志 | 动态拼接削减量 |
| `log.damage` | 造成 X 点伤害 | deals X damage | 伤害日志 | 动态拼接数值 |
| `log.defeated` | 被击败！ | defeated! | 击败日志 | 动态拼接目标名 |
| `log.weakness_hit` | 弱点命中！盾 | Weakness hit! Shield | 弱点命中日志 | 动态拼接 |
| `log.weakness_break` | 弱点暴击！护盾击破 [BREAK] | Weakness Break! | 弱点破盾日志 | |
| `log.non_weakness` | 属性 → 非弱点 | element → non-weakness | 非弱点提示 | |
| `log.crit` | [暴击!] | [CRITICAL!] | 暴击标记 | |
| `log.break_bonus` | [破防+50%] | [Break +50%] | 破防加成标记 | |
| `log.hit_miss` | 攻击未命中 | missed! | 未命中日志 | |
| `log.fell` | 倒下！ | fell! | 角色倒下日志 | |
| `log.heal` | 回复 X HP | restored X HP | 治疗日志 | 动态拼接 |
| `log.def_up` | 防御上升 | DEF UP | 防御Buff日志 | |
| `log.atk_up` | 攻击上升 | ATK UP | 攻击Buff日志 | |
| `log.atk_down` | 攻击下降 | ATK DOWN | 攻击Debuff日志 | |
| `log.acc_down` | 命中下降 | ACC DOWN | 命中Debuff日志 | |
| `result.win` | 战斗胜利！ | Victory! | 胜利标题 | |
| `result.lose` | 全军覆没... | Defeat... | 失败标题 | |
| `result.rounds` | 共 X 回合 | X rounds | 回合统计 | 动态拼接 |
| `result.survivors` | 存活 X 人 | X survivors | 存活统计 | 动态拼接 |
| `result.retry_prompt` | 请重新挑战 | Try again | 失败提示 | |
| `result.restart` | 重新战斗 | Rematch | 重试按钮 | |
| `element.sword` | 剑 | Sword | 属性标签 | |
| `element.dagger` | 匕首 | Dagger | 属性标签 | |
| `element.staff` | 杖 | Staff | 属性标签 | |
| `element.fire` | 火 | Fire | 属性标签 | |
| `element.ice` | 冰 | Ice | 属性标签 | |
| `element.lightning` | 雷 | Lightning | 属性标签 | |
| `buff.def_up` | 🛡防御 | 🛡DEF | Buff标签 | 含回合数 |
| `buff.atk_up` | ⚔攻击 | ⚔ATK | Buff标签 | 含回合数 |
| `buff.taunt` | 🎯嘲讽 | 🎯Taunt | Buff标签 | 含回合数 |
| `debuff.atk_down` | 💪攻击↓ | 💪ATK↓ | Debuff标签 | 含回合数 |
| `debuff.acc_down` | 👁命中↓ | 👁ACC↓ | Debuff标签 | 含回合数 |
| `hp.label` | HP | HP | 生命值标签 | |
| `sp.label` | SP | SP | 技能点标签 | |
| `bp.label` | BP | BP | 增幅点标签 | |
| `shield.label` | Shield | Shield | 护盾标签 | |
