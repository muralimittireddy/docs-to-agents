import asyncio
import streamlit as st
from dotenv import load_dotenv

from ingest import load_raw_documents
from chunking import chunk_documents
from indexes import RepoIndexes
from tools import SearchTools
from agent import build_agent
from logs import log_interaction_to_file
# from eval import eval_agent, evaluate_log_record

# from pydantic_ai import ModelResponse, TextPart

load_dotenv()

# -------------------------------------------------
# App config
# -------------------------------------------------
st.set_page_config(
    page_title="Git Hub Repo Chat Agent",
    page_icon="🤖",
    layout="centered",
)

st.title("📚 GitHub Repo AI Agent")
st.caption("Ask questions about the repository")

# -------------------------------------------------
# Persistent event loop (CRITICAL)
# -------------------------------------------------
def get_event_loop():
    if "event_loop" not in st.session_state:
        st.session_state.event_loop = asyncio.new_event_loop()
    return st.session_state.event_loop

# -------------------------------------------------
# Agent initialization (cached)
# -------------------------------------------------
@st.cache_resource
def init_agent():
    docs = load_raw_documents()
    chunks = chunk_documents(docs)
    indexes = RepoIndexes(chunks)
    tools = SearchTools(indexes)
    agent = build_agent(tools)
    return agent


agent = init_agent()

# -------------------------------------------------
# Session state
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------------------------
# Render chat history
# -------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# Sync wrapper for async agent
# -------------------------------------------------
def run_agent(prompt: str):
    loop = get_event_loop()
    return loop.run_until_complete(
        agent.run(user_prompt=prompt)
    )

# -------------------------------------------------
# Chat input
# -------------------------------------------------
if prompt := st.chat_input("Ask your question..."):
    # User message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant message
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = run_agent(prompt)
            response_text = result.output
            st.markdown(response_text)

            log_interaction_to_file(
                agent, result.new_messages()
            )

    st.session_state.messages.append(
        {"role": "assistant", "content": response_text}
    )