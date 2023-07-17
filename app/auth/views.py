"""Views сервиса авторизации (AUTH)."""

from typing import Any

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from core.components import Request
from auth.schemes import (
    OkSchema,
    RefreshSchema,
    TokenSchema,
    UserSchemaLogin,
    UserSchemaOut,
    UserSchemaRegistration,
)

auth_route = APIRouter(prefix='/api/v1')


@auth_route.post(
    '/create_user',
    summary='Регистрация нового пользователя',
    description='Регистрация нового пользователя в сервисе.',
    response_description='Анкетные данные пользователя, кроме секретных данных.',
    tags=['AUTH'],
    response_model=UserSchemaOut,
)
async def create_user(
        request: 'Request',
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
    try:
        new_user = await request.app.store.auth.create_user(**user.model_dump())
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Email {email} is not existing'.format(email=user.email),
        )
    access_token, refresh_token = await request.app.store.auth.create_tokens(
        new_user.id.hex,
    )
    await request.app.store.auth.update_response(refresh_token, response)
    return UserSchemaOut(
        id=new_user.id,
        user_name=new_user.name,
        email=new_user.email,
        access_token=access_token,
    )


@auth_route.post(
    '/login',
    summary='Авторизация',
    description='Авторизация пользователя в сервисе.',
    response_description='Анкетные данные пользователя, кроме секретных данных.',
    tags=['AUTH'],
    response_model=UserSchemaOut,
)
async def login(request: 'Request', response: Response, user: UserSchemaLogin) -> Any:
    """Login.

    Args:
        request: "Request"
        response: Response
        user: UserSchemaLogin

    Returns:
        Response or HTTPException 401 UNAUTHORIZED
    """
    user_db = await request.app.store.auth.get_user_by_email(user.email)
    if user_db:
        if user_db.password == user.password:
            access_token, refresh_token = await request.app.store.auth.create_tokens(
                user_db.id.hex,
            )
            await request.app.store.auth.update_response(refresh_token, response)
            return UserSchemaOut(
                id=user_db.id,
                user_name=user_db.name,
                email=user_db.email,
                access_token=access_token,
            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='The user or password is incorrect',
    )


@auth_route.get(
    '/logout',
    summary='Выход',
    description='Выход из системы, что бы снова пользоваться '
                'сервисом необходимо будет снова авторизоваться.',
    tags=['AUTH'],
    response_model=OkSchema,
)
async def logout(request: 'Request', response: Response) -> Any:
    """Logout user.

    Args:
        request: "Request"
        response: hashed password

    Returns:
        object: OkSchema
    """
    await request.app.store.auth.logout(request, response)
    return OkSchema()


@auth_route.get(
    '/refresh',
    summary='Обновить токен доступа',
    description='Обновление токенов доступа.',
    tags=['AUTH'],
    response_model=RefreshSchema,
)
async def refresh(request: 'Request', response: Response) -> Any:
    """Update tokens.

    Args:
        request: "Request"
        response: Response

    Returns:
        Response or HTTPException 401 UNAUTHORIZED
    """
    refresh_token = request.app.store.auth.get_refresh_token(request)
    user_id = TokenSchema(refresh_token).payload.user_id.hex
    is_correct = await request.app.store.auth.compare_refresh_token(
        user_id=user_id,
        refresh_token=refresh_token,
    )
    if is_correct:
        (
            access_token,
            refresh_token,
        ) = await request.app.store.auth.refresh(
            refresh_token,
        )
        await request.app.store.auth.update_response(
            refresh_token,
            response,
        )
        return RefreshSchema(access_token=access_token)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Refresh token not valid',
    )