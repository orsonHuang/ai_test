# AI_INDEX · 文件路由表

> **用途**：AI 每轮对话前按本文路由加载文件，避免盲目全读或遗漏关键文件。
> **维护**：文件增减时同步更新本表。Orson 无需手动维护。

---

## 启动必读（每次对话开始）

| 优先级 | 文件 | 职责 |
|--------|------|------|
| 1 | `heartbeat-state.md` | 检查上轮收尾状态 |
| 2 | `AGENT.md` | 全局协作规则 |
| 3 | `memory.md` | 近期活跃模式 |
| 4 | `NOW.md` | 当前在哪一步 |

---

## 按需路由（根据 NOW.md 上下文选读）

### 工作区容器

> **项目工作铁律**：每次针对 `#PROJECT/<项目名>/` 里的项目进行工作前，**必须先读取该项目的 `README.md`**，了解项目结构、工作流与注意事项。如果该项目没有 `README.md`，先建 README 再开展后续工作。

| 触发条件 | 文件 |
|----------|------|
| 启动新项目、继续已有项目工作 | `#PROJECT/<项目名>/README.md`（必读） |
| 查询知识库、需要方法论支持 | `#LLM-WIKI/README.md` → `#LLM-WIKI/AGENTS.md` → 按主题深入 `domains/` / `wiki/` |
| 需要确认知识库指令或触发词 | `#LLM-WIKI/COMMAND_MANUAL.md` |
| 查看临时草稿、实验性输出 | `#AI-NOTEBOOK/` 下对应文件 |
| 读取手动下载的源文件 | `#DOWNLOAD/` 下对应文件 |

### 历史项目（已迁移到 #PROJECT）

| 触发条件 | 文件 |
|----------|------|
| 讨论 Project ZH | `#PROJECT/Project-ZH/README.md` |
| 查看操作历史 | `#PROJECT/Project-ZH/CHANGELOG.md` |
| 讨论 HeroGuide（勇者引路人） | `#PROJECT/HeroGuide/README.md` |
| HeroGuide 核心玩法 | `#PROJECT/HeroGuide/GDD/01-核心玩法.md` |
| HeroGuide 寻路设计 | `#PROJECT/HeroGuide/GDD/02-寻路与AI设计.md` |
| 讨论 Brainstorm-GodotGame（脑暴项目） | `#PROJECT/Brainstorm-GodotGame/README.md` |
| GodotGame 脑暴日志 | `#PROJECT/Brainstorm-GodotGame/00-脑暴日志.md` |
| 讨论 Godot-RogueIdle（放置肉鸽） | `#PROJECT/Godot-RogueIdle/README.md` |
| RogueIdle 战斗系统 | `#PROJECT/Godot-RogueIdle/GDD/01-战斗系统/` |
| RogueIdle 地图系统 | `#PROJECT/Godot-RogueIdle/GDD/02-地图系统/` |
| RogueIdle 装备系统 | `#PROJECT/Godot-RogueIdle/GDD/03-装备系统/` |
| RogueIdle 技能系统 | `#PROJECT/Godot-RogueIdle/GDD/04-技能系统/` |
| RogueIdle 英雄职业 | `#PROJECT/Godot-RogueIdle/GDD/05-英雄职业/` |
| RogueIdle 局外养成 | `#PROJECT/Godot-RogueIdle/GDD/06-局外养成/` |
| RogueIdle 技术架构 | `#PROJECT/Godot-RogueIdle/GDD/07-技术架构/` |
| RogueIdle 项目计划 | `#PROJECT/Godot-RogueIdle/project-plan/` |

---

## 默认不读（避免污染）

| 路径 | 原因 |
|------|------|
| `meta-agent-collab/` | 框架教学文档，日常协作不需要 |
| `#LLM-WIKI/system/` | 知识库内部协议与维护脚本，仅在知识库任务中按需读取 |
