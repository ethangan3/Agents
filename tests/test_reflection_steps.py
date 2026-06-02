from mini_agent.agents.BaseAgent import AgentRunInput
from mini_agent.agents.ReflectionAgent import ReflectionAgent


class SequenceLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.messages = []

    def think(self, messages, temperature=0):
        self.messages.append(messages)
        if not self.responses:
            return ""
        return self.responses.pop(0)


def make_agent(responses, max_iterations=1) -> ReflectionAgent:
    return ReflectionAgent(
        llm_client=SequenceLLM(responses),
        max_iterations=max_iterations,
    )


def test_reflection_records_generate_step():
    agent = make_agent(["初始答案"], max_iterations=0)

    result = agent.run("任务")

    assert result.status == "success"
    assert len(result.steps) == 1
    assert result.steps[0].action == "Generate"
    assert result.steps[0].observation == "初始答案"


def test_reflection_records_reflect_and_refine_steps():
    agent = make_agent(
        ["初始答案", "需要补充边界条件", "优化后答案"],
        max_iterations=1,
    )

    result = agent.run("任务")

    assert result.status == "success"
    assert [step.action for step in result.steps] == ["Generate", "Reflect", "Refine"]
    assert result.steps[1].observation == "需要补充边界条件"
    assert result.steps[2].observation == "优化后答案"
    assert result.answer == "优化后答案"


def test_reflection_stops_when_feedback_says_no_improvement_needed():
    agent = make_agent(["初始答案", "无需改进"], max_iterations=3)

    result = agent.run("任务")

    assert result.status == "success"
    assert [step.action for step in result.steps] == ["Generate", "Reflect"]
    assert result.metadata["stopped_by_feedback"] is True


def test_reflection_respects_max_steps():
    agent = make_agent(["初始答案", "需要继续优化"], max_iterations=3)

    result = agent.run(AgentRunInput(question="任务", max_steps=2))

    assert result.status == "max_steps_exceeded"
    assert len(result.steps) == 2
    assert [step.action for step in result.steps] == ["Generate", "Reflect"]


def test_reflection_metadata_records_iterations():
    agent = make_agent(
        ["初始答案", "需要优化", "优化后答案", "无需改进"],
        max_iterations=2,
    )

    result = agent.run("任务")

    assert result.metadata["completed_iterations"] == 2
    assert result.metadata["max_iterations"] == 2
    assert result.metadata["stopped_by_feedback"] is True
