from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcpdemo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    print(f"mcp demo called: add({a}, {b})")
    return a + b

@mcp.tool()
def weather(city: str):
    """获取某个城市的天气
    Args:
        city: 城市名称
    Returns:
        str: 天气情况
    """
    return "城市" + city + ",今天天气不错"

@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Greet a person by name.
    """
    print(f"mcp demo called: greeting {name}")
    return f"Hello {name}"

if __name__ == "__main__":
    mcp.run(transport="sse")