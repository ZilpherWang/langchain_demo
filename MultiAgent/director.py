import os
import asyncio
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.config import get_stream_writer
from langgraph.graph import StateGraph
from operator import add
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver
from langchain_community.embeddings import DashScopeEmbeddings
from langgraph.constants import START, END
from langchain_community.chat_models import ChatTongyi

nodes = ["supervisor", "other", "couplet", "joke", "travel"]

llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add]
    type: str

def supervisor_node(state:State):
    print(">>> supervisor_node")
    writer = get_stream_writer()
    writer({"node", ">>>> supervisor_node"})
    # 更具用户的问题，对问题进行分类
    prompt = """你是一个专业的智能助手，根据用户的问题，对问题进行分类，并将任务分给其他Agent执行
            如果用户的问题是关于旅游的，返回travel。
            如果用户的问题是关于笑话的，返回joke。
            如果用户的问题是关于诗词的，返回couplet。
            如果用户的问题是其他的，返回other。
            """
    prompts = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": state["messages"][0]}
    ]
    # 如果已经有type属性了，表示问题已经交由其他节点处理完成了，就可以直接返回
    if "type" in state:
        writer({"supervisor_step": f"已获得 {state['type']} 智能体处理结果"})
        return {"type": END}
    response = llm.invoke(prompts) 
    writer({"supervisor_step", f"问题分类结果：{response.content}"})
    if response.content in nodes:
        return {"type": response.content}
    else:
        raise ValueError(f"未知的type: {response.content}")


def other_node(state:State):
    print(">>> other_node")
    writer = get_stream_writer()
    writer({"node": ">>>> other_node"})
    return {"messages": [HumanMessage(content="我暂时无法回答这个问题")], "type": "other"}

def couplet_node(state:State):
    print(">>> couplet_node")
    writer = get_stream_writer()
    writer({"node": ">>>> couplet_node"})
    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system", """
                你是一个专业的对联大师，你的任务是根据用户给出的上联，设计一个下联。
                回答时，可以参考下面的参考对联。
                参考对联：
                    {samples}
                请用中文回答问题
            """
        ),
        ("user", "{text}")
    ])
    query = state["messages"][0]
    if not os.environ.get("DASHSCOPE_API_KEY"):
        os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
    
    embedding_model = DashScopeEmbeddings(model="text-embedding-v1")

    redis_url = "redis://localhost:6379"

    from langchain_redis import RedisConfig, RedisVectorStore
    config = RedisConfig(
        index_name="couplet",
        redis_url=redis_url
    )
    vector_store = RedisVectorStore(embedding_model, config=config)

    samples = []
    scored_results = vector_store.similarity_search_score(query, k=10)
    for doc, score in scored_results:
        samples.append(doc.page_content)
    prompt = prompt_template.invoke({"samples": samples, "text": query})
    writer({"couplet_node": prompt.content})
    response = llm.invoke(prompt)
    return {"messages": [HumanMessage(content=response.content)], "type": "couplet"}

def joke_node(state:State):
    print(">>> joke_node")
    writer = get_stream_writer()
    writer({"node": ">>>> joke_node"})
    system_prompt = "你是一个笑话大师，根据用户的问题，写一个不超过100个字的笑话。"
    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["messages"][0]}
    ]
    response = llm.invoke(prompts)
    writer({"joke_result": response.content})
    return {"messages": [HumanMessage(content=response.content)], "type": "joke"}

def travel_node(state:State):
    print(">>> travel_node")
    writer = get_stream_writer()
    writer({"node": ">>>> travel_node"})
    system_prompt = "你是一个旅游助手，根据用户的问题，写一个不超过100个字的旅游计划。"
    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["messages"][0]}
    ]
    client = MultiServerMCPClient(
    {
        # "amap-amap-sse": {
        #     "url": "https://mcp.amap.com/sse?key=451ad40d0e39453600f2a305e31eabe4",
        #     "transport":"streamable_http"
        # },
    "amap-maps": {
    "command": "npx",
    "args": [
    "-y",
    "@amap/amap-maps-mcp-server"
    ],
    "env": {
    "AMAP_MAPS_API_KEY": "451ad40d0e39453600f2a305e31eabe4"
    },
    "transport":"stdio"
    }
    }
    )
    tools = asyncio.run(client.get_tools())
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    response = agent.invoke({"messages": prompts})
    writer({"travel_node": response["messages"][-1].content})
    return {"messages": [HumanMessage(content=response["messages"][-1].content)], "type": "travel"}

def routing_func(state:State):
    if state["type"] == "travel":
        return "travel_node"
    elif state["type"] == "joke":
        return "joke_node"
    elif state["type"] == "couplet":
        return "couplet_node"
    elif state["type"] == END:
        return END
    else:
        return "other_node"
# 构建图
builder = StateGraph(State)
# 添加节点
builder.add_node("supervisor_node", supervisor_node)
builder.add_node("travel_node", travel_node)
builder.add_node("joke_node", joke_node)
builder.add_node("couplet_node", couplet_node)
builder.add_node("other_node", other_node)
# 添加边
builder.add_edge(START, "supervisor_node")
builder.add_conditional_edges("supervisor_node", routing_func, ["travel_node", "joke_node", "couplet_node", "other_node", END])
builder.add_edge("travel_node", "supervisor_node")
builder.add_edge("joke_node", "supervisor_node")
builder.add_edge("couplet_node", "supervisor_node")
builder.add_edge("other_node", "supervisor_node")

# 构建图
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": 1}}
    # for chunk in graph.stream({"messages": ["给我讲一个郭德纲的笑话"]}, config, stream_mode="custom"):
    #     print(chunk)
    
    for chunk in graph.stream({"messages": ["给我规划一条北京通州北苑到霍营的驾车路线"]}, config, stream_mode="custom"):
        print(chunk)
