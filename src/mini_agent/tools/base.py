from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolSpec(BaseModel):
    """工具对外暴露的结构化描述。"""

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=lambda: {"type": "string"})


class ToolResult(BaseModel):
    """工具执行的统一返回结构。"""

    status: Literal["success", "failed"]
    output: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    def to_observation(self) -> str:
        if self.is_success:
            return self.output or ""
        return f"工具调用失败: {self.error or '未知错误'}"


class BaseTool(ABC):
    """所有工具的统一抽象基类。"""

    name: str
    description: str
    parameters: dict[str, Any] = {"type": "string"}

    @abstractmethod
    def run(self, tool_input: Any = "") -> str:
        raise NotImplementedError

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=self.name,
            description=self.description,
            parameters=dict(self.parameters),
        )
