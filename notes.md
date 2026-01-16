
笔记链接：https://blog.csdn.net/2503_92750729/article/details/157019953?sharetype=blogdetail&sharerId=157019953&sharerefer=PC&sharesource=2503_92750729&spm=1011.2480.3001.8118

# LangChain Agent 学习与实践笔记

通过菜鸟教程总结的Langchain学习笔记
---

## 一、环境搭建与 Demo 跑通

### 1.1 Python 环境

* Python 版本要求：**Python ≥ 3.9**
* 建议使用虚拟环境（venv / conda）

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

---

### 1.2 安装依赖

```bash
pip install langchain langchain-openai langchain-community python-dotenv
```

---

### 2.3 配置环境变量

LangChain 不推荐在代码中硬编码 API Key，而是通过环境变量统一管理。

```bash
export DEEPSEEK_API_KEY="你的 API Key"
```

Windows PowerShell：

```powershell
setx DEEPSEEK_API_KEY "你的 API Key"
```

---

### 2.4 运行示例 Demo

```python
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


resp = llm.invoke("用一句话解释什么是 LangChain")
print(resp.content)
```

**预期输出示例：**

```
LangChain 是一个用于构建可组合大语言模型应用的框架……
```

成功输出即表明：

* 环境变量读取正常
* 模型接口调用成功
* LangChain 基础调用流程可用

---

## 二、材料核心概念总结

### 1. LangChain 的模块化思想

### LangChain 的核心概念

从实际使用体验来看，LangChain 更像是一个 **“大模型应用的工程框架”**，而不是单纯调用模型的工具。它的作用并不是替代语言模型，而是作为中间层，把语言模型与外部系统组织起来，解决“模型能说，但做不了事”的问题。

在不使用 LangChain 的情况下，大语言模型通常只能根据输入生成文本，本身无法获取实时数据、访问私有知识，也无法执行计算或调用接口。而 LangChain 通过统一的组件设计，把这些能力以模块化的方式组合起来，使模型可以参与到完整的业务流程中。

具体来说，LangChain 主要解决了以下几个实际限制：  

* **知识更新问题**：模型训练数据是静态的，LangChain 可以通过检索组件接入最新数据或私有文档。  
* **领域知识不足**：通过向量检索或数据库查询，将企业或专业领域知识引入模型推理过程。  
* **缺乏执行能力**：模型本身不能计算或调用接口，而 LangChain 可以通过工具让模型间接完成这些操作。  
* **上下文连续性不足**：在多轮对话中，LangChain 的记忆模块可以帮助模型保留关键信息，避免每轮对话都“从零开始”。

从结构上看，LangChain 将这些能力拆分为清晰的模块：模型接口负责与大模型通信，Prompt 模板用于规范输入，Chains 或 LCEL 负责流程编排，Memory 管理上下文，Retrievers 负责知识检索，而 Agent 与 Tool 机制则让模型能够根据任务需要自主选择执行方式。通过这种模块化设计，开发者可以像搭积木一样构建复杂但可维护的 AI 应用。

---

### 2.PromptTemple

PromptTemplate 用于将用户输入嵌入到结构化 Prompt 中，使模型输入更稳定、可控，避免每次手写 Prompt。

---

### 3. LCEL

LCEL 使用 `|` 管道符将多个步骤连接起来，例如：

```

Prompt → LLM → OutputParser

```

这种方式相比传统 Chain：

* 更灵活
* 更支持异步
* 流式输出

---

### 4. OutputParser

* 模型输出永远是 Message
* StrOutputParser 是显式类型转换
* 没有 Parser，工程不可控

---

### 5.Agent 与 Tool

Agent 的本质是：

> **让模型自主决定使用哪个工具来完成任务，而不是只生成文本。**

模型可以根据上下文：

在我自己的理解里，LangChain 里的 Agent 本质上是在解决一个问题：
如果任务的执行步骤不固定，代码该怎么写？

如果不用 Agent，常见做法是把流程在代码里全部写死，比如先查什么、再算什么、最后总结。但我在看示例和自己写 demo 的时候发现，一旦任务稍微复杂一点，这种方式就会让代码变得又长又乱，而且很难扩展。

Agent 的引入，本质上是把“下一步该做什么”的判断权交给模型。

---

### 6.Retrievers / VectorStores

在实际使用大语言模型时，一个非常明显的限制是：模型的知识是静态的，只能基于训练时学到的内容进行回答，无法获取最新信息。

LangChain 通常会先把原始文档进行加载和处理：例如从本地文件或数据库中读取文本，然后通过文本切分将长文档拆成更小的片段，接着使用向量模型把文本转换成向量，并最终存储到向量数据库中。

在链式调用中，模型并不需要关心向量数据库的具体实现细节，只需要通过 Retriever 输入问题，就能返回与问题语义最相关的文档内容。这些检索结果随后可以被自动注入到 Prompt 中，作为上下文提供给模型进行回答

---

## 三、项目运行说明

1. 安装 Python ≥ 3.9
2. 创建并激活虚拟环境
3. 安装 LangChain 相关依赖
4. 配置 API Key 环境变量
5. 运行示例脚本
6. 验证终端输出结果

---

## 四、常见报错与解决方案

### 问题 1：未配置 API Key

**报错信息：**

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/4cd9c66cb14b4a318cdd5e9d6ef661ae.png#pic_center)

**解决方案：**

* 确认环境变量已正确设置
* 确认当前终端与 Python 运行环境一致

---

### 问题 2：依赖版本冲突

**现象：**

* ImportError
* ModuleNotFoundError

**解决方案：**

* 升级 Python 至 3.10+
* 保证 `langchain` 与 `langchain-openai` 版本一致
* 必要时新建虚拟环境

---

## 五、关键设计选择分析

我认为 LangChain 最关键的设计选择，是把 “大模型能力” 和 “工程控制逻辑”明确拆开，并通过 Agent 机制让模型在一定边界内自行做决策。在我实际跑示例和编写 demo 的过程中可以明显感受到，如果只使用原生 OpenAI SDK，模型更多只是一个文本生成接口，所有流程判断、工具调用顺序都需要在代码中提前写死，一旦需求变得复杂，代码会迅速变得难以维护。

而 LangChain Agent 的引入改变了这一点。模型在接收到用户输入后，不再只是生成一段回答，而是可以根据当前上下文判断是否需要使用工具、下一步应该执行什么操作，例如先进行信息检索，再对结果进行总结。这种方式在我理解示例代码时给了我很直观的感受：模型开始参与流程决策，而不是被动执行固定脚本。

更重要的是，LangChain 并没有因为能力增强而牺牲工程结构。通过 Tool 的统一抽象以及 LCEL 管道式的组合方式，复杂流程仍然可以被拆解为清晰、可复用的模块。实际体验下来，这种设计既保留了大模型的灵活性，又避免了脚本式调用带来的失控问题。我认为这正是 LangChain 在工程实践中最有价值、也最具长期意义的设计选择。

---

## 六、总结

通过本次学习与实践：

* 成功跑通 LangChain 官方示例
* 理解了 Agent、LCEL 与结构化输出的核心思想
* 为后续代码重构和信息抽取模块奠定了基础
