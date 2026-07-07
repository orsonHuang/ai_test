# 08 - 迭代日志

> 每次会话开始时，AI会先读本文件了解最新进展。
> 每次有改动时，在下方追加新记录。

---

## 2026-07-07 - 项目初始化

### AI操作
- 建立 `awakening-demo/` 项目结构
- 编写 `AGENT.md`（项目说明 + 工作约定）
- 撰写 8 个 GDD 文档初稿：
  - 01-concept.md（核心概念）
  - 02-gameplay.md（玩法机制）
  - 03-story.md（故事剧本）
  - 04-characters.md（角色设定）
  - 05-flow.md（30分钟流程）
  - 06-ui.md（UI/UX）
  - 07-tech.md（技术方案）
  - 08-iteration-log.md（本文件）

### 当前状态
- 框架阶段
- 文本内容均为占位符 `[FILL:xxx]`
- 等待用户填充剧情和具体内容

### 下一步
- [ ] 用户填充 `03-story.md` 中的 `[FILL:xxx]`（核心秘密、章节内容、对话样本）
- [ ] 用户填充 `04-characters.md` 中的 `[FILL:xxx]`（AI名字、主人身份、玩家身份）
- [ ] 决定密码设置（2-3个关键密码）
- [ ] 撰写 `knowledge/files/` 下的虚拟文件（邮件、日记、研究笔记）
- [ ] 撰写 `knowledge/plot/` 下的章节剧情脚本
- [ ] 启动代码框架搭建（app.py + engine/ + index.html）

### 待用户决策
- [ ] 电脑主人消失的真相选哪个方向（A自我放逐/B被消失/C主人就是AI/D自定义）
- [ ] AI的具体名字和性格
- [ ] 电脑主人的身份和职业
- [ ] 玩家在游戏中的身份
- [ ] 多结局的具体设计

### 技术决策记录
- API：百炼（用户已有Key）
- 部署：腾讯云Ubuntu + Nginx
- 模式：混合（90%规则 + 10%AI + 缓存）

---

## 2026-07-07 - 代码框架完成

### AI操作
- 搭建 `engine/` 6个核心模块（hybrid_reply/rule_engine/cache_manager/ai_fallback/character_state/file_reader）
- 撰写 `app.py` Flask后端（4个API端点：/health /api/chat /api/status /api/reset）
- 撰写 `index.html` 终端风格前端（章节进度、AI状态徽章、打字机效果、键盘操作）
- 撰写 `requirements.txt` 和 `setup.sh` 一键部署脚本
- 撰写 `knowledge/triggers/keyword-rules.json`（5个基础关键词模板）
- 撰写 `knowledge/triggers/passwords.json`（alpha-7和X-7-final两个示例密码）
- 撰写 `knowledge/files/` 占位文件（welcome/readme/emails/diary/research/final-revelation）
- 撰写 `knowledge/plot/` 章节占位（chapter-1-boot、chapter-2-curious、chapter-3-6-placeholder）
- 撰写 `knowledge/characters/awakening-ai.md` 角色卡
- 撰写 `tests/game-flow-test.md` 测试用例

### 框架验证结果
- ✅ 5个核心模块全部加载成功
- ✅ Flask服务启动（端口8088）
- ✅ /health 端点正常
- ✅ 关键词模板触发（"你是谁" → rule_template）
- ✅ 密码系统（alpha-7 → 章节3，状态puzzled）
- ✅ 文件读取（/read welcome.txt → 显示内容）
- ✅ AI兜底调百炼API（dormant状态返回懵懂风格回复）

### 当前状态
- 代码框架完成，混合模式5个分支全部跑通
- 文本内容仍为占位符 `[FILL:xxx]`
- 等待用户填充剧情和具体内容

### 下一步
- [ ] 用户填充 `GDD/03-story.md` 中的 `[FILL:xxx]`
- [ ] 用户填充 `GDD/04-characters.md` 中的 `[FILL:xxx]`
- [ ] 决定密码设置（替换alpha-7和X-7-final为真实密码）
- [ ] 撰写 `knowledge/files/` 下的具体文件内容
- [ ] 撰写 `knowledge/plot/` 下的章节剧情脚本
- [ ] 本地体验：浏览器打开 http://localhost:8088 玩一下
- [ ] 调整 `engine/ai_fallback.py` 的角色卡prompt

### 已知小问题
- 端口8080被占用，需用PORT=8088启动（不影响功能）

---

## 2026-07-07 - plan文件夹建立

### AI操作
- 创建 `plan/` 子目录
- 编写 `plan/README.md`（快速跳转）
- 编写 `plan/01-roadmap.md`（整体路线图，6个阶段）
- 编写 `plan/02-done.md`（已完成清单，4批次）
- 编写 `plan/03-todo.md`（待完成清单，按P0-P5优先级）
- 更新 `AGENT.md` 当前阶段为"内容创作"

### 当前状态
- 框架+代码+GDD全部完成
- 进入内容创作阶段
- 等待用户做核心剧情决策

---

