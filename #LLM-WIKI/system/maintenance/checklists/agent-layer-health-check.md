# Agent 层健康检查

- [ ] `system/registry/KNOWLEDGE_SCOPE.md` 明确专家层是否启用。
- [ ] 每个 domain 的 `agent_type` 为 `role|context|personal|none`。
- [ ] role / context 的 `prompt` 位于 `agents/prompts/` 且存在。
- [ ] personal / none 没有被自动加载。
- [ ] prompt 不复制共享协议、domain 正文或易漂移状态。
- [ ] `BUILD_GUIDE.md` 只做动态发现，没有硬编码领域矩阵。
- [ ] 根 README 只指向 `system/protocols/RUNTIME_ROUTING.md`；运行路由再分发 Query 与专家协议。
- [ ] 自动调用不显示身份；显式专家模式才显示实际 role。
- [ ] 空 prompts 目录时专家模式明确不可用。
- [ ] `run-query-agent-contract.ps1` 通过。
- [ ] 行为场景按 `query-agent-behavior-check.md` 抽查。
