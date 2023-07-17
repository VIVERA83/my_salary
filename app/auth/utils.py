from typing import Literal

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
