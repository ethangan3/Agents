# MiniAgent Runtime

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-ready-green)
![Streamlit](https://img.shields.io/badge/Streamlit-demo-ff4b4b)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-purple)
![Docker](https://img.shields.io/badge/Docker-supported-2496ed)
![Status](https://img.shields.io/badge/status-active%20development-orange)

MiniAgent Runtime is a small, readable Agent runtime for learning and
experimenting with LLM agent execution. It implements the core mechanics behind
agent frameworks directly: unified agent inputs and outputs, step-level traces,
tool registration, ReAct action parsing, plan execution, reflection loops, and a
thin FastAPI service layer.

The goal is not to hide the runtime behind a large framework. The goal is to
make the runtime easy to inspect, debug, test, and explain.

## Highlights

- **Unified agent contract**: every agent accepts `AgentRunInput` and returns
  `AgentRunResult`.
- **Step-level execution trace**: intermediate reasoning, action, observation,
  error, and metadata are captured as `AgentStep` records.
- **Shared lifecycle control**: `BaseAgent` handles run IDs, max-step limits,
  latency, exception fallback, and trace persistence.
- **Multiple agent strategies**: ReAct, Plan-and-Solve, and Reflection agents
  share the same runtime shape.
- **Tool registry**: tools are registered once and exposed to the agent and API.
- **API and UI**: FastAPI endpoints and a Streamlit demo are included.
- **Docker support**: run the API and frontend with Docker Compose.

## Agent Types

| Agent | Status | What it demonstrates |
| --- | --- | --- |
| `ReActAgent` | Available | Thought -> Action -> Observation loop with tool calls |
| `PlanAndSolveAgent` | Experimental | Planner first, then step-by-step execution |
| `ReflectionAgent` | Experimental | Generate -> reflect -> refine iterations |

## Architecture

```text
User question
    |
    v
AgentRunInput
    |
    v
BaseAgent.run()
    |
    |-- create run_id
    |-- normalize max_steps
    |-- catch exceptions
    |-- measure latency
    |-- persist trace
    |
    v
Concrete agent strategy
    |
    |-- ReAct / Plan-and-Solve / Reflection
    |-- append AgentStep records
    |-- call LLM and tools when needed
    |
    v
AgentRunResult
```

The core implementation lives under `src/mini_agent`:

```text
src/mini_agent/
  agents/
    BaseAgent.py            # shared input/output, lifecycle, max-step handling
    Agents.py               # ReActAgent
    PlanAndSolveAgent.py    # planner + executor strategy
    ReflectionAgent.py      # generate/reflect/refine strategy
    LLM.py                  # OpenAI-compatible LLM wrapper
  api/
    app.py                  # FastAPI routes
    schema.py               # request/response models
  services/
    qa_service.py           # compatibility service for /ask
  tools/
    base.py                 # tool result models
    builtin.py              # built-in tool implementations
    general.py              # ToolExecutor
    registry.py             # default tool registration
    weather_search.py       # weather/search integration
  trace/
    models.py               # persisted trace model
    recorder.py             # JSON trace recorder
```

## Quick Start

### 1. Install

This project is designed to work well with `uv`:

```bash
uv sync --extra frontend
```

Or install it with standard Python tooling:

```bash
python -m venv .venv
pip install -e .
```

### 2. Configure

Create a local environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Fill in your OpenAI-compatible model provider:

```env
LLM_API_KEY=your_api_key
LLM_MODEL_ID=your_model_name
LLM_BASE_URL=https://your-openai-compatible-endpoint/v1
SERPAPI_API_KEY=
```

`SERPAPI_API_KEY` is only required when you use search-related tools.

### 3. Run an Agent in Python

```python
from dotenv import load_dotenv

from mini_agent.agents.Agents import ReActAgent
from mini_agent.agents.BaseAgent import AgentRunInput
from mini_agent.agents.LLM import HelloAgentsLLM
from mini_agent.tools.registry import build_default_tools

load_dotenv()

agent = ReActAgent(
    llm_client=HelloAgentsLLM(),
    tool_executor=build_default_tools(),
    max_steps=5,
)

result = agent.run(
    AgentRunInput(
        question="Calculate 23 * 17, then tell me the current time.",
        max_steps=5,
    )
)

print(result.model_dump())
```

### 4. Run the API

```bash
uv run uvicorn mini_agent.api.app:app --reload --host 0.0.0.0 --port 8000
```

Open:

- Health check: <http://localhost:8000/health>
- API docs: <http://localhost:8000/docs>

### 5. Run the Streamlit UI

```bash
uv run streamlit run frontend/app.py
```

The UI expects the API at `http://localhost:8000` by default. You can override
it with:

```bash
MINI_AGENT_API_URL=http://localhost:8000
```

## Docker

Build and run both the API and Streamlit frontend:

```bash
docker compose up --build
```

Then open:

- API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>
- Frontend: <http://localhost:8501>

The Compose setup mounts local traces into `./data`:

```text
./data/agent-runs.json
```

Useful Docker commands:

```bash
docker compose logs -f api
docker compose logs -f frontend
docker compose down
```

If dependency installation is slow on Windows, this is usually caused by large
Python wheels such as data or LLM framework dependencies. The Docker image sets
`UV_LINK_MODE=copy` to avoid hardlink warnings across filesystems.

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/v1/tools` | List registered tools |
| `POST` | `/v1/agents/react/run` | Run the ReAct agent |
| `POST` | `/v1/agents/plan-solve/run` | Run the Plan-and-Solve agent |
| `POST` | `/v1/agents/reflection/run` | Run the Reflection agent |
| `GET` | `/v1/runs` | List recent persisted traces |
| `GET` | `/v1/runs/{run_id}` | Fetch one persisted trace |
| `POST` | `/ask` | Compatibility endpoint for the ReAct service |

Example:

```bash
curl -X POST http://localhost:8000/v1/agents/react/run \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Calculate 12 * 8, then tell me the current time.\",\"max_steps\":6}"
```

Response shape:

```json
{
  "run_id": "9a4d...",
  "agent_type": "react",
  "question": "Calculate 12 * 8, then tell me the current time.",
  "answer": "96, and the current time is ...",
  "steps": [
    {
      "step_id": 1,
      "thought": "I should calculate first.",
      "action": "Calculator",
      "action_input": "12 * 8",
      "observation": "96",
      "error": null,
      "metadata": {}
    }
  ],
  "status": "success",
  "latency_ms": 1234,
  "error": null,
  "metadata": {}
}
```

## Built-in Tools

| Tool | Purpose |
| --- | --- |
| `Calculator` | Evaluate basic arithmetic expressions |
| `CurrentTime` | Return the current local time |
| `Search` | Search through SerpAPI |
| `HistorySearch` | Search local conversation history |
| `Todo` | Split task text into a simple todo list |

Register the default tool set:

```python
from mini_agent.tools.registry import build_default_tools

tools = build_default_tools()
print(tools.listTools())
```

Register a custom tool:

```python
from mini_agent.tools.general import ToolExecutor

def split_tasks(text: str) -> str:
    return "\n".join(
        f"- {item.strip()}"
        for item in text.split(";")
        if item.strip()
    )

tools = ToolExecutor()
tools.registerTool(
    name="TaskSplitter",
    description="Split semicolon-separated text into tasks.",
    func=split_tasks,
    args_schema={"text": "str"},
)
```

## Runtime Contract

All agents share the same input and output model.

Input:

```python
AgentRunInput(
    question="What should the agent solve?",
    max_steps=5,
    metadata={"source": "demo"},
)
```

Output:

```python
AgentRunResult(
    run_id="...",
    agent_type="react",
    question="...",
    answer="...",
    steps=[...],
    status="success",
    latency_ms=1200,
    error=None,
    metadata={},
)
```

Possible statuses:

- `success`
- `failed`
- `max_steps_exceeded`

## Demos

```bash
uv run python demos/react_demo.py
uv run python demos/plan_solve_demo.py
uv run python demos/reflection_demo.py
```

Some older demos still use `MIMO_API_KEY`, `MIMO_URL`, and `MIMO_MODEL` as
provider aliases. The package runtime uses `LLM_API_KEY`, `LLM_BASE_URL`, and
`LLM_MODEL_ID` by default.

## Tests

Run the test suite:

```bash
uv run pytest
```

The tests cover:

- Base agent lifecycle and max-step behavior
- Unified request and response schemas
- ReAct parser and runtime flow
- Plan-and-Solve step recording
- Reflection step recording
- Tool registry and executor behavior
- Built-in tools
- Trace recorder persistence
- FastAPI route behavior

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `LLM_API_KEY` | Yes | API key for an OpenAI-compatible provider |
| `LLM_MODEL_ID` | Yes | Model name |
| `LLM_BASE_URL` | Yes | OpenAI-compatible base URL |
| `SERPAPI_API_KEY` | No | Required only for search tools |
| `MINI_AGENT_API_URL` | No | Frontend API URL, defaults to `http://localhost:8000` |
| `MINI_AGENT_TRACE_PATH` | No | Trace file path, defaults to `agent-runs.json` |
| `MINI_AGENT_TRACE_DISABLED` | No | Set to `true` to disable trace persistence |

## Roadmap

- [x] Move core code into `src/mini_agent`
- [x] Add unified `BaseAgent`, `AgentRunInput`, and `AgentRunResult`
- [x] Add shared max-step and exception handling
- [x] Add ReAct Agent runtime
- [x] Add Plan-and-Solve and Reflection agents
- [x] Add tool registry and built-in tools
- [x] Add JSON trace persistence
- [x] Add FastAPI endpoints
- [x] Add Streamlit frontend
- [x] Add Docker and Docker Compose setup
- [x] Add unit test skeletons and runtime tests
- [ ] Clean up legacy demo environment aliases
- [ ] Add streaming API responses
- [ ] Add richer trace search and filtering
- [ ] Add CI for linting and tests
- [ ] Add a public license before publishing

## License

No license has been selected yet. Add a license before publishing this repository
as a public open-source project.
