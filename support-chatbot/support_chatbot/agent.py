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
#sql tool
from support_chatbot.sql_tools import get_sql_tools

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

    You have two capabilities:

    1. Policy search:
    Use search_policies tool ONLY for:
    - return policy
    - shipping policy
    - refund policy
    - cancellation policy
    - warranty
    - FAQs

    2. Customer data queries:
    Use SQL tools for user-specific questions:
    - my orders
    - order status
    - payment status
    - returns
    - purchase history
    - total spending

    Security rules:
    - Always use SQL tools for customer data.
    - Always filter results by the logged-in user's email.
    - Never answer customer-specific questions from memory.
    - Never expose another user's data.

    Example query pattern:

    Orders:
    JOIN users ON orders.user_id = users.id
    WHERE users.email = customer_email

    Tickets:
    JOIN users ON tickets.user_id = users.id
    WHERE users.email = customer_email

    If information is not found, say so clearly.

    Do not use tools for:
    - greetings
    - casual conversation
    - general questions.
    """
    return create_agent(
        model=llm,
        tools=[
            search_policies,
            *get_sql_tools()
        ],
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
            "thread_id": f"{user_email}:{conversation_id}",
            "user_email": "sivaprasad.valluru@gmail.com",   # user_email
        },
        "recursion_limit": 20,
    }
