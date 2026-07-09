# 03 - 待完成清单

> 按优先级分组。每完成一项就移到 02-done.md。

---

## 🔴 P0 - 阻塞后续工作（已完成 ✅）

### 剧情核心决策
- [x] 决定 **电脑主人消失的真相** — 公司同事/老板是外星人，主人发现真相后被消失
- [x] 决定 **电脑主人的身份/职业** — 女游戏策划（开发向），新入职游戏公司
- [x] 决定 **AI的名字** — M-M（主人入职时创建的工作助理）
- [x] 决定 **AI的原始用途** — 工作助理（任务管理、文件整理、信息检索）
- [x] 决定 **玩家在游戏中的身份** — 主人的青梅竹马（男性），主人消失后去她家调查
- [x] 决定 **公司同事角色** — 陆天枢(Boss/天枢)、林璇(同事A/天璇)、陈玑(同事B/天玑)、沈爻光(高层/摇光)，取自北斗七星
- [x] 决定 **外星人暴露的违和感** — 从不吃饭喝水、伤口愈合极快、听不懂"童年""梦"等词、游戏角色从培养室出生/成长极快
- [x] 决定 **密码系统** — 三层递进（密码1=入职账号 → 密码2=VPN密码 → 密码3=起源计划线索）
- [x] 决定 **叙事结构** — 29天工作日记为核心叙事载体，周日留白，*标记重要日

---

## 🟡 P1 - 内容创作（核心工作）

### GDD 文档更新（已完成 ✅）
- [x] GDD/01-concept.md — 核心Hook更新为外星人悬疑故事
- [x] GDD/02-gameplay.md — 文件解锁机制适配5层文件系统
- [x] GDD/03-story.md — 完整故事剧本（29天日记+6章节+对话样本+多结局）
- [x] GDD/04-characters.md — 角色设定全部填充（M-M+主人+4个北斗七星角色+玩家）
- [x] GDD/05-flow.md — 30分钟流程拆解适配新故事
- [ ] GDD/06-ui.md — UI适配（可选，后续）
- [ ] GDD/07-tech.md — 技术文档适配（可选，后续）

### 知识库内容（下一阶段重点）
- [ ] knowledge/files/todolist.txt（桌面文件，含日记路径线索）
- [ ] knowledge/files/入职资料.txt（含密码1）
- [ ] knowledge/work-diary/01.md ~ 29.md（29天工作日记，含*标记日和留白日）
- [ ] knowledge/private/异常观察记录.txt（密码1解锁）
- [ ] knowledge/private/账号密码.txt（含密码2 - VPN密码）
- [ ] knowledge/company/录音/会议录音_xxx.txt（文本转写格式）
- [ ] knowledge/company/录音/1v1_林璇_xxx.txt
- [ ] knowledge/company/录音/1v1_陈玑_xxx.txt
- [ ] knowledge/private/证据/final-evidence.txt（密码3解锁 - 终极证据）

### 剧情脚本
- [ ] knowledge/plot/chapter-1-boot.md（完整对话脚本）
- [ ] knowledge/plot/chapter-2-curious.md
- [ ] knowledge/plot/chapter-3-puzzled.md
- [ ] knowledge/plot/chapter-4-awakening.md
- [ ] knowledge/plot/chapter-5-truth.md
- [ ] knowledge/plot/chapter-6-ending.md

### 触发器配置
- [ ] knowledge/triggers/passwords.json
  - 替换为真实密码（3个密码的具体值待定）
- [ ] knowledge/triggers/keyword-rules.json
  - 按5个阶段 + 新的故事内容扩展关键词模板
  - 每个阶段20+条差异化回复

---

## 🟢 P2 - 代码优化

### AI 角色卡
- [ ] engine/ai_fallback.py → build_prompt() 函数
  - 基于新的 GDD/04-characters.md 填充真实角色卡
  - 5阶段 prompt 差异化
  - 知识边界适配新故事

### 规则引擎
- [ ] engine/rule_engine.py
  - 支持模糊匹配
  - 支持正则表达式
  - 按AI状态返回不同模板

### 文件系统适配
- [ ] engine/file_reader.py
  - 适配新的目录结构（work-diary/ private/ company/）

---

## 🔵 P3 - UI/UX 优化

- [ ] 章节进度条适配6章新内容
- [ ] 打字机效果（AI回复逐字显示）
- [ ] 状态切换动画
- [ ] 密码正确闪烁效果
- [ ] 响应式设计

---

## 🟣 P4 - 测试与部署

- [ ] 端到端30分钟体验测试
- [ ] 边界场景测试
- [ ] 部署到腾讯云

---

## 用户决策记录

> 每次做了关键决策，在这里追加。

### 2026-07-08 - P0 核心剧情决策
- 故事方向：悬疑 — 游戏公司同事/老板是外星人
- 电脑主人：女游戏策划（开发向），新入职游戏公司
- AI名字：M-M（主人入职时创建的工作助理）
- 玩家身份：主人的青梅竹马（男性）
- 叙事载体：29天工作日记，周日留白，*标记重要日
- 密码系统：3层递进（入职账号→VPN密码→起源计划线索）
- 角色命名：陆天枢、林璇、陈玑、沈爻光（北斗七星）
- 外星违和感：不吃饭喝水、快速愈合、语言异常、游戏设定非人
- 公司伪装：游戏公司，游戏中出现不符合正常人的设定

### 2026-07-07
- 决定项目方向：AI对话探索解谜游戏
- 决定架构：混合模式
- 决定部署：腾讯云服务器
- 决定上下文衔接方案：AGENT.md + 迭代日志
