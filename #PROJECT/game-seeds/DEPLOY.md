# 部署游戏种子 v0.1

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
