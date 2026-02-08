import streamlit as st
import asyncio
from mcp_use import MCPAgent, MCPClient
from langchain_groq import ChatGroq

# 1. CACHE THE CLIENT: This keeps the server processes ALIVE
@st.cache_resource
def get_mcp_client():
    # Use an internal loop to initialize once
    client = MCPClient.from_config_file("mcp-config.json")
    
    # We use a specialized way to run async init inside a cached function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.create_all_sessions())
    
    return client, loop

# 2. Setup the UI
st.set_page_config(page_title="Fast MCP Agent", layout="wide")

# Persistent state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar ---
with st.sidebar:
    st.header("⚡ Fast Mode Active")
    st.success("MCP Servers are cached & running.")
    if st.button("Restart Servers"):
        st.cache_resource.clear()
        st.rerun()

# --- Load Client (Instant after first time) ---
client, mcp_loop = get_mcp_client()

# --- Agent Function ---
async def run_agent(user_query):
    # LLM doesn't need caching as much, but you could cache it too
    llm = ChatGroq(
        model="qwen/qwen3-32b",
        api_key="",
        temperature=0
    )
    
    agent = MCPAgent(
        llm=llm,
        client=client, # Reusing the cached client
        system_prompt="Use tools only when necessary.",
        max_steps=10,
    )
    return await agent.run(user_query)

# --- Chat Interface ---
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        # Sidebar thinking indicator as requested
        with st.sidebar:
            status = st.status("🧠 Agent Thinking...", expanded=True)
            
        with st.spinner("Consulting MCP tools..."):
            # Reuse the existing loop to avoid 'Loop Closed' errors
            response = mcp_loop.run_until_complete(run_agent(prompt))
            st.markdown(response)
            
        status.update(label="✅ Thought complete", state="complete", expanded=False)
        st.session_state.messages.append({"role": "assistant", "content": response})
