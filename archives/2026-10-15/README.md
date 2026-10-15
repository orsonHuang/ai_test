# 项目空间存档（2026年10月15日）

本次保存项目空间当前可纳入 Git 的文件、项目资料、构建产物和验收记录；沿用各仓库现有忽略规则，忽略文件未强制加入。

## 独立项目版本

| 项目 | 存档提交 | 保存位置 |
| --- | --- | --- |
| 晚安小屋 Nite-Nite | `8d8b407` | 独立仓库 `#PROJECT/Nite-Nite`；目标远程为 `https://github.com/orsonHuang/Nite-Nite.git` |
| 骰子怪兽 DiceMonsterTT | `cf481c9` | 主仓库子模块指针及本目录 `dice-monster.bundle.part*` 完整历史分卷备份 |
| game-seeds | `20c7b78` | 源码直接纳入主仓库，本目录 `game-seeds.bundle` 保存完整历史 |
| 个人主页 | `8724756` | 原有子模块，工作区无待提交变更 |

主仓库的中文存档提交和 `archive/` 标签用于定位此次整体快照。晚安小屋沿用独立仓库管理，不重复复制到主仓库。

## 恢复说明

- 主仓库切换到本次 `archive/` 标签即可恢复已纳入主仓库的内容。
- 晚安小屋进入其独立仓库，切换到相同名称的存档标签。
- 骰子怪兽若远程无法取得提交，先运行本目录 `restore-dice-bundle.ps1` 合并分卷并校验，再执行 `git clone dice-monster.bundle <恢复目录>`；该备份不含本机远程配置及登录凭据。
- game-seeds 可直接使用主仓库中的源码，或执行 `git clone game-seeds.bundle <恢复目录>` 恢复其原始 Git 历史。

此次操作仅做 Git 存档，不代表新增或变更功能已经重新通过业务测试，也不执行游戏构建或发布。
