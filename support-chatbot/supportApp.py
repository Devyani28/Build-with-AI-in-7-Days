#imports
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage

#add llm
#model = ChatOpenAI(model="gpt-4.1-mini", temperature=0.5)

#at every step chk compilationErr of py file: py_compile supportApp.py
#run app: streamlit run suportApp.py
#streamlit style cnfig in .stteamlit/config.toml

#app start, welcom
def init_session():
    # Initialize messages in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Add initial assistant greeting, if no messages exist
    if not st.session_state.messages:
        st.session_state.messages = [
            AIMessage(content="Hi! Ask me anything.")
        ]
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
def chat_round(llm, user_input):
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
    # Get response from LLM using full chat history
    response = llm.invoke(
        st.session_state.messages
    )
    # Append assistant response
    st.session_state.messages.append(response)

def main():
    #header
    st.title("DeepDev Support Chatbot")
    
    # Configure Streamlit page
    st.set_page_config(
        page_title="DeepDev Support Chatbot",
        page_icon="🤖"
    )


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

        # Show assistant response area with spinner
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat_round(llm, prompt)

        # Refresh UI to display updated messages
        st.rerun()


if __name__ == "__main__": main()