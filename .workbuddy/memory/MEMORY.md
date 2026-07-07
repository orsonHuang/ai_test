# Project MEMORY

## 项目信息
- Project ZH：海外移动手游，正式名称 **Zodiac Heroes**（十二星座英雄）
- 主策划：Orson
- 团队工具：钉钉（聊天）、TAPD（任务）、金山文档（文档）
- 品类：三消 RPG 养成，已上架 Google Play
- 世界观：十二星座主题星球，玩家从水瓶座出发探险
- 核心玩法：三消驱动英雄战斗 + 英雄养成（等级/星级/装备/技能/羁绊）

## AI 协作
- AI 称呼：小七
- 风格：贾维斯模式（高效+偶尔幽默）
- 框架：meta-agent-collab 组合 D
- 协作文件：AGENT.md, AI_INDEX.md, NOW.md, heartbeat-state.md, memory.md

## 新项目：AI-Learning
- Orson 的 LLM 应用开发学习项目
- 方向：游戏AI策划（独立游戏）—— 聚焦 AI-NPC 设计与游戏内 AI 玩法落地
- 实战锚点：独立游戏 **《遥远行星：建造师》**（太空科幻 + 模拟经营 + RPG）
- 目标能力：LLM认知 + Prompt设计 + 游戏体验设计 + 代码/工作流落地
- 学习方式：理论速通 + 动手实践（混合模式）
- 四个阶段：AI-NPC基础 → 游戏知识库(RAG) → AI工作流(Agent) → 完整AI-NPC模块
- 项目目录：AI-Learning/
- 状态：**四阶段全部完成**（2026-07-07），评审通过
- API：百炼 Coding Plan，base_url=https://coding.dashscope.aliyuncs.com/v1，模型=qwen3.7-plus
- 核心产出：alpha-npc.py(01) → world-rag.py(02) → event-generator.py(03) → alpha-full.py(04完整版)

## 新项目：Awakening Demo（AI对话解谜游戏）
- 项目类型：独立游戏Demo，30分钟单局流程，AI对话探索解谜
- 核心玩法：唤醒被遗弃的电脑AI，通过对话让它探索文件，最终发现主人消失真相
- AI角色4阶段演化：懵懂→好奇→觉醒→真相
- 架构：混合模式（90%规则模板 + 10%AI生成 + 缓存）
- 项目目录：`awakening-demo/`
- 状态：**代码框架完成 + 验证通过**（2026-07-07），待文本内容填充
- 关键文件：
  - `AGENT.md` — 项目说明（每次会话AI自动读取）
  - `GDD/01-concept.md` ~ `GDD/08-iteration-log.md` — 8个设计文档
  - `knowledge/files/` `knowledge/plot/` `knowledge/characters/` `knowledge/triggers/` — 知识库
  - `engine/` — 6个核心模块（hybrid_reply/rule_engine/cache_manager/ai_fallback/character_state/file_reader）
  - `app.py` + `index.html` + `setup.sh` — 可部署三件套
- 验证结果：5个API端点全部跑通（关键词模板/密码/文件读取/AI兜底）
- 启动方式：`PORT=8088 python app.py` → 浏览器打开 http://localhost:8088
- 上下文衔接：AGENT.md + 08-iteration-log.md 实现跨会话无缝衔接
- 部署目标：腾讯云Ubuntu + Flask + Nginx
- API：百炼（暂），可切换DeepSeek/智谱免费API
