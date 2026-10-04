# v1 初始数值表

规则版本：gdd-v1.0-draft。全部属于设计调参起点，未替换HTML数据。2026-10-05 已通过 MCP 导入 cat-idle 的 53 份可编辑资源；运行时兼容版本为 `gdd-v1-demo-1`，见 [工程维护说明](../../cat-idle/README.md) 和 [引擎验收](../../docs/verification/godot-demo-v1/README.md)。通过规则测试不代表最终平衡。

| 表 | 范围 |
|---|---|
| [rules.csv](rules.csv) | 全局参数、预算、成长、恢复、品质、状态与被动 |
| [regions.csv](regions.csv) | 九块地图、对称邻接、前进边、公开地标、区域倍率 |
| [activities.csv](activities.csv) | 固定/随机活动、费用、次数、抽选权重 |
| [units.csv](units.csv) | 十二种单位的基础属性和成长 |
| [equipment.csv](equipment.csv) | 三装备部位的基础与每档成长 |
| [affixes.csv](affixes.csv) | 三个固定值词条、适用槽和权重 |
| [sets.csv](sets.csv) | 三套装各两级效果 |
| [skills.csv](skills.csv) | 六个主动技能；主角被动在rules表 |
| [events.csv](events.csv) | M1六事件、M2六事件的分支结果 |

统一UTF-8，逗号分列，管道符分隔ID列表。百分比字段30表示30%，系数1.15表示乘1.15，严禁混用。次数−1表示在预算允许下可重复，0不表示无限活动；套装trigger_limit_per_round=0表示没有额外次数上限，仍受来源过滤和状态层数限制。

sets表将触发次数上限trigger_limit_per_round与治疗总量上限heal_cap_per_round分列。余烬三件每轮治疗上限8，不能解释为触发八次；0表示该字段不施加额外限制。

units表的armor_every_levels=2意为从1级起每升2级加1护甲，值0表示不成长；敌人不用小队等级。装备档次取探索区stage（1–3），最终战不掉装备。地图坐标/顶点和视觉资源由Godot资源编辑，本表不包含几何形状。

示例计算、叠加边界见 [战斗数值验证](../01-战斗系统/03-战斗数值验证表.md)。修改这些表必须同步有具体数值的说明与示例；规则ID变更还需同步存档版本和验证器。

可执行静态检查：[validate_gdd.py](../../docs/tools/validate_gdd.py)。它检查表结构、ID、引用、路径、事件分支和基础预算，不是游戏模拟器，不会证明难度或商业可行性。
