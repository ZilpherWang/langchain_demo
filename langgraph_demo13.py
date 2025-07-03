# 在Graph图中，通过Edge(边)把Node(节点)连接起来，从⽽决定State应该如何在Graph中传递。LangGraph中也
# 提供了⾮常灵活的构建⽅式。
# 普通Edge和EntryPoint
# Edge通常是⽤来把两个Node连接起来，形成逻辑处理路线。例如 graph.add_edge("node_1","node_2") 。
# LangGraph中提供了两个默认的Node， START和END，⽤来作为Graph的⼊⼝和出⼝。
# 同时，也可以⾃⾏指定EntryPoint。例如
# builder = StateGraph(State)
# builder.set_entry_point("node1")
# builder.set_finish_point("node2")

from typing import TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.constants import START, END
from langgraph.graph import StateGraph
# 配置状态
class State(TypedDict):
    number: int
def node_1(state:State , config: RunnableConfig) -> State:
    return {"number":state["number"] + 1}
builder = StateGraph(State)
# Node缓存5秒
builder.add_node("node1", node_1)
def routing_func (state:State) -> str:
    if state["number"] > 5:
        return "node1"
    else:
        return END
builder.add_edge("node1", END)
builder.add_conditional_edges( START, routing_func)
graph = builder.compile()
print(graph.invoke({"number":7}))