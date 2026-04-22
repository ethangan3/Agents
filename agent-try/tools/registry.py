from pathlib import Path

from tools.builtin_tools import calculate, current_time, history_search
from tools.general import ToolExecutor
from tools.weather_search import search


def build_default_tools(history_path: str | Path = "chat-history.json") -> ToolExecutor:
    tools = ToolExecutor()

    tools.registerTool(
        "Search",
        "网页搜索工具，适合查询实时信息、事实信息、新闻、天气等模型知识库外的问题。",
        search,
        {"query": "str，搜索关键词或完整问题"}
    )
    tools.registerTool(
        "Calculator",
        "基础数学计算工具，适合加减乘除、乘方、取模等确定性算术。",
        calculate,
        {"expression": "str，数学表达式，例如 12*(3+4)"}
    )
    tools.registerTool(
        "CurrentTime",
        "获取当前本地日期和时间。",
        current_time,
        {"input": "str，可留空"}
    )

    def search_saved_history(query: str) -> str:
        return history_search(query, filename=history_path)

    tools.registerTool(
        "HistorySearch",
        "检索本地保存的对话历史，适合回答用户问到以前聊过什么的问题。",
        search_saved_history,
        {"query": "str，历史记录检索关键词；留空时返回最近记录"}
    )

    return tools
