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


class BaseUserSchema(BaseSchema):
    """Base User Schema."""

    name: str = Field(title='Имя пользователя', example='Василий Алибабаевич')
    email: EmailStr = Field(title='email адрес пользователя, уникальный элемент')


class UserSchemaRegistration(BaseSchema):
    """Schema of the user during registration."""

    name: str = Field(title='Имя', example='Василий')
    email: EmailStr = Field(title='email адрес пользователя, уникальный элемент.')
    password: str = Field(title='Пароль', example='password')
    password_confirmation: str = Field(
        title='Пароль, подтверждение ',
        example='password',
        exclude=True,
    )

    @field_validator('password', 'password_confirmation')
    def hash_passwords(cls, password: str) -> str:  # noqa
        """Хэшируем пароль.

        Args:
            password: plain password

        Returns:
            str:  Hashing password
        """
        return sha256(password.encode('utf-8')).hexdigest()

    @field_validator('password_confirmation')
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
        if password_confirmation != values.data.get('password'):
            raise ValueError('passwords do not match')
        return password_confirmation


class UserSchemaOut(BaseUserSchema):
    """User schema оut."""

    id: UUID = Field(
        description='уникальный `id` номер пользователя, задается автоматически',
        title='Id пользователя',
        example='a17b2315-5bb8-40d3-8d8a-2d48b6c3144e',
    )
    access_token: str = Field(title='Токен доступа')

    class Config:
        """Config."""

        from_attributes = True
        exclude = True


class UserSchemaLogin(BaseModel):
    """User authorization schemer."""

    email: EmailStr = Field(title='email адрес пользователя, уникальный элемент.')
    password: SecretStr = Field(
        title='Пароль',
        example='password',
        description='Пароль, который был указан при регистрации пользователя',
    )

    @field_validator('password')
    def hash_passwords(cls, password: SecretStr) -> str:  # noqa
        """Password hashing.

        Args:
            password: string SecretStr

        Returns:
            str:  Hashing password
        """
        return sha256(password.get_secret_value().encode('utf-8')).hexdigest()


class OkSchema(BaseModel):
    """Ok."""

    detail: str = 'OK 200'
    message: str = 'Successfully'


class TokenSchema(BaseModel):
    """Token."""

    token: str
    headers: 'HeadersTokenSchema' = Field(title='header', description='Заголовок')
    payload: 'PayloadTokenSchema' = Field(
        title='payload',
        description='Полезная нагрузка',
    )

    def __init__(self, token: str) -> None:
        """Construct TokenSchema.

        Args:
            token: jwt token
        """
        token = token
        payload_data = json.loads(jws.get_unverified_claims(token))
        payload_data.update(payload_data.pop('subject'))
        payload = PayloadTokenSchema(**payload_data)
        headers = HeadersTokenSchema(**jws.get_unverified_headers(token))
        TokenSchema.model_rebuild()
        super().__init__(payload=payload, headers=headers, token=token)


class RefreshSchema(BaseSchema):
    """Scheme for returning token after method /refresh."""

    access_token: str


class HeadersTokenSchema(BaseModel):
    """Token header."""

    algorithm: str = Field(alias='alg')
    type: str = Field(alias='typ')


class PayloadTokenSchema(BaseModel):
    """Token Payload."""

    exp: int
    iat: int
    type: str
    user_id: UUID = Field(title='уникальный идентификатор пользователя')
