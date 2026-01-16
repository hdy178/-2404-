# LangChain Learning & Refactoring Practice

> 本项目是一次围绕 LangChain 的学习、重构与功能实现练习，目标是将一段“能跑但结构混乱”的 legacy 脚本，重构为 **可维护、可组合、可复现** 的 LangChain 工程结构，并在此基础上实现一个**严格结构化输出模块**。

---

## 一、项目背景

在很多早期大模型项目中，常见的问题是：

- prompt 拼接、模型调用、输出解析全部混在一起
- 改一个 prompt 要动一堆代码
- 输出看起来是 JSON，但工程根本不敢直接用
- 一旦模型输出稍微不规范，程序直接崩掉

本项目以一段 legacy 单轮问答脚本为起点，通过 LangChain（LCEL）进行重构，并实现一个可复用的结构化信息抽取模块，重点关注 **工程组织方式而不是模型本身**。

---

## 二、项目结构

```text
.
├── README.md              # 项目说明（本文件）
├── notes.md               # 学习与实践笔记
├── requirements.txt       # 依赖列表
├── .env.example           # 环境变量示例（不包含密钥）
├── src/
│   ├── legacy_simple.py   # 原始 legacy 脚本（对照用）
│   ├── refactor_chain.py  # LangChain 重构后的核心逻辑（Part 2 + Part 3）
│   ├── demo.py
│   └── cli.py             # 命令行入口
├── examples/
│   ├── extract.py
│   ├── rewrite.py
│   └── info_extract.py
└── tests/
    └── test_report.py   # legacy vs refactor 行为对比说明
```

## 三、环境准备

### 1. Python 环境

- Python >= 3.9
- 推荐使用虚拟环境（venv / conda 均可）

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 环境变量配置

- 本项目 不在代码中写死 API Key，统一通过环境变量读取。

- 请在项目根目录复制一份环境变量示例文件：

```bash
cp .env.example .env
并在 .env 中填写你自己的 Key，例如：
env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

## 四、如何运行示例

本项目提供了多个可直接运行的示例代码，位于 examples/ 目录。
```bash
cli运行: "python -m src.cli --mode rewrite --task "{内容}""
```
### 1.文本改写

```bash
python examples/rewrite.py
```

#### 功能说明

```text
输入一段中文文本

使用 LCEL（prompt | llm | parser）进行改写仅输出改写后的结果文本
```

### 2.Legacy 行为对齐抽取

```bash
python examples/extract.py
```

#### 功能说明

```text
行为与 legacy_simple.py 保持一致

输出使用 Pydantic 结构化结果

用于验证「重构不改变业务语义」
```

### 3.严格结构化信息抽取

```bash
python examples/info_extract.py
```

#### 功能说明

```text

输入：新闻 / 会议纪要 / 客服对话等中文文本

输出：严格 JSON Schema

字段包括：

summary

keywords

action_items

risks

若模型输出不合法 JSON，会自动触发修复流程。
```

## 五、核心实现说明

### 1. LCEL 组合方式

项目核心逻辑均采用 LCEL 方式组织：

```bash
Prompt → LLM → OutputParser
```

- 这种写法使得：
  
```text

Prompt 可单独修改

模型可随时替换

输出格式由 Parser 兜底保证
```

- 为什么使用 Pydantic + OutputFixingParser
  
```text
Pydantic：定义明确的工程级数据结构

OutputFixingParser：在模型输出不规范时自动重试 / 修复

避免“看起来是 JSON，但一解析就炸”的问题
```

## 六、目录说明补充

### src/refactor_chain.py

- Part 2 与 Part 3 的最终合并实现文件  
- 包含所有 LangChain 核心链路逻辑（Prompt / LLM / Parser）  
- 使用 LCEL 方式组织，便于维护与扩展  

---

### tests/parity_report.md

- 用于对比 legacy 与 refactor 后实现的行为一致性  
- 通过多组输入输出示例，验证重构未引入语义偏差  
- 作为 Part 2「行为保持一致」要求的交付说明文档  

## 七、备注

- 本项目主要关注 **工程结构设计与可维护性**，而非模型参数调优  
- 模型本身可灵活替换，例如：
  - OpenAI
  - DeepSeek
  - 其他兼容 OpenAI API 规范的模型服务
- 只要模型接口遵循 **OpenAI-style API**，即可在不修改核心逻辑的情况下复用整体工程结构  

---

## 八、作者说明

本项目是一次围绕 LangChain 的学习与重构实践，重点在于理解并掌握其工程化思想，例如链路拆分、结构化输出与可复用设计，而非追求复杂功能或模型效果本身。
