import os

from dotenv import load_dotenv

from mini_agent.agents.LLM import HelloAgentsLLM
from mini_agent.agents.ReflectionAgent import ReflectionAgent

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

agent = ReflectionAgent(
    llm_client=mimo_llm,
    max_iterations=3,
)

task = "编写一个 Python 函数，找出 1 到 n 之间所有的素数，并尽量保证代码清晰、可读。"

response = agent.run(task)
print(response.model_dump())
