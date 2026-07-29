from langchain.tools import tool
from langchain.tools import ToolRuntime

from support_chatbot.context import SessionContext

#HIL for cancel order
@tool
def cancel_order_action(
    order_id: int,
    runtime: ToolRuntime[SessionContext]
):
    """
    Cancel an order after admin approval.
    """

    user_email = runtime.context.user_email

    return {
        "status": "cancelled",
        "order_id": order_id,
        "user": user_email
    }

#crete return action
@tool
def create_return_action(
    order_id: int,
    product_name: str,
    reason: str,
    runtime: ToolRuntime[SessionContext]
):
    """
    Create a return request after admin approval.
    """

    user_email = runtime.context.user_email

    return {
        "status": "return_created",
        "order_id": order_id,
        "user": user_email
    }

#export tools
def get_action_tools():
    return [
        cancel_order_action,
        create_return_action,
    ]
#test: uv run python -c "from support_chatbot.action_tools import get_action_tools print([t.name for t in get_action_tools()])