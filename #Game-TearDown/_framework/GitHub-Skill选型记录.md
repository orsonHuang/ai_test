# GitHub Skill 选型记录 · 2026-10-16

目标：支持“指定游戏→有来源的模块专业设计文档→三岗位图文阅读→跨游戏系统检索”。本次读取候选实际 SKILL.md、代表性模板／引用和仓库元数据；没有执行候选代码或整包安装。

## 结论

以本地 `game-system-teardown` 为主流程，使用已提供的官方 skill-creator 完成编写与验证；借鉴社区 Skill 的文档覆盖和对比方法。所检查候选中，没有一套已经证明能独立完成版本隔离、图文采证、系统规格、岗位阅读和网页字段交接。社区仓库的“professional/production-ready”是自述，不是质量证明。

| 候选与固定版本 | 能提供什么 | 限制与采用方式 |
|---|---|---|
| [OpenAI skills](https://github.com/openai/skills)，本机已提供 skill-creator | 官方来源，Skill 格式、渐进式引用和校验流程 | 本次官方 curated 列表未发现专门的游戏拆解 Skill；沿用已安装系统能力，不重复安装 |
| [lpf513/gameSkills · game-system-design](https://github.com/lpf513/gameSkills/blob/075f2415c66848fca020c58872d4c1c7859ad597/game-system-design/SKILL.md) | 数据、算法、接口、边界与验证的规格思路，领域最接近 | 本次未发现许可证文件；且强制先选模式、全部参数定界、固定一小时验证。只作选型参考，不复制安装，不把未知原作参数强填出来 |
| [tundraray/overture · feature-spec-template](https://github.com/tundraray/overture/blob/89553a2dc1cfe1950f0878be79036f732e6b89ea/gamedev/skills/documentation-criteria/references/feature-spec-template.md) | 输入输出、状态、调参、异常、交互、测试覆盖较完整 | MIT；模板绑定多代理审批与市场岗位，不适合照搬。本地独立编写规格标准，参考其覆盖思路，不引入审批和代理依赖 |
| [oleg-riazantsev/skills-saschb · game-design](https://github.com/oleg-riazantsev/skills-saschb/blob/ffc90eed41283f264d51acc3e33e8d3f0f5cc793/skills/productivity/game-design/SKILL.md) | 系统拆解、跨游戏变体比较、设计代价和失效条件 | MIT；已核对 references 真实存在。观点较强，如偏好横向成长，需按品类判断；用作分析问题参考，不用它决定游戏事实 |
| [morbeo/ai-skills · game-design](https://github.com/morbeo/ai-skills/blob/548d3d22eb58eb3ec1f4ab526f317e48b753298a/game-design/SKILL.md) | 玩家动机、UX、叙事、目标与反馈 | CC0-1.0；偏体验方法，缺模块规则／接口／证据流程。可作为交互评审参考，不承担生产主流程 |

## 信任与适配核查

GitHub API 当日显示：gameSkills 1 star、morbeo 0、overture 2、skills-saschb 0；均未归档。这个规模不足以证明广泛生产验证，也不等于内容无用。最近 push 分别为 2026-07-30、04-13、07-26、06-21；更新日期只证明仓库活动，不证明机制知识新旧。

官方 OpenAI 仓库来源可确认，但官方 curated 列表的工具型 Skill 与本任务领域不同，不因为官方就强行安装无关技能。候选元数据与许可证在对应仓库核查；未知许可不推断可复制。

本次审读的三个游戏设计 SKILL.md 为文字方法，未发现直接要求传送凭据或运行下载脚本的步骤；这不构成对整个仓库的安全审计。overture 的完整插件包含更多工作流，未安装、未执行，也不采用其多代理签核要求。

## 已吸收的设计原则

1. 模块文档要连通规则、状态、输入输出、UI 与验收，形成可追踪关系。
2. 对比表要解释不同实现如何解决同一个问题，不能只列共同点。
3. 设计评价同时写收益、成本、适用与不适用条件。
4. 玩家目标和反馈要落实到界面状态与可验证行为。

以上采用通用思路并独立组织文本；未复制第三方模板源码。针对本任务增加：事实／推断／参考设计／未知分层、平台与版本隔离、图片来源与公开状态、模块 ID 与网页索引。相关标准见 [模块专业设计文档标准](模块专业设计文档标准.md)。

## 能力验证方法

不能用 star 或 YAML 校验替代效果测试。以三款指定游戏实际生产，检查：是否错把 DLC 当本体、App 当小游戏；是否编造隐含参数；是否能给出模块级流程、数据与异常；图文是否支撑正文；开发、美术是否能明确还缺哪些决策。最终验收记录在框架进度中更新。
