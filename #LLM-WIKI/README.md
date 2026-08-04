<!-- knowledge-identity:display-name -->
# 游戏策划知识库

面向海外手游策划的 Markdown 知识库。聚焦游戏设计方法论、玩家留存策略和核心玩法打磨。

## 快速开始

1. 复制整个目录。
2. 安装 PowerShell 7；进入复制后的目录，运行 `pwsh -NoProfile -File ./system/maintenance/setup-wizard.ps1`（Windows 与 macOS 通用）。
3. 跟随 7 个小白问题完成设置；向导会解释用途、提供例子和推荐值，并在写入前展示 dry-run。
4. 将来源放入 `Clippings/`，说“开始 Ingest”。
5. 直接提问，或说“查询知识库”“Lint 健康检查”“专家模式”。

向导中可随时输入 `?` 查看说明、`B` 返回、`S` 使用推荐值、`Q` 安全退出。Windows PowerShell 5.1 的备用命令、macOS 环境要求和高级参数方式见 [SETUP.md](system/maintenance/SETUP.md)。

未初始化也可运行；范围为空时，首次 Ingest 会先补最小范围信息。根目录 [NOW.md](NOW.md) 提供 30 秒状态快照，详细状态见 [KNOWLEDGE_STATUS.md](system/registry/KNOWLEDGE_STATUS.md)。

## 怎么和知识库对话

### 初始化

直接运行问答向导，或对 AI 说“初始化知识库”。AI 应逐题解释名称、用途、使用者、主题、专家层和 IMA，不假设你理解这些术语；最终确认前只做 dry-run。

### 直接提问与查询

- “这个方案有哪些风险？”
- “查询知识库，找与主题 A 相关的方法。”
- “深查知识库，对照相关页面评审下面的方案。”
- “不要查知识库，只按我给的材料分析。”

空库会明确报告无内容，不遍历目录制造伪相关。版本、价格、政策、市场和其他时效事实应联网核实；无法联网时会标注未核实。

### 内容入库

提供 URL、附件、Clippings 文件或 IMA 条目，并说“开始 Ingest”。流程包含四个独立审核闸门；确认当前闸门不等于授权后续写入。

### 专家模式

说“专家模式：某领域”。只有存在匹配的 domain 与 prompt 时才加载；没有配置时如实报告不可用。普通专业任务可以静默使用共享方法，不显示身份。

### 健康检查

说“Lint 健康检查”。默认只报告问题，不自动修改；修复需要单独确认。

### 写入边界

- Query 默认只读。
- raw 是来源证词，审核通过后不做无依据重写。
- Wiki 是综合产物，可随新来源修订。
- 具体行为规则以对应协议为准，根 README 不复制查询等级、评分矩阵或维护实现。

## 核心闭环

```text
外部来源 → 评分 → raw 消化稿 → 人工审核 → Wiki 综合 → 域导航 → Query / Agent
```

- `raw-sources/`：证词层。入库后原则上不改写正文。
- `wiki/`：综合层。随新来源增量更新并处理冲突。
- `domains/`：导航层。只定义范围和指向 Wiki。
- `agents/`：可选方法层。默认休眠，无 prompt 时不宣称专家可用。

## AI 运行入口

- 新会话进入本知识库、从其他项目切换过来或上下文重置时，读取一次本文、`NOW.md` 与 `AGENTS.md`。
- 收到具体任务后进入 `system/protocols/RUNTIME_ROUTING.md`；同一任务的后续消息不重复读取本文。
- `COMMAND_MANUAL.md` 只在需要确认触发词、指令冲突或回答“可以怎么说”时读取，不再逐消息完整扫描。
- 修改目录、入口、协作规则或执行规则文件健康检查时重新读取本文。

## 最终目录结构

```text
your-knowledge-base/
├─ README.md / AGENTS.md / COMMAND_MANUAL.md / NOW.md
├─ .gitignore
├─ Clippings/README.md
├─ raw-sources/README.md + raw-source.template.md
├─ wiki/README.md + wiki.template.md
├─ domains/README.md + domain.template.md
├─ agents/
│  ├─ README.md / BUILD_GUIDE.md
│  ├─ EXPERT_PROTOCOL.md / CONTEXT_CONTRACT.md
│  └─ prompts/README.md + 专家模板
└─ system/
   ├─ README.md
   ├─ protocols/      运行路由、Query、Ingest、评分、模型与链接规则
   ├─ registry/       范围、索引、详细状态与来源登记表
   ├─ integrations/   脱敏 IMA 指南与本地配置模板
   └─ maintenance/    初始化、检查清单与变更记录
```

范围和显示名以 `system/registry/KNOWLEDGE_SCOPE.md` 为 SSOT；当前目录名以实际目录为事实。该树就是初始化后的正式运行结构，不再维护另一份目录树参考。
