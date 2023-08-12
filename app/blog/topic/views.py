"""Views сервиса по работе с темами для постов (TOPIC)."""
from typing import Any

from blog.topic.schemes import TopicSchemaIn, TopicSchemaOut, TopicSchemaUpdateIn
from core.components import Request
from fastapi import APIRouter

topic_route = APIRouter(prefix="/topic")


@topic_route.post(
    "/new_topic",
    summary="Добавить новую тему для постов",
    description="Добавление новой темы для постов.",
    response_description="Полная информация о добавленной теме",
    tags=["TOPIC"],
    response_model=TopicSchemaOut,
)
async def create_topic(request: Request, topic: TopicSchemaIn) -> Any:
    topic_data = await request.app.store.blog.create_topic(**topic.model_dump())
    return TopicSchemaOut(**topic_data.as_dict())


@topic_route.post(
    "/update_topic",
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
    return TopicSchemaOut(**topic_data.as_dict())


# https://opyat-remont.ru/test?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWJqZWN0Ijp7InVzZXJfaWQiOiJkOWFmMTViMDhmZDY0N2ZmOTA2ZDM4MzM3NGQ3YTI5ZiIsImVtYWlsIjoidml2ZXJhODNAYmsucnUifSwidHlwZSI6InZlcmlmaWNhdGlvbiIsImV4cCI6MTY5MTc1NDUyMywiaWF0IjoxNjkxNTgyNTIzLCJqdGkiOiI4OTgwNzZhMWRhZmU0N2Q5YWRlNzA5NDIwZjQ4YjVkMiJ9.7AY3gNchzMtmsGnZcZWE2oyJMkp9lmhHC-zvdGTbass
