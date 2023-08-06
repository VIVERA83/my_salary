"""Views сервиса авторизации (AUTH)."""

from typing import Any

from core.components import Request
from fastapi import APIRouter, Depends, Response
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.security import HTTPBearer

from user.schemes import (
    OkSchema,
    RefreshSchema,
    UserSchemaLogin,
    UserSchemaOut,
    UserSchemaRegistration,
)

auth_route = APIRouter(prefix="/api/v1")


@auth_route.post(
    "/create_user",
    summary="Регистрация нового пользователя",
    description="Регистрация нового пользователя в сервисе.",
    response_description="Анкетные данные пользователя, кроме секретных данных.",
    tags=["AUTH"],
    response_model=UserSchemaOut,
)
async def create_user(
    request: "Request",
    response: Response,
    user: UserSchemaRegistration,
) -> Any:
    """Create new user.

    Args:
        request: "Request"
        response: Response
        user: UserSchemaRegistration

    Returns:
        object: UserSchemaOut
    """
    user_data = await request.app.store.auth_manager.create_user(response, **user.model_dump())
    return UserSchemaOut(**user_data)


@auth_route.post(
    "/login",
    summary="Авторизация",
    description="Авторизация пользователя в сервисе.",
    response_description="Анкетные данные пользователя, кроме секретных данных.",
    tags=["AUTH"],
    response_model=UserSchemaOut,
)
async def login(request: "Request", response: Response, user: UserSchemaLogin) -> Any:
    """Login.

    Args:
        request: "Request"
        response: Response
        user: UserSchemaLogin

    Returns:
        Response or HTTPException 401 UNAUTHORIZED
    """
    return await request.app.store.auth_manager.login(response, **user.model_dump())


@auth_route.get(
    "/logout",
    summary="Выход",
    description="Выход из системы, что бы снова пользоваться "
    "сервисом необходимо будет снова авторизоваться.",
    tags=["AUTH"],
    response_model=OkSchema,
)
async def logout(request: "Request", response: Response) -> Any:
    """Logout user.

    Args:
        request: "Request"
        response: hashed password

    Returns:
        object: OkSchema
    """
    token = request.state.access_token
    await request.app.store.auth_manager.logout(
        response, request.state.user_id, token.token, token.payload.exp
    )
    return OkSchema()


@auth_route.get(
    "/refresh",
    summary="Обновить токен доступа",
    description="Обновление токенов доступа.",
    tags=["AUTH"],
    response_model=RefreshSchema,
)
async def refresh(request: "Request", response: Response) -> Any:
    """Update tokens.

    Args:
        request: "Request"
        response: Response

    Returns:
        Response or HTTPException 401 UNAUTHORIZED
    """
    return await request.app.store.auth_manager.refresh(request, response)


@auth_route.get(
    "/token",
    summary="Проверить токен доступа",
    tags=["AUTH"],
    response_model=OkSchema,
)
def get_token(
    authorization=Depends(HTTPBearer(auto_error=True)),
) -> Any:  # noqa
    """Returns Ok.

    Args:
        authorization: str. The authorization

    Returns:
        optional: ok if authorization is valid
    """
    return OkSchema()


@auth_route.get(
    "/test",
    summary="asdasdasd",
)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()
