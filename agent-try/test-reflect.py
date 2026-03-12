'''
Author: ganzhiyu syu015201@163.com
Date: 2026-03-12 15:24:31
LastEditors: ganzhiyu syu015201@163.com
LastEditTime: 2026-03-12 15:25:47
FilePath: \Agents\agent-try\test-reflect.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from models.LLM import HelloAgentsLLM
from models.ReflectionAgent import ReflectionAgent
from dotenv import load_dotenv

load_dotenv()

llm = HelloAgentsLLM()

agent = ReflectionAgent(llm)
question = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"

agent.run(question)
