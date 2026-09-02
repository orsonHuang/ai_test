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

last_heartbeat_started_at: 2026-09-02
last_reviewed_change_at: 2026-09-02
last_heartbeat_result: OK

## 上次收尾状态
- wrap-up 完成: 是（DiceMonster GDD v2 重写完成，旧版迁入 GDD_旧）
- observations 追加: 否（无案例观察）
- NOW 更新: 是（当前阶段更新为 GDD v2 完成待确认待定决策）
- memory 更新: 是（新增 DiceMonster 工程实况与 GDD v2 条目）
- memory 衰减检查: 否（本轮未检查）
- 未 commit 改动: 是（submodule GDD 重写 + 主仓库 README/状态文件，收尾最后一步 commit）
