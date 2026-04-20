'''
Author: ganzhiyu syu015201@163.com
Date: 2026-04-20 10:31:43
LastEditors: ganzhiyu syu015201@163.com
LastEditTime: 2026-04-20 10:48:05
FilePath: \Agents\agent-try\QA-assist.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
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

# 加载 .env 文件中的环境变量
load_dotenv()

llm = HelloAgentsLLM()

tools = ToolExecutor()
search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
tools.registerTool("Search", search_description, search)

agent = ReActAgent(
    llm_client=llm,
    tool_executor=tools,
    max_steps=1000
)

tools_desc = tools.getAvailableTools()
filled_prompt = REACT_PROMPT_TEMPLATE.format(
    tools=tools_desc,
    question="4月20日天津天气状况如何？",
    history=""
)

response = agent.run(filled_prompt)

save_history(response, "chat-history.json")
