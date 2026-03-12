'''
Author: ganzhiyu syu015201@163.com
Date: 2026-03-12 15:13:22
LastEditors: ganzhiyu syu015201@163.com
LastEditTime: 2026-03-12 15:15:54
FilePath: \Agents\agent-try\test-planandsolve.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from models.LLM import HelloAgentsLLM
from models.PlanAndSolveAgent import PlanAndSolveAgent
from dotenv import load_dotenv

load_dotenv()

llm = HelloAgentsLLM()

agent = PlanAndSolveAgent(llm)

question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"

agent.run(question)