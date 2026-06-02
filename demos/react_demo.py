from mini_agent.agents import Agents

from dotenv import load_dotenv
from pathlib import Path
import os

env_path = ".env"
load_dotenv(env_path)

print("env_path:", env_path)
print("MIMO_API_KEY loaded:", os.getenv("MIMO_API_KEY") is not None)
print("MIMO_URL:", os.getenv("MIMO_URL"))
print("MIMO_MODEL:", os.getenv("MIMO_MODEL"))

from mini_agent.agents.LLM import HelloAgentsLLM
from mini_agent.agents.prompts.react_prompts import REACT_PROMPT_TEMPLATE

mimo_llm = HelloAgentsLLM(model=os.getenv("MIMO_MODEL"), apiKey=os.getenv("MIMO_API_KEY"), baseUrl=os.getenv("MIMO_URL"))

from mini_agent.tools.general import ToolExecutor
from mini_agent.tools.registry import build_default_tools

tools = build_default_tools()
tools_des = tools.getAvailableTools()

agent = Agents.ReActAgent(
    llm_client=mimo_llm,
    tool_executor=tools,
    max_steps=1000
)

filled_prompt = REACT_PROMPT_TEMPLATE.format(
    tools=tools_des,
    question="4月20日天津天气状况如何？",
    history=""
)

response = agent.run(filled_prompt)
