import os

from fastapi import FastAPI, HTTPException, Query

from mini_agent.agents.Agents import ReActAgent
from mini_agent.agents.BaseAgent import AgentRunInput
from mini_agent.agents.LLM import HelloAgentsLLM
from mini_agent.agents.PlanAndSolveAgent import PlanAndSolveAgent
from mini_agent.agents.ReflectionAgent import ReflectionAgent
from mini_agent.api.schema import (
    AgentRunRequest,
    AgentRunResponse,
    AskRequest,
    AskResponse,
    RecentRunsResponse,
    RunTraceResponse,
    ToolListResponse,
)
from mini_agent.services.qa_service import ask_agent
from mini_agent.tools.registry import build_default_tools
from mini_agent.trace.recorder import DEFAULT_TRACE_PATH, TraceRecorder

app = FastAPI(
    title="MiniAgent Runtime API",
    version="0.1.0",
    description="轻量级多范式 Agent Runtime 服务",
)


def _trace_recorder() -> TraceRecorder:
    return TraceRecorder(os.getenv("MINI_AGENT_TRACE_PATH", DEFAULT_TRACE_PATH))


def _build_agent(agent_type: str):
    llm = HelloAgentsLLM()
    if agent_type == "react":
        return ReActAgent(
            llm_client=llm,
            tool_executor=build_default_tools(),
        )
    if agent_type == "plan-solve":
        return PlanAndSolveAgent(llm_client=llm)
    if agent_type == "reflection":
        return ReflectionAgent(llm_client=llm)
    raise ValueError(f"Unsupported agent type: {agent_type}")


def _run_agent(agent_type: str, request: AgentRunRequest) -> AgentRunResponse:
    try:
        agent = _build_agent(agent_type)
        result = agent.run(
            AgentRunInput(
                question=request.question,
                max_steps=request.max_steps,
            )
        )
        return AgentRunResponse(**result.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/v1/tools", response_model=ToolListResponse)
def list_tools():
    return ToolListResponse(tools=build_default_tools().listTools())


@app.get("/tools", response_model=ToolListResponse)
def tools():
    return list_tools()


@app.post("/v1/agents/react/run", response_model=AgentRunResponse)
def run_react(request: AgentRunRequest):
    return _run_agent("react", request)


@app.post("/v1/agents/plan-solve/run", response_model=AgentRunResponse)
def run_plan_solve(request: AgentRunRequest):
    return _run_agent("plan-solve", request)


@app.post("/v1/agents/reflection/run", response_model=AgentRunResponse)
def run_reflection(request: AgentRunRequest):
    return _run_agent("reflection", request)


@app.get("/v1/runs/{run_id}", response_model=RunTraceResponse)
def get_run(run_id: str):
    trace = _trace_recorder().get_run(run_id)
    if trace is None:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return RunTraceResponse(**trace.model_dump())


@app.get("/v1/runs", response_model=RecentRunsResponse)
def list_runs(limit: int = Query(10, ge=1, le=100)):
    return RecentRunsResponse(runs=_trace_recorder().list_recent(limit=limit))


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        response = ask_agent(
            request.question,
            save_flag=request.save_flag,
            max_steps=request.max_steps,
        )
        return AskResponse(**response.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
