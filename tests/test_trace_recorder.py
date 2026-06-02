from mini_agent.agents.BaseAgent import (
    AgentRunContext,
    AgentRunInput,
    AgentRunResult,
    AgentStep,
    BaseAgent,
)
from mini_agent.trace import TraceRecorder


def make_result(run_id: str, question: str = "问题") -> AgentRunResult:
    return AgentRunResult(
        run_id=run_id,
        agent_type="react",
        question=question,
        answer="答案",
        steps=[
            AgentStep(
                step_id=1,
                thought="思考",
                action="Calculator",
                action_input="1 + 2",
                observation="3",
            )
        ],
        status="success",
        latency_ms=12,
    )


def test_trace_recorder_records_and_gets_run_by_id(tmp_path):
    recorder = TraceRecorder(tmp_path / "runs.json")
    result = make_result("run-1")

    trace = recorder.record(result)

    loaded = recorder.get_run("run-1")
    assert trace.run_id == "run-1"
    assert loaded is not None
    assert loaded.question == "问题"
    assert loaded.steps[0].observation == "3"
    assert loaded.created_at


def test_trace_recorder_lists_recent_runs_newest_first(tmp_path):
    recorder = TraceRecorder(tmp_path / "runs.json")

    recorder.record(make_result("run-1", "问题1"))
    recorder.record(make_result("run-2", "问题2"))
    recorder.record(make_result("run-3", "问题3"))

    recent = recorder.list_recent(limit=2)

    assert [trace.run_id for trace in recent] == ["run-3", "run-2"]


def test_trace_recorder_replaces_existing_run_id(tmp_path):
    recorder = TraceRecorder(tmp_path / "runs.json")

    recorder.record(make_result("same-run", "旧问题"))
    recorder.record(make_result("same-run", "新问题"))

    recent = recorder.list_recent(limit=10)
    assert len(recent) == 1
    assert recent[0].question == "新问题"


class TraceableAgent(BaseAgent):
    agent_type = "traceable"

    def __init__(self, recorder):
        super().__init__(max_steps=3, trace_recorder=recorder)

    def _run(
        self,
        run_input: AgentRunInput,
        context: AgentRunContext,
    ) -> AgentRunResult:
        context.add_step(action="Answer", observation="ok")
        return self._build_result(context=context, answer="ok", status="success")


class FailingTraceableAgent(BaseAgent):
    agent_type = "failing-traceable"

    def __init__(self, recorder):
        super().__init__(max_steps=3, trace_recorder=recorder)

    def _run(
        self,
        run_input: AgentRunInput,
        context: AgentRunContext,
    ) -> AgentRunResult:
        raise RuntimeError("boom")


def test_base_agent_records_success_trace(tmp_path):
    recorder = TraceRecorder(tmp_path / "runs.json")
    agent = TraceableAgent(recorder)

    result = agent.run("问题")

    trace = recorder.get_run(result.run_id)
    assert trace is not None
    assert trace.status == "success"
    assert trace.answer == "ok"
    assert trace.steps[0].observation == "ok"


def test_base_agent_records_failed_trace(tmp_path):
    recorder = TraceRecorder(tmp_path / "runs.json")
    agent = FailingTraceableAgent(recorder)

    result = agent.run("问题")

    trace = recorder.get_run(result.run_id)
    assert trace is not None
    assert trace.status == "failed"
    assert trace.error == "boom"
    assert trace.steps[0].error == "boom"
