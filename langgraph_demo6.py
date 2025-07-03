from langchain_core.messages.utils import (
    trim_messages,
    count_tokens_approximately
)
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_community.chat_models import ChatTongyi

# 使⽤⼤模型对历史信息进⾏总结
llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)
# This function will be called every time before the node that calls LLM
def pre_model_hook(state):
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=384,
        start_on="human",
        end_on=("human", "tool"),
    )

    return {"llm_input_messages": trimmed_messages}

checkpointer = InMemorySaver()
agent = create_react_agent(
    model=llm,
    tools=[],
    pre_model_hook=pre_model_hook,
    checkpointer=checkpointer,
)
# 实现了基础的短期记忆管理后，LangGraph还提供了状态管理机制，⽤于保存处理过程中的中间结果。⽽且，这些
# 状态数据，还可以在Tools⼯具中使⽤。
config = {
    "configurable": {
        "thread_id": "1"
    }
}
cs_response = agent.invoke(
 {"messages": [{"role": "user", "content": "⻓沙天⽓怎么样？"}]},
config
)
print(cs_response)