from mini_agent.agents.BaseAgent import AgentRunInput
from mini_agent.agents.Agents import ReActAgent
from mini_agent.tools.general import ToolExecutor


class SequenceLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.messages = []

    def think(self, messages, temperature=0):
        self.messages.append(messages)
        return self.responses.pop(0)


def make_tools() -> ToolExecutor:
    tools = ToolExecutor()
    tools.registerTool(
        "Calculator",
        "计算器",
        lambda expression: {"1 + 2": "3", "1 + 1": "2"}[expression],
    )
    return tools


def test_react_returns_success_when_llm_outputs_final_answer():
    llm = SequenceLLM(["Thought: 已完成\nFinal Answer: 最终答案"])
    agent = ReActAgent(llm_client=llm, tool_executor=ToolExecutor())

    result = agent.run("问题")

    assert result.status == "success"
    assert result.answer == "最终答案"
    assert len(result.steps) == 1
    assert result.steps[0].action == "Finish"
    assert result.steps[0].action_input == "最终答案"


def test_react_still_supports_legacy_finish_action():
    llm = SequenceLLM(["Thought: 已完成\nAction: Finish[最终答案]"])
    agent = ReActAgent(llm_client=llm, tool_executor=ToolExecutor())

    result = agent.run("问题")

    assert result.status == "success"
    assert result.answer == "最终答案"


def test_react_executes_tool_and_records_observation():
    llm = SequenceLLM(
        [
            "Thought: 需要计算\nAction: Calculator[1 + 2]",
            "Thought: 得到结果\nAction: Finish[答案是3]",
        ]
    )
    agent = ReActAgent(llm_client=llm, tool_executor=make_tools())

    result = agent.run("1 + 2 等于多少?")

    assert result.status == "success"
    assert result.steps[0].action == "Calculator"
    assert result.steps[0].action_input == "1 + 2"
    assert result.steps[0].observation == "3"
    assert result.answer == "答案是3"


def test_react_records_tool_error_as_step_error():
    llm = SequenceLLM(["Thought: 调用未知工具\nAction: MissingTool[input]"])
    agent = ReActAgent(
        llm_client=llm,
        tool_executor=ToolExecutor(),
        max_steps=1,
    )

    result = agent.run("问题")

    assert len(result.steps) == 1
    assert result.steps[0].action == "MissingTool"
    assert result.steps[0].error is not None
    assert "工具调用失败" in result.steps[0].observation


def test_react_can_continue_after_tool_error_observation():
    llm = SequenceLLM(
        [
            "Thought: 先试一个不存在的工具\nAction: MissingTool[input]",
            "Thought: 已经看到工具失败\nFinal Answer: 工具不可用",
        ]
    )
    agent = ReActAgent(
        llm_client=llm,
        tool_executor=ToolExecutor(),
        max_steps=2,
    )

    result = agent.run("问题")

    assert result.status == "success"
    assert result.answer == "工具不可用"
    assert result.steps[0].error == "Tool not found: MissingTool"
    assert "Tool not found: MissingTool" in llm.messages[1][0]["content"]


def test_react_returns_failed_when_llm_response_is_empty():
    llm = SequenceLLM([""])
    agent = ReActAgent(llm_client=llm, tool_executor=ToolExecutor())

    result = agent.run("问题")

    assert result.status == "failed"
    assert "LLM" in result.error
    assert result.steps[0].error == result.error


def test_react_respects_max_steps():
    llm = SequenceLLM(["Thought: 继续调用\nAction: Calculator[1 + 1]"])
    agent = ReActAgent(
        llm_client=llm,
        tool_executor=make_tools(),
        max_steps=1,
    )

    result = agent.run(AgentRunInput(question="问题", max_steps=1))

    assert result.status == "max_steps_exceeded"
    assert len(result.steps) == 1
