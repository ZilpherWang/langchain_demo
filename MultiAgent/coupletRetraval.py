import os
from langchain_core.prompts import ChatPromptTemplate

import redis
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi

query = "帮我对个对联：瑞雪兆丰年"

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
prompt = prompt_template.invoke({"samples": samples, "text": query})

print(prompt)
llm = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY")
)

print(llm.invoke(prompt))