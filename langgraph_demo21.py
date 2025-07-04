# 时间回溯 Time Travel
# 由于大语言模型回答问题的不确定性，基于大语言模型构建的应用，也是充满不确定性的。而对于这种不确定性的系统，就有必要进行更精确的检查。当某一个步骤出现问题时，才能及时发现问题的那个步骤进行重演。为此，LangGraph提供了Time Travel!时间回溯功能，可以保存Graph的运行过程，并q且可以手动指定从Graph的某一个Node开始进行重演。

# 在运行Graph时，需要提供初始的输入消息。
# 运行时，指定threadid线程ID。并且要基于这个线程ID，再指定一个checkpoint检查点。执行后将在每一个Node执行后，生成一个check_point id
# 指定thread_id和check_point_id，进行任务重演。重演前，可以选择更新state，当然，如果没问题，也可以不指定。
from operator import add
import os
from typing_extensions import NotRequired
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
    joke: NotRequired[str]
    author: NotRequired[str]

def author_node(state: State):
    prompt = "需要帮我推荐一位受人们欢迎的作家。只需要给出作家的名字即可。"
    author = llm.invoke(prompt)
    return {"author": author}

def joke_node(state: State):
    prompt = f"用作家：{state['author']}的风格写一个100字以内的笑话。"
    joke = llm.invoke(prompt)
    return {"joke": joke}

builder = StateGraph(State)
builder.add_node(author_node)
builder.add_node(joke_node)

builder.add_edge(START, "author_node")
builder.add_edge("author_node", "joke_node")
builder.add_edge("joke_node", END)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
print(graph)

import uuid
config = {
    "configurable": {
        "thread_id": str(uuid.uuid4()),
    }
}
state = graph.invoke({}, config)
print(state["author"])
print()
print(state["joke"])

states = list(graph.get_state_history(config))
for state in states:
    print(state.next)
    print(state.config["configurable"]["checkpoint_id"])
    print()

# 选定某一个检查点，这里选择author_node,让大模型重新选择作家
selected_state = states[1]
print(selected_state.next)
print(selected_state.values)

# 为了后面的重演，更新state
new_config = graph.update_state(selected_state.config, values={"author": "郭德纲"})
print(new_config)

new_state = graph.invoke(None, new_config)
print(new_state)
