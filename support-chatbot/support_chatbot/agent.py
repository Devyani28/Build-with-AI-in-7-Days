#agent that chooses tools

from langchain.agents import create_agent
from support_chatbot.rag_tool import search_policies
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

#checkpointing- save across context
import os
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
#toolcall middleware
from support_chatbot.middleware import get_logging_middleware

_agent = None
_checkpointer = None

#compiled staegraph
def create_support_agent():
    """
    Create the customer support agent.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )
    system_prompt = """
    You are an AI customer support assistant for an e-commerce company.

    Use the search_policies tool ONLY when the user asks about:
    - return policy
    - shipping policy
    - refund policy
    - cancellation policy
    - warranty
    - FAQs covered in the company policy documents
    Answer using the information returned by the tool.

    Do not use the tool for:
    - greetings
    - casual conversation
    - simple questions that do not require company policies

    If the tool does not provide enough information, say you could not
    find the relevant company policy instead of making one up.
    """
    return create_agent(
        model=llm,
        tools=[search_policies],
        system_prompt=system_prompt,
        checkpointer=get_checkpointer(), #Day6
        middleware=get_logging_middleware(), #Day7
    )

def get_agent():
    """
    Return a cached support agent.
    """
    global _agent
    if _agent is None:
        _agent = create_support_agent()
    return _agent

def get_checkpointer():
    global _checkpointer
    if _checkpointer is None:
        db_path = os.getenv(
            "CHECKPOINTS_DB_PATH",
            "checkpoints.sqlite"
        )
        conn = sqlite3.connect(
            db_path,
            check_same_thread=False
        )
        _checkpointer = SqliteSaver(
            conn
        )
        _checkpointer.setup()
    return _checkpointer

def get_thread_config(user_email, conversation_id):
    return {
        "configurable": {
            "thread_id": f"{user_email}:{conversation_id}"
        },
        "recursion_limit": 20,
    }
