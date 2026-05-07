from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ToolCall:
    """A model request to call a named tool with JSON-like arguments."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class Message:
    role: Role
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role="system", content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role="user", content=content)

    @classmethod
    def assistant(
        cls,
        content: str,
        tool_calls: list[ToolCall] | None = None,
    ) -> "Message":
        return cls(role="assistant", content=content, tool_calls=tool_calls or [])

    @classmethod
    def tool(cls, tool_call_id: str, name: str, content: str) -> "Message":
        return cls(
            role="tool",
            content=content,
            tool_call_id=tool_call_id,
            name=name,
        )
