from fastapi import APIRouter, HTTPException

from app.chatbot.schemas import (
    ChatRequest,
    ChatResponse
)
from app.chatbot.service import process_chat_message


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):
    try:
        result = await process_chat_message(
            message=request.message,
            company_name=request.company_name
        )

        return ChatResponse(
            success=result.get(
                "success",
                False
            ),
            answer=result.get(
                "answer",
                "Unable to process the request."
            ),
            intent=result.get(
                "intent"
            ),
            source=result.get(
                "source"
            ),
            data=result.get(
                "data"
            )
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to process the chatbot request."
            )
        )