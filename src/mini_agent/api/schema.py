"""API 请求和响应模型。"""
from typing import Optional

from pydantic import BaseModel, Field

from mini_agent.agents.BaseAgent import AgentRunInput, AgentRunResult, AgentStep


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        description="用户提出的问题",
        max_length=5000,
        min_length=1
    )
    save_flag: bool = Field(
        False,
        description="是否保存对话历史"
    )
    max_steps: Optional[int] = Field(
        None,
        ge=1,
        description="本次 Agent 运行的最大步数"
    )


class AskResponse(AgentRunResult):
    pass


__all__ = [
    "AgentRunInput",
    "AgentRunResult",
    "AgentStep",
    "AskRequest",
    "AskResponse",
]
