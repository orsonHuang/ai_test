# ai_test 完整工作区备份

用户授权保存并推送整个 ai_test 及子仓库；对没有远端的 Game-Pulse-Prototype 和 game-seeds，用户明确选择将完整 Git 历史打包到 ai_test 一并推送。

## 两个独立仓库的完整历史

| 仓库 | HEAD | 历史包 |
|---|---|---|
| Game-Pulse-Prototype | 91d975a31af9e359b01d60efdc5e447072fb1c5f | repositories/Game-Pulse-Prototype.bundle |
| game-seeds | dd4affd5feae42b872bcfce028c568925537c319 | repositories/game-seeds.bundle |

两仓库打包时工作树干净。包使用 git bundle create --all，git bundle verify 确认完整历史、无前置依赖，包含所有本地引用和 HEAD。原仓库保留原位，不改远端设置。

SHA-256：
- Game-Pulse-Prototype.bundle：438c22f92ebce0719190ec622de9c2f54675576825561aa4d8d069b54987af8a
- game-seeds.bundle：944dc7c2fc216cab285b16143aa75cb5328dc413d98a06cc210bdc14e394541b

在新的空目录恢复：

```powershell
git clone --branch main ./repositories/Game-Pulse-Prototype.bundle ./Game-Pulse-Prototype-restored
git clone --branch main ./repositories/game-seeds.bundle ./game-seeds-restored
```

## 有远端仓库

- ai_test → 现有 GitHub origin/main。
- Nite-Nite → 现有 GitHub origin/main，独立仓库；根目录 Nite-Nite 是同一位置的 junction，不重复保存。
- orson-huang-homepage → 现有 GitHub origin/main，不操作部署用 server 远端。
- DiceMonsterTT → 原 Maker 远端；工作树无改动，远端 main 已核对为 102904c2ce79ff8486cb0cef1d22ce27ed8b8aec，与本地一致，无需产生新构建。

最终推送结果及提交以 remote-verification.json 为准；该文件生成前不能视为全部推送成功。

## 备份边界

保留所有现有受版本控制文件、未忽略的项目开发成果、素材原图/生成提示词/导出物、预览工具、微信构建快照及工作记录。Nite-Nite 的三个长期预览工具目录已从通用 artifacts 忽略规则中单独放行，确保换机器后仍能预览。

不把可重装依赖缓存、运行日志、本机代理配置、WeChat 私人偏好、已有规则排除的玩家数据备份和凭证提交。排除仅影响 Git 跟踪，未删除本机文件。新暂存文本做凭证模式检查，未发现真实密钥；不改写已有 Git 历史。
