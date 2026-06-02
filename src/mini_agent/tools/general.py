from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from inspect import signature
from typing import Any

from mini_agent.tools.base import BaseTool, ToolResult, ToolSpec


class FunctionTool(BaseTool):
    """将普通函数包装成统一工具对象。"""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable[..., Any],
        parameters: dict[str, Any] | None = None,
    ):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters or {"input": "str"}

    def run(self, tool_input: Any = "", **kwargs: Any) -> str:
        if kwargs:
            return str(self.func(**kwargs))

        if isinstance(tool_input, str):
            stripped_input = tool_input.strip()
            if stripped_input.startswith("{") and stripped_input.endswith("}"):
                try:
                    json_input = json.loads(stripped_input)
                    if isinstance(json_input, dict):
                        return str(self.func(**json_input))
                except json.JSONDecodeError:
                    pass

        parameters = signature(self.func).parameters
        if len(parameters) == 0:
            return str(self.func())
        return str(self.func(tool_input))


class ToolRegistry:
    """工具注册中心，只负责保存、查询和列出工具。"""

    def __init__(self, tools: Iterable[BaseTool] | None = None):
        self.tools: dict[str, BaseTool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: BaseTool) -> BaseTool:
        if not isinstance(tool, BaseTool):
            raise TypeError("ToolRegistry.register 只接受 BaseTool 实例。")
        self.tools[tool.name] = tool
        return tool

    def get(self, name: str) -> BaseTool | None:
        return self.tools.get(name)

    def list_tools(self) -> list[ToolSpec]:
        return [tool.spec() for tool in self.tools.values()]


class ToolExecutor:
    """统一工具执行器，执行失败时返回结构化 ToolResult。"""

    def __init__(self, registry: ToolRegistry | None = None):
        self.registry = registry or ToolRegistry()

    @property
    def tools(self) -> dict[str, BaseTool]:
        return self.registry.tools

    def registerTool(
        self,
        tool_new: BaseTool | str,
        description: str | None = None,
        func: Callable[..., Any] | None = None,
        args_schema: dict[str, Any] | None = None,
    ) -> BaseTool:
        """兼容旧代码的注册入口。新代码优先使用 ToolRegistry.register。"""
        if isinstance(tool_new, str):
            if description is None or func is None:
                raise ValueError("使用字符串注册工具时，必须提供 description 和 func。")
            tool_new = FunctionTool(
                name=tool_new,
                description=description,
                func=func,
                parameters=args_schema,
            )

        if not isinstance(tool_new, BaseTool):
            raise TypeError("registerTool 只接受 BaseTool 实例或字符串函数注册参数。")

        return self.registry.register(tool_new)

    def getTool(self, name: str) -> BaseTool | None:
        """兼容旧代码的工具查询入口。"""
        return self.registry.get(name)

    def execute(self, name: str, tool_input: Any = None, **kwargs: Any) -> ToolResult:
        tool = self.registry.get(name)
        if tool is None:
            return ToolResult(
                status="failed",
                error=f"Tool not found: {name}",
                metadata={"tool_name": name},
            )

        try:
            if isinstance(tool, FunctionTool):
                output = tool.run(tool_input, **kwargs)
            elif kwargs:
                raise ValueError(f"Tool '{name}' does not accept keyword arguments.")
            else:
                output = tool.run("" if tool_input is None else tool_input)
        except Exception as exc:
            return ToolResult(
                status="failed",
                error=f"{type(exc).__name__}: {exc}",
                metadata={
                    "tool_name": name,
                    "exception_type": type(exc).__name__,
                },
            )

        return ToolResult(
            status="success",
            output=str(output),
            metadata={"tool_name": name},
        )

    def executeTool(self, name: str, tool_input: Any = None, **kwargs: Any) -> Any:
        """兼容旧代码的执行入口。失败时仍抛 ValueError，推荐新代码使用 execute。"""
        result = self.execute(name, tool_input, **kwargs)
        if not result.is_success:
            raise ValueError(result.error)
        return result.output

    def getAvailableTools(self) -> str:
        tool_lines = []
        for spec in self.registry.list_tools():
            schema = json.dumps(spec.parameters, ensure_ascii=False)
            tool_lines.append(f"- {spec.name}: {spec.description} 输入参数: {schema}")
        return "\n".join(tool_lines)

    def listTools(self) -> list[dict[str, Any]]:
        """兼容旧 API，同时暴露 parameters 字段给新调用方。"""
        return [
            {
                "name": spec.name,
                "description": spec.description,
                "parameters": spec.parameters,
                "args_schema": spec.parameters,
            }
            for spec in self.registry.list_tools()
        ]


__all__ = [
    "BaseTool",
    "FunctionTool",
    "ToolExecutor",
    "ToolRegistry",
    "ToolResult",
    "ToolSpec",
]
