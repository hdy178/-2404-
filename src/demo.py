from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


resp = llm.invoke("用一句话解释什么是 LangChain")
print(resp.content)