"""Interface Streamlit pour le chatbot Agentic RAG / garantie."""

import asyncio
import uuid

import streamlit as st
from dotenv import load_dotenv

from app.graph import graph

load_dotenv()
st.set_page_config(page_title="SAV agentique", page_icon="🛠️")
st.title("Assistant après-vente — TP LangGraph")
st.caption(
    "Les manuels et numéros de série de cette démonstration sont fictifs."
)

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "chat" not in st.session_state:
    st.session_state.chat = []

for message in st.session_state.chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

image_ref = st.text_input(
    "Référence de photo (facultatif)", placeholder="img_px200_01"
)
prompt = st.chat_input("Décrivez le problème ou donnez un numéro de série")

if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    initial_state = {
        "request": prompt,
        "image_ref": image_ref.strip() or None,
        "answer": None,
        "history": [{"role": "user", "content": prompt}],
    }
    with st.chat_message("assistant"):
        answer = asyncio.run(graph.ainvoke(initial_state, config=config))
        st.markdown(answer["answer"])
        st.caption(
            f"Catégorie : {answer['category']} · Agent : {answer['agent']}"
        )
    st.session_state.chat.append(
        {"role": "assistant", "content": answer["answer"]}
    )
