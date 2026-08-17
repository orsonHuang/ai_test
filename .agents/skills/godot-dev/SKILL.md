---
name: godot-dev
description: Godot 独立游戏开发规范。编写/审查 GDScript、调试、场景与导出配置、打包构建时使用。
whenToUse: 涉及 Godot 项目代码、场景、测试、导出与构建的任务
metadata:
  engine: godot
  version: "4.x"
---

# Godot 开发规范

本 Skill 定义本项目（独立游戏，Godot 引擎）的代码与工程约定。涉及 Godot 相关任务时必须遵守。

## 版本与 API 约定

- 项目使用 **Godot 4.x**，API 一律以 4.x 为准，禁止使用 3.x 语法（如 `is_action_pressed` 签名、`get_node` 写法、旧 Tween API）。
- 不确定 API 时先查官方文档（docs.godotengine.org 的 4.x 分支），不要凭记忆写。
- `@tool` 脚本与编辑器脚本仅在必要时使用。

## GDScript 风格

- 遵循官方 GDScript 风格指南：4 空格缩进、`snake_case` 变量与函数、`PascalCase` 类名与节点名、常量 `UPPER_SNAKE_CASE`。
- 显式类型标注：`var health: int`、`func take_damage(amount: int) -> void`。
- 优先 `@export` 暴露可调参数，避免硬编码魔法数字；必要时加 `@export_group`。
- 信号命名用过去式（如 `health_changed`）；内部状态用 `_` 前缀私有成员。
- 场景树访问：优先节点路径或 `%UniqueName`，避免频繁 `get_node`。

## 工程结构约定

- 场景文件 `.tscn`、脚本 `.gd`、资源 `.tres` 按功能分目录（如 `scenes/`、`scripts/`、`resources/`、`assets/`）。
- 美术/音频等大文件放在 `assets/` 下，脚本不直接引用绝对路径。
- 依赖注入优先于全局单例（autoload 尽量少用，仅保留游戏管理器类）。

## 测试与构建

- 无头测试运行：
  ```
  godot --headless --script res://tests/run_tests.gd
  ```
- 导出前检查 `export_presets.cfg` 的平台预设与导出路径。
- 构建流程、批处理脚本统一放在 `tools/` 目录，避免散落。

## 调试注意

- 沙箱/无头环境不可用 `os.clock()`、`io.*` 等受限标准库；计时用 `_process(delta)` 或 `Time.get_ticks_msec()`。
- 预览"卡住"且无报错时，优先检查是否命中受限 API，其次查运行日志。
