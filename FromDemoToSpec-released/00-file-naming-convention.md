# F2S 文件命名规范

> **本文是什么**：F2S 工作流内所有产物的命名规则。把"项目-版本-类型"三段式命名从隐性约定显化为强制规则。
> **本文不是什么**：流程文档（流程见 README / 01-input-elicitation-protocol / 03-prototype-to-spec-mapping）。
> **编号 00**：本文不在流程主链上，是横切规范，与其他 00 类文档（command-manual / ai-collaboration-principles / input-elicitation-protocol）平级。
> **为什么需要**：发布版二次复核发现「无框架版」产出的文件命名混用（`index-v2.html` / `spec.md` / `design-doc-endless-path.md` / `03-design-doc-template-project.md` 副本），策划/开发回头取材时无法仅凭文件名判断"这是什么 / 哪一版 / 对应哪个原型"。三段式命名 = 文件名即元数据，零阅读成本归档。

---

## WHAT · 命名规则

### 1. HTML 原型

```
{原型名}-v{版本号}_mvp.html
```

| 例 | 说明 |
|----|------|
| `挂机装备RPG-v5_mvp.html` | 原型「挂机装备 RPG」第 5 版可玩原型 |
| `塔防-v1_mvp.html` | 原型「塔防」首版 |

- **原型名**：中英文均可，但同一原型内保持一致。避免 `tower-defense` 和 `塔防` 混用。
- **版本号**：从 v1 开始，连续递增。**不跳号**（不写 v1、v3 直接跳）。
- **后缀 `_mvp`**：固定，区分于将来可能的 `_full` / `_demo` 等变体。

### 2. 配套 Markdown 文档

```
{原型名}_input.md                       ← 输入文档（仅生成一次，无版本号）
{原型名}-v{版本号}_mvp.md                 ← MVP 设计文档（与 HTML 同版本）
{原型名}-v{版本号}_spec.md                ← AI 提取的 Spec（与 HTML 同版本）
{原型名}-v{版本号}_spec-technical.md      ← 技术 Spec（可选，与 HTML 同版本）
{原型名}-v{版本号}_design-doc.md          ← 策划填写的 game/product 模板产出（WHY）
{原型名}-v{版本号}_design-doc-project.md  ← 策划填写的 project 模板产出（WHAT+HOW）
CHANGELOG.md                             ← 变更记录（项目内单文件，无前缀）
```

**判断规则**：
- 凡是"AI 提取自代码"的产物，文件名含 `spec`
- 凡是"策划/人工填写"的产物，文件名含 `design-doc`
- 凡是"WHAT+HOW 落地清单"的产物，文件名含 `design-doc-project`
- 凡是"原始输入 / 问答补齐结果"的产物，文件名含 `input`

### 3. 一个完整原型目录的标准布局

```
Demo/挂机装备RPG/
├── 挂机装备RPG_input.md
├── 挂机装备RPG-v1_mvp.html
├── 挂机装备RPG-v1_mvp.md
├── 挂机装备RPG-v2_mvp.html
├── 挂机装备RPG-v2_mvp.md
├── ...
├── 挂机装备RPG-v5_mvp.html
├── 挂机装备RPG-v5_mvp.md
├── 挂机装备RPG-v5_spec.md
├── 挂机装备RPG-v5_spec-technical.md   ← 可选，若需交付程序员
├── 挂机装备RPG-v5_design-doc.md
├── 挂机装备RPG-v5_design-doc-project.md
└── CHANGELOG.md
```

---

## WHY · 为什么必须三段式

| 痛点 | 三段式如何解决 |
|------|--------------|
| 一周后回看，不知道 `spec.md` 是哪个原型的 | 文件名前缀显式带原型名 |
| 多版本并存时 `_mvp.html` 哪个最新？ | 版本号显式后缀，按字典序排即时序 |
| 看到 `design-doc.md` 不知道是 game 模板还是 project 模板 | `_design-doc.md` vs `_design-doc-project.md` 一眼区分 |
| `03-design-doc-template-project.md`（模板副本）和真正填写的 design-doc 混在一起 | 模板副本必须重命名为 `{原型名}-vN_design-doc-project.md`，不保留 04- 前缀 |

---

## HOW · 强制规则

1. **创建任何 F2S 产物文件前，先按本文规则命名**——不允许先用 `index.html` / `spec.md` 等无前缀名再后补改名。
2. **模板副本必须立即重命名**：从 `04-*-template-*.md` 拷贝出来填写时，第一步是改名为 `{原型名}-vN_*.md`，不允许保留 `04-` 前缀的填好副本。
3. **同一原型内命名一致**：不允许第 v1 叫「挂机装备RPG」、v2 又叫「endless-path」。改名需要走 §四「迁移」流程。
4. **AI 生成产物时主动按本规则命名**——不依赖用户提示。

---

## 四、迁移：发现已有不规范命名怎么办

| 情况 | 处理 |
|------|------|
| 已发布到 released/ 的旧产物 | 不动（避免破坏对外引用），下次同原型新版本起按规范 |
| 工作目录内的不规范命名 | 走文档维护流程：先批量改名 + 同步引用，在 CHANGELOG 记录 |
| 模板副本未改名 | 立即改名，CHANGELOG 标注「修正模板副本命名」 |

---

## 五、与其他规范的关系

- `Demo/README.md` 段「输出目录规范」是本文的简版引用，本文是完整版
- `00-ai-collaboration-principles.md` §6 产物命名的格式应与本文同步——本文为权威源


