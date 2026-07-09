# 02 - 已完成清单

> 每次完成工作，在下方追加一条记录（不删除历史）。
> 格式：## YYYY-MM-DD - [任务名]

---

## 2026-07-07 - 项目立项 + 架构决策

**完成内容：**
- ✅ 决定项目方向：AI对话探索解谜游戏，30分钟单局
- ✅ 决定技术栈：Python + Flask + 原生HTML
- ✅ 决定部署：腾讯云Ubuntu + Nginx
- ✅ 决定模式：混合（90%规则 + 10%AI + 缓存）
- ✅ 决定AI角色4阶段演化：懵懂→好奇→觉醒→真相
- ✅ 决定上下文衔接方案：AGENT.md + iteration-log

---

## 2026-07-07 - GDD设计文档（8个文档初稿）

**完成内容：**
- ✅ 01-concept.md（核心概念）
- ✅ 02-gameplay.md（玩法机制）
- ✅ 03-story.md（故事剧本）
- ✅ 04-characters.md（角色设定）
- ✅ 05-flow.md（30分钟流程拆解）
- ✅ 06-ui.md（UI/UX设计）
- ✅ 07-tech.md（技术实现方案）
- ✅ 08-iteration-log.md（迭代日志）

---

## 2026-07-07 - 代码框架搭建

**完成内容：**
- ✅ engine/__init__.py
- ✅ engine/character_state.py（AI人格状态机）
- ✅ engine/file_reader.py（知识库读取）
- ✅ engine/rule_engine.py（规则匹配）
- ✅ engine/cache_manager.py（缓存管理）
- ✅ engine/ai_fallback.py（百炼API兜底）
- ✅ engine/hybrid_reply.py（混合回复核心）
- ✅ app.py（Flask后端，4个API端点）
- ✅ index.html（终端风格前端）
- ✅ requirements.txt（Python依赖）
- ✅ setup.sh（一键部署脚本）
- ✅ knowledge/triggers/keyword-rules.json（5个基础关键词模板）
- ✅ knowledge/triggers/passwords.json（alpha-7 + X-7-final）
- ✅ knowledge/files/*（占位文件）
- ✅ knowledge/plot/*（章节剧情占位）
- ✅ knowledge/characters/awakening-ai.md（角色卡）
- ✅ tests/game-flow-test.md（测试用例）

---

## 2026-07-07 - 框架验证通过

**完成内容：**
- ✅ 5个核心模块加载成功
- ✅ Flask服务启动（端口8088）
- ✅ /health 端点正常
- ✅ /api/chat 关键词模板触发（"你是谁" → rule_template）
- ✅ /api/chat 密码系统（alpha-7 → 章节3，状态puzzled）
- ✅ /api/chat 文件读取（/read welcome.txt）
- ✅ /api/chat AI兜底调百炼API（dormant状态返回懵懂风格）

---

## 2026-07-07 - 项目计划文件夹建立

**完成内容：**
- ✅ 创建 plan/ 子目录
- ✅ plan/README.md（快速跳转）
- ✅ plan/01-roadmap.md（整体路线图）
- ✅ plan/02-done.md（本文件）
- ✅ plan/03-todo.md（待办清单）

---

---

## 2026-07-08 - P0 核心剧情决策完成 + GDD 文档填充

**完成内容：**
- ✅ P0 全部9项核心决策确定（故事方向、主人身份、AI名字、玩家身份、角色设定、密码系统、叙事结构）
- ✅ GDD/01-concept.md — 核心Hook更新为外星人悬疑
- ✅ GDD/02-gameplay.md — 文件解锁机制适配5层系统
- ✅ GDD/03-story.md — 完整重写（29天日记设计+6章节+对话样本+4结局）
- ✅ GDD/04-characters.md — 完整重写（M-M 5阶段人格+4个北斗七星角色+玩家角色）
- ✅ GDD/05-flow.md — 完整重写（每分钟事件表+状态切换条件+情绪曲线）
- ✅ knowledge/characters/awakening-ai.md — 角色卡更新为M-M
- ✅ knowledge/triggers/passwords.json — 更新为3层密码系统结构

**当前状态：**
- 阶段3内容创作 — P0决策完成，GDD文档全部填充完毕
- 下一批工作：撰写知识库文件（29天日记、入职资料、录音转写、证据包）

---

## 2026-07-08 - RAG 架构改造：AI-NPC 知识库智能回答

**完成内容：**
- ✅ 新建 `engine/memory.py` — M-M 记忆系统（可访问文件/已读/事实/观察/发现/理解摘要）
- ✅ 新建 `engine/knowledge_search.py` — 知识库检索（分块+Jaccard相似度+Top-K）
- ✅ 重写 `engine/ai_fallback.py` — RAG Prompt 三层注入（角色卡+记忆+检索知识）
- ✅ 重写 `engine/hybrid_reply.py` — 整合 Memory 生命周期（文件读→记忆，密码→解锁，AI回复→迭代）
- ✅ 改造 `engine/file_reader.py` — 新增 `resolve_file_path` + `get_file_summary`
- ✅ 修复 Python 3.9 兼容性（cache_manager.py / rule_engine.py / ai_fallback.py）
- ✅ 更新 `AGENT.md` — 新架构文档
- ✅ 全部模块导入和基础调用验证通过

**新架构数据流：**
```
对话 → hybrid_reply → AI-RAG → 角色卡 + 记忆 + 知识检索 → AI模型 → 迭代记忆 → 反馈
```

---

## 关键文件清单

### 设计文档（GDD/）
- 01-concept.md - 核心概念
- 02-gameplay.md - 玩法机制
- 03-story.md - 故事剧本
- 04-characters.md - 角色设定
- 05-flow.md - 30分钟流程
- 06-ui.md - UI/UX
- 07-tech.md - 技术方案
- 08-iteration-log.md - 迭代日志

### 核心代码（engine/）
- hybrid_reply.py - 混合模式核心（约150行）
- ai_fallback.py - AI兜底（约100行）
- rule_engine.py - 规则匹配（约60行）
- cache_manager.py - 缓存管理（约60行）
- character_state.py - 状态机（约80行）
- file_reader.py - 文件读取（约50行）

### 入口文件
- app.py - Flask后端（约80行）
- index.html - 前端（约300行）

### 知识库（knowledge/）
- files/ - 8个虚拟文件（welcome/readme/emails×2/diary×2/research×1/final-revelation）
- plot/ - 3个剧情文件（chapter-1-boot/chapter-2-curious/chapter-3-6-placeholder）
- characters/awakening-ai.md - 角色卡
- triggers/keyword-rules.json - 5个关键词模板
- triggers/passwords.json - 2个示例密码

### 部署
- requirements.txt - flask + openai + gunicorn
- setup.sh - 一键安装脚本
