# Interview Task: Mixed Sync and Background Tool Calls

## 背景

这个项目已经实现了一个同步 tool-calling agent。当前 agent 在模型返回 `tool_calls` 后，会在主循环里直接调用：

```python
tool_result = self.tools.execute(tool_call)
```

这对所有工具都会阻塞 agent loop。你的任务不是把所有工具都无脑改成后台执行，而是让 agent 同时支持同步工具和后台工具。

## 目标

调整 agent 的执行流程，让不同工具可以选择不同的执行策略：

- 同步工具保持当前行为：立即执行，把结果写入 `tool` 消息，然后继续 agent loop
- 后台工具不阻塞当前 agent 调用：启动任务后尽快返回，并保留稍后继续运行所需的状态

你可以自行设计接口和数据结构。重点不是实现完整队列，而是让 agent 能根据工具的执行策略做出不同控制流选择。

## 要求

- 最小范围只要求支持一个 pending background tool call
- `calculator` 保持同步工具：调用后应直接得到最终回答
- `get_weather` 改为后台工具：启动后 agent 本次调用应尽快返回，而不是等待天气结果
- 后台工具的返回值需要包含足够的信息，让调用方之后可以继续 agent loop
- 后台工具结果可用后，agent 能把结果作为 `tool` 消息写回上下文，并继续得到最终回答
- 新增或调整测试，证明同步工具仍然同步、后台工具不会阻塞当前 agent 调用
- tool 执行失败时，agent 应该把结构化错误作为 tool message 返回给模型
- 不需要接入真实队列、数据库或 LLM API，内存实现即可

## 不要求

- 一个 assistant turn 里的多个 tool call
- 多个工具并发执行
- 持久化 agent 状态
- 真实任务队列
- 让所有工具都后台执行

## 追问或加分

- 支持一个 assistant turn 里的多个 tool call：依次启动多个后台任务，但不等待前一个完成后才启动下一个
- 同一个 assistant turn 中混合同步工具和后台工具
- 支持超时
- 支持取消任务
- 支持 `pending`、`running`、`succeeded`、`failed` 状态
- 把后台任务执行层设计成可替换接口，后续能替换为 Celery、RQ、Temporal 或数据库队列

## 运行方式

```bash
cd ~/workspace/tool-calling-agent-interview
uv sync --extra dev
uv run pytest
uv run tool-agent --trace
```
