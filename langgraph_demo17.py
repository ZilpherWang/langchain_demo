from typing import TypedDict
from langgraph.config import get_stream_writer
from langgraph.graph import StateGraph, START
class State(TypedDict):
    query: str
    answer: str
def node(state: State):
    writer = get_stream_writer()
    writer({"⾃定义key": "在节点内返回⾃定义信息"})
    return {"answer": "some data"}
graph = (
StateGraph(State)
 .add_node(node)
 .add_edge(START, "node")
 .compile()
)
inputs = {"query": "example"}
# Usage
for chunk in graph.stream(inputs, stream_mode="custom"):
    print(chunk)