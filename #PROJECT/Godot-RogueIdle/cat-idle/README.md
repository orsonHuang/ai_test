# 雾境远征 · Godot 可玩 Demo

2026-10-05，基于 [GDD v1](../GDD/README.md) 实现的 M1 功能样片。遵循项目 [AGENTS.md](../AGENTS.md)。实际制作与验收版本为 Godot **4.7.2-stable Steam**，保留现有 Forward Plus / D3D12 配置。

## 开始体验

打开本目录的 [project.godot](project.godot)，按 **F5**。主场景为 [ExpeditionDemo.tscn](scenes/expedition/ExpeditionDemo.tscn)。旧 [Battle.tscn](scenes/Battle.tscn) 仍可单独 F6 运行。

1. 选择开局技能流派和一名伙伴，点击「开始远征」。所有流派之后都能免费改战术。
2. 点击相邻前方地图块，再点右侧「前往」。远方地标可提前看套装方向。
3. 每个探索地区有 6 时段：副本 2，其他活动 1；离开后不能回头。
4. 第一地区有招募，队伍最多主角加两名随从。可在「小队整备」交换阵位、调整技能与换装。
5. 战斗自动回合结算，可暂停、1/2/4 倍播放或跳过。战后领取装备，跨区生命延续。
6. 经过三个探索地区，挑战魔王城。每次状态改变自动保存，重开可继续，战中续档默认暂停。

第一次可尝试「铁壁＋牧师」，沿荆棘林地、苔石矿谷收集荆棘套装，并为招募、休整留时段。这是已验证的一条通关路线，不代表唯一解或最终平衡。

## 在编辑器里继续制作

| 文件 | 可调整内容 |
|---|---|
| [ExpeditionDemo.tscn](scenes/expedition/ExpeditionDemo.tscn) | 页面组合、标题、按钮、根节点 Catalog / Playback Interval；默认每事件 0.65 秒 |
| [MapPage.tscn](scenes/expedition/MapPage.tscn) | 左侧小队、地图容器、地区说明、活动按钮；World 下是九个真实地图块实例 |
| [LoadoutPage.tscn](scenes/expedition/LoadoutPage.tscn) | 阵位、技能选项、装备栏、原生 ItemList 背包 |
| [BattlePage.tscn](scenes/expedition/BattlePage.tscn) | 敌我角色卡实例、意图提示、战斗日志和回放按钮 |
| [UnitCard.tscn](scenes/expedition/components/UnitCard.tscn) | 共用角色卡的 Label、ProgressBar、间距、样式 |
| [RegionTile.tscn](scenes/expedition/components/RegionTile.tscn) | 地图块的 Polygon2D、Line2D、标签；几何来源为 Definition 资源 |
| [DecisionModal.tscn](scenes/expedition/components/DecisionModal.tscn) | 招募、事件、奖励与结果窗口的原生布局 |
| [ExpeditionTheme.tres](resources/expedition/ExpeditionTheme.tres) | 共享颜色、字级、按钮和面板 StyleBox |
| [catalog.tres](resources/expedition/catalog.tres) | 53 份配置资源的总入口，包含地图、单位、技能、套装、事件及规则 |

地图编辑：打开 MapPage，选择 World 下的地图块，在 Inspector 展开 Definition。修改 Polygon 顶点、Label Position 或 Tint 会更新编辑器预览。几何以资源为准；脚本会同步 Land、Border 和标签的位置。MapBoard 会按 Reference Size 缩放 World，布局缩放不应直接改 World 的 Transform。

角色生命、按钮文字、活动可用性、战斗意图属于运行时绑定值；要改初始单位数据，应编辑 `resources/expedition/units/`。要改共用组件的布局，打开对应源场景，保留实例关系。界面初版采用矢量地图与原生控件，尚未制作最终角色美术、动画和音效。

## 代码与数据维护

- [FogRun.gd](scripts/expedition/FogRun.gd)：选路、迷雾快照、时段、活动、背包、队伍与结算状态机。
- [FogCombat.gd](scripts/expedition/FogCombat.gd)：确定性规则、技能/状态共用效果函数和战报帧，不依赖播放速度。
- [FogSave.gd](scripts/expedition/FogSave.gd)：临时写入、校验、备份和恢复。存档在 `user://fog_expedition_v1.json`，不写回配置资源。
- [FogDemo.gd](scripts/expedition/ui/FogDemo.gd)：绑定已保存场景节点、处理输入、显示模态窗口和播放战报，不创建整页 UI。
- [GDD 数值表](../GDD/data/README.md) 是本轮参数来源。调整数值时同步文档、CSV 和 `.tres`，避免两套规则漂移。

[import_gdd.py](tools/import_gdd.py) 通过 MCP 导入 CSV；已存在资源时默认拒绝覆盖。确需重新导入玩法数值时显式用 `--overwrite-configs`，保留现有地图顶点、标签位置、颜色和首领名称。先审阅差异；此命令仍会替换其他已在 Inspector 调整的数值。

[build_demo_scenes.py](tools/build_demo_scenes.py) 与 `tools/requests/` 是首次 MCP 制作的历史脚手架，后续修复已直接保存在场景和脚本中。**不要重放它们覆盖现有场景**；当前 `.tscn/.gd/.tres` 才是维护源文件。

## 验证入口

编辑器打开本工程并停止游戏，现有 MCP 服务运行时执行：

```powershell
python tools/mcp_bridge.py --requests tools/check_rules.json --name rules-latest --brief
```

独立检查保存的场景结构、组件引用、资源和入口：

```powershell
godot --headless --path . --script res://tools/verify_demo.gd
```

本次通过 13 项规则测试、111 个断言；场景检查 268 项、211 个节点。另完成真实 MCP 鼠标通关、战中恢复与 1440×810 / 1280×720 画面检查，详见 [验收记录](../docs/verification/godot-demo-v1/README.md)。测试存档使用独立 `user://fog_demo_ui_test.json`，与玩家续档隔离。

这是可继续迭代的功能 Demo。多人定性试玩、完整难度校准、正式美术音频、Steam 接入与发布导出仍待后续阶段。正式导出前还需移除开发用 MCP 控制入口。
