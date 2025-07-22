import os
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_community.chat_models import ChatTongyi


# 1️⃣ 定义角色：Analyst、Executor、Reviewer

llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

def get_analyst_node():
    prompt = PromptTemplate.from_template(
        """你是一个任务分析师，请从以下用户请求中提取关键目标和需求点，并用列表形式返回：
        用户请求: {input}"""
    )
    chain = prompt | llm
    return RunnableLambda(lambda state: {"analysis": chain.invoke({"input": state["input"]})})

def get_executor_node():
    prompt = PromptTemplate.from_template(
        """你是一个内容生成专家，请根据以下分析要点完成初步内容：
        要点: {analysis}"""
    )
    chain = prompt | llm
    return RunnableLambda(lambda state: {"draft": chain.invoke({"analysis": state["analysis"].content})})

def get_reviewer_node():
    prompt = PromptTemplate.from_template(
        """你是一个审稿专家，请检查以下草稿内容是否符合质量要求，并输出最终版本：
        草稿: {draft}"""
    )
    chain = prompt | llm
    return RunnableLambda(lambda state: {"final": chain.invoke({"draft": state["draft"].content})})

# 2️⃣ 定义多角色状态（State）
from typing import TypedDict, Optional

class DocGenState(TypedDict):
    input: str
    analysis: Optional[str]
    draft: Optional[str]
    final: Optional[str]

# 3️⃣ 构建Graph流程

builder = StateGraph(DocGenState)

builder.add_node("AnalystAgent", get_analyst_node())
builder.add_node("ExecutorAgent", get_executor_node())
builder.add_node("ReviewerAgent", get_reviewer_node())

builder.set_entry_point("AnalystAgent")
builder.add_edge("AnalystAgent", "ExecutorAgent")
builder.add_edge("ExecutorAgent", "ReviewerAgent")
builder.set_finish_point("ReviewerAgent")

# 4️⃣ 构建可执行图

graph = builder.compile(checkpointer=InMemorySaver())

# 5️⃣ 运行示例任务

input_data = {"input": "帮我写一份关于AI在医疗行业应用的报告，涵盖诊断、药物研发、数据安全等方面"}
config = {"configurable": {"thread_id": "1"}}
result = graph.invoke(input_data, config)
print("🔍 最终结果：\n", result["final"].content)
