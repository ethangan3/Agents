import pytest


@pytest.fixture(autouse=True)
def disable_default_trace_recorder(monkeypatch):
    monkeypatch.setenv("MINI_AGENT_TRACE_DISABLED", "1")
