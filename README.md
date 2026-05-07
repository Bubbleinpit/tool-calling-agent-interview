# Tool Calling Agent Interview Project

一个自包含的 Python 小项目，用来演示最小可运行的 agent tool calling 循环。它不依赖真实 LLM API，因此适合现场编程题：候选人可以直接跑测试，然后把同步 tool 调用改造成一个最小 background task 接口。

## 项目结构

```text
src/tool_agent/
  agent.py        # agent loop: model -> tool calls -> tool results -> final answer
  tools.py        # tool registry and synchronous execution
  model.py        # deterministic model stub used by tests and demo
  demo_tools.py   # calculator and weather demo tools
  cli.py          # command line entrypoint
tests/
  test_agent.py   # behavior tests
```

## 快速开始

```bash
cd ~/workspace/tool-calling-agent-interview
uv sync --extra dev
uv run tool-agent --trace
uv run pytest
```

示例输出会包含两次 tool 调用：`calculator` 和 `get_weather`。

## 当前行为

`ToolCallingAgent.run()` 是一个经典同步 tool-calling loop：

1. 把用户消息发给 `ChatModel.complete()`
2. 如果模型返回 `tool_calls`，逐个调用 `ToolRegistry.execute()`
3. 把每个工具结果作为 `tool` 消息追加到上下文
4. 再次调用模型，直到模型返回最终回答

关键同步执行点在 `src/tool_agent/agent.py`：

```python
tool_result = self.tools.execute(tool_call)
```

## 15 分钟面试扩展题

把 `ToolRegistry.execute(tool_call)` 改成通过 `BackgroundTaskRunner` 提交执行。目标不是实现完整任务队列，而是看候选人能否拆出清晰接口、调整 agent loop，并用测试证明行为。

建议最小接口：

```python
class BackgroundTaskRunner:
    def submit(self, tool_call: ToolCall) -> str: ...
    def result(self, job_id: str) -> str: ...
```

要求：

- `submit(tool_call)` 返回 `job_id`
- `result(job_id)` 可以阻塞等待并返回 tool result
- 一个 agent turn 中如果有多个 `tool_call`，先全部 `submit`，再逐个取 `result`
- 现有测试继续通过
- 新增一个测试，证明 agent 确实调用了 `submit`

追问或加分项：

- 支持任务超时和取消
- 支持 `pending`、`running`、`succeeded`、`failed` 状态
- 多个 tool call 真正并发执行
- 后续替换成 Celery、RQ、Temporal 或数据库队列
