import os
import asyncio
from dotenv import load_dotenv
from fastmcp import Client
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

ROOT_PATH = r"C:/Users/mansi/OneDrive/Documents/Resume"

SERVERS = {
    "filesystem": {
        "transport": "stdio",
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            ROOT_PATH
        ],
        "cwd": ROOT_PATH,
    }
}


SYSTEM_PROMPT = """
You are a resume assistant.

When user asks to:
- list files → say: ACTION:LIST_FILES
- read a file → say: ACTION:READ_FILE:filename
- analyze resume → say: ACTION:ANALYZE:filename

Only respond with these ACTION tags when file access is needed.
Otherwise answer normally.
"""


async def main():
    config = {"mcpServers": SERVERS}

    async with Client(config) as mcp:
        print("✅ MCP Connected")

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )

        chat = model.start_chat()

        while True:
            user_query = input("\nUser: ")
            response = chat.send_message(user_query).text.strip()

            # 🔥 Router logic (YOU control tools, not Gemini)
            if response.startswith("ACTION:LIST_FILES"):
                result = await mcp.call_tool("list_directory", {"path": "."})
                print("\nFiles:\n", result)

            elif response.startswith("ACTION:READ_FILE"):
                filename = response.split(":")[2]
                result = await mcp.call_tool("read_file", {"path": filename})
                print("\nFile Content:\n", result)

            elif response.startswith("ACTION:ANALYZE"):
                filename = response.split(":")[2]
                file_data = await mcp.call_tool("read_file", {"path": filename})

                analysis = chat.send_message(
                    f"Analyze this resume for Data Scientist role:\n{file_data}"
                ).text

                print("\nAnalysis:\n", analysis)

            else:
                print("\nAssistant:", response)


if __name__ == "__main__":
    asyncio.run(main())
