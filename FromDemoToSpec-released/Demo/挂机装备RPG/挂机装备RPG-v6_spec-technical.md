# 挂机装备RPG · 技术架构 Spec v6

> **模板用途**：由 AI 从 HTML 原型自动提取并填入。面向"交付给程序员"场景。
> **来源原型**：`Demo/挂机装备RPG/挂机装备RPG-v6_mvp.html`
> **配套通用 spec**：`Demo/挂机装备RPG/挂机装备RPG-v6_spec.md`
> **生成版本**：v6（基于 v5 spec-technical 增量更新，含 v6-c1/c2/c3a/c3b/c3c 全部改动；c4 战力公式重写已废弃）
> **提取时间**：2026-06-12（v5）/ 2026-06-13（v6）
> **人工复核**：[X] 已复核（原型阶段产物）

---

## 0. v5 → v6 演进摘要（详细参见 design-doc § 0）

详细演进表参见 `挂机装备RPG-v6_design-doc.md` § 0。

技术层面 v6 主要改动：
- 新增 `batchOpenN()` 函数 + 加速开箱按钮 ×N 显示
- `chestGenMs` 锁死 1500ms / `chestOpenMs = max(1500, 2500-ct×125)`
- `genStages` 删除喘息关分支 / BOSS mod 2.0（c3b 临时 2.5 已回退）/ 精英 mod 1.3
- `rEquip` 锁定槽位渲染：目标列大字「📦 还需 N 箱」 + 高亮边框；删除 `rUnlockHint` 函数
- 新增 `regionOf` / `rRegion` / `showRegionUnlock` 函数
- `endC` win 首通分支检测 BOSS：发宝石礼包 + ct+1 档高品宝箱（临时切 S.ct 跑 genEquip 的副作用路径，待重构）+ 区域解锁飘字
- `AUTO_EQUIP_UNLOCK` 500→1000

**已废弃改动**（c4 系列）：calcPower / totalPow 几何平均重写、pStats 实战属性公式、量级放大系数——全部回退到 c3c 状态。详见 §9 已知问题。

---

## 一、概述

| 字段 | 内容 |
|------|------|
| 原型名称 | 挂机装备RPG (Idle Equipment RPG) |
| 原型类型 | 经济/资源流 + 即时制自动战斗 |
| 文件规模 | 单文件 HTML，255 行（CSS ~55 行、HTML 结构 ~43 行、JS ~147 行） |
| 运行时长 | 无限循环（挂机类），单次战斗约 5~30 秒 |
| 关键运行时假设 | 浏览器单文件运行；无 localStorage（无存档，刷新即重置）；无网络请求；纯 JS 状态机驱动 |

---

## 二、架构概览

### 2.1 模块依赖图

> 来源：原型代码顶层结构（`const C`、`const S`、`const EB`、函数群划分）

```
CONFIG (C)
    │ 只读常量注入
    ▼
STATE (S)  ←──────────────────────────────┐
    │ 状态读写                              │
    ▼                                      │
逻辑层                                     │
  ├─ 宝箱系统（genChest / openChest / upgradeChest）
  ├─ 装备系统（genEquip / receive / chooseEquip / upgradeSlot）
  ├─ 战斗系统（startChallenge / tick / endC）
  └─ 解锁系统（slotUnlocked / manualUnlocked / autoEquipUnlocked）
    │ emit 事件
    ▼
EventBus (EB)
    │ 订阅回调
    ▼
渲染层（rAll / rChest / rEquip / rPlayer / rCombat / rChoice）
    │ DOM 写入
    ▼
HTML 界面
```

### 2.2 分层职责

| 层 | 代表标识 | 职责 | 禁止 |
|----|---------|------|------|
| CONFIG | `const C` | 所有可调参数的唯一来源 | 在逻辑层硬编码魔法数字 |
| STATE | `const S` | 运行时唯一状态容器 | 在渲染层修改状态 |
| 逻辑层 | 普通函数群 | 状态读写 + emit 事件 | 直接操作 DOM |
| EventBus | `const EB` | 解耦逻辑层与渲染层 | 在 EB 回调内做逻辑计算 |
| 渲染层 | `r*` 函数群 | 读 STATE → 写 DOM | 修改 STATE |

---

## 三、状态机

> 来源：`S.ph` 字段 + `enterCombat / exitCombat / receive / chooseEquip / sellPending` 函数

### 3.1 主状态（`S.ph`）

```
         ┌──────────────────────────────────────────────┐
         │                                              │
    ┌────┴────┐    enterCombat()    ┌──────────┐        │
    │  idle   │ ─────────────────► │  combat  │        │
    │（挂机中）│ ◄─────────────────  │（战斗中）│        │
    └────┬────┘    exitCombat()    └──────────┘        │
         │                                              │
         │ receive()（新装备战力 > 当前）                │
         ▼                                              │
    ┌─────────┐    chooseEquip()                        │
    │ choice  │ ──────────────────────────────────────► │
    │（抉择中）│    sellPending()                        │
    └─────────┘ ──────────────────────────────────────► │
                                                        └─ → idle
```

| 状态 | 描述 | 可执行操作 |
|------|------|-----------|
| `idle` | 宝箱产出/自动开箱运行中 | 进入战斗、手动开箱（20箱后）、升级宝箱、升级装备 |
| `combat` | 战斗界面，等待挑战或战斗中 | 挑战关卡、退出战斗 |
| `choice` | 新装备弹出，等待玩家决策 | 替换（chooseEquip）、放弃（sellPending）；自动替换倒计时中 |

### 3.2 战斗子状态（`S.cRun`）

| `S.cRun` | `S.lastResult` | 含义 |
|---------|---------------|------|
| `false` | `null` | 战斗未开始 |
| `true` | `null` | 战斗进行中 |
| `false` | `'win'` | 战斗胜利，等待下一步 |
| `false` | `'lose'` | 战斗失败，等待重试 |

> **v5.1++**：`win` 状态下若玩家不点"进入下一关"而直接 `exitCombat` 退出战斗，会自动 `S.cSt++`（除非已是最后一关）。避免下次 `enterCombat` 仍指向已通关关卡导致重打。

---

## 四、核心数据模型

> 来源：`const C`、`const S`、`genEquip` 函数

### 4.1 全局 CONFIG（`const C`，关键字段）

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `CHEST_GEN_BASE` | ms | 1500 | 宝箱产出基础间隔（热调可改） |
| `CHEST_OPEN_BASE` | ms | 2500 | 宝箱开启基础间隔 |
| `CHEST_TIER_BOOST` | float | 0.08 | 每升一级宝箱，速度提升 8% |
| `CHEST_MAX_PER_TIER` | int | 50 | 每级宝箱上限增量（基础 200） |
| `MANUAL_OPEN_UNLOCK` | int | 20 | 手动开箱解锁所需总开箱数 |
| `AUTO_EQUIP_UNLOCK` | int | 500 | 自动替换解锁所需总开箱数 |
| `AUTO_EQUIP_DELAY` | ms | 3000 | 自动替换倒计时 |
| `COL_UNLOCK` | int[7] | [0,0,40,100,200,500,1000] | 7 列装备槽的解锁所需总开箱数 |
| `TICK` | ms | 300 | 战斗基础 tick 间隔 |
| `SELL_BASE` | int | 50 | 卖出金币基础值 |
| `EUP_BASE` / `EUP_GROW` | int/float | 50 / 1.5 | 装备升级费用：`EUP_BASE × EUP_GROW^(lv-1)` |
| `QA` | 品质数组[10] | — | 普通→至尊，含名称/颜色/最大词缀数/战力区间 |
| `AP` | 词缀池[15] | — | 词缀定义（id/名称/类型 flat|pct/稀有度 r/数值范围/权重） |
| `AW` | 权重映射 | — | 各词缀 id → 战力计算权重 |

### 4.2 运行时 STATE（`const S`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `ph` | string | 主状态机：`'idle'` / `'combat'` / `'choice'` |
| `cs` | int | 当前宝箱数量 |
| `gd` | int | 金币 |
| `gm` | int | 宝石 |
| `ct` | int | 宝箱等级（0~9） |
| `totalOpened` | int | 历史总开箱数（解锁判据） |
| `eq` | Equip\|null[14] | 14 个装备槽当前装备 |
| `cSt` | int | 当前选中关卡索引 |
| `clr` | int[] | 已通关关卡索引列表 |
| `cRun` | bool | 战斗是否进行中 |
| `cPH/cPM/cEH/cEM` | int | 玩家/敌人当前HP/最大HP |
| `cS` | object | 本局战斗统计：伤害/承伤/暴击/治疗/开始时间/结束时间 |
| `cTid` | timer | 战斗 tick setTimeout id |
| `pnd` | Equip\|null | 待决策的新装备 |
| `pSi` | int | 待决策的槽位索引 |
| `gT/oT/pT` | timer | 产出/开箱/进度条 setInterval id |
| `oProg` | int | 开箱进度（ms 累计，0~chestOpenMs） |
| `autoEquip` | bool | 自动替换是否开启 |
| `autoTimer` | timer | 自动替换倒计时 setTimeout id |
| `lastResult` | string\|null | 最近战斗结果：`'win'` / `'lose'` / null |

### 4.3 装备对象（Equip）

```js
{
  s: int,        // 槽位索引 0~13
  q: int,        // 品质索引 0~9（对应 C.QA）
  lv: int,       // 等级（初始为该槽当前装备等级，无装备时为 1）
  af: Affix[],   // 词缀数组（1~6 条，由品质决定上限）
  p: int         // 战力（calcPower 计算结果，缓存值）
}

// Affix
{
  id: string,    // 词缀 id（如 'atk' / 'crR' / 'pen'）
  n: string,     // 显示名称
  t: 'flat' | 'pct',  // 数值类型
  v: int         // 数值
}
```

### 4.4 关卡对象（Stage，由 `genStages()` 生成）

```js
{
  id: int,       // 关卡编号（1~100）
  n: string,     // 显示名称（含类型标记：·BOSS / ·精英 / ·喘息）
  hp: int,       // 敌人 HP
  atk: int,      // 敌人攻击
  def: int,      // 敌人防御
  rec: int,      // 推荐战力
  gr: int,       // 首通金币奖励
  cr: int,       // 首通宝箱奖励数量
  edod: int,     // 敌人闪避（0~30）
  teg: '' | 'elite' | 'boss'  // 关卡类型标记
}
```

---

## 五、核心算法

### 5.1 宝箱速度公式

> 来源：`chestGenMs()` / `chestOpenMs()` 函数，L129-130

```
产出间隔(ms) = floor(CHEST_GEN_BASE / (1 + ct × CHEST_TIER_BOOST))
开启间隔(ms) = floor(CHEST_OPEN_BASE / (1 + ct × CHEST_TIER_BOOST))
宝箱上限     = 200 + ct × CHEST_MAX_PER_TIER
```

### 5.2 宝箱品质概率分布

> 来源：`chestPool()` / `chestProbDist()` / `rollChestQ()` 函数，L146-148

```
当前宝箱等级 ct：
  候选品质池 = [max(0, ct-2) .. min(ct+2, 9)]（3~5 个品质）
  各品质权重 = (0.5 + DROP_LUCK×0.1)^i  （i 为从高到低的索引，越高品质权重越低）
  归一化后按概率滚点
```

### 5.3 装备战力计算

> 来源：`calcPower()` / `baseStatPow()` / `baseStat()` 函数，L143-150

```
基础属性值 = (槽位类型基础值 + (lv-1) × 成长值) × (1 + q × 0.25)
  攻击槽：BATK1=5, 成长 BATK_LV=3
  防御槽：BDEF1=7, 成长 BDEF_LV=3
  生命槽：BHP1=20, 成长 BHP_LV=10

基础战力贡献：
  攻击槽 = 基础属性值 × 2
  防御槽 = 基础属性值 × 1.5
  生命槽 = 基础属性值 × 0.5

词缀战力贡献：
  百分比词缀 = 数值 × AW[词缀id]
  固定值词缀 = 数值 × AW[词缀id]

总战力 = clamp(基础战力 + 所有词缀战力, 1, 999999)
```

### 5.4 战斗 tick 算法

> 来源：`tick()` 函数，L199

```
每 tick（基础 300ms，受攻速调整）：
  玩家攻击：
    命中判定：random(0,100) < clamp(玩家命中 - 敌闪避, 5, 95)
    命中时：
      基础伤害 = max(玩家ATK × PLAYER_DMG_MULT - 敌DEF × (1 - 穿甲/100), 1)
      暴击判定：random(0,100) < 暴击率
      最终伤害 = floor(基础伤害 × 暴伤/100 if 暴击 else 基础伤害) × (1 + 伤害加成/100)
      吸血：恢复 floor(最终伤害 × 吸血/100)，上限最大HP
    未命中：显示 MISS

  敌方攻击：
    玩家闪避判定：random(0,100) < 玩家闪避
    闪避成功：
      反击判定：random(0,100) < 玩家反击率
      反击：造成 floor(max(玩家ATK×0.5 - 敌DEF, 1)) 伤害
    未闪避：
      受伤 = max(敌ATK × ENEMY_MULT - 玩家DEF, 1) × (1 - 伤害减免/100)

  tick 间隔 = clamp(TICK × 100/(100 + 攻速), 100, 600) ms
```

### 5.5 关卡生成公式

> 来源：`genStages()` 函数，L126

```
第 i 关（0-indexed）：
  baseP    = floor(250 × 1.065^i)
  mod      = 2.0(BOSS) | 1.5(精英) | 0.65(喘息，i>10 且 i%10==1) | 1.0(普通)
  推荐战力 = floor(baseP × mod)
  HP       = floor(推荐战力 × 0.55)  // v5.1: 0.7 → 0.55
  ATK      = floor(推荐战力 × 0.07)  // v5.1: 0.045 → 0.07
  DEF      = floor(推荐战力 × 0.012) // v5.1: 0.004 → 0.012
  首通宝箱 = 8 + floor(i/3)（精英×1.5，BOSS×2；v5.1 从 20+floor(i/2) 调降）
  敌闪避   = min(20, floor(i × 0.2)) // v5.1: 上限 30→20，增长率 0.3→0.2
  玩家初始 HP = 200 // v5.1: 500 → 200（pStats 起始值）
```

---

## 六、定时器管理

> 来源：`restartGenTimer()` / `restartOpenTimer()` + L248，`startAutoCountdown()`

| 定时器 | 变量 | 类型 | 触发动作 | 启动/重启时机 |
|--------|------|------|---------|-------------|
| 宝箱产出 | `S.gT` | setInterval | `genChest()` | 游戏初始化、宝箱等级升级 |
| 宝箱开启 | `S.oT` | setInterval(100ms 轮询) | 累计到 `chestOpenMs` 后调用 `openChest()` | 游戏初始化、宝箱等级升级 |
| 进度条刷新 | `S.pT` | setInterval(200ms) | `rChest()` | 游戏初始化 |
| 战斗 tick | `S.cTid` | setTimeout（链式递归） | 下一帧战斗计算 | `startChallenge()` |
| 自动替换 | `S.autoTimer` | setTimeout（链式递归） | 每秒倒计时，归零后调用 `chooseEquip()` | 进入 choice 状态且 autoEquip=true |

**清理规则**：
- `resetGame()` 清除所有 setInterval + setTimeout
- `exitCombat()` 清除 `S.cTid`
- `stopAutoCountdown()` 清除 `S.autoTimer`
- 宝箱等级升级时 `restartGenTimer()` + `restartOpenTimer()` 先 clearInterval 再重建

---

## 七、容错与边界保护

> 来源：`cl()` 函数、各处 `Math.max/Math.min`、`try-catch`

| 场景 | 保护方式 | 来源 |
|------|---------|------|
| 属性数值上限 | `cl(v, lo, hi)` 工具函数，各属性均有上限（暴击率 100%、闪避 20%、吸血 50% 等） | L123、L195 |
| 伤害下限 | `Math.max(伤害, 1)`，保证最小 1 点 | L199 |
| tick 速率 | `clamp(tick间隔, 100, 600)` 防止攻速过高导致 0ms tick | L199 |
| 宝箱溢出 | `genChest()` 判断 `S.cs < chestMax()` 才产出 | L154 |
| 空装备槽开箱 | `openChest()` 检查 `slots.length === 0`，无可用槽时 lg 警告并 return | L160 |
| 自动替换 DOM 异常 | `try { D('aeCD').textContent = txt } catch(e) {}` 静默处理 | L176 |
| 战斗中断 | `tick()` 首行检查 `S.cRun`，false 直接 return | L199 |
| 金币/宝石不足 | `upgradeSlot` / `upgradeChest` 检查余额，不足时 lg 提示并 return | L187-188 |
| 宝箱已最高级 | `upgradeChest()` 检查 `S.ct >= 9`，return | L188 |
| 多次 victory/defeat 节点残留 | 战斗开始/阶段切换时 `querySelectorAll('.victory,.defeat').forEach(e=>e.remove())` | L193、L198、L213 |

---

## 八、EventBus 事件清单

> 来源：`EB.on` 注册，L218-235

| 事件 | 触发来源 | 订阅处理 |
|------|---------|---------|
| `log` | `lg()` | 向日志面板追加行 |
| `cu`（chest update） | `genChest / openChest` 等 | `rChest()` |
| `ed`（equip drop） | `receive()` | `rEquip + rPlayer + rGoldGem + showDrop 动效` |
| `ec`（equip change） | `upgradeSlot()` | `rEquip + rPlayer + rGoldGem` |
| `phc`（phase change） | 所有状态切换 | `rDynamic + rChest + rGoldGem` |
| `cn`（choice new） | `receive()` 进入 choice | `rChoice + 显示 sv + rChest` |
| `cd`（choice done） | `chooseEquip / sellPending` | `stopAutoCountdown + 隐藏 sv + rChest + rEquip + rPlayer + rGoldGem` |
| `gd`（gem drop） | `openChest()` | `lg + gemFlash 动效 + shake + rChest + rGoldGem` |
| `ctc`（chest tier change） | `upgradeChest()` | `rChest + rGoldGem` |
| `opened` | `openChest()` | `rEquip + rChest + rGoldGem` |
| `cEn`（combat enter） | `enterCombat()` | `stopAutoCountdown + rDynamic + rCombat + rChest` |
| `cEx`（combat exit） | `exitCombat()` | `rDynamic + rChest + rGoldGem` |
| `cs`（combat start） | `startChallenge()` | `rCombat()` |
| `cf`（combat float） | `tick()` | `showFloat 浮字动效` |
| `chp`（combat hp） | `tick()` / `endC()` | `rCombat()` |
| `ce`（combat end） | `endC()` | `showVictory + rCombat + rPlayer + rGoldGem` |
| `sc`（stage change） | `selectStage()` | `rCombat()` |
| `ae_toggle` | `toggleAutoEquip()` | （无渲染订阅，由 `rChest` 驱动） |

---

## 九、程序员接手注意事项

1. **无持久化**：当前版本无 localStorage，所有状态随页面刷新丢失。正式工程需设计存档方案（`S` 对象序列化到 localStorage 或服务端）。

2. **定时器内存泄漏风险**：原型中 `S.pT`（进度条 200ms 刷新）在 `resetGame()` 中被清除但未在 `init()` 前保护判断——正式实现需确保所有定时器在重新创建前已被清除。

3. **战斗 tick 为链式 setTimeout**：不是 `setInterval`，每帧末尾自调度下一帧。好处是动态 tick 间隔（攻速影响），坏处是中断需要显式清除 `S.cTid`。正式实现建议封装为 `CombatSystem` 类统一管理。

4. **EventBus 无优先级/无错误隔离**：原型 EB 实现极简，订阅者异常会中断后续订阅者执行。正式工程建议加 try-catch 隔离。

5. **渲染层全量重绘**：`rEquip()` 每次重建 14 个装备槽的完整 innerHTML，`rCombat()` 每次重建关卡按钮列表。原型频次（每 100ms 一次开箱轮询触发）勉强可接受，正式工程需要局部更新。

6. **`STAGES` 在初始化时全量生成**：100 关数据在脚本加载时一次性计算存入数组，内存占用极小，正式工程可直接复用此模式或改为按需生成。

7. **词缀战力权重（`AW`）与词缀定义（`AP`）解耦**：`AP` 定义词缀属性，`AW` 定义各词缀对战力的贡献系数，两者通过 `id` 关联。正式工程扩展词缀时需同时维护两处。

---

## 已知数值难题（v6 沉淀，留给数值策划专项处理）

### 问题描述

战力数字与实战表现不完全一致——v6 试玩多次出现以下场景：

- 玩家战力 1 万，打过推荐 2.5 万的关卡（高估了关卡难度，玩家以为打不过）
- 玩家战力 4820，打不过推荐 1175 的 20 关 BOSS（高估了玩家实力）
- 单件装备战力 45，全身总战力 29（量级错位，部分小于整体）

### 已尝试的方案与结论

| 版本 | 方案 | 结论 |
|------|------|------|
| v5.1+ | 战斗系数调整（HP 200/敌HP×0.55/敌ATK×0.07/敌DEF×0.012）| 缓解了"免疫挨打"和"突然卡关"，但战力↔实战仍不一致 |
| v6-c3b | hp 词条权重 0.5→0.3 | 治标不治本——加权和公式本质问题在于无法反映"暴击/吸血/攻速"的复利效果 |
| v6-c4 | calcPower / totalPow 改几何平均 `(atk×def×hp/10)^(1/3) × (1+Σ pct)` | 与 pStats() 战斗实际属性两套数据流脱节，战力数字与实战完全不挂钩 |
| v6-c4d | totalPow 改用 pStats 实战属性 `sqrt(atkEff × survEff) × utilMult` | 量级与单件 calcPower 错位（总战力 29 < 单件 45）；STAGE_BASE_REC 同步从 250→30 后又出"2 件装备打通 10 关" |
| v6-c4e | totalPow ×10 + STAGE_BASE_REC 30→100 量级校准 | "战力 4820 打不过推荐 1175 BOSS" 仍存在——多套校准均未根除问题 |
| v6-c4f（最终决策）| **回退到 c3c 的加权和公式** | 承认"战力↔实战一致"是数值精调的硬骨头，原型阶段无法靠手动调参解决 |

### 根本原因（c4 系列试错后归纳）

1. **战力公式只有一组数据流，实战公式有多组复利**：战斗实际由 atk × 暴击期望 × 命中率 × 攻速 × 吸血 × 防御折算等多维复利构成，单一加权和或几何平均都无法精确反映。
2. **关卡推荐战力 (`rec`) 与玩家战力是"两个公式独立估算"**：`rec = 250 × 1.065^i × mod` 是数学模型，玩家战力是装备词条加权和——两者用不同维度，对比意义有限。
3. **战力数字没有"分阶段校准"**：v5 加权和的权重表（atk×2 / hp×0.5 / pen×8 等）是经验拍脑袋值，没有用大规模战斗模拟验证拟合曲线。

### 留给后续数值策划的工作

1. **建批量战斗模拟器**：参数化跑 1000+ 场战斗（不同装备组合 vs 不同关卡），统计通关率，做战力↔通关率回归。
2. **用回归结果反推"权重表"**：让加权和公式逼近"实战预期 DPS × 实战预期生存"的简化估算。
3. **关卡推荐战力 `rec` 公式重新校准**：基于上一步的拟合曲线，让"推荐战力 == 50% 通关率门槛"成立。
4. **保留 MVP 阶段的临时缓解**：左侧热调面板的"敌人属性倍率"和"玩家伤害倍率"滑块作为玩家自校准入口。

> **关键约束**：原型阶段的多次手动精调（c3b/c4/c4b/c4c/c4d/c4e）证明，没有量化数据支持的纯手动调参在战力↔实战一致性上是低效的。立项后必须先建模拟器再调参，不要重蹈原型阶段的覆辙。
