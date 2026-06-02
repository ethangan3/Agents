from mini_agent.agents.BaseAgent import (
    AgentRunContext,
    AgentRunInput,
    AgentRunResult,
    BaseAgent,
)


class RecordingAgent(BaseAgent):
    agent_type = "recording"

    def __init__(self):
        super().__init__(max_steps=3)
        self.received_input = None

    def _run(
        self,
        run_input: AgentRunInput,
        context: AgentRunContext,
    ) -> AgentRunResult:
        self.received_input = run_input
        context.add_step(action="Answer", observation="ok")
        return self._build_result(
            context=context,
            answer="ok",
            status="success",
            metadata={"agent_meta": "value"},
        )


class ExceptionAgent(BaseAgent):
    agent_type = "exception"

    def _run(
        self,
        run_input: AgentRunInput,
        context: AgentRunContext,
    ) -> AgentRunResult:
        raise RuntimeError("boom")


class MaxStepsAgent(BaseAgent):
    agent_type = "max-steps"

    def _run(
        self,
        run_input: AgentRunInput,
        context: AgentRunContext,
    ) -> AgentRunResult:
        while True:
            context.add_step(action="Loop")


def test_run_normalizes_string_input():
    agent = RecordingAgent()

    result = agent.run("普通问题")

    assert isinstance(agent.received_input, AgentRunInput)
    assert agent.received_input.question == "普通问题"
    assert result.question == "普通问题"


def test_run_returns_common_result_fields():
    result = RecordingAgent().run("问题")

    assert result.run_id
    assert result.agent_type == "recording"
    assert result.question == "问题"
    assert result.status == "success"
    assert len(result.steps) == 1
    assert isinstance(result.latency_ms, int)
    assert result.latency_ms >= 0


def test_run_merges_input_metadata_into_result():
    agent_input = AgentRunInput(
        question="问题",
        metadata={"input_meta": "value"},
    )

    result = RecordingAgent().run(agent_input)

    assert result.metadata["input_meta"] == "value"
    assert result.metadata["agent_meta"] == "value"


def test_run_catches_unhandled_exception():
    result = ExceptionAgent().run("问题")

    assert result.status == "failed"
    assert result.error == "boom"
    assert len(result.steps) == 1
    assert result.steps[0].error == "boom"
    assert result.steps[0].metadata["exception_type"] == "RuntimeError"


def test_run_converts_max_steps_exception_to_result():
    agent = MaxStepsAgent(max_steps=1)

    result = agent.run("问题")

    assert result.status == "max_steps_exceeded"
    assert len(result.steps) == 1
    assert result.steps[0].action == "Loop"
