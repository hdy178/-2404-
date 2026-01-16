
from src.refactor_chain import run_extract

text = """
今天公司召开季度例会，总结上季度业绩：
1. 下周完成产品文档更新。
2. 客户反馈问题需尽快解决。
3. 本季度整体销售额增长10%。
"""


result = run_extract(text)


print(result.model_dump_json(indent=2, ensure_ascii=False))
