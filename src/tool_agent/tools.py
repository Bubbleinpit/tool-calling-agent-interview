from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .messages import ToolCall


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(frozen=True)
class Tool:
    spec: ToolSpec
    handler: Callable[..., Any]


class ToolRegistry:
    """Stores tool definitions and synchronously executes tool calls."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        if name in self._tools:
            raise ValueError(f"tool already registered: {name}")
        self._tools[name] = Tool(
            spec=ToolSpec(
                name=name,
                description=description,
                input_schema=input_schema,
            ),
            handler=handler,
        )

    def specs(self) -> list[ToolSpec]:
        return [tool.spec for tool in self._tools.values()]

    def execute(self, tool_call: ToolCall) -> str:
        tool = self._tools.get(tool_call.name)
        if tool is None:
            raise UnknownToolError(f"unknown tool: {tool_call.name}")

        try:
            result = tool.handler(**tool_call.arguments)
        except Exception as exc:
            raise ToolExecutionError(f"tool failed: {tool_call.name}: {exc}") from exc

        if isinstance(result, str):
            return result
        return json.dumps(result, ensure_ascii=False, sort_keys=True)


class ToolExecutionError(RuntimeError):
    pass


class UnknownToolError(ToolExecutionError):
    pass
