import asyncio
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.config import get_stream_writer
from langgraph.graph import StateGraph

from langchain_core.messages import HumanMessage
from langgraph.constants import START, END
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from operator import add
import os

# from MultiAgent.coupletLoader import vector_store

nodes = ["guidance", "diagnosis", "error", "doctor"]


llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add]
    type: str


def supervisor_node(state:State):
    print(">>> supervisor_node")
    # writer = get_stream_writer()
    # writer({"node", ">>>> supervisor_node"})
    # 更具用户的问题，对问题进行分类
    prompt = """你是一个专业的智能助手，根据用户的问题，对问题进行分类，并将任务分给其他Agent执行
            如果用户的问题是关于就诊记录的，返回guidance。
            如果用户的问题是关于病情诊断的，返回diagnosis。
            如果用户的问题是关于咨询医生的，返回doctor。
            如果用户的问题是其他的，返回error。
            除了这几个选项外，不要返回其他的内容。
            """
    prompts = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": state["messages"][0]}
    ]
    # 如果已经有type属性了，表示问题已经交由其他节点处理完成了，就可以直接返回
    if "type" in state:
        # writer({"supervisor_step": f"已获得 {state['type']} 智能体处理结果"})
        return {"type": END}
    response = llm.invoke(prompts) 
    # writer({"supervisor_step", f"问题分类结果：{response.content}"})
    if response.content in nodes:
        return {"type": response.content}
    else:
        raise ValueError(f"未知的type: {response.content}")

# def guidance_node(state: State):
#     tools = asyncio.run(client.get_tools())
#     agent = create_react_agent(
#         llm=llm,
#         tools=tools,
#     )
#     response = asyncio.run(agent.ainvoke({"messages": prompts}))
#     # writer({"guidance_result": response["messages"][-1].content})
#     for message in response["messages"]:
#         print("guidance_result:"+message)
#     return {"messages": [HumanMessage(content=response["messages"][-1].content)], "type": "guidance"}

async def guidance_node(state: State):
    print(">>> guidance_node")
    # writer = get_stream_writer()
    # writer({"node": ">>> guidance_node"})
    system_prompt = "你是一个专业的导诊护士，需要根据病人编号，获取病人的就诊记录。并将就诊记录按时间进行倒序排列。整理出前三次就诊信息。请用中文回答。"
    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["messages"][0]}
    ]
    client = MultiServerMCPClient(
        {
            "guidanceServer": {
                "url": "http://localhost:8000/sse",
                "transport": "sse"
            },
        }
    )
    tools = await client.get_tools()
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    response = await agent.ainvoke({"messages": prompts})
    # response = agent.ainvoke({"messages": prompts})
    print(response)
    # writer({"guidance_result": response["messages"][-1].content})
    return {"messages": [HumanMessage(content=response["messages"][-1].content)], "type": "guidance"}



def doctor_node(state: State):
    print(">>> doctor_node")
    # writer = get_stream_writer()
    # writer({"doctor_result": ">>> doctor_node"})

    system_prompt = "你是一个经验丰富的医生，根据用户的问题，给出不超过100字的回答。"
    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["messages"][0]}
    ]
    response = llm.invoke(prompts)
    # writer({"doctor_result": response.content})
    return {"messages": [HumanMessage(content=response.content)], "type": "doctor"}

def error_node(state: State):
    print(">>> error_node")

def diagnosis_node(state: State):
    print(">>> diagnosis_node")
    # writer = get_stream_writer()
    # writer({"node": ">>> diagnosis_node"})
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """
            你是一位经验丰富的医生，你的任务是根据下面的参考信息回答用户的问题。
            参考信息：
                {samples}
            请用中文回答问题
        """),
        ("user", "{text}")
    ])
    query = state["messages"][0]
    if not os.environ.get("DASHSCOPE_API_KEY"):
        os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
    samples = []
    scored_results = vector_store.similarity_search_with_score(query, k=10)
    for doc, score in scored_results:
        samples.append(doc.page_content)
    prompt = prompt_template.invoke({"samples": samples, "text": query})
    print({"diagnosis_prompt": prompt})
    response = llm.invoke(prompt)
    # writer({"diagnosis_result": response.content})
    print({"diagnosis_result": response.content})
    return {"messages": [HumanMessage(content=response.content)], "type": "diagnosis"}

def routing_func(state:State):
    if state["type"] == "diagnosis":
        return "diagnosis_node"
    elif state["type"] == "doctor":
        return "doctor_node"
    elif state["type"] == "guidance":
        return "guidance_node"
    elif state["type"] == END:
        return END
    else:
        return "error_node"
# 构建图
builder = StateGraph(State)
# 添加节点
builder.add_node("supervisor_node", supervisor_node)
builder.add_node("guidance_node", guidance_node)
builder.add_node("diagnosis_node", diagnosis_node)
builder.add_node("error_node", error_node)
builder.add_node("doctor_node", doctor_node)
# 添加边
builder.add_edge(START, "supervisor_node")
builder.add_conditional_edges("supervisor_node", routing_func, ["guidance_node", "diagnosis_node", "error_node", "doctor_node", END])
builder.add_edge("guidance_node", "supervisor_node")
builder.add_edge("diagnosis_node", "supervisor_node")
builder.add_edge("error_node", "supervisor_node")
builder.add_edge("doctor_node", "supervisor_node")

# 构建Graph
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "1"
        }
    }
    response = asyncio.run(graph.ainvoke({"messages": ["查找001号病人的就诊记录"]}, config))
    print(response, 111)
    # 查找001号病人的就诊记录
    # 右膝内侧副韧带损伤怎么处理？
    res = graph.invoke({"messages": ["你们这最牛的医生是谁？"]}, config)
    print(res)