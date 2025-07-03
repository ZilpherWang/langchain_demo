from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_community.chat_models import ChatTongyi
# 构建阿⾥云百炼⼤模型客户端
llm = ChatTongyi(
model="qwen-plus",
api_key=os.getenv("DASHSCOPE_API_KEY"),
)
# 相⽐Cline客户端配置，只要增加transport属性即可。不过测试stremaable_http有问题。不知道是不是版本的原因。
client = MultiServerMCPClient(
 {
    "mcp-demo-sse": {
        "url": "http://127.0.0.1:8000/sse",
        "transport":"sse"
    },
# "amap-maps": {
# "command": "npx",
# "args": [
# "-y",
# "@amap/amap-maps-mcp-server"
# ],
# "env": {
# "AMAP_MAPS_API_KEY": "451ad40d0e39453600f2a305e31eabe4"
# },
# "transport":"stdio"
# }
 }
)
async def main():
    tools = await client.get_tools()
    print(tools)
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    response = await agent.ainvoke(
     {"messages": [{"role": "user", "content": "今天天气怎么样"}]}
    )
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
