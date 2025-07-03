from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from langchain_community.chat_models import ChatTongyi
import datetime
import os
llm = ChatTongyi(
model="qwen-plus",
api_key=os.getenv("DASHSCOPE_API_KEY"),
)
# 定义⼯具 注意要添加注释
@tool
def get_current_date():
    """获取今天⽇期"""
    return datetime.datetime.today().strftime("%Y-%m-%d")
agent = create_react_agent(
    model=llm,
    tools=[get_current_date],
    prompt="You are a helpful assistant",
)
result = agent.invoke({"messages":[{"role":"user","content":"今天是⼏⽉⼏号"}]})
print(result)