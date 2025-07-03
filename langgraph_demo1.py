from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
# 创建访问OpenAI的Model。
model = init_chat_model("gpt-4o-mini",model_provider="openai")
agent = create_react_agent(
    model=model,
    tools=[],
    prompt="You are a helpful assistant",
)
agent.invoke({"messages":[{"role":"user","content":"你是谁？能帮我解决什么问题？"}]})