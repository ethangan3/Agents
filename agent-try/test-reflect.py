from models.LLM import HelloAgentsLLM
from models.ReflectionAgent import ReflectionAgent
from dotenv import load_dotenv

load_dotenv()

llm = HelloAgentsLLM()

agent = ReflectionAgent(llm)
question = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"

agent.run(question)
