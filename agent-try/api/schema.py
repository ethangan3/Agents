'''
Author: ganzhiyu syu015201@163.com
Date: 2026-04-20 14:26:47
LastEditors: ganzhiyu syu015201@163.com
LastEditTime: 2026-04-20 14:37:59
FilePath: \Agents\agent-try\api\schema.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
"""
用来存放请求和响应模型
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question: str = Field(
        ...,
        description="用户提出的问题",
        max_length=5000,
        min_length=1
    )
    save_flag: bool = Field(
        False,
        description="是否保存对话历史"
    )

class HistoryItem(BaseModel):
    step: int
    type: Literal["thought", "observation", "action"]
    content: str

class AskResponse(BaseModel):
    question: str
    answer: Optional[str] = None
    reasoning: Optional[str] = None