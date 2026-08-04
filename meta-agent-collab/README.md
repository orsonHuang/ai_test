# meta-agent-collab · 搭建你自己的 AI 协作框架

> **本目录是什么**：把"我和 AI 协作的这套框架"沉淀成可传播的指导。
> **目标读者**：未来想搭类似框架的人 / 未来的我（每隔一段时间回看是否过时）。
> **核心比喻 · 种子，不是模板**：希望它像一颗种子，种在别人的地里，可以长成大树，不一定和我的这棵完全一样，但是枝干一样健壮。

---

## 这个目录的写作原则

由"种子比喻"派生：

1. **讲为什么，不讲必须怎样**——重点是"为什么这样长"的原理，而不是"必须按 1-2-3 步抄答案"
2. **留生长空间**——读者的项目类型、个人姿态、协作节奏都和我不同；指导要让他们能**改写而不破坏骨架**
3. **真实样本 > 抽象规范**——具体案例（"我犯过这个错，所以加了这条规则"）比"规则总览"更有教学价值。**但样本须脱敏**：用「已有项目」「某次」替代项目名和具体日期——保留模式和判断逻辑，去掉项目指纹，让读者关注方法论自身
4. **诚实暴露失败**——只展示成功的部分会变成"看起来很美但没法学"；犯错记录是这套框架的**核心特性**之一，必须讲

---

## 这个目录不是什么

- **不是元层契约**——契约在上级目录的 `AGENT.md / PRODUCER_PROFILE.md`
- **不是当前协作状态**——当前在哪一步去 `NOW.md`
- **不是已成型的方法论**——本框架是"边长边记"，不假装权威

---

## AI 不读

- 本目录已加入 `../AI_INDEX.md` 默认不读清单
- AI 在**本工作区日常协作时**不打开本目录——它不是协作契约，读了反而会试图"按教学品的标准要求自己"，引入风格偏移
- **例外 1**：本工作区的制作人显式点名让 AI 帮写/审本目录内容时
- **例外 2 · 重要**：当本目录被复制/分享到**别的工作区**，由那里的 AI 按 `ai-bootstrap/` 帮新读者搭建框架时——此时 AI **必须读** `ai-bootstrap/`，这是它的工作指令

---

## 维护与分发

### 源头维护

- **改动频率极低**——搭建完成后，日常协作不触及本目录。只在框架发生显著演化时才回写
- **git 足够，不建 CHANGELOG**——howto 没有 breaking change 概念，改动频率低到 `git log` 可追溯。搭建阶段的 CHANGELOG 对接收者无意义
- **什么值得写进 howto**（判据）：① 同一模式被 ≥2 次实战验证 ② 框架演化改变了某篇 howto 的前提假设 ③ 被外部追问"这个怎么做的"
- **commit message 前缀**：本目录的 commit 用 `howto:` 前缀

### 分发模型

- **单一权威源**：只有源头发布更新。接收者不该修改 howto——防止方法论碎片化
- **定制化发生在框架层**：接收者改自己的 `AGENT.md` / `heartbeat` / `memory`，不改 howto。同一种子，不同土壤长成不同形态
- **更新方式**：源头发新版 → 接收者覆盖 howto 目录 → 看「最后更新」判断自己的框架是否需要调整

---

## 已有文章

### 起步（搭建者先读）
- `gradual-adoption.md` · 从零搭一套的渐进生长节奏（**stable**，迭代中）
- `element-decoupling-and-assembly.md` · 零件解耦与按需组装（**draft**，初稿）

### 框架核心机制
- `three-layer-agent.md` · 三层 AGENT 体系（**stable**，迭代中）
- `wrap-up-thinking.md` · 工作单元收尾的思想（**stable**，迭代中）
- `belief-and-decision-rhythm.md` · 信念度 + plan/ask/craft 决策节奏（**stable**）
- `cross-day-memory.md` · 跨日 AI 协作的"记忆外置"机制（**stable**，迭代中）
- `mistake-as-record-samples.md` · 犯错即记录的原则与指引（**stable**，迭代中）
- `derived-card-mechanics.md` · 衍生卡机制（**draft**，重塑中）

### 工程化
- `doc-ecosystem.md` · 文档生态全貌（**draft**，重塑中）
- `doc-health-engineering.md` · 文档健康度工程化（**stable**，迭代中）
- `context-budget-engineering.md` · Token 预算工程（**stable**，迭代中）
- `design-code-bidirectional.md` · 设计-代码双向影响（**draft**，重塑中）

### 设计哲学
- `spec-driven-dev.md` · spec 先行开发模式（**stable**，迭代中）
- `why-producer-profile.md` · PRODUCER_PROFILE 的存在理由（**stable**，迭代中）
- `framework-self-improvement-arc.md` · 框架自我硬化故事弧（**stable**，迭代中）
- `reusable-agent-skills.md` · 可复用 Agent Skills（**draft**，alpha）

---

## 搭建工具

- `ai-bootstrap/` — AI 帮新读者搭建框架的入口工具包（含问答清单、搭建顺序、信号速查表、文件模板）。由搭建 AI 按本目录在新读者工作区执行

---

## 最后更新

> 给接收者快速判断「这份 howto 比上次多了什么」

- 2026-06-04: `ai-bootstrap/` 重构——搭建路径从线性改为 5 条分支（对应 `element-decoupling-and-assembly.md` 的 A~E 组合）；新增 03-signal-sheet.md（信号速查表）；新增 5 个缺失模板（heartbeat / memory / CHANGELOG / AI_SELF_CHECK / AI_SOFT_HINTS）；移除 COLLABORATION 独立模板（已合并到 AGENT）；01 问题清单重写为通俗化 + 虚构示例
- 2026-06-04: 全部文章状态标注统一为 `stable / draft / outdated` 三态+括号补充（以身作则对齐 `doc-health-engineering.md` 推荐体系）
