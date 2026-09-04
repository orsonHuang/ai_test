# NOW · 当前状态锚点

> **用途**：AI 快速定位"我们现在在哪、下一步是什么"。每次对话结束更新。
> **维护**：AI 自动维护。Orson 可以随时口头更新"现在在做 X"。

---

## 当前在哪

- **主线项目**：DiceMonster（DiceMonsterTT 工程）
- **当前阶段**：GDD v2 重写完成（四阶段规范结构，首个规范试点），待确认各 analysis 待定决策
- **新开支线**：longcat（微信小游戏 · 滑行填充解谜 + 轻量 Roguelike）
  - 阶段：**GDD 四阶段已写完（18 份）**，全部 analysis 状态 `agent_proposal`，待 Orson 确认
  - 已完成：参考对象 Longcat TearDown（9 份）+ 项目骨架 + 全套 GDD
- **本轮完成**：
  - 建 `#PROJECT/longcat/`（替代原 `Cocos-Longcat` 代号目录）+ GDD 四阶段结构
  - 产出 GDD 18 份：README×2 + 00_concept/01_top_design/02_architecture 各 analysis+design + 03_systems S01~S05 各 analysis+design
  - 核心设计定调：**核心保留全覆盖（不动规则）→ 差异化全压元层（九条命 + 能力三选一）**
  - AI_INDEX 路由更新（longcat 项目 + GDD 路由）
  - 重学 DiceMonster：代码实况（TapTap Maker + Lua，core/data/ui 三层，核心闭环可玩）+ 旧 GDD 17 份 + 怪物设计总览
  - Orson 拍板 4 项：奖励=全部领取式+可放弃 / 地图=8 行行进度制 / GDD 用四阶段规范 / 未实现系统保留为规划
  - 旧 GDD 迁入 `DiceMonsterTT/GDD_旧/`；新 GDD 11 份写入 `DiceMonsterTT/GDD/`（README + 3 阶段×2 + S01~S05×2）
  - 外层项目 README 全量更新（技术选型/目录结构/SSOT 规则/状态清单）

---

## 下一步

### DiceMonster（主线，暂停中）
- Orson 确认各 analysis「待定决策」：碎片转换制（提案 1:1）、random 节点清理、附魔权重/退款修复范围
- 代码清理：死代码（3 选 1 生成器/random 配置）+ 已知缺陷（附魔退款/词条权重/转盘文案）
- 数值回收：玩家 HP 1000→100 全链路重调
- P1 落地：存档 → 外层大厅 → 结算转换 → 技能树

### longcat（新支线）
- **【阻塞·首要】** Orson 逐条确认 GDD 的 analysis 问题块（共 **34 个**：概念 5 / 顶层 6 / 架构 6 / S01 5 / S02 3 / S03 3 / S04 3 / S05 3），`agent_proposal` → `user_confirmed`
  - 建议顺序：00_concept（最上游，推翻代价最大）→ 01_top_design → 02_architecture → 03_systems
  - 可按「阶段」或「单个问题块」粒度确认，不必一次全确认
  - **确认前不动代码**
- 确认后：删除旧代号目录 `#PROJECT/Cocos-Longcat/`（需 Orson 批准）
- 并行可做：Orson 实玩 Longcat 10–15 关，验证 TearDown 中 6 项待验证推断
- 技术侧：确认 Cocos Creator 版本 → 选 MCP 插件（Funplay 3.8+ / cocos-mcp-server 3.7+ / Cocos Agent）
- GDD 定稿后：开数值表 → 执行文档 → 建 Cocos 工程

---

## 阻塞项

- **longcat**：GDD 全部 analysis 待 Orson 确认（20 个问题块）→ 确认前不动代码
- 旧代号目录 `#PROJECT/Cocos-Longcat/` 待批准后删除（内容已迁移至 `#PROJECT/longcat/`）

---

## 最近完成

- 2026-08-04：工作间目录结构规则落地 + 流程文件更新
- 2026-07-15：隐藏文件显示逻辑简化 + GDD 更新 + Git 提交 + 部署到 Lighthouse
- 2026-07-13：响应库扩展 15 条 + 成长反馈 + 侧边栏修复 + Day1 M-M 备忘
- 2026-07-12：响应库重构与智能匹配引擎上线
- 2026-07-11：generate_reply 引擎流程文档化
