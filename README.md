# MiniAgent Runtime

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-prototype-green)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-purple)
![LLM](https://img.shields.io/badge/LLM-OpenAI%20compatible-black)
![Status](https://img.shields.io/badge/status-active%20development-orange)

MiniAgent Runtime is a lightweight, from-scratch Agent runtime for studying how
LLM agents actually execute: reasoning loops, tool registration, action parsing,
observation feedback, and structured execution history.

The project is intentionally small. It is not another all-in-one enterprise AI
platform. Its purpose is to make the core mechanics behind ReAct-style agents
clear, runnable, and easy to explain.

## Why This Exists

Most Agent demos hide the interesting part behind large frameworks. This project
takes the opposite route: it keeps the system compact and implements the runtime
pieces directly.

MiniAgent Runtime focuses on four questions:

- How does an Agent decide the next action?
- How are tools described, registered, selected, and executed?
- How does the Observation return to the next reasoning step?
- How can the execution trace be inspected after a run?

This makes the repository useful as a learning project, interview project, and
minimal reference implementation for Agent runtime design.

## Features

| Capability | Status | Description |
|---|---:|---|
| ReAct Agent | Available | Thought -> Action -> Observation loop with max-step control |
| Tool Registry | Available | Register tools with names, descriptions, functions, and input schemas |
| Tool Executor | Available | Execute tools by name and pass string or JSON-like inputs |
| Built-in Tools | Available | Calculator, CurrentTime, Search, HistorySearch |
| OpenAI-compatible LLM Client | Available | Works with any OpenAI-compatible chat completion endpoint |
| Reasoning History | Available | Stores thought, action, and observation records during each run |
| Plan-and-Solve Agent | Experimental | Planner + executor implementation |
| Reflection Agent | Experimental | Generate, reflect, and refine loop |
| FastAPI Service | Prototype | Basic `/health`, `/tools`, and `/ask` endpoints |
| Web Demo | Planned | Streamlit scaffold exists, UI implementation is pending |
| Docker Deployment | Planned | Docker files are scaffolded, runtime wiring is pending |

## Architecture

```text
User Question
    |
    v
ReActAgent
    |
    |-- builds prompt with available tools
    |-- calls OpenAI-compatible LLM
    |-- parses Thought / Action
    |
    v
ToolExecutor
    |
    |-- finds tool by name
    |-- executes Calculator / CurrentTime / Search / HistorySearch
    |
    v
Observation
    |
    v
ReActAgent history
    |
    |-- Thought
    |-- Action
    |-- Observation
    |
    v
Final Answer
```

The current implementation keeps the runtime simple on purpose:

- `ReActAgent` owns the execution loop.
- `HelloAgentsLLM` wraps an OpenAI-compatible streaming chat API.
- `ToolExecutor` owns tool registration, listing, and execution.
- Built-in tools live under `mini_agent.tools`.
- FastAPI and demo layers are thin wrappers over the core runtime.

## Project Layout

```text
.
├── README.md
├── pyproject.toml
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── demos/
│   └── react_demo.py
├── frontend/
│   └── app.py
├── src/
│   └── mini_agent/
│       ├── agents/
│       │   ├── Agents.py
│       │   ├── LLM.py
│       │   ├── PlanAndSolveAgent.py
│       │   ├── ReflectionAgent.py
│       │   └── prompts/
│       ├── api/
│       │   ├── app.py
│       │   └── schema.py
│       ├── services/
│       │   └── qa_service.py
│       └── tools/
│           ├── builtin_tools.py
│           ├── general.py
│           ├── registry.py
│           ├── history.py
│           └── weather_search.py
└── docs/
    └── mini_agent_runtime_optimization_plan.md
```

## Quick Start

### 1. Install

Using `uv`:

```bash
uv sync
```

Or using standard Python tooling:

```bash
python -m venv .venv
pip install -e .
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then fill in the values:

```env
LLM_API_KEY=your_api_key
LLM_MODEL_ID=your_model_name
LLM_BASE_URL=https://your-openai-compatible-endpoint/v1
SERPAPI_API_KEY=your_serpapi_key
```

`SERPAPI_API_KEY` is only required when using the `Search` tool.

### 3. Run a ReAct Agent

```python
from dotenv import load_dotenv

from mini_agent.agents.Agents import ReActAgent
from mini_agent.agents.LLM import HelloAgentsLLM
from mini_agent.tools.registry import build_default_tools

load_dotenv()

llm = HelloAgentsLLM()
tools = build_default_tools()

agent = ReActAgent(
    llm_client=llm,
    tool_executor=tools,
    max_steps=5,
)

result = agent.run("计算 23 * 17，然后告诉我当前时间。")
print(result.model_dump())
```

The returned object contains:

```json
{
  "question": "...",
  "answer": "...",
  "reason": "...",
  "history": [
    {
      "step": 1,
      "type": "thought",
      "content": "..."
    },
    {
      "step": 1,
      "type": "action",
      "content": "Calculator[23 * 17]"
    },
    {
      "step": 1,
      "type": "observation",
      "content": "391"
    }
  ]
}
```

### 4. Run the Bundled Demo

```bash
python demos/react_demo.py
```

The bundled demo currently uses `MIMO_API_KEY`, `MIMO_URL`, and `MIMO_MODEL`
aliases. If you prefer the generic environment variables, instantiate
`HelloAgentsLLM()` without explicit arguments as shown above.

## Built-in Tools

| Tool | Purpose | Notes |
|---|---|---|
| `Calculator` | Safe arithmetic evaluation | Supports basic numeric expressions |
| `CurrentTime` | Local date and time | No external API required |
| `Search` | Web search through SerpAPI | Requires `SERPAPI_API_KEY` |
| `HistorySearch` | Search saved local conversation history | Reads JSON history records |

Tools are registered in one place:

```python
from mini_agent.tools.registry import build_default_tools

tools = build_default_tools()
print(tools.listTools())
```

Registering a new tool:

```python
from mini_agent.tools.general import ToolExecutor

def todo_splitter(text: str) -> str:
    return "\n".join(f"- {item.strip()}" for item in text.split(";") if item.strip())

tools = ToolExecutor()
tools.registerTool(
    "TodoSplitter",
    "Split a semicolon-separated task description into todo items.",
    todo_splitter,
    {"text": "str, semicolon-separated todo text"},
)
```

Once registered, the ReAct Agent can call it with:

```text
Action: TodoSplitter[write README; add tests; clean imports]
```

## ReAct Output Format

The prompt asks the model to respond with:

```text
Thought: analyze the problem and decide what to do next
Action: ToolName[tool input]
```

When the model has enough information, it should finish with:

```text
Action: Finish[final answer]
```

The runtime then:

1. Parses the `Action`.
2. Executes the selected tool.
3. Appends the `Observation` to history.
4. Repeats until `Finish[...]` or `max_steps` is reached.

## API Prototype

The FastAPI layer currently exposes a small prototype API:

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `GET` | `/tools` | List registered tools |
| `POST` | `/ask` | Ask the ReAct Agent a question |

Intended local command:

```bash
uvicorn mini_agent.api.app:app --reload --host 0.0.0.0 --port 8000
```

Example request:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"计算 12 * 8，然后告诉我当前时间\",\"save_flag\":true}"
```

The API module is being migrated from the original script layout to package
qualified imports. If you run into import errors, use the Python runtime example
above as the stable path while the API layer is being finalized.

## Environment Variables

| Variable | Required | Description |
|---|---:|---|
| `LLM_API_KEY` | Yes | API key for an OpenAI-compatible model provider |
| `LLM_MODEL_ID` | Yes | Model name used by chat completion |
| `LLM_BASE_URL` | Yes | OpenAI-compatible base URL |
| `LLM_TIMEOUT` | No | Request timeout in seconds, defaults to `60` |
| `SERPAPI_API_KEY` | No | Required only by the `Search` tool |
| `MIMO_API_KEY` | Demo only | Alias used by `demos/react_demo.py` |
| `MIMO_URL` | Demo only | Alias used by `demos/react_demo.py` |
| `MIMO_MODEL` | Demo only | Alias used by `demos/react_demo.py` |

## Development Notes

This repository is in active refactoring from an experimental script collection
to a standard Python package. The core ReAct loop and tool system are already in
`src/mini_agent`; service, API, Docker, and UI layers are still being cleaned up.

Recommended next engineering steps:

- Normalize imports to `mini_agent.*` across API and service modules.
- Add `AgentRunResult` with `run_id`, `status`, `latency_ms`, and structured steps.
- Add pytest coverage for calculator, tool registry, action parsing, and API health.
- Implement the Streamlit UI in `frontend/app.py`.
- Fill in `Dockerfile` and `docker-compose.yml`.
- Add trace persistence and query APIs.

## Roadmap

- [x] Move core code into `src/mini_agent`
- [x] Implement ReAct Agent loop
- [x] Implement tool registry and executor
- [x] Add Calculator, CurrentTime, Search, and HistorySearch tools
- [x] Add OpenAI-compatible LLM client
- [ ] Normalize package imports
- [ ] Add unified `BaseAgent` and `AgentRunResult`
- [ ] Add persistent run trace storage
- [ ] Add `/v1/agents/react/run` API
- [ ] Add Plan-and-Solve and Reflection API endpoints
- [ ] Add Streamlit demo UI
- [ ] Add Docker Compose deployment
- [ ] Add automated tests

## Interview Explanation

A concise way to describe this project:

```text
MiniAgent Runtime is a lightweight Agent runtime implemented from scratch.
It focuses on the core mechanisms behind Agent frameworks: the ReAct execution
loop, tool registration, action parsing, observation feedback, and reasoning
history. Compared with enterprise Agent platforms, this project is deliberately
small so that the Agent internals are easy to inspect, debug, and explain.
```

Key technical talking points:

- Why `ToolExecutor` is better than hard-coded tool calls.
- How `Thought -> Action -> Observation` creates an iterative reasoning loop.
- How max-step control prevents infinite Agent execution.
- How tool errors are converted into observations instead of crashing the loop.
- How this runtime could later connect to MCP tools or LangGraph workflows.

## License

No license has been selected yet. Add a license before publishing this repository
as a public open-source project.
