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

## 15 分钟面试扩展题

让 agent 同时支持同步工具和后台工具。目标不是实现完整任务队列，而是看候选人能否识别阻塞点、为工具引入执行策略，并调整 agent loop 的返回语义。

最小要求：

- 只需要支持一个 pending background tool call
- `calculator` 保持同步工具：调用后应直接得到最终回答
- `get_weather` 改为后台工具：启动后 agent 本次调用应尽快返回
- 后台工具返回值需要包含足够信息，让调用方之后可以继续 agent loop
- 后台工具结果可用后，agent 能把结果作为 `tool` 消息写回上下文，并继续得到最终回答
- 新增或调整测试，证明同步工具仍然同步、后台工具不会阻塞当前 agent 调用

追问或加分项：

- 支持一个 assistant turn 里的多个 tool call：依次启动多个后台任务，但不等待前一个完成后才启动下一个
- 同一个 assistant turn 中混合同步工具和后台工具
- 支持任务超时和取消
- 支持 `pending`、`running`、`succeeded`、`failed` 状态
- 后续替换成 Celery、RQ、Temporal 或数据库队列
