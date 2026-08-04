# BUILD_GUIDE · 专家发现与加载

## 一、发现算法

1. 读取 `../system/registry/KNOWLEDGE_SCOPE.md`，确认专家层已启用。
2. 扫描 `../domains/*.md` 的 frontmatter，不读取正文知识。
3. 只接受 `agent_type: role|context|personal|none`。
4. `role` / `context` 的 `prompt` 必须是 `prompts/` 下的相对路径且文件存在。
5. 根据任务选择最少必要的 role；只有单 role 无法覆盖关键变量时才组合。

没有合法 role prompt 时，专家模式明确报告“尚未配置”，不得用通用聊天能力伪装专家。

## 二、执行链

```text
自动识别专业任务
→ QUERY_PROTOCOL 决定 L0/L1/L2/Web
→ 读取 EXPERT_PROTOCOL + CONTEXT_CONTRACT
→ 动态发现最少 role/context
→ 静默使用，不显示身份

显式“专家模式”
→ 同一加载链
→ 首行显示实际加载的 role
→ 本轮结束后不保留状态
```

L0 只加载共享协议与 role prompt，不读取 domain / Wiki / raw。L1/L2 才按 Query 结果读取相关 domain 和 Wiki。

## 三、组合边界

- role 先分别给出本域约束，再由主任务统一取舍。
- context 只补稳定约束，不独立作答。
- 不为“全面”全量加载 prompt。
- `personal` 和 `none` 永远不进入自动或显式专家加载。
