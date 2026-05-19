from fastapi import HTTPException, status, Header, Depends
from typing import Optional
from .schemas import User


def get_current_user(
        x_user_id: Optional[str] = Header(None),
        x_user_role: Optional[str] = Header("user")
) -> User:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header is required"
        )

    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id must be a valid integer"
        )

    return User(id=user_id, role=x_user_role)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_storage_dep():
    from .storage import get_storage
    return get_storage()