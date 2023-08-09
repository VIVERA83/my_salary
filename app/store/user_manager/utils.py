import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4

from fastapi import Response
from pydantic import EmailStr


@dataclass
class User:
    email: EmailStr
    password: str
    id: str = uuid4().hex
    name: str = "Пользователь"
    is_superuser: bool = None
    refresh_token: str = None
    access_token: str = None

    @property
    def as_dict(self):
        return asdict(self)

    @property
    def as_string(self):
        return json.dumps(self.as_dict)


class TokenType(Enum):
    verification = "verification"


def set_cookie(key: str, value: str, response: "Response", expire: int, httponly: bool = True, domain: str = None):
    """Adding a token to cookies.

    Args:
        key: name of the cookie
        value: string
        response: Response object
        expire: int the number of seconds
        httponly: if false cookies are available for javascript
        domain: string the domain
    """
    seconds_expires = int(datetime.utcnow().timestamp() + expire)
    response.set_cookie(
        key=key,
        value=value,
        httponly=httponly,
        max_age=seconds_expires,
        domain=domain,
    )


def unset_cookie(
        key: str,
        response: "Response",
):
    """Removing a token from cookies.

    Args:
        response: Response object
        key: name of the cookie
    """
    response.set_cookie(key=key, value="", httponly=True, max_age=-1)

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWJqZWN0Ijp7InVzZXJfaWQiOiJjODdiNzZkOThkMWU0YzA2ODQ4Y2UxNDJiMGM5NjRlOSIsImVtYWlsIjoidml2ZXJhODNAeWFuZGV4LnJ1In0sInR5cGUiOiJ2ZXJpZmljYXRpb24iLCJleHAiOjE2OTE0NTI5NjYsImlhdCI6MTY5MTQzNDk2NiwianRpIjoiNjVkMDg3ZGNhMGNiNGRlZTkzODFhYzZmNjY4OTAwMTYifQ.icFhnh-tGF7_PseE1qJ-PThAqyjkTikkbIxMgCUvnwE
