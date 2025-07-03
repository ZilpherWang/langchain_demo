# Command命令
# 通常，Graph中⼀个典型的业务步骤是State进⼊⼀个Node处理。在Node中先更新State状态，然后再通过
# Edges传递给下⼀个Node。如果希望将这两个步骤合并为⼀个命令，那么还可以使⽤Command命令。
from operator import add
from typing import TypedDict, Annotated
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from langgraph.types import Command
# 配置状态
class State(TypedDict):
    messages: Annotated[list[str],add]
def node_1(state:State):
    new_message = []
    for message in state["messages"]:
        new_message.append( message + "!")
    return Command(
        goto=END,
        update={"messages":new_message}
    )
builder = StateGraph(State)
builder.add_node("node1", node_1)
# node1中通过Command同时集成了更新State和指定下个Node
builder.add_edge(START,"node1")
graph = builder.compile()
print(graph.invoke({"messages":["hello","world","hello","graph"]}))
# {'messages': ['hello', 'world', 'hello', 'graph', 'hello!', 'world!', 'hello!','graph!']}