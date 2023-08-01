"""Schemas сервиса Авторизации (AUTH)."""
import json
from hashlib import sha256
from uuid import UUID

from jose import jws
from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class BaseSchema(BaseModel):
    """Base Schema class."""

    class Config:
        """Config."""

        from_attributes = True
        exclude = True


class BaseTopicSchema(BaseModel):
    title: str
    description: str


class TopicSchemaIn(BaseTopicSchema):
    ...


class TopicSchemaOut(BaseTopicSchema):
    id: UUID
