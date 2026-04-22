from dotenv import load_dotenv

from models.LLM import HelloAgentsLLM
from models.Agents import ReActAgent
from tools.history import save_history
from tools.registry import build_default_tools
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)


def build_agent(save_path: str = "chat-history.json", max_steps: int = 8) -> ReActAgent:
    """
    创建一个带默认多工具集的 ReActAgent。
    """
    llm = HelloAgentsLLM()
    tools = build_default_tools(history_path=save_path)
    return ReActAgent(
        llm_client=llm,
        tool_executor=tools,
        max_steps=max_steps
    )


def ask_agent(question: str, save_flag: bool = True, save_path: str = "chat-history.json"):
    """
    向智能体提问，并返回其回答和思考过程。
    """
    agent = build_agent(save_path=save_path)

    response = agent.run(question) # response现在不是json字符串，而是一个AgentResult对象

    if save_flag:
        save_history(response.model_dump(), save_path)
    return response
