import asyncio
import json
from fastmcp import Client
from groq import Groq

GROQ_API_KEY = "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"
groq_client = Groq(api_key=GROQ_API_KEY)

# 🔥 This line auto starts the MCP server
mcp_client = Client("server.py")


def ask_groq(messages, tools=None):
    try:
        return groq_client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
    except Exception as e:
        print("Groq error:", e)
        return None


async def chat():
    async with mcp_client:
        print("✅ MCP Server Auto-Started\n")

        tools = await mcp_client.list_tools()

        groq_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema,
                },
            }
            for t in tools
        ]

        messages = []

        while True:
            user_query = input("Ask Query: ")

            if user_query.lower() in ["exit", "quit"]:
                break

            messages.append({"role": "user", "content": user_query})

            response = ask_groq(messages, groq_tools)
            if not response:
                continue

            msg = response.choices[0].message

            # Tool call
            if msg.tool_calls:
                for call in msg.tool_calls:
                    try:
                        args = json.loads(call.function.arguments)

                        print(f"\n🔧 Tool: {call.function.name} → {args}\n")

                        result = await mcp_client.call_tool(
                            call.function.name,
                            args
                        )

                        messages.append(msg)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": str(result.data),
                        })

                    except Exception as e:
                        print("Tool error:", e)

                final = ask_groq(messages)
                if final:
                    answer = final.choices[0].message.content
                    print("\n🤖:", answer, "\n")
                    messages.append({"role": "assistant", "content": answer})

            else:
                answer = msg.content
                print("\n🤖:", answer, "\n")
                messages.append({"role": "assistant", "content": answer})


asyncio.run(chat())

server.py

# gdrive_mcp_server.py
from fastmcp import FastMCP
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import io
import pdfplumber
import fitz

mcp = FastMCP("GDrive MCP Server")

# -----------------------------
# Google Drive Init
# -----------------------------
try:
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
    creds = Credentials.from_service_account_file(
        "credentials.json", scopes=SCOPES
    )
    drive = build("drive", "v3", credentials=creds)
except Exception as e:
    drive = None
    print("❌ Drive init failed:", e)


# -----------------------------
# PDF Extraction
# -----------------------------
def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    text = ""

    # pdfplumber
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print("pdfplumber failed:", e)

    # pymupdf fallback
    if not text.strip():
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text += page.get_text()
        except Exception as e:
            print("pymupdf failed:", e)

    return text or "No text extracted from PDF"


# -----------------------------
# MCP TOOLS
# -----------------------------
@mcp.tool
def list_files() -> list:
    """List files from Google Drive"""
    try:
        if not drive:
            return [{"error": "Drive not initialized"}]

        results = drive.files().list(
            pageSize=10,
            fields="files(id, name)"
        ).execute()

        return results.get("files", [])

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool
def read_file(file_id: str, file_name: str) -> str:
    """Read file and extract text"""
    try:
        if not drive:
            return "Drive not initialized"

        request = drive.files().get_media(fileId=file_id)
        file_bytes = request.execute()

        if file_name.lower().endswith(".pdf"):
            return extract_text_from_pdf_bytes(file_bytes)

        # txt / md
        try:
            return file_bytes.decode("utf-8")
        except Exception:
            return "Unsupported or binary file type"

    except Exception as e:
        return f"Error reading file: {str(e)}"


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    try:
        mcp.run()
    except Exception as e:
        print("❌ MCP Server crashed:", e)





import os
import asyncio
import json
from dotenv import load_dotenv
from groq import Groq

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def mcp_to_groq_tool(tool):
    schema = tool.inputSchema

    # Ensure required exists
    if "required" not in schema:
        schema["required"] = []

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": schema,
        },
    }


async def main():
    transport = StdioTransport(command="python", args=["server.py"])

    async with Client(transport) as mcp:
        tools = await mcp.list_tools()
        groq_tools = [mcp_to_groq_tool(t) for t in tools]

        messages = []

        while True:
            user_input = input("\nYou: ")
            messages.append({"role": "user", "content": user_input})

            response = groq_client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=messages,
                tools=groq_tools,
                tool_choice="auto",
            )

            msg = response.choices[0].message

            if msg.tool_calls:
                for call in msg.tool_calls:
                    tool_name = call.function.name
                    args = json.loads(call.function.arguments)

                    result = await mcp.call_tool(tool_name, args)

                    messages.append(msg)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": str(result),
                    })

                final = groq_client.chat.completions.create(
                    model="qwen/qwen3-32b",
                    messages=messages,
                )

                answer = final.choices[0].message.content
                print("\nAI:", answer)
                messages.append({"role": "assistant", "content": answer})

            else:
                print("\nAI:", msg.content)
                messages.append({"role": "assistant", "content": msg.content})


if __name__ == "__main__":
    asyncio.run(main())

server.py

# server.py
from fastmcp import FastMCP
from pathlib import Path
import pdfplumber
import fitz  # PyMuPDF
from docx import Document
import pytesseract
from PIL import Image
import io

ROOT_DIR = Path(r"C:/Users/mansi/OneDrive/Documents/Resume")

mcp = FastMCP("smart-filesystem-server")


def ocr_pdf(path: Path) -> str:
    text = ""
    doc = fitz.open(path)
    for page in doc:
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        text += pytesseract.image_to_string(img)
    return text


def extract_pdf_text(path: Path) -> str:
    # Try pdfplumber
    try:
        with pdfplumber.open(path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        if text.strip():
            return text
    except:
        pass

    # Try PyMuPDF
    try:
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        if text.strip():
            return text
    except:
        pass

    # Fallback OCR
    return ocr_pdf(path)


def extract_docx_text(path: Path) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


@mcp.tool()
def list_files() -> list:
    """List all files in resume directory"""
    return [str(p.name) for p in ROOT_DIR.iterdir() if p.is_file()]


@mcp.tool()
def read_file(filename: str) -> str:
    """Read file content with smart extraction"""
    path = ROOT_DIR / filename

    if not path.exists():
        return "File not found"

    suffix = path.suffix.lower()

    # Plain text
    if suffix in [".txt", ".md"]:
        return path.read_text(errors="ignore")

    # PDF
    if suffix == ".pdf":
        return extract_pdf_text(path)

    # DOCX
    if suffix == ".docx":
        return extract_docx_text(path)

    # Fallback OCR for images
    try:
        img = Image.open(path)
        return pytesseract.image_to_string(img)
    except:
        return "Unsupported file type"


if __name__ == "__main__":
    mcp.run(transport="stdio")

