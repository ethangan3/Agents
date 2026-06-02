from __future__ import annotations

import json
import os
from pathlib import Path

from mini_agent.agents.BaseAgent import AgentRunResult
from mini_agent.trace.models import RunTrace


DEFAULT_TRACE_PATH = "agent-runs.json"


class TraceRecorder:
    """基于 JSON 文件的轻量运行轨迹记录器。"""

    def __init__(self, trace_path: str | Path = DEFAULT_TRACE_PATH):
        self.trace_path = Path(trace_path)

    def record(self, result: AgentRunResult | RunTrace) -> RunTrace:
        trace = result if isinstance(result, RunTrace) else RunTrace.from_result(result)
        traces = [
            existing
            for existing in self._load_traces()
            if existing.run_id != trace.run_id
        ]
        traces.append(trace)
        self._write_traces(traces)
        return trace

    def get_run(self, run_id: str) -> RunTrace | None:
        for trace in self._load_traces():
            if trace.run_id == run_id:
                return trace
        return None

    def list_recent(self, limit: int = 10) -> list[RunTrace]:
        if limit <= 0:
            return []
        return list(reversed(self._load_traces()[-limit:]))

    def _load_traces(self) -> list[RunTrace]:
        if not self.trace_path.exists():
            return []
        try:
            raw = json.loads(self.trace_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

        records = raw if isinstance(raw, list) else [raw]
        traces: list[RunTrace] = []
        for record in records:
            try:
                traces.append(RunTrace.model_validate(record))
            except Exception:
                continue
        return traces

    def _write_traces(self, traces: list[RunTrace]) -> None:
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [trace.model_dump(mode="json") for trace in traces]
        self.trace_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def get_default_trace_recorder() -> TraceRecorder | None:
    disabled = os.getenv("MINI_AGENT_TRACE_DISABLED", "").lower()
    if disabled in {"1", "true", "yes", "on"}:
        return None
    return TraceRecorder(os.getenv("MINI_AGENT_TRACE_PATH", DEFAULT_TRACE_PATH))
