import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

from models.LLM import HelloAgentsLLM
from tools.general import ToolExecutor
from tools.weather_search import *
from models.Agents import ReActAgent

from models.prompts.react_prompts import REACT_PROMPT_TEMPLATE
from tools.history import save_history, load_history
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

def ask_agent(question: str, save_flag: bool = True, save_path: str = "chat-history.json"):
    """
    向智能体提问，并返回其回答和思考过程。
    """
    llm = HelloAgentsLLM()

    tools = ToolExecutor()
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    tools.registerTool("Search", search_description, search)

    agent = ReActAgent(
        llm_client=llm,
        tool_executor=tools,
        max_steps=1000
    )

    response = agent.run(question) # response现在不是json字符串，而是一个AgentResult对象

    if save_flag:
        save_history(response.model_dump(), save_path)
    return response