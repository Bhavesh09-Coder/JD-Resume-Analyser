https://docs.google.com/document/d/1_kDLjOTt2pl7faahm3ecDIfZsIS4CXR8CUufcg5SzSE/edit?tab=t.0
streamlit
fastapi
uvicorn
langchain
langchain-groq
python-dotenv
requests

GROQ_API_KEY=your_groq_key

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="FastMCP Calculator Server")

class CalcInput(BaseModel):
    a: float
    b: float

@app.get("/tools")
def tools():
    return {
        "calculate_sum": {
            "description": "Add two numbers",
            "input_schema": {"a": "number", "b": "number"},
            "output_schema": {"result": "number"}
        }
    }

@app.post("/tools/calculate_sum")
def calculate_sum(data: CalcInput):
    return {"result": data.a + data.b}

uvicorn mcp_server:app --port 4000

import requests

MCP_SERVER_URL = "http://localhost:4000"

def call_calculator(a, b):
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/calculate_sum",
        json={"a": a, "b": b}
    )
    return response.json()["result"]

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    return ChatGroq(
        model="llama3-8b-8192",
        temperature=0
    )

import streamlit as st
from llm import get_llm
from mcp_client import call_calculator
import re

st.title("🧮 MCP + Groq Calculator")

query = st.text_input("Ask something (e.g., Add 10 and 20)")

if st.button("Ask"):
    llm = get_llm()

    # Simple intent detection
    numbers = re.findall(r"\d+", query)

    if "add" in query.lower() and len(numbers) == 2:
        a, b = map(float, numbers)
        result = call_calculator(a, b)
        st.success(f"Result: {result}")
    else:
        response = llm.invoke(query)
        st.write(response.content)
