# CHANGELOG

本文件记录知识库框架与内容的已完成变更。版本遵循语义化版本。

## [Unreleased]

### Added

- 首次 Ingest 完成：5 篇 raw 消化稿、4 个 Wiki 页面、3 个 domain（按策划岗位分类：关卡策划、系统策划、市场与商业化）
- 新建 Wiki：关卡节奏与心流设计、开放世界空间设计方法论、系统策划能力框架、游戏定价与市场趋势
- 新建 domain：关卡策划.md、系统策划.md、市场与商业化.md
- 更新 quick-reference.md、raw-list.md、KNOWLEDGE_STATUS.md、NOW.md

### Release integration

- 新增 `_release.json`，记录源 revision、生成器版本、生成时间和 manifest 哈希；该文件是发布来源标记，不是用户知识内容。
- 发布包改由 Knowledge 仓内白名单生成器单向生成；54 个业务文件保持正式树合同，版本化总文件数增加为 55。
- LF 所有权从父仓 `Knowledge-released/**` 迁入 Knowledge 的 `release-input/**` 与 `released/**`。
- 发布总契约同时校验 54 个业务文件、`_release.json` 五字段、55 个版本化运行文件和既有 13 目录合同。
- 高级初始化示例改从仓内 `released/` 运行，不再引用已退役的父仓兄弟目录。

### Added

- 新增 `system/protocols/RUNTIME_ROUTING.md`，集中定义 README 读取时机、初始化/Query/Ingest/专家/Lint/状态分发和 COMMAND_MANUAL 按需读取规则。
- 新增 `system/maintenance/setup-wizard.ps1` 小白初始化向导：7 个核心问题、逐题解释、例子、推荐值、帮助/返回/默认/退出控制和最终确认。
- 新增 `system/maintenance/setup-wizard.zh-CN.json` 作为中文问答资源；脚本保持纯 ASCII，兼容 Windows PowerShell 5.1。
- 新增 `system/maintenance/checklists/run-platform-contract.ps1`，统一检查全部脚本解析、参数期路径求值、可移植路径字面量和 macOS 文档入口。
- 新增 `system/README.md` 和空 CHANGELOG 归档，明确正式运行目录职责。

### Changed

- 推翻发布包根目录扁平方案；协议、登记表、集成与维护资产全部迁入与正式 Knowledge 同路径的 `system/`。
- 模板由根级 `_templates/` 迁到 raw、Wiki、domain 与 `agents/prompts/` 对应目录；移除根级 `_checklists/`、`scripts/` 和 `integrations/`。
- 源侧发布流程入口保持为 `Knowledge/system/maintenance/RELEASED.md`；同步目标由扁平映射改为同构路径。
- 新增 `.gitattributes`，强制 `Knowledge-released/**` 在 Git 克隆与导出时使用 LF，避免 Windows 自动换行转换破坏发布包自检。
- 默认初始化入口改为问答向导；原参数脚本保留为底层事务内核，并允许被向导连续调用 dry-run 与 `-Apply`。
- USER_GUIDE 的小白路径合并到根 README；README 同时记录唯一最终目录树，不再拆分使用说明或目录参考。
- NOW 改为固定六节、45 行上限的薄快照；详细状态继续放在 `system/registry/KNOWLEDGE_STATUS.md`，历史只进 CHANGELOG。
- README 删除详细文件路由，只保留小白使用说明、目录树与 RUNTIME_ROUTING 指针；同一任务后续消息不再重读 README 或完整指令手册。
- README 目录树使用中性根名，避免初始化改名后的旧目录身份残留；初始化身份文件收口为 README、AGENTS 与 NOW。
- 初始化与检查脚本移除参数默认值中的提前 `$PSScriptRoot` 求值；包内路径统一使用跨平台写法。
- 目录名校验改为 Windows/macOS 可移植字符并集；当前工作目录判断使用系统目录分隔符边界。

### Removed

- 删除 released 的 `docs/`、`system/guides/`、实施 PLAN、独立目录树参考和 `llm-wiki.md`；正式库的理念参考不随空库搭建包分发。

### Tests

- 发布契约固定 54 个基础文件和 13 个目录；启用 IMA 本地配置后为 55 个运行时文件，并禁止已删除路径或旧扁平路径回流。
- 发布契约新增向导脚本解析、ASCII 兼容、中文问答键、控制键和必需文件检查。
- Windows PowerShell 5.1 平台契约通过；macOS PowerShell 7 实机回归入口已建立，正式发布前仍需在 macOS 执行。
- Query/Agent 契约新增根 README 用户入口、NOW 固定结构与 NOW/KNOWLEDGE_STATUS 快照一致性检查。
- Windows 独立副本重新通过参数 dry-run、真实目录改名、身份残留扫描、IMA `configured_unverified` 与 55 文件运行态总契约。

## [0.1.0] - 2026-07-14

### Added

- 建立 51 个文件组成的领域中立空知识库框架，包含零状态入口、模板、协议、检查清单和维护说明。
- 新增事务式初始化脚本：默认 dry-run，可同步修改显示名、目录名与身份登记引用，并支持大小写专用重命名和失败回滚。
- 新增脱敏 IMA 指南、非密钥配置模板与禁用、待鉴权、未验证、已验证四态初始化。
- 新增空 Agent 层、动态专家发现规则、`llm-wiki.md` 参考边界与 GPT-5.6 模型路由。
- 在源 `Knowledge/` 建立 `RELEASED.md` 单向发布维护入口。

### Changed

- 将 Query、Ingest、评分、Wiki 链接与专家协议改写为领域中立规则；空索引、零 raw、零 Wiki 和零 prompt 均为合法状态。

### Tests

- 发布契约通过：51 个文件的相对链接、脱敏、零内容、模板字段、Query/Agent 行为与父目录依赖检查均通过。
- 临时副本通过 dry-run 不变性、普通及大小写改名、三种 IMA 初始化结果和非法/冲突/逃逸/保留目录名拒绝测试。
- 全部新增文本通过 UTF-8、LF、无 BOM 检查；源 `Knowledge/` 的内容目录 diff 为零。
