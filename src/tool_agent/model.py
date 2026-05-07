from __future__ import annotations

import re
from typing import Protocol, Sequence

from .messages import Message, ToolCall
from .tools import ToolSpec


class ChatModel(Protocol):
    """Model interface used by the agent loop."""

    def complete(self, messages: Sequence[Message], tools: Sequence[ToolSpec]) -> Message:
        ...


class RuleBasedDemoModel:
    """Deterministic local model stub for demos and tests.

    A real implementation can replace this class with an OpenAI, Anthropic,
    LangChain, or LlamaIndex adapter while keeping the agent loop unchanged.
    """

    def complete(self, messages: Sequence[Message], tools: Sequence[ToolSpec]) -> Message:
        if self._has_pending_tool_results(messages):
            return Message.assistant(self._summarize_tool_results(messages))

        user_text = self._last_user_message(messages)
        tool_calls = self._plan_tool_calls(user_text)
        if tool_calls:
            return Message.assistant(content="", tool_calls=tool_calls)

        available_tools = ", ".join(tool.name for tool in tools) or "no tools"
        return Message.assistant(
            "I can answer directly, or use tools when the request needs them. "
            f"Available tools: {available_tools}."
        )

    def _has_pending_tool_results(self, messages: Sequence[Message]) -> bool:
        return bool(messages and messages[-1].role == "tool")

    def _summarize_tool_results(self, messages: Sequence[Message]) -> str:
        results = []
        for message in messages:
            if message.role == "tool":
                results.append(f"{message.name}: {message.content}")
        return "Tool results: " + "; ".join(results)

    def _last_user_message(self, messages: Sequence[Message]) -> str:
        for message in reversed(messages):
            if message.role == "user":
                return message.content
        return ""

    def _plan_tool_calls(self, user_text: str) -> list[ToolCall]:
        calls: list[ToolCall] = []

        expression = self._extract_math_expression(user_text)
        if expression:
            calls.append(
                ToolCall(
                    id=f"call_{len(calls) + 1}",
                    name="calculator",
                    arguments={"expression": expression},
                )
            )

        city = self._extract_city(user_text)
        if city:
            calls.append(
                ToolCall(
                    id=f"call_{len(calls) + 1}",
                    name="get_weather",
                    arguments={"city": city},
                )
            )

        return calls

    def _extract_math_expression(self, user_text: str) -> str | None:
        if not re.search(r"\d", user_text):
            return None
        if not re.search(r"(calculate|math|计算|算|等于|多少)", user_text, re.IGNORECASE):
            return None

        match = re.search(r"[-+*/().% 0-9]*\d[-+*/().% 0-9]*", user_text)
        if match is None:
            return None

        expression = match.group(0).strip()
        return expression or None

    def _extract_city(self, user_text: str) -> str | None:
        city_aliases = {
            "北京": "Beijing",
            "beijing": "Beijing",
            "上海": "Shanghai",
            "shanghai": "Shanghai",
            "深圳": "Shenzhen",
            "shenzhen": "Shenzhen",
            "杭州": "Hangzhou",
            "hangzhou": "Hangzhou",
        }

        lowered = user_text.lower()
        if not re.search(r"(weather|天气|温度)", lowered):
            return None

        for alias, city in city_aliases.items():
            if alias in lowered:
                return city
        return "Beijing"
