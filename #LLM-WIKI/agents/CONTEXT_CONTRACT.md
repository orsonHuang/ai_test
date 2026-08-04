# CONTEXT_CONTRACT · ContextBrief 接口

```yaml
task: 必填
target_outcome: 可选
target_audience: 可选
current_state: 可选
project_stage: 可选
constraints: []
observed_symptoms: []
locked_decisions: []
available_evidence: []
```

加载优先级：用户当前明确说明 → ContextBrief → 项目文件 / 附件 → 本轮已确认信息 → 只追问会阻断判断的缺口。

- 缺失项能条件化处理时，写明假设后继续。
- 缺失会改变推荐方向、数值或实现边界时，一次性追问。
- `locked_decisions` 未经显式重议不得回退。
- 独立使用时从对话与附件临时构建；不要求宿主目录。
- ContextBrief 默认只在当前任务有效，不自动写入知识库。
