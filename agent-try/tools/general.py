import json
from collections.abc import Callable
from dataclasses import dataclass, field
from inspect import signature
from typing import Any


@dataclass
class ToolSpec:
    name: str
    description: str
    func: Callable[..., Any]
    args_schema: dict[str, Any] = field(default_factory=lambda: {"input": "str"})

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)


class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具。
    """
    def __init__(self):
        self.tools: dict[str, ToolSpec] = {}

    def registerTool(
        self,
        tool_new: ToolSpec | str,
        description: str | None = None,
        func: Callable[..., Any] | None = None,
        args_schema: dict[str, Any] | None = None
    ):
        """
        向工具箱中注册一个新工具。
        """
        if isinstance(tool_new, str):
            if description is None or func is None:
                raise ValueError("使用字符串注册工具时，必须提供 description 和 func。")
            tool_new = ToolSpec(
                name=tool_new,
                description=description,
                func=func,
                args_schema=args_schema or {"input": "str"}
            )

        if tool_new.name in self.tools:
            print(f"警告:工具 '{tool_new.name}' 已存在，将被覆盖。")
        self.tools[tool_new.name] = tool_new
        print(f"工具 '{tool_new.name}' 已注册。")

    def getTool(self, name: str) -> ToolSpec | None:
        """
        根据名称获取一个工具的执行函数。
        """
        return self.tools.get(name)

    def executeTool(self, name: str, tool_input: Any = None, **kwargs) -> Any:
        tool = self.getTool(name)
        if not tool:
            raise ValueError(f"工具 '{name}' 未找到。")

        if kwargs:
            return tool.func(**kwargs)

        if isinstance(tool_input, str):
            stripped_input = tool_input.strip()
            if stripped_input.startswith("{") and stripped_input.endswith("}"):
                try:
                    json_input = json.loads(stripped_input)
                    if isinstance(json_input, dict):
                        return tool.func(**json_input)
                except json.JSONDecodeError:
                    pass

        parameters = signature(tool.func).parameters
        if len(parameters) == 0:
            return tool.func()
        return tool.func(tool_input)

    def getAvailableTools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串。
        """
        tool_lines = []
        for tool in self.tools.values():
            schema = json.dumps(tool.args_schema, ensure_ascii=False)
            tool_lines.append(f"- {tool.name}: {tool.description} 输入参数: {schema}")
        return "\n".join(tool_lines)

    def listTools(self) -> list[dict[str, Any]]:
        """
        获取所有可用工具的结构化信息。
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "args_schema": tool.args_schema,
            }
            for tool in self.tools.values()
        ]
