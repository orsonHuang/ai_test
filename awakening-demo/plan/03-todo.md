# 03 - 待完成清单

> 按优先级分组。每完成一项就移到 02-done.md。

---

## 🔴 P0 - 阻塞后续工作（必须先做）

### 剧情核心决策
- [ ] 决定 **电脑主人消失的真相**（4个方向选1或自创）
  - 方向A：自我放逐（伦理问题主动消失）
  - 方向B：被迫消失（被组织灭口）
  - 方向C：主人就是AI（意识上传）
  - 方向D：自定义
- [ ] 决定 **电脑主人的身份/职业**（研究员？工程师？科学家？）
- [ ] 决定 **AI的名字**（占位"Awak"）
- [ ] 决定 **AI的原始用途**（家用助手？研究伙伴？监控？）
- [ ] 决定 **玩家在游戏中的身份**（路人？调查员？被托付者？）

---

## 🟡 P1 - 内容创作（核心工作）

### GDD文档填充
- [ ] GDD/03-story.md
  - 6个章节的详细对话脚本
  - 多结局设计（A/B/C/D）
  - 关键对话样本（懵懂/好奇/觉醒/真相4阶段）
- [ ] GDD/04-characters.md
  - AI详细性格描述
  - 玩家在故事中的作用
  - 电脑主人性格碎片
- [ ] GDD/05-flow.md
  - 章节内的每分钟事件表
  - 状态切换的具体触发条件

### 知识库内容
- [ ] knowledge/files/welcome.txt（开机欢迎语）
- [ ] knowledge/files/readme.txt（系统说明）
- [ ] knowledge/files/emails/1.md（第一封邮件 - 含密码线索）
- [ ] knowledge/files/emails/2.md（加密邮件 - 解锁后内容）
- [ ] knowledge/files/diary/1.md（第一篇日记）
- [ ] knowledge/files/diary/2.md（加密日记）
- [ ] knowledge/files/research/1.md（研究笔记）
- [ ] knowledge/files/final-revelation.md（真相文件）
- [ ] knowledge/plot/chapter-1-boot.md（完整对话脚本）
- [ ] knowledge/plot/chapter-2-curious.md
- [ ] knowledge/plot/chapter-3-puzzled.md
- [ ] knowledge/plot/chapter-4-awakening.md
- [ ] knowledge/plot/chapter-5-truth.md
- [ ] knowledge/plot/chapter-6-ending.md

### 触发器配置
- [ ] knowledge/triggers/passwords.json
  - 替换 alpha-7 为真实密码
  - 替换 X-7-final 为真实密码
  - 添加更多密码（如有需要）
- [ ] knowledge/triggers/keyword-rules.json
  - 补充更多关键词模板
  - 按章节分组
  - 4阶段人格对应的不同回复

---

## 🟢 P2 - 代码优化

### AI角色卡
- [ ] engine/ai_fallback.py → build_prompt() 函数
  - 填充真实角色卡内容（基于GDD/04-characters.md）
  - 4阶段prompt差异化
  - 知识边界严格定义
  - 说话规则细化

### 规则引擎
- [ ] engine/rule_engine.py
  - 支持模糊匹配（不只精确关键词）
  - 支持正则表达式
  - 多模板随机选择（避免重复感）
  - 按AI状态返回不同模板

### 缓存优化
- [ ] engine/cache_manager.py
  - 同义输入识别
  - 跨章节缓存复用
  - 缓存大小监控

### 状态机
- [ ] engine/character_state.py
  - 添加过渡状态（curious→puzzled的中间态）
  - 状态切换动画提示

---

## 🔵 P3 - UI/UX优化

### 视觉
- [ ] index.html
  - 打字机效果（AI回复逐字显示）
  - 状态切换动画
  - 真相揭露动画
  - 章节进度条动画
  - 错误输入震动反馈
  - 密码正确闪烁效果

### 响应式
- [ ] 桌面（>1024px）布局优化
- [ ] 平板（768-1024px）适配
- [ ] 手机（<768px）适配

### 可访问性
- [ ] 高对比度模式
- [ ] 字号可调
- [ ] 完整键盘操作

---

## 🟣 P4 - 测试与部署

### 测试
- [ ] tests/game-flow-test.md 完整执行
- [ ] 端到端30分钟体验测试
- [ ] 边界场景测试（断网/API失败/输入异常）
- [ ] 多浏览器兼容测试
- [ ] 移动设备测试

### 部署
- [ ] 上传代码到腾讯云服务器
- [ ] 运行 setup.sh
- [ ] 配置Nginx（如需要）
- [ ] 域名解析（可选）
- [ ] 浏览器实测
- [ ] 简历作品链接生成

### 监控
- [ ] 错误日志配置
- [ ] AI调用次数监控
- [ ] 用户行为分析（可选）

---

## ⚪ P5 - 远期迭代

- [ ] 声音设计（环境音、状态音、情绪音）
- [ ] 二周目内容（新剧情、新AI状态）
- [ ] 多AI角色（不只当前一个）
- [ ] 玩家存档系统
- [ ] 选择影响AI性格演化路径
- [ ] 桌面客户端（Electron打包）
- [ ] Steam发布（远期）

---

## 用户决策记录

> 每次你做了关键决策，在这里追加。

### 2026-07-07
- 决定项目方向：AI对话探索解谜游戏
- 决定架构：混合模式
- 决定部署：腾讯云服务器
- 决定上下文衔接方案：AGENT.md + 迭代日志

### 待决策
- 核心秘密方向
- AI名字
- 主人身份
- 玩家身份
