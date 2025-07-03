from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from langchain_community.chat_models import ChatTongyi
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)
# 定义⼯具 return_direct=True 表示直接返回⼯具的结果
@tool("devide_tool",return_direct=True)
def devide(a : int,b : int) -> float:
    """计算两个整数的除法。
    Args:
    a (int): 除数
    b (int): 被除数"""
    # ⾃定义错误
    if b == 1:
        raise ValueError("除数不能为1")
    return a/b
print(devide.name)
print(devide.description)
print(devide.args)
# 定义⼯具调⽤错误处理函数
def handle_tool_error(error: Exception) -> str:
    """处理⼯具调⽤错误。
    Args:
    error (Exception): ⼯具调⽤错误"""
    if isinstance(error, ValueError):
        return "除数为1没有意义，请重新输⼊⼀个除数和被除数。"
    elif isinstance(error, ZeroDivisionError):
        return "除数不能为0，请重新输⼊⼀个除数和被除数。"
    return f"⼯具调⽤错误：{error}"
tool_node = ToolNode(
    [devide],
    handle_tool_errors=handle_tool_error
)
agent_with_error_handler = create_react_agent(
    model=llm,
    tools=tool_node
)
result = agent_with_error_handler.invoke({"messages":[{"role":"user","content":"10除以0等于多少？"}]})
# 打印最后的返回结果
# print(result["messages"][-1].content)
print(result)