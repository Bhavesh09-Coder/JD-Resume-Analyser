import os
import json
import asyncio
from dotenv import load_dotenv
from groq import Groq

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ABSOLUTE_FILE_PATH = r"C:/Users/mansi/OneDrive/Documents/Resume"


def ask_qwen(messages, tools):
    return groq_client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )


def convert_tools(mcp_tools):
    tools = []

    for t in mcp_tools:
        # Case 1: dict
        if isinstance(t, dict):
            name = t.get("name")
            description = t.get("description", "")
            schema = t.get("inputSchema", {})

        # Case 2: tuple -> (name, schema)
        elif isinstance(t, tuple):
            name = t[0]
            raw = t[1] if len(t) > 1 else {}
            raw = raw or {}

            description = raw.get("description", "") if isinstance(raw, dict) else ""
            schema = raw.get("inputSchema", {}) if isinstance(raw, dict) else {}

        else:
            continue

        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": schema if schema else {
                    "type": "object",
                    "properties": {}
                },
            }
        })

    return tools



async def main():
    server = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            ABSOLUTE_FILE_PATH,
        ],
    )

    # 🔥 THIS IS THE MAGIC LINE EVERYONE MISSES
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as mcp:

            mcp_tools = await mcp.list_tools()
            tools = convert_tools(mcp_tools)

            print("✅ MCP tools:", [t["function"]["name"] for t in tools])

            messages = [
                {"role": "system", "content": "Use filesystem tools to read and analyze resumes."}
            ]

            while True:
                user_query = input("\nAsk: ")
                messages.append({"role": "user", "content": user_query})

                response = ask_qwen(messages, tools)
                msg = response.choices[0].message

                if msg.tool_calls:
                    messages.append(msg)

                    for call in msg.tool_calls:
                        name = call.function.name
                        args = json.loads(call.function.arguments)

                        print(f"\n🛠 Tool call: {name}")
                        result = await mcp.call_tool(name, args)

                        messages.append({
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": str(result)
                        })

                    final = ask_qwen(messages, tools)
                    answer = final.choices[0].message.content
                    print("\n✅ Answer:\n", answer)

                    messages.append({"role": "assistant", "content": answer})

                else:
                    print("\n✅ Answer:\n", msg.content)
                    messages.append({"role": "assistant", "content": msg.content})


if __name__ == "__main__":
    asyncio.run(main())
