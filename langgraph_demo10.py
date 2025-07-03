# Graph是LangGraph的基本构建模块，它是⼀个有向⽆环图（DAG），⽤于描述任务之间的依赖关系。
# 主要包含三个基本的元素：
# State: 在整个应⽤当中共享的⼀种数据结构。
# Node : ⼀个处理数据的节点。LangGraph中通常是⼀个Python的函数，以State为输⼊，经过⼀些操作后，
# 返回更新后的State。
# Edge : 表示Node之前的依赖关系。LangGraph中通常也是⼀个Python函数，根据当前State来决定接下来执
# ⾏哪个Node。
# 接下来⽤⼀个最简单的案例，来看⼀下Graph的基本⽤法。
from typing import TypedDict
from langgraph.constants import END, START
from langgraph.graph import StateGraph
class InputState(TypedDict):
    user_input: str

class OutputState(TypedDict):
    graph_output: str

class OverallState(TypedDict):
    foo: str
    user_input: str
    graph_output: str

class PrivateState(TypedDict):
    bar: str
def node_1(state: InputState) -> OverallState:
    # Write to OverallState
    return {"foo": state["user_input"] + ">这个人"}

def node_2(state: OverallState) -> PrivateState:
    # Read from OverallState, write to PrivateState
    return {"bar": state["foo"] + ">⾮常"}
def node_3(state: PrivateState) -> OutputState:
    # Read from PrivateState, write to OutputState
    return {"graph_output": state["bar"] + ">帅"}
# 构建图
builder = StateGraph(OverallState,input=InputState,output=OutputState)
# 添加Node
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
# 添加Edge
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", "node_3")
builder.add_edge("node_3", END)
# 编译图
graph = builder.compile()
# 调⽤图
print(graph.invoke({"user_input":"汪德志"}))
from IPython.display import Image, display
# draw_mermaid⽅法可以打印出Graph的mermaid代码。
display(Image(graph.get_graph().draw_mermaid_png()))