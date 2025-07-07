import os
import redis

from MultiAgent.coupletLoader import vector_store

if not os.environ.get("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")

from langchain_community.embeddings import DashScopeEmbeddings

embedding_model = DashScopeEmbeddings(model="text-embedding-v1")

# 3，保存向量数据库
redis_url = "redis://localhost:6379"
redis_client = redis.from_url(redis_url)
from langchain_redis import RedisConfig, RedisVectorStore
config = RedisConfig(
    index_name="diagnosis",
    redis_url=redis_url
)
vector_store = RedisVectorStore(embedding_model, config=config)

if __name__ == "__main__":
    lines = []
    with open("../resource/test_encyclopedia.csv", "r", encoding="utf-8") as file:
        for line in file:
            print(line)
            lines.append(line)
    vector_store.add_texts(lines)