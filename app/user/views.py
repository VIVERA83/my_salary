"""Views сервиса авторизации (AUTH)."""

from typing import Any

from core.components import Request
from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPBearer
from user.schemes import (OkSchema, RefreshSchema, TokenSchema,
                          UserSchemaLogin, UserSchemaOut,
                          UserSchemaRegistration)
from user.utils import (description_create_user, description_login_user,
                        description_logout_user, description_refresh_tokens,
                        description_registration_user)

auth_route = APIRouter(prefix="/api/v1")


@auth_route.post(
    "/create_user",
    tags=["AUTH"],
    summary="Создание учетной записи пользователя",
    description=description_create_user,
    response_description="Анкетные данные пользователя, кроме секретных данных.",
    response_model=OkSchema,
)
async def create_user(
        request: "Request",
        user: UserSchemaRegistration,
) -> Any:
    """A temporary user record is created in the temporary storage.

    And an email is sent to the user's email address to complete the registration process.
    The record is stored for a limited time.
    This record will be used if the user confirms the email to complete the user registration.

    Args:
        request: "Request"
        user: UserSchemaRegistration

    Returns:
        object: UserSchemaOut
    """
    await request.app.store.auth_manager.create_user(**user.model_dump())
    return OkSchema(message="Temporary user record and sent verification email successfully")


@auth_route.get(
    "/registration_user",
    tags=["AUTH"],
    summary="Регистрация пользователя",
    description=description_registration_user,
    response_description="Анкетные данные пользователя, кроме секретных данных.",
    response_model=UserSchemaOut,
)
async def user_registration(request: "Request", response: Response) -> Any:
    """User registration.

    From the current moment, the user is registered and receives an account
    in the database, the email address is confirmed.

    Args:
        request: Request
        response: Response
    """
    return await request.app.store.auth_manager.user_registration(request.state.token, response)


@auth_route.post(
    "/login",
    summary="Авторизация",
    description=description_login_user,
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
    description=description_logout_user,
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
    token = request.state.token
    await request.app.store.auth_manager.logout(
        response, token.user_id, token.token, token.exp
    )
    return OkSchema()


@auth_route.get(
    "/refresh",
    summary="Обновить токен доступа",
    description=description_refresh_tokens,
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
    response_model=TokenSchema,
)
def get_token(request: Request, authorization=Depends(HTTPBearer(auto_error=True))) -> Any:  # noqa
    """Returns Ok.

    Args:
        authorization: str. The authorization
        request: Request
    Returns:
        optional: token object
    """
    return TokenSchema(**request.state.token.as_dict)
