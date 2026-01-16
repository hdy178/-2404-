
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.refactor_chain import run_rewrite, run_extract

CASES = [
    {
        "mode": "rewrite",
        "input": "这次作业怎么这么难？我有点做不出来。",
        "legacy": "这次作业有点难，我做不出来。",
        "refactor": "这次作业难度较高，我在完成过程中遇到了一些困难。",
    },
    {
        "mode": "rewrite",
        "input": "老师，这个地方我真的不太懂。",
        "legacy": "老师，这个地方我不懂。",
        "refactor": "老师，这一部分的内容我理解得还不够清楚。",
    },
    {
        "mode": "extract",
        "input": "这次课程作业要求下周一提交代码和实验报告，目前代码基本完成，但报告还没开始写。",
        "legacy": {
            "summary": "...",
            "action_items": ["提交代码", "提交实验报告"],
            "tone": "中性",
        },
        "refactor": {
            "summary": "课程作业需要在下周一提交代码和实验报告，目前代码已基本完成，但实验报告尚未开始撰写。",
            "action_items": ["完成实验报告", "下周一提交作业"],
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
