# Interview Task: Non-Blocking Tool Calls

## 背景

这个项目已经实现了一个同步 tool-calling agent。当前 agent 在模型返回 `tool_calls` 后，会在主循环里直接调用：

```python
tool_result = self.tools.execute(tool_call)
```

这会阻塞 agent loop。你的任务是让工具调用进入后台运行，使 agent 在工具尚未完成时也能把控制权交还给调用方。

## 目标

调整 agent 的执行流程：当模型请求调用工具时，agent 不应等待工具执行完成后才返回。它应该记录必要状态，稍后在工具结果可用时继续完成后续模型调用。

你可以自行设计接口和数据结构。重点不是实现完整队列，而是把“启动工具调用”和“继续 agent loop”拆开。

## 要求

- 最小范围只要求支持一个 pending tool call
- 工具开始执行后，agent 本次调用应尽快返回，而不是等待工具结果
- 返回值需要包含足够的信息，让调用方之后可以继续 agent loop
- 工具结果可用后，agent 能把结果作为 `tool` 消息写回上下文，并继续得到最终回答
- 新增或调整测试，证明 tool call 不会阻塞 agent 本次调用
- tool 执行失败时，agent 应该把结构化错误作为 tool message 返回给模型
- 不需要接入真实队列、数据库或 LLM API，内存实现即可

## 不要求

- 一个 assistant turn 里的多个 tool call
- 多个工具并发执行
- 持久化 agent 状态
- 真实任务队列

## 追问或加分

- 支持一个 assistant turn 里的多个 tool call：依次启动多个后台任务，但不等待前一个完成后才启动下一个
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
