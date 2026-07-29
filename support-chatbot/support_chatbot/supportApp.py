#imports
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
#effective prompt handlimng
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
#threadId: unique context
from uuid import uuid4
#custom
from auth import authenticate_user
#sqlite save/load
from conversation_store import (
    save_conversation,
    load_conversations,
) 
from support_chatbot.rag_tool import initialize_vector_store
#langgraph - select tools
from support_chatbot.agent import (
    get_agent,
    get_thread_config,
)



"""
Author: Devyani28
Date: 2026-07-27
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
    # RAG knowledge base status
    st.session_state.setdefault(
        "vector_store_ready",
        False
    ) 


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
# def chat_round(chain, user_input):
#Day 5: agent for select tool
def chat_round(user_input):
    # """
    # Handles one chat turn:
    # 1. Add user message to history
    # 2. Send full conversation history to the model
    # 3. Add assistant response to history
    # """
    #Day 5: langgraph agent decides tools
    """
    Handles one agent chat turn:
    1. Add user message to session history
    2. Convert history for LangGraph agent
    3. Invoke agent
    4. Save assistant response
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
    # response = chain.invoke(
    #     {
    #         "history": st.session_state.messages,
    #         "input": user_input,
    #     }
    # )
    # # Append assistant response
    # st.session_state.messages.append(response)
    #Day 5: LangChain msg to agent for select tools
    # Convert LangChain messages to agent format
    # messages = []
    # for msg in st.session_state.messages:
    #     if isinstance(msg, HumanMessage):
    #         role = "user"
    #     else:
    #         role = "assistant"
    #     messages.append(
    #         {
    #             "role": role,
    #             "content": msg.content,
    #         }
    #     )
    #Day 6 : checkpointing
    config = get_thread_config(
        st.session_state.user_email,
        st.session_state.conversation_id,
    )
    # Invoke LangGraph agent
    result = get_agent().invoke(
        {
            "messages": [
                {
                    "role": "user",
                    # "content": user_input,
                    "content": f"""
                        Logged in user email: {st.session_state.user_email}
                        Question:
                        {user_input}
                        When using SQL, filter using the logged in user email above.
                        """
                }
            ]
        }, config=config, #checkpointing
    )
    # Extract last agent message
    response_content = ""
    if result.get("messages"):
        last_message = result["messages"][-1]
        response_content = last_message.content
    if not response_content:
        response_content = "Sorry, I could not generate a response."
    # Save assistant message for UI
    st.session_state.messages.append(
        AIMessage(content=response_content)
    )
    
    #Day3: chat/msg with conversationId
    if st.session_state.conversation_id:
        st.session_state.conversations[
            st.session_state.conversation_id
        ] = st.session_state.messages.copy()
    if (st.session_state.user_email and st.session_state.conversation_id):
        save_conversation(
            st.session_state.conversation_id,
            st.session_state.user_email,
            st.session_state.messages,
        )



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

#Day2: multiple conversations based on id
def start_new_conversation():
    """
    Start a new chat thread.
    """
    conversation_id = str(uuid4())
    messages = [
        AIMessage(content="Hi! Ask me anything.")
    ]
    st.session_state.conversation_id = conversation_id
    st.session_state.messages = messages
    st.session_state.conversations[conversation_id] = messages.copy()
    #persist in db
    if st.session_state.user_email:
        save_conversation(
            conversation_id,
            st.session_state.user_email,
            messages,
        )


def load_conversation(conversation_id):
    """
    Load an existing conversation.
    """
    if conversation_id in st.session_state.conversations:
        st.session_state.conversation_id = conversation_id
        st.session_state.messages = (
            st.session_state.conversations[conversation_id].copy()
        )

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
    # ---------------- Initialize RAG ----------------
    if not st.session_state.vector_store_ready:
        try:
            with st.spinner(
                "Initializing knowledge base..."
            ):
                initialize_vector_store()
            st.session_state.vector_store_ready = True
        except Exception as e:
            st.error(
                f"Failed to initialize knowledge base: {e}"
            )
            st.stop()

    # ---------------- Login Form----------------
    if st.session_state.user_email is None:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox(
                "Role",
                ["customer", "admin"]
            )
            login = st.form_submit_button("Login")

        if login:
            user = authenticate_user(
                email=email,
                password=password,
                role=role
            )
            if user:
                st.session_state.user_email = user["email"]
                st.session_state.user_role = user["role"]
                # start_new_conversation() #new context at every login
                #Day4: get from db
                st.session_state.conversations = load_conversations(
                    user["email"]
                    # st.session_state.user_email
                )
                if st.session_state.conversations:
                    first_key = next(iter(st.session_state.conversations))
                    load_conversation(first_key)
                else:
                    start_new_conversation()
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email, password or role.")
        return
    
     # ---------------- User Info ----------------
    st.info(
        f"""
        **Logged in as:** {st.session_state.user_email}

        **Role:** {st.session_state.user_role}

        **Conversation ID:** {st.session_state.conversation_id or "—"}
        """
    )
     
     # ---------------- Sidebar ----------------
    st.sidebar.header("Conversations")
    conversation_options = (
        list(st.session_state.conversations.keys())
        if st.session_state.conversations
        else ["(no threads yet)"]
    )
    #select sidebar selected id
    selected = st.sidebar.selectbox(
        "Select Conversation",
        conversation_options,
        index=conversation_options.index(st.session_state.conversation_id)
        if st.session_state.conversation_id in conversation_options
        else 0,
    )
    if ( #render id based history
        selected != "(no threads yet)"
        and selected != st.session_state.conversation_id):
            load_conversation(selected)
            st.rerun()
    if st.sidebar.button("Start New Conversation"):
        start_new_conversation()
        st.rerun()

    render_history() #without threadId/authenticateUser

    # Get user input
    prompt = st.chat_input("Ask me anything.")
    if prompt:
        # if st.session_state.conversation_id is None:
        #     start_new_conversation() #if prompt not have id, than
        # chat load based on user
        # Get LLM instance
        # llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.5)
        # chain = build_chain(llm)
        # Show assistant response area with spinner
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # chat_round(llm, prompt)
                # chat_round(chain, prompt)
                #Day5: use agent/graph select tools, not llm
                chat_round(prompt)
        # Refresh UI to display updated messages
        st.rerun()



if __name__ == "__main__": main()