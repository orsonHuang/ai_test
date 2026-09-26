# Cocos MCP 选型 · 2026-09-26

## 结论

推荐优先验证 [FunplayAI/funplay-cocos-mcp](https://github.com/FunplayAI/funplay-cocos-mcp)，候选固定版 [v0.6.4](https://github.com/FunplayAI/funplay-cocos-mcp/releases/tag/v0.6.4)。适配本项目Creator 3.8.8仍需实机连接测试；当前只完成README、发布记录与关键源码静态初筛，未安装、未运行测试、未修改MCP配置。不是完整安全审计。

## 比较

| 项目 | 免费与适配依据 | 主要价值 | 当前判断 |
|---|---|---|---|
| [Funplay](https://github.com/FunplayAI/funplay-cocos-mcp) | 仓库声明MIT；文档包含Creator 3.8.x操作；当前Release标记v0.6.4 | 场景／编辑器脚本、截图、预制体与资源检查、工具配置；文档列出Codex客户端配置支持 | 首选验证；功能覆盖本项目UI搭建与读回检查 |
| [harady/cocos-creator-mcp](https://github.com/harady/cocos-creator-mcp) | MIT；package.json为2.0.2、editor >=3.8.0 | 场景、组件、预制体、资源；包含3.8.x兼容测试说明 | 备选；源码跨域与鉴权边界需先处理 |
| [caravanglory/cocos-mcp-server](https://github.com/caravanglory/cocos-mcp-server) | README声明MIT、支持3.8.x | 中文面板、节点／组件／预制体工具、按类管理工具 | 备选；安全防护与发布验证证据不足以优先选择 |
| [RomaRogov/cocos-code-mode](https://github.com/RomaRogov/cocos-code-mode) | Apache-2.0 | UTCP工具发现与CodeMode MCP桥接 | 本项目暂不优先，增加桥接与集成环节 |

免费指开源MCP软件的许可与使用，不代表AI模型调用免费；不推断商店渠道定价，也不把Stars数量当安全证明。

## 静态安全检查

- Funplay v0.6.4 [config.js](https://github.com/FunplayAI/funplay-cocos-mcp/blob/v0.6.4/lib/config.js)：默认host为127.0.0.1、脚本检查开启、自动启动开启，可设置工具范围。
- Funplay v0.6.4 [server.js](https://github.com/FunplayAI/funplay-cocos-mcp/blob/v0.6.4/lib/server.js)：RPC检查Origin并限制请求体；允许无Origin请求，未发现此文件实现强身份鉴权。Origin检查与可选会话ID都不等于身份认证；调试GET接口也不能视作私密认证接口。
- Funplay [javascript-safety.js](https://github.com/FunplayAI/funplay-cocos-mcp/blob/main/lib/javascript-safety.js)：main源码含删除、shell与路径的模式检查；README明确可按调用关闭检查，且不构成完整沙箱。不能据此声称任意JS被可靠隔离；固定包需复核同文件。
- Funplay [发布记录](https://github.com/FunplayAI/funplay-cocos-mcp/releases/tag/v0.6.4)：提供ZIP、manifest与SHA256SUMS。校验和帮助检查下载完整性，不证明发布者或代码一定安全。
- harady [mcp-server.ts](https://github.com/harady/cocos-creator-mcp/blob/main/source/mcp-server.ts)：仅监听127.0.0.1，但CORS为*；注释和实现明确使用始终放行的占位OAuth。不能将OAuth端点当作实际保护。
- caravanglory [mcp-server.ts](https://github.com/caravanglory/cocos-mcp-server/blob/main/source/mcp-server.ts)：仅监听127.0.0.1，CORS为*；已阅请求处理代码未见强鉴权。来源限制弱于本次检查的Funplay，不据此认定恶意。

本轮未做完整依赖漏洞扫描、二进制与源码一致性校验、全库外联审计或攻击验证，不保证零风险。插件目录搜索未找到现成Cocos连接项；GitHub编辑器扩展仍可作为后续自定义MCP接入候选。

## 建议接入方式（未执行）

1. 固定v0.6.4发布包，核对校验和与关键代码，记录版本。安装到现有Cocos工程的项目级extensions目录，暂不全局安装、不同时安装多个候选。
2. 保持127.0.0.1、不做公网或局域网转发；保持脚本检查开启。按需开放工具，注意默认core也包含可写脚本能力，并非只读配置。
3. 先确认服务返回的是Goodnight-House项目与Creator 3.8.8，再进行写操作；端口以面板实际显示为准，不照抄示例8765。
4. 在独立测试场景验收：读层级 → 建Canvas与Label → 改属性 → 保存／重开读回 → 建预制体及实例 → 重开检查引用 → 预览截图 → 读取报错。没有报错不等于画面验收通过。
5. 保留工程Git快照。运行时代码、规则和生成器仍由正常代码工作流开发；MCP主要承担编辑器场景／组件／预制体操作、诊断及视觉检查。

选择状态：推荐未安装。通过上述验收后再将候选标记为项目正式工具。
