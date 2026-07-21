import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
import uuid
import os
import json
load_dotenv()


THREADS_FILE = "chat_threads.json"

def load_threads():
    if os.path.exists(THREADS_FILE):
        with open(THREADS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_threads(threads):
    with open(THREADS_FILE, "w", encoding="utf-8") as f:
        json.dump(threads, f)

def add_thread(thread_id):
    threads = load_threads()
   
    threads.insert(0, {"id": thread_id, "label": f"Chat {thread_id[:8]}"})
    save_threads(threads)

if "thread_id" not in st.session_state:
    threads = load_threads()
    if threads:
        st.session_state.thread_id = threads[0]["id"]
    else:
        st.session_state.thread_id = str(uuid.uuid4())
        add_thread(st.session_state.thread_id)



st.title("NpCI Chatbot")

with st.sidebar:
    st.header("Chat Threads")
    if st.button("New Thread"):
        st.session_state.thread_id = str(uuid.uuid4())
        add_thread(st.session_state.thread_id)
        st.rerun()

    threads = load_threads()

    if threads:
        labels = [t["label"] for t in threads]
        ids = [t["id"] for t in threads]

        current_index = ids.index(st.session_state.thread_id)

        picked_label = st.selectbox("Previous Chats", labels, index=current_index)

        picked_index = ids[labels.index(picked_label)]
        if picked_index != st.session_state.thread_id:
            st.session_state.thread_id = picked_index
            st.rerun()
  

THREAD_ID = st.session_state.thread_id
config = {"configurable": {"thread_id": THREAD_ID}}
st.caption(f"Thread ID: {THREAD_ID}")

@st.cache_resource
def get_agent():   

    llm = ChatOpenAI(model_name="gpt-4.1-mini")

    agent = create_agent(
        model=llm,
        tools=[TavilySearch()],
        checkpointer=InMemorySaver()
    )   

    return agent

agent = get_agent()

snapshot = agent.get_state(config=config)

if snapshot.values.get("messages"):
    print(f"Snapshot: {snapshot.values['messages']}")

for message in snapshot.values.get("messages", []):
    if message.type == 'human':
        with st.chat_message("user"):
            st.markdown(message.content)
    elif message.type == 'ai' and message.content:
        with st.chat_message("assistant"):
            st.markdown(message.content)

if prompt := st.chat_input("Enter your prompt:"):

    with st.spinner("Generating response..."):
        agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }, config=config
        )

        st.rerun()

