from fastapi import HTTPException
from starlette import status


CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authenticate认证失败",
        headers={"WWW-Authenticate": "Bearer"},
)

USERBLOCK_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户账号被锁定，请联系管理员",
        headers={"WWW-Authenticate": "Bearer"},
)