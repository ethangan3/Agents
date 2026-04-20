'''
Author: ganzhiyu syu015201@163.com
Date: 2026-04-20 10:29:45
LastEditors: ganzhiyu syu015201@163.com
LastEditTime: 2026-04-20 11:33:24
FilePath: \Agents\agent-try\tools\history.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
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