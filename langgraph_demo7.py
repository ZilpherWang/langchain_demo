# 实现了基础的短期记忆管理后，LangGraph还提供了状态管理机制，⽤于保存处理过程中的中间结果。⽽且，这些
# 状态数据，还可以在Tools⼯具中使⽤。
from typing import Annotated
from langgraph.prebuilt import InjectedState, create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.tools import tool
from langchain_community.chat_models import ChatTongyi
# 使⽤⼤模型对历史信息进⾏总结
llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)
class CustomState(AgentState):
    user_id: str

@tool(return_direct=True)
def get_user_info(
    state: Annotated[CustomState, InjectedState]
) -> str:
    """查询⽤户信息."""
    user_id = state["user_id"]
    return "user_123⽤户的姓名：楼兰。" if user_id == "user_123" else "未知⽤户"

agent = create_react_agent(
    model=llm,
    tools=[get_user_info],
    state_schema=CustomState,
)
response = agent.invoke({
    "messages": "查询⽤户信息",
    "user_id": "user_123"
})
print(response)
