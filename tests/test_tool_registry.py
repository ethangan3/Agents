import json

from mini_agent.tools import registry


def test_build_default_tools_registers_expected_tool_names():
    tools = registry.build_default_tools()

    tool_names = {tool["name"] for tool in tools.listTools()}

    assert {"Search", "Calculator", "CurrentTime", "HistorySearch", "Todo"} <= tool_names
    assert all(tool["description"] for tool in tools.listTools())
    assert all(tool["parameters"] for tool in tools.listTools())


def test_build_default_registry_lists_tool_specs():
    default_registry = registry.build_default_registry()

    specs = default_registry.list_tools()

    assert {spec.name for spec in specs} >= {
        "Search",
        "Calculator",
        "CurrentTime",
        "HistorySearch",
        "Todo",
    }
    assert all(spec.parameters for spec in specs)


def test_build_default_tools_calculator_points_to_builtin_calculate():
    tools = registry.build_default_tools()

    result = tools.executeTool("Calculator", "1 + 2")

    assert result == "3"


def test_build_default_tools_current_time_is_callable():
    tools = registry.build_default_tools()

    result = tools.executeTool("CurrentTime", "")

    assert result


def test_build_default_tools_history_search_uses_custom_history_path(tmp_path):
    history_path = tmp_path / "custom-history.json"
    history_path.write_text(
        json.dumps([{"question": "项目进度", "answer": "已完成"}], ensure_ascii=False),
        encoding="utf-8",
    )
    tools = registry.build_default_tools(history_path=history_path)

    result = tools.executeTool("HistorySearch", "项目进度")

    assert "项目进度" in result
    assert "已完成" in result


def test_build_default_tools_search_can_be_mocked_without_network(monkeypatch):
    monkeypatch.setattr(registry, "search", lambda query: f"fake:{query}")
    tools = registry.build_default_tools()

    result = tools.execute("Search", "北京天气")

    assert result.status == "success"
    assert result.output == "fake:北京天气"


def test_build_default_tools_todo_tool_splits_items():
    tools = registry.build_default_tools()

    result = tools.execute("Todo", "写测试，更新文档；提交代码")

    assert result.status == "success"
    assert "1. 写测试" in result.output
    assert "3. 提交代码" in result.output
