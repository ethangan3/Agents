import pytest
from pydantic import ValidationError

from mini_agent.api.schema import AskRequest, AskResponse
from mini_agent.agents.BaseAgent import AgentStep


def test_ask_request_accepts_question_and_optional_max_steps():
    request = AskRequest(question="今天北京天气怎么样?", max_steps=3)

    assert request.question == "今天北京天气怎么样?"
    assert request.save_flag is False
    assert request.max_steps == 3


def test_ask_request_rejects_empty_question():
    with pytest.raises(ValidationError):
        AskRequest(question="")


def test_ask_response_matches_agent_run_result_shape():
    response = AskResponse(
        run_id="run-1",
        agent_type="react",
        question="问题",
        answer="答案",
        steps=[],
        status="success",
        latency_ms=12,
    )

    dumped = response.model_dump()

    assert dumped["run_id"] == "run-1"
    assert dumped["agent_type"] == "react"
    assert dumped["question"] == "问题"
    assert dumped["steps"] == []
    assert dumped["status"] == "success"
    assert dumped["latency_ms"] == 12


def test_agent_step_serializes_nested_in_response():
    step = AgentStep(
        step_id=1,
        thought="思考",
        action="Search",
        action_input="query",
        observation="result",
        error=None,
    )
    response = AskResponse(
        run_id="run-1",
        agent_type="react",
        question="问题",
        answer="答案",
        steps=[step],
        status="success",
        latency_ms=1,
    )

    dumped = response.model_dump()

    assert dumped["steps"][0]["thought"] == "思考"
    assert dumped["steps"][0]["action"] == "Search"
    assert dumped["steps"][0]["observation"] == "result"
    assert dumped["steps"][0]["error"] is None


def test_max_steps_must_be_positive():
    with pytest.raises(ValidationError):
        AskRequest(question="问题", max_steps=0)
