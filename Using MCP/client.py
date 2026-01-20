# import asyncio
# import os
# from dotenv import load_dotenv

# from fastmcp import Client
# from langchain_groq import ChatGroq

# load_dotenv()

# def mcp_to_openai_tools(mcp_tools):
#     """
#     Convert MCP tool objects to OpenAI/Groq function schema
#     """
#     openai_tools = []

#     for tool in mcp_tools:
#         openai_tools.append({
#             "type": "function",
#             "function": {
#                 "name": tool.name,
#                 "description": tool.description,
#                 "parameters": tool.inputSchema
#             }
#         })

#     return openai_tools


# async def main():
#     llm = ChatGroq(
#         groq_api_key=os.getenv("GROQ_API_KEY"),
#         model="llama-3.1-8b-instant"
#     )

#     async with Client("http://127.0.0.1:3333/mcp") as client:

#         # 1️⃣ Get MCP-native tools
#         mcp_tools = await client.list_tools()

#         # 2️⃣ Convert MCP tools → OpenAI/Groq format
#         tools = mcp_to_openai_tools(mcp_tools)

#         # 3️⃣ Bind tools to LLM
#         llm_with_tools = llm.bind(tools=tools)

#         # 4️⃣ Invoke
#         response = llm_with_tools.invoke("What is 10 + 20?")

#         print(response.content)

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
import os
from dotenv import load_dotenv

from fastmcp import Client
from langchain_groq import ChatGroq

load_dotenv()


def mcp_to_openai_tools(mcp_tools):
    """
    Convert MCP-native tools to OpenAI/Groq function format
    """
    tools = []
    for tool in mcp_tools:
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        })
    return tools


async def main():
    # 1️⃣ Initialize LLM
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant"
    )

    # 2️⃣ Connect to MCP HTTP endpoint
    async with Client("http://127.0.0.1:3333/mcp") as client:

        # 3️⃣ Fetch MCP-native tools
        mcp_tools = await client.list_tools()

        # 4️⃣ Convert tools to Groq/OpenAI format
        tools = mcp_to_openai_tools(mcp_tools)

        # 5️⃣ Bind tools to LLM
        llm_with_tools = llm.bind(tools=tools)

        # 6️⃣ Ask question (force explanation)
        response = llm_with_tools.invoke(
            "Use the calculator tool to compute 10 + 20 and clearly explain the final answer."
        )

        # 7️⃣ Print output
        print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
