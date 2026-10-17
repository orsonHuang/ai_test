# UI 说明与可点击原型

原型用于检验一个具体设计问题。先明确哪些行为有原作证据、哪些是补充设计，再确定关键路径与必要异常；不制作不能说明问题的大量静态屏。

## 交付内容

1. 用低保真线框解释信息层级，区域编号逐一对应功能、条件、输入、反馈和跳转。
2. 需要验证操作时实现 HTML/CSS/JS 原型；沿用现有站点技术与设计，不强制 React、CDN、Figma 或营销页模板。
3. 展示当前状态与操作结果；禁用有原因，返回有去处，取消不暗中提交。支持重置演示，模拟资源和随机结果明确标注。
4. 参考设计在图和原型旁就能识别。演示运行通过只证明有限前端流程，不声称服务器、真实支付、网络同步或原游戏实现已验证。

## 游戏与地区适配

- 触屏检查点击区域、安全区、竖横屏与弹窗遮挡；PC/主机按对象检查键鼠/手柄焦点与返回。分析输入方式不能由地区推断。
- 按实际目标语言检查文案长度、单位和布局；没有跨区来源就不宣称还原海外界面。
- 装备/背包关注过滤、对比、保护、批量操作预览；合作关注角色权限、准备撤销与共同目标；购买关注价格/消耗/结果及取消。

## 验收

浏览器实际点击主路径和关键错误路径；检查桌面、390、320像素，键盘焦点、重置和离开返回。UI 编号、状态图、正文规则、原型结果相互吻合。测试结果记录哪些分支执行过，未实现部分不以“可开发”掩盖。

方法参考：[cc-designer / prototypes](https://github.com/Openclaw-Metis/cc-designer/blob/main/references/prototypes.md)、[game-ui-ux](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/disciplines/game-ui-ux/SKILL.md)、[wireframe-annotated](https://github.com/nexu-io/open-design/blob/main/plugins/_official/examples/wireframe-annotated/SKILL.md)。独立组织通用方法，没有复制组件或默认外壳。
