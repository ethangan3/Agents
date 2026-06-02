import pytest

from mini_agent.tools.general import ToolExecutor, ToolSpec


def test_register_tool_accepts_tool_spec_instance():
    tool = ToolSpec(
        name="Echo",
        description="回显工具",
        func=lambda value: value,
        args_schema={"value": "str"},
    )
    executor = ToolExecutor()

    executor.registerTool(tool)

    assert executor.getTool("Echo") is tool
    assert executor.listTools() == [
        {
            "name": "Echo",
            "description": "回显工具",
            "args_schema": {"value": "str"},
        }
    ]


def test_register_tool_accepts_string_signature():
    executor = ToolExecutor()

    executor.registerTool(
        "Echo",
        "回显工具",
        lambda value: value,
        {"value": "str"},
    )

    tool = executor.getTool("Echo")
    assert isinstance(tool, ToolSpec)
    assert tool.description == "回显工具"

    with pytest.raises(ValueError):
        executor.registerTool("Broken")


def test_register_tool_overwrites_duplicate_name():
    executor = ToolExecutor()

    executor.registerTool("Echo", "旧工具", lambda value: f"old:{value}")
    executor.registerTool("Echo", "新工具", lambda value: f"new:{value}")

    assert len(executor.tools) == 1
    assert executor.executeTool("Echo", "x") == "new:x"


def test_execute_tool_passes_plain_string_to_single_argument_function():
    executor = ToolExecutor()
    executor.registerTool("Echo", "回显工具", lambda value: f"got:{value}")

    result = executor.executeTool("Echo", "input")

    assert result == "got:input"


def test_execute_tool_expands_json_object_string():
    executor = ToolExecutor()

    def weather(city, days):
        return f"{city}:{days}"

    executor.registerTool("Weather", "天气工具", weather)

    result = executor.executeTool("Weather", '{"city": "北京", "days": 3}')

    assert result == "北京:3"


def test_execute_tool_prefers_explicit_kwargs():
    executor = ToolExecutor()
    executor.registerTool("ChooseCity", "城市工具", lambda city: city)

    result = executor.executeTool("ChooseCity", "ignored", city="上海")

    assert result == "上海"


def test_execute_tool_calls_zero_argument_function_without_input():
    executor = ToolExecutor()
    executor.registerTool("Ping", "无参数工具", lambda: "pong")

    result = executor.executeTool("Ping")

    assert result == "pong"


def test_execute_tool_raises_for_missing_tool():
    executor = ToolExecutor()

    with pytest.raises(ValueError, match="Missing"):
        executor.executeTool("Missing", "input")


def test_get_available_tools_formats_human_readable_description():
    executor = ToolExecutor()
    executor.registerTool(
        "Echo",
        "回显工具",
        lambda value: value,
        {"value": "str"},
    )

    result = executor.getAvailableTools()

    assert "- Echo: 回显工具" in result
    assert '"value": "str"' in result
