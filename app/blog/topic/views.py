"""Views сервиса по работе с темами для постов (TOPIC)."""
from typing import Any

from icecream import ic

from blog.topic.schemes import TopicSchemaOut, TopicSchemaIn
from core.components import Request
from fastapi import APIRouter

topic_route = APIRouter(prefix="/topic")


@topic_route.post(
    "/new_topic",
    summary="Добавить новый для постов",
    description="Добавление нового раздела для постов.",
    response_description="id размещенного раздела",
    tags=["TOPIC"],
    response_model=TopicSchemaOut,
)
async def create_topic(request: Request,
                       topic: TopicSchemaIn ) -> Any:
    topic_data = await request.app.store.blog.create_topic(**topic.model_dump())
    ic(topic_data.as_dict())
    return TopicSchemaOut(**topic_data.as_dict())
