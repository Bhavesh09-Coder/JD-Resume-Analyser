import asyncio
import os
from dotenv import load_dotenv

from fastmcp import Client
from langchain_groq import ChatGroq

load_dotenv()


def mcp_to_openai_tools(mcp_tools):
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        }
        for tool in mcp_tools
    ]


async def main():
    # 1️⃣ Initialize LLM
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant"
    )

    # 2️⃣ Connect to MCP
    async with Client("http://127.0.0.1:3333/mcp") as client:

        # 3️⃣ Fetch MCP tools
        mcp_tools = await client.list_tools()
        tools = mcp_to_openai_tools(mcp_tools)

        # 4️⃣ Ask question (LLM decides tool usage)
        response = llm.invoke(
            "Add 20 and 20 using calculator",
            tools=tools
        )

        # 5️⃣ LLM tool call → MCP execution
        if response.tool_calls:
            tool_call = response.tool_calls[0]

            print("LLM decided to call tool:", tool_call["name"])
            print("Arguments:", tool_call["args"])

            result = await client.call_tool(
                tool_call["name"],
                tool_call["args"]
            )

            print("Tool result:", result)
        else:
            print("No tool call made")
            print(response.content)


if __name__ == "__main__":
    asyncio.run(main())


# import asyncio
# import os
# from dotenv import load_dotenv

# from fastmcp import Client
# from langchain_groq import ChatGroq

# load_dotenv()


# def mcp_to_openai_tools(mcp_tools):
#     return [
#         {
#             "type": "function",
#             "function": {
#                 "name": tool.name,
#                 "description": tool.description,
#                 "parameters": tool.inputSchema
#             }
#         }
#         for tool in mcp_tools
#     ]


# async def main():
#     llm = ChatGroq(
#         groq_api_key=os.getenv("GROQ_API_KEY"),
#         model="llama-3.1-8b-instant"
#     )

#     async with Client("http://127.0.0.1:3333/mcp") as client:

#         # 1️⃣ Get tools
#         mcp_tools = await client.list_tools()
#         tools = mcp_to_openai_tools(mcp_tools)

#         # 2️⃣ Ask model (with tools)
#         response = llm.invoke(
#             "Use the calculator tool to compute 10 + 20.",
#             tools=tools
#         )

#         # 3️⃣ Check if model requested a tool
#         if response.tool_calls:
#             tool_call = response.tool_calls[0]

#             # 4️⃣ Call MCP tool
#             result = await client.call_tool(
#                 tool_call["name"],
#                 tool_call["args"]
#             )

#             # 5️⃣ Send tool result back to LLM
#             final_response = llm.invoke(
#                 f"The tool returned {result}. Explain the final answer clearly."
#             )

#             print(final_response.content)
#         else:
#             print(response.content)


# if __name__ == "__main__":
#     asyncio.run(main())
