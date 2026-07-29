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
#Human In Loop
from support_chatbot.action_tools import get_action_tools
from support_chatbot.context import SessionContext
from langchain.agents.middleware import HumanInTheLoopMiddleware


_agent = None
_checkpointer = None
_checkpoint_conn = None

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
    You are an e-commerce customer support assistant.

You have three capabilities.

1. Policy questions:
Use search_policies ONLY for:
- shipping policy
- refund policy
- return policy
- cancellation policy
- warranty
- FAQ

2. Customer data:
Use SQL tools for:
- my orders
- order status
- payments
- spending history

Always filter SQL using the logged-in user's email.
Never expose another customer's data.

3. Order actions:

For cancellation:

Step 1:
Use SQL to verify:
- order belongs to logged-in user
- order status

Step 2:
If cancellation is allowed:
request admin approval.

Step 3:
After approval:
call cancel_order_action.

For returns:

Step 1:
Use SQL to verify:
- ownership
- order status

Step 2:
Request admin approval.

Step 3:
After approval:
call create_return_action.


Rules:
- Never directly cancel or return an order.
- Never bypass approval.
- Use only one action tool per turn.
- Maximum SQL attempts: 3.
- Never guess customer information.
    """
    return create_agent(
        model=llm,
        tools=[
            search_policies,
            *get_sql_tools(),
            *get_action_tools(),
        ],
        system_prompt=system_prompt,
        checkpointer=get_checkpointer(), #Day6
        middleware=[
        *get_logging_middleware(),

        HumanInTheLoopMiddleware(
            interrupt_on={
                "cancel_order_action": {
                    "allowed_decisions": [
                        "approve",
                        "reject",
                    ],
                },
                "create_return_action": {
                    "allowed_decisions": [
                        "approve",
                        "reject",
                    ],
                },
            }
        ),
    ],

    context_schema=SessionContext,
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
    global _checkpointer, _checkpoint_conn

    if _checkpointer is None:

        db_path = os.getenv(
            "CHECKPOINTS_DB_PATH",
            "checkpoints.sqlite"
        )

        _checkpoint_conn = sqlite3.connect(
            db_path,
            check_same_thread=False,
            timeout=30,
        )

        _checkpointer = SqliteSaver(
            _checkpoint_conn
        )

        _checkpointer.setup()

    return _checkpointer

def get_thread_config(user_email, conversation_id):
    return {
        "configurable": {
            "thread_id": f"{user_email}:{conversation_id}",
            # "user_email": "sivaprasad.valluru@gmail.com",   # user_email for sqltool
        },
        "recursion_limit": 20,
    }
