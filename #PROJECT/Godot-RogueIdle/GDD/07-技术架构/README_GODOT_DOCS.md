# Godot 技术架构文档

此目录包含为Godot Rogue Idle游戏开发准备的技术架构设计文档。

## 文档列表

### 场景与架构
1. **godot_scene_structure.md** - Godot场景结构设计
   - 主要场景的节点层次结构
   - 包括主场景、玩家、敌人、关卡和UI相关场景

2. **godot_visual_hierarchy.md** - 可视化场景层次结构
   - 完整的项目架构视图
   - 场景加载/卸载顺序和节点组管理

### 信号与接口
3. **godot_signal_connections.md** - 系统信号连接关系
   - 战斗系统、地图系统、游戏管理系统等之间的信号连接
   - 各系统的信号接口规范

4. **godot_interface_specifications.md** - 接口规范文档
   - 各节点的方法接口和信号参数详细定义
   - 包含数据结构定义，便于实际开发使用

### MCP 集成
5. **godot_mcp_setup_and_test.md** - Godot MCP服务配置与测试
   - MCP服务配置指南
   - 连接测试步骤
   - 核心战斗demo开发准备清单
   
6. **mcp_connection_test_report.md** - Godot MCP服务连接测试报告
   - 详细的测试过程和结果
   - 验证文件说明
   - 测试结论和建议

## 用途

这些文档为Godot Rogue Idle游戏的开发提供了清晰的架构指导和接口规范，可以直接用于实际的编码工作中。

## 相关文档

- `01-技术架构.md` - 项目整体技术架构设计