"""API 请求和响应模型。"""
from typing import Any, Optional

from pydantic import BaseModel, Field

from mini_agent.agents.BaseAgent import AgentRunInput, AgentRunResult, AgentStep
from mini_agent.trace.models import RunTrace


class AgentRunRequest(BaseModel):
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


class AgentRunResponse(AgentRunResult):
    """统一 Agent 运行响应。"""


class AskRequest(AgentRunRequest):
    """兼容旧 /ask 接口的请求结构。"""


class AskResponse(AgentRunResponse):
    """兼容旧 /ask 接口的响应结构。"""


class ToolListResponse(BaseModel):
    tools: list[dict[str, Any]]


class RunTraceResponse(RunTrace):
    """单条运行轨迹响应。"""


class RecentRunsResponse(BaseModel):
    runs: list[RunTrace]


__all__ = [
    "AgentRunRequest",
    "AgentRunResponse",
    "AgentRunInput",
    "AgentRunResult",
    "AgentStep",
    "AskRequest",
    "AskResponse",
    "RecentRunsResponse",
    "RunTraceResponse",
    "ToolListResponse",
]
