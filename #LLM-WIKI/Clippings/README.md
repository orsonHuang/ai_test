# Clippings · 来源入口

存放待消化与已消化的 Markdown 剪藏。通过文件名前缀 + frontmatter 双重标记区分状态。

## 状态标记（三态）

| 文件名前缀 | frontmatter `status` | 含义 |
|-----------|---------------------|------|
| **无前缀** | 无 `status` 字段 | 新导入，尚未进入工作流 |
| `【TODO】` | `status: todo` | 已评分，等待 Ingest 消化入库 |
| `【DONE】` | `status: done` | 已消化入库 |

### 判断规则（优先级从高到低）

1. 文件名以 `【DONE】` 开头 → 已消化入库
2. 文件名以 `【TODO】` 开头 → 未消化，等待 Ingest
3. 以上都不匹配（即文件名前 6 个字符不是 `【TODO】` 或 `【DONE】`）→ 新导入，尚未进入工作流

### 生命周期

- **新导入**：Obsidian Web Clipper 导入后自动写入 `status: todo`；若因意外未写入，无前缀的文件同样视为待处理。
- **评分后**：文件名加 `【TODO】` 前缀，标准化为 `【TODO】YYYYMMDD-简短标题.md`。
- **入库后**：`status` 改为 `done`，前缀改为 `【DONE】`。

### frontmatter 字段

```yaml
status: todo    # 未消化
status: done    # 已消化入库
```

AI 查找未消化文件时，搜索条件为：`status: todo` **或** 文件名的前 6 个字符不是 `【DONE】` 且不是 `【TODO】`（即无前缀的新文件）。

## 文件规范

- 原文 URL、标题、作者和剪藏时间放入 frontmatter。
- Ingest 前检查截断、嵌入视频、图片信息量和正文完整性。
- 评分-only 阶段不改文件；确认入库或跳过后再标准化命名。
- Clippings 是中间产物，不参与知识图谱。
