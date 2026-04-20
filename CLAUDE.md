# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Agents

All scripts run from the repo root. Set up `agent-try/.env` first:

```
LLM_MODEL_ID=<model-name>
LLM_API_KEY=<api-key>
LLM_BASE_URL=<base-url>
LLM_TIMEOUT=60
SERPAPI_API_KEY=<serpapi-key>
```

```bash
python agent-try/hello-agent.py          # Basic LLM client demo
python agent-try/test-react.py           # ReAct agent (web search)
python agent-try/test-planandsolve.py    # Plan-and-Solve agent (math problems)
python agent-try/test-reflect.py         # Reflection agent (code generation)
python agent-try/test-weather-search.py  # Search tool smoke test
```

**Dependencies** (no requirements.txt yet): `openai`, `python-dotenv`, `serpapi`

## Architecture

This is a Python multi-agent framework demonstrating three agentic reasoning patterns. All code lives in `agent-try/`.

### LLM Client
`models/LLM.py` — `HelloAgentsLLM` wraps any OpenAI-compatible API, loads config from `.env`, and supports streaming responses.

### Three Agent Types

**1. ReActAgent** (`models/Agents.py`)
- Thought → Action → Observation loop, up to `max_steps` (default 5)
- Parses LLM output for `Thought:` and `Action:` / `Finish:` patterns
- Uses `tools/general.py` `ToolExecutor` to dispatch tool calls

**2. PlanAndSolveAgent** (`models/PlanAndSolveAgent.py`)
- Stage 1: `Planner` (`models/Planner.py`) generates a Python list of steps
- Stage 2: `Executer` (`models/Executer.py`) runs each step sequentially, accumulating results

**3. ReflectionAgent** (`models/ReflectionAgent.py`)
- Iterative loop (max 3): Generate → Reflect → Refine
- `Memory` (`models/Memory.py`) tracks trajectory and reflection history across iterations

### Tools
`tools/general.py` — `ToolExecutor` registry; register callables as tools.
`tools/weather_search.py` — `Search` tool backed by SerpApi.

### Prompts
All prompt templates are in `models/prompts/`. They are in Simplified Chinese. Each agent type has its own template(s):
- ReAct: `react_prompts.py`
- Plan-and-Solve: `planner_prompt.py`, `executer_prompt.py`
- Reflection: `initial_prompt.py`, `reflect_prompt.py`, `refine_prompt.py`

### Adding a New Tool
1. Implement the tool as a callable in `tools/`
2. Register it with `ToolExecutor.register(name, func, description)`
3. Pass the executor to the agent constructor
