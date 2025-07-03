from langchain_core.messages import AnyMessage, AIMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing import Annotated,TypedDict
from operator import add

# State是所有节点共享的状态，它是⼀个字典，包含了所有节点的状态。有⼏个需要注意的地⽅：
# State形式上，可以是TypedDict字典，也可以是Pydantic中的⼀个BaseModel。例如：
# from pydantic import BaseModel
# # The overall state of the graph (this is the public state shared across nodes)
# class OverallState(BaseModel):
#     a: str

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    list_field: Annotated[list[int],add]
    extra_field: int
def node1(state: State):
    new_message = AIMessage("Hello!")
    return {"messages": [new_message],"list_field":[10],"extra_field": 10}
def node2(state: State):
    new_message = AIMessage("LangGraph!")
    return {"messages": [new_message], "list_field":[20],"extra_field": 20}
def node3(state: State):
    new_message = AIMessage("LangGraph!!")
    return {"messages": [new_message], "list_field":[30],"extra_field": 30}
graph = (StateGraph(State)
    .add_node("node1",node1)
    .add_node("node2",node2)
    .add_node("node3",node3)
    .set_entry_point("node1")
    .add_edge("node1", "node2")
    .add_edge("node2", "node3")
    .compile())
input_message = {"role": "user", "content": "Hi"}
result = graph.invoke({"messages": [input_message], "list_field": [1,2,3]})
print(result)
# for message in result["messages"]:
#   message.pretty_print()
# print(result["extra_field"])

# 在LangGraph的应⽤当中，State通常都会要保存聊天消息。为此，LangGraph中还提供了⼀个
# langgraph.graph.MessagesState，可以⽤来快速保存消息。
# 他的声明⽅式就是这样的：
# class MessagesState(TypedDict):
#     messages: Annotated[list[AnyMessage], add_messages]
