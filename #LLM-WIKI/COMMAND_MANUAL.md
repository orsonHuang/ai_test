# COMMAND_MANUAL · 指令手册

> 读取时机：由 `system/protocols/RUNTIME_ROUTING.md` 按需调用，用于确认触发表达或指令冲突；不得在每条消息中完整扫描。执行规则仍归对应协议所有。

## 1. 初始化知识库

触发词：初始化知识库、配置空知识库、修改知识库名称。

执行：读 `system/maintenance/SETUP.md` → 优先运行或模拟 `system/maintenance/setup-wizard.ps1` 的逐题引导 → 每题解释含义并提供推荐值和例子 → 调用底层初始化脚本 dry-run → 展示包内和包外影响 → 用户确认后应用 → 从新路径运行初始化检查。

## 2. 开始 Ingest

触发词：开始 Ingest、消化、入库、处理这篇来源。

执行：读 `system/protocols/INGEST_PROTOCOL.md` 和 `system/maintenance/checklists/ingest-stage-gates.md`。只有明确入库意图才进入；仅提供 URL 且意图不明时先确认“只读摘要还是入库”。

IMA 来源先检查 `system/integrations/ima-config.local.json`：禁用则停止并说明；启用后按 `system/integrations/IMA-GUIDE.md` 获取内容。

## 3. 查询知识库

触发词：查询知识库、深查知识库、不要查知识库、库里有没有。

执行：读 `system/protocols/QUERY_PROTOCOL.md`；显式覆盖优先于自动路由。

## 4. Lint 健康检查

触发词：Lint、健康检查、检查知识库质量。

执行：读 `system/maintenance/checklists/knowledge-health-check.md`。默认只报告问题，不自动修改。

## 5. 专家模式

触发词：专家模式、以某领域身份、切换到某领域视角。

执行：整理 ContextBrief → Query 路由 → `agents/EXPERT_PROTOCOL.md` → `agents/BUILD_GUIDE.md`。仅显式命令显示模式标签。

## 冲突处理

- 同时命中多个写入流程：列出命中项并请求排序。
- “不要查知识库”只关闭 Knowledge 检索，不自动关闭 Web。
- “不要联网”不影响读取本地知识库。
- 初始化目录重命名与其他编辑不得并行执行。
