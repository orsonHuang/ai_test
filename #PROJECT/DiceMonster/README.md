# DiceMonster · 骰子打怪

> 项目代号：**DiceMonster**（暂定，可改）
> 立项日期：2026-08-07
> 灵感参考：《小丑牌》(Balatro) 的「投掷→选子→组牌型→结算」核心体验 + 《杀戮尖塔》爬塔结构
> 技术选型：**TapTap Maker + 纯 Lua**（旧 Godot 方案已废弃，见 GDD 02_architecture analysis）

## 项目一句话

玩家用 **5 颗骰子**（初始 5×无词条 d6）反复投掷、重摇选中的骰子、**恰好选 3 颗**组成牌型后对怪物造成伤害；在 **3 层 × 8 行行进度地图**上选择路线，通过**全部领取式奖励**（可放弃）、骰子替换与商店附魔把骰子池养成专属构筑；击败第 3 层最终 Boss 通关。

## 工作规则

- **GDD 权威**：设计文档以 `DiceMonsterTT/GDD/`（v2，四阶段结构）为准；旧版 GDD 存于 `DiceMonsterTT/GDD_旧/`，仅历史参考。
- **SSOT 分工**：设计规则看 GDD；最终数值与内容表看 `DiceMonsterTT/scripts/data/*.lua`；怪物美术与意图详表 SSOT 是 `DiceMonsterTT/docs/怪物设计总览.md`。
- **配置化原则**：数值、怪物、关卡、能力、词条、奖励全部在 `scripts/data/*.lua`，改平衡不改逻辑代码。
- **文档规范**：GDD 遵循 `#GDD-TEMPLATE/README.md`（四阶段漏斗 + analysis/design 配对 + 边界即契约）。
- 工程 AI 协作规则见 `DiceMonsterTT/AGENTS.md` 与 `DiceMonsterTT/CLAUDE.md`。

## 伤害公式（创新点）

```
伤害 = (牌型基础值 + 所选骰子点数之和[含词条修正]) × 能力倍率 × 装备占位 × 技能树占位
```

- **5 选 3 玩法**：投掷 5 颗骰子，重摇**选中的**（每回合 2 次），固定选 3 颗出牌
- **牌型基础值**：散牌 0 / 对子 5 / 顺子 10 / 三条 20（4 种牌型）
- **多面骰 + 词条**：掉落骰池 d6/d8/d10/d12（d10 为新增；d4 仅事件降级用），每骰最多 1 条词条（8 条，2 条占位未实装）
- **13 条肉鸽能力**：5 类（牌型加成/全局倍率/最大面/连击/重摇），详见 `DiceMonsterTT/scripts/data/Abilities.lua`

> 详细规则见 `DiceMonsterTT/GDD/03_systems/S01_dice_core/design.md`。

## 核心循环（TL;DR）

1. **地图**：每层 8 行，每行 2~3 个候选节点选 1 个前进；行配置强制节奏（开局必战、Boss 前保底休息）。
2. **战斗**：投掷 → 重摇 → 选 3 出牌 → 怪物按意图序列反击，2~4 回合分胜负。
3. **奖励（全部领取式，可放弃）**：金币自动入账 + 必给 1 颗骰子（满 5 颗进替换界面，可放弃替换）+ 按节点等级概率掉能力。
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
    ├── GDD_旧/                ← 旧版 GDD（01-16 平铺，2026-08-20 止），仅历史参考
    ├── scripts/               ← Lua 代码：core/（规则）+ data/（配置）+ ui/（界面）
    ├── docs/                  ← 怪物设计总览（SSOT）等
    ├── documents/             ← 怪物设计表 xlsx（美术需求）
    └── README.md              ← 工程仓库说明（旧版内容，待与本文档合并）
```

## 当前状态

- [x] 脑暴阶段（`#PROJECT/Brainstorm/brainStorm-0807/`）
- [x] 立项 + 伤害公式创新（牌型基础值 + 点数之和）
- [x] 核心闭环可玩：3 层 × 8 行地图 / 战斗 / 奖励 / 商店 / 休息 / 事件 / 层过渡 / 通关
- [x] 配置表落地（`scripts/data/*.lua`：Monsters 33 只 / Abilities 13 条 / DiceAffixes 8 条 / Rewards / RestShop / Events 5 个 / MapConfig / Balance）
- [x] GDD v2 重写（四阶段规范结构，追认实现现状）
- [ ] 数值平衡 v1（**玩家 HP 代码 1000 为测试值，设计值 100，正式前全链路回收**）
- [ ] 意图系统补全（debuff 空转、DOT 退化为一次性，见 GDD S03 缺口清单）
- [ ] 外层系统（开始页/大厅/存档/结算）——P1，蓝图见 GDD S05
- [ ] 局外养成（技能树+碎片，碎片来源待拍板）——P1
- [ ] 装备 / 局外商店 / 无尽模式——P2
- [ ] 音效——P2
- [ ] 美术资源接入（怪物 portrait 全空，图片资产已就位一批）

## 已知缺陷（见各系统 GDD analysis）

1. 商店附魔先扣钱不退款（`Run.lua`）
2. 附魔随机词条含 2 条占位无效词条、无稀有度权重（`RestShop.GetRandomAffix`）
3. 事件"命运转盘"文案与实现不一致（移除骰子 vs 降级 d4）
4. 死代码：3 选 1 奖励生成器、random 节点配置（拍板废弃，待清理）

## 编辑约定

- 所有 `.md` 用 UTF-8、中文。
- GDD 内数值一律标注 SSOT 来源（`scripts/data/*.lua`），GDD 只保留规则与示例。
- 涉及"是否要做"的开放问题，集中在对应阶段/系统的 `analysis.md` 末尾「待定决策」，由 Orson 拍板。
- 修改 GDD 前先读对应 `analysis.md`，理解决策理由再动 design。
