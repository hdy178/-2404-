
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.refactor_chain import run_rewrite, run_extract

CASES = [
    {
        "mode": "rewrite",
        "input": "你怎么这么慢？",
        "legacy": "请问进度是否可以再快一些？",
        "refactor": "请问是否可以加快一些进度？",
    },
    {
        "mode": "rewrite",
        "input": "把这个马上改完。",
        "legacy": "请尽快完成这项修改。",
        "refactor": "请您尽快完成这项修改。",
    },
    {
        "mode": "extract",
        "input": "我们需要准备 PPT，下周一汇报，目前进度一般。",
        "legacy": {
            "summary": "...",
            "action_items": ["准备 PPT", "下周一汇报"],
            "tone": "中性",
        },
        "refactor": {
            "summary": "团队需要准备下周一汇报用的PPT，但当前进度一般。",
            "action_items": ["准备PPT", "下周一汇报"],
            "tone": "中性",
        },
    },
]

@pytest.mark.parametrize("case", CASES)
def test_parity(case):

    if case["mode"] == "rewrite":
        result = run_rewrite(case["input"])

        ref_text = case["refactor"].replace(" ", "").replace("？", "").replace("。", "")
        res_text = result.replace(" ", "").replace("？", "").replace("。", "")
        assert ref_text in res_text or res_text in ref_text, f"Rewrite 不一致: {result}"

    elif case["mode"] == "extract":
        result = run_extract(case["input"])
        data = result.model_dump()


        ref_items = [x.replace(" ", "") for x in case["refactor"]["action_items"]]
        res_items = [x.replace(" ", "") for x in data["action_items"]]
        assert ref_items == res_items, f"action_items 不一致: {data['action_items']}"


        assert data["tone"] == case["refactor"]["tone"], f"tone 不一致: {data['tone']}"


        ref_summary = case["refactor"]["summary"].replace(" ", "")
        res_summary = data["summary"].replace(" ", "")
        assert ref_summary in res_summary or res_summary in ref_summary, f"summary 不一致: {data['summary']}"

    # 1.输出稳定性差异
    # 差异表现：Legacy版本的输出内容和格式容易波动，同一输入多次运行可能得到风格不同的回答；重构版本输出更加稳定、统一。
    # 原因说明：Refactor 版本使用了PromptTemplate明确约束回答语言、角色和格式，而legacy写法通常是直接拼接字符串，模型自由度过高。
    # 2.输出可解析性差异
    # 差异表现：Legacy版本输出多为自然语言文本，程序无法直接解析；重构版本可以稳定输出JSON或固定结构。
    # 原因说明：Refactor版本引入了OutputParser，对模型输出进行了显式类型约束，使结果具备工程可用性。
    # 3.工程可维护性差异
    # 差异表现：Legacy代码中prompt、模型调用、解析逻辑混在一起，修改需求时容易牵一发动全身；重构版本结构清晰、模块职责明确。
    # 原因说明：LangChain通过LCEL将流程拆分成独立组件，降低了耦合度。