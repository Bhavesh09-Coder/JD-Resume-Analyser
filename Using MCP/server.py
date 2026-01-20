from fastmcp import FastMCP

mcp = FastMCP("calculator-mcp")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=3333
    )
