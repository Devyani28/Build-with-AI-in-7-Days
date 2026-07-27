#imports
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
#effective prompt handlimng
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
#threadId: unique context
from uuid import uuid4
from auth import authenticate_user

"""
Author: Devyani28
Date: 2026-07-27
Description: support chatbot
"""

#at every step chk compilationErr of py file: py_compile supportApp.py
#run app: streamlit run suportApp.py
#streamlit style config in .stteamlit/config.toml

#app start, welcom
#Day1 : initi- only messages
# def init_session():
#     # Initialize messages in session state
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
#     # Add initial assistant greeting, if no messages exist
#     if not st.session_state.messages:
#         st.session_state.messages = [
#             AIMessage(content="Hi! Ask me anything.")
#         ]
#Day2: advance chat: msg, email, role, threadId, history
def init_session():
    """
    Initialize Streamlit session state for authentication
    and multi-conversation support.
    """
    st.session_state.setdefault("conversations", {})
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("user_email", None)
    st.session_state.setdefault("user_role", None)
    st.session_state.setdefault("conversation_id", None)  


#load all history on evry rerun
def render_history():
    """
    show history: Converts stored messages into visible chat bubbles according to their roles
    """
    for msg in st.session_state.messages:
        # Decide chat role based on message type
        if isinstance(msg, HumanMessage):
            role = "user"
        else:
            role = "assistant"
        # Render message bubble
        with st.chat_message(role):
            st.markdown(msg.content)


#handel every prompt from user        
#Day2 # def chat_round(llm, user_input):
def chat_round(chain, user_input):
    """
    Handles one chat turn:
    1. Add user message to history
    2. Send full conversation history to the model
    3. Add assistant response to history
    """
    # Append user message
    st.session_state.messages.append(
        HumanMessage(content=user_input)
    )

    #Day1 -Get response from LLM using full chat history
    # response = llm.invoke(
    #     st.session_state.messages
    # )
    #Day2 - advance invoke llm using chain
    response = chain.invoke(
        {
            "history": st.session_state.messages,
            "input": user_input,
        }
    )
    # Append assistant response
    st.session_state.messages.append(response)

#day-2: lets advance chat_round, invoke llm with chain of prompt | llm, for context of prev msg
def build_chain(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a concise, helpful assistant. Use prior chat history to stay on context."
            ),
            MessagesPlaceholder(variable_name="history"),
                (
                    "human",
                    "{input}"
                ),
        ]
    )
    return prompt | llm #LCEL chain


#load db using db_init.py



def main():
    # Configure Streamlit page
    st.set_page_config(
        page_title="DeepDev Support Chatbot",
        page_icon="🤖"
    )
    #header
    st.title("DeepDev Support Chatbot")
    # Load environment variables
    load_dotenv()
    import os
    #test key load: print("API key exists:", bool(os.getenv("OPENAI_API_KEY")))
    # Initialize session and render chat history
    init_session()
    render_history()
    # Get user input
    prompt = st.chat_input("Ask me anything.")
    if prompt:
        # Get LLM instance
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.5)
        chain = build_chain(llm)
        # Show assistant response area with spinner
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # chat_round(llm, prompt)
                chat_round(chain, prompt)
        # Refresh UI to display updated messages
        st.rerun()



if __name__ == "__main__": main()