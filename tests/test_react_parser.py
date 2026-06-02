from mini_agent.agents.Agents import ReActAgent
from mini_agent.tools.general import ToolExecutor


class FakeLLM:
    def think(self, messages, temperature=0):
        return "Action: Finish[done]"


def make_agent() -> ReActAgent:
    return ReActAgent(
        llm_client=FakeLLM(),
        tool_executor=ToolExecutor(),
    )


def test_parse_output_extracts_thought_and_action():
    agent = make_agent()

    thought, action = agent._parse_output("Thought: 需要计算\nAction: Calculator[1 + 2]")

    assert thought == "需要计算"
    assert action == "Calculator[1 + 2]"


def test_parse_output_handles_action_only():
    agent = make_agent()

    thought, action = agent._parse_output("Action: Finish[最终答案]")

    assert thought is None
    assert action == "Finish[最终答案]"


def test_parse_output_strips_observation_from_action():
    agent = make_agent()

    _, action = agent._parse_output(
        "Thought: 调用工具\nAction: Search[北京天气]\nObservation: 晴天"
    )

    assert action == "Search[北京天气]"


def test_parse_action_extracts_tool_name_and_input():
    agent = make_agent()

    tool_name, tool_input = agent._parse_action("Calculator[3 * (2 + 5)]")

    assert tool_name == "Calculator"
    assert tool_input == "3 * (2 + 5)"


def test_parse_action_returns_none_for_invalid_format():
    agent = make_agent()

    tool_name, tool_input = agent._parse_action("无法解析的动作")

    assert tool_name is None
    assert tool_input is None


def test_extract_final_answer_from_finish_brackets():
    agent = make_agent()

    answer = agent._extract_final_answer("Finish[最终答案]")

    assert answer == "最终答案"


def test_extract_final_answer_from_finish_call_style():
    agent = make_agent()

    answer = agent._extract_final_answer('Finish(answer="最终答案")')

    assert answer == "最终答案"
