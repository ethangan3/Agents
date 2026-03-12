'''
Author: ganzhiyu syu015201@163.com
Date: 2026-03-12 15:21:39
LastEditors: ganzhiyu syu015201@163.com
LastEditTime: 2026-03-12 15:21:50
FilePath: \Agents\agent-try\models\prompts\initial_prompt.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
INITIAL_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。请根据以下要求，编写一个Python函数。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。

要求: {task}

请直接输出代码，不要包含任何额外的解释。
"""