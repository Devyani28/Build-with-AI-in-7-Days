import sqlite3
from datetime import datetime

from langgraph.types import Command


def get_db():
    return sqlite3.connect("ecommerce.db")

#after interrupted by HIL
def handle_interrupt(result, thread_id, user_email):

    interrupts = result.get("__interrupt__")

    if not interrupts:
        return None

    interrupt = interrupts[0]

    print("RAW INTERRUPT:", interrupt)

    data = interrupt.value

    print("INTERRUPT VALUE:", data)

    # LangGraph HIL structure can vary
    action_type = None
    order_id = None
    product_name = None
    reason = None

    if isinstance(data, dict):

        # New LangGraph HIL format
        action_type = data.get("action_name") or data.get("tool_name")

        args = data.get("args", {})

        order_id = args.get("order_id")
        product_name = args.get("product_name")
        reason = args.get("reason")

    # fallback: inspect string
    if not action_type:
        text = str(data)

        if "cancel_order_action" in text:
            action_type = "cancel_order_action"

        elif "create_return_action" in text:
            action_type = "create_return_action"


    if not action_type:
        raise Exception(
            f"Could not identify action from interrupt: {data}"
        )


    with get_db() as conn:

        conn.execute(
            """
            INSERT INTO pending_actions
            (
            thread_id,
            user_email,
            action_type,
            order_id,
            product_name,
            reason,
            status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                thread_id,
                user_email,
                action_type,
                order_id,
                product_name,
                reason,
                "PENDING",
            )
        )

        conn.commit()


    return """
## Approval Required

Your request needs admin approval.

Status:
⏳ Pending review
"""


def resume_with_decision(
    agent,
    thread_id,
    decision
):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }


    result = agent.invoke(
        Command(
            resume={
                "decision": decision
            }
        ),
        config=config
    )


    return result