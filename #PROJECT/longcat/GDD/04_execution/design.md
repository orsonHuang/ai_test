# 执行文档：longcat

> 状态：本文依据 GDD 00-03 阶段定稿，**本文已定稿**。
> 上游约束：`00_concept` / `01_top_design` / `02_architecture` / `03_systems` 全部定稿。

## 技术栈选型

| 层 | 选型 | 理由 |
|---|---|---|
| 游戏引擎 | Cocos Creator 3.x | 微信小游戏原生支持，包体小，性能优 |
| 开发语言 | TypeScript | 与 `core/` 规则代码统一，离线工具与运行时共用 |
| 目标平台 | 微信小游戏 | 概念定稿：唯一首发平台 |
| 包体限制 | 主包 ≤ 4MB | 微信小游戏硬约束 |
| 关卡存储 | 内置（resource）+ 远程（CDN） | 前 20–30 关内置，其余远程懒加载 |
| 本地存储 | `wx.setStorage` | MVP 进度持久化 |

## 代码结构

```
longcat/
├── assets/
│   ├── scripts/
│   │   ├── core/              # 纯 TypeScript 规则代码（不依赖 Cocos）
│   │   │   ├── grid.ts        # 网格数据结构与状态
│   │   │   ├── slide.ts       # 滑行结算逻辑
│   │   │   ├── validator.ts   # 通关/困死判定
│   │   │   └── types.ts       # 类型定义
│   │   │
│   │   ├── systems/           # 游戏系统（依赖 Cocos）
│   │   │   ├── S01_slide_core/
│   │   │   │   ├── SlideCoreSystem.ts    # 滑行核心系统
│   │   │   │   └── UndoManager.ts        # 撤销管理
│   │   │   │
│   │   │   └── S02_level/
│   │   │       ├── LevelSystem.ts        # 关卡系统
│   │   │       ├── LevelLoader.ts        # 关卡加载器（内置/远程）
│   │   │       ├── LevelCache.ts         # 关卡缓存
│   │   │       └── ProgressManager.ts    # 进度持久化
│   │   │
│   │   ├── ui/                # UI 组件
│   │   │   ├── GameScene.ts   # 游戏主场景
│   │   │   ├── GridRenderer.ts # 网格渲染
│   │   │   ├── CatRenderer.ts  # 猫咪渲染
│   │   │   ├── FlowerRenderer.ts # 蒲公英渲染
│   │   │   ├── WallRenderer.ts   # 木箱子渲染
│   │   │   ├── UndoButton.ts     # 撤销按钮
│   │   │   └── ResultPopup.ts    # 通关/困死弹窗
│   │   │
│   │   └── utils/             # 工具函数
│   │       ├── InputHandler.ts # 划线输入处理
│   │       └── Storage.ts      # 本地存储封装
│   │
│   ├── resources/
│   │   └── levels/            # 内置关卡（前 20–30 关）
│   │       └── builtin_levels.json
│   │
│   └── scenes/
│       └── game.scene         # 游戏主场景
│
├── tools/                     # 离线工具（node 脚本）
│   ├── generator/
│   │   ├── level_generator.ts # 关卡生成器
│   │   └── solver.ts          # 求解器（DFS + 剪枝）
│   │
│   ├── validator/
│   │   └── batch_validate.ts  # 批量验证工具
│   │
│   └── package.json           # 工具依赖
│
└── package.json               # 项目配置
```

## 核心代码模块

### 1. core/ — 规则代码（不依赖 Cocos）

#### grid.ts

```typescript
// 格子状态枚举
export enum CellType {
  EMPTY = 0,      // 空格（草地）
  WALL = 1,       // 木箱子（障碍）
  FLOWER = 2,     // 蒲公英（已填充）
}

// 网格类
export class Grid {
  width: number;
  height: number;
  cells: CellType[];  // 一维数组，按行存储
  
  constructor(width: number, height: number);
  get(x: number, y: number): CellType;
  set(x: number, y: number, type: CellType): void;
  isEmpty(x: number, y: number): boolean;
  isWall(x: number, y: number): boolean;
  isFlower(x: number, y: number): boolean;
  isOutOfBounds(x: number, y: number): boolean;
}
```

#### slide.ts

```typescript
// 方向枚举
export enum Direction {
  UP = 'U',
  DOWN = 'D',
  LEFT = 'L',
  RIGHT = 'R',
}

// 滑行结果
export interface SlideResult {
  path: Array<{x: number, y: number}>;  // 滑行路径
  finalPos: {x: number, y: number};     // 最终位置
  valid: boolean;                        // 是否有效（路径长度 > 0）
}

// 滑行结算
export function slide(
  grid: Grid,
  startPos: {x: number, y: number},
  direction: Direction
): SlideResult;
```

#### validator.ts

```typescript
// 关卡状态
export enum GameResult {
  PLAYING = 'PLAYING',
  WIN = 'WIN',
  STUCK = 'STUCK',
}

// 通关判定
export function checkWin(grid: Grid): boolean;

// 困死判定
export function checkStuck(grid: Grid, catPos: {x: number, y: number}): boolean;

// 综合判定
export function checkResult(grid: Grid, catPos: {x: number, y: number}): GameResult;
```

### 2. S01_slide_core — 滑行核心系统

#### SlideCoreSystem.ts

```typescript
export class SlideCoreSystem {
  private grid: Grid;
  private catPos: {x: number, y: number};
  private catDirection: Direction;
  private undoStack: Array<{catPos: {x: number, y: number}, flowerCount: number}>;
  private undoCount: number;
  private result: GameResult;
  private steps: number;
  
  constructor(levelData: LevelData);
  
  // 接收划线输入
  slide(direction: Direction): SlideResult;
  
  // 撤销
  undo(): boolean;
  
  // 获取状态
  getState(): SlideCoreState;
  
  // 重置关卡
  reset(): void;
}
```

#### UndoManager.ts

```typescript
export class UndoManager {
  private stack: Array<UndoState>;
  private maxCount: number;
  private currentCount: number;
  
  constructor(maxCount: number = 3);
  
  push(state: UndoState): void;
  pop(): UndoState | null;
  canUndo(): boolean;
  getCount(): number;
  reset(): void;
}
```

### 3. S02_level — 关卡系统

#### LevelSystem.ts

```typescript
export class LevelSystem {
  private currentLevelId: number;
  private levelCompleted: Map<number, boolean>;
  private levelSteps: Map<number, number>;
  private currentLevel: LevelData | null;
  private loader: LevelLoader;
  private cache: LevelCache;
  private progress: ProgressManager;
  
  constructor();
  
  // 加载关卡
  async loadLevel(levelId: number): Promise<LevelData>;
  
  // 通关处理
  onLevelComplete(levelId: number, steps: number): void;
  
  // 获取当前关卡
  getCurrentLevel(): LevelData | null;
  
  // 下一关
  async nextLevel(): Promise<LevelData | null>;
  
  // 获取网格尺寸（动态计算）
  getGridSize(levelId: number): {width: number, height: number};
}
```

#### LevelLoader.ts

```typescript
export class LevelLoader {
  private builtinLevels: Map<number, LevelData>;
  private cache: LevelCache;
  
  constructor();
  
  // 统一加载接口
  async loadLevel(levelId: number): Promise<LevelData>;
  
  // 加载内置关卡
  private loadBuiltinLevel(levelId: number): LevelData;
  
  // 加载远程关卡
  private async loadRemoteLevel(levelId: number): Promise<LevelData>;
}
```

#### LevelCache.ts

```typescript
export class LevelCache {
  private cache: Map<number, LevelData>;
  private maxSize: number;
  
  constructor(maxSize: number = 100);
  
  get(levelId: number): LevelData | null;
  set(levelId: number, data: LevelData): void;
  has(levelId: number): boolean;
  clear(): void;
}
```

#### ProgressManager.ts

```typescript
export class ProgressManager {
  private currentLevelId: number;
  private levelCompleted: Map<number, boolean>;
  private levelSteps: Map<number, number>;
  
  constructor();
  
  // 加载进度
  load(): void;
  
  // 保存进度
  save(): void;
  
  // 更新通关记录
  markCompleted(levelId: number, steps: number): void;
  
  // 获取当前关卡
  getCurrentLevelId(): number;
  
  // 设置当前关卡
  setCurrentLevelId(levelId: number): void;
  
  // 获取关卡步数
  getLevelSteps(levelId: number): number | null;
}
```

## 关卡数据格式

```json
{
  "id": 0,
  "size": [5, 6],
  "grid": "S....#.###..#.....#..###..#.....",
  "start": [0, 0],
  "solution": "RRDDLLURR",
  "meta": {
    "solutionCount": 2,
    "firstMoveTolerance": 0.5,
    "difficulty": 0.3,
    "source": "handmade",
    "tags": ["tutorial"]
  }
}
```

**网格编码规则：**
- `S` = 起点（银渐层猫初始位置）
- `.` = 空格（草地）
- `#` = 木箱子（障碍）
- 字符串长度 = width × height，按行存储

**障碍物视觉规则：**
- 边界 = 空气墙（透明，不占格子）
- 内部障碍 = 木箱子（实体可见）

**木箱子生成启发式：**
- 优先生成"至少 3 面有路"的木箱子
- 允许例外（某些特殊布局可放宽到"至少 2 面有路"）

## 网格尺寸动态计算

```typescript
export function getGridSize(levelId: number): {width: number, height: number} {
  const sizeIndex = levelId % 10;
  
  if (sizeIndex < 2) {
    // 小网格：4×5 ~ 5×6
    return {
      width: 4 + Math.floor(Math.random() * 2),
      height: 5 + Math.floor(Math.random() * 2),
    };
  } else if (sizeIndex < 5) {
    // 中网格：6×7 ~ 7×8
    return {
      width: 6 + Math.floor(Math.random() * 2),
      height: 7 + Math.floor(Math.random() * 2),
    };
  } else {
    // 大网格：7×8 ~ 8×10
    return {
      width: 7 + Math.floor(Math.random() * 2),
      height: 8 + Math.floor(Math.random() * 3),
    };
  }
}
```

## 撤销机制实现

```typescript
// 撤销状态快照
interface UndoState {
  catPos: {x: number, y: number};
  flowerPositions: Array<{x: number, y: number}>;  // 本步长出的蒲公英
}

// 撤销流程
function undo(): boolean {
  if (undoCount <= 0 || undoStack.length === 0) {
    return false;
  }
  
  const prevState = undoStack.pop()!;
  
  // 移除本步长出的蒲公英
  for (const pos of prevState.flowerPositions) {
    grid.set(pos.x, pos.y, CellType.EMPTY);
  }
  
  // 恢复猫位置
  catPos = prevState.catPos;
  
  // 撤销次数 -1
  undoCount--;
  
  return true;
}
```

## 输入处理

```typescript
// 划线输入处理
class InputHandler {
  private startPos: {x: number, y: number} | null = null;
  private onSlide: (direction: Direction) => void;
  
  constructor(onSlide: (direction: Direction) => void);
  
  // 触摸开始
  onTouchStart(x: number, y: number): void;
  
  // 触摸结束
  onTouchEnd(x: number, y: number): void;
  
  // 计算方向
  private getDirection(start: {x: number, y: number}, end: {x: number, y: number}): Direction | null;
}
```

## 渲染层

### GridRenderer.ts

```typescript
// 网格渲染
export class GridRenderer {
  private gridNode: cc.Node;
  private cellSize: number;
  
  constructor(gridNode: cc.Node, cellSize: number);
  
  // 渲染网格
  render(grid: Grid, catPos: {x: number, y: number}): void;
  
  // 渲染单个格子
  private renderCell(x: number, y: number, type: CellType): void;
}
```

### CatRenderer.ts

```typescript
// 猫咪渲染
export class CatRenderer {
  private catNode: cc.Node;
  private slideAnimation: cc.Animation;
  
  constructor(catNode: cc.Node);
  
  // 更新猫咪位置
  updatePosition(pos: {x: number, y: number}, direction: Direction): void;
  
  // 播放滑行动画
  playSlideAnimation(path: Array<{x: number, y: number}>): Promise<void>;
}
```

### FlowerRenderer.ts

```typescript
// 蒲公英渲染
export class FlowerRenderer {
  private flowerPool: cc.NodePool;
  
  constructor();
  
  // 长出蒲公英
  growFlower(x: number, y: number): void;
  
  // 移除蒲公英（撤销）
  removeFlower(x: number, y: number): void;
  
  // 清除所有蒲公英
  clear(): void;
}
```

### WallRenderer.ts

```typescript
// 木箱子渲染
export class WallRenderer {
  private wallPool: cc.NodePool;
  
  constructor();
  
  // 渲染木箱子
  renderWall(x: number, y: number): void;
  
  // 清除所有木箱子
  clear(): void;
}
```

## 离线工具

### 关卡生成器

```typescript
// tools/generator/level_generator.ts

import { Grid, CellType } from '../assets/scripts/core/grid';
import { solve } from './solver';

interface GeneratorParams {
  width: number;
  height: number;
  wallDensity: number;  // 木箱子密度（0.1 ~ 0.3）
  minSolutionCount: number;
  maxSolutionCount: number;
}

export function generateLevel(params: GeneratorParams): LevelData | null {
  // 1. 随机生成网格
  const grid = generateRandomGrid(params);
  
  // 2. 连通性预检
  if (!checkConnectivity(grid)) {
    return null;
  }
  
  // 3. 求解器验证
  const solutions = solve(grid);
  if (solutions.length === 0) {
    return null;
  }
  
  // 4. 难度评估
  const difficulty = evaluateDifficulty(solutions);
  if (difficulty < params.minSolutionCount || difficulty > params.maxSolutionCount) {
    return null;
  }
  
  // 5. 输出关卡数据
  return {
    id: 0,
    size: [params.width, params.height],
    grid: encodeGrid(grid),
    start: findStart(grid),
    solution: solutions[0],
    meta: {
      solutionCount: solutions.length,
      firstMoveTolerance: calculateFirstMoveTolerance(grid, solutions),
      difficulty: difficulty,
      source: 'generated',
      tags: ['normal'],
    },
  };
}
```

### 求解器

```typescript
// tools/generator/solver.ts

import { Grid, CellType, Direction } from '../assets/scripts/core/grid';
import { slide, checkWin, checkStuck } from '../assets/scripts/core/slide';

export function solve(grid: Grid): string[] {
  const solutions: string[] = [];
  const catPos = findStart(grid);
  
  // DFS + 剪枝
  dfs(grid, catPos, '', solutions);
  
  return solutions;
}

function dfs(
  grid: Grid,
  catPos: {x: number, y: number},
  path: string,
  solutions: string[]
): void {
  // 通关判定
  if (checkWin(grid)) {
    solutions.push(path);
    return;
  }
  
  // 困死判定
  if (checkStuck(grid, catPos)) {
    return;
  }
  
  // 剪枝：死腔检测
  if (hasDeadZone(grid)) {
    return;
  }
  
  // 剪枝：奇偶性检测
  if (!checkParity(grid)) {
    return;
  }
  
  // 四方向尝试
  for (const dir of [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]) {
    const result = slide(grid, catPos, dir);
    if (result.valid) {
      // 应用滑行
      const newGrid = applySlide(grid, result);
      dfs(newGrid, result.finalPos, path + dir, solutions);
    }
  }
}
```

## 测试计划

### 单元测试

| 模块 | 测试内容 |
|---|---|
| `core/grid.ts` | 格子状态读写、边界检测 |
| `core/slide.ts` | 滑行结算、路径计算、无效输入处理 |
| `core/validator.ts` | 通关判定、困死判定 |
| `UndoManager` | 撤销栈操作、次数限制 |
| `LevelLoader` | 内置/远程加载、缓存逻辑 |
| `ProgressManager` | 进度读写、持久化 |

### 集成测试

| 场景 | 测试内容 |
|---|---|
| 完整关卡流程 | 进入关卡 → 划线 → 通关 → 下一关 |
| 撤销功能 | 划线 → 撤销 → 重新划线 |
| 困死处理 | 划线 → 困死 → 重置 |
| 网格循环 | 连续 10 关，验证网格尺寸变化 |
| 远程加载失败 | 模拟网络错误，验证降级到内置关卡 |

### 离线工具测试

| 工具 | 测试内容 |
|---|---|
| 关卡生成器 | 生成的关卡 100% 有解 |
| 求解器 | 与运行时行为一致 |
| 批量验证 | 1000 关验证，无崩溃、无死关 |

### 性能测试

| 指标 | 目标 |
|---|---|
| 单关加载时间 | < 100ms |
| 滑行结算耗时 | < 1ms |
| 困死判定耗时 | < 10ms（8×10 网格） |
| 内存占用 | < 50MB |

## 开发里程碑

### MVP（4 周）

| 周 | 任务 |
|---|---|
| W1 | 搭建项目骨架、实现 `core/` 规则代码、单元测试 |
| W2 | 实现 S01 滑行核心系统、S02 关卡系统、UI 渲染 |
| W3 | 实现撤销功能、内置 20 关手工关卡、离线生成器 |
| W4 | 集成测试、性能优化、微信小游戏适配 |

### P1 迭代（后续）

- 每日挑战系统
- 好友排行榜
- 分享奖励
- 成就图鉴

## 风险与应对

| 风险 | 应对 |
|---|---|
| 求解器性能不足 | 优化剪枝策略、限制网格尺寸上限（8×10） |
| 微信包体超限 | 内置关卡控制在 20–30 关、压缩 JSON |
| 远程加载失败 | 本地缓存 + 内置关卡池降级 |
| 玩家误操作焦虑 | 撤销机制（每关 3 次） |
| 关卡难度失控 | 生成器难度评估 + 手工关卡保底 |
