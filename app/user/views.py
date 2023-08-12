"""Views сервиса авторизации (AUTH)."""

from typing import Any

from base.type_hint import Sorted_direction
from core.components import Request
from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPBearer
from pydantic import EmailStr
from user.schemes import (
    BaseUserSchema,
    OkSchema,
    RefreshSchema,
    TokenSchema,
    UserPasswordSchema,
    UserSchemaLogin,
    UserSchemaOut,
    UserSchemaRegistration,
    query_page_number,
    query_page_size,
    query_sort_created,
    query_sort_email,
    query_sort_modified,
    query_sort_name,
    query_sort_user_id,
)
from user.utils import (
    description_create_user,
    description_login_user,
    description_logout_user,
    description_refresh_tokens,
    description_registration_user,
)

auth_route = APIRouter(prefix="/auth", tags=["AUTH"])


@auth_route.post(
    "/create_user",
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
    temp_user = await request.app.store.auth_manager.create_user(**user.model_dump())
    return OkSchema(
        message=f"Sent  letter  to  {temp_user.email}, for verification email addresses"
    )


@auth_route.get(
    "/registration_user",
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
    await request.app.store.auth_manager.logout(response, token.user_id, token.token, token.exp)
    return OkSchema()


@auth_route.get(
    "/refresh",
    summary="Обновить токен доступа",
    description=description_refresh_tokens,
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


@auth_route.get(
    "/reset_password",
    summary="Инициализация сброса пароля",
    response_model=OkSchema,
)
async def reset_password(request: Request, email: EmailStr) -> Any:
    """Initializing reset user password.

    Args:
        request: Request
        email: user email for initializing reset password
    Returns:
        optional: OkSchema
    """
    user = await request.app.store.auth_manager.reset_password(email)
    return OkSchema(message=f"Sent letter to {user.email}, for reset password")


@auth_route.post(
    "/update_password",
    summary="Задать новый пароль",
    description="Enter password",
    response_model=OkSchema,
)
async def update_password(request: Request, password: UserPasswordSchema) -> Any:
    await request.app.store.auth.update_password(request.state.user_id, password.password)
    return OkSchema(message="Password changed successfully")


@auth_route.get(
    "/users",
    summary="Получить список пользователей",
    description="Получить список зарегистрированных "
    "пользователей согласно заданным параметрам фильтрации",
    response_description="Список пользователей",
    response_model=list[BaseUserSchema],
)
async def get_users(
    request: Request,
    page: int = query_page_number,
    size: int = query_page_size,
    id: Sorted_direction = query_sort_user_id,
    email: Sorted_direction = query_sort_email,
    name: Sorted_direction = query_sort_name,
    created: Sorted_direction = query_sort_created,
    modified: Sorted_direction = query_sort_modified,
) -> Any:
    sorted_params = {
        name: value
        for index, (name, value) in enumerate(locals().items())
        if int(index) > 2 and value
    }
    users_data = await request.app.store.auth.get_users(page - 1, size, sorted_params)
    return [BaseUserSchema(execute=["access_token"], **user.as_dict()) for user in users_data]
