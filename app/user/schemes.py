"""Schemas сервиса Авторизации (AUTH)."""
from datetime import datetime
from hashlib import sha256
from uuid import UUID

from base.type_hint import Sorted_direction
from fastapi import Query
from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator
from pydantic_core.core_schema import FieldValidationInfo

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
query_sort_user_id: Sorted_direction = Query(
    default=None,
    description="Sort unique identification of user",
)
query_sort_email: Sorted_direction = Query(
    default=None,
    description="Sort email address",
)
query_sort_name: Sorted_direction = Query(
    default=None,
    description="Sort user name",
)

query_sort_created: Sorted_direction = Query(
    default=None,
    description="Sort created date",
)
query_sort_modified: Sorted_direction = Query(
    default=None,
    description="Sort modified date",
)

EMAIL = Field(title="email адрес пользователя, уникальный элемент")


class BaseSchema(BaseModel):
    """Base Schema class."""

    class Config:
        """Config."""

        from_attributes = True
        exclude = True


class BaseUserSchema(BaseSchema):
    """Base User Schema."""

    name: str = Field(title="Имя пользователя", example="Василий Алибабаевич")
    email: EmailStr = EMAIL
    created: datetime
    modified: datetime


class UserPasswordSchema(BaseSchema):
    """Base User Password Schema."""

    password: str = Field(title="Пароль", example="password")
    password_confirmation: str = Field(
        title="Пароль, подтверждение ",
        example="password",
        exclude=True,
    )

    @field_validator("password", "password_confirmation")
    def hash_passwords(cls, password: str) -> str:  # noqa
        """Хэшируем пароль.

        Args:
            password: plain password

        Returns:
            str:  Hashing password
        """
        return sha256(password.encode("utf-8")).hexdigest()

    @field_validator("password_confirmation")
    def passwords_match(
        cls,  # noqa
        password_confirmation: str,
        values: FieldValidationInfo,
    ) -> str:
        """Password comparison.

        Args:
            password_confirmation: string password
            values: other parameters

        Returns:
            str: password
        """
        if password_confirmation != values.data.get("password"):
            raise ValueError("passwords do not match")
        return password_confirmation


class UserSchemaRegistration(UserPasswordSchema):
    """Schema of the user during registration."""

    name: str = Field(title="Имя", example="Василий")
    email: EmailStr = EMAIL


class UserSchemaOut(BaseUserSchema):
    """User schema оut."""

    id: UUID = Field(
        description="уникальный `id` номер пользователя, задается автоматически",
        title="Id пользователя",
        example="a17b2315-5bb8-40d3-8d8a-2d48b6c3144e",
    )
    access_token: str = Field(title="Токен доступа")


class UserSchemaLogin(BaseModel):
    """User authorization schemer."""

    email: EmailStr = Field(title="email адрес пользователя, уникальный элемент.")
    password: SecretStr = Field(
        title="Пароль",
        example="password",
        description="Пароль, который был указан при регистрации пользователя",
    )

    @field_validator("password")
    def hash_passwords(cls, password: SecretStr) -> str:  # noqa
        """Password hashing.

        Args:
            password: string SecretStr

        Returns:
            str:  Hashing password
        """
        return sha256(password.get_secret_value().encode("utf-8")).hexdigest()


class RefreshSchema(BaseSchema):
    """Scheme for returning token after method /refresh."""

    access_token: str


class TokenSchema(BaseModel):
    """Token."""

    token: str | None
    alg: str | None
    exp: str | None
    iat: str | None
    email: str | None
    user_id: str | None
    type: str


class OkSchema(BaseModel):
    """Ok."""

    detail: str = "OK 200"
    message: str = "Successfully"
