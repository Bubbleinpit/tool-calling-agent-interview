# Tool Calling Agent Interview Project

一个自包含的 Python 小项目，用来演示最小可运行的 agent tool calling 循环。它不依赖真实 LLM API，因此适合现场编程题：候选人可以直接跑测试，然后把同步 tool 调用改造成非阻塞后台执行。

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

示例输出会包含一次 `calculator` tool 调用。

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

把同步 tool 调用改成非阻塞后台执行。目标不是实现完整任务队列，而是看候选人能否识别阻塞点、调整 agent loop 的返回语义，并用测试证明工具运行不会卡住本次 agent 调用。

最小要求：

- 只需要支持一个 pending tool call
- 工具开始执行后，agent 本次调用应尽快返回
- 返回值需要包含足够信息，让调用方之后可以继续 agent loop
- 工具结果可用后，agent 能把结果作为 `tool` 消息写回上下文，并继续得到最终回答
- 新增或调整测试，证明 tool call 不会阻塞 agent 本次调用

追问或加分项：

- 支持一个 assistant turn 里的多个 tool call：依次启动多个后台任务，但不等待前一个完成后才启动下一个
- 支持任务超时和取消
- 支持 `pending`、`running`、`succeeded`、`failed` 状态
- 后续替换成 Celery、RQ、Temporal 或数据库队列
