# 可复用 Agent Skills · 给模块层加一个"任务维度"

> **状态**：draft（alpha，尚未经实战验证）
> **本文是什么**：聊聊在当前三层 AGENT 体系之外，增加一种按**任务类型**而非项目位置触发的可复用能力包——Skills。
> **不是什么**：Skill 管理平台说明 / 具体技术实现指南。
> **灵感来源**：WorkBuddy 的 Skills 体系 + 当前框架中 `context-budget-engineering.md` 的"按需租金"理念。

---

## 核心想法（2 段）

**问题**：当前三层 AGENT 的加载逻辑是**位置触发**——你在哪个项目/模块，就读哪层的 AGENT。但有些能力跨越项目边界，比如"代码评审"、"写周报"、"合同审核"——它们在多个项目中出现，但按当前位置读不到。

**解法**：引入 **Skills**——按任务类型触发的可复用能力包。Skill 不在模块层或项目层里，而是独立存在。AI 命中某个任务类型时才加载，不占固定租金。

---

## Skill 是什么

| 维度 | 模块层（现有） | Skills（新增） |
|------|-------------|-------------|
| 触发方式 | 位置触发——"你在 combat 目录下" | 任务触发——"你要做代码评审" |
| 加载时机 | 进入模块时必读 | 命中任务类型时才加载 |
| 复用范围 | 项目/模块内自洽 | 跨项目可分发 |
| 打包结构 | README + spec/ | SKILL.md + scripts/ + references/ + assets/ |

核心区别：**模块层是局域的（在哪做什么），Skills 是跨域的（做什么，无论在哪）**。

---

## Skill 的打包结构

```
my-skill/
├── SKILL.md        ← 入口：何时触发 + 工作流步骤 + 指向子资源
├── scripts/        ← 可执行脚本（可选）
├── references/     ← 领域参考知识（可选）
└── assets/         ← 模板、样例等静态资源（可选）
```

`SKILL.md` 是最小存在——其他子目录按需出现。这和"模块层 = README + spec"的拆分逻辑一致。

---

## 何时建一个 Skill（判据）

从 `memory.md` 的 3 次晋升机制延伸：

> 同一任务类型在 **≥3 个不同项目/模块**中出现 → 建 Skill

反例（不建 Skill）：
- 只在单个项目内重复 → 进项目层 checklist 即可
- 任务有强位置耦合（"combat 系统的 damage floor"）→ 放模块 spec
- 一次性的、不会再出现的 → 不建

---

## 与 AI_INDEX 的路由集成

`AI_INDEX.md` 当前按"文件位置"路由。引入 Skills 后需要额外的**任务→Skill 映射**：

```
AI_INDEX 追加：
├── Skills 路由（任务类型 → skill 目录）
│   ├── 代码评审     → skills/code-review/
│   ├── 周报生成     → skills/weekly-report/
│   └── ...
```

AI 遇到用户说"帮我 review 一下这段代码"时：
1. 先检查 AI_INDEX 的 Skills 路由
2. 命中 "代码评审" → 加载 `skills/code-review/SKILL.md`
3. 按 SKILL.md 中定义的工作流执行
4. **不需要**用户手动 @引用（这与引用普通文件不同——Skills 是自路由的）

---

## 与现有框架的交叉引用

| 现有文件 | 与 Skills 的关系 |
|---------|-----------------|
| `context-budget-engineering.md` | Skills 是"按需租金"的终极形态——只在命中任务时加载，不占固定租金 |
| `three-layer-agent.md` | Skills 是三层之外的**水平补充**——不是第 4 层，是正交维度 |
| `memory.md` | Skill 的建判据（≥3 次跨项目出现）直接继承 memory 的 3 次晋升机制 |
| `AI_INDEX.md` | 需要新增任务→Skill 的路由条目 |

---

## 三层 + Skills 的关系图

```
          任务维度（横切）
          ────────────────→
          │ 代码评审  周报  合同审核  ...
          │  Skill   Skill   Skill
          │
位置      │
维度      │
  ↓       │
全局层 AGENT.md          ← 跨项目通用
项目层 AGENT.md          ← 项目特定
模块层 README + spec/    ← 模块特定
```

模块层回答"在哪做什么"，Skills 回答"做什么，无论在哪"——两者正交，不替换。

---

## 对 Game 项目的反哺

当前 BattleLine / DiceTemple 各有一套独立的 `docs/` 体系。引入 Skills 后可以考虑：

- **`skills/code-review/`**：跨 BattleLine + DiceTemple 的 JS 代码评审标准（不再每个项目各写一份）
- **`skills/game-design-review/`**：设计文档评审模板
- **`skills/release-checklist/`**：发布前检查清单

这些目前散落在各项目层 AGENT 或 checklist 中，适合提升到 Skills 层。

---

## 给"想搭这套"的人的建议

- **Skills 不是必须的**：如果所有任务都绑定在单个项目内，模块层就够了。跨项目需求出现之前，不要为了架构完整性硬建 Skill
- **从 checklist 自然晋升**：项目中重复出现的 checklist → 提取为 Skill。不要从零设计
- **SKILL.md 保持短**：和 AGENT 一样，核心工作流 ≤100 行，细节放 references/
- **触发路由不要过度自动化**：AI_INDEX 里写"代码评审 → skills/code-review/"作为建议路由即可，AI 仍然可以按场景判断是否需要

---