from tool_agent import Message, RuleBasedDemoModel, ToolCallingAgent
from tool_agent.demo_tools import build_demo_registry


def test_agent_executes_calculator_tool() -> None:
    agent = ToolCallingAgent(
        model=RuleBasedDemoModel(),
        tools=build_demo_registry(),
    )

    result = agent.run("请计算 2 + 3 * 4")

    assert '"result": 14' in result.final_answer
    assert [message.role for message in result.messages] == [
        "system",
        "user",
        "assistant",
        "tool",
        "assistant",
    ]


def test_agent_executes_weather_tool() -> None:
    agent = ToolCallingAgent(
        model=RuleBasedDemoModel(),
        tools=build_demo_registry(),
    )

    result = agent.run("告诉我上海天气")

    tool_messages = [message for message in result.messages if message.role == "tool"]
    assert len(tool_messages) == 1
    assert tool_messages[0].name == "get_weather"
    assert '"city": "Shanghai"' in result.final_answer


def test_unknown_tool_returns_tool_error_message() -> None:
    # Build the malformed tool call explicitly to keep this test focused on
    # the agent's error path instead of the demo model's planner.
    from tool_agent.messages import ToolCall

    class UnknownToolModel:
        def complete(self, messages, tools):
            if messages[-1].role == "tool":
                return Message.assistant(f"observed {messages[-1].content}")
            return Message.assistant(
                "",
                tool_calls=[
                    ToolCall(id="call_1", name="missing_tool", arguments={}),
                ],
            )

    agent = ToolCallingAgent(
        model=UnknownToolModel(),
        tools=build_demo_registry(),
    )

    result = agent.run("use a missing tool")

    assert "unknown tool: missing_tool" in result.final_answer
