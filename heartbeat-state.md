# HEARTBEAT · 心跳状态

> **用途**：对话启动 + AI 输出结束时读取。由本文自主判断收尾状态，多一层保底。
> **维护**：AI 每轮输出结束时自动更新。不应手动编辑。

---

## 会话启动时

> 上轮对话是否正常收尾？检查「上次收尾状态」→ 未收尾 → 先补收尾再回应新消息。

---

## 输出结束时 · 自主判断

> 本段由 heartbeat-state.md 自己承载判断逻辑——不依赖 AI 记住。

1. 读「未 commit 改动」字段
2. **若 = 是**：
   - 本轮有文件写入/修改？→ 收尾条件成立
   - 用户本消息含「收尾 / 收工 / 完成 / 提交」？→ 收尾意图确认
   - 收尾流程是否已在本轮跑过？（看下方「wrap-up 完成」字段）
   - **若需要收尾且未跑过** → 立即执行收尾三件套（更新 memory + NOW + 追加 observations），全部完成后最后一步 commit
   - **若已跑过** → 跳过
3. **若 = 否** → 无需动作

---

last_heartbeat_started_at: 2026-09-04
last_reviewed_change_at: 2026-09-04
last_heartbeat_result: OK

## 上次收尾状态
- wrap-up 完成: 是
- observations 追加: 否
- NOW 更新: 是（第二轮：longcat GDD 18 份写完，阻塞项改为「20 个 analysis 问题块待确认」）
- memory 更新: 是（追加 2026-09-04 第二轮条目：GDD 18 份 + 核心设计定调 + 架构四条铁律 + 关键决策摘录）
- memory 衰减检查: 否（本轮未检查）
- AI_INDEX 更新: 是（第二轮：路由 Cocos-Longcat → longcat，新增 GDD 四阶段路由）
- 未 commit 改动: **是**（本轮新增 `#PROJECT/longcat/` 18 份；上轮 `#Game-TearDown/Longcat/` 9 份未提交；改动 AI_INDEX.md / NOW.md / memory.md / 本文件）
- commit 状态: 未执行（Orson 未要求，按全局规则不主动 commit）

## 下轮启动提示
- **首要阻塞**：`#PROJECT/longcat/GDD/` 全部 analysis 为 `agent_proposal`（34 个问题块），待 Orson 确认后转 `user_confirmed`
  - 确认顺序建议：00_concept → 01_top_design → 02_architecture → 03_systems
  - **确认前不动代码**
- 次要待办：旧代号目录 `#PROJECT/Cocos-Longcat/` 待 Orson 批准后删除（内容已迁移至 `#PROJECT/longcat/`）
- 若回主线 DiceMonster：仍停在「Orson 确认各 analysis 待定决策」
