from typing import List
from langchain.output_parsers import OutputFixingParser
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0.2,
)

rewrite_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个中文助手，擅长将表达改写得更礼貌、专业。"),
        (
            "user",
            """请将下面的内容改写得更礼貌、更职业，保持原意。
只输出改写后的文本，不要解释。

内容：
{task}
""",
        ),
    ]
)

rewrite_chain = rewrite_prompt | llm | StrOutputParser()

class LegacyExtractResult(BaseModel):
    summary: str = Field(description="文本摘要")
    action_items: List[str] = Field(description="待办事项")
    tone: str = Field(description="语气：正面 / 中性 / 负面")


legacy_parser = PydanticOutputParser(pydantic_object=LegacyExtractResult)

legacy_extract_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个信息抽取助手，严格按照格式输出。"),
        (
            "user",
            """请从下面文本中提取信息。

{format_instructions}

文本：
{task}
""",
        ),
    ]
).partial(format_instructions=legacy_parser.get_format_instructions())

legacy_extract_chain = legacy_extract_prompt | llm | legacy_parser


def run_extract(task: str) -> LegacyExtractResult:

    return legacy_extract_chain.invoke({"task": task})



def run_rewrite(task: str) -> str:

    return rewrite_chain.invoke({"task": task})

#part3

class InfoExtract(BaseModel):
    summary: str = Field(description="文本摘要")
    keywords: List[str] = Field(description="关键词")
    action_items: List[str] = Field(description="待办事项")
    risks: List[str] = Field(description="潜在风险")


info_parser = PydanticOutputParser(pydantic_object=InfoExtract)

info_fixing_parser = OutputFixingParser.from_llm(
    parser=info_parser,
    llm=llm,
)

info_extract_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个中文信息抽取助手，必须严格按照 JSON Schema 输出，不得包含多余文本。",
        ),
        (
            "user",
            """请从下面文本中提取结构化信息。

{format_instructions}

文本：
{task}
""",
        ),
    ]
).partial(format_instructions=info_parser.get_format_instructions())

info_extract_chain = info_extract_prompt | llm | info_fixing_parser


def run_info_extract(task: str) -> InfoExtract:

    return info_extract_chain.invoke({"task": task})


