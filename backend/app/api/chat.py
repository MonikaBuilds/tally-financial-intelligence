from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.chatbot.schemas import (
    ChatRequest,
    ChatResponse,
)
from app.chatbot.service import process_chat_message
from app.security.auth import (
    UserContext,
    authorize_company,
    get_current_user,
)


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    current_user: UserContext = Depends(get_current_user),
):
    try:
        company_name = authorize_company(
            user=current_user,
            requested_company=request.company_name,
        )

        result = await process_chat_message(
            message=request.message,
            company_name=company_name,
        )

        return ChatResponse(
            success=result.get(
                "success",
                False,
            ),
            answer=result.get(
                "answer",
                "Unable to process the request.",
            ),
            intent=result.get("intent"),
            source=result.get("source"),
            data=result.get("data"),
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to process the chatbot request."
            ),
        )