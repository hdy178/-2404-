from src.refactor_chain import run_info_extract

text = """
今天公司召开季度例会，讨论了以下事项：
1. 下周需要完成产品文档更新。
2. 客户反馈问题需尽快解决。
3. 潜在市场风险包括竞争对手的价格战。
"""

result = run_info_extract(text)

print(result.model_dump_json(indent=2, ensure_ascii=False))

