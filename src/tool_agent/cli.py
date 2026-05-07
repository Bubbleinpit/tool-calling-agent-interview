from __future__ import annotations

import argparse

from .agent import ToolCallingAgent
from .demo_tools import build_demo_registry
from .model import RuleBasedDemoModel


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the demo tool-calling agent.")
    parser.add_argument(
        "prompt",
        nargs="?",
        default="请计算 2 + 3 * 4",
        help="User prompt to send to the agent.",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Print the message trace after the final answer.",
    )
    args = parser.parse_args()

    agent = ToolCallingAgent(
        model=RuleBasedDemoModel(),
        tools=build_demo_registry(),
    )
    result = agent.run(args.prompt)

    print(result.final_answer)

    if args.trace:
        print()
        print("Trace:")
        for message in result.messages:
            suffix = ""
            if message.tool_calls:
                suffix = " " + ", ".join(call.name for call in message.tool_calls)
            if message.name:
                suffix = f" {message.name}"
            print(f"- {message.role}{suffix}: {message.content}")


if __name__ == "__main__":
    main()
