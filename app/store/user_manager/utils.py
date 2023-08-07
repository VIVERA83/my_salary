from datetime import datetime

from fastapi import Response
from icecream import ic


def set_cookie(key: str, value: str, response: "Response", expire: int, httponly: bool = True):
    """Adding a token to cookies.

    Args:
        key: name of the cookie
        value: string
        response: Response object
        expire: int the number of seconds
        httponly: if false cookies are available for javascript
    """
    seconds_expires = int(datetime.utcnow().timestamp() + expire)
    response.set_cookie(
        key=key,
        value=value,
        httponly=httponly,
        max_age=seconds_expires,
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
