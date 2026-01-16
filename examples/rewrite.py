

from src.refactor_chain import run_rewrite

text = """
今天的会议很混乱，大家讨论的问题没有明确结论，
需要进一步整理和总结。
"""

result = run_rewrite(text)


print(result)
