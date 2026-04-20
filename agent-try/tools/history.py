import json
from pydantic import BaseModel

def save_history(history, filename):
    """将对话历史保存到JSON文件中。"""
    with open(filename, 'w', encoding='utf-8') as f:
        if isinstance(history, BaseModel):
            json.dump(history.model_dump(), f, ensure_ascii=False, indent=4)
        else:
            json.dump(history, f, ensure_ascii=False, indent=4)

def load_history(filename):
    """从JSON文件中加载对话历史。"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            history = json.load(f)
        return history
    except FileNotFoundError:
        return []