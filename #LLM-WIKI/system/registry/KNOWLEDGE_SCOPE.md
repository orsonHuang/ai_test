---
schema_version: 1
configured: true
name: '游戏策划知识库'
directory_name: 'Ai_Learning'
purpose: '学习和沉淀游戏策划方法论，支撑海外手游 Project ZH 的设计决策与能力成长'
audience: ['Orson（主策划）', '项目策划团队']
topics: ['游戏核心玩法设计', '留存与 D3-D7 优化', '中后期内容规划', '经济系统与数值平衡', '叙事设计', '关卡设计', '用户体验与交互', '竞品分析与拆解', '游戏心理学', '策划工作流与工具链']
excluded_topics: ['娱乐八卦', '非游戏行业的一般商业分析', '纯技术开发实现细节（非策划视角）']
source_quality: '优先一手、可追溯、论证完整的来源；GDC 演讲、知名游戏设计书籍、一线团队经验分享优先'
default_language: 'zh-CN'
expert_layer_enabled: false
ima_enabled: false
time_sensitive_facts: '需要外部核实并标注核实日期'
---

# KNOWLEDGE_SCOPE · 知识库范围

本文件是显示名、用途和知识范围的 SSOT。`configured: false` 是合法空库状态；首次 Ingest 必须先补齐 `purpose`、至少一个 `topic` 和排除边界，再进行相关性评分。

## 范围解释

- `topics` 决定什么内容具有直接相关性。
- `excluded_topics` 是明确不进入知识库的边界。
- `source_quality` 定义来源门槛，不替代 `../protocols/SCORING_SYSTEM.md` 的逐项评分。
- `expert_layer_enabled` 只控制是否允许发现专家 prompt，不代表已经存在专家。
- `ima_enabled` 仅是范围镜像；运行状态以本地 IMA 配置为准。
