# HTML 原型编写规范 v1.0

---

## 0. 总则

单文件 HTML（CSS + JS 全部内嵌），零外部依赖，浏览器直接打开即可运行。

**目标**：让非技术人员也能打开、试玩、调参。

---

## 1. 架构约束

### 1.1 逻辑与渲染分离

- 所有游戏逻辑（状态、规则、计算）不得直接操作 DOM
- 渲染层只读取状态，不修改状态
- 逻辑 → `EventBus.emit('event', data)` → 渲染层监听并更新画面
- **禁止**：逻辑函数里出现 `document.getElementById` / `innerHTML` / `querySelector` 等 DOM 操作

```javascript
// ✅ 正确：逻辑层只操作数据
function attackUnit(attacker, defender) {
  const damage = calcDamage(attacker.atk, defender.def);
  defender.hp -= damage;
  EventBus.emit('hp_changed', { unit: defender, hp: defender.hp });
}

// ❌ 错误：逻辑层直接操作 DOM
function attackUnit(attacker, defender) {
  const damage = calcDamage(attacker.atk, defender.def);
  defender.hp -= damage;
  document.getElementById('hp-bar').style.width = defender.hp + '%'; // 禁止
}
```

### 1.2 配置集中

- 所有可调数值集中在文件顶部的 `CONFIG` 对象中
- 代码中**禁止魔法数字**（裸的 `100`、`0.5` 等）

```javascript
const CONFIG = {
  // 战场
  GRID_SIZE: 8,
  CELL_PX: 64,
  
  // 数值
  INITIAL_HP: 100,
  DAMAGE_BASE: 20,
  CRIT_MULTIPLIER: 1.5,
  
  // 节奏
  TURN_TIME_LIMIT: 30,
  MAX_TURNS: 20,
};
```

代码中引用：`CONFIG.DAMAGE_BASE`，绝不写 `20`。

### 1.3 单文件结构顺序

```
  1. CONFIG 对象
  2. 状态对象（const state = {...}）
  3. EventBus 实现（使用下方标准实现，禁止 AI 自行定义接口）
  4. 逻辑层函数（纯数据操作）
  5. 渲染层函数（只读 state + 操作 DOM）
  6. 调试面板函数
  7. 初始化入口
```

**标准 EventBus 实现（必须逐字复制，不得修改接口）：**

```javascript
const EventBus = (() => {
  const _listeners = {};
  return {
    on(event, fn)  { (_listeners[event] = _listeners[event] || []).push(fn); },
    off(event, fn) { _listeners[event] = (_listeners[event] || []).filter(f => f !== fn); },
    emit(event, data) { (_listeners[event] || []).forEach(fn => fn(data)); },
  };
})();
```

> **约束**：AI 生成原型时必须使用上方代码，不允许自行实现替代版本。
> 接口固定为 `on` / `off` / `emit` 三个方法，保证映射规范中 `EventBus.on('event_name'` 正则可正确匹配。

---

## 2. 调试接口（强制）

每个原型必须提供以下调试能力：

### 2.1 状态查看面板

- 位置：左侧固定，200px 宽
- 内容：实时显示关键状态（HP、回合数、分数、当前阶段等）
- 更新方式：渲染层每帧 / 每次 EventBus 事件后更新面板 DOM
- 至少展示 5 个关键状态字段

### 2.2 参数热调区

- 位置：右侧或底部
- 控件：`<input type="range">` 滑块，拖动实时修改 CONFIG 中的参数
- 数量：至少提供 3 个可调参数（如：伤害倍率、移动速度、回合时长）
- 行为：修改参数后，下次逻辑计算使用新值（不需重置游戏）
- 每个滑块旁显示当前值

### 2.3 一键重置

- 位置：调试面板顶部
- 功能：清空状态 → 回到初始状态 → 重新渲染
- 不刷新页面

### 2.4 日志输出区

- 位置：可折叠区域
- 内容：记录关键事件（状态切换、核心计算结果、胜负/结局/解锁判定、异常）
- 格式：`[时间戳] 事件描述 | 关键数值`

```javascript
// 全局日志函数
window.logEvent = function(msg) {
  const timestamp = new Date().toLocaleTimeString();
  const line = `[${timestamp}] ${msg}`;
  console.log(line);
  // 同时写入调试面板日志区
  EventBus.emit('log_entry', line);
};
```

---

## 3. 命名规范

| 类别 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | camelCase（英文） | `calcDamage()`, `currentTurn` |
| 常量 | UPPER_SNAKE | `CONFIG.GRID_SIZE`, `MAX_UNITS` |
| 事件名 | snake_case | `'unit_moved'`, `'turn_end'` |
| CSS class | kebab-case | `.debug-panel`, `.unit-card` |
| 注释 | 中文 | `// 计算攻击伤害（含暴击判定）` |

---

## 4. 错误处理

### 4.1 边界检查

- 数组访问前检查索引是否越界
- 除法前检查分母 ≠ 0
- 关键函数入口检查参数是否为 null/undefined

### 4.2 状态回退

- 不允许"状态卡住"：每个操作如果失败，必须有清晰错误提示，状态回退到上一个合法状态
- 不允许静默吞错：任何异常必须出现在日志区

### 4.3 错误信息格式

```
[错误] 位置 → 原因 → 当前值 → 期望值
```

```javascript
// 示例
if (index < 0 || index >= units.length) {
  logEvent(`[错误] selectUnit() → 索引越界 → 当前=${index} → 期望=0~${units.length - 1}`);
  return false;
}
```

---

## 5. 视觉约束（建议遵循）

- 默认使用 Canvas 2D 或纯 CSS Grid/Flexbox 布局
- 不使用外部字体（回退到系统默认字体栈）
- 颜色用 CSS 变量统一管理（方便后续换主题）
- 网格/棋盘类原型：每个格子 ≥ 48px（方便点击）
- 移动端不做强制适配（原型目标是桌面端快速验证）

```css
:root {
  --bg-primary: #1a1a2e;
  --bg-secondary: #16213e;
  --text-primary: #e0e0e0;
  --accent: #0f3460;
  --success: #2ecc71;
  --danger: #e74c3c;
}
```

---

## 6. 表现力弹性空间（建议遵循）★v1.3新增

> 两次双轨实验（挂机装备RPG + 策略回合制RPG）一致显示：无工作流时 AI 更倾向于在动效、音效、键盘快捷键、可视化等非功能维度自主创新；而 01 规范的强约束可能抑制这种主动性。
> 本节为 AI 在以下非功能维度提供**弹性空间**——不强制实现，但明确允许并鼓励 AI 在满足 §1-§4 工程约束的前提下自主发挥：

### 6.1 动效与动画

- **允许**：AI 可在原型中自主添加过渡动画、伤害数字动效、战斗反馈动效等
- **约束**：动效实现不得阻塞主逻辑（异步执行）；不得依赖外部库
- **推荐模式**：CSS transition/animation + class toggle；或 requestAnimationFrame 短生命周期动画

### 6.2 音效反馈

- **允许**：AI 可自主使用 Web Audio API（AudioContext / OscillatorNode）实现点击反馈音、战斗音效提示
- **约束**：必须通过用户交互解锁 AudioContext；不得在无交互时自动播放；代码行数控制在 30 行以内
- **非强制**：音效是加分项而非验收项，无音效不影响原型通过

### 6.3 键盘快捷键

- **允许**：AI 可自主设计键盘快捷键方案（如 `1/2/3` 选技能、`B` 普攻、`Esc` 取消）
- **约束**：快捷键必须标注在 UI 上（按钮旁的小字 / 底部提示条），不能只有键盘无界面提示
- **冲突检查**：不与浏览器默认快捷键冲突（Ctrl+T/Ctrl+W/F5/F12 等）

### 6.4 可视化与图表

- **允许**：AI 可在对话中或原型旁产出自发性的架构图、机制关系图、UI 布局图（如 SVG/Mermaid）
- **定位**：作为对话辅助理解工具，非原型交付物的一部分
- **非强制**：不影响原型验收，但可作为沟通质量的加分项

> **设计意图**：§1-§4（架构约束 + 调试接口 + 命名规范 + 错误处理）是"工程基础设施"——不可降级。本节 §6 是"表现力上限"——不设天花板，AI 有空间的就做，时间紧就优先保证工程基础设施。


