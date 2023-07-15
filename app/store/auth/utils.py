from fastapi import Depends
from fastapi.security import HTTPBearer

METHODS = [
    'post',
    'get',
    'put',
    'delete',
    'patch',
]


def get_token(
    authorization: str = Depends(HTTPBearer(auto_error=True)),
) -> str:
    """Returns token.

    Args:
        authorization: str. The authorization

    Returns:
        optional: token if authorization is okay
    """
    return authorization.credentials  # type: ignore[26]
