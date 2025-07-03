# 短期记忆通常认为是⽐较紧张的，所以需要定期做清理，防⽌历史消息过多。
# LangGraph的Agent中，提供了⼀个pre_model_hook属性，可以在每次调⽤⼤模型之前触发。通过这个hook，就
# 可以来定期管理短期记忆。
# LangGraph中管理短期记忆的⽅法主要有两种：
# Summarization 总结：⽤⼤模型的⽅式，对短期记忆进⾏总结，然后再把总结的结果作为新的短期记忆。
# Trimming 删除：直接把短期记忆中最旧的消息删除掉。
# LangGraph提供了SummarizationNode函数，⽤于使⽤⼤模型的⽅式对短期记忆进⾏总结。
from langmem.short_term import SummarizationNode
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_community.chat_models import ChatTongyi
from typing import Any

# 使⽤⼤模型对历史信息进⾏总结
llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)
summarization_node = SummarizationNode(
    token_counter=count_tokens_approximately,
    model=llm,
    max_tokens=384,
    max_summary_tokens=128,
    output_messages_key="llm_input_messages",
)
class State(AgentState):
    # 注意：这个状态管理的作⽤是为了能够保存上⼀次总结的结果。这样就可以防⽌每次调⽤⼤模型时，都要重新总结历史信息。
    # 这是⼀个⽐较常⻅的优化⽅式，因为⼤模型的调⽤是⽐较耗时的。
    context: dict[str, Any]

checkpointer = InMemorySaver()
def get_weather(city: str) -> str:
    """获取某个城市的天⽓"""
    return f"城市：{city}，天⽓⼀直都是晴天！"
tools = [get_weather]
agent = create_react_agent(
    model=llm,
    tools=tools,
    pre_model_hook=summarization_node,
    state_schema=State,
    checkpointer=checkpointer,
)

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