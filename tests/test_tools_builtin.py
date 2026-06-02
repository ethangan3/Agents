import json
import re

from mini_agent.tools.builtin_tools import calculate, current_time, history_search


def test_calculator_evaluates_basic_math():
    result = calculate("1 + 2 * 3")

    assert result == "7"


def test_calculator_rejects_unsafe_expression():
    result = calculate('__import__("os").system("echo unsafe")')

    assert "计算失败" in result


def test_current_time_returns_non_empty_string():
    result = current_time("")

    assert result
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", result)


def test_history_search_returns_no_history_when_file_missing(tmp_path):
    missing_file = tmp_path / "missing-history.json"

    result = history_search("任何内容", filename=missing_file)

    assert result == "没有找到历史记录。"


def test_history_search_finds_matching_records(tmp_path):
    history_file = tmp_path / "history.json"
    history_file.write_text(
        json.dumps(
            [
                {"question": "alpha 问题", "answer": "alpha 答案"},
                {"question": "beta 问题", "answer": "beta 答案"},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = history_search("alpha", filename=history_file)

    assert "alpha 问题" in result
    assert "beta 问题" not in result
