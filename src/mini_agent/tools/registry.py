from pathlib import Path

from mini_agent.tools.builtin import (
    CalculatorTool,
    CurrentTimeTool,
    HistorySearchTool,
    SearchTool,
    TodoTool,
)
from mini_agent.tools.general import ToolExecutor, ToolRegistry
from mini_agent.tools.weather_search import search


def build_default_registry(history_path: str | Path = "chat-history.json") -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(SearchTool(search_func=search))
    registry.register(CalculatorTool())
    registry.register(CurrentTimeTool())
    registry.register(HistorySearchTool(history_path=history_path))
    registry.register(TodoTool())
    return registry


def build_default_tools(history_path: str | Path = "chat-history.json") -> ToolExecutor:
    return ToolExecutor(registry=build_default_registry(history_path=history_path))
