# 部署游戏种子 v0.2

## 最新阅读体验更新（2026-10-17）

- 发布 `game-ideas-20261017T102116Z`，46 文件、3,573,746 字节。修订蔚蓝 11 篇正文段落与列表；全库阅读页新增游戏大标题、标题区收藏、目录上方双返回和访问位置恢复。
- 备份 `/var/www/game-ideas-20261017T102116Z-previous`；归档与配套 SHA 清单位于 `/root/game-seeds-releases/`。首页指纹仍为 `6589befe71a27cc7485c4012eddda70802c97658f58873903259e32931b3f1d9`。
- 本地核心、旧工作台、42 文档、11 页样稿、三屏导航专项均通过；公网 46 文件 SHA 一致。导航专项包括连续系统阅读、刷新、原生前进后退、来源阅读位置、目录滚动、筛选列表、直达回退及主页入口。
- `tests/reader-navigation.cjs` 支持 BASE_URL。位置记录仅存当前标签的 sessionStorage，不进入公开包或收藏备份。

## 历史样稿更新（2026-10-16）

- 发布 `game-ideas-20261016T142557Z`，46文件、3,562,144字节。新增永远的蔚蓝星球整游分析与10篇系统正文、地图、UI线框及10张原创关系封面；其余游戏正文保持。
- 使用 `deploy-update-release.sh` 校验暂存文件后切换，仅替换 game-ideas 目录；上一版本保留在 `/var/www/game-ideas-20261016T142557Z-previous`。归档和同名 sha256 清单位于 `/root/game-seeds-releases/`。
- 首页 SHA256 保持 `6589befe71a27cc7485c4012eddda70802c97658f58873903259e32931b3f1d9`，未修改 Nginx。公开包不含来源研究截图和金山文档内容。
- 更新内容时保留游戏目录下 reader.json、reader/、reader-assets/。build-catalog 会在旧图清单后追加明确标记原创/已授权的阅读封面；build:library 采用公开文章并保留参考附录。
- 样稿验收：`node tests/reader-sample.cjs`，`BASE_URL` 支持线上地址；检查十次真实地图跳转、每页图解、附录流程图、收藏持久化与320/390像素无横向溢出。

## 首次线上交付（2026-10-16）

- 线上入口：<https://orson.games/game-ideas/>，默认系统案例库；旧创意工作台通过导航继续使用。
- 发布号：`game-ideas-20261016T090325Z`。36文件/3,449,640字节：27原创SVG、42文档入口、27系统与离线Mermaid渲染。
- 发布目录：`/var/www/orson-huang-homepage/game-ideas/`。发布前目录不存在，暂存包逐文件SHA256通过后移动到目标目录；Nginx和原主页未改。
- 服务器发布归档：`/root/game-seeds-releases/game-ideas-20261016T090325Z.tar.gz`；本地可移交ZIP为`game-seeds-v0.2-static.zip`。只发布dist内容，不含资料库研究截图、服务器凭证、测试用户数据和Sites身份。
- 证据：`validation/online-integrity.json`记录公网36文件全部SHA256匹配、无末尾斜线跳转、主页和awakening均200；`validation/library-acceptance.json`记录真实HTTPS下42文档及全部流程图/筛选/收藏/备份/1440、390、320宽度通过。原创意工作台流程验收见`validation/acceptance.json`。
- 根首页SHA256保持`a080846e6a41b55316d90a2032b42ce8d13326f35ec2a8df736edf624acd22f8`；Nginx站点配置保持`937c04753eab247b52fa455506affe4b1b51175b331ed5b7ed46bc52a350d75e`。

## 后续更新内容

1. 用拆解Skill维护`#Game-TearDown`原文、game.json、来源与媒体台账并验证，重建catalog/public-media。
2. 本项目执行`npm ci`（仅首次或依赖改变），再执行`npm run build:library`。内容构建只复制公开图片允许清单，原始HTML转义，引用截图仅显示来源提示。
3. 启动本机HTTP服务后运行`node tests/engine.cjs`、`node tests/browser.cjs`、`node tests/library.cjs`；通过后`python scripts/package-release.py`生成发布归档与校验清单。
4. 后续替换发布需先备份现有game-ideas目录，再暂存、验哈希和切换。`deploy-first-release.sh`只用于本次首次部署，目标已存在时会主动停止，不能直接用于覆盖更新。
5. `python scripts/verify-release.py`验证公网文件与归档manifest一致；`BASE_URL=https://orson.games/game-ideas/`可运行资料库浏览器验收。

服务器不需要安装Node或数据库。若需回退本次首次发布，可经确认将整个game-ideas目录移到同站点根目录外的备份位置；不能替换或清空整个站点根目录。后续发布保留上一版目录供回滚。

## 系统收藏说明

系统收藏使用独立的`game-seeds-library-v1`存储键，按稳定systemId关联笔记；列表提供“导出系统收藏/导入系统收藏”。导入合并，相同ID保留当前笔记。原创意备份使用`game-seeds-v1`，两个入口分别导入导出，互不覆盖。清除网站数据会删除本机收藏，资料库公开内容仍可访问。

以下为v0.1历史说明，当前发布请使用完整v0.2 ZIP或dist全部文件，不再使用旧五文件包。

## 本地使用

直接打开 `dist/index.html`，或使用静态 HTTP 服务：

```powershell
python -m http.server 8789 --bind 127.0.0.1 --directory dist
```

访问 `http://127.0.0.1:8789/`。HTTP/HTTPS 环境的存储与复制行为更稳定。

## 发布到 orson.games

本项目不需要 Node 服务、数据库、API 密钥或打包安装。`game-seeds-v0.1-static.zip` 只包含网页运行文件，不包含个人资料、测试资料或 Sites 私有部署身份。

根据现有主页 README，Nginx 静态根目录为 `/var/www/orson-huang-homepage/`。部署时先核实当前配置；将 ZIP 中的五个文件解压至一个新目录：

```text
/var/www/orson-huang-homepage/game-ideas/
  index.html
  styles.css
  engine.js
  app.js
  favicon.svg
```

随后访问 `https://orson.games/game-ideas/`。目录末尾保留 `/`，以便浏览器正确解析相对资源。常规 Nginx 静态目录无需额外后端或重启；若站点有统一路由重写，应单独为 `/game-ideas/` 保留静态目录匹配。

在现有主页添加入口：

```html
<a href="/game-ideas/">游戏创意工作台</a>
```

若希望嵌在某个页面：

```html
<iframe src="/game-ideas/" title="游戏种子：游戏创意工作台"
  style="width:100%;height:960px;border:0;border-radius:12px"></iframe>
```

独立页面在手机上更适合使用。发布后依次检查：入口、样式、资料保存、刷新、JSON 备份恢复和下载。

## 数据与迁移

- 数据只在当前浏览器的 localStorage（键 `game-seeds-v1`）中保存，不发送给站点服务器或任何 AI 服务。
- 不同域名、端口和浏览器各有一份工作空间。请先导出 JSON，再在目标站点导入。
- 恢复采用合并：相同编号保留当前记录；未修改过的内置示例可由备份恢复收藏与笔记。新编号记录追加。
- 多标签页检测到其他页面更新时会阻止继续覆盖；先备份当前工作，再刷新合并。
- 清除浏览器网站数据会删除工作空间，请定期备份。

## 后续联网接入

`engine.js` 的 `generateIdeas(sources, brief)` 是独立分析接口，返回 `ideas`、`signals`、`message`。未来可以通过后端适配器替换它，保持创意卡数据结构与来源引用。

联网采集应提供原始内容、来源 URL、采集时间与资料类型；在线模型需由后端调用，保留事实、推断和假设的标记，不把 API 密钥放进静态文件。

## 验证

```text
node tests/engine.cjs
node tests/browser.cjs
```

浏览器测试默认使用本机 Edge；可用 `PLAYWRIGHT_MODULE` 指定已安装的 Playwright 模块路径。先启动本地 8789 静态服务。截图和验收结果在 `validation/`，不随站点发布。
