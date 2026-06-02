# MiniAgent Runtime 项目优化方案

> 目标：将当前较分散的 `Agents` 学习型仓库，重构为一个可展示、可运行、可面试讲解的轻量级 Agent Runtime 项目。  
> 定位：**从零实现 Agent 底层执行机制的小型框架**，用于补充主项目“智能业务运营系统”的工程深度。

---

## 0. 项目重新定位

当前已有主项目已经覆盖：

- 企业级 Agent 平台
- AIOps 智能运营系统
- RAG 知识库
- MCP 工具体系
- LangGraph 工作流
- PostgreSQL / Redis / Milvus
- OpenTelemetry / 日志 / 审计 / 权限
- Docker Compose 部署与测试

因此，`Agents` 小项目不应继续扩展成另一个大而全的企业级系统，否则会和主项目高度重复。

建议将其重构为：

> **MiniAgent Runtime：轻量级多范式 Agent 执行框架**

项目核心价值：

```text
从零实现 ReAct / Plan-and-Solve / Reflection 三类 Agent 执行模式，
支持工具注册、工具调用解析、运行轨迹记录、API 调用和简单前端演示。
```

最终在简历中的作用：

| 项目 | 定位 | 证明能力 |
|---|---|---|
| 智能业务运营系统 | 企业级 AI Agent + AIOps 应用系统 | 证明工程落地、系统设计、业务闭环能力 |
| MiniAgent Runtime | 轻量级 Agent 执行框架 | 证明理解 Agent 底层机制，不只是会用框架 |

---

## 1. 最终项目目标

优化完成后，项目应具备以下能力：

1. 支持三种 Agent 执行模式：
   - ReAct Agent
   - Plan-and-Solve Agent
   - Reflection Agent

2. 支持统一工具系统：
   - 工具注册中心 Tool Registry
   - 工具 schema 描述
   - 工具执行器 Tool Executor
   - Calculator / CurrentTime / Search / HistorySearch 等内置工具

3. 支持运行轨迹记录：
   - Thought
   - Action
   - Observation
   - Final Answer
   - Latency
   - Status
   - Run ID

4. 支持 FastAPI 服务化调用：
   - 查看健康状态
   - 查看工具列表
   - 运行不同类型 Agent
   - 查询历史运行记录

5. 支持简单 Web Demo：
   - 输入问题
   - 选择 Agent 类型
   - 展示最终答案
   - 展示中间执行轨迹

6. 支持基础工程化：
   - README
   - `.env.example`
   - Dockerfile
   - docker-compose.yml
   - pytest 测试
   - 示例脚本
   - 架构文档

---

## 2. 推荐最终目录结构

建议将原有 `agent-try` 中的代码整理到标准工程目录中：

```text
mini-agent-runtime/
├── README.md
├── pyproject.toml
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── src/
│   └── mini_agent/
│       ├── main.py
│       ├── config.py
│       ├── api/
│       │   ├── app.py
│       │   ├── routes.py
│       │   └── schemas.py
│       ├── agents/
│       │   ├── base.py
│       │   ├── react.py
│       │   ├── plan_solve.py
│       │   └── reflection.py
│       ├── llm/
│       │   ├── client.py
│       │   └── prompts.py
│       ├── tools/
│       │   ├── base.py
│       │   ├── registry.py
│       │   └── builtin.py
│       ├── memory/
│       │   └── store.py
│       ├── trace/
│       │   ├── models.py
│       │   └── recorder.py
│       └── utils/
│           └── parser.py
├── frontend/
│   └── app.py
├── examples/
│   ├── react_demo.py
│   ├── plan_solve_demo.py
│   └── reflection_demo.py
├── tests/
│   ├── test_tool_registry.py
│   ├── test_react_parser.py
│   ├── test_calculator.py
│   ├── test_trace_recorder.py
│   └── test_api.py
└── docs/
    ├── architecture.md
    ├── api.md
    └── demo.md
```

---

# 3. 分阶段优化计划

---

## Phase 1：仓库清理与项目骨架重构

### 目标

将当前学习型、脚本型仓库整理为一个标准 Python 工程，使 GitHub 首页看起来像一个正式项目。

### 主要任务

- [ ] 将 `agent-try` 中有价值的代码迁移到 `src/mini_agent/`。
- [ ] 删除或移动根目录中临时性质明显的文件，例如：
  - `test-react.py`
  - `test-planandsolve.py`
  - `async-try.py`
  - `QA-assist.py`
  - root `main.py` 中的 hello world 示例
- [ ] 将临时测试脚本移动到 `examples/` 或 `tests/`。
- [ ] 创建标准目录：
  - `src/mini_agent/agents`
  - `src/mini_agent/tools`
  - `src/mini_agent/api`
  - `src/mini_agent/trace`
  - `src/mini_agent/llm`
  - `frontend`
  - `docs`
  - `tests`
- [ ] 补充 `.env.example`，至少包含：
  - `OPENAI_API_KEY`
  - `BASE_URL`
  - `MODEL_NAME`
  - `TEMPERATURE`
  - `MAX_STEPS`
- [ ] 初始化 `pyproject.toml`，明确依赖：
  - `fastapi`
  - `uvicorn`
  - `pydantic`
  - `python-dotenv`
  - `requests` 或 `httpx`
  - `pytest`
  - `streamlit`

### 验收标准

必须满足以下条件：

- [ ] 根目录结构清晰，不再像零散学习脚本。
- [ ] `README.md` 不为空，至少包含项目简介、功能列表、启动方式。
- [ ] 可以通过如下命令安装依赖：

```bash
uv sync
```

或：

```bash
pip install -e .
```

- [ ] 可以运行一个最小示例：

```bash
python examples/react_demo.py
```

- [ ] 示例能够返回一个完整的 Agent 执行结果，而不是只打印 hello world。

---

## Phase 2：统一 Agent 抽象与返回结构

### 目标

将 ReAct、Plan-and-Solve、Reflection 三类 Agent 统一到同一套抽象接口中，避免每个 Agent 都是独立脚本。

### 主要任务

- [ ] 定义 `BaseAgent` 抽象类。
- [ ] 统一 Agent 输入参数。
- [ ] 统一 Agent 输出结构。
- [ ] 将 ReAct Agent 迁移到 `agents/react.py`。
- [ ] 将 Plan-and-Solve Agent 迁移到 `agents/plan_solve.py`。
- [ ] 将 Reflection Agent 迁移到 `agents/reflection.py`。
- [ ] 统一异常处理逻辑。
- [ ] 统一最大步数控制逻辑。

### 推荐核心数据结构

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AgentStep(BaseModel):
    step_id: int
    thought: Optional[str] = None
    action: Optional[str] = None
    action_input: Optional[str] = None
    observation: Optional[str] = None
    error: Optional[str] = None

class AgentRunResult(BaseModel):
    run_id: str
    agent_type: str
    question: str
    answer: Optional[str]
    steps: List[AgentStep]
    status: str
    latency_ms: int
    metadata: Dict[str, Any] = {}
```

### 推荐 Agent 接口

```python
class BaseAgent:
    agent_type: str

    def run(self, question: str) -> AgentRunResult:
        raise NotImplementedError
```

### 验收标准

必须满足以下条件：

- [ ] 三类 Agent 均继承或遵循 `BaseAgent` 接口。
- [ ] 三类 Agent 的 `run()` 方法返回统一的 `AgentRunResult`。
- [ ] 可以分别运行：

```bash
python examples/react_demo.py
python examples/plan_solve_demo.py
python examples/reflection_demo.py
```

- [ ] 三个示例都能输出：
  - `run_id`
  - `agent_type`
  - `question`
  - `answer`
  - `steps`
  - `status`
  - `latency_ms`
- [ ] Agent 执行失败时不会导致程序崩溃，而是返回 `status="failed"` 和错误信息。

---

## Phase 3：工具注册中心与工具执行器优化

### 目标

将工具调用从硬编码方式改造为统一注册和统一执行，使项目具备可扩展性。

### 主要任务

- [x] 定义 `BaseTool`。
- [x] 定义 `ToolSpec`。
- [x] 实现 `ToolRegistry`。
- [x] 实现 `ToolExecutor`。
- [x] 将已有工具统一迁移到 `tools/builtin.py`。
- [x] 保留或实现以下工具：
  - `CalculatorTool`
  - `CurrentTimeTool`
  - `SearchTool`
  - `HistorySearchTool`
- [x] 新增一个业务类工具，建议二选一：
  - `TodoTool`：将用户输入拆成待办事项
  - `FileSummaryTool`：对本地文本文件做摘要
- [x] 工具调用失败时返回结构化错误，而不是直接抛异常。

### 推荐工具结构

```python
class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict

class BaseTool:
    name: str
    description: str

    def run(self, tool_input: str) -> str:
        raise NotImplementedError

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=self.name,
            description=self.description,
            parameters={"type": "string"}
        )
```

### 工具注册示例

```python
registry = ToolRegistry()
registry.register(CalculatorTool())
registry.register(CurrentTimeTool())
registry.register(SearchTool())
registry.register(HistorySearchTool())
```

### 验收标准

必须满足以下条件：

- [x] 新增工具时，只需要在 `ToolRegistry` 中注册，不需要修改 Agent 主循环。
- [x] 可以通过代码查看所有工具：

```python
tools = registry.list_tools()
```

- [x] 可以通过工具名调用工具：

```python
executor.execute("Calculator", "1 + 2 * 3")
```

- [x] 工具调用失败时返回明确错误信息，例如：

```json
{
  "status": "failed",
  "error": "Tool not found: xxx"
}
```

- [x] 至少包含 4 个可运行工具。
- [x] 至少有 2 个工具测试用例通过。

---

## Phase 4：ReAct 主循环与 Action 解析增强

### 目标

将 ReAct Agent 做成该项目的核心亮点，完整展示 Agent 如何进行推理、选择工具、读取观察结果并生成最终答案。

### 主要任务

- [x] 规范 ReAct Prompt。
- [x] 固定模型输出格式：

```text
Thought: ...
Action: ToolName[tool input]
Observation: ...
Final Answer: ...
```

- [x] 实现稳健的 Action 解析器。
- [x] 支持最大步数限制。
- [x] 支持工具调用失败后的 Observation 回传。
- [x] 支持提前结束：检测到 `Final Answer` 后终止循环。
- [x] 支持每一步写入 trace。

### 推荐 ReAct 执行流程

```text
1. 接收用户问题
2. 构造包含工具列表的 Prompt
3. 调用 LLM 生成 Thought / Action
4. 解析 Action
5. 执行工具
6. 将 Observation 追加到上下文
7. 重复执行，直到生成 Final Answer 或达到最大步数
8. 返回 AgentRunResult
```

### 验收标准

必须满足以下条件：

- [x] ReAct Agent 能完成至少 3 类任务：
  - 计算类问题
  - 当前时间类问题
  - 需要多步推理的问题
- [x] Action 解析器能够解析如下格式：

```text
Action: Calculator[3 * (2 + 5)]
```

- [x] 达到最大步数时，Agent 能返回失败状态或总结已有观察结果。
- [x] 工具不存在时，Agent 不崩溃，而是将错误作为 Observation 继续处理或结束。
- [x] 返回结果中包含完整 steps。

---

## Phase 5：运行轨迹 Trace 与轻量持久化

### 目标

让项目具备可观测性，能够保存和回放 Agent 执行过程。

### 主要任务

- [x] 定义 `RunTrace` 数据结构。
- [x] 定义 `TraceRecorder`。
- [x] 使用 SQLite 或 JSON 文件保存运行记录。
- [x] 每次运行生成唯一 `run_id`。
- [x] 记录：
  - 输入问题
  - Agent 类型
  - 每一步 Thought / Action / Observation
  - 最终答案
  - 执行状态
  - 延迟
  - 时间戳
- [x] 提供查询接口：
  - 查询单条 run
  - 查询最近 runs

### 推荐 Trace 示例

```json
{
  "run_id": "20260601-153000-a1b2c3",
  "agent_type": "react",
  "question": "计算 23 * 17 并告诉我当前时间",
  "steps": [
    {
      "step_id": 1,
      "thought": "I need to calculate the multiplication first.",
      "action": "Calculator",
      "action_input": "23 * 17",
      "observation": "391"
    },
    {
      "step_id": 2,
      "thought": "Now I need to get the current time.",
      "action": "CurrentTime",
      "action_input": "",
      "observation": "2026-06-01 15:30:00"
    }
  ],
  "answer": "23 * 17 = 391，当前时间是 2026-06-01 15:30:00。",
  "status": "success",
  "latency_ms": 1820
}
```

### 验收标准

必须满足以下条件：

- [x] 每次 Agent 运行都会生成 `run_id`。
- [x] 每次 Agent 运行都会记录完整 steps。
- [x] 可以通过 `run_id` 查询历史运行结果。
- [x] 可以查看最近 10 条运行记录。
- [x] Trace 记录不依赖大模型输出是否完美，失败任务也要保存。
- [x] 至少有 1 个 Trace 相关测试通过。

---

## Phase 6：FastAPI 服务化封装

### 目标

将项目从命令行脚本升级为可被外部系统调用的 Agent 服务。

### 主要任务

- [x] 创建 FastAPI 应用。
- [x] 实现健康检查接口。
- [x] 实现工具列表接口。
- [x] 实现三类 Agent 运行接口。
- [x] 实现运行记录查询接口。
- [x] 使用 Pydantic 定义请求体和响应体。
- [x] 添加异常处理。
- [x] 自动生成 Swagger 文档。

### 推荐 API 设计

```text
GET  /health
GET  /v1/tools
POST /v1/agents/react/run
POST /v1/agents/plan-solve/run
POST /v1/agents/reflection/run
GET  /v1/runs/{run_id}
GET  /v1/runs
```

### 推荐请求体

```json
{
  "question": "计算 12 * 8，然后告诉我当前时间",
  "max_steps": 5
}
```

### 推荐响应体

```json
{
  "run_id": "xxx",
  "agent_type": "react",
  "question": "计算 12 * 8，然后告诉我当前时间",
  "answer": "12 * 8 = 96，当前时间是 ...",
  "steps": [],
  "status": "success",
  "latency_ms": 1600
}
```

### 验收标准

必须满足以下条件：

- [x] 可以通过如下命令启动服务：

```bash
uvicorn mini_agent.api.app:app --host 0.0.0.0 --port 8000 --reload
```

- [x] 访问以下地址能够看到 Swagger 文档：

```text
http://localhost:8000/docs
```

- [x] `/health` 返回正常状态。
- [x] `/v1/tools` 返回当前可用工具列表。
- [x] 三个 Agent 接口都能被调用。
- [x] `/v1/runs/{run_id}` 能查询历史执行轨迹。
- [x] 至少有 1 个 API 测试通过。

---

## Phase 7：简单 Web Demo

### 目标

提供一个可演示页面，让面试官或招聘方能直观看到 Agent 的运行过程。

### 技术建议

优先使用 Streamlit，不要做复杂前端。

### 页面功能

- [x] 输入用户问题。
- [x] 选择 Agent 类型：
  - ReAct
  - Plan-and-Solve
  - Reflection
- [x] 点击运行。
- [x] 展示最终答案。
- [x] 展示中间执行轨迹。
- [x] 展示运行状态和耗时。

### 推荐页面布局

```text
MiniAgent Runtime Demo

[问题输入框]
[Agent 类型选择下拉框]
[运行按钮]

最终回答：
...

执行轨迹：
Step 1
Thought: ...
Action: ...
Observation: ...

Step 2
...
```

### 验收标准

必须满足以下条件：

- [x] 可以通过如下命令启动前端：

```bash
streamlit run frontend/app.py
```

- [x] 页面可以调用后端 API。
- [x] 页面可以切换不同 Agent 类型。
- [x] 页面可以展示最终答案。
- [x] 页面可以展示中间执行轨迹。
- [ ] 至少准备 3 张 Demo 截图放入 `docs/demo.md` 或 README。

---

## Phase 8：测试、Docker 与 README 完善

### 目标

让项目达到可投递、可面试、可复现的状态。

### 主要任务

- [ ] 编写 pytest 测试。
- [ ] 编写 Dockerfile。
- [ ] 编写 docker-compose.yml。
- [ ] 完善 README。
- [ ] 完善 docs 文档。
- [ ] 增加 Demo 截图。
- [ ] 增加常见问题说明。

### 推荐测试范围

至少包含：

```text
1. Calculator 工具测试
2. Tool Registry 注册测试
3. ReAct Action 解析测试
4. Trace Recorder 测试
5. API /health 测试
6. API /v1/tools 测试
```

### README 必须包含

- [ ] 项目简介
- [ ] 项目特点
- [ ] 架构图或架构说明
- [ ] 快速启动
- [ ] 环境变量说明
- [ ] API 示例
- [ ] Demo 截图
- [ ] 技术栈
- [ ] 项目目录结构
- [ ] 后续优化方向

### Docker 验收标准

必须满足：

```bash
docker compose up --build
```

之后可以访问：

```text
http://localhost:8000/docs
```

如果 Streamlit 也纳入 compose，则还应能访问：

```text
http://localhost:8501
```

### 测试验收标准

必须满足：

```bash
pytest
```

通过核心测试，至少包含：

- [ ] 工具注册测试通过
- [ ] 工具调用测试通过
- [ ] Action 解析测试通过
- [ ] API 健康检查测试通过

---

# 4. 最小可行版本

如果时间紧，优先完成下面这个版本。该版本 2–3 天内应可完成。

## 最小版本功能

- [ ] 重构目录到 `src/mini_agent/`
- [ ] 补充 README
- [ ] 保留 ReAct Agent
- [ ] 保留 Calculator / CurrentTime / HistorySearch 三个工具
- [ ] 增加 FastAPI 接口：

```text
GET  /health
GET  /v1/tools
POST /v1/agents/react/run
```

- [ ] 增加 trace 返回
- [ ] 增加 Streamlit 简单前端
- [ ] 增加 Dockerfile
- [ ] 增加 3 个 pytest：
  - Calculator 测试
  - Tool Registry 测试
  - Action Parser 测试

## 最小版本验收标准

- [ ] `README.md` 能指导别人跑通项目。
- [ ] `python examples/react_demo.py` 能运行。
- [ ] `uvicorn mini_agent.api.app:app --reload` 能启动。
- [ ] `POST /v1/agents/react/run` 能返回答案和 steps。
- [ ] `streamlit run frontend/app.py` 能打开页面。
- [ ] `pytest` 至少通过 3 个核心测试。

---

# 5. 完整版本验收清单

优化完成后，最终项目应满足：

## 功能验收

- [ ] 支持 ReAct Agent。
- [ ] 支持 Plan-and-Solve Agent。
- [ ] 支持 Reflection Agent。
- [ ] 支持工具注册中心。
- [ ] 支持至少 4 个内置工具。
- [ ] 支持工具调用失败处理。
- [ ] 支持 Agent 执行轨迹记录。
- [ ] 支持历史运行记录查询。
- [ ] 支持 FastAPI 调用。
- [ ] 支持简单 Web Demo。

## 工程验收

- [ ] 项目目录结构清晰。
- [ ] README 完整。
- [ ] `.env.example` 完整。
- [ ] Dockerfile 可用。
- [ ] docker-compose.yml 可用。
- [ ] pytest 核心测试通过。
- [ ] API 文档可访问。
- [ ] Demo 截图已加入文档。

## 面试验收

你需要能清楚回答：

- [ ] 为什么要做这个项目？
- [ ] 它和你的主项目有什么区别？
- [ ] ReAct Agent 是怎么运行的？
- [ ] Tool Registry 为什么比硬编码工具更好？
- [ ] Agent 的中间轨迹为什么重要？
- [ ] 如果工具调用失败，系统怎么处理？
- [ ] 如何限制 Agent 最大执行步数？
- [ ] 这个项目后续如何扩展到 MCP 或 LangGraph？

---

# 6. 简历写法建议

该项目不建议写得比主项目更长。它应作为第二项目或补充项目出现。

推荐写法：

```text
MiniAgent Runtime：轻量级多范式 Agent 执行框架 | Python, FastAPI, Pydantic, SQLite, Docker

项目简介：从零实现一个轻量级 Agent Runtime，支持 ReAct、Plan-and-Solve、Reflection 三种执行模式，提供工具注册、工具调用、运行轨迹记录、会话记忆和 FastAPI 接口，用于验证 Agent 底层执行机制。

主要工作：
- 实现 ReAct Agent 主循环，支持 Thought-Action-Observation 多轮推理、工具调用解析、最大步数控制和最终答案抽取。
- 设计 Tool Registry 与 ToolExecutor，将 Calculator、Search、CurrentTime、HistorySearch 等工具以统一 schema 注册，降低新工具接入成本。
- 实现 Agent Run Trace 记录，结构化保存每轮 Thought、Action、Observation、最终答案、运行状态和延迟，便于调试和可观测性分析。
- 使用 FastAPI 封装多 Agent 执行接口，并提供简单 Web Demo 展示 Agent 类型选择、最终回答和中间执行轨迹。
- 使用 pytest 编写工具调用、Action 解析和 API 接口测试，并通过 Docker Compose 提供一键启动环境。
```

---

# 7. 面试表达建议

可以这样介绍这个项目：

```text
我的主项目偏企业级 AI 应用落地，里面用了 LangGraph、MCP、RAG 和 AIOps 流程。为了避免只停留在框架使用层面，我另外做了一个轻量级 Agent Runtime 项目，自己实现了 ReAct、Plan-and-Solve、Reflection 三种 Agent 执行模式。

这个项目重点不是业务复杂度，而是把 Agent 的主循环、工具注册、Action 解析、Observation 回传、运行轨迹记录这些底层机制跑通。通过这个项目，我能更清楚地理解 LangChain、LangGraph 这类框架背后到底在做什么。
```

项目和主项目的关系可以这样讲：

```text
主项目证明我能做业务系统，小项目证明我理解 Agent 原理。
```

---

# 8. 后续扩展方向

完成基础版本后，可以按需扩展，但不要在短期内继续堆太多功能。

优先级较高的扩展：

- [ ] 接入 MCP Server 工具。
- [ ] 增加 LangGraph 版本对照实现。
- [ ] 增加更规范的 Function Calling schema。
- [ ] 增加异步工具调用。
- [ ] 增加 OpenTelemetry trace。
- [ ] 增加多轮 Memory 管理。
- [ ] 增加 RAG Tool，但不要把它做成完整知识库系统。

不建议短期做的功能：

- [ ] 复杂权限系统。
- [ ] 大型前端后台。
- [ ] 多租户系统。
- [ ] 完整企业知识库。
- [ ] 复杂 AIOps 业务流。

这些功能已经由主项目承担，小项目应保持轻量、聚焦、可讲清楚。

---

# 9. 最终结论

`Agents` 仓库应从“学习草稿”升级为：

> **MiniAgent Runtime：轻量级多范式 Agent 执行框架**

它的目标不是功能大而全，而是清晰展示：

- Agent 如何循环执行；
- Agent 如何选择工具；
- 工具如何注册和调用；
- Observation 如何回传；
- Trace 如何记录；
- API 如何服务化；
- Demo 如何展示。

最终简历组合为：

```text
项目一：智能业务运营系统
定位：企业级 AI Agent + AIOps 应用系统

项目二：MiniAgent Runtime
定位：从零实现 Agent 执行机制的小型框架
```

该组合比两个“大而杂”的 Agent 项目更清晰，更适合面向：

- AI Agent 开发实习生
- AI 应用开发实习生
- Python 后端 AI 方向实习生
- LLM 应用工程实习生
