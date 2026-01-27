
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
