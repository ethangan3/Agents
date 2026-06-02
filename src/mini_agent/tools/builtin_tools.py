import ast
import operator
from datetime import datetime
from pathlib import Path
from typing import Any

from mini_agent.tools.history import load_history


def current_time(unused_input: str = "") -> str:
    """返回当前本地时间。"""
    now = datetime.now().astimezone()
    return now.strftime("%Y-%m-%d %H:%M:%S %Z%z")


def calculate(expression: str) -> str:
    """安全计算基础数学表达式。"""
    try:
        parsed_expression = ast.parse(expression, mode="eval")
        result = _eval_math_node(parsed_expression.body)
        return str(result)
    except Exception as exc:
        return f"计算失败: {exc}"


def history_search(query: str, filename: str | Path = "chat-history.json") -> str:
    """从历史记录中检索相关对话。"""
    history = load_history(str(filename))
    if not history:
        return "没有找到历史记录。"

    query_text = query.strip()
    records = history if isinstance(history, list) else [history]
    matched_records = []

    for record in records:
        record_text = str(record)
        if not query_text or query_text in record_text:
            matched_records.append(record_text)

    if not matched_records:
        return f"没有找到与 '{query_text}' 相关的历史记录。"

    return "\n\n".join(matched_records[-3:])


def _eval_math_node(node: ast.AST) -> Any:
    allowed_binary_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    allowed_unary_ops = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp):
        operator_func = allowed_binary_ops.get(type(node.op))
        if operator_func is None:
            raise ValueError("不支持的二元运算符")
        return operator_func(_eval_math_node(node.left), _eval_math_node(node.right))

    if isinstance(node, ast.UnaryOp):
        operator_func = allowed_unary_ops.get(type(node.op))
        if operator_func is None:
            raise ValueError("不支持的一元运算符")
        return operator_func(_eval_math_node(node.operand))

    raise ValueError("只支持数字和基础数学运算")
