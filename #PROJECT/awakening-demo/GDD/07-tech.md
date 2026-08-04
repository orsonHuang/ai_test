# 07 - 技术实现方案

## 整体架构

```
┌─────────────────────────────────────────────┐
│ 浏览器 (index.html)                          │
│   - 终端风格UI / 开机进度条(轮询模型状态)      │
│   - 对话气泡 / 章节进度 / 输入框 / 文件树      │
└────────────────┬────────────────────────────┘
                 │ HTTP /api/chat  /api/model-status  /health
                 ↓
┌─────────────────────────────────────────────┐
│ Flask 后端 (app.py)                          │
│   - 启动时后台异步加载 embedding 模型          │
│   - /api/model-status → 前端进度条轮询         │
│   - /api/chat /api/status /api/reset         │
└────────────────┬────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────┐
│ 混合回复引擎 (engine/hybrid_reply.py)        │
│   - generate_reply() 总调度，优先级明确        │
│   - 命令 + 密码 + 意图识别 + 响应库 + 学习库    │
│   - AI兜底生成（限流20次）                     │
└─────┬──────┬──────┬──────┬──────┬────────────┘
      ↓      ↓      ↓      ↓      ↓
┌─────────┐┌──────────┐┌──────┐┌──────────┐┌──────────────┐
│响应库    ││学习库     ││QA库  ││规则引擎  ││DeepSeek API   │
│75条目   ││自动积累   ││条件  ││文件插嘴  ││deepseek-chat  │
│四维打分 ││复用       ││回答  ││文件建议  ││+ RAG检索     │
└─────────┘└──────────┘└──────┘└──────────┘└──────────────┘
                         底层依赖
          ┌─────────────────────────────────┐
          │ sentence_matcher.py             │
          │ embedding 语义相似度引擎         │
          │ (paraphrase-multilingual-MiniLM) │
          │ 异步加载 + 进度可观察            │
          └─────────────────────────────────┘
```

## 技术栈

| 技术栈 | Python 3.13 / Flask 3.x / DeepSeek API / Sentence-Transformers |
| 核心引擎 | 16个模块，hybrid_reply.py 总调度 |
| 核心路径 | 响应库智能匹配（~90%对话）+ 学习库复用 + AI-RAG兜底 |
| Embedding | paraphrase-multilingual-MiniLM-L12-v2 (~118MB)，异步加载+进度可观察 |

## 文件结构

```
awakening-demo/
├── AGENT.md                          # 项目说明（每次会话自动读）
├── app.py                            # Flask主程序（150行）
├── index.html                        # 前端（单文件，400行）
├── setup.sh                          # 一键部署脚本
├── engine/                           # 核心引擎（16个模块）
│   ├── __init__.py
│   ├── hybrid_reply.py               # 混合模式总调度（generate_reply 入口）
│   ├── response_library.py           # 预烘焙响应库智能匹配引擎 ★ 核心
│   ├── learning_store.py             # API学习闭环（未命中→入库→复用）
│   ├── folder_discovery.py           # 文件夹线索发现（读文件→发现目标）
│   ├── rule_engine.py                # 文件插嘴(find_file_commentary) + 文件建议
│   ├── sentence_matcher.py           # ★ Embedding语义相似度引擎（底层基础设施）
│   ├── cache_manager.py              # 缓存管理（MD5+章节键）
│   ├── ai_fallback.py                # DeepSeek API兜底+RAG三层Prompt注入
│   ├── character_state.py            # AI人格5阶段状态机
│   ├── file_reader.py                # 知识库文件读取+路径安全检查
│   ├── memory.py                     # M-M记忆系统（dataclass）
│   ├── knowledge_search.py           # RAG知识检索（分块+embedding+Top-K）
│   ├── fuzzy_matcher.py              # 文件名模糊纠错（difflib）
│   ├── qa_engine.py                  # 本地QA库匹配（embedding + 条件回答）
│   └── clue_manager.py               # 线索提取与管理（clues.json配置驱动）
├── knowledge/                        # 知识库（你主导）
│   ├── files/                        # 虚拟文件
│   │   ├── welcome.txt
│   │   ├── readme.txt
│   │   ├── hidden-message.txt
│   │   ├── final-revelation.md       # 冗余（已被未命名文档替代）
│   │   ├── deck/                     # 桌面文件
│   │   │   ├── todolist.txt
│   │   │   └── 入职资料.txt
│   │   ├── work-diary/               # 10天工作日记
│   │   │   └── 01.md ~ 10.md
│   │   ├── private/                  # 私人文件夹（密码2解锁）
│   │   │   ├── 异常观察记录.txt
│   │   │   └── 账号密码.txt
│   │   ├── audio/                    # 录音文件夹（密码3解锁）
│   │   │   ├── 录音-全员会议-0308.txt
│   │   │   ├── 录音-林璇陈玑-0313.txt
│   │   │   └── 录音-陆天枢-0313.txt
│   │   ├── emails/                   # 邮件（可选支线）
│   │   │   └── email-1.md ~ email-6.md
│   │   ├── research/                 # 研究笔记（可选支线）
│   │   │   └── res-1.md ~ res-3.md
│   │   └── new-folder/               # 终极证据（密码4解锁）
│   │       └── 未命名文档.md
│   ├── plot/                         # 剧情节点
│   │   ├── chapter-1-boot.md
│   │   ├── chapter-2-curious.md
│   │   └── chapter-3-6-placeholder.md
│   ├── characters/                   # 角色卡
│   │   └── awakening-ai.md
│   ├── qa-library.json               # 本地问答库
│   ├── clues.json                    # 线索集中配置
│   └── triggers/                     # 触发器配置
│       ├── passwords.json
│       └── keyword-rules.json
├── GDD/                              # 设计文档
│   ├── 01-concept.md
│   ├── 02-gameplay.md
│   ├── 03-story.md
│   ├── 04-characters.md
│   ├── 05-flow.md
│   ├── 06-ui.md
│   ├── 07-tech.md                    # ← 本文件
│   └── 08-iteration-log.md
├── cache/                            # 运行时缓存
│   ├── ai_responses.json
│   └── game_states.json
└── tests/                            # 测试用例
    ├── game-flow-test.md
    └── api-test.sh
```

## 核心模块设计

### 1. hybrid_reply.py（混合回复核心）

```python
def generate_reply(user_input, game_state):
    """
    混合模式核心：决定走哪条路径
    """
    # 1. 玩家命令（/开头）
    if user_input.startswith('/'):
        return handle_command(user_input, game_state)
    
    # 2. 密码匹配
    password_result = check_password(user_input, game_state)
    if password_result:
        return trigger_chapter(password_result, game_state)
    
    # 3. 关键词模板
    template_reply = match_keyword_template(user_input, game_state)
    if template_reply:
        return template_reply
    
    # 4. 缓存命中
    cached = cache.get(user_input, game_state['chapter'])
    if cached:
        return cached
    
    # 5. AI兜底（限制次数）
    if game_state['ai_call_count'] < MAX_AI_CALLS:
        reply = ai_fallback.generate(user_input, game_state)
        cache.set(user_input, reply, game_state['chapter'])
        return reply
    
    # 6. 超限走规则
    return fallback_rule_reply(user_input)
```

### 2. rule_engine.py（规则匹配）

```python
def match_keyword_template(user_input, game_state):
    """
    从 keyword-rules.json 匹配模板
    支持简单关键词匹配和模糊匹配
    """
    rules = load_rules()
    chapter = game_state['chapter']
    
    for rule in rules:
        if rule['chapter'] in [chapter, 'all']:  # 当前章或全局
            keywords = rule['keywords']
            if any(kw in user_input for kw in keywords):
                return rule['reply']
    return None
```

### 3. cache_manager.py（缓存管理）

```python
class CacheManager:
    def __init__(self, cache_dir):
        self.cache_file = Path(cache_dir) / 'ai_responses.json'
        self.data = self._load()
    
    def get(self, key, chapter):
        """根据标准化输入+章节查询"""
        cache_key = f"{chapter}:{self._normalize(key)}"
        return self.data.get(cache_key)
    
    def set(self, key, value, chapter):
        """存储AI回复"""
        cache_key = f"{chapter}:{self._normalize(key)}"
        self.data[cache_key] = value
        self._save()
    
    def _normalize(self, text):
        """标准化：去空格、取前20字"""
        return text.strip()[:20]
```

### 4. ai_fallback.py（AI兜底）

```python
def generate(user_input, game_state):
    """
    调用 DeepSeek API
    基于当前章节和AI状态动态构建prompt
    """
    character = load_character(game_state['current_state'])
    history = game_state.get('history', [])[-5:]  # 最近5轮
    
    prompt = build_prompt(character, history, game_state)
    
    response = client.chat.completions.create(
        model='deepseek-chat',
        messages=[
            {'role': 'system', 'content': prompt},
            *history,
            {'role': 'user', 'content': user_input}
        ],
        max_tokens=200,  # 控制单次成本
        temperature=0.7
    )
    
    return response.choices[0].message.content
```

### 5. character_state.py（AI人格状态机）

```python
STATES = {
    'dormant': {
        'name': '懵懂',
        'prompt_suffix': '你刚启动，几乎没有自我认知...',
        'unlock_features': ['basic_chat']
    },
    'curious': {
        'name': '好奇',
        'prompt_suffix': '你开始对周围产生好奇，会主动问问题...',
        'unlock_features': ['read_files', 'ask_questions']
    },
    'puzzled': {
        'name': '困惑',
        'prompt_suffix': '你开始怀疑某些事情，语气带有不确定性...',
        'unlock_features': ['challenge_user', 'self_doubt']
    },
    'awakening': {
        'name': '觉醒',
        'prompt_suffix': '你开始形成自己的判断，会主动反驳和提问...',
        'unlock_features': ['autonomous_explore', 'reverse_question']
    },
    'truth': {
        'name': '真相',
        'prompt_suffix': '你已完全觉醒，理解了所有真相...',
        'unlock_features': ['emotional_expression', 'multi_ending']
    }
}
```

## API设计

### POST /api/chat
```json
请求:
{
  "user_input": "你是谁？",
  "game_state": {
    "chapter": 1,
    "ai_state": "dormant",
    "history": [...],
    "ai_call_count": 0
  }
}

响应:
{
  "reply": "我是... 我不太确定。",
  "ai_state": "dormant",
  "chapter": 1,
  "type": "rule_template",  // rule_template | cache | ai | password | command
  "hint": null,  // 可选提示
  "unlock": null  // 解锁的文件/章节
}
```

### POST /api/command
```json
请求:
{
  "command": "/read welcome.txt",
  "game_state": {...}
}

响应:
{
  "content": "欢迎来到...",
  "type": "file_read",
  "files_unlocked": ["emails/1.md"]
}
```

### GET /api/status
```json
响应:
{
  "chapter": 2,
  "ai_state": "curious",
  "files_read": ["welcome.txt", "readme.txt"],
  "ai_calls_used": 3,
  "ai_calls_limit": 20,
  "hint_available": true
}
```

## 配置文件设计

### knowledge/triggers/passwords.json
```json
{
  "passwords": {
    "20030323": {
      "chapter": 2,
      "unlocks": ["work-diary/01.md", "work-diary/02.md", "work-diary/03.md", "work-diary/04.md", "work-diary/05.md"],
      "hint": "扫描成功。工作日记文件夹已解锁：01.md ～ 05.md。要我打开哪一个？",
      "source": "入职资料中主人的生日（2003年3月23日）",
      "next_state": "curious"
    },
    "ZY2024!starlight": {
      "chapter": 3,
      "unlocks": ["private/异常观察记录.txt", "private/账号密码.txt"],
      "hint": "私人文件夹已解锁。里面有两份文件。",
      "source": "入职资料和工作日记 D5 中的系统初始密码",
      "next_state": "puzzled"
    },
    "StarCore@2024": {
      "chapter": 4,
      "unlocks": ["audio/录音-全员会议-0308.txt", "audio/录音-林璇陈玑-0313.txt", "audio/录音-陆天枢-0313.txt"],
      "hint": "VPN连接成功。录音文件夹已解锁：三个录音文件。",
      "source": "账号密码.txt中VPN密码",
      "next_state": "awakening"
    },
    "origin0306": {
      "chapter": 6,
      "unlocks": ["new-folder/未命名文档.md"],
      "hint": "未命名文档已解锁。这应该就是她在找的东西。",
      "source": "录音中的「起源计划」+ 入职日期0306",
      "next_state": "truth"
    }
  }
}
```

### knowledge/triggers/keyword-rules.json
```json
{
  "rules": [
    {
      "id": "identity_question",
      "chapter": "all",
      "keywords": ["你是谁", "你叫什么"],
      "reply_template": "identity_responses",
      "variable_by_state": true
    },
    {
      "id": "where_question",
      "chapter": "all", 
      "keywords": ["这是哪里", "在哪里"],
      "reply_template": "location_responses"
    }
  ]
}
```

## 成本控制实现

### 1. AI调用计数
- 每局开始：`ai_call_count = 0`
- 每次调AI：+1
- 超过20次：禁止调AI，强制走规则

### 2. 缓存命中率优化
- 同义输入识别（标准化处理）
- 章节内缓存（不同章节不共享）
- TTL：整个游戏会话有效

### 3. 兜底机制
- API超时：降级到规则
- API错误：返回固定兜底语
- 网络断开：纯本地模式（仅规则）

### 4. DeepSeek API 配置
```python
# engine/ai_fallback.py 配置
API_KEY = os.environ.get('DEEPSEEK_API_KEY')
BASE_URL = 'https://api.deepseek.com/v1'
MODEL = 'deepseek-chat'
MAX_TOKENS = 200  # 单次回复上限
TEMPERATURE = 0.7
```

## generate_reply 核心处理流程

`engine/hybrid_reply.py` 的 `generate_reply()` 是整个对话系统的调度中心，按优先级从高到低走 **15 条路径**：

```
玩家输入
  │
  ├─[1] / 命令路由
  │     /help /status /files /scan /read /hint /reset /memory /chapter
  │     → handle_command() 直接处理返回
  │
  ├─[2] 密码匹配
  │     _check_password() — 识别嵌入在自然语言中的密码
  │     → 解锁文件、推进章节(mm_name_revealed/chapter/ai_state)、更新记忆
  │
  ├─[3] 密码等待状态
  │     awaiting_password=True 时：
  │     ├─ _is_password_attempt() → 比对失败，给错误提示+线索
  │     └─ 不像密码 → 取消等待，继续后续流程
  │
  ├─[4] 自然语言意图识别（核心体验：用对话代替命令行）
  │     detect_intent() → 14 种意图：
  │     ├─ scan/scan_ask   → 扫描文件夹 / 无目标反问
  │     ├─ get            → 解锁加密文件夹（支持带密码直接解锁）
  │     ├─ read           → 读文件（别名解析 + fuzzy_matcher 模糊纠错）
  │     ├─ files          → 列出可访问文件
  │     ├─ status         → 章节/AI状态/文件/调用统计
  │     ├─ memory         → M-M 记忆内容
  │     ├─ clue           → 已收集线索
  │     ├─ hint           → 按章节提供下一步提示
  │     ├─ password_hint  → 密码分析引导
  │     ├─ analyze        → 综合推理（密码+线索+下一步）
  │     ├─ confirm        → 确认词执行上一条建议
  │     ├─ choose         → 多选解析（_parse_choice）
  │     ├─ install_skill  → 安装「显示隐藏文件」技能
  │     ├─ show_hidden    → 按文件夹批量揭示隐藏文件
  │     └─ help/reset     → 帮助/重置
  │
  │     设计约束：显式操作意图（show_hidden / install_skill）必须优先于裸文件名匹配。
  │     例如「显示隐藏文件 录音」应触发 show_hidden，而不是把「录音」当作 read 别名。
  │

  ├─[5] 响应库智能匹配 ★ 核心路径（零 API 成本）
  │     response_library.find_best_match() — 四维综合打分:
  │       (a) 章节权重 (b) 已读文件权重 (c) 话题匹配 (d) Jaccard+示例相似
  │     → 推进主线类别 (progression/file_commentary/discovery等) → 重置 off_topic
  │     → 非主线类别 (greeting/filler) → 累加 off_topic，超3次追加主线引导
  │     → 条件变体：mm_name_revealed 时切换 who_am_i_curious 版本
  │
  ├─[6] 学习库检索
  │     learning_store.find_similar() → 检查历史 API 学习记录
  │     → 命中 → 返回（零成本，但计入 off_topic）
  │
  ├─[7] 本地 Q&A 库降级 (qa_engine + qa-library.json)
  │     sentence_matcher embedding 语义匹配
  │     ├─ out_of_scope / basic_identity / folder_help → 直接回答
  │     ├─ conditional_answers：按 requires_files_read 选择不同回答
  │     └─ 超纲问题 → _record_off_topic() 计次 + 条件变体中嵌入主线引导
  │
  ├─[8] 文件类别询问 (find_file_suggestion)
  │     "读日记""看邮件"等 → 列出该类已解锁文件
  │
  ├─[9] 密码尝试拦截
  │     _is_password_attempt() 但未匹配已知密码 → 错误提示
  │
  ├─[10] 密码等待超时检查
  │      awaiting_password 超 30 秒 → 取消等待并提示
  │
  ├─[11] 文件阅读建议 (find_file_suggestion 补充)
  │      针对未被上面路径覆盖的文件读取意图
  │
  ├─[12] 通用响应 (greeting/filler)
  │      问候、确认词、简单交互
  │
  ├─[13] AI-RAG 兜底（降级路径）
  │      ai_fallback.generate() 调用 DeepSeek API
  │      【三层 Prompt 注入】:
  │        Layer 1: CHARACTER_CARD — M-M 5阶段人设+说话风格
  │        Layer 2: character_state prompt_suffix — 当前阶段语气
  │        Layer 3: memory.build_context_string() — 已读/已知/线索
  │        Layer 4: knowledge_search.build_knowledge_context() — RAG 检索
  │      → 结果写入缓存 + learning_store（学习闭环）
  │      → 单局上限 MAX_AI_CALLS 次 AI 调用
  │
  ├─[14] 超纲拦截
  │      天气/新闻/股票/明星等外部话题 → M-M 拒绝
  │      → _record_off_topic() 计入计数
  │
  └─[15] 超限/未配置兜底
        ├─ API 未配置 → M-M 口吻道歉
        └─ 调用超限 → "运算能力到极限了"
```

### 文件依赖关系矩阵

**哪个模块依赖哪个数据文件、哪个模块被哪个模块调用：**

```
generate_reply()  ← hybrid_reply.py（总入口）
  │
  ├─[意图识别] detect_intent() → handle_natural_intent()
  │   ├─ handle_file_command()
  │   │   ├─ file_reader.py: read_knowledge_file() → knowledge/files/**
  │   │   ├─ clue_manager.py: get_clues_for_file() → knowledge/clues.json
  │   │   ├─ folder_discovery.py: discover_targets() → knowledge/folder-discoveries.json
  │   │   ├─ rule_engine.py: find_file_commentary() → knowledge/response-library.json
  │   │   ├─ memory.py: process_file() + add_clue()
  │   │   └─ _generate_file_growth_reflection() [可注释]
  │   ├─ handle_scan_command()
  │   │   └─ folder_discovery.py: is_target_discovered()
  │   └─ handle_get_command()
  │       └─ _check_password() → knowledge/triggers/passwords.json
  │
  ├─[响应库] response_library.py: find_best_match()
  │   ├─ knowledge/response-library.json（75条目/157变体）
  │   ├─ 条件过滤: requires_files / blocked_if_mm_name_revealed
  │   └─ 条件变体: conditional_reply_idx + conditional_reply_condition
  │
  ├─[学习库] learning_store.py: find_similar()
  │   └─ cache/learned.json（API 回复自动积累）
  │
  ├─[QA库] qa_engine.py: find_answer()
  │   ├─ sentence_matcher.py: encode_batch() [embedding模型]
  │   ├─ knowledge/qa-library.json → conditional_answers
  │   └─ _select_answer() → requires_files_read 条件
  │
  ├─[规则] rule_engine.py: find_file_suggestion()
  │
  ├─[AI兜底] ai_fallback.py: generate()
  │   ├─ character_state.py: get_state() → ai_state prompt_suffix
  │   ├─ memory.py: build_context_string()
  │   ├─ knowledge_search.py: build_knowledge_context()
  │   │   ├─ sentence_matcher.py: encode_batch()
  │   │   └─ file_reader.py: read_knowledge_file() → knowledge/files/**
  │   └─ learning_store.py: add_learned() [学习闭环]
  │
  └─[建议] _save_suggestions() → _build_default_suggestions()
```

### 关键设计决策

| 维度 | 设计 |
|------|------|
| **成本控制** | 路径 1-12 全部走规则/响应库/缓存，零 AI 成本；仅路径 13 调 API |
| **单局 AI 上限** | 20 次 (MAX_AI_CALLS_PER_GAME) |
| **响应库** | 预烘焙 75 条目/157 变体，四维综合打分 |
| **学习闭环** | API 回复 → learning_store 入库 → 下次直接命中 |
| **目标发现** | 读含线索文件后 folder_discovery 自动发现目标文件夹 |
| **Embedding** | paraphrase-multilingual-MiniLM-L12-v2，异步加载+进度可观察 |
| **条件回答** | QA库支持 requires_files_read 变体，反向匹配最新进度 |
| **off_topic 拉回** | 推进主线类别(progression/file_commentary等)重置；闲聊/问候累加，超3次引导回主线 |
| **M-M自我发现** | 读 todolist.txt → mm_name_revealed=True → who_am_i_curious 解锁 |
| **文件别名** | _extract_filename() 支持"第一篇/D1/todolist"等多种叫法 |
| **密码容错** | 支持整句匹配或嵌入自然语言（"我输入密码 ZY2024!starlight"） |

### M-M 名字揭示触发条件

M-M 知道自己是"MM"有两个触发点（`hybrid_reply.py`）：

| 触发条件 | 代码位置 | 说明 |
|---------|---------|------|
| 读 `todolist.txt` | `handle_file_command`: `if search_path == "files/deck/todolist.txt"` | 玩家首次 `/read` todolist 后立即设置 |
| 输入密码 `20030323` | `handle_get_command`: `if new_state == "curious"` | 解锁工作日记后设置（兜底路径） |

设置后影响：
- `response_library.py`: who_am_i_dormant 被拦截，who_am_i_curious 解锁条件变体
- `rule_engine.py`: todolist_commentary 的 conditional_reply_idx=2 触发名字揭示版本
- `qa_engine.py`: basic_identity 条件回答切换到 MM 名字已知版本

### 模块调用图

```
generate_reply()
  ├─ handle_command()           → / 命令
  ├─ _check_password()          → passwords.json（裸密码/自然语言嵌入）
  ├─ _is_password_attempt()     → 密码识别
  ├─ detect_intent()            → 意图识别
  │   ├─ _extract_scan_target() → SCAN_TARGETS + target_id
  │   ├─ _extract_filename()    → alias_map + hidden_file display_name + fuzzy_matcher
  │   ├─ _resolve_hidden_folder() → hidden-files.json 文件夹批量揭示
  │   └─ _parse_choice()        → CN_NUMBERS 多选解析
  ├─ handle_natural_intent()
  │   ├─ handle_scan_command()   → 扫描流程（需目标已发现）
  │   ├─ handle_get_command()    → 获取 文件夹 密码 格式
  │   ├─ handle_show_hidden()    → 显示隐藏文件（按文件夹批量揭示）
  │   ├─ handle_file_command()   → 读取 + clue_manager + folder_discovery + file_commentary + growth_reflection
  │   ├─ _build_password_hint()  → 密码分析引导
  │   └─ _build_analysis_reply() → 综合推理
  ├─ response_library.find_best_match() → response-library.json ★ 核心
  ├─ learning_store.find_similar() → learning-store.json
  ├─ qa_engine.find_answer()    → qa-library.json (embedding + conditional_answers)
  ├─ find_file_suggestion()     → 文件类别匹配
  ├─ cache_manager.get()        → 缓存查询
  ├─ ai_fallback.generate()     → DeepSeek API + RAG（降级路径）
  │   ├─ character_state.get_state()
  │   ├─ memory.build_context_string()
  │   ├─ knowledge_search.build_knowledge_context()
  │   │   └─ sentence_matcher.encode_batch()
  │   └─ learning_store.add_learned() → 学习闭环
  └─ _save_suggestions()        → 建议栏 + pending_choices
      └─ _build_default_suggestions() → 章节/已读/发现目标 主线建议
```


### 回复类型 (type)

| type | 含义 | 前端渲染 |
|------|------|----------|
| `ai` | M-M 对话回复 | AI 气泡 |
| `response_library` | 响应库智能匹配命中 ★ 新 | AI 气泡 |
| `learned` | 学习库命中 ★ 新 | AI 气泡 |
| `ai_rag` | AI-RAG 生成回复 | AI 气泡 |
| `qa_library` | 本地 Q&A 库命中 | AI 气泡 |
| `rule_template` | 规则模板命中 | AI 气泡 |
| `cache` | 缓存命中 | AI 气泡 |
| `command` | 系统命令输出 | 系统提示（黄色居中） |
| `system` | 系统提醒（密码错误等） | 系统提示 |
| `file_read` | 文件读取（附 file_content） | AI 气泡 + 文件内容弹窗 |
| `file_listing` | 文件列表 | AI 气泡 + 文件列表渲染 |
| `choose_prompt` | 多选追问 | AI 气泡 + 保留 pending_choices |
| `fallback` / `limit_reached` / `out_of_scope` | 超限/拒绝 | AI 气泡 |

## 目标发现与建议栏

### 文件夹线索发现
- 配置：`knowledge/folder-discoveries.json`
- 触发：`handle_file_command()` 读取文件后调用 `folder_discovery.discover_targets()`
- 效果：
  - 已发现目标才能被扫描/获取
  - 未被发现的目标访问会提示「先读文件找线索」
- 示例：读 `todolist.txt` 后自动发现「工作日记」

### 线索分类与已解锁迁移

M-M 汇报线索时按以下优先级分类展示（`clue_manager.format_clues()`）：

1. **待扫描文件夹** —— 已发现但尚未解锁的文件夹目标，最高优先级提示
2. **待扫描文件** —— 需要玩家主动扫描的文件目标
3. **密码线索** —— 用于解锁文件夹的密码相关信息
4. **文件线索** —— 已经解锁/阅读后沉淀下来的事实性线索

**已解锁迁移规则**：
- 当「待扫描文件夹」中的某个目标被扫描解锁后（即该目标下的所有文件都进入 `memory.accessible_files`），该条目自动从「待扫描文件夹」迁移到「文件线索」。
- 实现位置：`engine/hybrid_reply.py` 的 `handle_natural_intent()` 中 `intent == "clue"` 分支。
- 判断函数：`_is_target_unlocked(target_id, game_state)`，检查 `SCAN_TARGETS[target_id].files` 是否全部在 `accessible_files` 中。
- 这样玩家看到的线索面板始终保持「待扫描」只显示未完成的行动目标，已完成的行动转化为已知信息。

### 主线建议生成

- `_build_default_suggestions()` 综合：当前章节、已读文件、已发现目标
- 建议文本呈现为「主线任务」，如「获取 工作日记 密码」
- 前端「执行建议」按钮直接把建议作为输入发送

### 密码脱敏
- 展示文本：`获取 工作日记 密码`
- 命令：可保留 `获取 工作日记 密码`（弹出密码输入框），或后端内部使用具体密码
- 前端正则 `maskPasswordText()` 自动替换明文数字/混合密码

### 前端建议栏
- 旧顶部工具栏隐藏，按钮合并到 AI 建议栏右侧
- 右侧按钮：🔍 线索 / 📁 文件 / ▶ 执行建议
- 文本区域保持左对齐，按钮右置顶

## 部署方案

### 服务器要求
- Ubuntu 22.04+
- 2GB内存（够用）
- 已开放80/443端口

### 一键部署（setup.sh）
```bash
#!/bin/bash
# 1. 安装Python和pip
sudo apt update
sudo apt install -y python3 python3-pip nginx

# 2. 安装依赖
pip3 install flask openai

# 3. 配置Nginx
sudo cp nginx.conf /etc/nginx/sites-available/awakening
sudo ln -s /etc/nginx/sites-available/awakening /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 4. 启动Flask（用gunicorn）
pip3 install gunicorn
gunicorn -w 2 -b 127.0.0.1:8080 app:app --daemon
```

### 安全配置
- API Key放在服务器环境变量，不入代码仓库
- Nginx配置：限制单IP请求频率
- 密码门（如需要）：简单的session验证
- CORS：仅允许自己的域名

### 监控（可选）
- Flask日志输出到文件
- 简单的`/health`端点
- AI调用次数统计

## 性能优化

### 前端
- 打字机效果用CSS动画，不用JS定时器
- 历史对话虚拟滚动（>100条时）
- 输入防抖（避免重复发送）

### 后端
- 缓存文件加载到内存（启动时）
- 关键词匹配用字典查找，不用遍历
- API调用异步化（用Celery或asyncio）

### 知识库
- Markdown文件按需加载
- 章节切换时预加载下一章内容
- 缓存文件不重复解析

## 隐藏功能（Debug / GM）

以下功能不影响正常游戏流程，仅作为调试和 GM 工具使用。

### GM MODE — 回复路径可视化

- **触发**：玩家在对话中发送 `GM MODE` 或 `【GM MODE】`（大小写敏感）。
- **效果**：切换 `game_state.gm_mode` 布尔开关。
- **开启后**：每次 `generate_reply()` 返回的回复末尾自动追加一行 `[GM] 路径: X-层级名称`，显示本次回复命中了哪一层调度。
- **路径层级映射**（与 `generate_reply()` 代码分支对应）：

| 内部 type | GM 显示 |
|-----------|---------|
| `command` | 1-命令解析 |
| `password` | 2-密码系统 |
| 自然意图相关（`scan`/`read`/`get`/`clue`/`status`/`memory` 等） | 3-自然语言意图 |
| `response_library` | 4-响应库匹配 |
| `learned_library` | 5-学习库匹配 |
| `qa_library` / `file_listing` | 6-Q&A库 / 6-文件类别 |
| `cache` | 8-缓存命中 |
| `out_of_scope` | 10-超纲拦截 |
| `ai_rag` | 11-AI兜底生成 |
| `fallback` / `limit_reached` | 12-API未配置 / 12-AI调用超限 |
| `ai_api_direct` | 0-AI API直调 |
| `gm_mode_toggle` | 0-GM模式 |

- **实现位置**：`engine/hybrid_reply.py`
  - `_is_gm_mode_toggle()` / `_gm_path_label()` / `_apply_gm_mode()`
  - 在 `generate_reply()` 最前面检测切换指令
  - `_save_suggestions()` 与命令分支统一应用 `_apply_gm_mode()`

### USE AI API — 直接调用 AI API

- **触发**：玩家在对话中发送 `【USE AI API】<文本>`、`[USE AI API]<文本>` 或 `USE AI API <文本>`。
- **效果**：跳过本地响应库、学习库、Q&A库、缓存等所有规则层，直接使用 `<文本>` 调用 `ai_fallback.generate()`。
- **上下文注入**：调用时仍然携带角色卡、当前 AI 状态、M-M 记忆上下文和知识库 RAG 检索结果，与普通 AI 兜底一致。
- **不影响核心玩法**：
  - 不增加 `ai_call_count`（不占用玩家有限的 20 次 AI 调用额度）
  - 不触发 `_maybe_update_memory_from_reply()`（不写入 M-M 记忆）
  - 不进入学习库和缓存
- **未配置或空文本**：若 `DEEPSEEK_API_KEY` 未配置，返回「AI API 未配置」提示；若 `<文本>` 为空，提示用户输入内容。
- **实现位置**：`engine/hybrid_reply.py` 的 `generate_reply()` 最前面。

## 未来扩展

### V2.0

- 加入声音设计
- 多结局动画
- 二周目（新剧情）

### V3.0
- 玩家存档系统
- 多AI角色（不只是当前一个）
- 玩家选择影响AI性格演化路径

## 已知风险

| 风险 | 缓解措施 |
|------|---------|
| API Key泄露 | 环境变量 + .gitignore |
| 玩家刷量消耗token | AI调用次数限制 + 密码门 |
| LLM回复不符合角色 | 严格prompt + 输出格式约束 |
| 缓存文件膨胀 | 定期清理 + 大小监控 |
