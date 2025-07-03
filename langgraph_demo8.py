# ⻓期记忆通常认为是⽐较充⾜的记忆空间，因此使⽤时，可以⽐短期记忆更加粗犷，不太需要实时关注内存空间⼤
# ⼩。
# ⾄于使⽤⽅式，和短期记忆差不太多。主要是通过Agent的store属性指定⼀个 实现类就可以了。
# 与短期记忆最⼤的区别在于，短期记忆通过thread_id来区分不同的对话，⽽⻓期记忆则通过namespace来区分不
# 同的命名空间。
from langchain_core.runnables import RunnableConfig
from langgraph.config import get_store
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langchain_core.tools import tool
from langchain_community.chat_models import ChatTongyi

llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)
# 定义⻓期存储
store = InMemoryStore()
# 添加⼀些测试数据。 users是命名空间，user_123是key，后⾯的JSON数据是value
store.put(
    ("users",),
    "user_123",
    {
        "name": "楼兰",
        "age": "33",
    }
)
#定义⼯具
@tool(return_direct=True)
def get_user_info(config: RunnableConfig) -> str:
    """查找⽤户信息"""
    # 获取⻓期存储。获取到了后，这个存储组件可读也可写
    store = get_store()
    # store.put(
    # ("users",),
    # "user_456",
    # {
    # "name": "楼兰",
    # "age": "33",
    # }
    # )
    # 获取配置中的⽤户ID
    user_id = config["configurable"].get("user_id")
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"

agent = create_react_agent(
    model=llm,
    tools=[get_user_info],
    store=store
)
# Run the agent
response = agent.invoke(
    {"messages": [{"role": "user", "content": "查找⽤户信息"}]},
    config={"configurable": {"user_id": "user_123"}}
)
print(response)