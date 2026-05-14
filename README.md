# Tool Calling Agent Interview Project

一个自包含的 Python 小项目，用来演示最小可运行的 agent tool calling 循环。它不依赖真实 LLM API，因此适合现场编程题：候选人可以直接跑测试，然后把 agent 改造成同时支持同步工具和非阻塞后台工具。

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

## 面试扩展题

让 agent 同时支持同步工具和**非阻塞**后台工具。`get_weather` 带有真实延迟，同步执行会阻塞整个 agent 调用。核心考察点：候选人能否识别 agent loop 与后台任务之间需要一种通信 / 同步机制，并把它实现出来（最简单可接受方案是轮询）。

完整任务说明见 [INTERVIEW_TASK.md](INTERVIEW_TASK.md)。
