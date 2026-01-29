"""Auth API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps.database import get_transaction
from api.errors.exceptions import AppError
from api.errors.schema import error_responses
from api.schemas.auth import LoginRequest, LoginResponse
from auth.exceptions import AuthError
from auth.service import AuthService, auth_service

from .cookie import clear_refresh_cookie, read_refresh_cookie, set_refresh_cookie

router = APIRouter()


def get_auth_service() -> AuthService:
    """Provide auth service dependency."""
    return auth_service


AuthSession = Annotated[AsyncSession, Depends(get_transaction)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        **error_responses(400, 401, 403),
        422: {"description": "Validation Error"},
    },
)
async def login(
    payload: LoginRequest,
    response: Response,
    session: AuthSession,
    service: AuthServiceDep,
) -> LoginResponse:
    """Authenticate a user and return tokens."""
    try:
        result = await service.login(session, login=payload.login, password=payload.password)
    except AuthError as exc:
        raise _app_error(exc) from exc
    set_refresh_cookie(response, result.refresh_token)
    return LoginResponse.from_result(result)


@router.post(
    "/refresh",
    response_model=LoginResponse,
    responses={
        **error_responses(400, 401, 403),
        422: {"description": "Validation Error"},
    },
)
async def refresh(
    request: Request,
    response: Response,
    session: AuthSession,
    service: AuthServiceDep,
) -> LoginResponse:
    """Refresh access token using refresh cookie."""
    token = read_refresh_cookie(request)
    try:
        result = await service.refresh(session, refresh_token=token)
    except AuthError as exc:
        clear_refresh_cookie(response)
        raise _app_error(exc) from exc
    set_refresh_cookie(response, result.refresh_token)
    return LoginResponse.from_result(result)


def _app_error(exc: AuthError) -> AppError:
    """Map domain auth errors to API errors."""
    return AppError(exc.code, exc.message, status=exc.status)


__all__ = ["router"]
