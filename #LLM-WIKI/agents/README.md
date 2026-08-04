# agents · 可选专家方法层

本层默认休眠。发布包不附带任何具体领域 prompt；使用者可从 `prompts/` 内的 role / context 模板创建。

## 文件职责

- `EXPERT_PROTOCOL.md`：诊断、拆解、设计和实现审查的共享方法。
- `CONTEXT_CONTRACT.md`：最小上下文接口。
- `BUILD_GUIDE.md`：根据 domain frontmatter 动态发现 prompt。
- `prompts/`：具体 role / context prompt；当前为空。

## 创建规则

- `agent_type: role`：`prompt` 必须指向一个 role prompt。
- `agent_type: context`：可被 role 按任务注入，不独立显示身份。
- `agent_type: personal`：只供人工参考，不创建 Agent。
- `agent_type: none`：不参与专家发现。

prompt 只写领域观察维度、工具箱、产物和失败模式，不复制共享协议或 domain 中的知识原则。
