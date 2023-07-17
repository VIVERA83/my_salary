from typing import Literal

from starlette import status

ALGORITHMS = Literal[
    "HS256",
    "HS128",
]
METHODS = Literal[
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

HTTP_EXCEPTION = {
    status.HTTP_401_UNAUTHORIZED: '401 Unauthorized',
    status.HTTP_403_FORBIDDEN: '403 Forbidden',
    status.HTTP_404_NOT_FOUND: '404 Not Found',
    status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal server error",
}
