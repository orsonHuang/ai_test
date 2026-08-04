# domains · 知识域规则

domain 是顶层导航，不复制 Wiki 正文。每个域一个 Markdown 文件，使用同目录 `domain.template.md`。

## 创建条件

- `system/registry/KNOWLEDGE_SCOPE.md` 明确包含该范围；或首次 Ingest 出现稳定归属需求。
- 名称能描述长期边界，不以单篇来源标题命名。

## 维护

- domain 只链接 Wiki，使用标准 Markdown 相对链接。
- domain 之间默认不互链。
- 新增、删除或重命名 domain 时同步 `system/registry/index.md`、`system/registry/quick-reference.md` 和相关 Wiki frontmatter。
- `agent_type` 仅允许 `role`、`context`、`personal` 或 `none`。

## 当前域

暂无。
