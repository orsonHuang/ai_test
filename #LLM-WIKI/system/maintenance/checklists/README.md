# checklists · 回归入口

| 文件 | 用途 |
|---|---|
| `initialization-check.md` | 初始化、改名和 IMA 状态验收 |
| `ingest-stage-gates.md` | Ingest 四阶段硬停点 |
| `knowledge-health-check.md` | 全库健康检查 |
| `agent-layer-health-check.md` | domain / prompt / 专家发现一致性 |
| `query-agent-behavior-check.md` | Query 与 Agent 行为场景 |
| `release-package-check.md` | 发布包独立性与脱敏验收 |
| `check-raw-depth.ps1` | raw 基础深度结构静态检查 |
| `check-raw-style.ps1` | raw 可扫描性静态检查 |
| `run-query-agent-contract.ps1` | Query / Agent 静态契约 |
| `run-platform-contract.ps1` | Windows / macOS 路径、解析与 PowerShell 兼容契约 |
| `run-release-contract.ps1` | 发布包总回归 |

静态脚本不能替代人工内容审核；失败时停止推进并报告具体文件。
