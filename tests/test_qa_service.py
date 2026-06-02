from mini_agent.agents.Agents import ReActAgent
from mini_agent.agents.BaseAgent import AgentRunInput
from mini_agent.services import qa_service


class FakeLLM:
    """用于验证 build_agent 依赖注入的假 LLM。"""


class FakeTools:
    """用于验证 build_agent 依赖注入的假工具集合。"""


class FakeResponse:
    def __init__(self, payload=None):
        self.payload = payload or {"answer": "ok"}

    def model_dump(self):
        return self.payload


def test_build_agent_wires_llm_tools_and_max_steps(monkeypatch):
    calls = {}
    fake_tools = FakeTools()

    def fake_build_default_tools(history_path):
        calls["history_path"] = history_path
        return fake_tools

    monkeypatch.setattr(qa_service, "HelloAgentsLLM", FakeLLM)
    monkeypatch.setattr(qa_service, "build_default_tools", fake_build_default_tools)

    agent = qa_service.build_agent(save_path="tmp.json", max_steps=8)

    assert isinstance(agent, ReActAgent)
    assert isinstance(agent.llm_client, FakeLLM)
    assert agent.tool_executor is fake_tools
    assert agent.max_steps == 8
    assert calls["history_path"] == "tmp.json"


def test_ask_agent_passes_question_and_max_steps_to_agent_run(monkeypatch):
    calls = {}

    class FakeAgent:
        def run(self, agent_input):
            calls["agent_input"] = agent_input
            return FakeResponse()

    monkeypatch.setattr(qa_service, "build_agent", lambda save_path: FakeAgent())

    qa_service.ask_agent("问题", save_flag=False, max_steps=3)

    assert isinstance(calls["agent_input"], AgentRunInput)
    assert calls["agent_input"].question == "问题"
    assert calls["agent_input"].max_steps == 3


def test_ask_agent_saves_response_when_save_flag_true(monkeypatch):
    saved = {}
    response = FakeResponse({"answer": "ok"})

    class FakeAgent:
        def run(self, agent_input):
            return response

    monkeypatch.setattr(qa_service, "build_agent", lambda save_path: FakeAgent())

    def fake_save_history(history, filename):
        saved["history"] = history
        saved["filename"] = filename

    monkeypatch.setattr(qa_service, "save_history", fake_save_history)

    qa_service.ask_agent("问题", save_flag=True, save_path="history.json")

    assert saved["history"] == {"answer": "ok"}
    assert saved["filename"] == "history.json"


def test_ask_agent_does_not_save_when_save_flag_false(monkeypatch):
    saved = {"called": False}

    class FakeAgent:
        def run(self, agent_input):
            return FakeResponse()

    monkeypatch.setattr(qa_service, "build_agent", lambda save_path: FakeAgent())
    monkeypatch.setattr(
        qa_service,
        "save_history",
        lambda history, filename: saved.update(called=True),
    )

    qa_service.ask_agent("问题", save_flag=False)

    assert saved["called"] is False


def test_ask_agent_returns_agent_response_directly(monkeypatch):
    response = FakeResponse()

    class FakeAgent:
        def run(self, agent_input):
            return response

    monkeypatch.setattr(qa_service, "build_agent", lambda save_path: FakeAgent())

    result = qa_service.ask_agent("问题", save_flag=False)

    assert result is response
