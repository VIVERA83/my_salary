"""Views сервиса по работе с темами для постов (TOPIC)."""
from typing import Any
from uuid import UUID

from base.type_hint import Sorted_direction
from blog.topic.schemes import (
    TopicSchemaIn,
    TopicSchemaOut,
    TopicSchemaUpdateIn,
    query_page_number,
    query_page_size,
    query_sort_created,
    query_sort_description,
    query_sort_modified,
    query_sort_title,
    query_sort_topic_id,
)
from core.components import Request
from fastapi import APIRouter

topic_route = APIRouter(prefix="/topic", tags=["TOPIC"])


@topic_route.post(
    "/create",
    summary="Добавить новую тему для постов",
    description="Добавление новой темы для постов.",
    response_description="Полная информация о добавленной теме",
    response_model=TopicSchemaOut,
)
async def create_topic(request: Request, topic: TopicSchemaIn) -> Any:
    topic_data = await request.app.store.blog.create_topic(**topic.model_dump())
    return TopicSchemaOut(**topic_data.as_dict())


@topic_route.patch(
    "/update/{id_topic}",
    summary="Обновить данные о теме.",
    description="Обновление данных темы для постов. "
    "Возможно обновление как всех так и по отдельности полей темы: "
    "Просто указываете те поля которые требуется изменить. "
    "Обратите внимание, менять значение поля `id` не возможно.",
    response_description="Полная информация о обновленной теме",
    response_model=TopicSchemaOut,
)
async def update_topic(request: Request, id_topic: UUID, topic: TopicSchemaUpdateIn) -> Any:
    topic_data = await request.app.store.blog.update_topic(id_topic.hex, **topic.model_dump())
    assert topic_data, f"Topic with id '{id_topic}' not found."
    return TopicSchemaOut(**topic_data.as_dict())


@topic_route.delete(
    "/delete/{id_topic}",
    summary="Удалить тему",
    description="Удаление темы, по `id`.",
    response_description="Полная информация о удаленной теме.",
    response_model=TopicSchemaOut,
)
async def delete_topic(request: Request, id_topic: UUID) -> Any:
    topic_data = await request.app.store.blog.delete_topic(id_topic.hex)
    assert topic_data, f"Topic with id '{id_topic}' not found."
    return TopicSchemaOut(**topic_data.as_dict())


@topic_route.get(
    "/get/{id_topic}",
    summary="Получить",
    description="Получить тему, по `id`.",
    response_description="Полная информация о теме.",
    response_model=TopicSchemaOut,
)
async def get_topic(request: Request, id_topic: UUID) -> Any:
    topic_data = await request.app.store.blog.get_topic_by_id(id_topic.hex)
    assert topic_data, f"Topic with id '{id_topic}' not found."
    return TopicSchemaOut(**topic_data.as_dict())


@topic_route.get(
    "/get",
    summary="Получить темы ",
    description="Получить темы согласно условию пагинации .",
    response_description="Список тем",
    response_model=list[TopicSchemaOut],
)
async def get_topic(
    request: Request,
    page: int = query_page_number,
    size: int = query_page_size,
    id: Sorted_direction = query_sort_topic_id,
    title: Sorted_direction = query_sort_title,
    description: Sorted_direction = query_sort_description,
    created: Sorted_direction = query_sort_created,
    modified: Sorted_direction = query_sort_modified,
) -> Any:
    sorted_params = {
        name: value
        for index, (name, value) in enumerate(locals().items())
        if int(index) > 2 and value
    }
    topic_data = await request.app.store.blog.get_topics(page - 1, size, sorted_params)
    return [TopicSchemaOut(**topic.as_dict()) for topic in topic_data]
