import random
from director import graph
config ={
"configurable":{
"thread_id":random.randint(1, 10000)
}
}
query="请给我讲一个郭德纲的笑话"
res = graph.invoke({"messages":["今天天气怎么样"]} ,config, stream_mode="values")
print(res["messages"][-1].content)