from datetime import datetime

from langchain.agents.middleware import (
    wrap_model_call,
    wrap_tool_call,
)

def _ts():
    """
    Return formatted timestamp.
    """
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

@wrap_model_call
def model_logging_middleware(request, handler):
    """
    Logs model request and response.
    """
    try:
        messages = request.state["messages"]
        last_message = (
            messages[-1]
            if messages
            else None
        )
        print(
            f"[{_ts()}] MODEL CALL"
        )
        print(
            f"Message count: {len(messages)}"
        )
        if last_message:
            print(
                "Last message:",
                str(last_message.content)[:100]
            )
        response = handler(request)
        response_messages = (
            response.state.get("messages", [])
            if hasattr(response, "state")
            else []
        )
        if response_messages:
            last_response = response_messages[-1]

            print(
                f"[{_ts()}] MODEL RESPONSE:",
                str(last_response.content)[:100]
            )
            if hasattr(last_response, "tool_calls"):
                print(
                    "Tool calls:",
                    last_response.tool_calls
                )
        return response

    except Exception as e:
        print(
            f"[{_ts()}] MODEL ERROR:",
            str(e)
        )
        raise


@wrap_tool_call
def tool_logging_middleware(request, handler):
    """
    Logs tool execution.
    """
    try:
        messages = request.state["messages"]
        last_message = (
            messages[-1]
            if messages
            else None
        )

        if last_message:
            print(
                f"[{_ts()}] TOOL CALL:",
                getattr(
                    last_message,
                    "tool_calls",
                    None
                )
            )

        result = handler(request)

        print(
            f"[{_ts()}] TOOL SUCCESS"
        )
        print("TOOL RESULT:", result)
        return result

    except Exception as e:
        print(
            f"[{_ts()}] TOOL ERROR:",
            str(e)
        )
        raise


def get_logging_middleware():
    return [
        model_logging_middleware,
        tool_logging_middleware,
    ]