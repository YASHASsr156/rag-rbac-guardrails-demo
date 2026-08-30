"""
Simple Streamlit UI for the RAG + RBAC + Guardrails system.
Wraps the existing simple_rag.py / load_dataset.py logic — no changes to
the core pipeline, just a web front-end on top.

Install:
    pip install streamlit

Run:
    streamlit run app.py

This will open a browser tab automatically (usually http://localhost:8501).
"""

import streamlit as st
from load_dataset import load_documents
from simple_rag import SimpleRAG, guardrail_check_input

st.set_page_config(page_title="RAG + RBAC Demo", page_icon="🔒")

st.title("🔒 RAG System with RBAC + Guardrails")
st.caption("Retrieval-Augmented Generation over internal PDFs & spreadsheets, "
           "with role-based access control and safety guardrails.")


@st.cache_resource
def get_rag():
    docs = load_documents()
    return SimpleRAG(docs), docs


rag, docs = get_rag()

# --- Sidebar: show what's loaded ---
with st.sidebar:
    st.header("📁 Loaded Documents")
    for d in docs:
        st.markdown(f"**{d.source}**")
        st.caption(f"Access: {', '.join(d.allowed_roles)}")
    st.divider()
    st.caption("Try switching roles below and asking the same question — "
               "notice how access changes what gets retrieved.")

# --- Main: role + query input ---
role = st.selectbox("Select your role", ["employee", "manager", "hr", "admin"])
query = st.text_input("Ask a question", placeholder="e.g. What is the salary band for a manager?")

if st.button("Ask", type="primary") and query:
    blocked = guardrail_check_input(query)
    if blocked:
        st.error(f"🚫 {blocked}")
    else:
        with st.spinner("Retrieving relevant documents..."):
            retrieved = rag.retrieve(query, role)

        st.subheader("Retrieved documents")
        if retrieved:
            for d in retrieved:
                st.success(f"✅ {d.source}")
        else:
            st.warning("⚠️ No accessible/relevant documents found for this role.")

        st.subheader("Answer")
        answer = rag.generate_answer(query, retrieved)
        st.write(answer)

st.divider()
st.caption("Sample questions to try: \"How many leave days do I get?\" · "
           "\"What is the salary band for a manager?\" · "
           "\"What is the Q3 budget for the RAG platform project?\"")
