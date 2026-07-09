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

## 2026-07-09 · 前端交互优化：AI建议 / 头像切换 / 密码弹窗 / 动画入场

### 背景
用户体验测试发现多处前端交互问题：缺乏操作引导、头像固定为AI、默认文件树错误、密码输入不直观、系统提示破坏沉浸感、输入栏突兀出现。

### 改动清单

| 序号 | 改动 | 文件 |
|------|------|------|
| 1 | **AI 建议提示栏** — 输入框上方新增 `#input-hint`，根据章节+已读文件动态推荐下一步操作（如"先打开 todolist.txt"、"试试输入 20240306"） | `index.html` |
| 2 | **M-M 头像切换** — 阅读 `入职资料.txt` 或进入 `curious` 状态后，`mm_name_revealed` 置 true，AI 头像自动改为 M-M | `index.html`、`hybrid_reply.py` |
| 3 | **默认文件系统修正** — 初始 `accessible_files` 从 `files/todolist.txt` 改为 `files/deck/todolist.txt` + `files/deck/入职资料.txt`，侧边栏正确显示 deck 文件夹 | `index.html` |
| 4 | **"找文件"→密码弹窗** — Chapter 1 输入"找文件""找到D盘工作日记"等口语，M-M 以 AI 口吻回复 + 触发 `password_prompt`，前端弹出密码输入框 | `hybrid_reply.py`、`index.html` |
| 5 | **系统提示→AI对话** — 关键词模板命中（`type: "rule_template"`）和扫描操作回复统一改为 `type: "ai"`，不再渲染成系统提示 | `hybrid_reply.py` |
| 6 | **输入面板上升动画** — `#input-hint` + `#input-area` 包入 `#input-panel`，开场阶段 opacity:0 + 禁用交互，开场白结束后从底部淡入升起（0.5s ease） | `index.html` |

### 设计原则
- AI 对话口吻始终成：M-M 说人话，不是系统输出
- 新玩家无需猜测操作：动态建议引导每个阶段该做什么
- 视觉节奏：系统启动→AI开场白→输入面板优雅入场
- 密码输入体验：M-M 指出"有密码"→弹窗输入→填回输入框发送，流程连贯

### 当前状态
- ✅ 所有改动已在本地验证通过
- ✅ 密码弹窗 + AI建议 + 头像切换联动正确
- ✅ 输入面板启动动画正常（位置不动、仅淡入上升）

