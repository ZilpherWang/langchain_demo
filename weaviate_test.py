import weaviate
from weaviate.auth import AuthApiKey

# 连接到本地部署的 Weaviate
client = weaviate.connect_to_local(
    auth_credentials=AuthApiKey("test-secret-key")
)

# 或者自定义连接
client = weaviate.connect_to_custom(
    skip_init_checks=False,
    http_host="43.153.65.218",
    http_port=8080,
    http_secure=False,
    grpc_host="43.153.65.218",
    grpc_port=50051,
    grpc_secure=False,
    # 对应 AUTHENTICATION_APIKEY_ALLOWED_KEYS 中的密钥
    # 注意：此处只需要密钥即可，不需要用户名称
    auth_credentials=AuthApiKey("test-secret-key")
)

# 检查连接是否成功
print(client.is_ready())

# 关闭连接
print(client.close())
