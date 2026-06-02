from .Memory import Memory
from .prompts.initial_prompt import INITIAL_PROMPT_TEMPLATE
from .prompts.reflect_prompt import REFLECT_PROMPT_TEMPLATE
from .prompts.refine_prompt import REFINE_PROMPT_TEMPLATE
from mini_agent.agents.BaseAgent import AgentRunContext, AgentRunInput, AgentRunResult, BaseAgent


class ReflectionAgent(BaseAgent):
    agent_type = "reflection"

    def __init__(
        self,
        llm_client,
        max_iterations=3,
        trace_recorder=None,
        trace_enabled: bool = True,
    ):
        super().__init__(
            max_steps=max_iterations * 2 + 1,
            trace_recorder=trace_recorder,
            trace_enabled=trace_enabled,
        )
        self.llm_client = llm_client
        self.memory = Memory()
        self.max_iterations = max_iterations

    def _run(
        self,
        run_input: AgentRunInput,
        context: AgentRunContext,
    ) -> AgentRunResult:
        task = run_input.question
        print(f"\n--- 开始处理任务 ---\n任务: {task}")

        # --- 1. 初始执行 ---
        print("\n--- 正在进行初始尝试 ---")
        initial_prompt = INITIAL_PROMPT_TEMPLATE.format(task=task)
        initial_code = self._get_llm_response(initial_prompt)
        self.memory.add_record("execution", initial_code)
        context.add_step(
            thought="Generate the initial answer.",
            action="Generate",
            action_input=task,
            observation=initial_code,
        )

        # --- 2. 迭代循环:反思与优化 ---
        iteration_limit = self.max_iterations
        completed_iterations = 0
        stopped_by_feedback = False
        for i in range(iteration_limit):
            if not context.has_step_budget():
                break

            print(f"\n--- 第 {i + 1}/{iteration_limit} 轮迭代 ---")

            # a. 反思
            print("\n-> 正在进行反思...")
            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(task=task, code=last_code)
            feedback = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)
            context.add_step(
                thought="Reflect on the previous answer.",
                action="Reflect",
                action_input=last_code,
                observation=feedback,
                metadata={"iteration": i + 1},
            )
            completed_iterations = i + 1

            # b. 检查是否需要停止
            if "无需改进" in feedback:
                print("\n✅ 反思认为代码已无需改进，任务完成。")
                stopped_by_feedback = True
                break

            if not context.has_step_budget():
                break

            # c. 优化
            print("\n-> 正在进行优化...")
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(
                task=task,
                last_code_attempt=last_code,
                feedback=feedback
            )
            refined_code = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution", refined_code)
            context.add_step(
                thought=feedback,
                action="Refine",
                action_input=last_code,
                observation=refined_code,
                metadata={"iteration": i + 1},
            )
        
        final_code = self.memory.get_last_execution()
        print(f"\n--- 任务完成 ---\n最终生成的代码:\n```python\n{final_code}\n```")
        status = "success" if final_code else "failed"
        error = None if final_code else "Reflection Agent 未生成有效结果。"
        if (
            completed_iterations < self.max_iterations
            and not context.has_step_budget()
            and not stopped_by_feedback
        ):
            status = "max_steps_exceeded"
            error = f"已达到最大 AgentStep 数 {context.max_steps}。"

        return super()._build_result(
            context=context,
            answer=final_code,
            status=status,
            error=error,
            metadata={
                "completed_iterations": completed_iterations,
                "max_iterations": self.max_iterations,
                "stopped_by_feedback": stopped_by_feedback,
            },
        )

    def _get_llm_response(self, prompt: str) -> str:
        """一个辅助方法，用于调用LLM并获取完整的流式响应。"""
        messages = [{"role": "user", "content": prompt}]
        response_text = self.llm_client.think(messages=messages) or ""
        return response_text
