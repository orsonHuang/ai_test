<!-- knowledge-identity:display-name -->
# Knowledge Base · AI 协作规则

## WHAT · 覆盖范围

本文件约束本知识库内的查询、入库、维护、专家加载和文件编辑。知识内容范围由 `system/registry/KNOWLEDGE_SCOPE.md` 定义。

## WHY · 设计目标

知识库必须在脱离原始工作区后仍可运行，并保持来源可追溯、人审可控制、知识可累积、空库状态合法。

## HOW · 协作规则

1. 新会话进入本库、任务类型变化或当前路由不明时读 `system/protocols/RUNTIME_ROUTING.md`；同一任务后续消息沿用已确定协议。`COMMAND_MANUAL.md` 只在触发词不明、指令冲突或用户询问指令时读取，不得逐消息完整扫描。
2. 编辑既有文件前先读取当前内容；不凭记忆覆盖。
3. Query 默认只读；模糊写入意图先确认。
4. Ingest 严格执行四个审核闸门。用户确认当前阶段不授权后续阶段。
5. 外部来源 → raw → Wiki → domain 单向沉淀；不得用无来源经验改写 raw。
6. 评分相关性必须引用 `system/registry/KNOWLEDGE_SCOPE.md`；范围未配置时先补最小信息。
7. raw、Wiki、domain 和专家模板分别就近放在对应内容目录，作为格式 SSOT。
8. Wiki 新建、拆分、链接和来源标注按 `wiki/README.md` 与 `system/protocols/WIKI-LINK-STANDARD.md`。
9. domain 只做导航，不复制 Wiki 正文；域变更同步 `domains/README.md`。
10. 专家层默认休眠；无匹配 prompt 时不得宣称专家身份或能力。
11. IMA 仅在本地配置 `enabled: true` 时加载；密钥不得写入仓库。
12. 根 README 是唯一使用者说明入口；不得拆出 USER_GUIDE，也不得把小白说明复制进 `COMMAND_MANUAL.md`。
13. 所有文本使用 UTF-8、LF、无 BOM；相对链接不得依赖父目录。
14. 修改后执行相关清单和回归；失败必须可见，不在红灯状态下继续。
15. 删除、批量改写、覆盖配置、目录重命名和外部写入必须先确认。
16. 维护记录追加到 `system/maintenance/CHANGELOG.md`，当前焦点同步根目录 `NOW.md`。
17. `NOW.md` 只保留固定六节，使用替换而非追加；快照必须与 `system/registry/KNOWLEDGE_STATUS.md` 一致，历史进入 CHANGELOG，正文不得超过 45 行。

## 互链边界

- raw 的来源关系和 Wiki 对 raw 的引用可用 `[[raw-sources/...]]`。
- Wiki 之间统一使用带标题锚点的 Markdown 相对链接。
- README、协议、状态、domain、prompt 和参考文档不产生 Obsidian 双链。

## 维护入口

任何写入完成后按 `system/maintenance/README.md` 执行最小维护链。Lint 默认只报告问题；用户确认后才修复。
