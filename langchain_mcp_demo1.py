from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

from langchain.tools import tool

@tool(description="规划行车路线")
def get_route_plan(origin_city:str, target_city:str):
    """规划行车路线
    Args:
        origin_city: 出发城市
        target_city: 目标城市
    """
    result = f"从城市 {origin_city} 出发，到达目标城市 {target_city} ，使用意念传送，只需要三分钟即可到达。"
    print(">>>>>> get_route_plan >>>>>>" + result)
    return result

# 大模型绑定工具
llm_with_tools = llm.bind_tools([get_route_plan])
# 工具容器
all_tools = {"get_route_plan": get_route_plan}
# 把所有消息存在一起
query = "帮我规划一条从长沙到北京的自驾路线"
messages = [query]
# 询问大模型，大模型会判断需要调用工具，并返回一个工具调用请求
ai_msg = llm_with_tools.invoke(messages)
print(ai_msg)
messages.append(ai_msg)
# 打印需要调用的工具
print(ai_msg.tool_calls)
if ai_msg.tool_calls:
    for tool_call in ai_msg.tool_calls:
        selected_tool = all_tools[tool_call["name"].lower()]
        tool_msg = selected_tool.invoke(tool_call)
        messages.append(tool_msg)
print(llm_with_tools.invoke(messages).content)
