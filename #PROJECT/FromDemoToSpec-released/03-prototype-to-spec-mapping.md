# 原型 → Spec 映射规范与映射配置表 v1.0

---

## 概述

本规范定义 HTML 原型代码中**可被自动识别的结构元素**与 **Spec 文档 / 策划文档字段**之间的对应关系。

AI 读取本规范后，从**已验证的 MVP 文档 + 原型代码**中提取信息，填入文档模板对应章节。

> **输入优先级**：MVP 文档（已结构化）优先于代码扫描（需推断）。MVP 中的"核心规则""配置项清单""已知问题"直接落入 Spec 对应章节；代码扫描补充 MVP 未覆盖的实现细节。

**可用 Spec 模板（提取的落点文件，位于 `spec-templates/` 目录）：**

| 模板文件 | 适用原型类型 | 参考 input-example |
|----------|------------|-------------------|
| `spec-templates/spec-template-combat.md` | 战斗 / 对抗类（回合制） | `input-example-combat.md` |
| `spec-templates/spec-template-realtime.md` | 即时制 / 实时驱动类（塔防、自动战斗等） | `input-example-realtime-towerdefense.md`、`input-example-realtime-autobattle.md` |
| `spec-templates/spec-template-match3.md` | 三消类（含回合制/即时制变体） | `input-example-match3.md` |
| `spec-templates/spec-template-activity.md` | 活动 / 小玩法类 | `input-example-activity.md` |
| `spec-templates/spec-template-system.md` | 系统 / 工具类 | `input-example-system.md` |
| `spec-templates/spec-template-ux.md` | 产品 / UX 类 | `input-example-ux.md` |
| `spec-templates/spec-template-narrative.md` | 叙事 / 剧情类 | `input-example-narrative.md` |
| `spec-templates/spec-template-economy.md` | 经济 / 资源流类 | `input-example-economy.md` |
| `spec-templates/spec-template-deckbuilding.md` | 构筑 / 卡组类 | `input-example-deckbuilding.md` |
| `spec-templates/spec-template-dashboard.md` | 数据可视化 / 仪表板类 | `input-example-dashboard.md` |
| `spec-templates/spec-template-form.md` | 表单 / 流程类 | `input-example-form.md` |

**定制模板（-sp，不通用）：**

| 模板文件 | 适用原型类型 | 参考 input-example |
|----------|------------|-------------------|
| `spec-templates/spec-template-match3-rpg-sp.md` | 即时制三消+RPG 复合类 ⚠ 不通用，仅适用于该特定组合 | `input-example-match3-rpg-sp.md` |

**交付场景模板（沉淀层默认产出，与玩法类型正交）：**

| 模板文件 | 产出时机 | 与通用 spec 的关系 |
|----------|---------|------------------|
| `spec-templates/spec-template-technical.md` | **原型验证完成、进入沉淀层时默认产出**。豁免条件：工程深度极低（无 localStorage/状态机/性能保护，纯前端展示）时可跳过，但须显式说明"已豁免，原因：XXX" | **并列产出**——与通用 spec 同时存在。通用 spec 面向策划/数值（设计语言），technical spec 面向程序员（架构/数据模型/算法伪代码/容错） |

> AI 执行提取时，默认使用与原型类型匹配的模板文件。
> `-sp` 后缀模板为定制模板，不适用于通用场景，使用前确认原型与模板描述完全匹配。
>
> **`system` vs `ux` 选型说明**：两者都属于非游戏产品原型，选择依据：
> - `system/工具`：核心是**数据处理/计算逻辑**（输入→处理→输出），关注计算公式、处理流程、异常处理
> - `ux/产品`：核心是**页面导航/交互流程**（多页面跳转、用户操作路径），关注页面清单、交互绑定、状态展示
> - 若同时具备两者特征，优先选 `ux`，在 `system/工具` 专属映射中手动补充计算逻辑章节
>
> **通用 spec vs technical spec 说明**：
> - 两者并出是默认行为——通用 spec 给策划/数值读，technical spec 给程序员读
> - 豁免 technical spec 的唯一理由：原型无 localStorage、无状态机、无性能保护、纯前端展示（如静态演示页）
> - 豁免时 AI 须在通用 spec 头部注明"technical spec：已豁免，原因：[XXX]"
> - **不要替代关系**：technical spec 不替代通用 spec，因为它不含资源流图/解锁里程碑/经济规则等设计语言段

**策划文档模板（AI 预填 + 策划补填，位于根目录）：**

| 模板文件 | 适用范围 | 填写方式 |
|----------|---------|---------|
| `03-design-doc-template-game.md` | 游戏类（战斗/活动/叙事/经济/构筑） — 设计意图文档（WHY：体验目标/核心假设/验证结论） | AI 预填 → 策划补填 |
| `03-design-doc-template-product.md` | 产品/工具类（系统/UX/Dashboard/表单） — 设计意图文档（WHY：设计决策/体验目标） | AI 预填 → 策划补填 |
| `03-design-doc-template-project.md` | 所有类型 — 落地策划案（WHAT+HOW：系统功能/页面/埋点/动效/音效/多语言） | AI 预填 → 策划补填 |

> 策划文档与 Spec 文档的分工：Spec 记录"代码说了什么"（AI 全自动提取），策划文档记录"设计者想要什么"（AI 预填可从代码/MVP 提取的部分，策划补设计意图）。
>
> **game/product 与 project 模板的分工**：前者记录设计思考和验证结论（WHY），后者是交付程序/美术/音效/QA 的直接执行依据（WHAT+HOW）。正常流程下，一个玩法/系统需同时产出 game/product 文档 + project 文档共两份。
>
> **AI 预填规则**（§自动预填规则）：AI 在提取 Spec 的同时预填策划文档。预填范围包括从代码/MVP 可直接提取的段；标记为"待策划填写"的段留给策划补。详见下文§自动预填规则。

---

## 一、映射配置方式

### 方式一：使用默认映射（推荐，覆盖 80% 场景）

直接使用下文的默认映射配置表。AI 按其自动提取信息。

无需额外配置，开箱即用。

### 方式二：自定义映射（JSON 配置文件）

当默认映射不满足需求时，创建 `mapping-config.json` 与原型文件同目录：

```json
{
  "version": "1.0",
  "prototype_type": "combat",
  "custom_mappings": [
    {
      "code_pattern": "函数名/关键字/正则",
      "extract_rule": "提取逻辑的文字说明（给 AI 的指令）",
      "spec_field": "Spec 文档中的目标字段路径",
      "design_doc_field": "策划文档中的目标字段路径（可选）"
    }
  ],
  "disable_defaults": ["unit_design"],
  "spec_template": "spec_template_combat.md",
  "design_doc_template": "design_doc_combat.md"
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `code_pattern` | 用于匹配代码元素的**正则表达式或关键字**（如 `cooldown\|CD_\|skill_cooldown`） |
| `extract_rule` | 提取逻辑的**自然语言说明**（给 AI 的指令，不是代码） |
| `spec_field` | 提取的信息在 Spec 文档中的目标章节路径 |
| `design_doc_field` | 提取的信息在策划文档中的目标章节路径（可选） |
| `disable_defaults` | 关闭不需要的默认映射项的名称数组 |
| `spec_template` | 指定使用的 Spec 文档模板文件名 |
| `design_doc_template` | 指定使用的策划文档模板文件名 |

---

## 二、默认映射配置表

### 2.1 通用映射（适用于所有原型类型）

| 代码元素 | 提取规则 | → Spec 字段 | → 策划文档字段 |
|----------|----------|-------------|----------------|
| `CONFIG` 对象的所有字段 | 遍历键值对，提取参数名 + 默认值 + 注释中的说明 | 数值设计 → 参数表 | 数值设计 → 可调参数表 |
| `state` 对象中非临时字段 | 排除 `_temp` / `_cache` 前缀的字段，提取其余字段名 | 系统设计 → 状态定义 | — |
| EventBus 注册的所有事件 | 搜索 `EventBus.on('event_name'` 模式，提取去重后的事件名列表 | 系统设计 → 事件清单 | — |
| `// TODO` / `// FIXME` / `// HACK` 注释 | 收集注释内容 + 所在函数名 + 行号 | 已知问题清单 | 验证结论 → 发现问题 |
| `logEvent()` / `console.log()` 调用 | 提取日志消息的静态文本部分，反推关键事件流 | 系统设计 → 关键事件流 | — |
| `function` 关键字定义的所有函数 | 收集函数名 + 注释中的功能说明 | 系统设计 → 模块清单 | — |
| try-catch 块 | 收集 catch 块中的处理逻辑，整理错误处理规则 | 系统设计 → 错误处理 | — |

### 2.2 战斗/对抗类专属映射

| 代码元素 | 提取规则 | → Spec 字段 | → 策划文档字段 |
|----------|----------|-------------|----------------|
| 单位定义（`units` 数组 / `unitTemplates` 对象 / `UNIT_DATA`） | 遍历所有单位条目，提取 name / hp / atk / def / moveRange / skill / team | 单位设计 → 属性表 | 单位设计 → 属性表 |
| 伤害计算函数（函数名含 `damage` / `calcDamage` / `applyDamage`） | 提取函数体中的计算公式字符串 | 战斗规则 → 伤害公式 | 数值设计 → 伤害公式 |
| 回合切换逻辑（`nextTurn()` / `endTurn()` / `switchPhase()`） | 提取函数内的步骤调用顺序 | 战斗规则 → 回合结构 | 战斗规则 → 回合结构 |
| 胜负判定（`checkWin()` / `checkGameOver()` / `checkVictory()`） | 提取 return 条件表达式 | 战斗规则 → 胜负条件 | 战斗规则 → 胜负条件 |
| AI 行为（`aiMove()` / `aiDecide()` / `aiAction()`） | 提取决策优先级逻辑、目标选择条件、行为分支 | — | 战斗规则 → AI 行为说明 |
| 技能/能力（`skills` 对象 / `useAbility()` / `castSkill()`） | 提取技能名、效果描述、冷却、消耗 | 单位设计 → 技能表 | 单位设计 → 技能表 |
| 移动/寻路逻辑（`moveUnit()` / `findPath()` / `getReachableCells()`） | 提取移动范围计算规则、障碍物处理 | 战斗规则 → 移动规则 | 战斗规则 → 移动规则 |

### 2.3 活动/小玩法类专属映射

| 代码元素 | 提取规则 | → Spec 字段 |
|----------|----------|-------------|
| `score` / `points` 相关变量和计算函数 | 提取计分逻辑和加分条件 | 积分规则 |
| `timer` / `countdown` / `timeLeft` 相关逻辑 | 提取时间限制值和倒计时行为 | 时间限制 |
| `reward` / `prize` 相关数据结构和计算 | 提取奖励触发条件和数量 | 奖励规则 |
| `leaderboard` / `ranking` 相关逻辑 | 提取排名计算方式和更新时机 | 排行榜规则 |
| `daily` / `reset` / `refresh` 相关逻辑 | 提取每日重置的时间和范围 | 每日重置规则 |

### 2.4 系统/工具类专属映射

| 代码元素 | 提取规则 | → Spec 字段 |
|----------|----------|-------------|
| 输入解析函数（`parseInput()` / `loadData()` / `import_`） | 提取支持的输入格式和校验规则 | 输入规范 |
| 输出生成函数（`renderOutput()` / `export_` / `generate_`） | 提取输出格式和数据结构 | 输出规范 |
| try-catch 块中的错误类型判断 | 提取每种错误类型的处理方式 | 异常处理规则 |
| `localStorage` / `sessionStorage` / `IndexedDB` 调用 | 提取持久化的键名和数据结构 | 存储方案 |
| 处理流程的主函数调用链 | 按调用顺序整理处理步骤 | 处理流程 |

### 2.5 产品/UX 类专属映射

| 代码元素 | 提取规则 | → Spec 字段 |
|----------|----------|-------------|
| 页面/视图切换逻辑（`showPage()` / `navigateTo()` / `switchView()`） | 提取所有页面名称和跳转关系 | 导航结构 |
| 各页面的渲染函数（`renderXxxPage()` / `drawXxxView()`） | 提取每个页面的展示元素列表 | 页面清单 |
| 按钮/交互元素的事件绑定（`addEventListener` / `onclick`） | 提取交互元素的 ID、位置、行为 | 交互清单 |
| 动画相关代码（`requestAnimationFrame` / `transition` / `animate`） | 提取动画场景和参数 | 动画规范 |
| 状态显示逻辑（`showLoading()` / `showError()` / `showEmpty()`） | 提取各状态的 UI 表现 | 状态展示 |

### 2.6 叙事/剧情类专属映射

| 代码元素 | 提取规则 | → Spec 字段 |
|----------|----------|-------------|
| 节点定义（`nodes` / `STORY_DATA` 数组） | 遍历所有节点，提取 id / title / isEnding，统计总数和结局数 | 故事树结构 → 节点清单 |
| 节点间跳转关系（`nextNodeId` 字段） | 按 nextNodeId 构建节点跳转图，识别 DAG / 树形结构 | 故事树结构 → 结构图 |
| 选项定义（`choices` / `options` 数组） | 提取每个选项的 label / resultText / nextNodeId / effects[] / condition | 选项与效果规则 → 选项结构 |
| 效果执行函数（`applyEffect()` / `executeChoice()`） | 提取所有效果类型（stat_add / flag_set 等）及其逻辑 | 选项与效果规则 → 效果类型清单 |
| 条件过滤函数（`isChoiceVisible()` / `filterChoices()`） | 提取条件判断表达式 | 选项与效果规则 → 条件选项规则 |
| 玩家状态（`PlayerState` / `gameState`，排除 flags）| 提取数值型变量名 / 初始值 / 上下限 | 变量设计 → 数值型变量 |
| 旗帜变量（`state.flags` / `PlayerState.flags`） | 提取所有 flag 键名、默认值、设置时机 | 变量设计 → 旗帜型变量 |
| 结局节点（`isEnding = true`） | 提取结局 ID / 标题 / 触发条件（关键 flags 或数值门槛） | 故事树结构 → 结局分类 |

### 2.7 经济/资源流类专属映射

| 代码元素 | 提取规则 | → Spec 字段 |
|----------|----------|-------------|
| 资源定义（`resources` / `RESOURCE_DATA` 对象） | 遍历所有资源，提取 id / name / amount / cap | 资源定义表 |
| 建筑/产出源定义（`buildings` / `BUILDING_DATA`） | 提取 id / name / outputResource / outputRate / unlockCondition | 建筑定义表 |
| 升级成本函数（`calcUpgradeCost()` / `getUpgradeCost()`） | 提取成本计算公式 | 升级成本公式 |
| Tick 驱动逻辑（`gameTick()` / `setInterval` 主循环） | 提取 tick 间隔值和每 tick 的步骤调用顺序 | 经济规则 → Tick 机制 |
| 资源收集函数（`collectResource()` / `addResource()`） | 提取溢出处理逻辑和 cap 校验 | 经济规则 → 溢出与上限规则 |
| 解锁检查函数（`checkUnlock()` / `onMilestone()`） | 提取触发条件、效果和提示文案 | 里程碑/解锁事件表 |
| 死锁检测（`checkDeadlock()` 或相关注释）| 提取触发条件和处理方式 | 经济规则 → 死锁检测 |

### 2.8 构筑/卡组类专属映射

| 代码元素 | 提取规则 | → Spec 字段 |
|----------|----------|-------------|
| 卡牌定义（`cards` / `CARD_DATA` 数组） | 遍历所有卡牌，提取 id / name / cost / type / tags / baseEffect / 副本数 | 卡池设计 → 卡牌属性表 |
| 标签枚举（`card.tags` 字段枚举值） | 收集去重后的所有标签，统计每个标签的卡数 | 卡池设计 → 标签体系 |
| 协同定义（`synergies` / `SYNERGY_DATA` 数组） | 提取所有协同规则的标签对 / 触发条件 / 效果描述 / 强度评分 | 协同系统 → 协同规则表 |
| 协同检测函数（`checkSynergies()` / `calcSynergyScore()`） | 提取检测算法和分值计算公式 | 协同系统 → 协同检测逻辑 |
| 抽牌函数（`drawCards()` / `generateOffer()`） | 提取每轮展示数、抽取策略（随机/权重）、废弃处理 | 草稿机制 → 抽牌规则 |
| 草稿进程对象（`Draft` / `draftState`） | 提取当前轮数、已选列表、剩余牌池 | 草稿机制 → 草稿进程 |
| 随机种子控制（`DRAFT_SEED` / `seedRandom()`） | 提取随机源和种子控制机制 | 系统设计 → 随机性控制 |

### 2.9 数据可视化/仪表板类专属映射

| 代码元素 | 提取规则 | → Spec 字段 |
|----------|----------|-------------|
| 指标/卡片定义（`metrics` / `METRIC_DATA` / `cards` 数组） | 提取 id / label / unit / anomalyThreshold | 指标定义表 |
| 预设数据集（`datasets` / `DATASET_DATA` 对象） | 提取所有数据集 id / 名称 / 描述 / 触发异常的指标 | 预设数据集表 |
| 异常判定函数（`isAnomaly()` / `checkAnomaly()`） | 提取判定表达式和阈值逻辑 | 异常检测规则 → 判定逻辑 |
| 多异常优先级排序（`sortCards()` / `rankAnomalies()`） | 提取排序规则和最大高亮数 | 异常检测规则 → 多异常优先级 |
| 布局配置（`layout` / `LAYOUT_CONFIG` 数组） | 提取每张卡的行/列位置和占格数 | 布局设计 → 卡片布局 |
| 图表渲染函数（`renderChart()` / `drawChart()`） | 提取图表类型 / 用途 / 数据格式要求 | 图表规格 → 图表类型与用途 |
| 时间粒度枚举（`timeGranularity` / `granularity`） | 提取支持的粒度选项和对应数据点数 | 图表规格 → 时间粒度 |

### 2.10 表单/流程类专属映射

| 代码元素 | 提取规则 | → Spec 字段 |
|----------|----------|-------------|
| 步骤定义（`steps` / `STEP_CONFIG` 数组） | 提取每步的 stepIndex / title / fields[] | 字段设计 → 步骤结构 |
| 字段配置（`FIELD_CONFIG` / `steps[].fields`） | 提取 id / label / type / required / validation / conditionalOn | 字段设计 → 完整字段清单 |
| 条件显示函数（`isFieldVisible()` / `conditionalOn` 逻辑） | 提取所有条件依赖关系，绘制依赖图 | 字段设计 → 条件字段依赖关系 |
| 字段校验函数（`validateField()` / `VALIDATION_RULES`） | 提取校验时机（失焦/提交）/ 规则描述 / 错误提示文案 | 校验规则 → 字段级校验 |
| 跨字段校验（`validateStep()` / `validateForm()` 内的跨字段逻辑） | 提取涉及字段 / 规则 / 触发时机 / 错误展示位置 | 校验规则 → 跨字段校验 |
| 步骤解锁条件（`canProceed()` / 下一步按钮禁用逻辑） | 提取每步的必填项校验通过列表 | 校验规则 → 步骤解锁条件 |
| 提交函数（`onSubmit()` / `submitForm()`） | 提取提交前置检查顺序 / loading 展示 / 成功/失败处理 | 提交与结果 |
| 数据持久化（`FormState` 的跨步骤保留逻辑） | 提取前进/后退/提交失败时的数据保留策略 | 流程设计 → 数据持久化 |

---

## 三、映射配置扩展示例

### 场景：项目有特殊"技能冷却系统"，默认映射未覆盖

在 `mapping-config.json` 中添加：

```json
{
  "custom_mappings": [
    {
      "code_pattern": "cooldown|CD_|skill_cooldown|coolDown",
      "extract_rule": "搜索所有涉及冷却的变量和逻辑，提取：(1) 每个技能的基础冷却回合数 (2) 冷却是否共享 (3) 冷却中的技能是否可用 (4) 冷却减少机制",
      "spec_field": "战斗规则 → 技能冷却系统",
      "design_doc_field": "战斗规则 → 技能冷却规则"
    }
  ]
}
```

### 场景：映射到现有公司策划文档模板的自定义字段

```json
{
  "custom_mappings": [
    {
      "code_pattern": "BALANCE_RATIO|balance_target",
      "extract_rule": "提取平衡目标数值（如：期望 5 回合内结束、期望先手胜率 55% 等）",
      "spec_field": "数值设计 → 平衡目标",
      "design_doc_field": "第四章 → 数值平衡 → 设计目标"
    }
  ]
}
```

---

## 四、映射失效处理协议

提取过程中若出现以下情况，**禁止静默跳过**，必须显式报错并暂停：

### 4.1 失效触发条件

| 情形 | 说明 |
|------|------|
| 默认 pattern 未匹配到任何代码元素 | 例：搜索 `calcDamage / damage / applyDamage` 均无结果 |
| 映射结果为空但 Spec 字段标注为"必填" | 模板中无"无则填'无'"兜底的字段 |
| 代码中存在同语义但不同命名的函数 | 例：伤害函数叫 `computeDmg()` 而非规范命名 |

### 4.2 失效时的处理流程

```
检测到 pattern 未命中
        │
        ▼
AI 停止提取，输出报错：
  [映射失效] 字段：{Spec 字段名}
  预期 pattern：{规范命名}
  实际代码中发现：{实际函数名/变量名（若能识别）}
  影响章节：{Spec 模板 §X.X}
        │
        ▼
AI 提出修复方案（二选一）：
  方案A：确认原型命名不规范 → 提示设计者修改原型代码使其符合 01 规范命名
  方案B：原型命名有意不同 → AI 提议新的 custom_mapping 条目（含 code_pattern + extract_rule）
        │
        ▼
设计者确认方案 → 若选方案B：
  1. 先将新 mapping 写入 mapping-config.json（与原型同目录）
  2. 再继续提取，不可在未记录的情况下直接提取
```

> **禁止行为**：发现命名不匹配后直接猜测映射关系、静默跳过字段、填入"无法提取"后继续——这些行为会导致 Spec 字段缺失但无法被发现。

### 4.3 命名合规性检查

AI 提取前先扫描原型代码，对照 `02-html-prototype-spec.md` 规范命名，标注不合规的函数/变量名。合规检查通过后再开始提取，可减少提取中途报错的频率。

---

## 五、Spec 文档的代码溯源标注

AI 提取 Spec 时，每个条目**必须标注来源**，确保可追溯：

```markdown
### 伤害公式
伤害 = ATK × 1.5 − DEF × 0.5（最少 1 点）

> 来源：原型代码 L142-L148（calcDamage 函数）
```

标注格式：`> 来源：原型代码 L{起始行}-L{结束行}（{函数名} 函数）`

---

## 六、策划文档自动预填规则

> AI 在「开始 Spec 提取」指令触发后，同步执行本段规则预填策划文档。

### 6.1 预填数据来源与优先级

| 优先级 | 数据来源 | 预填字段范围 |
|--------|---------|-------------|
| 1 | MVP 设计文档 | 功能概述、单位/角色定义、回合结构、配置项清单、已知问题 |
| 2 | 原型代码扫描 | CONFIG 参数表、函数清单、事件清单、状态定义、TODO/FIXME 注释 |
| 3 | 映射配置表（03） | 「→ 策划文档字段」列命中项 |

### 6.2 game/product 模板（WHY 文档）预填分工

| 章节 | AI 预填内容 | 策划补填内容 |
|------|-----------|------------|
| 一、设计背景 | 原型文件路径 + Spec 文档路径（自动填入） | 1.1 要解决的问题、1.2 核心假设、1.3 验证结论 |
| 二、玩法概述 | 2.3 玩法分类（从原型类型推断勾选） | 2.1 一句话描述、2.2 核心循环 |
| 三、设计意图（game）/ 三、设计决策（product） | 无（标记"待策划填写"） | 全部人工填写 |
| 四、数值平衡目标（game 专属） | 4.2 关键数值的默认值（从 CONFIG 提取） | 平衡判据、设计理由 |
| 五、类型专项 | 标记对应类型章节为"填写"状态 | 全部人工填写 |
| 六、验收标准 | 6.1 玩法验收项（从 MVP 验收清单迁移） | 验收结果勾选 |
| 七、用户研究记录 | 无（标记"待策划填写"） | 全部人工填写 |
| 八、后续迭代方向 | 已知问题清单（从 TODO/FIXME 提取） | 优先级、解决方向 |

### 6.3 project 模板（WHAT+HOW 文档）预填分工

| 章节 | AI 预填内容 | 策划补填内容 |
|------|-----------|------------|
| 简介 | 名词解释（从代码术语推断） | 设计目的、设计内容 |
| 方案概述 | 无（标记"待补原型图"） | 原型图 + 文字描述 |
| 设计决策理由 | 无（标记"从 game/product 文档迁移"） | 关键决策记录 |
| 系统功能 | 模块结构 + 规则（从代码函数清单 + 事件清单推断） | 细则补全 |
| 页面需求 | 页面清单（如有 UI 切换逻辑则提取） | 功能描述、入口、状态 |
| 埋点需求 | 标记"待策划填写" | 全部人工填写 |
| 动效需求 | 标记"待策划填写" | 全部人工填写 |
| 音效需求 | 标记"待策划填写" | 全部人工填写 |
| 多语言 key | 提取代码中的硬编码文本 → 生成 key 建议 | 英文翻译、使用位置确认 |

### 6.4 预填标记约定

AI 预填策划文档时使用以下标记：

| 标记 | 含义 | 示例 |
|------|------|------|
| `> [AI 预填]` | 该字段/表格由 AI 从代码/MVP 提取 | `> [AI 预填] 来源：MVP 文档 §3 + 原型代码 CONFIG` |
| `[待策划填写]` | 该段需要策划人工填写 | `1.2 核心假设：[待策划填写]` |
| `[待验证]` | AI 推断但不确定的内容 | `伤害公式：[待验证] ATK × 1.5 − DEF × 0.5` |


