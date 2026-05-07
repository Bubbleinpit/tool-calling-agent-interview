from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Sequence

from .messages import Message
from .model import ChatModel
from .tools import ToolExecutionError, ToolRegistry


@dataclass
class AgentResult:
    final_answer: str
    messages: list[Message]


class ToolCallingAgent:
    """A small agent loop that handles model-requested tool calls."""

    def __init__(
        self,
        model: ChatModel,
        tools: ToolRegistry,
        system_prompt: str = "You are a helpful assistant. Use tools when needed.",
        max_turns: int = 8,
    ) -> None:
        self.model = model
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_turns = max_turns

    def run(self, user_input: str, history: Sequence[Message] | None = None) -> AgentResult:
        messages = [Message.system(self.system_prompt)]
        if history:
            messages.extend(history)
        messages.append(Message.user(user_input))

        for _ in range(self.max_turns):
            assistant_message = self.model.complete(messages, self.tools.specs())
            messages.append(assistant_message)

            if not assistant_message.tool_calls:
                return AgentResult(
                    final_answer=assistant_message.content,
                    messages=messages,
                )

            for tool_call in assistant_message.tool_calls:
                try:
                    tool_result = self.tools.execute(tool_call)
                except ToolExecutionError as exc:
                    tool_result = json.dumps(
                        {"error": str(exc), "tool": tool_call.name},
                        ensure_ascii=False,
                        sort_keys=True,
                    )

                messages.append(
                    Message.tool(
                        tool_call_id=tool_call.id,
                        name=tool_call.name,
                        content=tool_result,
                    )
                )

        raise RuntimeError("agent stopped after reaching max_turns")
