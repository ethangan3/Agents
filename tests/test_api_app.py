from fastapi.testclient import TestClient

from mini_agent.agents.BaseAgent import AgentRunResult
from mini_agent.api import app as api_app
from mini_agent.trace import TraceRecorder


client = TestClient(api_app.app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_v1_tools_returns_registered_tools():
    response = client.get("/v1/tools")

    assert response.status_code == 200
    tool_names = {tool["name"] for tool in response.json()["tools"]}
    assert {"Calculator", "CurrentTime", "HistorySearch", "Search", "Todo"} <= tool_names


def test_v1_run_react_can_be_called_without_real_llm(monkeypatch):
    class FakeAgent:
        def run(self, agent_input):
            return AgentRunResult(
                run_id="run-1",
                agent_type="react",
                question=agent_input.question,
                answer="ok",
                steps=[],
                status="success",
                latency_ms=1,
            )

    monkeypatch.setattr(api_app, "_build_agent", lambda agent_type: FakeAgent())

    response = client.post(
        "/v1/agents/react/run",
        json={"question": "问题", "max_steps": 3},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "ok"
    assert response.json()["agent_type"] == "react"


def test_v1_runs_can_query_trace_by_run_id(monkeypatch, tmp_path):
    trace_path = tmp_path / "runs.json"
    recorder = TraceRecorder(trace_path)
    recorder.record(
        AgentRunResult(
            run_id="run-1",
            agent_type="react",
            question="问题",
            answer="ok",
            steps=[],
            status="success",
            latency_ms=1,
        )
    )
    monkeypatch.setenv("MINI_AGENT_TRACE_PATH", str(trace_path))

    response = client.get("/v1/runs/run-1")

    assert response.status_code == 200
    assert response.json()["run_id"] == "run-1"


def test_v1_runs_returns_recent_runs(monkeypatch, tmp_path):
    trace_path = tmp_path / "runs.json"
    recorder = TraceRecorder(trace_path)
    for index in range(3):
        recorder.record(
            AgentRunResult(
                run_id=f"run-{index}",
                agent_type="react",
                question=f"问题 {index}",
                answer="ok",
                steps=[],
                status="success",
                latency_ms=1,
            )
        )
    monkeypatch.setenv("MINI_AGENT_TRACE_PATH", str(trace_path))

    response = client.get("/v1/runs?limit=2")

    assert response.status_code == 200
    assert [run["run_id"] for run in response.json()["runs"]] == ["run-2", "run-1"]
