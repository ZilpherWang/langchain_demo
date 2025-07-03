# 五、Human-in-the-loop⼈类监督
# 这也是LangGraph的Agent中⾮常核⼼的⼀个功能。
# 在Agent的⼯作过程中，有⼀个问题是⾮常致命的。就是Agent可以添加Tools⼯具，但是要不要调⽤⼯具，却完全
# 是由Agent⾃⼰决定的。
# 这就会导致Agent在⾯对⼀些问题时，可能会出现错误的判断。
# 为了解决这个问题，LangGraph提供了Human-in-the-loop的功能。在Agent进⾏⼯具调⽤的过程中，允许⽤户进
# ⾏监督。这就需要中断当前的执⾏任务，等待⽤户输⼊后，再重新恢复任务。 
# 在实现时，LangGraph提供了interruput()⽅法添加⼈类监督。监督时需要中断当前任务，所以通常是和stream流
# 式⽅法配合使⽤。
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_community.chat_models import ChatTongyi
# An example of a sensitive tool that requires human review / approval

llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)
@tool(return_direct=True)
def book_hotel(hotel_name: str):
    """预定宾馆"""
    response = interrupt(
    f"正准备执⾏'book_hotel'⼯具预定宾馆，相关参数名： {{'hotel_name': {hotel_name}}}. "
    "请选择OK，表示同意，或者选择edit，提出补充意⻅."
    )
    if response["type"] == "OK":
        pass
    elif response["type"] == "edit":
        hotel_name = response["args"]["hotel_name"]
    else:
        raise ValueError(f"Unknown response type: {response['type']}")
    return f"成功在 {hotel_name} 预定了⼀个房间."

checkpointer = InMemorySaver()
agent = create_react_agent(
    model=llm,
    tools=[book_hotel],
    checkpointer=checkpointer,
)
config = {
    "configurable": {
        "thread_id": "1"
    }
}


# 执⾏完成后，会在book_hotel执⾏过程中，输出⼀个Interrupt响应，表示当前正在等待⽤户输⼊确认。
# 接下来，可以通过Agent提交⼀个Command请求，来继续完成之前的任务。
# 需要注意的是，在这个示例中，Agent只会⼀直等待⽤户输⼊。如果等待时间过⻓，后续请求就⽆法恢复了。

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "帮我在图灵宾馆预定⼀个房间"}]},
    config
):
    print(chunk)
    print("\n")

from langgraph.types import Command
for chunk in agent.stream(
    # Command(resume={"type": "OK"}),
    Command(resume={"type": "edit", "args": {"hotel_name": "三号宾馆"}}),
    config
    ):
    print(chunk)
    print(chunk['tools']['messages'][-1].content)
    print("\n")
