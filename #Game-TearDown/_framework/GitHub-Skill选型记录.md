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

## 阅读排版补充 · 2026-10-17

按用户要求再次检索 GitHub 并读取候选原文：

- [rhino-labs/skills · typography](https://github.com/rhino-labs/skills/blob/main/typography/SKILL.md)：正文优先，控制行宽、段落留白、标题层次，使用语义化列表。这些方法适合当前长文页面，融入本地独立编写的 reader-writing.md；英文行高、字符数与字体偏好没有直接照搬到中文。
- [skealeye/ClaudeSkills · gdd](https://github.com/skealeye/ClaudeSkills/blob/master/skills/gdd/SKILL.md)：阅读其入口、研究及文档目录组织部分，可参考整游索引连接独立章节。完整工作流还包含新建仓库、自动推送、Obsidian 和多代理写作，不适合本次现有资料库的排版修订，未采用整套流程。

此轮按 main/master 当日内容查阅，未固定新候选 commit，也未整包安装或执行仓库代码。采用的是一般排版与文档组织方法，用户指定的“顺序用数字、并列用中点”和作者文风优先。实际效果以蔚蓝星球 11 篇正文、桌面/手机页面及导航测试验收。

## 游戏分析专项筛选 · 2026-10-17

用户要求进一步找专业游戏分析 Skill，区分单机与商业化游戏，并覆盖海内外。以下为原文审读与适配判断，未安装新候选、未执行候选代码、未以真实案例验证其质量。

| 候选 | 核查版本 / 许可 | 适用价值 | 限制与建议 |
|---|---|---|---|
| [GameDesignOS / game-experience-analyzer](https://github.com/DY-2026/GameDesignOS/tree/ada4bf9e60c2c90a4c84866e4bfd191e3767d164/game-experience-analyzer) | ada4bf9；MIT | 首选。入口区分整游、机制、单机、商业化、长线运营；单机参考检查主路径、节奏、自主选择与挑战反馈；证据支持截图/录屏定位 | 公开入口为1.3.0 candidate。功能范围很宽，模板字段较多；应吸收方法到现有作者文章，不把诊断字段堆到读者面前。固定机会窗口、置信度阈值不作为通用实证规律 |
| [Steam Market Research](https://github.com/Abaudat/steam-market-research-skill/blob/c1c877ec562d59bfbbf86e4c6e192129d44d375b/SKILL.md) | c1c877e；MIT | Steam同类样本、标签、商店描述、定价与市场定位，包含表现不佳样本 | 聚焦Steam商业可行性，不承担系统拆解。默认美国/英语数据；评论量乘系数估算收入、当前价代历史成交价、固定净收入比例与“品类美术决定90%”都不宜直接采用 |
| [Unreleased Game Research](https://github.com/RayMEI-XiaoGaoShou/Unreleased_Game_Research_SKILL/blob/ead3c0ad614a38cad6ce10d730f22e93e8c461bc/unreleased-game-research/SKILL.md) | ead3c0a；API未识别许可，未认定可复制 | 未上线游戏的官方情报、B站/YouTube评论、TapTap评价、创作者评测分层，可参考跨平台声音对照 | 偏宣发与测试反馈，不能替代实机拆解；需要处理评论样本偏差。原文多轮索要Cookie/API凭证并绑定转录服务，不直接采用其采集流程 |
| [game-economy / game-monetization](https://github.com/tinh2/skills-hub-registry/tree/d38affbf56da216841e2b9e4032a4b978c2062fd/analysis) | d38affb；API未识别仓库许可 | 资源产消、付费内容、广告、通行证检查项 | 主要读取源码和配置做审计，和外部竞品拆解不同。固定70–90%产消比、抽取次数阈值等不能套所有品类；地区规定须另查现行官方依据。只作问题清单参考 |

核查范围：GameDesignOS入口、单机参考、分析模式和品类路由；Steam入口；Unreleased入口与采集/输出关键段；registry经济与商业化入口。GitHub API当日四仓库均未归档，分别425/0/1/20星；星数仅是活动线索，不代表专业认证或拆解效果。

### 建议给现有 Skill 增加的分析分支

此处为选型建议，不表示本轮已经修改已安装 Skill 或重写全部案例。

- 共用底座：产品/平台/版本、玩家动作与决策、核心循环、系统地图、数值关系、图文依据和迁移条件。
- 单机/完整体验：学习—挑战—探索—峰值的流程变化、关卡与叙事、失败成本、通关/重玩动机、本体与DLC边界。
- 长线商业化：首日/日周/赛季目标、资源产消、成长卡点、付费改变的能力或效率、免费与付费路径、活动/社交/回流与时间负担。
- 地区层独立叠加：按发行市场与区服分类，开发商国籍另记。中国大陆、港澳台、日本、韩国、北美、欧洲等按资料细分；平台再分App、小游戏、PC与主机。
- 同款跨区服对照：版本日期、内容进度、礼包价格/币种、广告、角色获取、活动时间与语言分别核对。不能混用国服规则、海外价格和不同时间窗口的市场数据。
- 数据口径：每项注明国家/地区、商店/渠道、时间区间、币种、官方/平台计数/第三方估算。评论数、下载、流水、收入和活跃不同口径不能直接拼接；仅凭英语评论也不能推断用户国籍。

推荐组合：现有 game-system-teardown 负责资料库与网页契约，吸收 GameDesignOS 的分析方法；Steam 研究作为市场专项，商业化问题清单和海内外对照作为按需分支。先在蔚蓝App与暖雪Steam样稿验证，不为了海内外覆盖编造同款海外版本。

## 美术、流程图与原型专项 · 2026-10-17

本轮为候选审读与适配建议，未安装外部 Skill、运行其代码、修改已安装 Skill 或发布网页。以下按当日 main 分支阅读，尚未固定提交；不能将文字审读视作产出效果验证。

| 方向与来源 | 建议吸收 | 适配边界 |
|---|---|---|
| [create-game-assets](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/disciplines/create-game-assets/SKILL.md) 及其 [art-direction](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/disciplines/create-game-assets/references/art-direction.md) | 用形状、轮廓、明暗、颜色职责、材质、镜头、动效和原生尺寸可读性描述美术；放回实际战斗背景判断 | 原 Skill 主要生产新资产。我们将这些维度转为截图分析问题；生成图不得作为原作证据。仅有静态宣传图时，不断言战斗特效与运动可读性 |
| [diagramming](https://github.com/arjunprabhulal/agent-skills/blob/main/skills/docs/diagramming/SKILL.md) | 按问题选流程、状态、时序等图型；一图一问题，同层级节点、箭头说明、异常分支、渲染检查、文字摘要 | 适合现有 Mermaid。约九节点仅作拆图提示，不设硬性上限；不照搬后台架构术语、所有图必须异常分支或禁止主题颜色等绝对要求 |
| [cc-designer](https://github.com/Openclaw-Metis/cc-designer/blob/main/SKILL.md) 及 [prototypes](https://github.com/Openclaw-Metis/cc-designer/blob/main/references/prototypes.md) | 可在浏览器打开的 HTML 原型，区分静态布局与真实关键交互，明确模拟范围，浏览器检查 | 不默认套营销页、操作系统外壳、React/Babel CDN 和多版本交付。沿用本站样式与本地依赖；原型只实现需要验证的流程。wireframes.md 本次未成功读取，不声称完整审读 |
| [game-ui-ux](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/disciplines/game-ui-ux/SKILL.md) | 屏幕/弹窗层级、返回路径、安全区、文字缩放、手柄焦点与输入设备切换，按地区检查文案长度 | 原文偏引擎实现，当前吸收可观察的交互检查项。不能由界面表现反推原作使用事件总线或特定代码架构；触屏游戏不强制补出原作手柄支持 |
| [wireframe-annotated](https://github.com/nexu-io/open-design/blob/main/plugins/_official/examples/wireframe-annotated/SKILL.md) | 线框区域编号与说明一一对应，说明放界面外侧，灰度结构保持清晰 | 原模板限定桌面营销页，借鉴标注方法，不能直接套进游戏界面 |

上述 diagramming 和 cc-designer 入口声明 MIT；本轮没有逐仓库核完其余许可，不复制第三方模板源码。只独立组织一般方法；如后续要安装或复用代码，再固定版本并核许可证与执行脚本。

### 建议纳入生产端的图文契约

1. 美术表现：先给原作截图及定位，再用编号说明观察到的视觉选择、服务的玩家判断及代价。减少“精美、丰富、沉浸”等无依据评价；截图来源、版本与时间随图记录。
2. 系统图：总览图用于模块跳转；流程图解释操作与判断；状态图解释条件和切换；合作等多角色交互可用泳道或时序。按需选图，不给每个系统机械补齐所有图型。手机窄屏应可读、可放大，不能只验证语法通过。
3. UI 说明：原作截图、依据截图重绘的线框、补充设计三种身份明确标注。控件编号与“功能／触发条件／反馈／跳转”对应，保持正文、图和原型用词一致。
4. 交互原型：先做关键路径和必要的锁定、资源不足、取消、返回等状态；每个按钮要有可解释反馈。证据不足的行为放在补充设计中，不伪装成原作流程。
5. 游戏差异：单机重点看战斗辨识、探索引导、叙事镜头、暂停和背包；长线商业化按实际内容看成长反馈、奖励层级、活动入口、商店和付费路径。海内外先按实际版本、语言和输入设备检查，不把地区刻板印象写成设计规律。

建议继续由 game-system-teardown 统一调用，新增美术分析、图表、UI原型三个按需参考模块，避免多个大 Skill 同时争夺文风和输出格式。首个验证对象可用蔚蓝合作系统：原作界面编号讲解、准备/开战状态图、可点击的补充设计原型；效果通过再推广。


## 实际吸收与应用 · 2026-10-17

用户授权后，方法已融入现有Skill并安装：analysis-modes（GameDesignOS模式与证据、Steam渠道口径、跨市场边界）、visual-evidence（美术观察与证据）、diagrams（问题与图型、放大阅读）、ui-prototypes（编号、状态与HTML验收）。此前reader-writing继续承担GDD作者文风和排版要求。外部采集项目仅吸收来源分层；不采用凭据索取、固定经济阈值、评论推收入或海外规则混用。没有复制第三方模板代码。

蔚蓝合作和阴阳师御魂作为两个前端样稿验证；阴阳师十系统应用完整作者正文与开发参考分层。效果评估以实际浏览器测试和人工截图核读为准，用户内容验收仍待反馈。
