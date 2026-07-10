# 项目：Awakening Demo

## 项目类型
独立游戏Demo — AI对话探索解谜，30分钟单局流程

## 用户原始需求
- 跟电脑AI对话探索文件的游戏
- AI初始懵懂，开机后可让AI查看电脑文件
- 包含密码解锁、不断交互聊天探索
- 最后发现电脑主人背后的秘密
- **AI-NPC 架构**：角色卡 + 记忆系统 + 知识库检索（RAG），让 M-M 基于知识库内容智能回答
- 混合模式：90%规则模板 + 10%AI生成（控制运营成本）
- 框架先行，文本后续迭代

## 工作约定
- **每次会话开始先读 CHANGELOG.md** — WorkBuddy / CodeBuddy 跨工具信息同步
- 详细技术变更见 GDD/08-iteration-log.md
- 用户的游戏设计想法改 GDD 优先，不要直接动代码

## 目录约定
- GDD/ = 设计文档（用户主导）
- knowledge/ = 知识库（用户主导的剧情内容）
- engine/ = 代码实现（AI主导）
- tests/ = 测试用例

## 当前阶段
优化迭代（阶段4）— RAG 架构完成，知识库已填充，4层密码系统就位

## AI-NPC 架构（RAG 增强版）
```
玩家对话 → hybrid_reply（调度）
              ├─ /command    → 命令处理（读取文件→更新记忆）
              ├─ 密码        → 文件解锁→更新记忆
              ├─ 关键词模板  → 规则返回（0成本）
              ├─ 缓存        → 复用历史
              └─ AI-RAG      → ai_fallback
                                ├─ 角色卡（CHARACTER_CARD）
                                ├─ 记忆层（memory.build_context_string）
                                ├─ 知识层（knowledge_search.search）
                                └─ AI模型（DeepSeek deepseek-chat）
              ↓
          迭代记忆 → 更新 Memory（facts/observations/discoveries）
              ↓
          反馈玩家
```

核心模块：
- `engine/memory.py` — M-M 记忆系统（可访问文件/已读/事实/观察/发现）
- `engine/knowledge_search.py` — 知识库检索（分块+Jaccard相似度+Top-K）
- `engine/ai_fallback.py` — RAG Prompt 三层注入（角色卡+记忆+知识）
- `engine/hybrid_reply.py` — 核心调度器（7条路径 + 记忆生命周期管理）

## 项目计划
- `plan/01-roadmap.md` — 整体路线图
- `plan/02-done.md` — 已完成清单
- `plan/03-todo.md` — 待完成清单（按优先级）

## 技术栈
- 前端：HTML + JS（终端风格UI）
- 后端：Python + Flask
- 部署：腾讯云Ubuntu轻量云 + 可选域名
- AI：DeepSeek API（deepseek-chat，兼容OpenAI SDK）
- 数据：JSON缓存 + Markdown知识库
