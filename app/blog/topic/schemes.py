"""Schemas сервиса Блога, подраздел Topic(TOPIC)."""
from uuid import UUID

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


class TopicSchemaUpdateIn(BaseModel):
    id: UUID = ID
    title: str | None
    # = Field(example="Docker",
    #                 default=None,
    #                 description="Topic description",
    #                 )
    description: str | None  # = Field(example="Docker documentations and examples or practice",
    #                      default=None,
    #                      description="description",
    #                      )
