"""
Streamlit web app for the University FAQ Chatbot.
Run with: streamlit run app.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
from rag_pipeline import get_existing_collection, answer_question

st.set_page_config(page_title="University FAQ Chatbot", page_icon="🎓")
st.title("🎓 University FAQ Chatbot")
st.caption("Ask me anything about admissions, fees, courses, or campus facilities!")

# Load the vector store once and cache it (so it doesn't reload every message)
@st.cache_resource
def load_collection():
    return get_existing_collection()

collection = load_collection()

# Keep chat history in session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📄 View sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**Source {i}:** {source}")

# Chat input
if question := st.chat_input("Ask a question about the university..."):
    # Show user's question
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate and show answer
    with st.chat_message("assistant"):
        with st.spinner("Searching university documents..."):
            answer, sources = answer_question(collection, question)
        st.markdown(answer)
        with st.expander("📄 View sources"):
            for i, source in enumerate(sources, 1):
                st.markdown(f"**Source {i}:** {source}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })
