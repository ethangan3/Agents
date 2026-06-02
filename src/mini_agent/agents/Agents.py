import logging
import re

from mini_agent.agents.BaseAgent import AgentRunContext, AgentRunInput, AgentRunResult, BaseAgent
from mini_agent.agents.LLM import HelloAgentsLLM
from mini_agent.agents.prompts.react_prompts import REACT_PROMPT_TEMPLATE
from mini_agent.tools.general import ToolExecutor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ReActAgent(BaseAgent):
    agent_type = "react"

    def __init__(
        self,
        llm_client: HelloAgentsLLM,
        tool_executor: ToolExecutor,
        max_steps: int = 5,
    ):
        super().__init__(max_steps=max_steps)
        self.llm_client = llm_client
        self.tool_executor = tool_executor

    def _run(
        self,
        run_input: AgentRunInput,
        context: AgentRunContext,
    ) -> AgentRunResult:
        question = run_input.question

        while context.has_step_budget():
            logger.info("ReAct step %s started.", len(context.steps) + 1)

            tools_desc = self.tool_executor.getAvailableTools()
            history_str = self._format_history(context.steps)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str,
            )

            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)
            if not response_text:
                error = "LLM未能返回有效响应。"
                context.add_step(error=error)
                return super()._build_result(
                    context=context,
                    status="failed",
                    error=error,
                )

            thought, action_text = self._parse_output(response_text)

            if not action_text:
                error = "未能解析出有效的Action。"
                context.add_step(
                    thought=thought,
                    error=error,
                    metadata={"raw_llm_output": response_text},
                )
                return super()._build_result(
                    context=context,
                    status="failed",
                    error=error,
                )

            if self._is_finish_action(action_text):
                final_answer = self._extract_final_answer(action_text)
                context.add_step(
                    thought=thought,
                    action="Finish",
                    action_input=final_answer,
                    observation="Agent produced final answer.",
                    metadata={"raw_llm_output": response_text},
                )
                return super()._build_result(
                    context=context,
                    answer=final_answer,
                    status="success",
                )

            tool_name, tool_input = self._parse_action(action_text)
            if not tool_name or tool_input is None:
                observation = f"错误:无法解析Action '{action_text}' 的工具名称或输入。"
                context.add_step(
                    thought=thought,
                    action=action_text,
                    observation=observation,
                    error=observation,
                    metadata={"raw_llm_output": response_text},
                )
                continue

            tool_result = self.tool_executor.execute(tool_name, tool_input)
            observation = tool_result.to_observation()
            error = None if tool_result.is_success else tool_result.error

            context.add_step(
                thought=thought,
                action=tool_name,
                action_input=tool_input,
                observation=observation,
                error=error,
                metadata={
                    "raw_llm_output": response_text,
                    "tool_result": tool_result.model_dump(),
                },
            )

        error = "已达到最大步数，未能完成任务。"
        return super()._build_result(
            context=context,
            status="max_steps_exceeded",
            error=error,
        )

    def _parse_output(self, text: str):
        """解析LLM的输出，提取Thought和Action。"""
        text = str(text).strip()

        thought = self._extract_labeled_block(
            text,
            "Thought",
            stop_labels=("Action", "Observation", "Final Answer"),
        )
        final_answer = self._extract_final_answer_from_output(text)
        if final_answer:
            return thought, f"Finish[{final_answer}]"

        action = self._extract_labeled_block(
            text,
            "Action",
            stop_labels=("Observation", "Final Answer", "Thought"),
        )

        if not action:
            candidate = text.strip()
            if self._is_finish_action(candidate) or self._parse_action(candidate) != (None, None):
                action = candidate

        return thought, action

    def _parse_action(self, action_text: str):
        """解析Action字符串，提取工具名称和输入。"""
        match = re.match(r"\s*([A-Za-z_]\w*)\s*\[(.*)\]\s*$", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2).strip()
        return None, None

    def _extract_final_answer(self, action_text: str) -> str:
        """从Finish动作中提取最终答案。"""
        final_answer = self._extract_final_answer_from_output(action_text)
        if final_answer:
            return final_answer

        bracket_match = re.match(
            r"\s*Finish\s*\[(.*)\]\s*$",
            action_text,
            re.DOTALL | re.IGNORECASE,
        )
        if bracket_match:
            return bracket_match.group(1).strip()

        call_match = re.match(
            r"\s*Finish\(\s*answer\s*=\s*['\"]?(.*?)['\"]?\s*\)\s*$",
            action_text,
            re.DOTALL | re.IGNORECASE,
        )
        if call_match:
            return call_match.group(1).strip()

        return action_text.removeprefix("Finish").strip(" ()[]")

    def _extract_final_answer_from_output(self, text: str) -> str | None:
        return self._extract_labeled_block(
            text,
            "Final Answer",
            stop_labels=("Thought", "Action", "Observation"),
        )

    def _is_finish_action(self, action_text: str) -> bool:
        stripped = str(action_text).strip()
        return bool(
            re.match(r"(?is)^Finish\s*(\[|\()", stripped)
            or re.match(r"(?is)^Final Answer\s*[:：]", stripped)
        )

    def _extract_labeled_block(
        self,
        text: str,
        label: str,
        stop_labels: tuple[str, ...],
    ) -> str | None:
        stop_pattern = "|".join(re.escape(stop_label) for stop_label in stop_labels)
        pattern = (
            rf"(?is)(?:^|\n)\s*{re.escape(label)}\s*[:：]\s*"
            rf"(.*?)(?=\n\s*(?:{stop_pattern})\s*[:：]|\Z)"
        )
        match = re.search(pattern, text)
        if not match:
            return None
        value = match.group(1).strip()
        return value or None

    def _format_history(self, steps):
        """将历史记录格式化为字符串，供提示词使用。"""
        formatted = []
        for step in steps:
            if step.thought:
                formatted.append(f"Thought: {step.thought}")
            if step.action:
                if step.action_input is not None:
                    formatted.append(f"Action: {step.action}[{step.action_input}]")
                else:
                    formatted.append(f"Action: {step.action}")
            if step.observation:
                formatted.append(f"Observation: {step.observation}")
        return "\n".join(formatted)
