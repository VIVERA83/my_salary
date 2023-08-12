"""Schemas сервиса Блога, подраздел Topic(TOPIC)."""
from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field, field_validator

ID: UUID = Field(
    example="1595c2fc-397a-40c9-8105-a4d2f0a33a7a",
    description="unique indicator of topic",
)
TITLE: str = Field(
    example="Docker",
    description="Topic description",
)
DESCRIPTION: str = Field(
    example="Docker documentations and examples or practice",
    description="description",
)


class BaseSchema(BaseModel):
    """Base Schema class."""

    class Config:
        """Config."""

        from_attributes = True
        exclude = True


class BaseTopicSchema(BaseModel):
    title: str = TITLE
    description: str = DESCRIPTION

    @field_validator("title", "description")
    def validate(cls, data: str) -> str:  # noqa
        if 5 <= len(data) <= 100:
            return data
        raise ValueError("String should have at least 5 characters")


class TopicSchemaIn(BaseTopicSchema):
    title: str = TITLE
    description: str = DESCRIPTION


class TopicSchemaOut(BaseTopicSchema):
    id: UUID = ID
    created: datetime
    modified: datetime


class TopicSchemaUpdateIn(BaseTopicSchema):
    title: str = Field(
        example="Docker",
        default=None,
        description="Topic description",
    )
    description: str = Field(
        example="Docker documentations and examples or practice",
        default=None,
        description="description",
    )


Sorting_direction = Literal["ASC", "DESC"]
query_page_number: int = Query(default=1, description="Number of page", alias="page[number]", gt=0)
query_page_size: int = Query(
    default=10, description="Size of the page", alias="page[size]", gt=0, le=100
)
query_sort_topic_id: Sorting_direction = Query(default=None, alias="id")
query_sort_title: Sorting_direction = Query(default=None)
query_sort_description: Sorting_direction = Query(default=None)
query_sort_created: Sorting_direction = Query(default=None)
query_sort_modified: Sorting_direction = Query(default=None)
