# 大模型消息持久化
from langchain_community.chat_models import ChatTongyi
import os
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import InMemorySaver

print(os.getenv("DASHSCOPE_API_KEY"))
llm = ChatTongyi(
    model="qwen-plus",
    api_key="sk-" + os.getenv("DASHSCOPE_API_KEY"),
)

def call_model(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": response}

builder = StateGraph(MessagesState)
builder.add_node(call_model)
builder.add_edge(START, "call_model")

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {
    "configurable": {
        "thread_id": "1"
    }
}

for chunk in graph.stream(
    {"messages": [{"role": "user", "content": "河南的省会在哪里？"}]},
    config,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

for chunk in graph.stream(
    {"messages": [{"role": "user", "content": "河北呢"}]},
    config,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()