import os
# 制定OpenAI的API_KEY。
# 没花钱所以调不通，流泪。。。  
from langchain.chat_models import init_chat_model
# 创建访问OpenAI的Model。
model = init_chat_model("gpt-4o-mini",model_provider="openai")
# openai在国内是⽆法直接访问的，需要科学上⽹。这⾥指定base_url是因为使⽤的是openai的国内代理，2233.ai。
# model = init_chat_model("gpt-4omini",model_provider="openai",base_url="https://api.gptsapi.net/v1")
model.invoke("你是谁？能帮我解决什么问题？")