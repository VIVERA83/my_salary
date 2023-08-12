"""Views сервиса по работе с темами для постов (TOPIC)."""
from typing import Any

from icecream import ic

from blog.topic.schemes import TopicSchemaIn, TopicSchemaOut, TopicSchemaUpdateIn
from core.components import Request
from fastapi import APIRouter

topic_route = APIRouter()


@topic_route.post(
    "/topic",
    summary="Добавить новую тему для постов",
    description="Добавление новой темы для постов.",
    response_description="Полная информация о добавленной теме",
    tags=["TOPIC"],
    response_model=TopicSchemaOut,
)
async def create_topic(request: Request, topic: TopicSchemaIn) -> Any:
    topic_data = await request.app.store.blog.create_topic(**topic.model_dump())
    return TopicSchemaOut(**topic_data.as_dict())


@topic_route.patch(
    "/topic",
    summary="Обновить данные о теме.",
    description="Обновление данных темы для постов. "
                "Возможно обновление как всех так и по отдельности полей темы: "
                "Просто указываете те поля которые требуется изменить. "
                "Обратите внимание, менять значение поля `id` не возможно.",
    response_description="Полная информация о обновленной теме",
    tags=["TOPIC"],
    response_model=TopicSchemaOut,
)
async def update_topic(request: Request, topic: TopicSchemaUpdateIn) -> Any:
    topic_data = await request.app.store.blog.update_topic(**topic.model_dump())
    assert topic_data, f"Topic with id '{topic.id}' not found."
    return TopicSchemaOut(**topic_data.as_dict())


@topic_route.delete(
    "/topic",
    summary="Обновить данные о теме.",
    description="Обновление данных темы для постов. "
                "Возможно обновление как всех так и по отдельности полей темы: "
                "Просто указываете те поля которые требуется изменить. "
                "Обратите внимание, менять значение поля `id` не возможно.",
    response_description="Полная информация о обновленной теме",
    tags=["TOPIC"],
    response_model=TopicSchemaOut,
)
async def delete_topic(request: Request, topic: TopicSchemaUpdateIn) -> Any:
    topic_data = await request.app.store.blog.update_topic(**topic.model_dump())
    assert topic_data, f"Topic with id '{topic.id}' not found."
    return TopicSchemaOut(**topic_data.as_dict())
