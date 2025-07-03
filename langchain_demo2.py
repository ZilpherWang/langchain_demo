import datetime
from langchain.tools import tool
from config.load_key import load_key
from langchain_community.chat_models import ChatTongyi
# 构建阿⾥云百炼⼤模型客户端
llm = ChatTongyi(
model="qwen-plus",
api_key=os.getenv("DASHSCOPE_API_KEY"),
)
# 定义⼯具 注意要添加注释
@tool
def get_current_date():
    """获取今天⽇期"""
    return datetime.datetime.today().strftime("%Y-%m-%d")
# ⼤模型绑定⼯具
llm_with_tools = llm.bind_tools([get_current_date])
# ⼯具容器
all_tools = {"get_current_date": get_current_date}
# 把所有消息存到⼀起
query = "今天是⼏⽉⼏号"
messages = [query]
# 询问⼤模型。⼤模型会判断需要调⽤⼯具，并返回⼀个⼯具调⽤请求
ai_msg = llm_with_tools.invoke(messages)
print(ai_msg)
messages.append(ai_msg)
# 打印需要调⽤的⼯具
print(ai_msg.tool_calls)
if ai_msg.tool_calls:
    for tool_call in ai_msg.tool_calls:
        selected_tool = all_tools[tool_call["name"].lower()]
        tool_msg = selected_tool.invoke(tool_call)
        messages.append(tool_msg)
        llm_with_tools.invoke(messages).content