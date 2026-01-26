import os
import re
import asyncio
from io import BytesIO
from dotenv import load_dotenv
from fastmcp import Client
import google.generativeai as genai
import pdfplumber

# ----------------- CONFIG -----------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

ROOT_PATH = r"C:/Users/mansi/OneDrive/Documents/Resume"

SERVERS = {
    "filesystem": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", ROOT_PATH],
        "cwd": ROOT_PATH,
    }
}

SYSTEM_PROMPT = """
You are a Resume Analysis Assistant.

Rules:
- If user asks to list files → respond exactly: ACTION:LIST
- If user asks to read/open/load a resume → respond exactly: ACTION:READ:<filename>
- For resume analysis, JD matching, summary, skills, gaps → use the resume content already shared.
- If JD is provided, compare JD vs Resume and give structured analysis.

Always respond concisely and professionally.
"""

# ----------------- GLOBAL MEMORY -----------------
LAST_RESUME_TEXT = ""
LAST_RESUME_NAME = ""

# ----------------- HELPERS -----------------
def extract_pdf_text(pdf_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def get_file_bytes(result):
    part = result.content[0]
    if hasattr(part, "blob") and part.blob:
        return part.blob
    return part.text.encode()

def extract_filename(action: str) -> str:
    return action.split("ACTION:READ:")[-1].strip()

def is_jd(text: str) -> bool:
    keywords = ["job description", "requirements", "responsibilities", "role"]
    return any(k in text.lower() for k in keywords)

# ----------------- MAIN -----------------
async def main():
    global LAST_RESUME_TEXT, LAST_RESUME_NAME

    async with Client({"mcpServers": SERVERS}) as mcp:
        print("✅ MCP Connected")

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )

        chat = model.start_chat()

        while True:
            user_input = input("\nUser: ").strip()

            if not user_input:
                continue

            response = chat.send_message(user_input).text.strip()

            # -------- LIST FILES --------
            if response == "ACTION:LIST":
                result = await mcp.call_tool("list_directory", {"path": "."})
                print("\n📂 Files:\n", result.content[0].text)
                continue

            # -------- READ FILE --------
            if response.startswith("ACTION:READ"):
                filename = extract_filename(response)
                result = await mcp.call_tool("read_file", {"path": filename})
                file_bytes = get_file_bytes(result)

                if filename.lower().endswith(".pdf"):
                    LAST_RESUME_TEXT = extract_pdf_text(file_bytes)
                else:
                    LAST_RESUME_TEXT = file_bytes.decode(errors="ignore")

                LAST_RESUME_NAME = filename

                chat.send_message(
                    f"""
This is the resume content of {filename}.
Remember it for all future analysis.

RESUME:
{LAST_RESUME_TEXT}
"""
                )

                print(f"\n✅ Resume loaded: {filename}")
                continue

            # -------- JD MATCH / ANALYSIS --------
            if is_jd(user_input):
                analysis_prompt = f"""
Compare the following Resume with the Job Description.

RESUME:
{LAST_RESUME_TEXT}

JOB DESCRIPTION:
{user_input}

Provide:
1. Candidate Summary
2. Key Skills
3. Relevant Experience
4. JD Match Percentage
5. Skill Gaps
6. Final Verdict (Fit / Partial / Not Fit)
"""
                analysis = chat.send_message(analysis_prompt).text
                print("\n📊 Analysis:\n", analysis)
                continue

            # -------- NORMAL QUERY --------
            print("\nAssistant:", response)

# ----------------- RUN -----------------
if __name__ == "__main__":
    asyncio.run(main())

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
