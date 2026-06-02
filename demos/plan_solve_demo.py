import os

from dotenv import load_dotenv

from mini_agent.agents.LLM import HelloAgentsLLM
from mini_agent.agents.PlanAndSolveAgent import PlanAndSolveAgent

env_path = ".env"
load_dotenv(env_path)

print("env_path:", env_path)
print("MIMO_API_KEY loaded:", os.getenv("MIMO_API_KEY") is not None)
print("MIMO_URL:", os.getenv("MIMO_URL"))
print("MIMO_MODEL:", os.getenv("MIMO_MODEL"))

mimo_llm = HelloAgentsLLM(
    model=os.getenv("MIMO_MODEL"),
    apiKey=os.getenv("MIMO_API_KEY"),
    baseUrl=os.getenv("MIMO_URL"),
)

agent = PlanAndSolveAgent(
    llm_client=mimo_llm,
    max_steps=8,
)

question = (
    "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。"
    "周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
)

response = agent.run(question)
print(response.model_dump())
