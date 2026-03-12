'''
Author: ganzhiyu syu015201@163.com
Date: 2026-03-12 11:32:47
LastEditors: ganzhiyu syu015201@163.com
LastEditTime: 2026-03-12 14:20:57
FilePath: \Agents\agent-try\prompts\react_prompts.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# ReAct 提示词模板
REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish(answer="...") 来输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""