import streamlit as st
import asyncio
from mcp_use import MCPAgent, MCPClient
from langchain_groq import ChatGroq

# --- Configuration & Caching ---
@st.cache_resource
def get_mcp_client():
    client = MCPClient.from_config_file("mcp-config.json")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.create_all_sessions())
    return client, loop

# --- UI Setup ---
st.set_page_config(page_title="MCP Assistant", page_icon="💼", layout="wide")

# --- Custom Styling (Black Sidebar, White Font, Professional UI) ---
st.markdown("""
    <style>
    /* Sidebar Background and Font */
    [data-testid="stSidebar"] {
        background-color: #000000;
        color: #ffffff;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Suggestion Cards */
    .suggestion-card {
        background-color: #1a1a1a;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #333;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }

    /* Chat Styling */
    .stChatMessage { border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Content ---
with st.sidebar:
    st.title("💼 Assistant")
    st.markdown("---")
    
    st.subheader("💡 Suggestions")
    
    # Professional Suggestions
    suggestions = [
        "📂 **Filesystem**: 'List the files in my directory.'",
        "📖 **Analysis**: 'Read the contents of requirements.txt.'",
        "🧮 **Math**: 'Calculate the square root of 144 plus 50.'",
        "💬 **General**: 'How can I optimize my Python project?'"
    ]
    
    for s in suggestions:
        st.markdown(f'<div class="suggestion-card">{s}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Connected via Model Context Protocol")

# --- Initialization ---
client, mcp_loop = get_mcp_client()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Main Screen Welcome ---
if not st.session_state.messages:
    st.title("Hi, I'm your MCP Assistant")
    st.markdown("""
    I'm a professional agent equipped with real-time access to your local tools and environment.
    You can ask me to **manage files**, **perform calculations**, or simply ask **general questions**.
    
    *Type a command below to get started.*
    """)
    st.divider()

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Agent Logic ---
async def execute_agent_task(prompt):
    llm = ChatGroq(
        model="qwen/qwen3-32b",
        api_key="123",
        temperature=0
    )
    agent = MCPAgent(
        llm=llm,
        client=client,
        system_prompt="You are a professional assistant. Use MCP tools only when necessary. If a question is normal, answer directly.",
        max_steps=10
    )
    return await agent.run(prompt)

# --- Chat Input & Thinking in Chat ---
if prompt := st.chat_input("Message your assistant..."):
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant Response
    with st.chat_message("assistant"):
        # The spinner/status is now inside the chat
        with st.status("Thinking...", expanded=False) as status:
            try:
                response = mcp_loop.run_until_complete(execute_agent_task(prompt))
                status.update(label="Response generated", state="complete")
            except Exception as e:
                status.update(label="Error", state="error")
                response = f"I apologize, I encountered an error: {str(e)}"

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
