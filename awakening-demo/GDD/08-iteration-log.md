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

