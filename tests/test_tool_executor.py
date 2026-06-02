import pytest

from mini_agent.tools.base import BaseTool
from mini_agent.tools.general import ToolExecutor, ToolRegistry


class EchoTool(BaseTool):
    name = "Echo"
    description = "回显工具"
    parameters = {"value": "str"}

    def run(self, tool_input=""):
        return f"echo:{tool_input}"


def test_registry_registers_and_lists_base_tool():
    registry = ToolRegistry()
    tool = EchoTool()

    registry.register(tool)

    assert registry.get("Echo") is tool
    assert registry.list_tools()[0].name == "Echo"
    assert registry.list_tools()[0].parameters == {"value": "str"}


def test_register_tool_accepts_string_signature_for_legacy_code():
    executor = ToolExecutor()

    executor.registerTool(
        "Echo",
        "回显工具",
        lambda value: value,
        {"value": "str"},
    )

    tool = executor.getTool("Echo")
    assert tool.name == "Echo"
    assert tool.description == "回显工具"

    with pytest.raises(ValueError):
        executor.registerTool("Broken")


def test_register_tool_overwrites_duplicate_name():
    executor = ToolExecutor()

    executor.registerTool("Echo", "旧工具", lambda value: f"old:{value}")
    executor.registerTool("Echo", "新工具", lambda value: f"new:{value}")

    assert len(executor.tools) == 1
    assert executor.execute("Echo", "x").output == "new:x"


def test_execute_returns_success_result_for_base_tool():
    executor = ToolExecutor(ToolRegistry([EchoTool()]))

    result = executor.execute("Echo", "input")

    assert result.status == "success"
    assert result.output == "echo:input"
    assert result.error is None


def test_execute_expands_json_object_string_for_function_tool():
    executor = ToolExecutor()

    def weather(city, days):
        return f"{city}:{days}"

    executor.registerTool("Weather", "天气工具", weather)

    result = executor.execute("Weather", '{"city": "北京", "days": 3}')

    assert result.status == "success"
    assert result.output == "北京:3"


def test_execute_prefers_explicit_kwargs_for_function_tool():
    executor = ToolExecutor()
    executor.registerTool("ChooseCity", "城市工具", lambda city: city)

    result = executor.execute("ChooseCity", "ignored", city="上海")

    assert result.status == "success"
    assert result.output == "上海"


def test_execute_calls_zero_argument_function_without_input():
    executor = ToolExecutor()
    executor.registerTool("Ping", "无参数工具", lambda: "pong")

    result = executor.execute("Ping")

    assert result.status == "success"
    assert result.output == "pong"


def test_execute_returns_structured_error_for_missing_tool():
    executor = ToolExecutor()

    result = executor.execute("Missing", "input")

    assert result.status == "failed"
    assert result.error == "Tool not found: Missing"


def test_execute_tool_legacy_wrapper_raises_for_failed_result():
    executor = ToolExecutor()

    with pytest.raises(ValueError, match="Tool not found: Missing"):
        executor.executeTool("Missing", "input")


def test_get_available_tools_formats_human_readable_description():
    executor = ToolExecutor(ToolRegistry([EchoTool()]))

    result = executor.getAvailableTools()

    assert "- Echo: 回显工具" in result
    assert '"value": "str"' in result
