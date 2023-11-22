from fastapi import HTTPException
from starlette import status


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authenticate failed",
    headers={"WWW-Authenticate": "Bearer"},
)

USERBLOCK_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="The user account is locked. Please contact the administrator",
    headers={"WWW-Authenticate": "Bearer"},
)

NOT_ADMIN_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="permission denied",
    headers={"WWW-Authenticate": "Bearer"},
)


USER_NOT_VERIFY_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Account not activated, please check your email to confirm your activation",
    headers={"WWW-Authenticate": "Bearer"},
)
