from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from mini_agent.tools.base import BaseTool
from mini_agent.tools.builtin_tools import calculate, current_time, history_search
from mini_agent.tools.weather_search import search


class CalculatorTool(BaseTool):
    name = "Calculator"
    description = "基础数学计算工具，适合加减乘除、乘方、取模等确定性算术。"
    parameters = {"expression": "str，数学表达式，例如 12*(3+4)"}

    def run(self, tool_input: Any = "") -> str:
        return calculate(str(tool_input))


class CurrentTimeTool(BaseTool):
    name = "CurrentTime"
    description = "获取当前本地日期和时间。"
    parameters = {"input": "str，可留空"}

    def run(self, tool_input: Any = "") -> str:
        return current_time(str(tool_input or ""))


class SearchTool(BaseTool):
    name = "Search"
    description = "网页搜索工具，适合查询实时信息、事实信息、新闻、天气等模型知识库外的问题。"
    parameters = {"query": "str，搜索关键词或完整问题"}

    def __init__(self, search_func=search):
        self.search_func = search_func

    def run(self, tool_input: Any = "") -> str:
        return self.search_func(str(tool_input))


class HistorySearchTool(BaseTool):
    name = "HistorySearch"
    description = "检索本地保存的对话历史，适合回答用户问到以前聊过什么的问题。"
    parameters = {"query": "str，历史记录检索关键词；留空时返回最近记录"}

    def __init__(self, history_path: str | Path = "chat-history.json"):
        self.history_path = history_path

    def run(self, tool_input: Any = "") -> str:
        return history_search(str(tool_input or ""), filename=self.history_path)


class TodoTool(BaseTool):
    name = "Todo"
    description = "将用户输入拆解为简洁的待办事项列表。"
    parameters = {"text": "str，需要拆解的任务描述，可用换行、逗号或分号分隔"}

    def run(self, tool_input: Any = "") -> str:
        text = str(tool_input or "").strip()
        if not text:
            return "没有可拆解的待办事项。"

        items = [
            item.strip(" \t-")
            for item in re.split(r"[\n,，;；]+", text)
            if item.strip(" \t-")
        ]
        if not items:
            return "没有可拆解的待办事项。"

        return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))
