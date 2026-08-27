from app.chatbot.executor import execute_tool
from app.chatbot.formatter import format_tool_response
from app.chatbot.gemini_client import select_tool
from app.chatbot.logging_utils import (
    create_request_id,
    log_chat_event
)
from app.chatbot.policy import (
    READ_ONLY_MESSAGE,
    is_write_request
)


UNSUPPORTED_MESSAGE = (
    "I can help with read-only Tally financial queries such as "
    "receivables, payables, pending invoices, revenue, expenses, "
    "profit or loss, Trial Balance, and Balance Sheet."
)


async def process_chat_message(
    message: str,
    company_name: str | None = None
) -> dict:
    request_id = create_request_id()

    log_chat_event(
        request_id=request_id,
        event="request_received"
    )

    cleaned_message = message.strip()

    if not cleaned_message:
        log_chat_event(
            request_id=request_id,
            event="invalid_request",
            intent="invalid_request"
        )

        return {
            "success": False,
            "source": None,
            "intent": "invalid_request",
            "answer": "Please enter a financial question.",
            "data": None
        }

    if is_write_request(cleaned_message):
        log_chat_event(
            request_id=request_id,
            event="write_request_blocked",
            intent="write_operation"
        )

        return {
            "success": False,
            "source": None,
            "intent": "write_operation",
            "answer": READ_ONLY_MESSAGE,
            "data": None
        }

    try:
        selection = await select_tool(
            cleaned_message
        )

    except Exception:
        log_chat_event(
            request_id=request_id,
            event="model_exception",
            intent="model_error"
        )

        return {
            "success": False,
            "source": None,
            "intent": "model_error",
            "answer": (
                "I am unable to understand the request right now. "
                "Please try again shortly."
            ),
            "data": None
        }

    model_error = selection.get(
        "error"
    )

    if model_error == "rate_limit":
        log_chat_event(
            request_id=request_id,
            event="model_rate_limit",
            intent="model_rate_limit"
        )

        return {
            "success": False,
            "source": None,
            "intent": "model_rate_limit",
            "answer": (
                "The AI service is temporarily busy. "
                "Please try again in a moment."
            ),
            "data": None
        }

    if model_error == "authentication":
        log_chat_event(
            request_id=request_id,
            event="model_authentication_error",
            intent="model_authentication_error"
        )

        return {
            "success": False,
            "source": None,
            "intent": "model_authentication_error",
            "answer": (
                "The chatbot service is temporarily unavailable."
            ),
            "data": None
        }

    if model_error == "model_not_found":
        log_chat_event(
            request_id=request_id,
            event="model_configuration_error",
            intent="model_configuration_error"
        )

        return {
            "success": False,
            "source": None,
            "intent": "model_configuration_error",
            "answer": (
                "The chatbot service is temporarily unavailable."
            ),
            "data": None
        }

    if model_error in {
        "model_error",
        "model_unavailable"
    }:
        log_chat_event(
            request_id=request_id,
            event="model_error",
            intent="model_error"
        )

        return {
            "success": False,
            "source": None,
            "intent": "model_error",
            "answer": (
                "The chatbot service is temporarily unavailable. "
                "Please try again shortly."
            ),
            "data": None
        }

    tool_name = selection.get(
        "tool_name"
    )

    arguments = selection.get(
        "arguments",
        {}
    )

    if not tool_name:
        log_chat_event(
            request_id=request_id,
            event="unsupported_request",
            intent="unsupported"
        )

        return {
            "success": False,
            "source": None,
            "intent": "unsupported",
            "answer": UNSUPPORTED_MESSAGE,
            "data": None
        }

    log_chat_event(
        request_id=request_id,
        event="tool_selected",
        intent=tool_name
    )

    if company_name:
        arguments["company_name"] = company_name

    tool_result = await execute_tool(
        tool_name=tool_name,
        arguments=arguments
    )

    if not tool_result.get("success"):
        log_chat_event(
            request_id=request_id,
            event="tool_failed",
            intent=tool_name,
            source=tool_result.get("source")
        )

        return {
            "success": False,
            "source": tool_result.get("source"),
            "intent": tool_name,
            "answer": tool_result.get(
                "message",
                "Unable to retrieve the requested data from Tally."
            ),
            "data": None
        }

    answer = format_tool_response(
        tool_name=tool_name,
        tool_result=tool_result
    )

    log_chat_event(
        request_id=request_id,
        event="request_completed",
        intent=tool_name,
        source="tally"
    )

    return {
        "success": True,
        "source": "tally",
        "intent": tool_name,
        "answer": answer,
        "data": tool_result.get("data")
    }