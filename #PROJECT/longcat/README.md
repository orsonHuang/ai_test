# longcat

> **⚠️ 命名提示**：`longcat` 是 Orson 指定的项目文件夹名 / 工作代号。
> **正式产品名待定**——参考对象 Martin Magni 的《Longcat》（2024，Fancade）已在 iOS/Android/Poki 发行，直接沿用同名存在混淆与商标风险。命名工作列为待办事项，不阻塞设计推进。

## 项目描述

微信小游戏 · 滑行填充解谜 + 轻量 Roguelike。
玩家操控一只会滑行的猫：选一个方向，猫一路滑到撞墙（或撞到自己）才停，走过的格子固化成身体；在一次 run 中连续填满多个关卡，每关后三选一获得能力，用「九条命」撑到更远。

当前阶段：**GDD 编写中**（四阶段规范结构）。参考对象拆解已完成，位于 `#Game-TearDown/Longcat/`。

---

## 项目信息

| 项 | 内容 |
|----|------|
| 技术栈 | Cocos Creator（版本待定） + TypeScript |
| AI 协作 | Cocos MCP 插件（方案待定） |
| 目标平台 | 微信小游戏 |
| 玩法地基 | 滑行填充解谜（参考 Longcat） + Roguelike 元层（差异化） |
| 当前阶段 | GDD 四阶段编写中（全部 analysis 状态为 `agent_proposal`，待 Orson 确认） |
| 参考拆解 | `#Game-TearDown/Longcat/`（9 份） |
| GDD | `#PROJECT/longcat/GDD/`（四阶段规范结构） |

---

## 工作规则

1. **GDD 规范**：严格执行 `#GDD-TEMPLATE/README.md` 规范 v1——四阶段漏斗 + analysis/design 配对 + 边界即契约 + 验证收尾。**GDD 永不承载最终数值**。
2. **确认流程**：当前 GDD 全部 `analysis.md` 状态为 `agent_proposal`。Orson 逐条确认后改为 `user_confirmed`，design.md 才视为定稿。**确认前不动代码。**
3. **逻辑与引擎解耦**：滑行规则、求解器必须是不依赖 Cocos 的纯 TypeScript，可跑 node 单测，并可复用为离线关卡生成器/验证器。**架构铁律。**
4. **关卡数据远程化**：微信小游戏主包 4MB 限制 + 提审周期约束，关卡 JSON 一律走 CDN/云开发远程加载 + 本地缓存，**绝不打进包体**。
5. **可读性优先**：空间解谜的前提是全图可读。任何特效、动态遮挡、镜头跟随的提案，必须先论证对可读性的影响。
6. **引用而非复述**：需要 Longcat 的具体数据（50 关步数、难度基准、生成器架构）时，回查 `#Game-TearDown/Longcat/`，不在此重复记录。
7. **不做清单即契约**：各阶段 design.md 的「不是什么 / 不做清单 / 不负责」是硬边界，新增需求必须先回上游改 analysis（标记 `superseded`），不得在下游偷偷加。

---

## 目录结构

```
longcat/
├── README.md              # 本文件（项目 INDEX）
└── GDD/                   # 四阶段规范结构
    ├── README.md          # GDD INDEX + 项目专属规范说明
    ├── 00_concept/        # 做什么 / 给谁玩 / 凭什么不可替代
    ├── 01_top_design/     # 循环单位 / 规模 / 系统范围
    ├── 02_architecture/   # 系统清单 / 依赖 / 数据流 / 目录映射
    └── 03_systems/        # S01~S05 各系统 analysis + design
```

> Cocos 工程位置待定（可能由 Cocos Dashboard 管理在工作区外），确认后在此记录绝对路径。

---

## 注意事项

### 待 Orson 拍板

| # | 决策项 | 选项 | 优先级 |
|---|-------|------|-------|
| 1 | **正式产品名** | 待定（需与 Martin Magni 的 Longcat 区分） | 🟡 不阻塞设计 |
| 2 | **GDD 全部 analysis 问题块** | 逐条确认 / 推翻 | 🔴 **阻塞开发** |
| 3 | **Cocos Creator 版本** | 3.7 / 3.8+ | 🟡 影响 MCP 选型 |
| 4 | **MCP 插件选型** | Funplay MCP（3.8+，开源）/ cocos-mcp-server（3.7+，商店）/ Cocos Agent | 🟡 |
| 5 | **关卡托管方案** | 微信云开发 / 自建 CDN | 🟢 可延后 |

### 已知风险

| 风险 | 等级 | 应对 |
|------|------|------|
| 玩法与 Longcat 高度重合，抄袭感 | 🔴 | 差异化压在元层（九条命 + 能力系统）+ 微信社交层 |
| 求解器性能（网格 >8×10 指数爆炸） | 🔴 | 网格限 8×10 内 + 强剪枝，大网格改用启发式 |
| 内容消耗快（玩家数天刷完） | 🟡 | 每日挑战优先级高于堆关卡量 |
| 超包体 | 🟡 | 关卡远程化 + 资源分包 |
| 无版号只能靠广告 | 🟢 | 设计阶段预留广告位（提示/复活/双倍） |

### 关键参考（回查入口）

| 需要什么 | 去哪看 |
|---------|--------|
| 机制规则 / 伪代码 | `#Game-TearDown/Longcat/gameplay/核心机制拆解.md` |
| 50 关步数基准 / 难度曲线 | `#Game-TearDown/Longcat/numbers/难度曲线实证数据.md` |
| 关卡生成器 + 求解器架构 | `#Game-TearDown/Longcat/systems/关卡系统.md` |
| 微信生态适配 / 首版范围 | `#Game-TearDown/Longcat/notes/对微信小游戏项目的启示.md` |
| 差异化方向推导 | `#Game-TearDown/Longcat/notes/设计亮点与可借鉴点.md` §4 |
