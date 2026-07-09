# CHANGELOG

> 本文件供 WorkBuddy / CodeBuddy 跨会话同步。每次有实质性变更时追加一条。

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

## 技术栈

- 前端：HTML + JS（终端风格）
- 后端：Python 3.9 + Flask
- AI：DeepSeek API（deepseek-chat，兼容OpenAI SDK）
- 架构：RAG（角色卡+记忆+知识检索） + 规则模板 + 缓存

## 变更记录详细版

- `GDD/08-iteration-log.md` — 详细技术迭代日志
- `plan/02-done.md` — 已完成清单
- `plan/03-todo.md` — 待完成清单
