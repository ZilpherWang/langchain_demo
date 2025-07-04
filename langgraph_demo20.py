# 人类干预 Human-in-the-loop
from operator import add
import os
from langchain_core.messages import AnyMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph, MessagesState
from langchain_community.chat_models import ChatTongyi

llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)
from typing import Literal, TypedDict, Annotated
from langgraph.types import interrupt, Command

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add]

def human_approval(state: State) -> Command[Literal["call_llm", END]]:
    is_approved = interrupt(
        {"question": "是否同意调用大语言模型？"}
    )
    if is_approved:
        return Command(goto="call_llm")
    else:
        return Command(goto=END)

def call_llm(state: State) -> Command[END]:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(State)

builder.add_node("human_approval", human_approval)
builder.add_node("call_llm", call_llm)

builder.add_edge(START, "human_approval")
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

from langchain_core.messages import HumanMessage
thread_config = {"configurable": {"thread_id": 1}}
response = graph.invoke({"messsages": [HumanMessage("湖南的省会是哪里？")]}, config=thread_config)
print(response)

# 确认同意，继续执行任务
final_result = graph.invoke(Command(resume=True), config=thread_config)
print(final_result)
# 不同意，终止任务
# final_result = graph.invoke(Command(resume=True), config=thread_config)
# print(final_result)