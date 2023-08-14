"""Schemas сервиса Блога, подраздел Topic(TOPIC)."""
from datetime import datetime
from uuid import UUID

from base.type_hint import Sorted_direction
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


query_page_number: int = Query(
    default=1,
    description="Number of page",
    alias="page[number]",
    gt=0,
)
query_page_size: int = Query(
    default=10,
    description="Size of the page",
    alias="page[size]",
    gt=0,
    le=100,
)
query_sort_topic_id: Sorted_direction = Query(
    default=None,
    description="Sort unique identification of topic",
)
query_sort_title: Sorted_direction = Query(
    default=None,
    description="Sort title",
)
query_sort_description: Sorted_direction = Query(
    default=None,
    description="Sort description",
)
query_sort_created: Sorted_direction = Query(
    default=None,
    description="Sort created date",
)
query_sort_modified: Sorted_direction = Query(
    default=None,
    description="Sort modified date",
)
