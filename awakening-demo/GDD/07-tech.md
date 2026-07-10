# 07 - 技术实现方案

## 整体架构

```
┌─────────────────────────────────────────────┐
│ 浏览器 (index.html)                          │
│   - 终端风格UI                                │
│   - 对话气泡                                  │
│   - 章节进度                                  │
│   - 输入框                                    │
└────────────────┬────────────────────────────┘
                 │ HTTP /api/chat
                 ↓
┌─────────────────────────────────────────────┐
│ Flask 后端 (app.py)                          │
│   - 路由: /api/chat                          │
│   - 路由: /api/command  (处理 /命令)         │
│   - 路由: /api/status  (AI状态)              │
└────────────────┬────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────┐
│ 混合回复引擎 (engine/hybrid_reply.py)        │
│   - 优先级判断                                │
│   - 关键词模板匹配                            │
│   - 缓存查询                                  │
│   - AI兜底生成                                │
└─────┬──────────┬──────────┬──────────────────┘
      ↓          ↓          ↓
┌────────┐ ┌─────────┐ ┌──────────────┐
│规则模板│ │缓存系统 │ │DeepSeek API    │
│JSON    │ │JSON文件 │ │deepseek-chat   │
└────────┘ └─────────┘ └──────────────┘
```

## 技术栈

| 层 | 选型 | 版本 | 理由 |
|----|------|------|------|
| 后端 | Python | 3.13 | 你已熟悉 |
| Web框架 | Flask | 3.x | 轻量、单文件易部署 |
| LLM SDK | openai | 1.x | 兼容 OpenAI API |
| 前端 | HTML5 + 原生JS | - | 无构建步骤、单文件部署 |
| 样式 | 原生CSS | - | 单文件、复古终端风 |
| 数据 | JSON文件 | - | 无需数据库 |
| 部署 | 腾讯云Ubuntu + Nginx | - | 你已有服务器 |

## 文件结构

```
awakening-demo/
├── AGENT.md                          # 项目说明（每次会话自动读）
├── app.py                            # Flask主程序（150行）
├── index.html                        # 前端（单文件，400行）
├── setup.sh                          # 一键部署脚本
├── engine/                           # 核心引擎
│   ├── __init__.py
│   ├── hybrid_reply.py               # 混合模式核心
│   ├── rule_engine.py                # 规则匹配
│   ├── cache_manager.py              # 缓存管理
│   ├── ai_fallback.py                # AI兜底
│   ├── character_state.py            # AI人格状态机
│   ├── file_reader.py                # 知识库读取
│   ├── memory.py                     # 记忆系统
│   ├── knowledge_search.py           # RAG知识检索
│   ├── fuzzy_matcher.py              # 文件名模糊纠错
│   ├── qa_engine.py                  # 本地问答库
│   └── clue_manager.py               # 线索管理
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
      "unlocks": ["work-diary/01.md", "work-diary/02.md", "..."],
      "hint": "扫描成功。工作日记文件夹已解锁：01.md ～ 10.md。要我打开哪一个？",
      "source": "入职资料中主人的生日（2003年3月23日）",
      "next_state": "curious"
    },
    "ZY2024!starlight": {
      "chapter": 3,
      "unlocks": ["private/异常观察记录.txt", "private/账号密码.txt"],
      "hint": "私人文件夹已解锁。里面有两份文件。",
      "source": "入职资料中的系统密码",
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

`engine/hybrid_reply.py` 的 `generate_reply()` 是整个对话系统的调度中心，按优先级从高到低走 12 条路径：

```
玩家输入
  │
  ├─[1] / 命令路由
  │     /help /status /files /scan /read /hint /reset /memory /chapter
  │     → handle_command() 直接处理返回
  │
  ├─[2] 密码匹配
  │     _check_password() — 识别嵌入在自然语言中的密码
  │     → 解锁文件、推进章节、更新记忆，type=ai
  │
  ├─[3] 密码等待状态
  │     awaiting_password=True 时：
  │     ├─ _is_password_attempt() → 比对失败，给错误提示+线索
  │     └─ 不像密码 → 取消等待，继续后续流程
  │
  ├─[4] 自然语言意图识别（核心体验：用对话代替命令行）
  │     detect_intent() → 12 种意图：
  │     ├─ scan/scan_ask → 扫描文件夹 / 无目标反问
  │     ├─ get          → 解锁加密文件夹（支持带密码直接解锁）
  │     ├─ read         → 读文件（别名解析 + fuzzy_matcher 模糊纠错）
  │     ├─ files        → 列出可访问文件
  │     ├─ status       → 章节/AI状态/文件/调用统计
  │     ├─ memory       → M-M 记忆内容
  │     ├─ clue         → 已收集线索（clue_manager.format_clues）
  │     ├─ hint         → 按章节提供下一步提示
  │     ├─ password_hint → 密码分析引导（不给明文密码）
  │     ├─ analyze      → 综合推理（密码+线索+下一步，_build_analysis_reply）
  │     ├─ confirm      → 确认词（好/可以/试试）执行上一条建议
  │     ├─ choose       → 多选建议中解析玩家选择（_parse_choice）
  │     └─ help/reset   → 帮助/重置
  │     → 执行后 _save_suggestions() 更新前端建议栏
  │
  ├─[5] 本地 Q&A 库 (qa_engine + qa-library.json)
  │     Jaccard 相似度匹配常见问题
  │     ├─ 游戏内问题 → 直接回答（零成本）
  │     └─ out_of_scope → _record_off_topic() 计数，超 3 次拉回主线
  │
  ├─[6] 关键词模板 (rule_engine + keyword-rules.json)
  │     60+ 条规则按 5 阶段分组，支持 requires_document_read 过滤
  │     → M-M 口吻直接返回（零成本）
  │
  ├─[7] 文件类别询问 (find_file_suggestion)
  │     "读日记""看邮件"等 → 列出该类已解锁文件
  │
  ├─[8] 密码尝试拦截
  │     _is_password_attempt() 但未匹配已知密码 → 错误提示
  │
  ├─[9] 缓存命中 (cache_manager)
  │     MD5 hash 前 12 位 + 章节 → 返回缓存（零成本）
  │
  ├─[10] 超纲拦截
  │      天气/新闻/股票/明星等外部话题 → M-M 拒绝
  │      → _record_off_topic() 计入计数
  │
  ├─[11] AI-RAG 兜底 ★ 核心
  │      ai_fallback.generate() 调用 DeepSeek API
  │      【三层 Prompt 注入】:
  │        Layer 1: CHARACTER_CARD — M-M 5阶段人设+说话风格
  │        Layer 2: memory.build_context_string() — 已读/已知/线索
  │        Layer 3: knowledge_search.build_knowledge_context() — RAG 检索
  │      → 结果写入缓存 → _maybe_update_memory_from_reply() 迭代记忆
  │      → 单局上限 20 次 AI 调用
  │
  └─[12] 超限/未配置兜底
        ├─ API 未配置 → M-M 口吻道歉
        └─ 调用超 20 次 → "运算能力到极限了"
```

### 关键设计决策

| 维度 | 设计 |
|------|------|
| **成本控制** | 路径 1-10 全部走规则/缓存，零 AI 成本；仅路径 11 调 API |
| **单局 AI 上限** | 20 次 (MAX_AI_CALLS_PER_GAME) |
| **建议系统** | 每条回复后 `_save_suggestions()` → 从回复文本或默认规则提取可执行建议 → 前端显示快捷按钮 |
| **确认执行** | 玩家说"好""可以""试试"等 → 自动执行上一条建议命令，多条则追问选择 |
| **记忆闭环** | 读文件 → `memory.process_file()` + `clue_manager` 提取线索 → `_save_memory()` 持久化 |
| **模糊纠错** | `fuzzy_matcher.correct_filename()` — 处理拼写错误（"入职自立"→"入职资料"） |
| **off_topic 拉回** | 连续 3 次无关输入 → 强制返回当前章节主线提示 |
| **文件别名** | `_extract_filename()` 支持"第一篇/D1/日记一/todolist/全员会议"等多种叫法 |
| **密码容错** | 支持整句匹配或嵌入自然语言（"我输入密码 ZY2024!starlight"） |

### 模块调用图

```
generate_reply()
  ├─ handle_command()           → / 命令
  ├─ _check_password()          → passwords.json
  ├─ _is_password_attempt()     → 密码识别
  ├─ detect_intent()            → 意图识别
  │   ├─ _extract_scan_target() → SCAN_TARGETS
  │   ├─ _extract_filename()    → alias_map + fuzzy_matcher
  │   └─ _parse_choice()        → CN_NUMBERS 多选解析
  ├─ handle_natural_intent()
  │   ├─ handle_scan_command()   → 扫描流程 + _prompt_password_for_target
  │   ├─ handle_get_command()    → _try_unlock_with_password
  │   ├─ handle_file_command()   → 读取 + clue_manager.get_clues_for_file
  │   ├─ _build_password_hint()  → 密码分析引导
  │   └─ _build_analysis_reply() → 综合推理
  ├─ qa_engine.find_answer()    → qa-library.json
  ├─ rule_engine.match_keyword_template() → keyword-rules.json
  ├─ find_file_suggestion()     → 文件类别匹配
  ├─ cache_manager.get()        → 缓存查询
  ├─ ai_fallback.generate()     → DeepSeek API + RAG
  │   ├─ memory.build_context_string()
  │   └─ knowledge_search.build_knowledge_context()
  └─ _save_suggestions()        → 建议栏 + pending_choices
      └─ _build_default_suggestions() → 章节默认建议
```

### 回复类型 (type)

| type | 含义 | 前端渲染 |
|------|------|----------|
| `ai` | M-M 对话回复 | AI 气泡 |
| `ai_rag` | AI-RAG 生成回复 | AI 气泡 |
| `qa_library` | 本地 Q&A 库命中 | AI 气泡 |
| `rule_template` | 关键词模板命中 | AI 气泡 |
| `cache` | 缓存命中 | AI 气泡 |
| `command` | 系统命令输出 | 系统提示（黄色居中） |
| `system` | 系统提醒（密码错误等） | 系统提示 |
| `file_read` | 文件读取（附 file_content） | AI 气泡 + 文件内容弹窗 |
| `file_listing` | 文件列表 | AI 气泡 + 文件列表渲染 |
| `choose_prompt` | 多选追问 | AI 气泡 + 保留 pending_choices |
| `fallback` / `limit_reached` / `out_of_scope` | 超限/拒绝 | AI 气泡 |

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
