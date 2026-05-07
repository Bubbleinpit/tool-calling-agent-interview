# Interview Task: Minimal Background Tool Calls

## 背景

这个项目已经实现了一个同步 tool-calling agent。当前 agent 在模型返回 `tool_calls` 后，会在主循环里直接调用：

```python
tool_result = self.tools.execute(tool_call)
```

你的任务是把这个执行模型改成通过一个最小 background task 接口完成。这个题目按 15 分钟现场编程设计，不要求实现完整任务队列。

## 目标

实现一个 `BackgroundTaskRunner`，让 agent 先提交 tool call，再通过 `job_id` 取回结果。

建议最小接口：

```python
class BackgroundTaskRunner:
    def submit(self, tool_call: ToolCall) -> str: ...
    def result(self, job_id: str) -> str: ...
```

接口不必完全照抄，可以按你的设计调整，但需要保留“提交任务”和“按 job_id 取结果”这两个边界。

## 要求

- `submit(tool_call)` 返回 `job_id`
- `result(job_id)` 可以阻塞等待并返回 tool result
- 一个 agent turn 中如果有多个 `tool_call`，先全部 `submit`，再逐个取 `result`
- 现有测试继续通过
- 新增至少一个测试，证明 agent 确实调用了 `submit`
- tool 执行失败时，agent 应该把结构化错误作为 tool message 返回给模型
- 不需要接入真实队列、数据库或 LLM API，内存实现即可

## 追问或加分

- 支持超时
- 支持取消任务
- 支持 `pending`、`running`、`succeeded`、`failed` 状态
- 多个 tool call 真正并发执行
- 把后台任务执行层设计成可替换接口，后续能替换为 Celery、RQ、Temporal 或数据库队列

## 运行方式

```bash
cd ~/workspace/tool-calling-agent-interview
uv sync --extra dev
uv run pytest
uv run tool-agent --trace
```
