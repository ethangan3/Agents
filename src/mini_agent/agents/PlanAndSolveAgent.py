from .Planner import Planner
from .Executer import Executor
from mini_agent.agents.BaseAgent import AgentRunContext, AgentRunInput, AgentRunResult, BaseAgent


class PlanAndSolveAgent(BaseAgent):
    agent_type = "plan_solve"

    def __init__(
        self,
        llm_client,
        max_steps: int = 5,
        trace_recorder=None,
        trace_enabled: bool = True,
    ):
        """
        初始化智能体，同时创建规划器和执行器实例。
        """
        super().__init__(
            max_steps=max_steps,
            trace_recorder=trace_recorder,
            trace_enabled=trace_enabled,
        )
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)

    def _run(
        self,
        run_input: AgentRunInput,
        context: AgentRunContext,
    ) -> AgentRunResult:
        """
        运行智能体的完整流程:先规划，后执行。
        """
        question = run_input.question
        print(f"\n--- 开始处理问题 ---\n问题: {question}")
        
        # 1. 调用规划器生成计划
        plan = self.planner.plan(question)
        context.add_step(
            thought="Generate a plan before solving the task.",
            action="Plan",
            action_input=question,
            observation=str(plan) if plan else None,
        )
        
        # 检查计划是否成功生成
        if not plan:
            print("\n--- 任务终止 --- \n无法生成有效的行动计划。")
            return super()._build_result(
                context=context,
                answer=None,
                status="failed",
                error="无法生成有效的行动计划。",
            )

        # 2. 按计划项逐步执行，并把每个计划项记录为独立 AgentStep
        print("\n--- 正在执行计划 ---")
        history = ""
        final_answer = ""
        executed_steps = 0

        for index, plan_step in enumerate(plan, start=1):
            if not context.has_step_budget():
                break

            print(f"\n-> 正在执行步骤 {index}/{len(plan)}: {plan_step}")
            step_result = self.executor.execute_step(
                question=question,
                plan=plan,
                history=history,
                current_step=plan_step,
            )

            final_answer = step_result
            history += f"步骤 {index}: {plan_step}\n结果: {step_result}\n\n"
            executed_steps += 1

            context.add_step(
                thought=f"Execute plan step {index}/{len(plan)}.",
                action="Execute",
                action_input=plan_step,
                observation=step_result,
                error=None if step_result else "该计划步骤没有返回有效结果。",
                metadata={
                    "plan_index": index,
                    "total_plan_steps": len(plan),
                },
            )
            print(f"✅ 步骤 {index} 已完成，结果: {step_result}")

        if executed_steps < len(plan):
            error = f"计划共有 {len(plan)} 个执行步骤，已达到最大 AgentStep 数 {context.max_steps}。"
            print(f"\n--- 任务中止 ---\n{error}")
            return super()._build_result(
                context=context,
                answer=str(final_answer) if final_answer else None,
                status="max_steps_exceeded",
                error=error,
                metadata={
                    "plan": plan,
                    "executed_steps": executed_steps,
                    "total_plan_steps": len(plan),
                },
            )
        
        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")
        return super()._build_result(
            context=context,
            answer=str(final_answer) if final_answer else None,
            status="success" if final_answer else "failed",
            error=None if final_answer else "计划执行未生成有效答案。",
            metadata={
                "plan": plan,
                "executed_steps": executed_steps,
                "total_plan_steps": len(plan),
            },
        )
