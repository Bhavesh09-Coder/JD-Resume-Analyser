import os
import json
import asyncio
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
load_dotenv()

FILESYSTEM_PATH = r"C:/Users/mansi/OneDrive/Documents/Resume"

SERVERS = {
    "filesystem": {
        "transport": "stdio",
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            FILESYSTEM_PATH
        ],
    }
}

SYSTEM_PROMPT = """
You have access to filesystem tools.

Rules:
- If user asks to list, read, write, create, delete files → MUST call tool.
- After tool runs, return only final answer.
- If user asks general question → answer normally.
"""

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.set_page_config(page_title="Groq Qwen MCP Filesystem", page_icon="📂")
st.title("📂 Groq Qwen + MCP Filesystem Chat")

# ─────────────────────────────────────────────
# INIT (run once)
# ─────────────────────────────────────────────
if "init" not in st.session_state:

    # 1) Groq Qwen model
    llm = ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0
    )

    # 2) MCP client (filesystem only)
    client = MultiServerMCPClient(SERVERS)
    tools = asyncio.run(client.get_tools())

    st.session_state.llm = llm
    st.session_state.tools = tools
    st.session_state.tool_map = {t.name: t for t in tools}
    st.session_state.llm_with_tools = llm.bind_tools(tools)

    # 3) Conversation
    st.session_state.history = [SystemMessage(content=SYSTEM_PROMPT)]
    st.session_state.init = True

# ─────────────────────────────────────────────
# RENDER CHAT
# ─────────────────────────────────────────────
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)

    elif isinstance(msg, AIMessage):
        # Skip intermediate tool call messages
        if getattr(msg, "tool_calls", None):
            continue
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# ─────────────────────────────────────────────
# USER INPUT
# ─────────────────────────────────────────────
query = st.chat_input("Ask something...")

if query:
    # Show user
    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.history.append(HumanMessage(content=query))

    # First pass → let model decide tool or not
    first = asyncio.run(
        st.session_state.llm_with_tools.ainvoke(st.session_state.history)
    )

    tool_calls = getattr(first, "tool_calls", None)

    # ─────────────────────────────────────────
    # CASE 1: No tool needed
    # ─────────────────────────────────────────
    if not tool_calls:
        with st.chat_message("assistant"):
            st.markdown(first.content)
        st.session_state.history.append(first)

    # ─────────────────────────────────────────
    # CASE 2: Tool required
    # ─────────────────────────────────────────
    else:
        # 1) Save assistant message WITH tool calls (do not render)
        st.session_state.history.append(first)

        # 2) Execute tools
        tool_messages = []

        for tc in tool_calls:
            name = tc["name"]
            args = tc.get("args") or {}

            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except:
                    pass

            tool = st.session_state.tool_map[name]
            result = asyncio.run(tool.ainvoke(args))

            tool_messages.append(
                ToolMessage(
                    tool_call_id=tc["id"],
                    content=json.dumps(result)
                )
            )

        st.session_state.history.extend(tool_messages)

        # 3) Final answer after tool output
        final = asyncio.run(
            st.session_state.llm.ainvoke(st.session_state.history)
        )

        with st.chat_message("assistant"):
            st.markdown(final.content)

        st.session_state.history.append(
            AIMessage(content=final.content)
        )

