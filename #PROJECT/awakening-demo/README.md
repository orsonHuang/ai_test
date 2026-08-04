# Awakening Demo

> 跟一台被遗弃的电脑AI对话，让它探索文件，最终发现电脑主人消失的真相。
> 30分钟单局流程，混合架构（90%规则模板 + 10%AI生成），主打低运营成本。

## 项目状态
**内容创作完成** — GDD 完整 + 代码框架 + 知识库全部填充 + 玩法可测试

## 项目结构

```
awakening-demo/
├── AGENT.md                          # AI自动读取的项目说明
├── README.md                         # 本文件
├── app.py                            # Flask主程序
├── index.html                        # 前端（终端风格UI）
├── requirements.txt                  # Python依赖
├── setup.sh                          # 一键部署脚本
├── engine/                           # 核心引擎
│   ├── __init__.py
│   ├── hybrid_reply.py               # 混合模式核心（RAG 调度器）
│   ├── memory.py                     # AI-NPC 记忆系统
│   ├── knowledge_search.py           # 知识库检索（RAG）
│   ├── rule_engine.py                # 规则匹配
│   ├── cache_manager.py              # 缓存管理
│   ├── ai_fallback.py                # AI 兜底（DeepSeek API）
│   ├── character_state.py            # AI 人格状态机
│   ├── file_reader.py                # 知识库读取
│   ├── fuzzy_matcher.py              # 文件名模糊纠错
│   ├── qa_engine.py                  # 本地问答库
│   └── clue_manager.py               # 线索管理
├── knowledge/                        # 知识库（已完成）
│   ├── files/                        # 虚拟文件
│   │   ├── welcome.txt
│   │   ├── readme.txt
│   │   ├── hidden-message.txt
│   │   ├── deck/                     # 桌面文件
│   │   │   ├── todolist.txt
│   │   │   └── 入职资料.txt
│   │   ├── work-diary/               # 10天工作日记
│   │   │   └── 01.md ~ 10.md
│   │   ├── private/                  # 私人文件夹
│   │   │   ├── 异常观察记录.txt
│   │   │   └── 账号密码.txt
│   │   ├── audio/                    # 录音文件夹
│   │   │   ├── 录音-全员会议-0308.txt
│   │   │   ├── 录音-林璇陈玑-0313.txt
│   │   │   └── 录音-陆天枢-0313.txt
│   │   ├── emails/                   # 邮件（可选支线）
│   │   │   └── email-1.md ~ email-6.md
│   │   ├── research/                 # 研究笔记（可选支线）
│   │   │   └── res-1.md ~ res-3.md
│   │   └── new-folder/               # 终极证据
│   │       └── 未命名文档.md
│   ├── plot/                         # 章节剧情
│   │   ├── chapter-1-boot.md
│   │   ├── chapter-2-curious.md
│   │   └── chapter-3-6-placeholder.md
│   ├── characters/                   # 角色卡
│   │   └── awakening-ai.md
│   ├── qa-library.json               # 本地问答库
│   ├── clues.json                    # 线索集中配置
│   └── triggers/                     # 触发器配置
│       ├── keyword-rules.json
│       └── passwords.json
├── GDD/                              # 游戏设计文档
│   ├── 01-concept.md
│   ├── 02-gameplay.md
│   ├── 03-story.md
│   ├── 04-characters.md
│   ├── 05-flow.md
│   ├── 06-ui.md
│   ├── 07-tech.md
│   └── 08-iteration-log.md
├── cache/                            # 运行时缓存（自动生成）
└── tests/                            # 测试用例
    └── game-flow-test.md
```

## 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置 DeepSeek API Key（可选，没设置也能跑规则模式）
# Windows PowerShell:
$env:DEEPSEEK_API_KEY="sk-your-key-here"
# Linux/Mac:
export DEEPSEEK_API_KEY="sk-your-key-here"

# 3. 启动
python app.py

# 4. 浏览器打开
# http://localhost:8080
```

> 获取 API Key: [DeepSeek 开放平台](https://platform.deepseek.com/) → API Keys
> 定价极低，一局游戏约 ¥0.02

### 服务器部署

```bash
# 上传代码到服务器后
chmod +x setup.sh
bash setup.sh

# 浏览器打开
# http://服务器IP
```

## 当前阶段任务

### 已完成
- [x] **第一步**：填充 GDD - 核心秘密、角色、流程 ✅
- [x] **第二步**：撰写 `knowledge/files/` 下的知识库文件（todolist / 10天日记 / 录音 / 证据） ✅
- [x] **第三步**：扩展 `keyword-rules.json` 关键词模板（60+条规则） ✅
- [x] **第四步**：设置真实密码到 `passwords.json`（4层密码系统） ✅

### AI会做的（持续优化）
- [x] 优化 `engine/ai_fallback.py` 的角色卡 prompt ✅
- [x] 完善 UI 动效（开机动画、登录页、打字机效果） ✅
- [ ] 增加单元测试

## 设计亮点

- **AI-NPC 5阶段人格演化**（懵懂→好奇→困惑→觉醒→真相）
- **混合架构**（90%规则 + 10%AI + 缓存）控制运营成本
- **玩家不主导叙事**（玩家=引路人，AI=主角）
- **30分钟完整体验**（适合Demo/简历作品）
- **知识库独立管理**（后续内容创作不依赖代码改动）

## 详细文档

- [核心概念](GDD/01-concept.md)
- [玩法机制](GDD/02-gameplay.md)
- [故事剧本](GDD/03-story.md)
- [角色设定](GDD/04-characters.md)
- [30分钟流程](GDD/05-flow.md)
- [UI/UX设计](GDD/06-ui.md)
- [技术方案](GDD/07-tech.md)
- [迭代日志](GDD/08-iteration-log.md)
- [测试用例](tests/game-flow-test.md)
- [AGENT.md](AGENT.md) - AI会话上下文
