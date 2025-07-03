from langchain_community.chat_models import ChatTongyi
import os
from langgraph.graph import StateGraph, MessagesState, START

# 使⽤⼤模型对历史信息进⾏总结
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

graph = builder.compile()

for chunk in graph.stream(
    {"messages": [{"role": "user", "content": "河南的省会在哪里？"}]},
    stream_mode="messages"
):
    print(chunk)
