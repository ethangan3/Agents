from .LLM import HelloAgentsLLM
from tools.general import ToolExecutor
from .prompts.react_prompts import REACT_PROMPT_TEMPLATE
import re
import logging
from pydantic import BaseModel
from typing import Literal, Union, List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class HistoryItem(BaseModel):
    step: int
    type: Literal["thought", "action", "observation"]
    content: str

class AgentResult(BaseModel):
    question: str
    answer: Optional[str] = None
    reason: Optional[str] = None
    history: list[HistoryItem]


class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        # self.history = []
        self.history: list[HistoryItem] = []

    def run(self, question: str):
        """
        运行ReAct智能体来回答一个问题。
        """
        # self.history = [] # 每次运行时重置历史记录
        self.history: list[HistoryItem] = [] # 每次运行时重置历史记录
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第 {current_step} 步 ---")

            # 1. 格式化提示词
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = self._format_history()
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            # 2. 调用LLM进行思考
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)
            if not response_text:
                # print("错误:LLM未能返回有效响应。")
                logger.error("LLM未能返回有效响应。")
                # return {
                #     "question": question,
                #     "answer": None,
                #     "reason": "LLM未能返回有效响应。",
                #     "history": self.history
                # }
                return AgentResult(
                    question=question,
                    answer=None,
                    reason="LLM未能返回有效响应。",
                    history=self.history
                )
            # (这段逻辑在 run 方法的 while 循环内)
            # 3. 解析LLM的输出
            thought, action = self._parse_output(response_text)
            
            if thought:
                # print(f"思考: {thought}")
                logger.info(f"思考: {thought}")
                # self.history.append({
                #     "step": current_step,
                #     "type": "thought",
                #     "content": thought
                # })
                self.history.append(HistoryItem(
                    step=current_step,
                    type="thought",
                    content=thought
                ))

            if not action:
                # print("警告:未能解析出有效的Action，流程终止。")
                logger.warning("未能解析出有效的Action，流程终止。")
                # return {
                #     "question": question,
                #     "answer": None,
                #     "reason": "未能解析出有效的Action。",
                #     "history": self.history
                # }
                return AgentResult(
                    question=question,
                    answer=None,
                    reason="未能解析出有效的Action。",
                    history=self.history
                )
            # self.history.append({
            #     "step": current_step,
            #     "type": "action",
            #     "content": action
            # })
            self.history.append(HistoryItem(
                step=current_step,
                type="action",
                content=action
            ))
            # 4. 执行Action
            if action.startswith("Finish"):
                # 如果是Finish指令，提取最终答案并结束
                final_answer = re.match(r"Finish\[(.*)\]", action).group(1)
                # print(f"🎉 最终答案: {final_answer}")
                logger.info(f"最终答案: {final_answer}")
                # return {
                #     "question": question,
                #     "answer": final_answer,
                #     "reason": "成功完成任务。",
                #     "history": self.history
                # }
                return AgentResult(
                    question=question,
                    answer=final_answer,
                    reason="成功完成任务。",
                    history=self.history
                )

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                # ... 处理无效Action格式 ...
                observation = f"错误:无法解析Action '{action}' 的工具名称或输入。"
                print(observation)
                logger.error(observation)
                # self.history.append({
                #     "step": current_step,
                #     "type": "observation",
                #     "content": observation
                # })
                self.history.append(HistoryItem(
                    step=current_step,
                    type="observation",
                    content=observation
                ))

                continue

            # print(f"🎬 行动: {tool_name}[{tool_input}]")
            logger.info(f"行动: {tool_name}[{tool_input}]")

            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = f"错误:未找到名为 '{tool_name}' 的工具。"
            else:
                observation = tool_function(tool_input) # 调用真实工具
                # (这段逻辑紧随工具调用之后，在 while 循环的末尾)
            # print(f"👀 观察: {observation}")
            logger.info(f"观察: {observation}")

            # 将本轮的Action和Observation添加到历史记录中
            # self.history.append(f"Action: {action}")
            # self.history.append(f"Observation: {observation}")
            # self.history.append({
            #     "step": current_step,
            #     "type": "observation",
            #     "content": observation
            # })
            self.history.append(HistoryItem(
                step=current_step,
                type="observation",
                content=observation
            ))

        # 循环结束
        # print("已达到最大步数，流程终止。")
        logger.warning("已达到最大步数，流程终止。")
        # return {
        #     "question": question,
        #     "answer": None,
        #     "reason": "已达到最大步数，未能完成任务。",
        #     "history": self.history
        # }
        return AgentResult(
            question=question,
            answer=None,
            reason="已达到最大步数，未能完成任务。",
            history=self.history
        )


    def _parse_output(self, text: str):
        """解析LLM的输出，提取Thought和Action。"""
        thought_match = re.search(r"Thought: (.*)", text)
        action_match = re.search(r"Action: (.*)", text)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """解析Action字符串，提取工具名称和输入。"""
        match = re.match(r"(\w+)\[(.*)\]", action_text)
        if match:
            return match.group(1), match.group(2)
        return None, None
    # def _format_history(self):
    #     """将历史记录格式化为字符串，供提示词使用。"""
    #     formatted = []
    #     for item in self.history:
    #         if isinstance(item, dict):
    #             formatted.append(f"{item['type'].capitalize()}: {item['content']}")
    #         else:
    #             formatted.append(str(item))
    #     return "\n".join(formatted)
    def _format_history(self):
        """将历史记录格式化为字符串，供提示词使用。"""
        formatted = []
        for item in self.history:
            formatted.append(f"{item.type.capitalize()}: {item.content}")
        return "\n".join(formatted)
