# Godot-RogueIdle

Godot / Steam 单人远征游戏项目：带三人小队，在有限区域时段内选路刷装，通过自动回合战斗攻破魔王城。

## 编辑前必读

**对本项目文件夹的新增、编辑、整理和开发，必须遵循 [AGENTS.md](AGENTS.md)。** 规则仅在本项目目录及子目录生效；包括文档、GDD、素材、HTML与Godot工程。用户最新指令优先。

cat-idle、rogue-idle-gd 是独立Godot工程；html-mvp是独立玩法原型。不能仅按目录新旧自行合并或覆盖。开始实现任务时确认具体目标工程、版本和主场景。

## 当前状态

| 内容 | 状态 |
|---|---|
| [HTML MVP](html-mvp/index.html) | 2026-10-04已交付的可玩基线；直接离线打开 |
| [原型规则与验证](html-mvp/README.md) | 反映HTML实际行为，不被新设计自动替换 |
| [GDD v1](GDD/README.md) / [总览](GDD/00-总览.md) | 2026-10-05重写的开发设计目标，含待验证改进 |
| [改版说明](docs/design/gdd-v1-改版说明.md) | 旧稿、MVP与新目标的逐项差异、理由和风险 |
| [数值CSV](GDD/data/README.md) | 已导入 cat-idle 的 53 份可编辑资源；仍需真人平衡验证 |
| [静态核验](docs/design/gdd-v1-核验记录.md) | 文档与数据检查，不能替代引擎/真人验收 |
| [Godot 可玩 Demo](cat-idle/README.md) | 2026-10-05：已通过 MCP 在 cat-idle 中实现新版闭环，F5 运行 |
| [引擎验收](docs/verification/godot-demo-v1/README.md) | 13 项规则测试、原生场景检查、正常数值通关与战中续档；M1 真人试玩待完成 |

## 开发入口

- 直接体验：打开 [cat-idle/project.godot](cat-idle/project.godot)，按 F5；主场景 [ExpeditionDemo.tscn](cat-idle/scenes/expedition/ExpeditionDemo.tscn)。地图、整备、战斗及共用组件均为原生可编辑场景，详见 [工程说明](cat-idle/README.md)。
- 玩法与系统：[GDD索引](GDD/README.md)
- 制作计划：[M0/M1垂直切片](project-plan/01-原型阶段.md)、[M2 Demo](project-plan/02-Demo阶段.md)、[M3发布准备](project-plan/03-正式版.md)
- 工程约束：[技术架构](GDD/07-技术架构/01-技术架构.md)、[场景与资源](GDD/07-技术架构/02-场景与资源规范.md)
- 编辑规范：[AGENTS.md](AGENTS.md)

新版重点：随机区域活动组合、区域首胜成长、定向套装保底、不同首领机制、有限战术预设、可解释战报。6时段、重复副本、三人队与三槽继续作为验证基础。强化、重铸、永久属性树不进入M1/M2。

## 历史与参考

- [重写前完整归档与哈希清单](docs/archive/2026-10-04-before-gdd-v1/ARCHIVE_NOTES.md)：保留旧GDD、计划、项目入口及已有未提交的两份战斗文档。
- [Godot Demo 制作前归档](docs/archive/2026-10-05-before-godot-demo/ARCHIVE_NOTES.md)：保留 cat-idle 原始工程文件；旧 Battle 场景在工程内仍保留。
- [早期流程图PNG](docs/brainstorm/game-flow-v1.png) / [SVG](docs/brainstorm/game-flow-v1.svg)：历史脑暴示意，出现旧数值时以当前GDD目标或HTML实际规则分别解释。
- 参考图/与素材包/保存来源原件；采用的资产需另记许可与处理过程。

## 版本记录

| 版本 | 日期 | 含义 |
|---|---|---|
| v0.1 / v0.2旧稿 | 2026-07至08 | 多职业、装备强化等历史设计，已归档 |
| HTML v0.1 | 2026-10-04 | 完整区域远征与自动战斗验证原型 |
| GDD v1.0 | 2026-10-05 | 以MVP重建设计、数值与制作计划；不是游戏正式版 |
| Godot Demo v1 | 2026-10-05 | M1 功能样片、原生场景及续档；不是 Steam 发布版 |
