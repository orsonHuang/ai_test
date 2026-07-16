# NOW · 当前状态锚点

> **用途**：AI 快速定位"我们现在在哪、下一步是什么"。每次对话结束更新。
> **维护**：AI 自动维护。Orson 可以随时口头更新"现在在做 X"。

---

## 当前在哪

- **当前项目**：Awakening Demo（AI 对话解谜游戏）
- **当前阶段**：线上 embedding 模型重复加载问题已修复，服务运行稳定
- **本轮完成**：
  - 定位根因：gunicorn `-w 2` 双 worker 导致每个进程独立加载 embedding 模型
  - 修复方案：worker 降至 1，模型仅加载 1 份
  - 增加本地模型缓存兜底：`sentence_matcher.py` 优先从 `/root/.cache/torch/sentence_transformers/...` 加载，避免 HuggingFace/hf-mirror 网络超时
  - 通过 modelscope 预下载模型到服务器本地缓存
  - 更新 `setup.sh` 默认 worker 数为 1
  - 本地 Git 提交
  - 验证 openclaw、orson-huang-homepage 未受影响

---

## 下一步

- 在公网环境测试多轮对话，确认不再反复提示"加载中"
- 根据线上反馈继续补充响应库或调匹配阈值

---

## 阻塞项

（无）

---

## 最近完成

- 2026-07-15：隐藏文件显示逻辑简化 + GDD 更新 + Git 提交 + 部署到 Lighthouse
- 2026-07-13：响应库扩展 15 条 + 成长反馈 + 侧边栏修复 + Day1 M-M 备忘
- 2026-07-12：响应库重构与智能匹配引擎上线
- 2026-07-11：generate_reply 引擎流程文档化
