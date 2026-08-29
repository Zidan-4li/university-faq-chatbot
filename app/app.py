import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
from rag_pipeline import get_existing_collection, answer_question
from database import init_db, log_interaction, update_feedback

st.set_page_config(page_title="University FAQ Chatbot", page_icon="🎓")
st.title("🎓 University FAQ Chatbot")
st.caption("Ask me anything about the BIT program — admissions, fees, courses, or campus facilities!")

init_db()

@st.cache_resource
def load_collection():
    return get_existing_collection()

collection = load_collection()

if "messages" not in st.session_state:
    st.session_state.messages = []

for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📄 View sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**Source {i}:** {source}")
        if "db_id" in message:
            if message.get("feedback_given"):
                if message["feedback_given"] == "helpful":
                    st.caption("👍 You marked this as helpful")
                else:
                    st.caption("👎 You marked this as not helpful")
            else:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("👍 Helpful", key=f"up_{idx}"):
                        update_feedback(message["db_id"], "helpful")
                        message["feedback_given"] = "helpful"
                        st.rerun()
                with col2:
                    if st.button("👎 Not helpful", key=f"down_{idx}"):
                        update_feedback(message["db_id"], "not_helpful")
                        message["feedback_given"] = "not_helpful"
                        st.rerun()

if question := st.chat_input("Ask a question about the university..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching university documents..."):
            answer, sources = answer_question(collection, question)
        st.markdown(answer)
        with st.expander("📄 View sources"):
            for i, source in enumerate(sources, 1):
                st.markdown(f"**Source {i}:** {source}")

    db_id = log_interaction(question, answer, sources)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "db_id": db_id
    })
    st.rerun()
