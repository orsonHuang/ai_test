# Knowledge 健康检查

> Lint 默认只报告。每个问题最终落为修复、挂账或明确不处理。

## 1. 零状态

- 根 README 保留使用入口与目录树；`system/protocols/RUNTIME_ROUTING.md` 独立承担消息分发。
- raw、Wiki、domain、prompt 全为空时必须判健康。
- `system/registry/index.md`、`system/registry/quick-reference.md`、`system/registry/raw-list.md` 和状态页的计数一致。
- Query 空库停止，专家层无 prompt 时明确不可用。

## 2. Raw

- frontmatter 字段与模板一致。
- 来源和原文位置可追溯。
- raw-list 引用次数与 Wiki 反向搜索一致。
- `## 批注` 中亮点、存疑、可延伸、冗余均有消费去向；空段删除。
- `source_clipping` 指向存在且命名合规的文件。

## 3. Wiki

- frontmatter、章节来源和底部来源一致。
- domain 双向登记一致。
- Wiki 间链接带有效锚点；raw 引用使用双链。
- 相关页面不超过 5 条且说明关联命题。
- 300 行进入拆分观察；500 行拆分或挂账。

## 4. Domain 与 Agent

- domain 只导航 Wiki，不复制正文、不互链。
- `agent_type` 与 `prompt` 路径合法。
- 运行 `agent-layer-health-check.md` 和 Query / Agent 回归。

## 5. 派生状态与收尾

- 刷新 `system/registry/` 下的 index、quick-reference、raw-list、KNOWLEDGE_STATUS。
- 对账物理文件、frontmatter、索引和状态页，不沿用旧快照增量猜数。
- 检查编码、敏感信息、相对链接和 Git diff。
- 更新根目录 NOW 与 `system/maintenance/CHANGELOG.md`。
