# AI_INDEX · 文件路由表
> **用法**：AI 每轮对话前按本文路由加载文件，避免盲目全读或遗漏关键文件。> **维护**：文件增减时同步更新本表。Orson 无需手动维护。
---

## 启动必读（每次对话开始）

| 优先级 | 文件 | 职责 |
|--------|------|------|
| 1 | heartbeat-state.md | 检查上轮收尾状态 |
| 2 | AGENT.md | 全局协作规则 |
| 3 | memory.md | 近期活跃模式 |
| 4 | NOW.md | 当前在哪一步 |

---

## 按需路由（根据NOW.md 上下文选读）
### 工作区容器
> **项目工作铁律**：每次针对 #PROJECT/<项目名>/ 里的项目进行工作前，**必须先读取该项目的** README.md（即项目 INDEX 文件），学习并执行其中的「工作规则」「目录结构」「注意事项」。如果没有 README.md，先按 AGENT.md 中的标准模板创建再开展后续工作。
| 触发条件 | 文件 |
|----------|------|
| 启动新项目、继续已有项目工作 | #PROJECT/<项目名>/README.md（必读，项目 INDEX） |
| 进入游戏案例库前 | #Game-TearDown/README.md（必读，案例库 INDEX） |
| 查询知识库、需要方法论支持 | #LLM-WIKI/README.md → #LLM-WIKI/AGENTS.md → 按主题深入 domains/ / wiki/ |
| 需要游戏案例/拆解实证 | #Game-TearDown/README.md → 对应 <游戏名>/README.md → 按需深入 overview/gameplay/systems/numbers/ux/notes |
| 需要滑行填充解谜案例（Longcat） | #Game-TearDown/Longcat/README.md → gameplay/核心机制拆解.md（规则伪代码）、numbers/难度曲线实证数据.md（50关基准）、systems/关卡系统.md（生成器架构）、notes/对微信小游戏项目的启示.md |
| 需要确认知识库指令或触发词 | #LLM-WIKI/COMMAND_MANUAL.md |
| 查看临时草稿、实验性输出 | #AI-NOTEBOOK/ 下对应文件 |
| 读取手动下载的源文件 | #DOWNLOAD/ 下对应文件 |

### 历史项目（已迁移至#PROJECT）
| 触发条件 | 文件 |
|----------|------|
| 讨论 Project ZH | #PROJECT/Project-ZH/README.md |
| 查看操作历史 | #PROJECT/Project-ZH/CHANGELOG.md |
| 讨论 HeroGuide（勇者引路人） | #PROJECT/HeroGuide/README.md |
| HeroGuide 核心玩法 | #PROJECT/HeroGuide/GDD/01-核心玩法.md |
| HeroGuide 寻路设计 | #PROJECT/HeroGuide/GDD/02-寻路与AI设计.md |
| 讨论 Brainstorm-GodotGame（脑暴项目） | #PROJECT/Brainstorm/brainStorm-0804/README.md |
| GodotGame 脑暴日志 | #PROJECT/Brainstorm/brainStorm-0804/00-脑暴日志.md |
| 讨论 Godot-RogueIdle（放置肉鸽） | #PROJECT/Godot-RogueIdle/README.md |
| RogueIdle 战斗系统 | #PROJECT/Godot-RogueIdle/GDD/01-战斗系统/ |
| RogueIdle 地图系统 | #PROJECT/Godot-RogueIdle/GDD/02-地图系统/ |
| RogueIdle 装备系统 | #PROJECT/Godot-RogueIdle/GDD/03-装备系统/ |
| RogueIdle 技能系统 | #PROJECT/Godot-RogueIdle/GDD/04-技能系统 |
| RogueIdle 英雄职业 | #PROJECT/Godot-RogueIdle/GDD/05-英雄职业/ |
| RogueIdle 局外养成 | #PROJECT/Godot-RogueIdle/GDD/06-局外养成 |
| RogueIdle 技术架构 | #PROJECT/Godot-RogueIdle/GDD/07-技术架构 |
| RogueIdle 项目计划 | #PROJECT/Godot-RogueIdle/project-plan/ |
| 讨论 Godot-WeChat Mini Game（微信小程序小游戏） | #PROJECT/Brainstorm/brainStorm-0807/README.md |
| Godot-WeChat 脑暴日志 | #PROJECT/Brainstorm/brainStorm-0807/00-脑暴日志.md |
| 骰子战斗游戏概念设计 | #PROJECT/Brainstorm/brainStorm-0807/dice-game-concept.md |
| 讨论 DiceMonster（骰子打怪） | #PROJECT/DiceMonster/README.md |
| DiceMonster GDD 总览 | #PROJECT/DiceMonster/GDD/README.md |
| DiceMonster 各模块（核心循环/骰子/牌型/战斗/关卡/UI/音效/数值/技术/扩展/肉鸽能力/装备系统） | #PROJECT/DiceMonster/GDD/01-核心循环.md ~ 12-装备系统.md |
| DiceMonster 肉鸽能力设计 | #PROJECT/DiceMonster/GDD/11-肉鸽能力.md |
| DiceMonster 装备系统设计 | #PROJECT/DiceMonster/GDD/12-装备系统.md |
| DiceMonster 开发计划 | #PROJECT/DiceMonster/project-plan/README.md |
| 讨论 longcat（微信小游戏·滑行填充+Roguelike） | #PROJECT/longcat/README.md（工作代号，正式名待定） |
| longcat GDD（四阶段规范） | #PROJECT/longcat/GDD/README.md → 00_concept → 01_top_design → 02_architecture → 03_systems（S01~S05） |
| Longcat 拆解数据回查 | #Game-TearDown/Longcat/ 下对应子目录 |

---

## 默认不读（避免污染）

| 路径 | 原因 |
|------|------|
| meta-agent-collab/ | 框架教学文档，日常协作不需要 |
| #LLM-WIKI/system/ | 知识库内部协议与维护脚本，仅在知识库任务中按需读取 |
