from mini_agent.agents.BaseAgent import AgentRunInput
from mini_agent.agents.PlanAndSolveAgent import PlanAndSolveAgent


class FakePlanner:
    def __init__(self, plan):
        self.plan_response = plan
        self.questions = []

    def plan(self, question):
        self.questions.append(question)
        return self.plan_response


class FakeExecutor:
    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def execute_step(self, question, plan, history, current_step):
        self.calls.append(
            {
                "question": question,
                "plan": plan,
                "history": history,
                "current_step": current_step,
            }
        )
        return self.results.pop(0)


def make_agent(plan, results, max_steps=5) -> PlanAndSolveAgent:
    agent = PlanAndSolveAgent(llm_client=object(), max_steps=max_steps)
    agent.planner = FakePlanner(plan)
    agent.executor = FakeExecutor(results)
    return agent


def test_plan_solve_records_plan_step_first():
    agent = make_agent(["第一步"], ["完成"])

    result = agent.run("问题")

    assert result.steps[0].action == "Plan"
    assert result.steps[0].action_input == "问题"
    assert "第一步" in result.steps[0].observation


def test_plan_solve_records_each_plan_item_as_execute_step():
    plan = ["拆解问题", "执行计算", "整理答案"]
    agent = make_agent(plan, ["拆解完成", "计算完成", "最终答案"])

    result = agent.run("问题")

    execute_steps = [step for step in result.steps if step.action == "Execute"]
    assert len(execute_steps) == 3
    assert [step.action_input for step in execute_steps] == plan
    assert [step.observation for step in execute_steps] == ["拆解完成", "计算完成", "最终答案"]


def test_plan_solve_answer_uses_last_execution_result():
    agent = make_agent(["第一步", "第二步"], ["中间结果", "最终答案"])

    result = agent.run("问题")

    assert result.status == "success"
    assert result.answer == "最终答案"


def test_plan_solve_returns_failed_when_plan_is_empty():
    agent = make_agent([], [])

    result = agent.run("问题")

    assert result.status == "failed"
    assert len(result.steps) == 1
    assert result.steps[0].action == "Plan"
    assert result.error == "无法生成有效的行动计划。"


def test_plan_solve_respects_global_max_steps():
    agent = make_agent(
        ["第一步", "第二步", "第三步"],
        ["结果1", "结果2", "结果3"],
        max_steps=2,
    )

    result = agent.run(AgentRunInput(question="问题", max_steps=2))

    assert result.status == "max_steps_exceeded"
    assert len(result.steps) == 2
    assert result.metadata["executed_steps"] == 1
    assert result.metadata["total_plan_steps"] == 3
