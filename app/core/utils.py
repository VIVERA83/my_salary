import json
from dataclasses import asdict, dataclass
from typing import Literal

from jose import jws
from starlette import status

ALGORITHMS = [
    "HS512",
    "HS256",
    "HS128",
]
ALGORITHM = Literal[
    "HS256",
    "HS128",
]

METHOD = Literal[
    "HEAD",
    "OPTIONS",
    "GET",
    "POST",
    "DELETE",
    "PATCH",
    "PUT",
    "*",
]
HEADERS = Literal[
    "Accept-Encoding",
    "Content-Type",
    "Set-Cookie",
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Origin",
    "Authorization",
    "*",
]
PUBLIC_ACCESS = [
    ["/admin/*", "*"],
    ["/openapi.json", "GET"],
    ["/docs", "GET"],
    ["/redoc", "GET"],
    ["/docs/oauth2-redirect", "GET"],
    ["/auth/create_user", "POST"],
    ["/auth/login", "POST"],
    ["/auth/refresh", "GET"],
    ["/auth/reset_password", "POST"],
    ["/auth/reset_password", "GET"],
]


METHODS = [
    "HEAD",
    "OPTIONS",
    "GET",
    "POST",
    "DELETE",
    "PATCH",
    "PUT",
]

HTTP_EXCEPTION = {
    status.HTTP_400_BAD_REQUEST: "400 Bad Request",
    status.HTTP_401_UNAUTHORIZED: "401 Unauthorized",
    status.HTTP_403_FORBIDDEN: "403 Forbidden",
    status.HTTP_404_NOT_FOUND: "404 Not Found",
    status.HTTP_405_METHOD_NOT_ALLOWED: "405 Method Not Allowed",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "422 Unavailable Entity",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "500 Internal server error",
}
forbidden_message = (
    "Perhaps you are trying to perform actions that are not implied by the logic of the application."
    "Or you lack access rights."
    "For example, a user with the access level 'access' cannot register a new user,"
    "this functionality is available only to unregistered users or administrators"
)


@dataclass
class Token:
    token: str = None
    alg: str = None
    exp: int = None
    iat: int = None
    email: str = None
    user_id: str = None
    type: str = "anonymous"

    def __init__(self, token: str = None):
        data = {"token": token}
        if token:
            data.update(jws.get_unverified_headers(token))
            data.update(json.loads(jws.get_unverified_claims(token)))
            data.update(data.pop("subject", {}))
        for key, value in data.items():
            setattr(self, key, value)

    @property
    def as_dict(self):
        return asdict(self)
