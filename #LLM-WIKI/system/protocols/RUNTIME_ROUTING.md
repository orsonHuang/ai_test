# RUNTIME_ROUTING · 运行时路由

> 用途：收到知识库相关消息后，先判断任务类型，再读取最少的执行文件。本文只分发，不复制各协议的实现规则。

## README 读取时机

- 新会话进入本知识库、从其他项目切换过来：读一次根 `README.md`、`NOW.md`、`AGENTS.md`，再读本文。
- 同一任务的后续消息：不重复读取 README，沿用已经确定的协议；任务类型变化时重新读本文。
- 上下文重置、无法确认目录职责时：重新执行上一条启动链。
- 修改目录、入口、规则，或检查规则文件健康度时：重新读取 README 与 AGENTS。

## 消息分发

| 消息类型 | 第一读取入口 | 后续原则 |
|---|---|---|
| 初始化、修改知识库名称或 IMA 设置 | `system/maintenance/SETUP.md` | 使用问答向导；应用前保持 dry-run |
| 普通问答、改写、分析、显式查询 | `system/protocols/QUERY_PROTOCOL.md` | 由协议决定是否读取知识内容或联网 |
| 专业诊断、设计或审查 | Query 协议 → `agents/EXPERT_PROTOCOL.md` → `agents/CONTEXT_CONTRACT.md` | `agents/BUILD_GUIDE.md` 只加载实际存在的最少方法与领域文件 |
| 内容消化、入库、处理来源 | `system/protocols/INGEST_PROTOCOL.md` | 由协议加载评分、阶段闸门、来源工具与内容规则 |
| Lint、健康检查、质量扫描 | `system/maintenance/checklists/knowledge-health-check.md` | 默认只报告，修复另行确认 |
| 当前状态、能力、缺口 | 先读根 `NOW.md` | 需要详细判断时再读 `system/registry/KNOWLEDGE_STATUS.md`；具体结论回到 domain/Wiki |
| 修改文件或框架规则 | `AGENTS.md` → `system/maintenance/README.md` | 编辑前读当前文件，完成后执行最小维护链 |

## `COMMAND_MANUAL.md` 读取时机

- 需要确认自然语言是否命中指令、同时命中多个指令，或用户询问“可以怎么说”时读取。
- 已能从本文唯一确定任务类型时不读取；不得在每条消息中完整扫描。
- 指令手册只解释触发表达，不拥有 Query、Ingest、专家或初始化规则。

## 冲突与默认

- 显式“深查 / 不查知识库 / 联网 / 不联网 / 专家模式”优先，各控制轴独立。
- 写入意图模糊时先确认；Query 默认只读。
- 同时命中多个写入流程时列出冲突并让用户排序。
- 未命中知识库任务时停止，不预读内容或维护文件。
