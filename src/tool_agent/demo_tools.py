from __future__ import annotations

import ast
import operator
import time
from typing import Any

from .tools import ToolRegistry


WEATHER = {
    "Beijing": {"condition": "clear", "temperature_c": 23},
    "Shanghai": {"condition": "cloudy", "temperature_c": 25},
    "Shenzhen": {"condition": "rain", "temperature_c": 28},
    "Hangzhou": {"condition": "breezy", "temperature_c": 24},
}


DEFAULT_WEATHER_LATENCY_SECONDS = 0.2


def build_demo_registry(
    weather_latency: float = DEFAULT_WEATHER_LATENCY_SECONDS,
) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        name="calculator",
        description="Evaluate a basic arithmetic expression.",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic expression such as '2 + 3 * 4'.",
                }
            },
            "required": ["expression"],
        },
        handler=calculator,
    )

    def get_weather_with_latency(city: str) -> dict[str, Any]:
        # Simulates a slow remote call. This latency is the whole reason
        # running get_weather on the agent's main loop is a blocking problem.
        time.sleep(weather_latency)
        return get_weather(city)

    registry.register(
        name="get_weather",
        description="Look up demo weather for a supported city.",
        input_schema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "One of Beijing, Shanghai, Shenzhen, Hangzhou.",
                }
            },
            "required": ["city"],
        },
        handler=get_weather_with_latency,
    )
    return registry


def calculator(expression: str) -> dict[str, Any]:
    return {
        "expression": expression,
        "result": _safe_eval(expression),
    }


def get_weather(city: str) -> dict[str, Any]:
    if city not in WEATHER:
        return {
            "city": city,
            "error": "unsupported city",
            "supported_cities": sorted(WEATHER),
        }
    return {"city": city, **WEATHER[city]}


def _safe_eval(expression: str) -> int | float:
    node = ast.parse(expression, mode="eval")
    return _eval_node(node.body)


def _eval_node(node: ast.AST) -> int | float:
    binary_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    unary_ops = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in binary_ops:
        return binary_ops[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
        return unary_ops[type(node.op)](_eval_node(node.operand))

    raise ValueError(f"unsupported expression: {expression_preview(node)}")


def expression_preview(node: ast.AST) -> str:
    return ast.dump(node, include_attributes=False)
