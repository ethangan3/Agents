# agent-try

现在的 `QA-Assist` 已经改成了一个可扩展的多工具 ReAct Agent。

## 当前内置工具

- `Search`：网页搜索，适合天气、新闻、事实查询
- `Calculator`：数学计算
- `CurrentTime`：获取当前时间
- `HistorySearch`：检索本地历史对话

## 关键文件

- `tools/general.py`：工具定义、注册、执行
- `tools/registry.py`：默认工具注册中心
- `tools/builtin_tools.py`：本地内置工具实现
- `models/Agents.py`：ReAct Agent 主循环
- `models/prompts/react_prompts.py`：工具调用提示词
- `service/qa_service.py`：Agent 构建与问答服务入口

## 如何继续扩展新工具

1. 在 `tools/` 下新增工具函数
2. 在 `tools/registry.py` 里注册工具名、描述、函数、参数说明
3. 保持工具输入尽量是单个字符串，便于 ReAct 输出 `ToolName[...]`
4. 如果需要结构化入参，也可以让模型输出 JSON，例如 `ToolName[{"city":"上海"}]`

## 示例

```python
tools.registerTool(
    "StockPrice",
    "查询股票价格",
    stock_price,
    {"symbol": "str，股票代码"}
)
```

注册后，模型就可以在推理时输出：

```text
Thought: 我需要查询实时股价。
Action: StockPrice[AAPL]
```
