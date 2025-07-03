from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_community.chat_models import ChatTongyi

llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)
checkpointer = InMemorySaver()
def get_weather(city: str) -> str:
    """获取某个城市的天⽓"""
    return f"城市：{city}，天⽓⼀直都是晴天！"
agent = create_react_agent(
    model=llm,
    tools=[get_weather],
    checkpointer=checkpointer
)
# Run the agent
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
# Continue the conversation using the same thread_id
bj_response = agent.invoke(
 {"messages": [{"role": "user", "content": "北京呢？"}]},
config
)
print(bj_response)