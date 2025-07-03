# 4、⼦图
# 在LangGraph中，⼀个Graph除了可以单独使⽤，还可以作为⼀个Node，嵌⼊到另⼀个Graph中。这种⽤法就称
# 为⼦图。通过⼦图，我们可以更好的重⽤Graph，构建更复杂的⼯作流。尤其在构建多Agent时，⾮常有⽤。在⼤
# 型项⽬中，通常都是由⼀个团队专⻔开发Agent，再通过其他团队来完整Agent整合。
# 使⽤⼦图时，基本和使⽤Node没有太多的区别。
# 唯⼀需要注意的是，当触发了SubGraph代表的Node后，实际上是相当于重新调⽤了⼀次subgraph.invoke(state)
# ⽅法。
# subgraph与graph使⽤相同State
from operator import add
from typing import TypedDict, Annotated
from langgraph.constants import END
from langgraph.graph import StateGraph, MessagesState, START
class State(TypedDict):
    messages: Annotated[list[str],add]
# Subgraph
def sub_node_1 (state:State) -> MessagesState:
    return {"messages":["response from subgraph"]}
subgraph_builder = StateGraph(State)
subgraph_builder.add_node("sub_node_1",sub_node_1)
subgraph_builder.add_edge(START, "sub_node_1")
subgraph_builder.add_edge("sub_node_1",END)
subgraph = subgraph_builder.compile()
# Parent graph
builder = StateGraph(State)
builder.add_node("subgraph_node", subgraph)
builder.add_edge(START, "subgraph_node")
builder.add_edge("subgraph_node",END)
graph = builder.compile()
print(graph.invoke({"messages": ["hello subgraph"]}))
# 结果hello subgraph会出现两次。这是因为在subgraph_node中默认调⽤了⼀次subgraph.invoke(state)⽅法。主图⾥也调⽤了⼀次invoke。这就会往state中添加两次语句
#{'messages': ['hello subgraph', 'hello subgraph', 'response from subgraph']}