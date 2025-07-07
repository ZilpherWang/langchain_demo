# 把对联数据保存到redis向量数据库中

import os
import redis
from langchain_community.embeddings import DashScopeEmbeddings

if not os.environ.get("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")

embedding_model = DashScopeEmbeddings(model="text-embedding-v1")

# 保存向量数据库
redis_url = "redis://localhost:6379"

redis_client = redis.from_url(redis_url)
print(redis_client.ping())

from langchain_redis import RedisConfig, RedisVectorStore
config = RedisConfig(index_name="couplet", redis_url=redis_url)
vector_store = RedisVectorStore(embedding_model, config)

lines = []
with open("../resource/couplettest.csv", "r", encoding="utf-8") as file:
    for line in file:
        print(line)
        lines.append(line)
vector_store.add_texts(lines)
