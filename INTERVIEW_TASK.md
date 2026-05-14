# Interview Task: 同步工具 + 非阻塞后台工具

## 背景

这个项目已经实现了一个同步 tool-calling agent。模型返回 `tool_calls` 后，agent 在主循环里直接调用：

```python
tool_result = self.tools.execute(tool_call)
```

这对所有工具都会阻塞 agent loop。`get_weather` 现在带有真实延迟（模拟慢速远程调用），所以同步执行会让整个 agent 调用一直卡住等待结果。

你的任务不是把所有工具都无脑改成后台执行，而是让 agent 同时支持同步工具和**非阻塞**后台工具。

## 目标

调整 agent 的执行流程，让不同工具可以选择不同的执行策略：

- 同步工具保持当前行为：立即执行，把结果写入 `tool` 消息，然后继续 agent loop
- 后台工具不阻塞当前 agent 调用：启动任务后尽快返回，不等待结果

**核心考察点**：后台工具一旦启动，agent loop 与后台任务之间就需要某种通信 / 同步机制来传递完成状态。你需要识别这个需求并把它实现出来。最简单的可接受方案就是：启动异步任务 → 轮询状态（poll / sleep loop / thread join 都行）→ 任务完成后把结果写回 `tool` 消息 → 继续 loop 得到最终回答。

接口和数据结构自行设计。重点不是实现完整队列，而是识别阻塞点、为工具引入执行策略、并在 loop 和后台任务之间建立通信。

## 要求

- 最小范围只要求支持一个 pending background tool call
- `calculator` 保持同步工具：调用后应直接得到最终回答
- `get_weather` 改为后台工具：启动后 agent 本次调用应在后台任务**完成之前**就返回
- 后台工具的返回值 / agent 的返回值需要包含足够信息（任务句柄、状态等），让调用方之后可以查询状态并继续 agent loop
- 后台任务完成后，agent 能把结果作为 `tool` 消息写回上下文，并继续得到最终回答
- 后台任务要真正运行在 agent loop 之外（stdlib `threading` / `concurrent.futures` 即可），否则做不到非阻塞
- 新增测试，用时序断言证明：同步工具仍然同步；后台工具的 `run()` 在后台任务完成前就返回；任务完成后能继续拿到最终回答
- tool 执行失败时，agent 应该把结构化错误作为 tool message 返回给模型
- 不需要接入真实队列、数据库或 LLM API，内存实现即可

## 不要求

- 一个 assistant turn 里的多个 tool call
- 多个工具并发执行
- 持久化 agent 状态
- 真实任务队列
- 让所有工具都后台执行

## 追问或加分

- 让 LLM 自己驱动轮询：注册一个 `wait` / `sleep` 工具，模型看到 pending 状态后主动调用它再次进入 loop
- 支持一个 assistant turn 里的多个 tool call：依次启动多个后台任务，但不等待前一个完成后才启动下一个
- 同一个 assistant turn 中混合同步工具和后台工具
- 支持超时
- 支持取消任务
- 支持 `pending`、`running`、`succeeded`、`failed` 状态
- 把后台任务执行层设计成可替换接口，后续能替换为 Celery、RQ、Temporal 或数据库队列
- 注入 clock / sleep 抽象，让时序测试不依赖真实墙钟

## 运行方式

```bash
uv sync --extra dev
uv run pytest
uv run tool-agent --trace
```
