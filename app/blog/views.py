"""Views сервиса по работе с постами (POST)."""
from typing import Any

from core.components import Request
from fastapi import APIRouter, Depends, Response
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.security import HTTPBearer
from user.schemes import (OkSchema, RefreshSchema, UserSchemaLogin,
                          UserSchemaOut, UserSchemaRegistration)

post_route = APIRouter(prefix="/post")


@post_route(
    "/new_post",
    summary="Добавить новый пост",
    description="Добавление нового поста",
    response_description="id размещенного поста",
    tags=["POST"],
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
