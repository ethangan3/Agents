import json

from pydantic import BaseModel

from mini_agent.tools.history import load_history, save_history


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_load_history_returns_empty_list_when_file_missing(tmp_path):
    result = load_history(tmp_path / "missing.json")

    assert result == []


def test_load_history_returns_empty_list_when_json_invalid(tmp_path):
    history_file = tmp_path / "broken.json"
    history_file.write_text("{not-json", encoding="utf-8")

    result = load_history(history_file)

    assert result == []


def test_save_history_writes_single_record_when_append_false(tmp_path):
    history_file = tmp_path / "history.json"

    save_history({"question": "问题"}, history_file, append=False)

    saved = read_json(history_file)
    assert saved["question"] == "问题"
    assert "saved_at" in saved


def test_save_history_appends_to_empty_file_history(tmp_path):
    history_file = tmp_path / "history.json"

    save_history({"question": "问题"}, history_file, append=True)

    saved = read_json(history_file)
    assert isinstance(saved, list)
    assert saved[0]["question"] == "问题"


def test_save_history_appends_to_existing_list(tmp_path):
    history_file = tmp_path / "history.json"
    history_file.write_text(
        json.dumps([{"question": "旧问题"}], ensure_ascii=False),
        encoding="utf-8",
    )

    save_history({"question": "新问题"}, history_file, append=True)

    saved = read_json(history_file)
    assert [record["question"] for record in saved] == ["旧问题", "新问题"]


def test_save_history_converts_existing_single_record_to_list(tmp_path):
    history_file = tmp_path / "history.json"
    history_file.write_text(
        json.dumps({"question": "旧问题"}, ensure_ascii=False),
        encoding="utf-8",
    )

    save_history({"question": "新问题"}, history_file, append=True)

    saved = read_json(history_file)
    assert isinstance(saved, list)
    assert [record["question"] for record in saved] == ["旧问题", "新问题"]


def test_save_history_accepts_pydantic_model(tmp_path):
    class Message(BaseModel):
        question: str
        answer: str

    history_file = tmp_path / "history.json"

    save_history(Message(question="问题", answer="答案"), history_file, append=False)

    saved = read_json(history_file)
    assert saved["question"] == "问题"
    assert saved["answer"] == "答案"
