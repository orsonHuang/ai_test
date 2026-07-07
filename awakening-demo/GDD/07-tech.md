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
│规则模板│ │缓存系统 │ │百炼API        │
│JSON    │ │JSON文件 │ │qwen3.7-plus   │
└────────┘ └─────────┘ └──────────────┘
```

## 技术栈

| 层 | 选型 | 版本 | 理由 |
|----|------|------|------|
| 后端 | Python | 3.13 | 你已熟悉 |
| Web框架 | Flask | 3.x | 轻量、单文件易部署 |
| LLM SDK | openai | 1.x | 兼容百炼API |
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
│   └── file_reader.py                # 知识库读取
├── knowledge/                        # 知识库（你主导）
│   ├── files/                        # 虚拟文件
│   │   ├── welcome.txt
│   │   ├── readme.txt
│   │   ├── emails/
│   │   ├── diary/
│   │   └── research/
│   ├── plot/                         # 剧情节点
│   │   ├── chapter-1-boot.md
│   │   ├── chapter-2-curious.md
│   │   ├── chapter-3-puzzled.md
│   │   ├── chapter-4-awakening.md
│   │   ├── chapter-5-truth.md
│   │   └── chapter-6-ending.md
│   ├── characters/                   # 角色卡
│   │   └── awakening-ai.md
│   └── triggers/                     # 触发器配置
│       ├── passwords.json
│       ├── keyword-rules.json
│       └── chapter-triggers.json
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
    调用百炼API
    基于当前章节和AI状态动态构建prompt
    """
    character = load_character(game_state['current_state'])
    history = game_state.get('history', [])[-5:]  # 最近5轮
    
    prompt = build_prompt(character, history, game_state)
    
    response = client.chat.completions.create(
        model='qwen3.7-plus',
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
    "alpha-7": {
      "chapter": 3,
      "unlocks": ["emails/2.md", "diary/2.md"],
      "hint": "X-7 出现在第一封邮件中",
      "next_state": "puzzled"
    },
    "[FILL:终极密码]": {
      "chapter": 6,
      "unlocks": ["final-revelation.md"],
      "hint": "需要读完全部研究文件",
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

### 4. 百炼API配置
```python
# app.py 配置
API_KEY = os.environ.get('DASHSCOPE_API_KEY')
BASE_URL = 'https://coding.dashscope.aliyuncs.com/v1'
MODEL = 'qwen3.7-plus'
MAX_TOKENS = 200  # 单次回复上限
TEMPERATURE = 0.7
```

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
