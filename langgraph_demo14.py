# Send动态路由
# 在条件边中，如果希望⼀个Node后同时路由到多个Node，就可以返回Send动态路由的⽅式实现。
# Send对象可传⼊两个参数，第⼀个是下⼀个Node的名称，第⼆个是Node的输⼊。
from operator import add
from typing import TypedDict, Annotated
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import Send
# 配置状态
class State(TypedDict):
    messages: Annotated[list[str],add]
class PrivateState(TypedDict):
    msg:str
def node_1(state:PrivateState) -> State:
    res = state["msg"] + "!"
    return {"messages":[res]}
builder = StateGraph(State)
# Node缓存5秒


# Command命令
# 通常，Graph中⼀个典型的业务步骤是State进⼊⼀个Node处理。在Node中先更新State状态，然后再通过
# Edges传递给下⼀个Node。如果希望将这两个步骤合并为⼀个命令，那么还可以使⽤Command命令。
builder.add_node("node1", node_1)
def routing_func (state:State):
    result = []
    for message in state["messages"]:
        result.append(Send("node1",{"msg":message}))
    return result
# 通过路由函数，将消息中每个字符串分别传⼊node1处理。
builder.add_conditional_edges( START, routing_func,["node1"])
builder.add_edge("node1", END)
graph = builder.compile()
print(graph.invoke({"messages":["hello","world","hello","graph"]}))
#{'messages': ['hello', 'world', 'hello', 'graph', 'hello!', 'world!', 'hello!','graph!']}