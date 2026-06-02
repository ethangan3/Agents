"""
统一 Agent 的生命周期、调用入口和输入输出协议。

BaseAgent 只负责通用外壳：输入归一化、run_id、耗时统计和异常兜底。
具体推理策略由子类在 _run() 中实现。
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


AgentStatus = Literal["success", "failed", "max_steps_exceeded"]


class AgentRunInput(BaseModel):
    """一次 Agent 运行的统一输入。"""

    question: str = Field(..., min_length=1, description="用户问题或任务描述")
    max_steps: int | None = Field(None, ge=1, description="本次运行的最大步数")
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentStep(BaseModel):
    """统一的中间执行步骤。"""

    step_id: int
    thought: str | None = None
    action: str | None = None
    action_input: str | None = None
    observation: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRunResult(BaseModel):
    """所有 Agent 的统一返回结构。"""

    run_id: str
    agent_type: str
    question: str
    answer: str | None = None
    steps: list[AgentStep] = Field(default_factory=list)
    status: AgentStatus
    latency_ms: int = 0
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MaxStepsExceeded(Exception):
    """Agent 已达到最大步骤数。"""


@dataclass
class AgentRunContext:
    """一次 Agent 运行过程中的共享上下文。"""

    run_id: str
    agent_type: str
    question: str
    max_steps: int
    steps: list[AgentStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def has_step_budget(self) -> bool:
        return len(self.steps) < self.max_steps

    def add_step(
        self,
        *,
        thought: str | None = None,
        action: str | None = None,
        action_input: str | None = None,
        observation: str | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentStep:
        if not self.has_step_budget():
            raise MaxStepsExceeded(
                f"已达到最大步骤数 {self.max_steps}，无法继续添加 AgentStep。"
            )

        step = AgentStep(
            step_id=len(self.steps) + 1,
            thought=thought,
            action=action,
            action_input=action_input,
            observation=observation,
            error=error,
            metadata=metadata or {},
        )
        self.steps.append(step)
        return step


class BaseAgent(ABC):
    """所有 Agent 的统一抽象基类。"""

    agent_type = "base"

    def __init__(self, max_steps: int = 5):
        self.max_steps = max_steps

    def run(self, agent_input: str | AgentRunInput) -> AgentRunResult:
        run_input = self._normalize_input(agent_input)
        run_id = self._new_run_id()
        started_at = time.perf_counter()
        effective_max_steps = run_input.max_steps or self.max_steps
        context = AgentRunContext(
            run_id=run_id,
            agent_type=self.agent_type,
            question=run_input.question,
            max_steps=effective_max_steps,
            metadata=dict(run_input.metadata),
        )

        try:
            result = self._run(run_input=run_input, context=context)
        except MaxStepsExceeded as exc:
            result = self._build_result(
                context=context,
                answer=None,
                status="max_steps_exceeded",
                error=str(exc),
            )
        except Exception as exc:
            if context.has_step_budget():
                context.add_step(
                    error=str(exc),
                    metadata={"exception_type": type(exc).__name__},
                )
            result = self._build_result(
                context=context,
                answer=None,
                status="failed",
                error=str(exc),
            )

        result.latency_ms = int((time.perf_counter() - started_at) * 1000)
        return result

    @abstractmethod
    def _run(
        self,
        run_input: AgentRunInput,
        context: AgentRunContext,
    ) -> AgentRunResult:
        raise NotImplementedError

    def _build_result(
        self,
        context: AgentRunContext,
        status: AgentStatus,
        answer: str | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentRunResult:
        return AgentRunResult(
            run_id=context.run_id,
            agent_type=context.agent_type,
            question=context.question,
            answer=answer,
            steps=context.steps,
            status=status,
            error=error,
            metadata={**context.metadata, **(metadata or {})},
        )

    def _normalize_input(self, agent_input: str | AgentRunInput) -> AgentRunInput:
        if isinstance(agent_input, AgentRunInput):
            return agent_input
        return AgentRunInput(question=agent_input)

    def _new_run_id(self) -> str:
        return uuid4().hex
