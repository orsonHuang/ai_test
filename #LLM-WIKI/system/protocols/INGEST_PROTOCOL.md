# INGEST_PROTOCOL · 内容消化与入库

> 本文是来源从评分到 Wiki 写入的状态转换 SSOT。评分细则见 `SCORING_SYSTEM.md`，输出闸门见 `system/maintenance/checklists/ingest-stage-gates.md`。

## 一、加载边界

仅在用户明确表达消化或入库意图时读取。普通 Query 不加载本文、评分系统或维护规则。

开始前读取：

1. `system/registry/KNOWLEDGE_SCOPE.md`；未配置时一次补齐用途、主题和排除边界。
2. `system/maintenance/checklists/ingest-stage-gates.md`。
3. `SCORING_SYSTEM.md`、`raw-sources/README.md` 与相应模板。
4. 只有进入 Wiki 阶段才读 `wiki/README.md`、`WIKI-LINK-STANDARD.md`、`system/registry/index.md` 和目标 domain。

模型按 `MODEL_ROUTING.md` 选择。当前配置满足建议或更高时不要求降级；无法识别模型时不猜测。

## 二、来源获取

| 来源 | 前置处理 |
|---|---|
| URL / 附件 | 核实标题、作者、日期、正文完整性和可追溯位置 |
| Clippings | 检查截断、段落、图片与嵌入内容。无前缀或无 `status` 字段的文件视为新导入；确认终态后标准化为 `【TODO】YYYYMMDD-简短标题.md`，frontmatter 添加 `status: todo` |
| IMA | 本地配置必须 `enabled: true`；按 `system/integrations/IMA-GUIDE.md` 鉴权、选择知识库、搜索并获取全文 |
| 多来源 | 默认逐篇评分；只有共同问题链、连续章节或互补证据明确且用户确认时才合并 raw |

只评分时不改来源文件。IMA 初始化只建立绑定，不等于授权导入内容。

## 三、四阶段硬闸门

每个阶段结束必须停止并等待用户确认。“按推荐执行”“可以”只确认当前闸门，除非用户明确授权多个后续阶段。

### 阶段 0 · 来源质量与评分

1. 搜索标题、URL 或内容指纹，核对历史评分与重复入库。
2. 读取 `system/registry/quick-reference.md` 和相关 Wiki 标题，判断增量价值。
3. 按 `SCORING_SYSTEM.md` 独立评分；合并候选仍逐篇评分。
4. 输出评分包、合并建议、跳过候选与下一阶段模型建议。

用户确认后：跳过项写 `system/registry/skipped-sources.md`；其余只授权写 raw，不授权 Wiki。

### 阶段 1 · raw 消化稿审核

1. 先写“模块 → 命题 → 载体 → 推导 → 例证/数据”骨架。
2. 使用 `raw-sources/raw-source.template.md`，逐章节标注原文位置。
3. 保留定义、论证链、推导、案例、数据和作者限定；不得压缩成结论列表。
4. 写质量批注：`✅ 亮点`、`⚠️ 存疑`、`🔗 可延伸`、`🔄 冗余`。
5. 执行 raw 深度与风格检查，输出阶段一审核包后硬停。

阶段一通过只授权进入归属规划。禁止提前修改 Wiki、index、raw-list、domains 或 CHANGELOG。

### 阶段 2 · Wiki 归属与批注消费规划

1. 反思现有 domain 是否覆盖；需要新域时先提案。
2. 判断更新既有 Wiki、新建 Wiki 或暂时仅保留 raw。
3. 为每条批注指定目标页、目标段落、消费方式和放弃理由。
4. 预估写入后行数，只作为拆分信号，不作为压缩理由。
5. 输出阶段二归属包后硬停。

阶段二通过才授权 Wiki 写入与维护链。

### 阶段 3 · Wiki 写入与维护闭合

1. 完整写入后实测行数；达到 300 行评估拆分，达到 500 行必须拆分或明确挂账。
2. 按规划消费 raw 批注；条目清空后删除整个 `## 批注` 段。
3. 更新受影响的 domain、`system/registry/index.md`、`system/registry/quick-reference.md`、`system/registry/raw-list.md` 和 `system/registry/KNOWLEDGE_STATUS.md`。
4. 将对应 Clippings 文件的 frontmatter `status` 改为 `done`，文件名前缀从 `【TODO】` 改为 `【DONE】`。
5. 运行健康检查与 Query / Agent 回归。
6. 更新根目录 `NOW.md`、`system/maintenance/CHANGELOG.md`，输出阶段三闭合包。

## 四、零状态规则

- 第一份来源允许只生成 raw；没有足够证据时不为“闭环”强建 Wiki。
- 空 domain、空 index、零 Wiki、零 prompt 都是合法状态。
- 新建 domain 必须来自稳定范围需求，不以单篇来源标题命名。
- 首次 Wiki 可只有一份来源，但必须标明单来源边界。

## 五、质量批注

| 类型 | 触发 | 后续 |
|---|---|---|
| ✅ 亮点 | 原文中值得突出且易遗漏的关键命题 | 阶段二规划吸收位置 |
| ⚠️ 存疑 | 证据不足、概念冲突、数据或翻译待核 | 保留限定或追加核实 |
| 🔗 可延伸 | 与既有知识存在不可替代的关系 | 按链接标准规划内联或底部 |
| 🔄 冗余 | 已被现有 Wiki 完整覆盖 | 写明覆盖位置，决定跳过或只补证据 |

批注是审核工作区，不是永久正文。阶段三必须逐条闭合为“已吸收 / 已限定 / 已放弃并说明”。

## 六、失败与补审

发现越过闸门时：立即停止新材料 → 标出越权写入 → 重新输出缺失审核包 → 由用户选择保留、重写或回滚。不得用后补文档掩盖未经确认的内容写入。
