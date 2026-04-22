import json
from datetime import datetime
from pydantic import BaseModel

def save_history(history, filename, append: bool = True):
    """将对话历史保存到JSON文件中，默认追加保存每次结果。"""
    new_record = history.model_dump() if isinstance(history, BaseModel) else history

    if isinstance(new_record, dict) and "saved_at" not in new_record:
        new_record["saved_at"] = datetime.now().astimezone().isoformat()

    if append:
        old_history = load_history(filename)
        if isinstance(old_history, list):
            all_history = old_history
        elif old_history:
            all_history = [old_history]
        else:
            all_history = []
        all_history.append(new_record)
    else:
        all_history = new_record

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_history, f, ensure_ascii=False, indent=4)

def load_history(filename):
    """从JSON文件中加载对话历史。"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            history = json.load(f)
        return history
    except (FileNotFoundError, json.JSONDecodeError):
        return []
