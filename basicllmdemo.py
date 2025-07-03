from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=1.8 # [0,2)之间，越大，结果越随机，越小结果越固定
)

for i in range(5):
    response = llm.invoke([HumanMessage("给一款只能手机起一个酷炫的名字？返回字数4个汉字以内")])
    print(str(i)+ ">>" + response.content)