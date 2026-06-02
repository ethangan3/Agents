import pytest

from mini_agent.agents.BaseAgent import AgentRunContext, MaxStepsExceeded


def make_context(max_steps: int = 3) -> AgentRunContext:
    return AgentRunContext(
        run_id="run-1",
        agent_type="dummy",
        question="测试问题",
        max_steps=max_steps,
    )


def test_add_step_assigns_incremental_step_ids():
    context = make_context(max_steps=3)

    first = context.add_step(action="First")
    second = context.add_step(action="Second")
    third = context.add_step(action="Third")

    assert [first.step_id, second.step_id, third.step_id] == [1, 2, 3]
    assert [step.action for step in context.steps] == ["First", "Second", "Third"]


def test_add_step_preserves_step_fields():
    context = make_context()

    step = context.add_step(
        thought="需要调用工具",
        action="Calculator",
        action_input="1 + 2",
        observation="3",
        error=None,
        metadata={"source": "unit-test"},
    )

    assert step.thought == "需要调用工具"
    assert step.action == "Calculator"
    assert step.action_input == "1 + 2"
    assert step.observation == "3"
    assert step.error is None
    assert step.metadata == {"source": "unit-test"}


def test_add_step_raises_when_max_steps_exceeded():
    context = make_context(max_steps=1)

    context.add_step(action="Only")

    with pytest.raises(MaxStepsExceeded):
        context.add_step(action="Overflow")

    assert len(context.steps) == 1
    assert context.steps[0].action == "Only"


def test_has_step_budget_reflects_remaining_capacity():
    context = make_context(max_steps=2)

    assert context.has_step_budget() is True

    context.add_step(action="One")
    assert context.has_step_budget() is True

    context.add_step(action="Two")
    assert context.has_step_budget() is False
