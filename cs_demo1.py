from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.chains import RetrievalQA
from langchain.vectorstores import Weaviate
from langchain.embeddings import OpenAIEmbeddings
from langchain_core.tools import retriever
import weaviate

# ========== 模型预设参数（模型参数 + 模型选择 + 回调） ==========
llm = ChatOpenAI(
    model_name="gpt-4",     # ✅ 模型选择
    temperature=0.3,         # ✅ 控制输出创造力
    max_tokens=800,          # ✅ 控制输出长度
    callbacks=[],            # ✅ 可以插入 Token 计数/日志等回调
    streaming=False          # ✅ 可配置流式输出
)

# ========== System Prompt + System Keyword ==========
system_prompt = SystemMessage(content="""
你是一个中文智能客服机器人，请遵循以下规则：
- 所有回答请用简洁中文；
- 如有需要请输出 Markdown 表格；
- 请尽量避免废话，提供有用信息；
- 碰到退货/投诉类问题时必须先道歉；
""")

# ========== 默认记忆（保持上下文） ==========
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# ========== 默认工具列表 ==========
# 示例工具1：天气
weather_tool = Tool(
    name="Weather",
    func=lambda city: f"{city} 当前温度 26°C，晴转多云",
    description="获取天气信息，输入城市名"
)

# 示例工具2：RAG 工具（知识库）
# retriever = Weaviate(
#     client=weaviate.Client("http://localhost:8080"),
#     index_name="Document",
#     embedding=OpenAIEmbeddings(),
#     text_key="text"
# ).as_retriever()
retriever = None

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=False
)

rag_tool = Tool(
    name="Knowledge",
    func=rag_chain.run,
    description="回答与公司相关的业务问题"
)

tools = [weather_tool, rag_tool]

# ========== 初始化 Agent（带 Planning 模式） ==========
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,  # ✅ 使用 ReAct 多轮规划模式
    memory=memory,
    verbose=True
)

# ========== 执行一轮对话（包含全部预设） ==========
user_input = "我想投诉快递太慢了，顺便查下北京天气"
response = agent.run([system_prompt, HumanMessage(content=user_input)])
print("\n🤖 回复：", response)
