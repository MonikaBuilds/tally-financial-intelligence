import os
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class UserContext:
    user_id: str
    allowed_companies: tuple[str, ...]


def _auth_enabled() -> bool:
    return os.getenv("CHAT_AUTH_ENABLED", "false").lower() == "true"


def _decode_token(token: str) -> dict:
    secret = os.getenv("CHAT_JWT_SECRET")
    algorithm = os.getenv("CHAT_JWT_ALGORITHM", "HS256")

    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret is not configured.",
        )

    try:
        return jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UserContext:
    # Development compatibility:
    # auth can stay disabled until frontend/login integration is ready.
    if not _auth_enabled():
        return UserContext(
            user_id="development-user",
            allowed_companies=("*",),
        )

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    payload = _decode_token(credentials.credentials)

    user_id = payload.get("sub")
    companies = payload.get("companies", [])

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain a valid user identity.",
        )

    if not isinstance(companies, list):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid company permissions in token.",
        )

    return UserContext(
        user_id=str(user_id),
        allowed_companies=tuple(str(company) for company in companies),
    )


def authorize_company(
    user: UserContext,
    requested_company: str | None,
) -> str | None:
    allowed = user.allowed_companies

    # Development/admin-style wildcard.
    if "*" in allowed:
        return requested_company

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to any company.",
        )

    # If the user only has one company, select it automatically.
    if requested_company is None:
        if len(allowed) == 1:
            return allowed[0]

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select a company.",
        )

    requested_key = requested_company.casefold()

    for company in allowed:
        if company.casefold() == requested_key:
            return company

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to access this company.",
    )