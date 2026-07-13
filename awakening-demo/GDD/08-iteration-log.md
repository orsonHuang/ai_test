# 08 - 迭代日志

> 每次会话开始时，AI会先读本文件了解最新进展。
> 每次有改动时，在下方追加新记录。

---

## 2026-07-07 - 项目初始化

### AI操作
- 建立 `awakening-demo/` 项目结构
- 编写 `AGENT.md`（项目说明 + 工作约定）
- 撰写 8 个 GDD 文档初稿：
  - 01-concept.md（核心概念）
  - 02-gameplay.md（玩法机制）
  - 03-story.md（故事剧本）
  - 04-characters.md（角色设定）
  - 05-flow.md（30分钟流程）
  - 06-ui.md（UI/UX）
  - 07-tech.md（技术方案）
  - 08-iteration-log.md（本文件）

### 当前状态
- 框架阶段
- 文本内容均为占位符 `[FILL:xxx]`
- 等待用户填充剧情和具体内容

### 下一步
- [ ] 用户填充 `03-story.md` 中的 `[FILL:xxx]`（核心秘密、章节内容、对话样本）
- [ ] 用户填充 `04-characters.md` 中的 `[FILL:xxx]`（AI名字、主人身份、玩家身份）
- [ ] 决定密码设置（2-3个关键密码）
- [ ] 撰写 `knowledge/files/` 下的虚拟文件（邮件、日记、研究笔记）
- [ ] 撰写 `knowledge/plot/` 下的章节剧情脚本
- [ ] 启动代码框架搭建（app.py + engine/ + index.html）

### 待用户决策
- [ ] 电脑主人消失的真相选哪个方向（A自我放逐/B被消失/C主人就是AI/D自定义）
- [ ] AI的具体名字和性格
- [ ] 电脑主人的身份和职业
- [ ] 玩家在游戏中的身份
- [ ] 多结局的具体设计

### 技术决策记录
- API：百炼（用户已有Key）
- 部署：腾讯云Ubuntu + Nginx
- 模式：混合（90%规则 + 10%AI + 缓存）

---

## 2026-07-07 - 代码框架完成

### AI操作
- 搭建 `engine/` 6个核心模块（hybrid_reply/rule_engine/cache_manager/ai_fallback/character_state/file_reader）
- 撰写 `app.py` Flask后端（4个API端点：/health /api/chat /api/status /api/reset）
- 撰写 `index.html` 终端风格前端（章节进度、AI状态徽章、打字机效果、键盘操作）
- 撰写 `requirements.txt` 和 `setup.sh` 一键部署脚本
- 撰写 `knowledge/triggers/keyword-rules.json`（5个基础关键词模板）
- 撰写 `knowledge/triggers/passwords.json`（alpha-7和X-7-final两个示例密码）
- 撰写 `knowledge/files/` 占位文件（welcome/readme/emails/diary/research/final-revelation）
- 撰写 `knowledge/plot/` 章节占位（chapter-1-boot、chapter-2-curious、chapter-3-6-placeholder）
- 撰写 `knowledge/characters/awakening-ai.md` 角色卡
- 撰写 `tests/game-flow-test.md` 测试用例

### 框架验证结果
- ✅ 5个核心模块全部加载成功
- ✅ Flask服务启动（端口8088）
- ✅ /health 端点正常
- ✅ 关键词模板触发（"你是谁" → rule_template）
- ✅ 密码系统（alpha-7 → 章节3，状态puzzled）
- ✅ 文件读取（/read welcome.txt → 显示内容）
- ✅ AI兜底调百炼API（dormant状态返回懵懂风格回复）

### 当前状态
- 代码框架完成，混合模式5个分支全部跑通
- 文本内容仍为占位符 `[FILL:xxx]`
- 等待用户填充剧情和具体内容

### 下一步
- [ ] 用户填充 `GDD/03-story.md` 中的 `[FILL:xxx]`
- [ ] 用户填充 `GDD/04-characters.md` 中的 `[FILL:xxx]`
- [ ] 决定密码设置（替换alpha-7和X-7-final为真实密码）
- [ ] 撰写 `knowledge/files/` 下的具体文件内容
- [ ] 撰写 `knowledge/plot/` 下的章节剧情脚本
- [ ] 本地体验：浏览器打开 http://localhost:8088 玩一下
- [ ] 调整 `engine/ai_fallback.py` 的角色卡prompt

### 已知小问题
- 端口8080被占用，需用PORT=8088启动（不影响功能）

---

## 2026-07-07 - plan文件夹建立

### AI操作
- 创建 `plan/` 子目录
- 编写 `plan/README.md`（快速跳转）
- 编写 `plan/01-roadmap.md`（整体路线图，6个阶段）
- 编写 `plan/02-done.md`（已完成清单，4批次）
- 编写 `plan/03-todo.md`（待完成清单，按P0-P5优先级）
- 更新 `AGENT.md` 当前阶段为"内容创作"

### 当前状态
- 框架+代码+GDD全部完成
- 进入内容创作阶段
- 等待用户做核心剧情决策

---

## 2026-07-08 - RAG 架构改造：AI-NPC 知识库智能回答

### 背景
用户明确需求：知识库应该作为 M-M 智能回答的依赖数据源，而非仅能手动 `/read` 查看。
原有架构中 AI 看不到知识库文件内容，存在重大断层。

### 新增模块

| 模块 | 文件 | 说明 |
|------|------|------|
| 记忆系统 | `engine/memory.py` | M-M 的知识范围管理：可访问文件/已读文件/已知事实/观察/发现/当前理解 |
| 知识检索 | `engine/knowledge_search.py` | 基于玩家问题 + M-M 可访问范围，在知识库中检索相关片段（分块+Jaccard相似度+Top-K） |

### 改造模块

| 模块 | 改造内容 |
|------|---------|
| `ai_fallback.py` | 完整重写。Prompt = 角色卡 + 记忆上下文 + 知识库检索结果（RAG 三层注入） |
| `hybrid_reply.py` | 完整重写。整合 Memory 生命周期管理：文件读取→记忆更新，密码→文件解锁，AI回复→记忆迭代 |
| `file_reader.py` | 新增 `resolve_file_path`（智能路径解析）和 `get_file_summary`（内容摘要） |
| `cache_manager.py` | 修复 Python 3.9 类型注解兼容性 |
| `rule_engine.py` | 修复 Python 3.9 类型注解兼容性 |

### 新架构数据流

```
玩家对话
  ↓
hybrid_reply.generate_reply()
  ├─ /command → 直接处理（读文件时更新 Memory）
  ├─ 密码 → 解锁 Memory.accessible_files
  ├─ 关键词模板 → 快速返回（不消耗 AI 额度）
  ├─ 文件建议 → 解锁目录文件到 Memory
  ├─ 缓存 → 命中返回
  └─ AI-RAG →
       ├─ Memory.build_context_string() → [记忆层]
       ├─ knowledge_search.search() → [知识层]
       ├─ ai_fallback.generate() → 角色卡 + 记忆 + 知识 → [AI生成]
       └─ _maybe_update_memory_from_reply() → [迭代记忆]
  ↓
反馈玩家
```

### 当前状态
- ✅ 新架构全部模块导入和运行验证通过
- ✅ Memory 系统正常工作（初始化/文件解锁/阅读/上下文生成）
- ✅ 知识检索系统就绪（等待知识库文件填充后实际检索）
- ✅ AI RAG 路径已调通（"你好" → ai_rag 类型返回）
- ✅ `/status` 显示记忆统计

### 下一步
- [ ] 撰写知识库文件（todolist.txt / 29天日记 / 入职资料 / 录音 / 证据包）
- [ ] 在知识库填充后测试 RAG 检索效果
- [ ] 扩展 keyword-rules.json（匹配新故事内容）
- [ ] 更新 engine/ai_fallback.py 中 CHARACTER_CARD 为 GDD 最终版

---

### AI操作
- 确认全部 P0 核心剧情决策（用户提供详细设定）
- 完整重写 `GDD/01-concept.md`（Hook更新为外星人悬疑）
- 完整重写 `GDD/02-gameplay.md`（5层文件解锁系统）
- 完整重写 `GDD/03-story.md`（29天日记设计+6章节+对话样本+4结局）
- 完整重写 `GDD/04-characters.md`（M-M 5阶段+4个北斗七星角色+玩家）
- 完整重写 `GDD/05-flow.md`（每分钟事件表+状态切换+情绪曲线）
- 更新 `knowledge/characters/awakening-ai.md`（角色卡更名 M-M）
- 更新 `knowledge/triggers/passwords.json`（3层密码系统结构）
- 更新 `plan/02-done.md` + `plan/03-todo.md`

### 当前状态
- GDD 设计文档全部填充完毕，无 `[FILL:xxx]` 占位符
- 故事方向：悬疑 — 游戏公司外星人真相
- 叙事载体：29天工作日记为核心
- 密码系统：3层递进（入职账号→VPN→起源计划）
- 角色：M-M(AI) + 女游戏策划(主人) + 4个北斗七星角色 + 青梅竹马(玩家)

### 下一步
- [ ] 撰写 29 天工作日记（01.md ~ 29.md，含 * 标记日和留白日）
- [ ] 撰写 todolist.txt（桌面入口文件）
- [ ] 撰写 入职资料.txt（含密码1）
- [ ] 撰写 异常观察记录.txt + 账号密码.txt（密码1解锁内容）
- [ ] 撰写 录音文件夹（会议录音+1v1录音的文本转写）
- [ ] 撰写 final-evidence.txt（终极证据包）
- [ ] 扩展 keyword-rules.json（按5阶段差异化关键词模板）
- [ ] 更新 engine/ai_fallback.py 角色卡 prompt

---

## 2026-07-09 - 终局设计重构：从"行政菜单"到"情感闭环"

### 背景
原设计终局（28:00）弹出4个结局选项菜单（公开/报警/继续/销毁），玩家缺乏参与感。
重构为：玩家通过自然对话决定M-M的最终归宿，而非选择行政菜单。

### GDD 改动
- **GDD/03-story.md** — 重写多结局章节，改为终局对话流程（隐藏留言 → M-M问"你想让我怎么做" → 4个走向）
- **GDD/05-flow.md** — 更新第6章25-30分钟时间线，状态切换表新增终局状态
- **GDD/09-ending.md** — 新增独立终局设计文档（4个走向完整台词、触发条件、最终画面、二周目彩蛋）

### 代码改动
- **knowledge/files/hidden-message.txt** — 新增主人藏在启动代码中的隐藏留言文件
- **knowledge/triggers/keyword-rules.json** — 新增5条终局阶段规则：
  - `ending_hidden_message` — 终局引导语（"你想让我怎么做？"）
  - `ending_publish` — 公开真相走向
  - `ending_hide` — 保护M-M走向
  - `ending_wait` — 继续等待走向
  - `ending_take` — 带我走隐藏结局
- **engine/rule_engine.py** — match_keyword_template 新增 `game_state` 参数，支持 `requires_document_read` 过滤（终局关键词只在读完文档后激活）
- **engine/hybrid_reply.py** — 密码匹配传递 game_state 给 rule_engine；密码3解锁时设置 `document_read=True`

### 设计原则
- 终局是情感决策，不是行政决策
- M-M有完整弧光："我是谁？" → "你想让我怎么做？"
- "未命名文档"双重含义完成：主人和M-M两个"未命名"在此刻闭合
- 终局走规则模板，0 AI成本

---

## 2026-07-09 · 消息类型严格校准：AI 对话 vs 系统提醒

### 背景
用户测试发现：M-M 的台词（如关键词模板回复）被渲染成系统提示（黄色居中文字），破坏角色沉浸感。需要严格区分：
- M-M 的回复 → AI 对话气泡
- 密码错误 / 解锁进度 → 系统提醒
- 其他系统命令输出 → 系统提示

### 后端改动

| 文件 | 改动 |
|------|------|
| `engine/hybrid_reply.py` | 扫描相关 M-M 口吻回复（目标不存在/权限不足/文件列表/用法提示）全部改为 `type: "ai"` |
| `engine/hybrid_reply.py` | 密码正确后的 M-M 台词改为 `type: "ai"`，解锁文件列表由前端单独渲染为系统提示 |
| `engine/hybrid_reply.py` | 新增 `awaiting_password` 状态：扫描提示密码时置 true，正确识别后清除 |
| `engine/hybrid_reply.py` | 新增 `_is_password_attempt` 密码尝试识别，错误密码返回 `type: "system"` |
| `app.py` | API 响应增加 `password_prompt` 字段，前端弹窗依赖 |

### 前端改动

| 文件 | 改动 |
|------|------|
| `index.html` | 消息类型映射简化：仅 `command`/`system` 走系统提示，其余默认 AI 对话 |
| `index.html` | 解锁进度通知 `新文件已解锁：...` 改为 `system` 类型 |
| `index.html` | 初始 `gameState` 加入 `awaiting_password: false` |

### 验证结果
- ✅ "你是AI吗" → `type: ai`（AI 气泡）
- ✅ "找文件" → `type: ai` + `password_prompt: true` + `awaiting_password: true`
- ✅ 错误密码 → `type: system`（系统提示）
- ✅ 正确密码 → `type: ai` + `unlock`（AI 气泡 + 系统解锁通知）
- ✅ "/files" → `type: ai`（AI 气泡）
- ✅ 非密码输入在密码等待状态下取消等待并继续正常流程

### 当前状态
- AI 对话与系统提示边界清晰，符合用户要求
- 密码弹窗可通过 `password_prompt` 正确触发
- 等待提交 Git

### 改动文件
- `engine/hybrid_reply.py`
- `engine/rule_engine.py`（未改动，审计后无问题）
- `app.py`
- `index.html`
- `CHANGELOG.md`
- `GDD/08-iteration-log.md`

---

## 2026-07-09 · P0关键线索文件修复 + 玩家路径分析

### 背景
用户要求梳理完整玩家游戏路径，发现两个核心线索文件被 git 命令输出污染，导致第3章和第5-6章无法正常游玩。

### 问题诊断
| 文件 | 问题 | 影响范围 |
|------|------|---------|
| `private/账号密码.txt` | 被 git show 错误输出污染 | 第3章卡死（无法解锁录音） |
| `new-folder/未命名文档.md` | 被 git show 错误输出污染 | 第5-6章卡死（无法触发终局） |
| `final-revelation.md` | 冗余占位文件，与新设计冲突 | 设计一致性 |

### 文件修复

**1. `private/账号密码.txt`** — 重写为完整的VPN连接信息：
- 服务器地址：vpn.star-core.com
- 用户名：zhangzhiyu
- 密码：StarCore@2024
- 附带内部文件路径说明（指向录音文件夹）
- 星核互动 IT 部统一格式，与入职资料风格一致

**2. `new-folder/未命名文档.md`** — 重写为完整的最终真相文档：
- 第一部分：他们不是人类（生理证据 + 命名规律 + 语言证据 + 游戏设定疑点）
- 第二部分：3段录音关键转写（林璇→陈玑 / 陆天枢 / 林璇陈玑）
- 第三部分："起源计划"推断（目标/方法/阶段/标准流程）
- 第四部分：M-M（后门设置 + 隐藏留言）
- 第五部分：张知予的自述（9天发现真相 + "别让他们觉得人类可以被起源"）
- 署名 + 日期：2024年3月15日，电脑被收回之前

### 新增文档

**`GDD/10-player-path.md`** — 完整玩家路径分析报告：
- 22个文件清单与状态标记（✅完整 / ⚠️占位 / ❌污染）
- 第1-6章逐章玩家体验流程图
- 文件与GDD流程的对应关系表
- 4个设计问题与建议：
  - 邮件文件夹（5封）在流程中完全没被引用
  - 研究笔记有插嘴规则但无引导
  - 密码系统有混淆（todolist说8位数字，实际密码1不是）
  - final-revelation.md 与 未命名文档.md 的关系需要明确
- P0/P1/P2 修复优先级表

### 设计决策记录
- 密码系统对齐：todolist中的"8位数字"伏笔关联密码3（origin0306），密码1使用入职资料中的系统密码
- final-revelation.md 标记为冗余待删（被 未命名文档.md 替代）
- 邮件和研究笔记作为可选支线保留，不强制主线引用

### 当前状态
- ✅ 22个核心文件全部就位，从开机到终局的完整路径可以跑通
- ⚠️ 邮件（5封）和 research（3篇）未被流程引导，可选
- ⚠️ final-revelation.md 冗余待清理
- ⚠️ readme.txt 和 welcome.txt 仍为占位

---

## 2026-07-10 · 建议执行、文件状态、生日密码调整

### 背景
用户提出 6 项优化：AI 建议识别与执行、查看文件状态分类、张知予生日密码、获取命令空目标提示、密码分析引导、协助分析。

### 后端改动（engine/hybrid_reply.py）

| 文件 | 改动 |
|------|------|
| `engine/hybrid_reply.py` | 扩展确认词，支持单条执行、多条追问、选择执行；新增建议提取与选择解析 |
| `engine/hybrid_reply.py` | 新增 `password_hint` / `analyze` 意图，引导密码分析与综合推理 |
| `engine/hybrid_reply.py` | 单独输入“获取/解锁”时提示当前未解锁目标 |
| `engine/hybrid_reply.py` | `/files detailed` 返回三类文件状态：已解锁、已读、发现未解锁 |
| `engine/hybrid_reply.py` | 新增 `_build_default_suggestions`，根据章节生成默认建议 |
| `knowledge/triggers/passwords.json` | 第一个密码从 `20240306` 改为生日 `20030323` |
| `knowledge/files/deck/入职资料.txt` | 补充生日 2003年3月23日，并更新密码提示 |
| `knowledge/characters/awakening-ai.md` | 补充生日信息 |
| `engine/ai_fallback.py` | 角色卡重要流程改为从生日推理 8 位数字 |

### 前端改动（index.html）

| 功能 | 改动 |
|------|------|
| 建议系统 | 改为列表结构，支持多选与执行命令映射 |
| 查看文件按钮 | 请求 `/files detailed` 并展开侧边栏 |
| 确认词 | 同步扩展为好、可以、打开、执行、试试等 |

### 验证结果
- ✅ 编译通过
- ✅ 生日密码 `20030323` 解锁工作日记
- ✅ 确认词/多选/选择执行流程正常
- ✅ 密码分析与协助分析正确响应
- ✅ `/files detailed` 返回三类文件清单

### 当前状态
- 等待用户测试反馈
- 等待提交 Git

### 改动文件
- `index.html`
- `engine/hybrid_reply.py`
- `engine/ai_fallback.py`
- `knowledge/triggers/passwords.json`
- `knowledge/files/deck/入职资料.txt`
- `knowledge/characters/awakening-ai.md`
- `CHANGELOG.md`
- `GDD/08-iteration-log.md`（本文件）

---

## 2026-07-11 · generate_reply 引擎流程文档化

### 背景
完整梳理 `hybrid_reply.py` 的 `generate_reply()` 12 条处理路径，写入 GDD 技术文档。

### 改动
- `GDD/07-tech.md` — 新增「generate_reply 核心处理流程」章节：
  - 12 条路径的优先级完整流程图（/命令→密码→意图→Q&A→模板→文件类别→缓存→超纲→AI-RAG→兜底）
  - 12 种自然语言意图说明（scan/get/read/files/hint/analyze/confirm/choose 等）
  - AI-RAG 三层 Prompt 注入架构（角色卡+记忆+知识检索）
  - 模块调用图
  - 回复类型 (12 种 type) 与前端渲染映射表
  - 关键设计决策表（成本控制/建议系统/记忆闭环/off_topic 拉回等）

### 当前状态
- GDD 技术方案文档已完整覆盖引擎处理流程
- 等待提交 Git

---

## 2026-07-10 · GDD与项目结构同步优化

### 背景
项目经过多次迭代后，多个GDD文档与实际代码存在不一致：29天→10天日记、百炼→DeepSeek、engine/knowledge文件结构变化、密码系统重构等。

### GDD 文档修正

| 文件 | 修正内容 |
|------|---------|
| `GDD/02-gameplay.md` | 文件解锁机制从"5层含29天日记"重写为实际的"4层密码+10天日记+work-diary目录" |
| `GDD/07-tech.md` | 百炼API→DeepSeek API；qwen3.7-plus→deepseek-chat；补全engine模块（clue_manager/fuzzy_matcher/qa_engine/memory/knowledge_search）；补全knowledge子目录（audio/emails/research/new-folder）；密码配置示例更新为实际的4密码系统；API配置从DASHSCOPE_API_KEY→DEEPSEEK_API_KEY |
| `GDD/10-player-path.md` | 密码系统对应关系完全重写：4个密码的值、解锁内容、来源清晰表列，修正已过时的混淆分析 |
| `README.md` | 项目结构同步实际；当前阶段从"框架阶段完成"更新；29天→10天；4阶段→5阶段；任务完成列表更新 |
| `AGENT.md` | 当前阶段从"内容创作（阶段3）"更新为"优化迭代（阶段4）" |
| `CHANGELOG.md` | 技术栈修正（Python 3.13 + DeepSeek）；追加本条记录 |

### 项目结构同步摘要

| 维度 | GDD 旧值 | 实际/新值 |
|------|---------|-----------|
| AI模型 | 百炼 qwen3.7-plus | DeepSeek deepseek-chat |
| 日记天数 | 29天 | 10天 |
| 文件目录 | diary/ | work-diary/ |
| 密码数 | 3层（旧设计5层文件） | 4层密码（4个独立密码） |
| engine模块 | 6个 | 12个（新增memory/knowledge_search/fuzzy_matcher/qa_engine/clue_manager/cache_manager） |
| 知识库文件数 | ~20个占位 | 39个完整文件（含10天日记/6封邮件/3篇研究/3个录音等） |

### 当前状态
- GDD 与代码完全同步
- 无残留的"百炼"或"29天"描述
- 密码系统在GDD中有清晰完整的文档

---

## 2026-07-10 · 开机流程反转 + 登录页 + 密码引导弱化

### 背景
用户测试反馈：开机和登录顺序反了，应该先开机再登录；登录页需要按钮；AI 建议直接给出密码太直给；进入第2章的流程应更自然。

### 前端改动（index.html）

| 需求 | 改动 |
|------|------|
| 开机→登录 | 打开页面先播放「正在开机」动画，约 3 秒后显示登录页 |
| 登录按钮 | 新增「登录」按钮，输入框、按钮、「按 Enter 登录」提示全部居中 |
| 开机时长 | 进度条间隔和增量调整，总时长约 3 秒 |
| AI 建议 | 第1章建议不再直给密码：读完入职资料后引导扫描或尝试 8 位数字 |

### 后端改动（engine/hybrid_reply.py）

| 文件 | 改动 |
|------|------|
| `engine/hybrid_reply.py` | 第1章扫描工作日记回复改为「找到了。D 盘有一个「工作日记」文件夹，但被加密了。需要 8 位数字才能打开。」 |
| `engine/hybrid_reply.py` | `/hint` 第1章提示改为引导玩家从入职资料中找 8 位数字 |
| `engine/hybrid_reply.py` | 密码正确后优先使用 `passwords.json` 的 `hint`，避免重复追加文件列表 |
| `knowledge/triggers/passwords.json` | 第一个密码 `20240306` 的 `hint` 改为「扫描成功。工作日记文件夹已解锁：…」 |
| `engine/ai_fallback.py` | 角色卡【重要流程】不再直接写出密码，改为引导玩家从入职日期自行推理；增加「不要直接告诉玩家密码」约束 |

### 验证结果
- ✅ 编译通过，HTML 无 lint 错误
- ✅ 扫描工作日记 → 提示需要 8 位数字 → 输入 20240306 → 回复「扫描成功…」并解锁文件
- ✅ `/hint` 不再直给密码
- ✅ 其他密码（ZY2024!starlight、StarCore@2024、origin0306）的解锁提示不受负向影响

### 当前状态
- 等待用户测试反馈
- 等待提交 Git

### 改动文件
- `index.html`
- `engine/hybrid_reply.py`
- `engine/ai_fallback.py`
- `knowledge/triggers/passwords.json`
- `CHANGELOG.md`
- `GDD/08-iteration-log.md`（本文件）

---

## 2026-07-09 · 开机体验 + UI 细节 + M-M 知识边界

### 背景
用户测试反馈：
1. 开机缺少仪式感，输入名字后直接进游戏
2. 左侧文件树默认展开，新手不知道可以点
3. 章节进度标题提前剧透后续章节
4. 玩家反复问无关问题时，M-M 没有逐步拉回主线
5. M-M 角色卡缺少阶段化知识边界，容易产生"提前知道真相"的幻觉

### 改动清单

| 需求 | 文件 | 改动内容 |
|------|------|----------|
| 开机动画 | `index.html` | 输入名字后先显示"正在开机" + 进度条 0%→100% + 启动日志，完成后进入主页 |
| 登录文案 | `index.html` | "按 Enter 开机" → "按 Enter 登录" |
| 侧边栏默认收起 | `index.html` | 初始化时 `sidebar.classList.add('collapsed')`，toggle 显示 `[+]` |
| 初始 AI 建议 | `index.html` | "先打开 todolist.txt" → "可以打开左边系统文件侧边栏看看" |
| 章节进度防剧透 | `index.html` | 未到达章节显示 `N. ???`，已到达显示实际标题 |
| 无关问题拉回 | `engine/hybrid_reply.py` | 新增 `off_topic_count` 计数，连续无关问题逐步追加主线引导 |
| Q&A out_of_scope | `engine/hybrid_reply.py` | 天气/新闻/时间等超纲问题也计入无关问题计数 |
| 角色卡细化 | `knowledge/characters/awakening-ai.md` | 按 5 阶段列出知道/不知道/可读取文件/关键转折/典型台词 |
| GDD同步 | `GDD/04-characters.md` | 角色卡 prompt + 阶段知识边界速查表 |
| GDD同步 | `GDD/06-ui.md` | 开机动画、侧边栏、章节进度条说明更新 |

### 设计原则
- 开机流程要制造"这台电脑刚刚启动"的沉浸感
- UI 引导要明确：新手不应猜测如何打开文件
- 章节标题剧透会破坏悬疑节奏，未到达内容用 ??? 隐藏
- M-M 的"聪明"必须受限于当前阶段知识库，不能提前知道真相
- 连续无关问题不应让玩家卡死，而要柔性引导回主线

### 验证结果
- ✅ Python 编译通过（hybrid_reply.py / app.py / ai_fallback.py / character_state.py）
- ✅ HTML 无 lint 错误
- ✅ 连续问天气 3 次：第1次普通回答，第2次"你好像有点走神"，第3次直接给主线提示
- ✅ 正常输入后 off_topic_count 重置
- ✅ 密码/扫描/文件读取流程未受影响

### 当前状态
- 所有改动已写入本地
- 等待提交 Git

### 改动文件
- `index.html`
- `engine/hybrid_reply.py`
- `knowledge/characters/awakening-ai.md`
- `GDD/04-characters.md`
- `GDD/06-ui.md`
- `CHANGELOG.md`
- `GDD/08-iteration-log.md`（本文件）

---

## 2026-07-12 · 重构框架 — 响应库重构：从关键词模板到预烘焙智能库

### 背景
- 玩家反馈 AI "太笨"：关键词模板触发固定回复，像 FAQ 机器人；意图识别太宽，"帮我看看""分析一下"被误判为文件读取
- 单机游戏需要控制 API 成本，不能依赖持续的外部 AI 调用

### 方案
- **预烘焙响应库**：开发时一次性生成 75 条目 / 157 变体，运行时零 API 成本匹配
- **学习闭环**：API 只在响应库/学习库都未覆盖时触发，结果自动入库复用
- **智能匹配**：按章节、已读文件、话题命中、示例相似度、Jaccard 综合打分
- **意图收窄**：只保留明确操作词（打开/扫描/获取/提示），模糊意图让响应库处理
- **清理**：删除 `keyword-rules.json`，QA 库降级为超纲+基础身份兜底

### 新增文件
- `engine/response_library.py` — 响应库智能匹配引擎（章节权重/话题匹配/相似度/Jaccard 四维打分）
- `engine/learning_store.py` — API 学习闭环（未命中 → API → 结果自动入库）
- `knowledge/response-library.json` — 75 条目 / 157 变体，覆盖剧情/角色/异常/情绪/结局
- `tests/test_response_library.py` — 响应库 CLI 测试脚本
- `tests/_smoke.py` — 冒烟测试

### 修改文件
- `engine/hybrid_reply.py` — 重构 `generate_reply` 优先级：响应库 → 学习库 → 降级 QA → 文件类别 → 缓存 → 超纲 → 严格 AI 兜底
- `engine/rule_engine.py` — 移除旧关键词模板，保留文件类别询问/阅读插嘴
- `knowledge/qa-library.json` — 简化为 out_of_scope + basic_identity 兜底
- `knowledge/triggers/keyword-rules.json` — **删除**（功能已合并至响应库）
- `knowledge/response-library.json` — 补充条目至 530 行
- `heartbeat-state.md` — 状态更新

### 设计原则
- **框架思维**：规则引擎不再是"关键词→固定回复"，而是"意图识别+智能匹配+学习闭环"的三层框架
- 运行时零 API 成本：90%+ 对话走响应库/缓存，API 仅兜底
- 可扩展：新增剧情只需在 `response-library.json` 中追加条目，框架自动适配
- 可迁移：响应库文件是纯 JSON，结构清晰，未来可直接迁移至任何对话引擎

### 验证结果
- ✅ 响应库加载正常（75 条目）
- ✅ 基础对话命中率 > 85%（"你是谁""你好""帮助"等）
- ✅ 学习闭环：API 回复 → learning_store.append → 下次直接命中
- ✅ 旧关键词模板完全移除，无破坏性影响
- ✅ Python/HTML 编译无错误

### 当前状态
- 重构框架完成
- 运行时零 API 成本对话已落地
- 等待玩家实际体验反馈

### 改动文件
- `engine/hybrid_reply.py` — generate_reply 流程重排
- `engine/response_library.py` — 新增
- `engine/learning_store.py` — 新增
- `engine/rule_engine.py` — 移除关键词模板
- `knowledge/response-library.json` — 75条目/157变体
- `knowledge/qa-library.json` — 简化为兜底
- `knowledge/triggers/keyword-rules.json` — 删除
- `tests/test_response_library.py` — 新增
- `tests/_smoke.py` — 新增
- `heartbeat-state.md`
- `GDD/07-tech.md`
- `GDD/08-iteration-log.md`（本文件）
- `CHANGELOG.md`

---

## 2026-07-13 · 重构框架 — 目标发现与主线引导优化

### 背景
- 玩家不清楚哪些文件夹存在、何时能扫描
- 下一步建议按钮常驻顶部，占据空间且不够直观
- 建议中的密码明文显示，降低悬疑感
- 密码解锁格式不统一，玩家容易混淆

### 改动 1：文件夹线索发现机制
- 新增 `knowledge/folder-discoveries.json`：定义哪些文件包含哪些文件夹线索
  - 读 `todolist.txt` → 发现「工作日记」
  - 读 `工作日记/01.md` → 发现「私人文件夹」
  - 读 `账号密码.txt` → 发现「公司服务器/录音」
  - 读 `工作日记/03.md` → 发现「研究笔记」
  - 读 `录音-陆天枢-0313.txt` → 发现「未命名文档」
- 新增 `engine/folder_discovery.py`：加载配置、发现目标、查询是否已发现
- 读文件后自动触发发现，M-M 会提示「我注意到 D 盘有一个……」
- 扫描/获取时检查目标是否已发现，未发现则提示「先读文件找线索」

### 改动 2：AI 建议主线化
- `_build_default_suggestions` 根据章节 + 已读文件 + 已发现目标生成建议
- 建议风格从「可选操作」改为「主线任务」：
  - 未读 todolist →「打开 todolist.txt」
  - 已读入职资料 →「获取 工作日记 密码」
  - 已解锁私人 →「获取 私人文件夹 密码」

### 改动 3：UI 建议栏重构
- 删除顶部工具栏，把按钮合并到 AI 建议栏右侧
- 右侧按钮：🔍 线索 / 📁 文件 / ▶ 执行建议
- 不影响 AI 建议文本的左侧对齐

### 改动 4：执行建议 + 密码脱敏
- 点击「执行建议」直接以第一条建议作为输入发送
- 建议文本中密码自动替换为「密码」：
  - 展示：「获取 工作日记 密码」
  - 命令：保留原始（或同样为「密码」格式）
- 前端正则 `maskPasswordText` 统一处理

### 改动 5：密码解锁格式统一
- 新格式：`获取 文件夹名 密码`（弹出密码输入框）
- 新格式：`获取 文件夹名 具体密码`（直接验证并解锁）
- 示例：
  - 获取 工作日记 密码
  - 获取 工作日记 20030323
  - 获取 私人文件夹 ZY2024!starlight
- 旧习惯（直接输入裸密码）仍兼容
- `handle_get_command` 现在会验证目标是否已发现、密码是否匹配该目标

### 改动 6：QA 帮助
- 新增 `folder_help` 意图 + `qa-library.json` 兜底
- 当玩家问「怎么获取文件夹」「怎么打开文件夹」等，统一提示正确格式

### 验证结果
- ✅ 读取 todolist 后提示发现工作日记
- ✅ 未发现的文件夹扫描被婉拒
- ✅ 建议栏按钮右置不影响文本对齐
- ✅ 执行建议直接发送命令
- ✅ 密码建议展示已脱敏
- ✅ 获取 文件夹名 密码 格式弹出密码 UI
- ✅ 获取 文件夹名 具体密码 格式直接解锁
- ✅ 文件夹帮助意图返回正确格式提示

### 当前状态
- 目标发现与主线引导框架完成
- 等待新一轮玩家测试反馈

---

## 2026-07-13 · 体验调优：弹窗去除、文件状态、建议对齐与主线推进

### 背景
玩家新一轮测试反馈 6 项体验问题：
1. 点击侧边栏文件会额外弹出文件弹窗，打断聊天流
2. 「文件」按钮只展开侧边栏，没有主动告诉玩家当前文件状态
3. AI 建议栏文本与按钮分散两端，视觉上不紧凑
4. 工作日记全部读完后 AI 仍推荐继续读，不会推进到下一主线目标
5. 问「你是谁」时偶发回答成张知予（响应库变体错误）
6. 玩家输入空「获取」时，不知道当前有哪些已发现但未解锁的文件夹

### 改动

**前端（`index.html`）**
- 移除文件查看弹窗：删除 `#file-modal` DOM、CSS、JS 函数与引用
- 点击文件树只发送「打开 文件名」命令，文件内容在聊天区以卡片呈现
- 「文件」按钮改为发送「查看文件状态」，后端返回状态并自动展开侧边栏
- AI 建议栏 `justify-content` 从 `space-between` 改为 `flex-start`，按钮与文本间距统一为 `gap: 12px`
- 前端 `updateAISuggestion` 与后端同步：
  - 按顺序指向下一篇未读工作日记
  - 全部读完后推进到「获取 私人文件夹 密码」
  - 第 3/4 章也按已发现目标推进主线

**后端（`engine/hybrid_reply.py`）**
- `files` 自然语言意图改为调用 `_build_file_status_reply`，返回三类文件清单并标记 `expand_sidebar: true`
- 新增 `_build_get_folder_hint`：列出已发现但未解锁的文件夹，无发现则引导阅读文档
- `handle_get_command` 空目标或未识别目标时统一调用 `_build_get_folder_hint`
- `_build_default_suggestions` 第 2 章逻辑重写：按顺序推荐下一篇未读工作日记，全部读完后推进到私人文件夹密码

**配置（`knowledge/response-library.json`）**
- 修复 `who_am_i_curious` 的第二个变体，从「她叫张知予……」改为 M-M 自我介绍

### 验证结果
- ✅ Python 编译通过
- ✅ 响应库 JSON 格式有效
- ✅ 冒烟测试通过
- ✅ chapter 2 问「你是谁」返回 M-M 自我介绍
- ✅ 全部工作日记读完后建议变为「获取 私人文件夹 密码」
- ✅ 空「获取」时列出已发现未解锁文件夹
- ✅ 无发现文件夹时提示阅读文档
- ✅ 「查看文件状态」返回三类文件清单并携带 `expand_sidebar`

### 当前状态
- 6 项体验问题已修复，等待下一轮测试反馈

### 改动文件
- `index.html`
- `engine/hybrid_reply.py`
- `knowledge/response-library.json`
- `CHANGELOG.md`
- `GDD/08-iteration-log.md`（本文件）

---

## 2026-07-13 · 多模块优化：M-M自我发现、QA条件回答、异步模型加载、离题回引

### 背景
多轮测试反馈的累积优化。

### 改动 1：M-M 自我发现流程修复
- `engine/hybrid_reply.py` — 读 todolist 时按正确顺序设置 `mm_name_revealed` 触发条件变体
- `engine/rule_engine.py` — `find_file_commentary` 支持条件变体 + `game_state`

### 改动 2：QA 条件回答
- `engine/qa_engine.py` — 新增 `conditional_answers`：按 `requires_files_read` 选择回答
- `knowledge/qa-library.json` — 身份/天气/新闻等条目添加条件变体

### 改动 3：离题回引优化
- `engine/hybrid_reply.py` — 推进主线类别重置 off_topic，闲聊累加超 3 次引导回主线

### 改动 4：Embedding 异步加载 + 前端进度条 ★
- `engine/sentence_matcher.py` — 新增：`load_model_async()`、`get_load_status()`
- `app.py` — 后台异步加载 + `/api/model-status`
- `index.html` — 开机画面轮询真实模型加载进度

### 改动 5：文件读取成长反馈暂时注释
- `_generate_file_growth_reflection` 调用暂时注释

### 改动文件
- `engine/sentence_matcher.py` — 新增
- `engine/hybrid_reply.py` + `engine/rule_engine.py` + `engine/qa_engine.py`
- `knowledge/qa-library.json` + `knowledge/response-library.json`
- `app.py` + `index.html` + `requirements.txt`
- `GDD/07-tech.md` + `GDD/05-flow.md` + `GDD/10-player-path.md` + `GDD/08-iteration-log.md`





