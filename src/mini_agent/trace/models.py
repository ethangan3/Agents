from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from mini_agent.agents.BaseAgent import AgentRunResult, AgentStep, AgentStatus


class RunTrace(BaseModel):
    """一次 Agent 运行的可持久化轨迹。"""

    run_id: str
    agent_type: str
    question: str
    answer: str | None = None
    steps: list[AgentStep] = Field(default_factory=list)
    status: AgentStatus
    latency_ms: int = 0
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def from_result(cls, result: AgentRunResult) -> "RunTrace":
        return cls(
            run_id=result.run_id,
            agent_type=result.agent_type,
            question=result.question,
            answer=result.answer,
            steps=result.steps,
            status=result.status,
            latency_ms=result.latency_ms,
            error=result.error,
            metadata=dict(result.metadata),
        )
