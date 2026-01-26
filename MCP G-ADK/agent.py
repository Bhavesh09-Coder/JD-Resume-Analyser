# from google.adk.agents.llm_agent import LlmAgent
# from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams
# from dotenv import load_dotenv

# load_dotenv()

# ABSOLUTE_FILE_PATH = r"C:/Users/mansi/OneDrive/Documents/Resume"

# root_agent = LlmAgent(
#     model='gemini-2.5-flash',
#     name='filesystem_assistant_agent',
#     instruction="""
#     Help the user manage their files.
#     You can list files, read files, and analyze resume content.
#     """,
#     tools=[
#         McpToolset(
#             connection_params=StdioConnectionParams(
#                 server_params={
#                     "command": "npx",
#                     "args": [
#                         "-y",
#                         "@modelcontextprotocol/server-filesystem",
#                         ABSOLUTE_FILE_PATH
#                     ],
#                 }
#             )
#         )
#     ],
# )

import os
from dotenv import load_dotenv

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams

load_dotenv()

# Use Groq endpoint
os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"

ABSOLUTE_FILE_PATH = r"C:/Users/mansi/OneDrive/Documents/Resume"

root_agent = LlmAgent(
    model="llama-3.3-70b-versatile",  # ✅ Valid Groq model
    name="filesystem_assistant_agent",
    instruction="""
    Help the user manage their files.
    You can list files, read files, and analyze resume content.
    """,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params={
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        ABSOLUTE_FILE_PATH,
                    ],
                }
            )
        )
    ],
)
