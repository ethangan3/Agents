from .prompts.executer_prompt import EXECUTOR_PROMPT_TEMPLATE


class Executor:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def execute_step(
        self,
        question: str,
        plan: list[str],
        history: str,
        current_step: str,
    ) -> str:
        """
        执行计划中的单个步骤，并返回该步骤结果。
        """
        prompt = EXECUTOR_PROMPT_TEMPLATE.format(
            question=question,
            plan=plan,
            history=history if history else "无",
            current_step=current_step,
        )

        messages = [{"role": "user", "content": prompt}]
        return self.llm_client.think(messages=messages) or ""

    def execute(self, question: str, plan: list[str]) -> str:
        """
        根据计划，逐步执行并解决问题。
        """
        history = ""  # 用于存储历史步骤和结果的字符串
        response_text = ""
        
        print("\n--- 正在执行计划 ---")
        
        for i, step in enumerate(plan):
            print(f"\n-> 正在执行步骤 {i + 1}/{len(plan)}: {step}")
            response_text = self.execute_step(question, plan, history, step)
            
            # 更新历史记录，为下一步做准备
            history += f"步骤 {i + 1}: {step}\n结果: {response_text}\n\n"
            
            print(f"✅ 步骤 {i + 1} 已完成，结果: {response_text}")

        # 循环结束后，最后一步的响应就是最终答案
        final_answer = response_text
        return final_answer
