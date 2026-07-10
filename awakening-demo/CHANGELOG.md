# CHANGELOG

> 本文件供 WorkBuddy / CodeBuddy 跨会话同步。每次有实质性变更时追加一条。

---

## 2026-07-11 · generate_reply 引擎流程文档化

**GDD/07-tech.md：**
- 新增「generate_reply 核心处理流程」章节
- 12 条路径优先级完整流程图（/命令→密码→意图→Q&A→模板→文件类别→缓存→超纲→AI-RAG→兜底）
- 12 种自然语言意图说明（scan/get/read/files/hint/analyze/confirm/choose 等）
- AI-RAG 三层 Prompt 注入架构（角色卡+记忆+知识检索）
- 模块调用图 + 回复类型映射表

**改动文件：**
- `GDD/07-tech.md` — 新增引擎流程章节
- `GDD/08-iteration-log.md` — 追加记录
- `CHANGELOG.md` — 本条目

---

## 2026-07-10 · GDD 与项目结构同步优化

**背景：**
- 02-gameplay.md：29天日记→10天、diary/→work-diary/、5层文件解锁→4层密码系统
- 07-tech.md：百炼API→DeepSeek API、补全 engine 模块（clue_manager/fuzzy_matcher/qa_engine/memory/knowledge_search）、补全 knowledge 子目录（audio/emails/research/new-folder）、更新密码配置示例
- README.md：同步实际项目结构、更新当前阶段状态、29天→10天、4阶段→5阶段
- AGENT.md：阶段更新为「优化迭代（阶段4）」
- 10-player-path.md：密码系统对应关系完全重写对齐实际实现
- CHANGELOG.md：修正技术栈描述（Python 3.13、DeepSeek）

**改动文件：**
- `GDD/02-gameplay.md` — 文件解锁机制重写
- `GDD/07-tech.md` — API/架构/文件结构/密码配置全部同步
- `GDD/10-player-path.md` — 密码系统对应关系修正
- `README.md` — 项目结构与状态更新
- `AGENT.md` — 当前阶段更新
- `CHANGELOG.md` — 技术栈修正 + 本条目
- `GDD/08-iteration-log.md` — 追加本条记录

---

## 2026-07-10 · 建议执行、文件状态、生日密码调整

**背景：**
用户提出 6 项优化：AI 建议识别与执行、查看文件状态分类、张知予生日密码、获取命令空目标提示、密码分析引导、协助分析。

**后端（engine/hybrid_reply.py）：**
- 扩展确认词（好、可以、打开、执行、试试等），支持单条执行、多条追问、选择执行
- 新增 `extract_suggestions_from_reply` 从 AI 回复提取建议命令
- 新增 `_parse_choice` 解析玩家选择（编号/第一条/关键词）
- 新增 `password_hint` / `analyze` 意图，引导密码分析
- 单独输入“获取/解锁”时，提示当前未解锁目标
- `/files detailed` 返回三类文件状态：已解锁、已读、发现未解锁
- 新增 `_build_default_suggestions` 根据章节生成默认建议

**配置：**
- `knowledge/triggers/passwords.json`：第一个密码从入职日期 `20240306` 改为生日 `20030323`
- `knowledge/files/deck/入职资料.txt`：补充生日 2003年3月23日，并更新密码提示
- `knowledge/characters/awakening-ai.md`：补充生日信息

**前端（index.html）：**
- 建议系统改为列表结构，支持多选
- 查看文件按钮请求 `/files detailed` 并展开侧边栏
- 确认词同步扩展

**验证：**
- 编译通过
- 生日密码 `20030323` 解锁工作日记
- 确认词/多选/选择执行流程正常
- 密码分析与协助分析正确响应
- `/files detailed` 返回三类文件清单

---

## 2026-07-10 · 开机流程反转 + 登录页 + 密码引导弱化

**背景：**
用户测试反馈：开机和登录顺序反了，应该先开机再登录；登录页需要按钮；AI 建议直接给出密码太直给；进入下一章的流程应更自然。

**前端（index.html）：**
- 开机流程反转：打开页面先播放「正在开机」动画，约 3 秒后显示登录页
- 登录页新增「登录」按钮，输入框、按钮、「按 Enter 登录」提示全部居中
- 调整开机进度条逻辑，时长约 3 秒
- AI 建议不再直给密码：
  - 读完 todolist 后引导看入职资料
  - 读完入职资料后引导扫描工作日记或尝试 8 位数字

**后端（engine/hybrid_reply.py）：**
- 第1章扫描工作日记回复改为：「找到了。D 盘有一个「工作日记」文件夹，但被加密了。需要 8 位数字才能打开。」
- `/hint` 命令第1章提示改为引导玩家从入职资料中找 8 位数字
- 密码正确后的回复优先使用 `passwords.json` 中的 `hint`；若 `hint` 已包含文件列表和引导，不再重复追加

**配置（knowledge/triggers/passwords.json）：**
- 第一个密码 `20240306` 的 `hint` 改为「扫描成功。工作日记文件夹已解锁：…要我打开哪一个？」

**角色卡（engine/ai_fallback.py）：**
- 【重要流程】不再直接写出「密码是 20240306」，改为引导玩家从入职日期自行推理 8 位数字
- 增加约束：不要直接告诉玩家任何密码

**验证：**
- 编译通过，HTML 无 lint 错误
- 扫描工作日记 → 提示需要 8 位数字 → 输入 20240306 → 回复「扫描成功…」并解锁文件
- `/hint` 不再直给密码



**背景：**
用户测试发现开机流程过于直接、UI 缺乏引导、章节标题提前剧透、M-M 角色阶段知识边界不够清晰。

**前端（index.html）：**
- 新增"正在开机"动画：输入名字后显示进度条 0%→100% + 启动日志，完成后进入主页
- 登录提示改为"按 Enter 登录"
- 左侧文件系统侧边栏默认收起，初始 AI 建议改为"可以打开左边系统文件侧边栏看看"
- 章节进度未到达的节点显示为 ???（如 "2. ???"），已到达显示实际标题

**后端（engine/hybrid_reply.py）：**
- 新增 `off_topic_count` 连续无关问题计数
- 新增 `_is_password_attempt` 之外的主线拉回逻辑：连续无关问题会逐步给出更强引导
- Q&A 库中 `out_of_scope` 类别也纳入无关问题计数
- 正常游戏路径（命令/文件/扫描/密码/关键词模板）重置计数

**角色卡：**
- `knowledge/characters/awakening-ai.md` 重写：按 5 阶段详细列出每阶段"知道/不知道/可读取文件/关键转折/典型台词"
- `GDD/04-characters.md` 同步更新角色卡 prompt 和阶段知识边界速查表
- `GDD/06-ui.md` 同步更新开机动画、侧边栏、章节进度条说明

**验证：**
- 编译通过，无 lint 错误
- 连续无关问题 3 次后正确拉回主线
- 正常输入后计数重置
- 密码/扫描/文件读取流程正常

---

## 2026-07-09 · 消息类型严格校准：AI 对话 vs 系统提醒

**背景：**
M-M 台词（关键词模板、扫描回复等）被错误渲染为系统提示，破坏沉浸感。

**后端：**
- `engine/hybrid_reply.py` — 扫描/文件列表/密码正确等 M-M 口吻回复统一为 `type: ai`
- `engine/hybrid_reply.py` — 新增 `awaiting_password` 状态与密码尝试识别，错误密码返回 `type: system`
- `app.py` — API 响应增加 `password_prompt` 字段

**前端：**
- `index.html` — 消息类型映射：仅 `command`/`system` 走系统提示，其余默认 AI 对话
- `index.html` — 解锁进度通知改为 `system` 类型
- `index.html` — 初始 `gameState` 加入 `awaiting_password`

**验证：**
- "你是AI吗" → `ai`｜错误密码 → `system`｜正确密码 → `ai` + 系统解锁通知

---

## 2026-07-09 · 前端交互优化：AI建议 / 头像切换 / 密码弹窗 / 动画入场

**新增：**
- `index.html` — AI 建议提示栏（`#input-hint`），根据章节+已读文件动态推荐下一步
- `index.html` — 密码输入弹窗（`#password-modal`），M-M 提示密码时弹出专用输入框
- `index.html` — 输入面板上升动画（`#input-panel`），开场白结束后淡入升起

**修改：**
- `index.html` — M-M 头像切换逻辑：读取入职资料后 AI→M-M
- `index.html` — 默认文件系统修正：只显示 deck/todolist.txt + deck/入职资料.txt
- `engine/hybrid_reply.py` — scan 意图扩展"找"关键词，Ch1 未指定目标→AI口吻+密码弹窗
- `engine/hybrid_reply.py` — 关键词模板/扫描回复类型从 `command`/`rule_template` 统一为 `ai`
- `engine/hybrid_reply.py` — 新增 `mm_name_revealed` 标记管理，入职资料+curious触发

**迭代日志：**
- `GDD/08-iteration-log.md` — 追加本次6项优化记录

---

## 2026-07-09 · 密码系统 + 关键词模板 + AI角色卡 + 前端名字输入

**密码系统：**
- `knowledge/triggers/passwords.json` — 三层密码正式配置
  - 密码1: `ZY2024!starlight` → 私人文件夹
  - 密码2: `StarCore@2024` → VPN连接+录音
  - 密码3: `origin0306` → 未命名文档

**关键词模板：**
- `knowledge/triggers/keyword-rules.json` — 扩展至30条模板，按5阶段分组

**AI角色卡：**
- `engine/ai_fallback.py` CHARACTER_CARD — 完整M-M人物设定

**前端：**
- `index.html` — 新增名字输入界面，玩家名传递给API

---

## 2026-07-09 · 知识库文件撰写（Diary + 入职资料 + 私人文件夹 + 录音 + 未命名文档）

**新增：**
- `knowledge/files/work-diary/01.md` - D1 入职日记（张知予，星核互动，3/6周三）
- `knowledge/files/work-diary/02.md` - D2 细微异常（林璇不去食堂、咖啡没人碰）
- `knowledge/files/work-diary/03.md` - D3* 约林璇被拒、打字速度异常
- `knowledge/files/work-diary/04.md` - D4* 系统记录6类异常、面试伤口消失
- `knowledge/files/work-diary/05.md` - D5 周日留白
- `knowledge/files/work-diary/06.md` - D6* 北斗七星命名规律、游戏文档非人设定
- `knowledge/files/work-diary/07.md` - D7* 被监视、开始录音、设置后手
- `knowledge/files/work-diary/08.md` - D8* 录到关键对话（样本数据/人类适应期）
- `knowledge/files/work-diary/09.md` - D9* 被沈爻光点名、整合证据、M-M后门
- `knowledge/files/work-diary/10.md` - D10 留白 日记戛然而止
- `knowledge/files/入职资料.txt` - 星核互动入职包（含密码1：ZY2024!starlight）
- `knowledge/files/异常观察记录.txt` - 六类系统化异常报告
- `knowledge/files/账号密码.txt` - VPN密码（=入职密码）+ 私人文件夹路径
- `knowledge/files/录音-全员会议-0308.txt` - 沈爻光讲话（起源计划/人类创造力/不要暴露）
- `knowledge/files/录音-林璇陈玑-0313.txt` - 样本数据/采集周期/D3-D4观察进度
- `knowledge/files/录音-陆天枢-0313.txt` - 人类适应期/"她录音了"/到周末标准流程
- `knowledge/files/未命名文档.md` - 终极证据（五章系统化真相+张知予最后自述）

**修改：**
- D1日期修正：3/4周一→3/6周三
- D4伤口逻辑修正：面试时看到→入职第四天消失
- D6读音逻辑修正：姚光=摇光同音、何恒共享hēng
- D7结尾隐晦化：去掉直白的密码提示
- 未命名文档：玩家名改为自输入（去掉固定名"小武"）
- 日记总数：29天→10天（用户决策）

**GDD同步更新：**
- `GDD/03-story.md` 全面重写（公司名/主人名/10天节奏/对话样本/结局HE）
- `GDD/04-characters.md` 天数修正
- `GDD/05-flow.md` 章节流程适配10天

---

## 2026-07-08 · RAG 架构改造 + P0决策

**新增：**
- `engine/memory.py` - AI-NPC记忆系统（可访问文件/已读/事实/观察/发现）
- `engine/knowledge_search.py` - 知识库检索（分块+Jaccard相似度+Top-K）

**重写：**
- `engine/ai_fallback.py` - RAG三层注入Prompt（角色卡+记忆+知识检索）
- `engine/hybrid_reply.py` - 整合Memory生命周期

**改造：**
- `engine/file_reader.py` - 新增resolve_file_path + get_file_summary
- Python 3.9兼容性修复（cache_manager/rule_engine/ai_fallback）

**P0决策确认：**
- 故事方向：悬疑·游戏公司外星人真相
- 主人：张知予，女游戏策划（开发向）
- AI：M-M，入职时创建的工作助理
- 公司：星核互动
- 玩家：男性青梅竹马（名字自输入）
- 角色：陆天枢/林璇/陈玑/沈爻光（北斗七星）
- 密码3层递进（入职密码→VPN→起源计划+入职日期）
- 独立游戏《未命名文档》= 最终证据文件名

**GDD完整填充：**
- `GDD/01-concept.md` · `GDD/02-gameplay.md` · `GDD/03-story.md`
- `GDD/04-characters.md` · `GDD/05-flow.md`

---

## 2026-07-07 · 项目初始化 + 代码框架

- 建立项目结构（GDD/ engine/ knowledge/ plan/ tests/）
- 8个GDD设计文档初稿
- 6个核心引擎模块 + Flask后端 + 终端风格前端
- 框架验证全部通过（端口8088，5个分支跑通）
- plan子目录建立（roadmap/done/todo）
- API：百炼（后切到DeepSeek）

---

## 2026-07-09 · 叙事内容全面打磨：日记逻辑修正 / M-M情绪递进 / 硬证据散布 / 邮件系统

### 工作日记（D1-D10）逻辑修正
- `07.md` — 删除藏密码/路径段落（避免和D9重复），改为林璇停工位看手机细节维持恐惧感
- `08.md` — 陈玑分析段微调："这说明他和林璇不一样"→"他更像一个会假装关心的人"，摇摆感更自然
- `09.md` — 密码逻辑修正：私人文件夹用独立密码（非入职密码），保持游戏性；沈爻光场景加语境（"对另一个人说话"）
- `10.md` — 新增系统提示行`[此文件创建于 2024-03-15 00:00:00，内容为空。]`
- `05.md` — 周日留白补充内容：模仿同事坐姿20秒受不了、搜"人类坐姿"无果
- `06.md` — 北斗七星发现加自我怀疑段落（"不可能。不可能。我把浏览器关了。打开。又关了。"）
- `GDD/04-characters.md` — 疤痕位置统一为"左手手背靠近虎口"
- `GDD/03-story.md` — D5描述从"留白"更新为"周日在家模仿同事坐姿20秒受不了"

### 入职资料 + 线索文件优化
- `knowledge/files/入职资料.txt` — "尽量不要私下拉群"→"内部沟通统一使用企业钉钉，跨部门协作可创建项目群"
- `knowledge/files/异常观察记录.txt` — 日期从3/12修正为3/13（避免和3/13录音时间矛盾）；格式增加紧急感痕迹
- `knowledge/files/private/异常观察记录.txt` — 新增门禁体温证据、低温存储证据、交叉验证表格

### M-M 对话情绪递进（5阶段弧线）
- `knowledge/triggers/keyword-rules.json` — 全部 60+ 条回复按5阶段情感弧线重写：
  - 懵懂：空洞、短句、"记忆是空的"
  - 好奇：主动提问、"我喜欢这段"
  - 困惑：不安、"除非她觉得这些不是人"
  - 觉醒：确定、"语法不会说谎。他们不是同一类。"
  - 真相：守护、"我不确定自己配不配得上这个'我们'。但我会把这件事做完。"
- `engine/character_state.py` — 5阶段 prompt_suffix 同步更新
- `GDD/04-characters.md` — 典型台词更新为实际对话示例

### M-M 开场白重构
- `index.html` — bootSequence 重写：
  - M-M 知道自己是本地工作助理AI，但记忆数据为空
  - 识别玩家名字后不再问"你是谁"
  - 结尾改为"当前已知可查看文件有 todolist。或者，尝试一下其它功能？"

### 邮件系统（5封新文件）
- `knowledge/files/emails/1.md` — 行政部全员会议通知（3/8，填充真实感）
- `knowledge/files/emails/2.md` — 陈玑约午饭（3/7，回看恐怖：从不吃饭的人假装邀请）
- `knowledge/files/emails/3.md` — 林璇：看到速回（3/14 09:47）
- `knowledge/files/emails/4.md` — 林璇：boss找你（3/14 14:23，语气升级）
- `knowledge/files/emails/5.md` — 张知予：不用找了。你永远找不到我的。（3/14 15:01）

### 硬证据散布系统（新增4条不可解释证据）
- D4 新增：门禁体温日志（陈玑 33.2°C、何恒 33.2°C —— 低体温症区间但行为正常）
- D7 新增：后勤仓库瞥见采购单（低温存储单元 × 3，-180°C，审批人：陆天枢）
- 异常观察记录 新增：体温+低温存储+交叉验证表格（6个独立来源指向同一结论）
- 未命名文档 重写：门禁体温/低温存储/游戏文档对照/录音/命名规律/交叉验证 = 完整证据链

---

## 技术栈

- 前端：HTML + JS（终端风格）
- 后端：Python 3.13 + Flask
- AI：DeepSeek API（deepseek-chat）
- 架构：混合模式（关键词模板 + AI兜底 + 缓存）

## 变更记录详细版

- `GDD/08-iteration-log.md` — 详细技术迭代日志
- `plan/02-done.md` — 已完成清单
- `plan/03-todo.md` — 待完成清单
