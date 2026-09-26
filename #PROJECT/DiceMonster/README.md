# DiceMonster · 骰子打怪

> 项目代号：**DiceMonster**（暂定，可改）
> 立项日期：2026-08-07
> 灵感参考：《小丑牌》(Balatro) 的「投掷→选子→组牌型→结算」核心体验 + 《杀戮尖塔》爬塔结构
> 技术选型：**TapTap Maker + 纯 Lua**（旧 Godot 方案已废弃，见 GDD 02_architecture analysis）

## 项目一句话

玩家用 **5 颗 D6**（初始 5×无词条标准 D6）反复投掷、重摇选中的骰子、**恰好选 3 颗**组成牌型后对怪物造成伤害；在 **3 层 × 8 行行进度地图**上选择路线，通过**全部领取式奖励**（可放弃）、D6 构型替换、单面修改与商店附魔把骰子池养成专属构筑；击败第 3 层最终 Boss 通关。

## 工作规则

- **GDD 权威**：设计文档以 `DiceMonsterTT/GDD/`（四阶段结构）为准；旧版 GDD 存于外层 `GDD_旧/`，仅历史参考。
- **SSOT 分工**：设计规则看 GDD；最终数值与内容表看 `DiceMonsterTT/scripts/data/*.lua`；怪物美术与意图详表 SSOT 是 `DiceMonsterTT/docs/怪物设计总览.md`。
- **配置化原则**：数值、怪物、关卡、能力、词条、奖励全部在 `scripts/data/*.lua`，改平衡不改逻辑代码。
- **文档规范**：GDD 遵循 `#GDD-TEMPLATE/README.md`（四阶段漏斗 + analysis/design 配对 + 边界即契约）。
- **完成门槛**：每次代码/配置修改必须同步对应 GDD 与 `project-plan/README.md`，运行 `npm test`；测试通过后先询问 Orson，确认后才推送 Maker 构建与预览。
- 工程 AI 协作规则见 `DiceMonsterTT/AGENTS.md` 与 `DiceMonsterTT/CLAUDE.md`。

## 伤害公式（创新点）

```
伤害 = (牌型基础值 + 所选骰子点数之和[含词条修正]) × 能力倍率 × 装备占位 × 技能树占位
```

- **5 选 3 玩法**：投掷 5 颗骰子，重摇**选中的**（每回合 2 次），固定选 3 颗出牌
- **牌型基础值**：散牌 0 / 对子 5 / 顺子 10 / 三条 20（4 种牌型）
- **只有 D6 的构筑**：所有掉落与事件骰均为 D6，以六面点值配置区分标准、稳健、顺子、爆发、强攻、奇数、偶数和残缺构型；每骰最多 1 条词条（当前 14 条，未完整实现的词条不进入随机附魔池）
- **17 条肉鸽能力**：牌型、全局、极值、连击与重摇等类型，详见 `DiceMonsterTT/scripts/data/Abilities.lua`

> 详细规则见 `DiceMonsterTT/GDD/03_systems/S01_dice_core/design.md`。

## 核心循环（TL;DR）

1. **地图**：每层 8 行，每行 2~3 个候选节点选 1 个前进；行配置强制节奏（开局必战、Boss 前保底休息）。
2. **战斗**：投掷 → 重摇 → 选 3 出牌 → 怪物按意图序列反击，2~4 回合分胜负。
3. **奖励（全部领取式，可放弃）**：金币自动入账；构型 D6、附魔机会、单面修改和能力按节点等级概率生成；满 5 颗时进入替换界面，可放弃替换。
4. **节点**：商店（买骰/附魔/词条骰）、休息（回血30%/附魔/跳过）、事件（5 个随机事件）、奖励节点（不战斗直接领奖）。
5. **层过渡**：击败层 Boss 回血 20% 进下一层；第 3 层 final_boss 胜利通关。

> 详细见 `DiceMonsterTT/GDD/01_top_design/design.md` 与 `03_systems/`。

## 目录结构

```
DiceMonster/
├── README.md                  ← 你正在看（项目 INDEX）
└── DiceMonsterTT/             ← 工程仓库（git submodule，TapTap Maker + Lua）
    ├── GDD/                   ← GDD v2（2026-09-02 重写，四阶段结构）
    │   ├── README.md          ← GDD 导航与使用规则
    │   ├── 00_concept/        ← 概念（analysis + design）
    │   ├── 01_top_design/     ← 顶层设计（analysis + design）
    │   ├── 02_architecture/   ← 系统架构（analysis + design）
    │   └── 03_systems/        ← S01 骰子核心 / S02 行进度地图 / S03 战斗意图 /
    │                          S04 奖励经济（已实现）+ S05 外层局外（规划）
    ├── scripts/               ← Lua 代码：core/（规则）+ data/（配置）+ ui/（界面）
    ├── tests/                 ← 本地 Lua 单测、语法检查与文档漂移守卫
    ├── docs/                  ← 怪物设计总览（SSOT）等
    ├── documents/             ← 怪物设计表 xlsx（美术需求）
    └── README.md              ← 工程规则、实现实况与验证入口
├── GDD_旧/                    ← 旧版 GDD（历史参考，不再维护）
```

## 当前状态

- [x] 脑暴阶段（`#PROJECT/Brainstorm/brainStorm-0807/`）
- [x] 立项 + 伤害公式创新（牌型基础值 + 点数之和）
- [x] 核心闭环可玩：3 层 × 8 行地图 / 战斗 / 奖励 / 商店 / 休息 / 事件 / 层过渡 / 通关
- [x] 配置表落地（`scripts/data/*.lua`：DiceTypes 8 种 D6 构型 / Monsters 34 只 / Abilities 17 条 / DiceAffixes 14 条 / Events 5 个等）
- [x] GDD v2 重写（四阶段规范结构，追认实现现状）
- [x] 独立本地测试（`npm test`：Lua 语法、核心逻辑、战斗回归、文档漂移）
- [ ] 数值平衡 v1（玩家初始/最大HP已改100，首层11怪意图已落地；待试玩与后两层重调）
- [ ] 意图系统补全（DOT 已跨回合生效；debuff 与部分特殊语义仍为空转）
- [ ] 外层系统（开始页/大厅/存档/结算）——P1，蓝图见 GDD S05
- [ ] 局外养成（技能树+碎片，碎片来源待拍板）——P1
- [ ] 装备 / 局外商店 / 无尽模式——P2
- [ ] 音效——P2
- [ ] 美术与 UI 全量验收（怪物 portrait 已接入，仍需逐页面真机核对）

## 已知缺陷（见各系统 GDD analysis）

1. 玩家HP100，全34怪新意图已落地；首层已验收，第二/三层及全链路平衡待试玩。
2. 怪物表已不再引用空debuff/special；隐藏Boss下回合变身/加压已实现，待实机核对提示。
3. `blood_oath`、`overclock` 的代价未完整实现，已暂停进入随机附魔池。
4. 存档、外层、结算与局外成长尚未实现。

## 编辑约定

- 所有 `.md` 用 UTF-8、中文。
- GDD 内数值一律标注 SSOT 来源（`scripts/data/*.lua`），GDD 只保留规则与示例。
- 涉及"是否要做"的开放问题，集中在对应阶段/系统的 `analysis.md` 末尾「待定决策」，由 Orson 拍板。
- 修改 GDD 前先读对应 `analysis.md`，理解决策理由再动 design。
